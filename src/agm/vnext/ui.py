"""Loopback-only standard-library UI with per-session action tokens."""

from __future__ import annotations

import hmac
import ipaddress
import json
import secrets
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from .guidance import (
    ActorContext,
    build_context_selector_options,
    preview_reviewer_action,
    resolve_selector_tokens,
    utility_output,
)
from .models import VNextError
from .reporting import render_html, render_markdown
from .service import GovernanceService


MAX_FORM_BYTES = 64 * 1024


def validate_loopback_host(host: str) -> str:
    if host.lower() == "localhost":
        return host
    try:
        address = ipaddress.ip_address(host)
    except ValueError as exc:
        raise VNextError("Local UI host must be a loopback address") from exc
    if not address.is_loopback:
        raise VNextError("Local UI may bind only to a loopback address")
    return host


def new_action_token() -> str:
    return secrets.token_urlsafe(32)


def validate_action_token(expected: str, observed: str | None) -> None:
    if not observed or not hmac.compare_digest(expected, observed):
        raise VNextError("Invalid or missing local UI action token")


def _first(form: dict[str, list[str]], key: str, default: str = "") -> str:
    return form.get(key, [default])[0].strip()


def _lines(value: str) -> list[str]:
    return [item.strip() for item in value.splitlines() if item.strip()]


def _values(form: dict[str, list[str]], key: str) -> list[str]:
    return [item.strip() for item in form.get(key, []) if item.strip()]


def resolve_panel_selection(
    service: GovernanceService,
    *,
    case_id: str,
    form: dict[str, list[str]],
) -> dict[str, list[str] | str]:
    """Rebuild selector choices from current case before using any token."""
    action = _first(form, "action")
    tokens = _values(form, "selector_token")
    selector_actions = {
        "verify_evidence",
        "reject_evidence",
        "request_repair",
        "ask_clarification",
        "invalidate_attestation",
        "record_policy_conflict",
        "resolve_policy_conflict",
        "resubmit",
        "authorized_override",
    }
    if not tokens:
        if (
            action == "verify_evidence"
            and not _first(form, "obligation")
            and not _values(form, "obligation_ids")
            and not _first(form, "object_id")
        ):
            return {
                "obligation_ids": [],
                "object_id": "",
                "finding_ids": [],
            }
        if action in selector_actions:
            case = service.storage.load_case(case_id)
            options = build_context_selector_options(case, action)
            detail = (
                "请从页面提供的当前案例对象中选择。"
                if options
                else "当前案例没有适用于此操作的对象。"
            )
            raise VNextError(
                "Web 面板不接受手填内部 ID；" + detail
            )
        return {
            "obligation_ids": _values(form, "obligation_ids"),
            "object_id": _first(form, "object_id"),
            "finding_ids": _values(form, "finding_ids"),
        }
    case = service.storage.load_case(case_id)
    return resolve_selector_tokens(case, action, tokens)


def execute_panel_action(
    service: GovernanceService,
    *,
    case_id: str,
    audience: str,
    form: dict[str, list[str]],
    action_token: str,
) -> None:
    validate_action_token(action_token, _first(form, "action_token"))
    action = _first(form, "action")
    actor = _first(form, "actor")
    if audience == "contributor":
        statement = _first(form, "statement")
        if action == "confirm_attestation":
            service.attest(
                case_id,
                actor=actor,
                role="accountable_human",
                reviewed_scope=_lines(_first(form, "scope")),
                statement=statement,
                reservations=_lines(_first(form, "reservations")),
            )
            return
        if action == "request_correction":
            case = service.storage.load_case(case_id)
            service.request_correction(
                case_id,
                actor=actor,
                role="accountable_human",
                reason=statement,
                affected_obligation_ids=[
                    item.obligation_id
                    for item in case.obligations
                    if item.blocking
                ],
            )
            return
        if action == "decline_attestation":
            service.decline_attestation(
                case_id,
                actor=actor,
                role="accountable_human",
                reason=statement,
            )
            return
        raise VNextError(f"Unsupported contributor panel action: {action}")

    role = _first(form, "role")
    selected = _values(form, "obligation_ids")
    if not selected:
        obligation = _first(form, "obligation")
        selected = [obligation] if obligation else []
    object_id = _first(form, "object_id")
    finding_ids = _values(form, "finding_ids")
    reason = _first(form, "reason")
    if action == "verify_evidence":
        service.verify(
            case_id,
            actor=actor,
            role=role,
            reason=reason,
            obligation_ids=selected or None,
        )
    elif action == "reject_evidence":
        service.reject_evidence(
            case_id,
            actor=actor,
            role=role,
            evidence_id=object_id,
            reason=reason,
        )
    elif action == "request_repair":
        service.request_repair(
            case_id,
            actor=actor,
            role=role,
            message=reason,
            affected_obligation_ids=selected,
        )
    elif action == "ask_clarification":
        service.ask_clarification(
            case_id,
            actor=actor,
            role=role,
            question=reason,
            affected_obligation_ids=selected,
        )
    elif action == "invalidate_attestation":
        service.invalidate_attestation(
            case_id,
            actor=actor,
            role=role,
            attestation_id=object_id,
            reason=reason,
        )
    elif action == "record_policy_conflict":
        service.record_policy_conflict(
            case_id,
            actor=actor,
            role=role,
            message=reason,
            affected_obligation_ids=selected,
        )
    elif action == "resolve_policy_conflict":
        service.resolve_policy_conflict(
            case_id,
            actor=actor,
            role=role,
            finding_id=object_id,
            resolution=reason,
        )
    elif action == "resubmit":
        service.resubmit(
            case_id,
            actor=actor,
            role=role,
            summary=reason,
            affected_obligation_ids=selected,
            change_classification=_first(
                form, "change_classification", "non_material"
            ),
            change_reason=_first(form, "change_reason", reason),
        )
    elif action == "confirm_attestation":
        service.attest(
            case_id,
            actor=actor,
            role=role,
            reviewed_scope=_values(form, "scope"),
            statement=reason,
        )
    elif action == "authorized_override":
        service.override(
            case_id,
            actor=actor,
            role=role,
            reason=reason,
            obligation_ids=selected,
            finding_ids=finding_ids,
        )
    elif action.startswith("decide_"):
        decision = action.removeprefix("decide_")
        service.decide(
            case_id,
            actor=actor,
            role=role,
            decision=decision,
            reason=reason,
        )
    else:
        raise VNextError(f"Unsupported maintainer panel action: {action}")


def handler_class(
    service: GovernanceService,
    *,
    case_id: str,
    audience: str,
    action_token: str,
    current_actor: ActorContext | None = None,
) -> type[BaseHTTPRequestHandler]:
    class PanelHandler(BaseHTTPRequestHandler):
        server_version = "AGMLocalPanel/0.2-dev"

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
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; form-action 'self'")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/utility" and audience == "maintainer":
                query = parse_qs(parsed.query)
                action_id = _first(query, "action_id")
                try:
                    view = service.reviewer_guidance(
                        case_id,
                        actor=(
                            current_actor.actor
                            if current_actor
                            else "maintainer-reviewer"
                        ),
                        role=(
                            current_actor.role
                            if current_actor
                            else "maintainer"
                        ),
                    )
                    item = utility_output(view.utility_actions, action_id)
                except KeyError:
                    self._send(
                        HTTPStatus.NOT_FOUND,
                        "未知的只读 guidance 工具。",
                        content_type="text/plain; charset=utf-8",
                    )
                    return
                self._send(
                    HTTPStatus.OK,
                    item.output,
                    content_type=item.output_type + "; charset=utf-8",
                )
                return
            if parsed.path != "/" or parsed.query:
                self._send(HTTPStatus.NOT_FOUND, "<h1>Not found</h1>")
                return
            case = service.storage.load_case(case_id)
            transitions = service.storage.read_transitions(case_id)
            self._send(
                HTTPStatus.OK,
                render_html(
                    case,
                    transitions,
                    audience=audience,
                    action_token=action_token,
                    config=service.config,
                    current_actor=current_actor,
                ),
            )

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/":
                self._send(HTTPStatus.NOT_FOUND, "<h1>Not found</h1>")
                return
            content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            if content_type != "application/x-www-form-urlencoded":
                self._send(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "<h1>Unsupported form type</h1>")
                return
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send(HTTPStatus.BAD_REQUEST, "<h1>Invalid request</h1>")
                return
            if content_length <= 0 or content_length > MAX_FORM_BYTES:
                self._send(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "<h1>Invalid form size</h1>")
                return
            raw = self.rfile.read(content_length).decode("utf-8", errors="strict")
            form = parse_qs(raw, keep_blank_values=True)
            try:
                validate_action_token(
                    action_token, _first(form, "action_token")
                )
                if audience == "maintainer":
                    case = service.storage.load_case(case_id)
                    transitions = service.storage.read_transitions(case_id)
                    actor = ActorContext(
                        actor=_first(form, "actor"),
                        role=_first(
                            form,
                            "role",
                            (
                                current_actor.role
                                if current_actor
                                else "maintainer"
                            ),
                        ),
                    )
                    resolved = resolve_panel_selection(
                        service,
                        case_id=case_id,
                        form=form,
                    )
                    parameters = {
                        "obligation_ids": list(
                            resolved.get("obligation_ids", [])
                        ),
                        "object_id": str(
                            resolved.get("object_id", "")
                        ),
                        "finding_ids": list(
                            resolved.get("finding_ids", [])
                        ),
                        "reason": _first(form, "reason"),
                        "change_classification": _first(
                            form, "change_classification"
                        ),
                        "change_reason": _first(form, "change_reason"),
                    }
                    preview = preview_reviewer_action(
                        case,
                        service.config,
                        transitions,
                        actor,
                        _first(form, "action"),
                        parameters,
                    )
                    if _first(form, "confirm") != "execute":
                        self._send(
                            HTTPStatus.OK,
                            render_html(
                                case,
                                transitions,
                                audience=audience,
                                action_token=action_token,
                                config=service.config,
                                current_actor=actor,
                                preview=preview,
                                form_values=form,
                            ),
                        )
                        return
                    if not preview.authorized:
                        raise VNextError(
                            "Operation rejected by preview authorization: "
                            + preview.authorization_reason
                        )
                    if not hmac.compare_digest(
                        preview.preview_fingerprint,
                        _first(form, "preview_fingerprint"),
                    ):
                        raise VNextError(
                            "Case or action inputs changed after preview; "
                            "generate a new preview"
                        )
                    form = {
                        **form,
                        "obligation_ids": list(
                            resolved.get("obligation_ids", [])
                        ),
                        "object_id": [
                            str(resolved.get("object_id", ""))
                        ],
                        "finding_ids": list(
                            resolved.get("finding_ids", [])
                        ),
                    }
                execute_panel_action(
                    service,
                    case_id=case_id,
                    audience=audience,
                    form=form,
                    action_token=action_token,
                )
            except (UnicodeError, VNextError) as exc:
                import html

                self._send(
                    HTTPStatus.BAD_REQUEST,
                    f"<h1>Operation rejected</h1><p>{html.escape(str(exc))}</p>",
                )
                return
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

        def log_message(self, format: str, *args: Any) -> None:
            return

    return PanelHandler


def serve_panel(
    service: GovernanceService,
    *,
    case_id: str,
    audience: str,
    host: str = "127.0.0.1",
    port: int = 8765,
    actor: str | None = None,
    role: str | None = None,
) -> None:
    validate_loopback_host(host)
    if audience not in {"contributor", "maintainer"}:
        raise VNextError("Panel audience must be contributor or maintainer")
    case = service.storage.load_case(case_id)
    transitions = service.storage.read_transitions(case_id)
    current_actor = (
        ActorContext(
            actor=actor or "maintainer-reviewer",
            role=role or "maintainer",
        )
        if audience == "maintainer"
        else None
    )
    service.storage.write_report(
        case_id,
        markdown=render_markdown(
            case,
            transitions,
            audience=audience,
            config=service.config,
            current_actor=current_actor,
        ),
        html=render_html(
            case,
            transitions,
            audience=audience,
            config=service.config,
            current_actor=current_actor,
        ),
        guidance_json=(
            json.dumps(
                service.reviewer_guidance(
                    case_id,
                    actor=current_actor.actor,
                    role=current_actor.role,
                ).to_dict(),
                indent=2,
                ensure_ascii=False,
            )
            if current_actor
            else None
        ),
    )
    token = new_action_token()
    server = ThreadingHTTPServer(
        (host, port),
        handler_class(
            service,
            case_id=case_id,
            audience=audience,
            action_token=token,
            current_actor=current_actor,
        ),
    )
    print(f"AGM {audience} panel: http://{host}:{server.server_port}/")
    print("The server is bound to loopback only. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
