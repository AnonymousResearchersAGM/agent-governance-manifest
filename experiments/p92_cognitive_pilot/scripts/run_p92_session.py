"""Coordinate verified P92 task processes without running a real pilot."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import uuid
import webbrowser
from pathlib import Path
from typing import Any

from common import (
    TASK_IDS,
    atomic_write_json,
    find_free_loopback_port,
    load_config,
    package_root,
    read_jsonl,
    reset_task_runtime,
    utc_now,
    validate_participant_id,
    verify_baseline_manifest,
)
from stop_p92 import stop_marked_processes
from verify_p92_package import verify


def _wait_url(url: str, timeout: float = 20) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status < 500:
                    return
        except Exception as exc:  # noqa: BLE001 - bounded health retry
            last_error = exc
        time.sleep(0.15)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def _attempt_number(root: Path, participant: str, task_id: str) -> int:
    records = read_jsonl(root / "records" / "P92_session_log.jsonl")
    return (
        sum(
            item.get("participant_id") == participant
            and item.get("task_id") == task_id
            for item in records
        )
        + 1
    )


def _new_process(
    command: list[str],
    *,
    cwd: Path,
) -> subprocess.Popen[str]:
    creationflags = (
        subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    )
    return subprocess.Popen(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )


def _terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _session_file(root: Path) -> Path:
    return root / "runtime" / "session.json"


def _load_or_create_session(
    *,
    root: Path,
    repo_root: Path,
    participant: str,
    resume: bool,
) -> dict[str, Any]:
    path = _session_file(root)
    existing_records = read_jsonl(root / "records" / "P92_session_log.jsonl")
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not resume:
            raise RuntimeError(
                "An unfinished P92 session exists. Restart with --resume."
            )
        if payload["participant_id"] != participant:
            raise RuntimeError("Resume participant does not match the session.")
        return payload
    if existing_records and not resume:
        raise RuntimeError(
            "Existing P92 records were found. Use --resume or a new blank package."
        )
    payload = {
        "schema_version": "agm.p92_runtime_session/v1",
        "session_id": f"p92-session-{uuid.uuid4().hex}",
        "participant_id": participant,
        "repo_root": str(repo_root),
        "created_at": utc_now(),
        "completed_tasks": [],
        "formal_sample": False,
    }
    atomic_write_json(path, payload)
    return payload


def run_attempt(
    *,
    root: Path,
    repo_root: Path,
    participant: str,
    session: dict[str, Any],
    task_id: str,
    no_browser: bool,
    technical_rerun: bool,
) -> str:
    verify_baseline_manifest(root)
    runtime = reset_task_runtime(
        task_id,
        repo_root=repo_root,
        root=root,
    )
    task = load_config(root)["tasks"][task_id]
    project_root = runtime / "project"
    work_root = project_root / "p92-work"
    state_file = runtime / "proxy_state.json"
    ready_file = runtime / "backend_ready.json"
    backend_port = find_free_loopback_port()
    proxy_port = find_free_loopback_port()
    while proxy_port == backend_port:
        proxy_port = find_free_loopback_port()
    attempt_number = _attempt_number(root, participant, task_id)
    attempt_id = f"{session['session_id']}-{task_id}-a{attempt_number}-{uuid.uuid4().hex[:8]}"
    marker = f"P92_SESSION_MARKER_{uuid.uuid4().hex}"
    scripts = root / "scripts"
    backend_command = [
        sys.executable,
        str(scripts / "backend_runner.py"),
        "--repo-root",
        str(repo_root),
        "--project-root",
        str(project_root),
        "--work-root",
        str(work_root),
        "--case-id",
        task["case_id"],
        "--actor",
        "p92-human-maintainer",
        "--role",
        "maintainer",
        "--port",
        str(backend_port),
        "--session-marker",
        marker,
        "--ready-file",
        str(ready_file),
    ]
    backend = _new_process(backend_command, cwd=root)
    proxy: subprocess.Popen[str] | None = None
    process_file = root / "runtime" / "processes.json"
    try:
        _wait_url(f"http://127.0.0.1:{backend_port}/")
        proxy_command = [
            sys.executable,
            str(scripts / "experiment_proxy.py"),
            "--package-root",
            str(root),
            "--repo-root",
            str(repo_root),
            "--project-root",
            str(project_root),
            "--work-root",
            str(work_root),
            "--records-root",
            str(root / "records"),
            "--state-file",
            str(state_file),
            "--task",
            task_id,
            "--session-id",
            session["session_id"],
            "--participant-id",
            participant,
            "--attempt-id",
            attempt_id,
            "--attempt-number",
            str(attempt_number),
            "--backend-port",
            str(backend_port),
            "--proxy-port",
            str(proxy_port),
            "--backend-pid",
            str(backend.pid),
            "--session-marker",
            marker,
        ]
        if technical_rerun:
            proxy_command.append("--technical-rerun")
        proxy = _new_process(proxy_command, cwd=root)
        atomic_write_json(
            process_file,
            {
                "session_marker": marker,
                "session_id": session["session_id"],
                "task_id": task_id,
                "processes": [
                    {"kind": "backend", "pid": backend.pid},
                    {"kind": "proxy", "pid": proxy.pid},
                ],
            },
        )
        url = f"http://127.0.0.1:{proxy_port}/"
        _wait_url(f"http://127.0.0.1:{proxy_port}/p92/health")
        if not no_browser:
            webbrowser.open((root / "参与者说明.html").as_uri())
            webbrowser.open(url)
        print(f"P92 {task_id} participant URL: {url}", flush=True)
        while True:
            if proxy.poll() is not None:
                raise RuntimeError("P92 experiment proxy exited unexpectedly.")
            if state_file.exists():
                state = json.loads(state_file.read_text(encoding="utf-8"))
                if state["phase"] in {
                    "completed",
                    "retry_requested",
                }:
                    verify_baseline_manifest(root)
                    return str(state["phase"])
            time.sleep(0.25)
    finally:
        if proxy is not None:
            _terminate(proxy)
        _terminate(backend)
        process_file.unlink(missing_ok=True)
        verify_baseline_manifest(root)


def run(
    *,
    repo_root: Path,
    participant: str,
    selected_task: str,
    resume: bool,
    no_browser: bool,
    non_interactive: bool,
    technical_rerun: bool,
    root: Path,
) -> dict[str, Any]:
    root = root.resolve()
    repo_root = repo_root.resolve()
    participant = validate_participant_id(participant)
    stop_marked_processes(root)
    verification = verify(repo_root, root)
    session = _load_or_create_session(
        root=root,
        repo_root=repo_root,
        participant=participant,
        resume=resume,
    )
    tasks = list(TASK_IDS) if selected_task == "ALL" else [selected_task]
    config = load_config(root)
    completed = set(session.get("completed_tasks", []))
    for task_id in tasks:
        if task_id in completed and not technical_rerun:
            continue
        while True:
            phase = run_attempt(
                root=root,
                repo_root=repo_root,
                participant=participant,
                session=session,
                task_id=task_id,
                no_browser=no_browser,
                technical_rerun=technical_rerun,
            )
            if phase == "retry_requested" and task_id == "T0":
                print("T0 mastery was not completed; resetting training.", flush=True)
                continue
            break
        if phase != "completed":
            raise RuntimeError(f"P92 task ended in unexpected phase: {phase}")
        if task_id not in session["completed_tasks"]:
            session["completed_tasks"].append(task_id)
            atomic_write_json(_session_file(root), session)
        if (
            selected_task == "ALL"
            and task_id != tasks[-1]
            and not non_interactive
        ):
            input("本题已结束。研究者确认后按 Enter 进入下一题：")
    session["completed_at"] = utc_now()
    atomic_write_json(_session_file(root), session)
    return {
        "session_id": session["session_id"],
        "participant_id": participant,
        "completed_tasks": session["completed_tasks"],
        "verification": verification,
        "formal_sample": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--participant-id", required=True)
    parser.add_argument("--task", choices=("ALL", *TASK_IDS), default="ALL")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--non-interactive", action="store_true")
    parser.add_argument("--technical-rerun", action="store_true")
    parser.add_argument("--package-root", type=Path, default=package_root())
    args = parser.parse_args()
    print(
        json.dumps(
            run(
                repo_root=args.repo_root,
                participant=args.participant_id,
                selected_task=args.task,
                resume=args.resume,
                no_browser=args.no_browser,
                non_interactive=args.non_interactive,
                technical_rerun=args.technical_rerun,
                root=args.package_root,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
