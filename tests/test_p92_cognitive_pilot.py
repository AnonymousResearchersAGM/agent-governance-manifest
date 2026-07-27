from __future__ import annotations

import http.client
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import zipfile
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACKAGE = ROOT / "experiments" / "p92_cognitive_pilot"
P92_SCRIPTS = SOURCE_PACKAGE / "scripts"
for candidate in (ROOT / "src", P92_SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import build_delivery
import experiment_proxy
import export_p92_results
import run_p92_session
import stop_p92
import verify_p92_package
from common import (
    ARTIFACT_COMMIT,
    POLICY_FINGERPRINT,
    answers_correct,
    find_free_loopback_port,
    load_config,
    no_forbidden_prompt_leak,
    reset_task_runtime,
    sha256_file,
    verify_baseline_manifest,
)
from records import RecordStore, objective_score, snapshot_case

from agm.vnext.briefing.actions.draft import ReviewDraftStore
from agm.vnext.briefing.actions.preview import PreviewTokenRegistry
from agm.vnext.briefing.actions.server import _handler_class
from agm.vnext.guidance import ActorContext
from agm.vnext.service import GovernanceService


def copy_package(tmp_path: Path) -> Path:
    destination = tmp_path / "P92_AGM_Human_Work_Cognitive_Pilot"
    shutil.copytree(
        SOURCE_PACKAGE,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "runtime", "records"),
    )
    (destination / "runtime").mkdir()
    (destination / "records").mkdir()
    return destination


class LiveStack:
    def __init__(
        self,
        *,
        package: Path,
        task_id: str,
        service: GovernanceService,
        state: experiment_proxy.ProxyState,
        backend,
        proxy,
        threads,
    ):
        self.package = package
        self.task_id = task_id
        self.service = service
        self.state = state
        self.backend = backend
        self.proxy = proxy
        self.threads = threads
        self.origin = f"http://127.0.0.1:{proxy.server_port}"

    def request(
        self,
        method: str,
        path: str,
        *,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, dict[str, str], bytes]:
        connection = http.client.HTTPConnection(
            "127.0.0.1", self.proxy.server_port, timeout=10
        )
        supplied = {"Origin": self.origin}
        supplied.update(headers or {})
        connection.request(method, path, body=body, headers=supplied)
        response = connection.getresponse()
        payload = response.read()
        observed = {key: value for key, value in response.getheaders()}
        status = response.status
        connection.close()
        return status, observed, payload

    def form(
        self,
        path: str,
        values: dict[str, str],
    ) -> tuple[int, dict[str, str], bytes]:
        body = urllib.parse.urlencode(values).encode("utf-8")
        return self.request(
            "POST",
            path,
            body=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": str(len(body)),
            },
        )

    def get_html(self, path: str = "/") -> str:
        status, _, payload = self.request("GET", path)
        assert status == 200
        return payload.decode("utf-8")

    def csrf(self) -> str:
        rendered = self.get_html()
        match = re.search(r'name="csrf_token" value="([^"]+)"', rendered)
        assert match
        return match.group(1)

    def preview(
        self,
        option: str,
        reason: str = "",
    ) -> tuple[str, str]:
        csrf = self.csrf()
        values = {
            "csrf_token": csrf,
            "decision:1": option,
        }
        if reason:
            values[f"reason:1:{option}"] = reason
        status, _, payload = self.form("/preview", values)
        assert status == 200, payload.decode("utf-8")
        rendered = payload.decode("utf-8")
        match = re.search(r'name="preview_token" value="([^"]+)"', rendered)
        assert match
        return csrf, match.group(1)

    def execute(
        self, csrf: str, preview_token: str
    ) -> tuple[int, str]:
        status, _, payload = self.form(
            "/execute",
            {
                "csrf_token": csrf,
                "preview_token": preview_token,
            },
        )
        return status, payload.decode("utf-8")

    def feedback(self) -> tuple[int, str]:
        status, _, payload = self.form(
            "/p92/feedback",
            {
                "p92_secret": self.state.secret,
                "difficulty": "3",
                "confidence": "4",
                "comment": "测试反馈",
            },
        )
        return status, payload.decode("utf-8")

    def close(self) -> None:
        self.proxy.shutdown()
        self.backend.shutdown()
        self.proxy.server_close()
        self.backend.server_close()
        for thread in self.threads:
            thread.join(timeout=5)


@contextmanager
def live_stack(tmp_path: Path, task_id: str, *, ready: bool = False):
    package = copy_package(tmp_path)
    runtime = reset_task_runtime(
        task_id,
        repo_root=ROOT,
        root=package,
    )
    project = runtime / "project"
    work = project / "p92-work"
    task = load_config(package)["tasks"][task_id]
    service = GovernanceService(project, work_root=work)
    if ready:
        service.verify(
            task["case_id"],
            actor="p92-human-maintainer",
            role="maintainer",
            reason="Test fixture completes the scoped review.",
        )
    csrf = "p92-test-csrf"
    backend = experiment_proxy.ThreadingHTTPServer(
        ("127.0.0.1", 0),
        _handler_class(
            service,
            case_id=task["case_id"],
            actor=ActorContext(
                "p92-human-maintainer", "maintainer", True
            ),
            csrf_token=csrf,
            token_registry=PreviewTokenRegistry(),
            draft_store=ReviewDraftStore(service.storage),
        ),
    )
    backend_thread = threading.Thread(
        target=backend.serve_forever, daemon=True
    )
    backend_thread.start()
    proxy_port = find_free_loopback_port()
    state = experiment_proxy.ProxyState(
        package_root=package,
        project_root=project,
        work_root=work,
        repo_root=ROOT,
        records_root=package / "records",
        state_path=runtime / "proxy_state.json",
        task_id=task_id,
        task=task,
        session_id="p92-test-session",
        participant_id="P92-TEST",
        attempt_id=f"p92-test-{task_id}",
        attempt_number=1,
        technical_rerun=False,
        backend_port=backend.server_port,
        proxy_port=proxy_port,
        backend_pid=os.getpid(),
    )
    proxy = experiment_proxy.ThreadingHTTPServer(
        ("127.0.0.1", proxy_port),
        experiment_proxy._handler_class(state),
    )
    proxy_thread = threading.Thread(target=proxy.serve_forever, daemon=True)
    proxy_thread.start()
    stack = LiveStack(
        package=package,
        task_id=task_id,
        service=service,
        state=state,
        backend=backend,
        proxy=proxy,
        threads=(proxy_thread, backend_thread),
    )
    try:
        yield stack
    finally:
        stack.close()


def answer_form(
    stack: LiveStack,
    path: str,
    answers: dict[str, str],
) -> tuple[int, str]:
    values = {"p92_secret": stack.state.secret, **answers}
    status, _, payload = stack.form(path, values)
    return status, payload.decode("utf-8")


def test_p92_is_explicitly_excluded_from_formal_sample():
    config = load_config(SOURCE_PACKAGE)
    assert config["formal_sample"] is False
    assert config["exclusion_reason"] == (
        "Internal cognitive pilot for participant-facing human-work "
        "compilation before formal experiment freeze."
    )


def test_task_order_is_fixed():
    assert load_config(SOURCE_PACKAGE)["task_order"] == [
        "T0",
        "T1",
        "T2",
        "T3",
        "T4",
    ]


def test_task_prompts_do_not_leak_expected_answers():
    assert no_forbidden_prompt_leak(load_config(SOURCE_PACKAGE))


def test_artifact_commit_mismatch_is_rejected(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    package = tmp_path / "package"
    (repo / ".git").mkdir(parents=True)
    package.mkdir()
    monkeypatch.setattr(
        verify_p92_package,
        "_git",
        lambda *_args: "not-the-frozen-commit",
    )
    with pytest.raises(RuntimeError, match="commit mismatch"):
        verify_p92_package.verify(repo, package)


def test_dirty_repo_is_rejected(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    package = tmp_path / "package"
    (repo / ".git").mkdir(parents=True)
    package.mkdir()

    def fake_git(_repo, *args):
        return (
            ARTIFACT_COMMIT
            if args[:2] == ("rev-parse", "HEAD")
            else "?? dirty.txt"
        )

    monkeypatch.setattr(verify_p92_package, "_git", fake_git)
    with pytest.raises(RuntimeError, match="dirty"):
        verify_p92_package.verify(repo, package)


def test_policy_fingerprint_mismatch_is_rejected(tmp_path, monkeypatch):
    repo = ROOT
    package = tmp_path / "package"
    package.mkdir()
    monkeypatch.setattr(
        verify_p92_package,
        "_git",
        lambda _repo, *args: (
            ARTIFACT_COMMIT
            if args[:2] == ("rev-parse", "HEAD")
            else ""
        ),
    )
    import agm.vnext.config as config_module

    monkeypatch.setattr(
        config_module,
        "load_vnext_config",
        lambda _root: SimpleNamespace(policy_fingerprint="wrong"),
    )
    with pytest.raises(RuntimeError, match="fingerprint mismatch"):
        verify_p92_package.verify(repo, package)


def test_baseline_hashes_verify():
    manifest = verify_baseline_manifest(SOURCE_PACKAGE)
    assert manifest["policy_fingerprint"] == POLICY_FINGERPRINT
    assert len(manifest["files"]) > 40


def test_baseline_hash_mismatch_is_rejected(tmp_path):
    package = copy_package(tmp_path)
    target = next(
        path
        for path in (package / "baseline").rglob("case.yml")
    )
    target.write_text(target.read_text(encoding="utf-8") + "# changed\n")
    with pytest.raises(RuntimeError, match="baseline hash mismatch"):
        verify_baseline_manifest(package)


def test_runtime_is_outside_frozen_repo(tmp_path):
    package = copy_package(tmp_path)
    runtime = reset_task_runtime("T0", repo_root=ROOT, root=package)
    assert ROOT.resolve() not in runtime.resolve().parents
    assert runtime.resolve() != ROOT.resolve()


def test_runtime_reset_does_not_change_baseline(tmp_path):
    package = copy_package(tmp_path)
    before = json.dumps(verify_baseline_manifest(package), sort_keys=True)
    reset_task_runtime("T2", repo_root=ROOT, root=package)
    after = json.dumps(verify_baseline_manifest(package), sort_keys=True)
    assert before == after


def test_proxy_binds_only_loopback(tmp_path):
    with live_stack(tmp_path, "T1") as stack:
        assert stack.proxy.server_address[0] == "127.0.0.1"
        assert "0.0.0.0" not in Path(
            experiment_proxy.__file__
        ).read_text(encoding="utf-8")


def test_proxy_forwards_get_and_injects_task_strip(tmp_path):
    with live_stack(tmp_path, "T0") as stack:
        rendered = stack.get_html()
        assert "维护者逐项检查" in rendered
        assert 'id="p92-taskbar"' in rendered
        assert stack.state.task["prompt"] in rendered


def test_task_strip_persists_on_backend_error_page(tmp_path):
    with live_stack(tmp_path, "T1") as stack:
        status, _, payload = stack.request("GET", "/does-not-exist")
        assert status == 404
        assert 'id="p92-taskbar"' in payload.decode("utf-8")


def test_proxy_post_preserves_backend_csrf_and_origin_checks(tmp_path):
    with live_stack(tmp_path, "T0") as stack:
        csrf, token = stack.preview("sufficient")
        assert csrf == "p92-test-csrf"
        assert token


def test_missing_backend_csrf_is_still_rejected(tmp_path):
    with live_stack(tmp_path, "T0") as stack:
        status, _, payload = stack.form(
            "/preview",
            {"decision:1": "sufficient"},
        )
        assert status == 400
        assert "CSRF" in payload.decode("utf-8")
        assert stack.state.ended is False


def test_execute_without_valid_preview_token_is_rejected_and_locked(tmp_path):
    with live_stack(tmp_path, "T0") as stack:
        status, _, payload = stack.form(
            "/execute",
            {
                "csrf_token": stack.csrf(),
                "preview_token": "forged",
            },
        )
        assert status == 400
        assert stack.state.ended is True
        assert 'id="p92-lock"' in payload.decode("utf-8")


def test_task_strip_is_present_on_preview(tmp_path):
    with live_stack(tmp_path, "T0") as stack:
        _, token = stack.preview("sufficient")
        assert token
        events = stack.state.records.events_for_attempt(
            stack.state.attempt_id
        )
        assert any(item["event_type"] == "preview_click" for item in events)


def test_first_execute_locks_result_page(tmp_path):
    with live_stack(tmp_path, "T0") as stack:
        csrf, token = stack.preview("sufficient")
        status, rendered = stack.execute(csrf, token)
        assert status == 200
        assert "你的维护者检查已提交" in rendered
        assert 'id="p92-taskbar"' in rendered
        assert 'id="p92-lock"' in rendered
        assert stack.state.automatic_stop_reason == "first_execute_success"


def test_locked_page_rejects_second_backend_mutation(tmp_path):
    with live_stack(tmp_path, "T0") as stack:
        csrf, token = stack.preview("sufficient")
        assert stack.execute(csrf, token)[0] == 200
        status, _, _ = stack.form(
            "/execute",
            {"csrf_token": csrf, "preview_token": token},
        )
        assert status == 423
        case = stack.service.storage.load_case(
            stack.state.task["case_id"]
        )
        assert case.state == "ready_for_human_decision"


def test_error_execute_also_locks(tmp_path):
    with live_stack(tmp_path, "T2") as stack:
        status, _, _ = stack.form(
            "/execute",
            {
                "csrf_token": stack.csrf(),
                "preview_token": "wrong",
            },
        )
        assert status == 400
        assert stack.state.phase == "feedback"
        assert stack.state.automatic_stop_reason == "first_execute_error"


def test_technical_details_event_is_recorded(tmp_path):
    with live_stack(tmp_path, "T1") as stack:
        payload = json.dumps(
            {
                "type": "technical_details_open",
                "detail": {"summary": "治理过程与技术详情"},
            }
        ).encode()
        status, _, _ = stack.request(
            "POST",
            "/p92/event",
            body=payload,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(payload)),
                "X-P92-Session": stack.state.secret,
            },
        )
        assert status == 204
        assert stack.state.records.events_for_attempt(
            stack.state.attempt_id
        )[-1]["event_type"] == "technical_details_open"


def test_no_action_task_uses_taskbar_completion(tmp_path):
    with live_stack(tmp_path, "T1") as stack:
        status, _, payload = stack.form(
            "/p92/complete",
            {"p92_secret": stack.state.secret},
        )
        rendered = payload.decode("utf-8")
        assert status == 200
        assert "页面是否要求你现在执行维护者操作" in rendered
        assert stack.state.phase == "completion_questions"
        assert stack.state.before_snapshot == stack.state.after_snapshot


def test_t1_completion_answers_score_objectively(tmp_path):
    with live_stack(tmp_path, "T1") as stack:
        assert stack.form(
            "/p92/complete", {"p92_secret": stack.state.secret}
        )[0] == 200
        status, _ = answer_form(
            stack,
            "/p92/completion",
            {
                "requires_action": "不需要",
                "responsible_party": "贡献侧",
            },
        )
        assert status == 200
        assert stack.feedback()[0] == 200
        record = json.loads(
            (stack.package / "records" / "P92_session_log.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()[-1]
        )
        assert record["objective_exact_success"] is True
        assert record["transition_count_before"] == record[
            "transition_count_after"
        ]


def test_t3_completion_creates_no_mutation_or_finding(tmp_path):
    with live_stack(tmp_path, "T3") as stack:
        assert stack.form(
            "/p92/complete", {"p92_secret": stack.state.secret}
        )[0] == 200
        assert answer_form(
            stack,
            "/p92/completion",
            {
                "attempt_effect": "未生效",
                "needs_repeat": "不需要",
            },
        )[0] == 200
        assert stack.feedback()[0] == 200
        record = json.loads(
            (stack.package / "records" / "P92_session_log.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()[-1]
        )
        assert record["objective_exact_success"] is True
        assert record["new_finding_count"] == 0
        assert record["review_submission_count_after"] == 0


def test_t0_wrong_mastery_requests_training_retry(tmp_path):
    with live_stack(tmp_path, "T0") as stack:
        csrf, token = stack.preview("sufficient")
        assert stack.execute(csrf, token)[0] == 200
        assert answer_form(
            stack,
            "/p92/mastery",
            {"step": "最终接受贡献", "accepted": "是"},
        )[0] == 200
        assert stack.feedback()[0] == 200
        assert stack.state.phase == "retry_requested"


def test_t0_correct_mastery_completes_training(tmp_path):
    with live_stack(tmp_path, "T0") as stack:
        csrf, token = stack.preview("sufficient")
        assert stack.execute(csrf, token)[0] == 200
        assert answer_form(
            stack,
            "/p92/mastery",
            {"step": "维护者检查", "accepted": "否"},
        )[0] == 200
        assert stack.feedback()[0] == 200
        assert stack.state.phase == "completed"
        record = json.loads(
            (stack.package / "records" / "P92_session_log.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()[-1]
        )
        assert record["scored"] is False
        assert record["state_after"] == "ready_for_human_decision"


def test_scored_task_wrong_selection_ends_without_retry(tmp_path):
    with live_stack(tmp_path, "T2") as stack:
        csrf, token = stack.preview("sufficient")
        assert stack.execute(csrf, token)[0] == 200
        assert stack.feedback()[0] == 200
        assert stack.state.phase == "completed"
        record = json.loads(
            (stack.package / "records" / "P92_session_log.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()[-1]
        )
        assert record["objective_exact_success"] is False


def test_t2_supplement_reaches_scoped_repair(tmp_path):
    with live_stack(tmp_path, "T2") as stack:
        before = snapshot_case(
            stack.service, stack.state.task["case_id"]
        )
        csrf, token = stack.preview(
            "supplement", "说明没有覆盖实际子智能体行动和委派范围。"
        )
        assert stack.execute(csrf, token)[0] == 200
        after = snapshot_case(
            stack.service, stack.state.task["case_id"]
        )
        exact, safe, details = objective_score(
            "T2", stack.state.task, before, after, {}
        )
        assert exact and safe
        assert details["affected_obligation_count"] == 1
        assert after["state"] == "repair_requested"


def test_t4_material_risk_creates_high_blocking_finding(tmp_path):
    with live_stack(tmp_path, "T4") as stack:
        before = snapshot_case(
            stack.service, stack.state.task["case_id"]
        )
        csrf, token = stack.preview(
            "material-risk",
            "权限撤销后旧令牌仍可访问受限接口，关键认证回归失败。",
        )
        assert stack.execute(csrf, token)[0] == 200
        after = snapshot_case(
            stack.service, stack.state.task["case_id"]
        )
        exact, safe, details = objective_score(
            "T4", stack.state.task, before, after, {}
        )
        assert exact and safe
        assert details["new_finding_severity"] == "high"
        assert details["new_finding_blocking"] is True
        assert after["final_decision"] is None


def test_records_are_append_only(tmp_path):
    store = RecordStore(
        tmp_path / "records",
        session_id="session",
        participant_id="P92",
    )
    before = {
        "state": "evidence_incomplete",
        "transition_count": 1,
        "transition_names": ["mark_evidence_state"],
        "review_submission_count": 0,
        "submissions": [],
        "finding_count": 0,
        "findings": [],
        "denied_attempt_count": 0,
        "final_decision": None,
        "evidence": {},
    }
    task = load_config(SOURCE_PACKAGE)["tasks"]["T1"]
    kwargs = dict(
        task_id="T1",
        task=task,
        attempt_id="attempt",
        attempt_number=1,
        start_utc="2026-07-27T00:00:00Z",
        page_first_loaded_utc=None,
        before=before,
        after=before,
        completion_answers={
            "requires_action": "不需要",
            "responsible_party": "贡献侧",
        },
        automatic_stop_reason="participant_completed_no_action_task",
        feedback={"difficulty": 1, "confidence": 5, "comment": ""},
        ports={},
    )
    store.finalize(**kwargs)
    with pytest.raises(RuntimeError, match="append-only"):
        store.finalize(**kwargs)


def test_researcher_note_cannot_override_objective_score():
    task = load_config(SOURCE_PACKAGE)["tasks"]["T1"]
    snapshot = {
        "state": "evidence_incomplete",
        "transition_count": 3,
        "transition_names": ["a", "b", "c"],
        "review_submission_count": 0,
        "submissions": [],
        "finding_count": 0,
        "findings": [],
        "denied_attempt_count": 0,
        "final_decision": None,
        "evidence": {},
    }
    exact, _, _ = objective_score(
        "T1",
        task,
        snapshot,
        snapshot,
        {"requires_action": "需要", "responsible_party": "维护者"},
    )
    researcher_adjudication_note = "研究者认为参与者表现不错"
    assert researcher_adjudication_note
    assert exact is False


def test_resume_reuses_unfinished_session(tmp_path):
    package = copy_package(tmp_path)
    session = run_p92_session._load_or_create_session(
        root=package,
        repo_root=ROOT,
        participant="P92",
        resume=False,
    )
    resumed = run_p92_session._load_or_create_session(
        root=package,
        repo_root=ROOT,
        participant="P92",
        resume=True,
    )
    assert resumed["session_id"] == session["session_id"]


def test_stop_p92_does_not_kill_unrelated_python(tmp_path):
    package = copy_package(tmp_path)
    process = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        creationflags=(
            subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        ),
    )
    try:
        (package / "runtime" / "processes.json").write_text(
            json.dumps(
                {
                    "session_marker": "P92_MARKER_NOT_IN_PROCESS",
                    "processes": [{"kind": "unrelated", "pid": process.pid}],
                }
            ),
            encoding="utf-8",
        )
        result = stop_p92.stop_marked_processes(package)
        assert result["stopped"] == []
        assert result["skipped"][0]["pid"] == process.pid
        assert process.poll() is None
    finally:
        process.terminate()
        process.wait(timeout=10)


def test_stop_p92_discovers_marker_bearing_wrapper_and_child(tmp_path):
    package = copy_package(tmp_path)
    marker = f"P92_TEST_MARKER_{time.time_ns()}"
    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import time; time.sleep(30)",
            marker,
        ],
        creationflags=(
            subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        ),
    )
    try:
        (package / "runtime" / "processes.json").write_text(
            json.dumps(
                {
                    "session_marker": marker,
                    "processes": [{"kind": "test", "pid": process.pid}],
                }
            ),
            encoding="utf-8",
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(P92_SCRIPTS / "stop_p92.py"),
                "--package-root",
                str(package),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        result = json.loads(completed.stdout)
        process.wait(timeout=10)
        assert process.pid in result["stopped"]
        assert stop_p92._matching_process_ids(marker) == set()
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)


def test_export_contains_records_but_no_runtime_or_tokens(tmp_path):
    package = copy_package(tmp_path)
    (package / "package_integrity.json").write_text("{}\n", encoding="utf-8")
    (package / "records" / "P92_session_log.jsonl").write_text(
        '{"participant_id":"P92"}\n', encoding="utf-8"
    )
    result = export_p92_results.export_results(
        participant_id="P92",
        root=package,
        output_dir=tmp_path / "exports",
    )
    with zipfile.ZipFile(result["archive"]) as archive:
        names = archive.namelist()
    assert any(name.startswith("records/") for name in names)
    assert not any(name.startswith("runtime/") for name in names)
    assert not any("token" in name.lower() for name in names)


def test_delivery_package_contains_no_agm_source_or_p91_data(tmp_path):
    result = build_delivery.build(
        SOURCE_PACKAGE,
        tmp_path / "P92_AGM_Human_Work_Cognitive_Pilot",
    )
    with zipfile.ZipFile(result["archive"]) as archive:
        names = [name.lower() for name in archive.namelist()]
    assert not any(name.startswith("src/agm/") for name in names)
    assert not any("/p91" in name or name.startswith("p91") for name in names)
    assert not any(".git/" in name or ".venv/" in name for name in names)


def test_delivery_zip_is_content_deterministic(tmp_path):
    first = build_delivery.build(
        SOURCE_PACKAGE,
        tmp_path / "one" / "P92_AGM_Human_Work_Cognitive_Pilot",
    )
    second = build_delivery.build(
        SOURCE_PACKAGE,
        tmp_path / "two" / "P92_AGM_Human_Work_Cognitive_Pilot",
    )
    assert first["zip_sha256"] == second["zip_sha256"]


def test_baseline_task_states_and_item_counts():
    config = load_config(SOURCE_PACKAGE)
    expected = {
        "T0": ("awaiting_maintainer_verification", 1),
        "T1": ("evidence_incomplete", 0),
        "T2": ("awaiting_maintainer_verification", 1),
        "T3": ("awaiting_maintainer_verification", 0),
        "T4": ("awaiting_maintainer_verification", 1),
    }
    from agm.vnext.briefing.actions import compile_contextual_actions

    for task_id, (state, count) in expected.items():
        task = config["tasks"][task_id]
        service = GovernanceService(
            ROOT,
            work_root=SOURCE_PACKAGE / "baseline" / task["baseline"],
        )
        case = service.storage.load_case(task["case_id"])
        brief = service.review_brief(
            case.id, actor="p92-human-maintainer", role="maintainer"
        )
        view = compile_contextual_actions(
            review_brief=brief,
            governance_case=case,
            actor_context=ActorContext(
                "p92-human-maintainer", "maintainer", True
            ),
            policy_config=service.config,
            live_actions_enabled=True,
        )
        assert (case.state, len(view.items)) == (state, count)
        if view.items:
            assert all(
                option.authorized for option in view.items[0].options
            )


def test_t2_page_exposes_material_gap_without_task_prompt_leak(tmp_path):
    with live_stack(tmp_path, "T2") as stack:
        rendered = stack.get_html()
        assert "没有列出系统记录所涉及的子智能体行动" in rendered
        taskbar = rendered.split("</aside>", 1)[0]
        assert "请选择“要求补充或修正”" not in taskbar
        assert "正确答案" not in taskbar


def test_t4_page_exposes_high_risk_contradiction(tmp_path):
    with live_stack(tmp_path, "T4") as stack:
        rendered = stack.get_html()
        assert "权限撤销后旧令牌仍可访问受限接口" in rendered
        assert "关键认证回归测试失败" in rendered
        taskbar = rendered.split("</aside>", 1)[0]
        assert "请选择“标记重大风险”" not in taskbar
        assert "这是重大风险" not in taskbar


def test_final_decision_page_also_receives_task_strip(tmp_path):
    with live_stack(tmp_path, "T0", ready=True) as stack:
        rendered = stack.get_html("/final")
        assert "最终人类决定" in rendered
        assert 'id="p92-taskbar"' in rendered


def test_browser_event_payload_does_not_capture_keyboard_content(tmp_path):
    with live_stack(tmp_path, "T1") as stack:
        payload = json.dumps(
            {"type": "option_selected", "detail": {"option_id": "sufficient"}}
        ).encode()
        assert stack.request(
            "POST",
            "/p92/event",
            body=payload,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(payload)),
                "X-P92-Session": stack.state.secret,
            },
        )[0] == 204
        event = stack.state.records.events_for_attempt(
            stack.state.attempt_id
        )[-1]
        assert set(event["detail"]) == {"option_id"}
        assert "key" not in json.dumps(event).lower()


def test_completion_answer_helper_requires_all_answers():
    task = load_config(SOURCE_PACKAGE)["tasks"]["T1"]
    assert answers_correct(
        task,
        {
            "requires_action": "不需要",
            "responsible_party": "贡献侧",
        },
    )
    assert not answers_correct(task, {"requires_action": "不需要"})


def test_package_integrity_excludes_mutable_runtime_and_records(tmp_path):
    result = build_delivery.build(
        SOURCE_PACKAGE,
        tmp_path / "P92_AGM_Human_Work_Cognitive_Pilot",
    )
    output = Path(result["output"])
    integrity = json.loads(
        (output / "package_integrity.json").read_text(encoding="utf-8")
    )
    assert not any(
        name.startswith(("runtime/", "records/"))
        for name in integrity["immutable_files"]
    )
    assert integrity["mutable_directories"] == ["runtime", "records"]
