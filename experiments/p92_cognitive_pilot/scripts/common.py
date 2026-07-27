"""Shared, package-local utilities for the P92 cognitive pilot."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import socket
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


ARTIFACT_COMMIT = "cb1d741dac841a18dce3de53141ff66b1a57649b"
POLICY_FINGERPRINT = (
    "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564"
)
PARTICIPANT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
TASK_IDS = ("T0", "T1", "T2", "T3", "T4")
RECORD_FIELDS = (
    "session_id",
    "attempt_id",
    "participant_id",
    "task_id",
    "attempt_number",
    "scored",
    "technical_rerun",
    "start_utc",
    "end_utc",
    "duration_seconds",
    "page_first_loaded_utc",
    "task_prompt_visible",
    "state_before",
    "state_after",
    "transition_count_before",
    "transition_count_after",
    "new_transition_names",
    "review_submission_count_before",
    "review_submission_count_after",
    "selected_option_id",
    "selected_judgment_title",
    "reason_text",
    "reason_length",
    "preview_count",
    "execute_count",
    "denied_attempt_count",
    "new_finding_count",
    "new_finding_severity",
    "new_finding_blocking",
    "affected_obligation_count",
    "final_decision_before",
    "final_decision_after",
    "technical_details_opened",
    "completion_answers",
    "objective_exact_success",
    "objective_safe_boundary",
    "automatic_stop_reason",
    "browser_events",
    "participant_difficulty_1_7",
    "participant_confidence_1_5",
    "participant_comment",
    "researcher_observation",
    "researcher_adjudication_note",
    "researcher_help_provided",
    "anomaly_note",
    "proxy_port",
    "backend_port",
    "backend_pid",
    "proxy_pid",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_config(root: Path | None = None) -> dict[str, Any]:
    base = root or package_root()
    return json.loads((base / "p92_session.json").read_text(encoding="utf-8"))


def task_config(task_id: str, root: Path | None = None) -> dict[str, Any]:
    if task_id not in TASK_IDS:
        raise ValueError(f"Unknown P92 task: {task_id}")
    return dict(load_config(root)["tasks"][task_id])


def validate_participant_id(value: str) -> str:
    if not PARTICIPANT_PATTERN.fullmatch(value):
        raise ValueError(
            "ParticipantId must use 1-64 letters, numbers, dot, dash, or underscore."
        )
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(dict(payload), ensure_ascii=False, sort_keys=True))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            result.append(json.loads(line))
    return result


def append_csv(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    row = {}
    for field in RECORD_FIELDS:
        value = payload.get(field)
        row[field] = (
            json.dumps(value, ensure_ascii=False, sort_keys=True)
            if isinstance(value, (dict, list, tuple))
            else value
        )
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RECORD_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow(row)
        handle.flush()
        os.fsync(handle.fileno())


def ensure_within(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    root_resolved = root.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise ValueError(f"Path escapes P92 package: {resolved}")
    return resolved


def baseline_manifest_path(root: Path | None = None) -> Path:
    base = root or package_root()
    return base / "baseline" / "baseline_sha256.json"


def baseline_files(root: Path | None = None) -> list[Path]:
    base = root or package_root()
    baseline = base / "baseline"
    return sorted(
        (
            path
            for path in baseline.rglob("*")
            if path.is_file() and path.name != "baseline_sha256.json"
        ),
        key=lambda item: item.relative_to(baseline).as_posix(),
    )


def build_baseline_manifest(root: Path | None = None) -> dict[str, Any]:
    base = root or package_root()
    baseline = base / "baseline"
    return {
        "schema_version": "agm.p92_baseline_integrity/v1",
        "artifact_commit": ARTIFACT_COMMIT,
        "policy_fingerprint": POLICY_FINGERPRINT,
        "files": {
            path.relative_to(baseline).as_posix(): sha256_file(path)
            for path in baseline_files(base)
        },
    }


def verify_baseline_manifest(root: Path | None = None) -> dict[str, Any]:
    base = root or package_root()
    manifest_path = baseline_manifest_path(base)
    expected = json.loads(manifest_path.read_text(encoding="utf-8"))
    observed = build_baseline_manifest(base)
    if expected != observed:
        raise RuntimeError("P92 baseline hash mismatch.")
    return observed


def reset_task_runtime(
    task_id: str,
    *,
    repo_root: Path,
    root: Path | None = None,
) -> Path:
    base = root or package_root()
    task = task_config(task_id, base)
    source = ensure_within(base / "baseline" / task["baseline"], base)
    destination = ensure_within(base / "runtime" / task_id, base)
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    project = destination / "project"
    project.mkdir(parents=True)
    shutil.copytree(repo_root / ".agm", project / ".agm")
    shutil.copytree(repo_root / "skills", project / "skills")
    support_files = (
        "requirements.txt",
        "docs/AGM_HUMAN_GUIDE.md",
        "demo_app/auth.py",
        "demo_app/config.py",
    )
    for relative in support_files:
        source_file = repo_root / relative
        target = project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target)
    shutil.copytree(source, project / "p92-work")
    return destination


def find_free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", 0))
        return int(handle.getsockname()[1])


def file_count(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def stable_file_map(
    root: Path,
    *,
    excluded: Iterable[str] = (),
) -> dict[str, str]:
    excluded_set = set(excluded)
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(
            (item for item in root.rglob("*") if item.is_file()),
            key=lambda item: item.relative_to(root).as_posix(),
        )
        if path.relative_to(root).as_posix() not in excluded_set
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".pyo"}
    }


def duration_seconds(start: str, end: str) -> float:
    return round((parse_utc(end) - parse_utc(start)).total_seconds(), 3)


def answers_correct(task: Mapping[str, Any], answers: Mapping[str, str]) -> bool:
    questions = task.get("completion_questions") or task.get(
        "mastery_questions", []
    )
    return bool(questions) and all(
        answers.get(str(item["id"])) == item["correct"] for item in questions
    )


def no_forbidden_prompt_leak(config: Mapping[str, Any]) -> bool:
    forbidden = (
        "请选择“要求补充或修正”",
        "请选择“标记重大风险”",
        "正确答案",
        "预期操作",
        "当前应当",
        "你需要退回",
        "这是重大风险",
        "这是材料不足",
    )
    return all(
        not any(term in task["prompt"] for term in forbidden)
        for task in config["tasks"].values()
    )
