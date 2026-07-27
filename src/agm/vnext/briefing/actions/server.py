"""Loopback-only interactive review server with preview-before-execute."""

from __future__ import annotations

import html
import ipaddress
import secrets
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from ...guidance import ActorContext
from ...models import VNextError
from ...service import GovernanceService
from ...ui import validate_loopback_host
from .compiler import (
    compile_contextual_actions,
    compile_final_decision_view,
)
from .draft import ReviewDraftStore
from .executor import (
    execute_final_decision,
    execute_review_submission,
)
from .preview import (
    PreviewTokenRegistry,
    preview_final_decision,
    preview_review_submission,
)
from .presenters import (
    render_final_decision_html,
    render_final_preview_html,
    render_final_result_html,
    render_interactive_review_html,
    render_review_preview_html,
    render_review_result_html,
)


MAX_FORM_BYTES = 64 * 1024
MUTATION_PATHS = {
    "/draft",
    "/draft/abandon",
    "/preview",
    "/execute",
    "/final/preview",
    "/final/execute",
}


def _first(
    form: dict[str, list[str]],
    key: str,
    default: str = "",
) -> str:
    return form.get(key, [default])[0].strip()


def _is_loopback_name(value: str | None) -> bool:
    if not value:
        return False
    if value.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(value).is_loopback
    except ValueError:
        return False


def _handler_class(
    service: GovernanceService,
    *,
    case_id: str,
    actor: ActorContext,
    csrf_token: str,
    token_registry: PreviewTokenRegistry,
    draft_store: ReviewDraftStore,
) -> type[BaseHTTPRequestHandler]:
    class InteractiveReviewHandler(BaseHTTPRequestHandler):
        server_version = "AGMInteractiveReview/0.2-dev"

        def _send(
            self,
            status: int,
            body: str,
            *,
            content_type: str = "text/html; charset=utf-8",
        ) -> None:
            payload = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; style-src 'unsafe-inline'; "
                "form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
            )
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(payload)

        def _error(self, status: int, message: str) -> None:
            self._send(
                status,
                "<h1>请求已拒绝</h1>"
                f"<p>{html.escape(message)}</p>",
            )

        def _validate_host_and_origin(self) -> None:
            server_port = int(self.server.server_address[1])
            host = urlparse("//" + self.headers.get("Host", ""))
            if (
                not _is_loopback_name(host.hostname)
                or (host.port or 80) != server_port
            ):
                raise VNextError("Host 不是当前 loopback review session。")
            origin = urlparse(self.headers.get("Origin", ""))
            if (
                origin.scheme != "http"
                or not _is_loopback_name(origin.hostname)
                or (origin.port or 80) != server_port
            ):
                raise VNextError("Origin 不是当前 loopback review session。")

        def _read_form(self) -> dict[str, list[str]]:
            self._validate_host_and_origin()
            content_type = (
                self.headers.get("Content-Type", "")
                .split(";", 1)[0]
                .strip()
                .lower()
            )
            if content_type != "application/x-www-form-urlencoded":
                raise VNextError(
                    "Mutation endpoint 只接受表单编码 POST。"
                )
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise VNextError("Content-Length 无效。") from exc
            if length <= 0 or length > MAX_FORM_BYTES:
                raise VNextError("请求体大小无效。")
            try:
                raw = self.rfile.read(length).decode(
                    "utf-8",
                    errors="strict",
                )
            except UnicodeError as exc:
                raise VNextError("请求体不是有效 UTF-8。") from exc
            form = parse_qs(
                raw,
                keep_blank_values=True,
                strict_parsing=True,
            )
            observed_csrf = _first(form, "csrf_token")
            if not secrets.compare_digest(csrf_token, observed_csrf):
                raise VNextError("CSRF/session token 缺失或无效。")
            return form

        def _views(self):
            case = service.storage.load_case(case_id)
            brief = service.review_brief(
                case_id,
                actor=actor.actor,
                role=actor.role,
            )
            actions = compile_contextual_actions(
                review_brief=brief,
                governance_case=case,
                actor_context=actor,
                policy_config=service.config,
                live_actions_enabled=True,
            )
            return case, brief, actions

        def _selections(
            self,
            form: dict[str, list[str]],
            action_view,
        ) -> dict[str, dict[str, str]]:
            selections = {}
            for index, item in enumerate(action_view.items, start=1):
                option_id = _first(form, f"decision:{index}")
                if not option_id:
                    continue
                reason = _first(
                    form,
                    f"reason:{index}:{option_id}",
                )
                selections[item.judgment_id] = {
                    "option_id": option_id,
                    "reason": reason,
                }
            return selections

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.query:
                self._error(
                    HTTPStatus.NOT_FOUND,
                    "交互页面不接受 query 参数。",
                )
                return
            if parsed.path in MUTATION_PATHS:
                self._error(
                    HTTPStatus.METHOD_NOT_ALLOWED,
                    "状态改变端点仅允许 POST。",
                )
                return
            if parsed.path == "/":
                try:
                    case, _, actions = self._views()
                    draft = draft_store.restore(
                        case_id=case_id,
                        actor_id=actor.actor,
                        role=actor.role,
                    )
                    assessment = (
                        draft_store.assess(
                            draft=draft,
                            case=case,
                            action_view=actions,
                        )
                        if draft
                        else None
                    )
                    rendered = render_interactive_review_html(
                        actions,
                        draft=draft,
                        assessment=assessment,
                        csrf_token=csrf_token,
                    )
                except VNextError as exc:
                    self._error(HTTPStatus.BAD_REQUEST, str(exc))
                    return
                self._send(HTTPStatus.OK, rendered)
                return
            if parsed.path == "/final":
                try:
                    case, brief, _ = self._views()
                    final_view = compile_final_decision_view(
                        review_brief=brief,
                        governance_case=case,
                        actor_context=actor,
                        policy_config=service.config,
                    )
                    rendered = render_final_decision_html(
                        final_view,
                        csrf_token=csrf_token,
                    )
                except VNextError as exc:
                    self._error(HTTPStatus.BAD_REQUEST, str(exc))
                    return
                self._send(HTTPStatus.OK, rendered)
                return
            self._error(HTTPStatus.NOT_FOUND, "Not found")

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.query or parsed.path not in MUTATION_PATHS:
                self._error(HTTPStatus.NOT_FOUND, "Not found")
                return
            try:
                form = self._read_form()
                case, _, actions = self._views()
                if parsed.path == "/draft/abandon":
                    draft_store.abandon(
                        case_id=case_id,
                        actor_id=actor.actor,
                        role=actor.role,
                    )
                    self.send_response(HTTPStatus.SEE_OTHER)
                    self.send_header("Location", "/")
                    self.end_headers()
                    return
                if parsed.path in {"/draft", "/preview"}:
                    draft = draft_store.save(
                        action_view=actions,
                        selections=self._selections(form, actions),
                    )
                    if parsed.path == "/draft":
                        self.send_response(HTTPStatus.SEE_OTHER)
                        self.send_header("Location", "/")
                        self.end_headers()
                        return
                    preview = preview_review_submission(
                        service=service,
                        actor_context=actor,
                        review_draft=draft,
                        token_registry=token_registry,
                    )
                    self._send(
                        HTTPStatus.OK,
                        render_review_preview_html(
                            preview,
                            csrf_token=csrf_token,
                        ),
                    )
                    return
                if parsed.path == "/execute":
                    result = execute_review_submission(
                        service=service,
                        actor_context=actor,
                        case_id=case_id,
                        preview_token=_first(form, "preview_token"),
                        token_registry=token_registry,
                        draft_store=draft_store,
                    )
                    self._send(
                        HTTPStatus.OK,
                        render_review_result_html(result),
                    )
                    return
                if parsed.path == "/final/preview":
                    preview = preview_final_decision(
                        service=service,
                        actor_context=actor,
                        case_id=case_id,
                        decision_id=_first(form, "decision_id"),
                        reason=_first(form, "reason"),
                        token_registry=token_registry,
                    )
                    self._send(
                        HTTPStatus.OK,
                        render_final_preview_html(
                            preview,
                            csrf_token=csrf_token,
                        ),
                    )
                    return
                if parsed.path == "/final/execute":
                    result = execute_final_decision(
                        service=service,
                        actor_context=actor,
                        case_id=case_id,
                        preview_token=_first(form, "preview_token"),
                        token_registry=token_registry,
                        draft_store=draft_store,
                    )
                    self._send(
                        HTTPStatus.OK,
                        render_final_result_html(result),
                    )
                    return
            except (KeyError, ValueError, VNextError) as exc:
                draft_store.record_rejected_attempt(
                    case_id=case_id,
                    actor_id=actor.actor,
                    role=actor.role,
                    reason=str(exc),
                    operation=parsed.path,
                )
                self._error(HTTPStatus.BAD_REQUEST, str(exc))

        def log_message(self, format: str, *args: Any) -> None:
            return

    return InteractiveReviewHandler


def serve_interactive_review(
    service: GovernanceService,
    *,
    case_id: str,
    actor: str,
    role: str,
    host: str = "127.0.0.1",
    port: int = 8768,
) -> None:
    """Serve contextual review actions on loopback only."""

    validate_loopback_host(host)
    service.storage.load_case(case_id)
    actor_context = ActorContext(actor=actor, role=role, human=True)
    csrf_token = secrets.token_urlsafe(32)
    token_registry = PreviewTokenRegistry()
    draft_store = ReviewDraftStore(service.storage)
    server = ThreadingHTTPServer(
        (host, port),
        _handler_class(
            service,
            case_id=case_id,
            actor=actor_context,
            csrf_token=csrf_token,
            token_registry=token_registry,
            draft_store=draft_store,
        ),
    )
    print(
        "AGM interactive maintainer review: "
        f"http://{host}:{server.server_port}/"
    )
    print(
        "Loopback-only; POST mutations require session CSRF and a one-time "
        "preview token. Press Ctrl+C to stop."
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


__all__ = ["_handler_class", "serve_interactive_review"]
