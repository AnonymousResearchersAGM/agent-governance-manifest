"""Loopback-only read-only server for the maintainer review brief."""

from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from ..service import GovernanceService
from ..ui import validate_loopback_host
from .presenters import render_review_brief_html


def _handler_class(
    service: GovernanceService,
    *,
    case_id: str,
    actor: str,
    role: str,
) -> type[BaseHTTPRequestHandler]:
    class BriefHandler(BaseHTTPRequestHandler):
        server_version = "AGMReviewBrief/0.2-dev"

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
                "default-src 'none'; style-src 'unsafe-inline'",
            )
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path != "/" or parsed.query:
                self._send(HTTPStatus.NOT_FOUND, "<h1>Not found</h1>")
                return
            view = service.review_brief(
                case_id, actor=actor, role=role
            )
            self._send(
                HTTPStatus.OK, render_review_brief_html(view)
            )

        def do_POST(self) -> None:  # noqa: N802
            self._send(
                HTTPStatus.METHOD_NOT_ALLOWED,
                "Review Brief Phase 1 is read-only.",
                content_type="text/plain; charset=utf-8",
            )

        def log_message(self, format: str, *args: Any) -> None:
            return

    return BriefHandler


def serve_review_brief(
    service: GovernanceService,
    *,
    case_id: str,
    actor: str,
    role: str,
    host: str = "127.0.0.1",
    port: int = 8767,
) -> None:
    """Serve only the briefing page; no state-changing route exists."""

    validate_loopback_host(host)
    service.storage.load_case(case_id)
    server = ThreadingHTTPServer(
        (host, port),
        _handler_class(
            service,
            case_id=case_id,
            actor=actor,
            role=role,
        ),
    )
    print(
        "AGM maintainer review brief: "
        f"http://{host}:{server.server_port}/"
    )
    print("Phase 1 server is loopback-only and read-only. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
