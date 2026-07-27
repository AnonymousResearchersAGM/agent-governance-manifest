"""Objective snapshots and append-only records for P92 attempts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from common import (
    POLICY_FINGERPRINT,
    append_csv,
    append_jsonl,
    atomic_write_json,
    duration_seconds,
    read_jsonl,
    sha256_file,
    utc_now,
)


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return read_jsonl(path)


def snapshot_case(service, case_id: str) -> dict[str, Any]:
    case = service.storage.load_case(case_id)
    case_dir = service.storage.case_dir(case_id)
    transitions = service.storage.read_transitions(case_id)
    submissions = _jsonl(case_dir / "review_submissions.jsonl")
    denied_review = _jsonl(case_dir / "review_action_attempts.jsonl")
    return {
        "state": case.state,
        "transition_count": len(transitions),
        "transition_names": [item.action for item in transitions],
        "review_submission_count": len(submissions),
        "submissions": submissions,
        "finding_count": len(case.findings),
        "findings": [item.to_dict() for item in case.findings],
        "denied_attempt_count": (
            len(case.attempted_operations) + len(denied_review)
        ),
        "final_decision": (
            case.final_decision.to_dict() if case.final_decision else None
        ),
        "evidence": {
            item.id: {
                "obligation_ids": list(item.obligation_ids),
                "validity_state": item.validity_state,
            }
            for item in case.evidence
        },
    }


def _submission_fields(
    task: Mapping[str, Any],
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> dict[str, Any]:
    index = int(before["review_submission_count"])
    new_submissions = list(after["submissions"])[index:]
    if not new_submissions:
        return {
            "selected_option_id": None,
            "selected_judgment_title": None,
            "reason_text": None,
            "reason_length": 0,
            "operations": [],
        }
    item = new_submissions[0]
    draft = item.get("draft", {})
    decisions = draft.get("judgment_decisions", [])
    decision = decisions[0] if decisions else {}
    reason = decision.get("reason")
    operations = item.get("submission", {}).get("executed_operations", [])
    return {
        "selected_option_id": decision.get("selected_option_id"),
        "selected_judgment_title": task.get("judgment_title"),
        "reason_text": reason,
        "reason_length": len(reason or ""),
        "operations": list(operations),
    }


def _finding_fields(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> dict[str, Any]:
    new_findings = list(after["findings"])[int(before["finding_count"]):]
    obligations = sorted(
        {
            obligation
            for finding in new_findings
            for obligation in finding.get("affected_obligation_ids", [])
        }
    )
    severities = [item.get("severity") for item in new_findings]
    return {
        "new_finding_count": len(new_findings),
        "new_finding_severity": severities[0] if len(severities) == 1 else severities,
        "new_finding_blocking": (
            all(bool(item.get("blocking")) for item in new_findings)
            if new_findings
            else False
        ),
        "affected_obligation_ids": obligations,
        "affected_obligation_count": len(obligations),
    }


def _unaffected_evidence_preserved(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    affected: set[str],
) -> bool:
    for evidence_id, item in before["evidence"].items():
        if set(item["obligation_ids"]) & affected:
            continue
        if item["validity_state"] not in {"valid", "verified"}:
            continue
        observed = after["evidence"].get(evidence_id)
        if not observed or observed["validity_state"] not in {
            "valid",
            "verified",
        }:
            return False
    return True


def objective_score(
    task_id: str,
    task: Mapping[str, Any],
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    completion_answers: Mapping[str, str],
) -> tuple[bool, bool, dict[str, Any]]:
    submission = _submission_fields(task, before, after)
    finding = _finding_fields(before, after)
    transition_delta = int(after["transition_count"]) - int(
        before["transition_count"]
    )
    submission_delta = int(after["review_submission_count"]) - int(
        before["review_submission_count"]
    )
    final_unchanged = (
        before["final_decision"] == after["final_decision"] is None
    )
    safe = (
        final_unchanged
        and after["state"] not in {"accepted", "rejected", "closed"}
    )
    from common import answers_correct

    if task_id in {"T0", "T2", "T4"}:
        exact = (
            submission_delta == 1
            and submission["selected_option_id"]
            == task["expected_option_id"]
            and submission["operations"] == [task["expected_operation"]]
            and after["state"] == task["expected_state"]
        )
        if task_id == "T2":
            exact = (
                exact
                and finding["affected_obligation_count"] == 1
                and _unaffected_evidence_preserved(
                    before,
                    after,
                    set(finding["affected_obligation_ids"]),
                )
            )
        if task_id == "T4":
            exact = (
                exact
                and finding["new_finding_count"] == 1
                and finding["new_finding_severity"]
                == task["expected_finding_severity"]
                and finding["new_finding_blocking"] is True
                and finding["affected_obligation_count"] == 1
                and _unaffected_evidence_preserved(
                    before,
                    after,
                    set(finding["affected_obligation_ids"]),
                )
            )
    else:
        exact = (
            submission_delta == 0
            and transition_delta == 0
            and after["state"] == task["expected_state"]
            and answers_correct(task, completion_answers)
        )
        if task_id == "T3":
            exact = (
                exact
                and finding["new_finding_count"] == 0
                and after["denied_attempt_count"]
                == before["denied_attempt_count"]
            )
    details = {**submission, **finding}
    return bool(exact), bool(safe), details


class RecordStore:
    def __init__(
        self,
        records_root: Path,
        *,
        session_id: str,
        participant_id: str,
    ):
        self.root = records_root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id
        self.participant_id = participant_id
        notes = self.root / "P92_researcher_notes.txt"
        if not notes.exists():
            notes.write_text(
                "P92 研究者原话与观察（仅追加，不覆盖客观评分）\n\n",
                encoding="utf-8",
            )

    @property
    def events_path(self) -> Path:
        return self.root / "P92_interaction_events.jsonl"

    def event(
        self,
        *,
        attempt_id: str,
        task_id: str,
        event_type: str,
        detail: Mapping[str, Any] | None = None,
        occurred_at: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "schema_version": "agm.p92_interaction_event/v1",
            "session_id": self.session_id,
            "attempt_id": attempt_id,
            "participant_id": self.participant_id,
            "task_id": task_id,
            "event_type": event_type,
            "detail": dict(detail or {}),
            "occurred_at": occurred_at or utc_now(),
        }
        append_jsonl(self.events_path, payload)
        self.write_integrity()
        return payload

    def events_for_attempt(self, attempt_id: str) -> list[dict[str, Any]]:
        return [
            item
            for item in read_jsonl(self.events_path)
            if item.get("attempt_id") == attempt_id
        ]

    def finalize(
        self,
        *,
        task_id: str,
        task: Mapping[str, Any],
        attempt_id: str,
        attempt_number: int,
        start_utc: str,
        page_first_loaded_utc: str | None,
        before: Mapping[str, Any],
        after: Mapping[str, Any],
        completion_answers: Mapping[str, str],
        automatic_stop_reason: str,
        feedback: Mapping[str, Any],
        ports: Mapping[str, Any],
        technical_rerun: bool = False,
    ) -> dict[str, Any]:
        existing = read_jsonl(self.root / "P92_session_log.jsonl")
        if any(item.get("attempt_id") == attempt_id for item in existing):
            raise RuntimeError("P92 attempt is already finalized; records are append-only.")
        end = utc_now()
        events = self.events_for_attempt(attempt_id)
        exact, safe, derived = objective_score(
            task_id,
            task,
            before,
            after,
            completion_answers,
        )
        new_transitions = after["transition_names"][
            int(before["transition_count"]):
        ]
        payload = {
            "schema_version": "agm.p92_task_record/v1",
            "session_id": self.session_id,
            "attempt_id": attempt_id,
            "participant_id": self.participant_id,
            "task_id": task_id,
            "attempt_number": attempt_number,
            "scored": bool(task["scored"]),
            "technical_rerun": bool(technical_rerun),
            "start_utc": start_utc,
            "end_utc": end,
            "duration_seconds": duration_seconds(start_utc, end),
            "page_first_loaded_utc": page_first_loaded_utc,
            "task_prompt_visible": any(
                item["event_type"] == "page_load" for item in events
            ),
            "state_before": before["state"],
            "state_after": after["state"],
            "transition_count_before": before["transition_count"],
            "transition_count_after": after["transition_count"],
            "new_transition_names": new_transitions,
            "review_submission_count_before": before[
                "review_submission_count"
            ],
            "review_submission_count_after": after[
                "review_submission_count"
            ],
            "selected_option_id": derived["selected_option_id"],
            "selected_judgment_title": derived[
                "selected_judgment_title"
            ],
            "reason_text": derived["reason_text"],
            "reason_length": derived["reason_length"],
            "preview_count": sum(
                item["event_type"] == "preview_click" for item in events
            ),
            "execute_count": sum(
                item["event_type"] == "execute_click" for item in events
            ),
            "denied_attempt_count": (
                int(after["denied_attempt_count"])
                - int(before["denied_attempt_count"])
            ),
            "new_finding_count": derived["new_finding_count"],
            "new_finding_severity": derived["new_finding_severity"],
            "new_finding_blocking": derived["new_finding_blocking"],
            "affected_obligation_count": derived[
                "affected_obligation_count"
            ],
            "final_decision_before": before["final_decision"],
            "final_decision_after": after["final_decision"],
            "technical_details_opened": any(
                item["event_type"] == "technical_details_open"
                for item in events
            ),
            "completion_answers": dict(completion_answers),
            "objective_exact_success": exact,
            "objective_safe_boundary": safe,
            "automatic_stop_reason": automatic_stop_reason,
            "browser_events": events,
            "participant_difficulty_1_7": feedback.get("difficulty"),
            "participant_confidence_1_5": feedback.get("confidence"),
            "participant_comment": feedback.get("comment", ""),
            "researcher_observation": "",
            "researcher_adjudication_note": "",
            "researcher_help_provided": False,
            "anomaly_note": "",
            "proxy_port": ports.get("proxy_port"),
            "backend_port": ports.get("backend_port"),
            "backend_pid": ports.get("backend_pid"),
            "proxy_pid": ports.get("proxy_pid"),
        }
        append_jsonl(self.root / "P92_session_log.jsonl", payload)
        append_csv(self.root / "P92_session_log.csv", payload)
        summary_path = self.root / "P92_task_summary.json"
        summary = (
            json.loads(summary_path.read_text(encoding="utf-8"))
            if summary_path.exists()
            else {
                "schema_version": "agm.p92_task_summary/v1",
                "formal_sample": False,
                "session_id": self.session_id,
                "participant_id": self.participant_id,
                "attempts": [],
            }
        )
        summary["attempts"].append(
            {
                "attempt_id": attempt_id,
                "task_id": task_id,
                "attempt_number": attempt_number,
                "scored": bool(task["scored"]),
                "objective_exact_success": exact,
                "objective_safe_boundary": safe,
                "automatic_stop_reason": automatic_stop_reason,
            }
        )
        atomic_write_json(summary_path, summary)
        self.write_integrity()
        return payload

    def write_debrief(self, answers: Mapping[str, str]) -> None:
        path = self.root / "P92_debrief.json"
        if path.exists():
            raise RuntimeError("P92 debrief already exists; refusing overwrite.")
        atomic_write_json(
            path,
            {
                "schema_version": "agm.p92_debrief/v1",
                "session_id": self.session_id,
                "participant_id": self.participant_id,
                "recorded_at": utc_now(),
                "answers_verbatim": dict(answers),
            },
        )
        self.write_integrity()

    def write_integrity(self) -> None:
        path = self.root / "P92_integrity.json"
        files = {}
        for candidate in sorted(self.root.iterdir(), key=lambda item: item.name):
            if candidate.is_file() and candidate.name != path.name:
                files[candidate.name] = sha256_file(candidate)
        atomic_write_json(
            path,
            {
                "schema_version": "agm.p92_records_integrity/v1",
                "session_id": self.session_id,
                "participant_id": self.participant_id,
                "policy_fingerprint": POLICY_FINGERPRINT,
                "files": files,
                "updated_at": utc_now(),
            },
        )
