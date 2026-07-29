"""Loopback-only, read-only PR diagnostic and artifact server."""
from __future__ import annotations

import html
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from ..models import VNextError
from ..ui import validate_loopback_host
from .presenters import render_pr_diagnostic_html
from .sidecar import SidecarEvidenceStore

MAX_ARTIFACT_BYTES = 512 * 1024

def _safe_segment(value: str) -> bool:
    return bool(value) and value == unquote(value) and "/" not in value and "\\" not in value and ".." not in value and not value.startswith(("/", "\\")) and ":" not in value

def _handler(service, case_id: str, actor_role: str):
    store = SidecarEvidenceStore(service.root)
    class Handler(BaseHTTPRequestHandler):
        server_version = "AGMPRDiagnostic/0.2-dev"
        def _send(self,status,body,content_type="text/html; charset=utf-8"):
            raw=body.encode("utf-8")
            self.send_response(status); self.send_header("Content-Type",content_type); self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.send_header("X-Content-Type-Options","nosniff"); self.send_header("Content-Security-Policy","default-src 'none'; style-src 'unsafe-inline'"); self.end_headers(); self.wfile.write(raw)
        def do_GET(self): # noqa:N802
            parsed=urlparse(self.path); parts=[unquote(part) for part in parsed.path.split("/") if part]
            if parsed.query: self._send(HTTPStatus.NOT_FOUND,"Not found","text/plain; charset=utf-8"); return
            if not parts:
                self._send(HTTPStatus.OK,render_pr_diagnostic_html(service.pr_diagnosis(case_id,actor_role=actor_role))); return
            if parts == ["healthz"]:
                self._send(HTTPStatus.OK,json.dumps({"status":"ok","case_id":case_id}),"application/json; charset=utf-8"); return
            if parts == ["audit-summary"]:
                self._send(HTTPStatus.OK,json.dumps(store.read_audit_summary()),"application/json; charset=utf-8"); return
            if len(parts)!=4 or parts[0]!="artifacts" or not all(_safe_segment(part) for part in parts[1:]): self._send(HTTPStatus.NOT_FOUND,"Not found","text/plain; charset=utf-8"); return
            supplied_case,digest,artifact_id=parts[1:]
            if supplied_case!=case_id: self._send(HTTPStatus.NOT_FOUND,"Not found","text/plain; charset=utf-8"); return
            try:
                package=store.get_package_by_digest(digest)
                if package.get("case_id")!=case_id: raise VNextError("package is not owned by case")
                metadata,content=store.read_artifact(digest,artifact_id)
                if metadata.get("case_id")!=case_id or len(content.encode("utf8"))>MAX_ARTIFACT_BYTES: raise VNextError("artifact denied")
            except VNextError:
                self._send(HTTPStatus.NOT_FOUND,"Not found","text/plain; charset=utf-8"); return
            # active content is always inert text: no storage path, no HTML execution.
            store.record_read_access(case_id=case_id,package_digest=digest,artifact_id=artifact_id)
            self._send(HTTPStatus.OK,"<pre>"+html.escape(content)+"</pre>","text/html; charset=utf-8")
        def do_POST(self): self._send(HTTPStatus.METHOD_NOT_ALLOWED,"Read-only service","text/plain; charset=utf-8")
        def log_message(self,format,*args): return
    return Handler

def create_pr_diagnostic_server(service, *, case_id: str, actor_role: str="maintainer", host: str="127.0.0.1", port: int=8768):
    validate_loopback_host(host); service.storage.load_case(case_id)
    return ThreadingHTTPServer((host,port),_handler(service,case_id,actor_role))

def serve_pr_diagnostic(service, *, case_id: str, actor_role: str="maintainer", host: str="127.0.0.1", port: int=8768):
    server=create_pr_diagnostic_server(service,case_id=case_id,actor_role=actor_role,host=host,port=port)
    try: server.serve_forever()
    finally: server.server_close()
