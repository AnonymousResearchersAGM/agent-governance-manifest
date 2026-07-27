"""Traversal-safe, atomic local storage for Governance Cases."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

import yaml

from .models import (
    AttemptedOperation,
    GovernanceCase,
    StateTransition,
    VNextError,
    fingerprint,
)


CASE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def validate_case_id(case_id: str) -> str:
    if not CASE_ID_PATTERN.fullmatch(case_id):
        raise VNextError(
            "Case ID must contain only letters, numbers, dot, underscore, or dash"
        )
    return case_id


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temporary_name = handle.name
        os.replace(temporary_name, path)
    except Exception:
        if temporary_name:
            try:
                Path(temporary_name).unlink(missing_ok=True)
            except OSError:
                pass
        raise


def dump_yaml(value: Any) -> str:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True)


class CaseStorage:
    def __init__(self, root: Path, work_root: Path | None = None):
        self.root = root.resolve()
        self.work_root = (
            work_root.resolve()
            if work_root is not None
            else (self.root / ".agm-work").resolve()
        )
        self.cases_root = (self.work_root / "cases").resolve()
        if self.work_root != self.root and self.root not in self.work_root.parents:
            raise VNextError("Case work root must remain inside the project root")

    def case_dir(self, case_id: str) -> Path:
        validate_case_id(case_id)
        candidate = (self.cases_root / case_id).resolve()
        if self.cases_root not in candidate.parents:
            raise VNextError("Case path escapes .agm-work/cases")
        return candidate

    def create_case(self, case: GovernanceCase) -> Path:
        directory = self.case_dir(case.id)
        if directory.exists():
            raise VNextError(f"Governance Case already exists: {case.id}")
        directory.mkdir(parents=True)
        self.save_case(case)
        return directory

    def save_case(self, case: GovernanceCase) -> Path:
        directory = self.case_dir(case.id)
        if not directory.exists():
            raise VNextError(f"Governance Case does not exist: {case.id}")
        atomic_write_text(directory / "case.yml", dump_yaml(case.to_dict()))
        atomic_write_text(
            directory / "policy_snapshot.yml",
            dump_yaml(case.policy_snapshot.to_dict()),
        )
        atomic_write_text(
            directory / "matched_rules.yml",
            dump_yaml(
                {
                    "schema_version": "agm.matched_rule_set/v0.2-dev",
                    "items": [item.to_dict() for item in case.matched_rules],
                }
            ),
        )
        atomic_write_text(
            directory / "obligations.yml",
            dump_yaml(
                {
                    "schema_version": "agm.compiled_obligation_set/v0.2-dev",
                    "items": [item.to_dict() for item in case.obligations],
                }
            ),
        )
        atomic_write_text(
            directory / "evidence.yml",
            dump_yaml(
                {
                    "schema_version": "agm.bound_evidence_set/v0.2-dev",
                    "items": [item.to_dict() for item in case.evidence],
                }
            ),
        )
        atomic_write_text(
            directory / "attestations.yml",
            dump_yaml(
                {
                    "schema_version": "agm.human_attestation_set/v0.2-dev",
                    "items": [item.to_dict() for item in case.attestations],
                }
            ),
        )
        atomic_write_text(
            directory / "findings.yml",
            dump_yaml(
                {
                    "schema_version": "agm.governance_finding_set/v0.2-dev",
                    "items": [item.to_dict() for item in case.findings],
                }
            ),
        )
        atomic_write_text(
            directory / "repair_requests.yml",
            dump_yaml(
                {
                    "schema_version": "agm.repair_request_set/v0.2-dev",
                    "items": [item.to_dict() for item in case.repair_requests],
                }
            ),
        )
        atomic_write_text(
            directory / "attempted_operations.yml",
            dump_yaml(
                {
                    "schema_version": (
                        "agm.attempted_operation_audit/v0.2-dev"
                    ),
                    "append_only": True,
                    "items": [
                        item.to_dict()
                        for item in case.attempted_operations
                    ],
                }
            ),
        )
        atomic_write_text(
            directory / "verifications.yml",
            dump_yaml(
                {
                    "schema_version": "agm.maintainer_verification_set/v0.2-dev",
                    "items": [
                        item.to_dict() for item in case.maintainer_verifications
                    ],
                }
            ),
        )
        if case.closure_receipt:
            atomic_write_text(
                directory / "closure_receipt.yml",
                dump_yaml(case.closure_receipt.to_dict()),
            )
        return directory / "case.yml"

    def load_case(self, case_id: str) -> GovernanceCase:
        path = self.case_dir(case_id) / "case.yml"
        if not path.is_file():
            raise VNextError(f"Governance Case not found: {case_id}")
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise VNextError(f"Malformed Governance Case YAML: {path}") from exc
        if not isinstance(data, dict):
            raise VNextError(f"Governance Case must be a mapping: {path}")
        case = GovernanceCase.from_dict(data)
        if case.id != case_id:
            raise VNextError("Stored Governance Case ID does not match directory")
        audit_events = self.read_attempted_operations(case_id)
        if audit_events:
            by_id = {
                item.id: item for item in case.attempted_operations
            }
            for item in audit_events:
                by_id[item.id] = item
            case.attempted_operations = list(by_id.values())
        return case

    def append_transition(self, transition: StateTransition) -> Path:
        directory = self.case_dir(transition.case_id)
        if not directory.exists():
            raise VNextError(
                f"Cannot append transition for missing case: {transition.case_id}"
            )
        path = directory / "transitions.jsonl"
        line = json.dumps(
            transition.to_dict(), ensure_ascii=False, sort_keys=True
        ) + "\n"
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        return path

    def read_transitions(self, case_id: str) -> list[StateTransition]:
        path = self.case_dir(case_id) / "transitions.jsonl"
        if not path.exists():
            return []
        result = []
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise VNextError(
                    f"Malformed transition JSONL at line {line_number}"
                ) from exc
            result.append(StateTransition.from_dict(raw))
        return result

    def append_attempted_operation(
        self,
        attempt: AttemptedOperation,
    ) -> Path:
        """Append a rejected-operation audit fact without a state transition."""

        directory = self.case_dir(attempt.case_id)
        if not directory.exists():
            raise VNextError(
                "Cannot append attempted operation for missing case: "
                f"{attempt.case_id}"
            )
        path = directory / "attempted_operations.jsonl"
        line = json.dumps(
            attempt.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
        ) + "\n"
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        return path

    def read_attempted_operations(
        self,
        case_id: str,
    ) -> list[AttemptedOperation]:
        path = self.case_dir(case_id) / "attempted_operations.jsonl"
        if not path.exists():
            return []
        result = []
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise VNextError(
                    "Malformed attempted-operation JSONL at line "
                    f"{line_number}"
                ) from exc
            result.append(AttemptedOperation.from_dict(raw))
        return result

    def transition_log_hash(self, case_id: str) -> str:
        transitions = [
            item.to_dict() for item in self.read_transitions(case_id)
        ]
        return fingerprint(transitions)

    def write_report(
        self,
        case_id: str,
        *,
        markdown: str,
        html: str,
        guidance_json: str | None = None,
    ) -> dict[str, Path]:
        directory = self.case_dir(case_id)
        if not directory.exists():
            raise VNextError(f"Governance Case not found: {case_id}")
        markdown_path = directory / "report.md"
        html_path = directory / "report.html"
        atomic_write_text(markdown_path, markdown)
        atomic_write_text(html_path, html)
        paths = {"markdown": markdown_path, "html": html_path}
        if guidance_json is not None:
            guidance_path = directory / "guidance.json"
            atomic_write_text(guidance_path, guidance_json)
            paths["guidance_json"] = guidance_path
        return paths
