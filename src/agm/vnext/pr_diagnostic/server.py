"""Loopback-only, read-only PR diagnostic and artifact server."""
from __future__ import annotations

import base64
import hashlib
import html
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from ..models import VNextError
from ..ui import validate_loopback_host
from .artifact_projection import project_structured_artifact
from .presenters import render_pr_diagnostic_html
from .sidecar import SidecarEvidenceStore

MAX_ARTIFACT_BYTES = 512 * 1024

ARTIFACT_SCRIPT = r"""
(() => {
  const decode = (value) => new TextDecoder().decode(Uint8Array.from(atob(value), c => c.charCodeAt(0)));
  const root = document.querySelector('[data-artifact-viewer]');
  if (!root) return;
  const tabs = Array.from(root.querySelectorAll('[role="tab"]'));
  const select = (tab) => {
    tabs.forEach((item) => {
      const active = item === tab;
      item.setAttribute('aria-selected', String(active));
      item.tabIndex = active ? 0 : -1;
      document.getElementById(item.getAttribute('aria-controls')).hidden = !active;
    });
    tab.focus();
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', (event) => {
      let target = index;
      if (event.key === 'ArrowRight') target = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') target = (index + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') target = 0;
      else if (event.key === 'End') target = tabs.length - 1;
      else return;
      event.preventDefault();
      select(tabs[target]);
    });
  });
  const status = root.querySelector('[role="status"]');
  root.querySelectorAll('[data-copy]').forEach((button) => {
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(decode(root.dataset[button.dataset.copy]));
        status.textContent = button.dataset.success;
      } catch (_) {
        status.textContent = '复制失败，请检查浏览器剪贴板权限。';
      }
    });
  });
  const wrap = root.querySelector('#wrap-raw');
  const raw = root.querySelector('#raw-code');
  if (wrap && raw) wrap.addEventListener('change', () => raw.classList.toggle('wrap', wrap.checked));
})();
""".strip()


def _encoded(value: str) -> str:
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def _artifact_page(metadata: dict, content: str, package_digest: str) -> str:
    projection = project_structured_artifact(
        metadata=metadata, content=content, package_digest=package_digest
    )
    if projection is None:
        return (
            "<!doctype html><html lang=\"zh-CN\"><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>材料原始数据</title><style>"
            "body{margin:0;background:#f3f6f8;font:16px/1.55 system-ui;color:#18212f}"
            "main{max-width:1040px;margin:auto;padding:16px;min-width:0}"
            "pre{background:#fff;border:1px solid #dbe2ea;border-radius:12px;padding:16px;"
            "white-space:pre;overflow:auto;overflow-wrap:normal;word-break:normal;max-width:100%}"
            "</style><main><h1>材料原始数据</h1><pre>"
            + html.escape(content)
            + "</pre></main></html>"
        )
    readable = (
        projection.rendered_html
        if projection.readable_available
        else "<section class=\"parse-error\"><h2>该材料无法生成结构化可读视图</h2>"
        "<p>内容未被猜测或修复；请在“原始数据”中检查原始材料。</p></section>"
    )
    markdown_button = (
        '<button type="button" data-copy="markdown" data-success="已复制 Markdown。">复制 Markdown</button>'
        if projection.markdown is not None
        else ""
    )
    title = html.escape(str(metadata.get("title") or "结构化材料"))
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6f8;font:16px/1.55 system-ui;color:#18212f;overflow-wrap:anywhere}}main{{max-width:1040px;margin:auto;padding:16px;min-width:0}}header,.panel,details{{background:#fff;border:1px solid #dbe2ea;border-radius:12px;padding:16px;margin:14px 0;min-width:0}}header{{background:#153452;color:#fff}}.identity{{font-size:.92rem}}.identity code{{word-break:break-all}}[role=tablist]{{display:flex;gap:4px;border-bottom:2px solid #aebbc8}}[role=tab]{{font:inherit;font-weight:700;padding:10px 16px;border:1px solid #aebbc8;border-bottom:0;border-radius:8px 8px 0 0;background:#e9eef3;color:#18212f}}[role=tab][aria-selected=true]{{background:#fff;color:#0b4f7d}}[role=tabpanel]:focus{{outline:3px solid #75a9d0;outline-offset:2px}}button{{font:inherit;padding:8px 12px;margin:4px 6px 4px 0;cursor:pointer}}.notice{{border-left:5px solid #3578a8;padding-left:12px}}.parse-error{{border-left:5px solid #a64b17}}.raw-pane{{min-width:0;max-width:100%;overflow:hidden}}pre.raw{{font:14px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;white-space:pre;overflow-x:auto;overflow-y:auto;overflow-wrap:normal;word-break:normal;max-width:100%;padding:16px;background:#111923;color:#ecf2f8;border-radius:8px}}pre.raw.wrap{{white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word}}.controls{{display:flex;flex-wrap:wrap;align-items:center;gap:8px}}.technical code{{word-break:break-all}}li[class^=depth-]{{margin-top:4px}}.depth-1{{margin-left:1rem}}.depth-2{{margin-left:2rem}}.depth-3{{margin-left:3rem}}[hidden]{{display:none!important}}@media(max-width:720px){{main{{padding:8px}}[role=tab]{{flex:1;padding:10px 6px}}pre.raw{{max-height:65vh}}}}
</style><main data-artifact-viewer data-raw="{_encoded(projection.raw_text)}" data-formatted="{_encoded(projection.formatted_text)}" data-markdown="{_encoded(projection.markdown or '')}">
<header><h1>{title}</h1><p>结构化材料检查页</p></header>
<p class="notice">此可读视图由当前结构化材料自动生成，不是独立证据。</p>
<div class="identity"><strong>Artifact ID：</strong><code>{html.escape(projection.artifact_id)}</code><br><strong>Source digest：</strong><code>{html.escape(projection.source_digest)}</code></div>
<div role="tablist" aria-label="材料视图"><button type="button" id="tab-readable" role="tab" aria-selected="true" aria-controls="panel-readable">可读视图</button><button type="button" id="tab-raw" role="tab" aria-selected="false" aria-controls="panel-raw" tabindex="-1">原始数据</button></div>
<section id="panel-readable" class="panel" role="tabpanel" aria-labelledby="tab-readable" tabindex="0">{readable}<div>{markdown_button}</div></section>
<section id="panel-raw" class="panel raw-pane" role="tabpanel" aria-labelledby="tab-raw" tabindex="0" hidden><p>当前页面仅对原始材料进行格式化展示；材料内容和摘要未发生改变。摘要基于原始 canonical bytes，而不是格式化后的显示文本。</p><div class="controls"><button type="button" data-copy="raw" data-success="已复制原始内容。">复制原始内容</button><button type="button" data-copy="formatted" data-success="已复制格式化内容。">复制格式化内容</button><label><input type="checkbox" id="wrap-raw"> 自动换行</label></div><pre id="raw-code" class="raw">{html.escape(projection.formatted_text)}</pre></section>
<p role="status" aria-live="polite"></p>
<details class="technical"><summary>技术详情</summary><ul><li>Artifact type：<code>{html.escape(projection.artifact_type)}</code></li><li>Source artifact ID：<code>{html.escape(projection.artifact_id)}</code></li><li>Source digest：<code>{html.escape(projection.source_digest)}</code></li><li>Package binding：<code>{html.escape(projection.package_digest)}</code></li><li>Contribution binding：<code>{html.escape(projection.contribution_fingerprint)}</code></li><li>Projection template version：<code>{html.escape(projection.template_version)}</code></li><li>Derived human-readable projection</li></ul></details>
</main><script>{ARTIFACT_SCRIPT}</script></html>'''

def _safe_segment(value: str) -> bool:
    return bool(value) and value == unquote(value) and "/" not in value and "\\" not in value and ".." not in value and not value.startswith(("/", "\\")) and ":" not in value

def _handler(service, case_id: str, actor_role: str):
    store = SidecarEvidenceStore(service.root)
    class Handler(BaseHTTPRequestHandler):
        server_version = "AGMPRDiagnostic/0.2-dev"
        def _send(self,status,body,content_type="text/html; charset=utf-8",csp=None):
            raw=body.encode("utf-8")
            policy=csp or "default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; object-src 'none'; base-uri 'none'"
            self.send_response(status); self.send_header("Content-Type",content_type); self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.send_header("X-Content-Type-Options","nosniff"); self.send_header("Content-Security-Policy",policy); self.end_headers(); self.wfile.write(raw)
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
                try:
                    metadata,content=store.read_artifact(digest,artifact_id)
                except VNextError:
                    view=service.pr_diagnosis(case_id,actor_role=actor_role)
                    item=next((candidate for candidate in view.inspection_objects if candidate.artifact_route==parsed.path and candidate.evidence_package_digest==digest and candidate.inline_content is not None),None)
                    if item is None: raise
                    metadata={**item.technical_metadata,"artifact_id":item.object_id,"artifact_type":item.technical_metadata.get("artifact_type"),"title":item.title,"content_digest":item.content_digest,"contribution_fingerprint":item.contribution_fingerprint,"case_id":case_id}
                    content=item.inline_content
                if metadata.get("case_id")!=case_id or len(content.encode("utf8"))>MAX_ARTIFACT_BYTES: raise VNextError("artifact denied")
            except VNextError:
                self._send(HTTPStatus.NOT_FOUND,"Not found","text/plain; charset=utf-8"); return
            store.record_read_access(case_id=case_id,package_digest=digest,artifact_id=artifact_id)
            body=_artifact_page(metadata,content,digest)
            script_hash=base64.b64encode(hashlib.sha256(ARTIFACT_SCRIPT.encode("utf-8")).digest()).decode("ascii")
            csp=f"default-src 'none'; style-src 'unsafe-inline'; script-src 'sha256-{script_hash}'; img-src 'none'; connect-src 'none'; object-src 'none'; base-uri 'none'; frame-src 'none'"
            self._send(HTTPStatus.OK,body,"text/html; charset=utf-8",csp)
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
