"""Same-origin loopback proxy and participant task controller for P92."""

from __future__ import annotations

import argparse
import html
import http.client
import json
import secrets
import sys
import threading
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import parse_qs, urlencode, urlparse

from common import (
    TASK_IDS,
    atomic_write_json,
    load_config,
    task_config,
    utc_now,
)
from records import RecordStore, snapshot_case


MAX_BODY = 64 * 1024
BACKEND_MUTATIONS = {
    "/draft": "save_click",
    "/draft/abandon": "draft_abandon_click",
    "/preview": "preview_click",
    "/execute": "execute_click",
    "/final/preview": "final_decision_click",
    "/final/execute": "final_decision_execute_click",
}
P92_CSP = (
    "default-src 'none'; style-src 'unsafe-inline'; "
    "script-src 'unsafe-inline'; connect-src 'self'; form-action 'self'; "
    "base-uri 'none'; frame-ancestors 'none'"
)


def _esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _options(question: Mapping[str, Any]) -> str:
    name = _esc(question["id"])
    return "".join(
        '<label class="p92-answer">'
        f'<input type="radio" name="{name}" value="{_esc(option)}" required>'
        f"<span>{_esc(option)}</span></label>"
        for option in question["options"]
    )


def _question_form(
    *,
    title: str,
    questions: list[Mapping[str, Any]],
    action: str,
    secret: str,
) -> str:
    blocks = "".join(
        '<fieldset class="p92-question">'
        f"<legend>{index}. {_esc(question['text'])}</legend>"
        f"{_options(question)}</fieldset>"
        for index, question in enumerate(questions, start=1)
    )
    return (
        f"<h2>{_esc(title)}</h2>"
        '<p>请根据你刚才看到的页面回答。系统不会显示自动评分。</p>'
        f'<form method="post" action="{_esc(action)}">'
        f'<input type="hidden" name="p92_secret" value="{_esc(secret)}">'
        f"{blocks}<button type=\"submit\">提交回答</button></form>"
    )


def _feedback_form(secret: str, notice: str = "") -> str:
    notice_html = f'<p class="p92-training-feedback">{_esc(notice)}</p>' if notice else ""
    return (
        f"{notice_html}<h2>本题已经结束</h2>"
        "<p>请停止操作并通知研究者。页面不会显示正确或错误反馈。</p>"
        '<form method="post" action="/p92/feedback">'
        f'<input type="hidden" name="p92_secret" value="{_esc(secret)}">'
        '<fieldset class="p92-question"><legend>本题难度（1–7）</legend>'
        '<input type="number" name="difficulty" min="1" max="7" required></fieldset>'
        '<fieldset class="p92-question"><legend>你的判断信心（1–5）</legend>'
        '<input type="number" name="confidence" min="1" max="5" required></fieldset>'
        '<label class="p92-comment">可选原话或疑问'
        '<textarea name="comment" maxlength="4000"></textarea></label>'
        '<button type="submit">保存本题反馈</button></form>'
    )


def _debrief_form(config: Mapping[str, Any], secret: str) -> str:
    fields = "".join(
        '<label class="p92-comment">'
        f"{index}. {_esc(question)}"
        f'<textarea name="q{index}" maxlength="6000" required></textarea></label>'
        for index, question in enumerate(config["debrief_questions"], start=1)
    )
    return (
        "<h2>P92 结束访谈</h2>"
        "<p>请按原话回答；系统不会自动改写你的回答。</p>"
        '<form method="post" action="/p92/debrief">'
        f'<input type="hidden" name="p92_secret" value="{_esc(secret)}">'
        f"{fields}<button type=\"submit\">提交结束访谈</button></form>"
    )


TASKBAR_CSS = """
<style id="p92-task-style">
#p92-taskbar{position:sticky;top:0;z-index:2147483000;background:#102f49;
color:#fff;border-bottom:4px solid #f0b429;padding:12px 18px;
font:15px/1.45 system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;
box-shadow:0 8px 24px #091c2c35}
#p92-taskbar .p92-row{width:min(1080px,100%);margin:auto;display:flex;
align-items:center;gap:14px;justify-content:space-between}
#p92-taskbar strong{font-size:1.05rem}#p92-taskbar p{margin:2px 0}
#p92-taskbar .p92-boundary{color:#ffe7a3;font-weight:750}
#p92-taskbar button,#p92-lock button{border:0;border-radius:8px;padding:9px 15px;
background:#fff;color:#153452;font:inherit;font-weight:800;cursor:pointer}
#p92-clock{font-variant-numeric:tabular-nums;white-space:nowrap}
#p92-lock{position:fixed;inset:0;z-index:2147483500;background:#eef3f7f5;
display:grid;place-items:center;padding:18px;overflow:auto}
#p92-lock .p92-panel{width:min(720px,100%);max-height:calc(100vh - 36px);
overflow:auto;background:#fff;color:#18212f;border:2px solid #176b9c;
border-radius:16px;padding:24px;box-shadow:0 24px 70px #10283f38;
font:16px/1.55 system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif}
.p92-question{border:1px solid #d5dee6;border-radius:10px;padding:12px;
margin:14px 0}.p92-question legend{font-weight:800}
.p92-answer{display:block;padding:8px}.p92-answer input{margin-right:8px}
.p92-comment{display:block;margin:14px 0;font-weight:750}
.p92-comment textarea{display:block;width:100%;min-height:82px;margin-top:6px}
.p92-training-feedback{background:#fff3cf;border-left:5px solid #a66a00;
padding:12px}.p92-finished{font-weight:800;color:#176b4c}
@media(max-width:720px){#p92-taskbar{padding:10px}
#p92-taskbar .p92-row{align-items:stretch;flex-direction:column;gap:6px}
#p92-taskbar button{width:100%}#p92-lock{padding:8px}
#p92-lock .p92-panel{padding:16px;max-height:calc(100vh - 16px)}}
</style>
"""


def _taskbar(
    task_id: str,
    task: Mapping[str, Any],
    *,
    secret: str,
    started_at: str,
    show_complete: bool,
    ended: bool,
) -> str:
    complete = ""
    if show_complete and not ended:
        complete = (
            '<form method="post" action="/p92/complete">'
            f'<input type="hidden" name="p92_secret" value="{_esc(secret)}">'
            '<button type="submit" data-p92-action="complete">完成本题</button>'
            "</form>"
        )
    return (
        '<aside id="p92-taskbar" role="region" aria-label="当前实验任务">'
        '<div class="p92-row"><div>'
        f"<strong>任务 {task_id}：{_esc(task['title'])}</strong>"
        f"<p>{_esc(task['prompt'])}</p>"
        '<p class="p92-boundary">只完成当前任务，不要继续下一阶段。</p>'
        '</div><div><div id="p92-clock" '
        f'data-start="{_esc(started_at)}">计时 00:00</div>{complete}</div>'
        "</div></aside>"
    )


def _event_script(secret: str, task_id: str) -> str:
    safe_secret = json.dumps(secret)
    safe_task = json.dumps(task_id)
    return f"""
<script id="p92-events">
(()=>{{
const secret={safe_secret},task={safe_task};
const emit=(type,detail={{}})=>fetch('/p92/event',{{
 method:'POST',headers:{{'Content-Type':'application/json','X-P92-Session':secret}},
 body:JSON.stringify({{type,detail,task}}),keepalive:true
}}).catch(()=>{{}});
const bar=document.getElementById('p92-taskbar');
const clock=document.getElementById('p92-clock');
if(clock){{const start=Date.parse(clock.dataset.start);setInterval(()=>{{
 const seconds=Math.max(0,Math.floor((Date.now()-start)/1000));
 clock.textContent='计时 '+String(Math.floor(seconds/60)).padStart(2,'0')+':'+
 String(seconds%60).padStart(2,'0');}},1000);}}
emit('page_load',{{path:location.pathname,task_prompt_visible:!!bar}});
document.querySelectorAll('details').forEach(node=>node.addEventListener('toggle',()=>emit(
 node.open?'technical_details_open':'technical_details_close',
 {{summary:(node.querySelector('summary')||{{textContent:''}}).textContent.trim()}}
)));
document.addEventListener('change',event=>{{
 if(event.target.matches('input[type=radio][name^="decision:"]')){{
   emit('option_selected',{{option_id:event.target.value}});
 }}
}});
document.addEventListener('click',event=>{{
 const link=event.target.closest('a[href="/final"]');
 if(link)emit('final_decision_link_click');
 const button=event.target.closest('button');
 if(!button)return;
 const action=button.formAction?new URL(button.formAction).pathname:'';
 const types={{'/draft':'ui_save_click','/preview':'ui_preview_click',
 '/execute':'ui_execute_click','/p92/complete':'ui_task_complete_click',
 '/final/preview':'ui_final_decision_click','/final/execute':'ui_final_decision_execute_click'}};
 if(types[action])emit(types[action]);
}});
window.addEventListener('error',event=>emit('browser_error',{{message:String(event.message||'error')}}));
}})();
</script>
"""


def inject_html(
    backend_html: str,
    *,
    task_id: str,
    task: Mapping[str, Any],
    secret: str,
    started_at: str,
    ended: bool,
    overlay: str | None = None,
) -> str:
    bar = _taskbar(
        task_id,
        task,
        secret=secret,
        started_at=started_at,
        show_complete=not bool(task["action_task"]),
        ended=ended,
    )
    lock = (
        f'<div id="p92-lock"><div class="p92-panel">{overlay}</div></div>'
        if overlay
        else ""
    )
    additions = TASKBAR_CSS + bar + lock
    if "<body" in backend_html:
        close = backend_html.find(">", backend_html.find("<body"))
        backend_html = backend_html[: close + 1] + additions + backend_html[close + 1 :]
    else:
        backend_html = additions + backend_html
    script = _event_script(secret, task_id)
    if "</body>" in backend_html:
        backend_html = backend_html.replace("</body>", script + "</body>", 1)
    else:
        backend_html += script
    return backend_html


def standalone_page(content: str) -> str:
    return (
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>P92 当前任务</title></head><body>"
        '<main style="width:min(900px,calc(100% - 24px));margin:24px auto">'
        "<section><h1>P92 当前任务</h1></section></main></body></html>"
    )


@dataclass
class ProxyState:
    package_root: Path
    project_root: Path
    work_root: Path
    repo_root: Path
    records_root: Path
    state_path: Path
    task_id: str
    task: dict[str, Any]
    session_id: str
    participant_id: str
    attempt_id: str
    attempt_number: int
    technical_rerun: bool
    backend_port: int
    proxy_port: int
    backend_pid: int
    secret: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    start_utc: str = field(default_factory=utc_now)
    page_first_loaded_utc: str | None = None
    ended: bool = False
    finalized: bool = False
    phase: str = "active"
    completion_answers: dict[str, str] = field(default_factory=dict)
    automatic_stop_reason: str = ""
    after_snapshot: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        source = str(self.repo_root / "src")
        if source not in sys.path:
            sys.path.insert(0, source)
        from agm.vnext.service import GovernanceService

        self.service = GovernanceService(
            self.project_root,
            work_root=self.work_root,
        )
        self.before_snapshot = snapshot_case(
            self.service, self.task["case_id"]
        )
        self.records = RecordStore(
            self.records_root,
            session_id=self.session_id,
            participant_id=self.participant_id,
        )
        self.write_state()

    def write_state(self) -> None:
        atomic_write_json(
            self.state_path,
            {
                "session_id": self.session_id,
                "attempt_id": self.attempt_id,
                "task_id": self.task_id,
                "phase": self.phase,
                "ended": self.ended,
                "finalized": self.finalized,
                "automatic_stop_reason": self.automatic_stop_reason,
                "started_at": self.start_utc,
            },
        )

    def event(self, event_type: str, detail: Mapping[str, Any] | None = None) -> None:
        self.records.event(
            attempt_id=self.attempt_id,
            task_id=self.task_id,
            event_type=event_type,
            detail=detail,
        )
        if event_type == "page_load" and not self.page_first_loaded_utc:
            self.page_first_loaded_utc = utc_now()

    def stop_backend_actions(self, reason: str) -> None:
        if not self.ended:
            self.after_snapshot = snapshot_case(
                self.service, self.task["case_id"]
            )
            self.ended = True
            self.automatic_stop_reason = reason
            self.phase = (
                "mastery"
                if self.task_id == "T0"
                else "feedback"
            )
            self.write_state()

    def finalize(self, feedback: Mapping[str, Any]) -> dict[str, Any]:
        if self.finalized:
            raise RuntimeError("Attempt already finalized.")
        after = self.after_snapshot or snapshot_case(
            self.service, self.task["case_id"]
        )
        payload = self.records.finalize(
            task_id=self.task_id,
            task=self.task,
            attempt_id=self.attempt_id,
            attempt_number=self.attempt_number,
            start_utc=self.start_utc,
            page_first_loaded_utc=self.page_first_loaded_utc,
            before=self.before_snapshot,
            after=after,
            completion_answers=self.completion_answers,
            automatic_stop_reason=self.automatic_stop_reason,
            feedback=feedback,
            ports={
                "proxy_port": self.proxy_port,
                "backend_port": self.backend_port,
                "backend_pid": self.backend_pid,
                "proxy_pid": __import__("os").getpid(),
            },
            technical_rerun=self.technical_rerun,
        )
        self.finalized = True
        if self.task_id == "T0" and not (
            payload["objective_exact_success"]
            and all(
                self.completion_answers.get(item["id"]) == item["correct"]
                for item in self.task["mastery_questions"]
            )
        ):
            self.phase = "retry_requested"
        elif self.task_id == "T4":
            self.phase = "debrief"
        else:
            self.phase = "completed"
        self.write_state()
        return payload


def _handler_class(state: ProxyState) -> type[BaseHTTPRequestHandler]:
    class P92ProxyHandler(BaseHTTPRequestHandler):
        server_version = "P92ExperimentProxy/1"

        def _send(
            self,
            status: int,
            body: str | bytes,
            *,
            content_type: str = "text/html; charset=utf-8",
            headers: Mapping[str, str] | None = None,
        ) -> None:
            payload = body.encode("utf-8") if isinstance(body, str) else body
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            if content_type.startswith("text/html"):
                self.send_header("Content-Security-Policy", P92_CSP)
            for key, value in (headers or {}).items():
                if key.lower() not in {"content-length", "content-security-policy"}:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(payload)

        def _read_bytes(self) -> bytes:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise ValueError("Invalid Content-Length") from exc
            if length <= 0 or length > MAX_BODY:
                raise ValueError("Invalid request body size")
            return self.rfile.read(length)

        def _form(self) -> dict[str, str]:
            content_type = self.headers.get("Content-Type", "").split(";", 1)[0]
            if content_type != "application/x-www-form-urlencoded":
                raise ValueError("P92 endpoint requires form-encoded POST.")
            values = parse_qs(
                self._read_bytes().decode("utf-8"),
                keep_blank_values=True,
                strict_parsing=True,
            )
            form = {key: items[0].strip() for key, items in values.items()}
            if not secrets.compare_digest(
                form.get("p92_secret", ""), state.secret
            ):
                raise ValueError("Invalid P92 session control token.")
            return form

        def _validate_host(self) -> None:
            host = urlparse("//" + self.headers.get("Host", ""))
            if (
                host.hostname not in {"127.0.0.1", "localhost"}
                or (host.port or 80) != state.proxy_port
            ):
                raise ValueError("P92 proxy accepts only its loopback origin.")

        def _backend(
            self, method: str, path: str, body: bytes | None = None
        ) -> tuple[int, dict[str, str], bytes]:
            connection = http.client.HTTPConnection(
                "127.0.0.1", state.backend_port, timeout=15
            )
            headers = {
                "Host": f"127.0.0.1:{state.backend_port}",
                "User-Agent": "P92-Experiment-Proxy/1",
            }
            if method == "POST":
                headers["Origin"] = f"http://127.0.0.1:{state.backend_port}"
                headers["Content-Type"] = self.headers.get(
                    "Content-Type", "application/x-www-form-urlencoded"
                )
                headers["Content-Length"] = str(len(body or b""))
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            payload = response.read()
            observed_headers = {key: value for key, value in response.getheaders()}
            status = response.status
            connection.close()
            return status, observed_headers, payload

        def _locked_overlay(self) -> str:
            if state.phase == "mastery":
                return _question_form(
                    title="训练理解检查",
                    questions=state.task["mastery_questions"],
                    action="/p92/mastery",
                    secret=state.secret,
                )
            if state.phase == "feedback":
                return _feedback_form(state.secret)
            if state.phase == "debrief":
                return _debrief_form(load_config(state.package_root), state.secret)
            if state.phase == "retry_requested":
                return (
                    "<h2>本次训练需要重试</h2>"
                    "<p>研究者将重置训练案例。请勿继续操作当前页面。</p>"
                )
            return (
                "<h2>本题已经结束</h2>"
                "<p>请停止操作并通知研究者。</p>"
            )

        def _participant_page(self, content: str) -> str:
            return inject_html(
                content,
                task_id=state.task_id,
                task=state.task,
                secret=state.secret,
                started_at=state.start_utc,
                ended=state.ended,
                overlay=self._locked_overlay() if state.ended else None,
            )

        def do_GET(self) -> None:  # noqa: N802
            try:
                self._validate_host()
            except ValueError as exc:
                self._send(HTTPStatus.BAD_REQUEST, _esc(exc))
                return
            parsed = urlparse(self.path)
            if parsed.query:
                self._send(HTTPStatus.NOT_FOUND, "Not found")
                return
            if parsed.path == "/p92/health":
                self._send(
                    HTTPStatus.OK,
                    json.dumps(
                        {
                            "ready": True,
                            "task_id": state.task_id,
                            "ended": state.ended,
                            "phase": state.phase,
                        }
                    ),
                    content_type="application/json; charset=utf-8",
                )
                return
            if parsed.path.startswith("/p92/"):
                self._send(HTTPStatus.NOT_FOUND, "Not found")
                return
            if state.ended:
                self._send(
                    HTTPStatus.OK,
                    self._participant_page(standalone_page("")),
                )
                return
            try:
                status, headers, payload = self._backend("GET", parsed.path)
                content_type = headers.get(
                    "Content-Type", "application/octet-stream"
                )
                if content_type.startswith("text/html"):
                    rendered = payload.decode("utf-8", errors="strict")
                    payload = self._participant_page(rendered).encode("utf-8")
                self._send(
                    status,
                    payload,
                    content_type=content_type,
                    headers={
                        key: value
                        for key, value in headers.items()
                        if key.lower() in {"location"}
                    },
                )
            except (OSError, UnicodeError, http.client.HTTPException) as exc:
                error = standalone_page("")
                self._send(
                    HTTPStatus.BAD_GATEWAY,
                    inject_html(
                        error,
                        task_id=state.task_id,
                        task=state.task,
                        secret=state.secret,
                        started_at=state.start_utc,
                        ended=False,
                        overlay=f"<h2>页面暂时无法加载</h2><p>{_esc(exc)}</p>",
                    ),
                )

        def _p92_post(self, path: str) -> None:
            if path == "/p92/event":
                if not secrets.compare_digest(
                    self.headers.get("X-P92-Session", ""), state.secret
                ):
                    self._send(HTTPStatus.FORBIDDEN, "Forbidden")
                    return
                if self.headers.get("Content-Type", "").split(";", 1)[0] != "application/json":
                    self._send(HTTPStatus.BAD_REQUEST, "Bad request")
                    return
                payload = json.loads(self._read_bytes().decode("utf-8"))
                state.event(
                    str(payload.get("type", "unknown")),
                    payload.get("detail") if isinstance(payload.get("detail"), dict) else {},
                )
                self._send(
                    HTTPStatus.NO_CONTENT,
                    b"",
                    content_type="application/json",
                )
                return
            form = self._form()
            if path == "/p92/complete":
                if state.task["action_task"] or state.ended:
                    raise ValueError("This task cannot be ended from the task strip.")
                state.event("task_complete_click")
                state.ended = True
                state.phase = "completion_questions"
                state.automatic_stop_reason = "participant_completed_no_action_task"
                state.after_snapshot = snapshot_case(
                    state.service, state.task["case_id"]
                )
                state.write_state()
                questions = _question_form(
                    title="本题完成问题",
                    questions=state.task["completion_questions"],
                    action="/p92/completion",
                    secret=state.secret,
                )
                self._send(
                    HTTPStatus.OK,
                    self._participant_page(standalone_page("")).replace(
                        '<div id="p92-lock"><div class="p92-panel">'
                        + self._locked_overlay(),
                        '<div id="p92-lock"><div class="p92-panel">'
                        + questions,
                        1,
                    ),
                )
                return
            if path == "/p92/completion":
                if state.phase != "completion_questions":
                    raise ValueError("Completion questions are not active.")
                state.completion_answers = {
                    item["id"]: form.get(item["id"], "")
                    for item in state.task["completion_questions"]
                }
                state.event("completion_questions_submitted")
                state.phase = "feedback"
                state.write_state()
                self._send(
                    HTTPStatus.OK,
                    self._participant_page(standalone_page("")),
                )
                return
            if path == "/p92/mastery":
                if state.phase != "mastery":
                    raise ValueError("Training mastery questions are not active.")
                state.completion_answers = {
                    item["id"]: form.get(item["id"], "")
                    for item in state.task["mastery_questions"]
                }
                state.event("mastery_questions_submitted")
                correct = all(
                    state.completion_answers.get(item["id"]) == item["correct"]
                    for item in state.task["mastery_questions"]
                )
                state.phase = "feedback"
                state.write_state()
                feedback = (
                    ""
                    if correct
                    else (
                        "你刚才完成的是维护者检查。维护者检查完成后，仍需由具有"
                        "最终决定权限的人类维护者决定是否接受贡献。"
                    )
                )
                page = self._participant_page(standalone_page(""))
                page = page.replace(
                    _feedback_form(state.secret),
                    _feedback_form(state.secret, feedback),
                    1,
                )
                self._send(HTTPStatus.OK, page)
                return
            if path == "/p92/feedback":
                if state.phase != "feedback":
                    raise ValueError("Participant feedback is not active.")
                difficulty = int(form.get("difficulty", "0"))
                confidence = int(form.get("confidence", "0"))
                if difficulty not in range(1, 8) or confidence not in range(1, 6):
                    raise ValueError("Feedback rating is outside the allowed range.")
                state.event("participant_feedback_submitted")
                state.finalize(
                    {
                        "difficulty": difficulty,
                        "confidence": confidence,
                        "comment": form.get("comment", ""),
                    }
                )
                self._send(
                    HTTPStatus.OK,
                    self._participant_page(standalone_page("")),
                )
                return
            if path == "/p92/debrief":
                if state.phase != "debrief":
                    raise ValueError("Debrief is not active.")
                config = load_config(state.package_root)
                answers = {
                    f"q{index}": form.get(f"q{index}", "")
                    for index, _ in enumerate(
                        config["debrief_questions"], start=1
                    )
                }
                state.event("debrief_submitted")
                state.records.write_debrief(answers)
                state.phase = "completed"
                state.write_state()
                self._send(
                    HTTPStatus.OK,
                    self._participant_page(standalone_page("")),
                )
                return
            raise ValueError("Unknown P92 control endpoint.")

        def do_POST(self) -> None:  # noqa: N802
            try:
                self._validate_host()
                parsed = urlparse(self.path)
                if parsed.query:
                    raise ValueError("Query parameters are not accepted.")
                if parsed.path.startswith("/p92/"):
                    self._p92_post(parsed.path)
                    return
                if state.ended:
                    self._send(
                        HTTPStatus.LOCKED,
                        self._participant_page(standalone_page("")),
                    )
                    return
                body = self._read_bytes()
                event_type = BACKEND_MUTATIONS.get(parsed.path)
                if event_type:
                    state.event(event_type, {"path": parsed.path, "source": "proxy"})
                status, headers, payload = self._backend(
                    "POST", parsed.path, body
                )
                content_type = headers.get(
                    "Content-Type", "application/octet-stream"
                )
                if parsed.path == "/execute":
                    state.stop_backend_actions(
                        "first_execute_success"
                        if status < 400
                        else "first_execute_error"
                    )
                if content_type.startswith("text/html"):
                    rendered = payload.decode("utf-8", errors="strict")
                    payload = self._participant_page(rendered).encode("utf-8")
                self._send(
                    status,
                    payload,
                    content_type=content_type,
                    headers={
                        key: value
                        for key, value in headers.items()
                        if key.lower() in {"location"}
                    },
                )
            except (
                ValueError,
                json.JSONDecodeError,
                UnicodeError,
                OSError,
                http.client.HTTPException,
            ) as exc:
                self._send(
                    HTTPStatus.BAD_REQUEST,
                    self._participant_page(
                        "<!doctype html><html lang=\"zh-CN\"><body>"
                        f"<h1>请求未完成</h1><p>{_esc(exc)}</p></body></html>"
                    ),
                )

        def log_message(self, format: str, *args: Any) -> None:
            return

    return P92ProxyHandler


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--records-root", type=Path, required=True)
    parser.add_argument("--state-file", type=Path, required=True)
    parser.add_argument("--task", choices=TASK_IDS, required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--participant-id", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--attempt-number", type=int, required=True)
    parser.add_argument("--backend-port", type=int, required=True)
    parser.add_argument("--proxy-port", type=int, required=True)
    parser.add_argument("--backend-pid", type=int, required=True)
    parser.add_argument("--session-marker", required=True)
    parser.add_argument("--technical-rerun", action="store_true")
    args = parser.parse_args()
    task = task_config(args.task, args.package_root)
    state = ProxyState(
        package_root=args.package_root.resolve(),
        project_root=args.project_root.resolve(),
        work_root=args.work_root.resolve(),
        repo_root=args.repo_root.resolve(),
        records_root=args.records_root.resolve(),
        state_path=args.state_file.resolve(),
        task_id=args.task,
        task=task,
        session_id=args.session_id,
        participant_id=args.participant_id,
        attempt_id=args.attempt_id,
        attempt_number=args.attempt_number,
        technical_rerun=args.technical_rerun,
        backend_port=args.backend_port,
        proxy_port=args.proxy_port,
        backend_pid=args.backend_pid,
    )
    server = ThreadingHTTPServer(
        ("127.0.0.1", args.proxy_port),
        _handler_class(state),
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
