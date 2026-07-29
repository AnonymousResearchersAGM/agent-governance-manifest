"""Typed, obligation-specific validation for sidecar evidence artifacts."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from ..evidence import parse_timestamp
from ..models import GovernanceCase, VNextError, fingerprint
from .diff_parser import parse_verified_diff

SCHEMA_VERSION = "agm.evidence_artifact/v1"
HEX_FINGERPRINT = re.compile(r"^[0-9a-f]{64}$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40,64}$")
SCENARIO_TOKEN = re.compile(r"^D(?:\d+|6[AB])(?:[_-].*)?$", re.IGNORECASE)

ARTIFACT_COMPATIBILITY: dict[str, set[str]] = {
    "unified_diff": {"O-CHANGED-FILES"},
    "diff": {"O-CHANGED-FILES"},  # accepted transport alias; normalized below
    "change_summary": {"O-SUMMARY"},
    "changed_files": {"O-CHANGED-FILES"},
    "rationale": {"O-RATIONALE"},
    "known_limitations": {"O-LIMITATIONS"},
    "impact_statement": {"O-AUTH-IMPACT", "O-POLICY-IMPACT"},
    "test_result": {"O-TEST-COMMAND", "O-ARTIFACT", "O-TEST-EXPLANATION"},
    "agent_activity": {"O-AGENT-SCOPE"},
    "contribution_declaration": {"O-AGENT-SCOPE"},
    "human_confirmation": set(),
    "repair_record": set(),
    "final_receipt": set(),
    "supporting_statement": set(),
}

CANONICAL_TYPES: dict[str, dict[str, str]] = {
    "unified_diff": {"O-CHANGED-FILES": "changed_files"},
    "diff": {"O-CHANGED-FILES": "changed_files"},
    "change_summary": {"O-SUMMARY": "contribution_summary"},
    "changed_files": {"O-CHANGED-FILES": "changed_files"},
    "rationale": {"O-RATIONALE": "rationale"},
    "known_limitations": {"O-LIMITATIONS": "known_limitations"},
    "impact_statement": {
        "O-AUTH-IMPACT": "security_auth_impact",
        "O-POLICY-IMPACT": "policy_impact",
    },
    "test_result": {
        "O-TEST-COMMAND": "test_command",
        "O-ARTIFACT": "artifact",
        "O-TEST-EXPLANATION": "test_explanation",
    },
    "agent_activity": {"O-AGENT-SCOPE": "agent_action_scope"},
    "contribution_declaration": {"O-AGENT-SCOPE": "agent_action_scope"},
}


@dataclass(frozen=True)
class ValidatedArtifact:
    metadata: dict[str, Any]
    content: str
    typed_value: dict[str, Any] | None
    artifact_type: str
    obligation_refs: tuple[str, ...]
    derived_files: tuple[str, ...] = ()

    @property
    def artifact_id(self) -> str:
        return str(self.metadata["artifact_id"])


def _require_string(value: dict[str, Any], field: str) -> str:
    item = value.get(field)
    if not isinstance(item, str) or not item.strip():
        raise VNextError(f"Artifact field '{field}' must be a non-empty string")
    return item.strip()


def _require_string_list(
    value: dict[str, Any], field: str, *, allow_empty: bool = False
) -> list[str]:
    items = value.get(field)
    if not isinstance(items, list) or (not items and not allow_empty):
        raise VNextError(f"Artifact field '{field}' must be a list")
    if any(not isinstance(item, str) or not item.strip() for item in items):
        raise VNextError(f"Artifact field '{field}' contains an invalid value")
    return [item.strip() for item in items]


def _repo_path(path: str) -> str:
    if "\\" in path or not path or path.startswith("/") or re.match(r"^[A-Za-z]:", path):
        raise VNextError("Changed-files paths must be repository-relative")
    parts = PurePosixPath(path).parts
    if ".." in parts or "." in parts or SCENARIO_TOKEN.fullmatch(path):
        raise VNextError("Changed-files paths must be safe repository-relative paths")
    return path


def _typed_json(content: str, artifact_type: str) -> dict[str, Any]:
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        raise VNextError(f"{artifact_type} artifact content must be valid JSON") from exc
    if not isinstance(value, dict):
        raise VNextError(f"{artifact_type} artifact content must be a JSON object")
    return value


def _common(
    value: dict[str, Any],
    *,
    artifact_type: str,
    artifact: dict[str, Any],
    package: dict[str, Any],
    case: GovernanceCase,
) -> None:
    if value.get("schema_version") != SCHEMA_VERSION:
        raise VNextError("Artifact schema_version is missing or unsupported")
    if value.get("artifact_type") != artifact_type:
        raise VNextError("Artifact content type does not match package metadata")
    contribution = _require_string(value, "contribution_fingerprint")
    if not HEX_FINGERPRINT.fullmatch(contribution):
        raise VNextError("Artifact contribution_fingerprint is invalid")
    if contribution != package.get("contribution_fingerprint") or contribution != case.contribution_fingerprint:
        raise VNextError("Artifact contribution binding does not match current case")
    head = _require_string(value, "head_commit_sha")
    if not COMMIT_SHA.fullmatch(head):
        raise VNextError("Artifact head_commit_sha is invalid")
    if head != package.get("head_commit_sha") or head != artifact.get("head_commit_sha"):
        raise VNextError("Artifact head commit binding does not match package")
    observed = _require_string(value, "observed_at")
    parse_timestamp(observed, label="artifact observed_at")
    refs = _require_string_list(value, "obligation_refs")
    if refs != list(artifact.get("obligation_refs", [])):
        raise VNextError("Artifact obligation_refs do not match package metadata")


def _validate_summary(value: dict[str, Any]) -> None:
    summary = _require_string(value, "summary")
    _require_string_list(value, "affected_components")
    _require_string(value, "behavioral_change")
    lowered = summary.lower()
    if (
        len(summary) < 16
        or SCENARIO_TOKEN.fullmatch(summary)
        or lowered.startswith(("case-", "artifact-", "package-"))
        or HEX_FINGERPRINT.fullmatch(lowered)
        or "concrete contribution material" in lowered
        or "绑定当前版本的具体贡献材料" in summary
    ):
        raise VNextError("Change summary is an identifier or placeholder, not a factual summary")


def _validate_changed_files(value: dict[str, Any]) -> tuple[str, ...]:
    files = tuple(_repo_path(item) for item in _require_string_list(value, "files"))
    if len(set(files)) != len(files):
        raise VNextError("Changed-files artifact contains duplicates")
    return files


def _validate_rationale(value: dict[str, Any]) -> None:
    reason = _require_string(value, "reason")
    outcome = _require_string(value, "intended_outcome")
    if reason == outcome:
        raise VNextError("Rationale reason and intended outcome must be distinct")


def _validate_limitations(value: dict[str, Any]) -> None:
    limitations = _require_string_list(value, "limitations", allow_empty=True)
    explicit_none = value.get("no_known_limitations")
    if not limitations and explicit_none is not True:
        raise VNextError("Empty limitations require no_known_limitations=true")
    if limitations and explicit_none is True:
        raise VNextError("Known limitations contradict no_known_limitations=true")
    _require_string(value, "declared_by")


def _validate_impact(value: dict[str, Any]) -> None:
    for field in (
        "security_impact",
        "compatibility_impact",
        "data_impact",
        "operational_impact",
    ):
        item = value.get(field)
        if isinstance(item, str):
            if not item.strip():
                raise VNextError(f"Impact field '{field}' is empty")
        elif isinstance(item, dict):
            status = _require_string(item, "status")
            if status == "not_applicable":
                _require_string(item, "reason")
        else:
            raise VNextError(f"Impact field '{field}' is missing")


def _validate_test(value: dict[str, Any], artifact: dict[str, Any]) -> None:
    for field in ("command", "environment", "result_summary", "source_tool"):
        _require_string(value, field)
        if value[field] != artifact.get(field):
            raise VNextError(f"Test field '{field}' does not match package metadata")
    for field in ("exit_code", "tests_passed", "tests_failed"):
        item = value.get(field)
        if not isinstance(item, int) or isinstance(item, bool) or item < 0:
            raise VNextError(f"Test field '{field}' must be a non-negative integer")
        if item != artifact.get(field):
            raise VNextError(f"Test field '{field}' does not match package metadata")
    scope = _require_string_list(value, "affected_scope")
    if scope != artifact.get("affected_scope"):
        raise VNextError("Test affected_scope does not match package metadata")


def _validate_agent(value: dict[str, Any], case: GovernanceCase) -> None:
    used = value.get("other_agents_or_tools_used")
    if not isinstance(used, bool):
        raise VNextError("other_agents_or_tools_used must be boolean")
    tools = _require_string_list(value, "tools_used", allow_empty=True)
    scope = _require_string_list(value, "activity_scope")
    _require_string(value, "source_tool")
    if used and not tools:
        raise VNextError("Agent activity that used tools must name them")
    if not used and tools:
        raise VNextError("Agent activity declares no tools but tools_used is non-empty")
    if not set(scope) & set(case.changed_files):
        raise VNextError("Agent activity scope does not overlap the contribution")


def _validate_declaration(value: dict[str, Any], case: GovernanceCase) -> None:
    used = value.get("other_agents_or_tools_used")
    if not isinstance(used, bool):
        raise VNextError("other_agents_or_tools_used must be boolean")
    tools = _require_string_list(value, "declared_tools", allow_empty=True)
    scope = _require_string_list(value, "declaration_scope")
    _require_string(value, "declared_by")
    if used and not tools:
        raise VNextError("Declaration that used tools must name them")
    if not used and tools:
        raise VNextError("Declaration says no tools but declared_tools is non-empty")
    if not set(scope) & set(case.changed_files):
        raise VNextError("Declaration scope does not overlap the contribution")


def _validate_human_confirmation(value: dict[str, Any]) -> None:
    _require_string(value, "confirmed_by")
    parse_timestamp(_require_string(value, "confirmed_at"), label="confirmed_at")
    _require_string_list(value, "confirmation_scope")
    _require_string(value, "statement")


class TypedArtifactValidator:
    """Validate all package artifacts before canonical state is constructed."""

    def validate_package(
        self,
        case: GovernanceCase,
        package: dict[str, Any],
        read_artifact: Any,
    ) -> tuple[ValidatedArtifact, ...]:
        validated: list[ValidatedArtifact] = []
        known_obligations = {item.obligation_id for item in case.obligations}
        for metadata in package.get("artifacts", []):
            artifact, content = read_artifact(package["package_digest"], metadata["artifact_id"])
            if fingerprint(content) != artifact.get("content_digest"):
                raise VNextError("Evidence artifact digest verification failed")
            for field, expected in (
                ("case_id", case.id),
                ("contribution_fingerprint", case.contribution_fingerprint),
                ("policy_fingerprint", case.policy_snapshot.policy_fingerprint),
            ):
                if artifact.get(field) != expected:
                    raise VNextError(f"Evidence artifact {field} binding does not match")
            artifact_type = artifact.get("artifact_type")
            if artifact_type not in ARTIFACT_COMPATIBILITY:
                raise VNextError("Evidence artifact type is not supported")
            refs = tuple(artifact.get("obligation_refs", ()))
            if set(refs) - known_obligations:
                raise VNextError("Evidence artifact references obligations not compiled for this case")
            if set(refs) - ARTIFACT_COMPATIBILITY[artifact_type]:
                raise VNextError("Evidence artifact type is incompatible with referenced obligation")
            if refs:
                scope = artifact.get("affected_scope")
                if (
                    not isinstance(scope, list)
                    or not scope
                    or not set(scope) & set(case.changed_files)
                ):
                    raise VNextError("Evidence artifact affected_scope is missing or unbound")
                if not isinstance(artifact.get("source_tool"), str) or not artifact["source_tool"].strip():
                    raise VNextError("Evidence artifact source_tool is required")
                parse_timestamp(
                    artifact.get("observed_at"), label="artifact metadata observed_at"
                )
            if artifact_type == "supporting_statement":
                if refs:
                    raise VNextError("Supporting statements cannot satisfy canonical obligations")
                validated.append(ValidatedArtifact(artifact, content, None, artifact_type, refs))
                continue
            if artifact_type in {"unified_diff", "diff"}:
                locations = parse_verified_diff(content)
                files = tuple(dict.fromkeys(item.path for item in locations))
                validated.append(ValidatedArtifact(artifact, content, None, "unified_diff", refs, files))
                continue
            value = _typed_json(content, artifact_type)
            _common(
                value,
                artifact_type=artifact_type,
                artifact=artifact,
                package=package,
                case=case,
            )
            if "source_tool" in value and value["source_tool"] != artifact.get(
                "source_tool"
            ):
                raise VNextError(
                    "Artifact source_tool does not match package metadata"
                )
            derived_files: tuple[str, ...] = ()
            if artifact_type == "change_summary":
                _validate_summary(value)
            elif artifact_type == "changed_files":
                derived_files = _validate_changed_files(value)
            elif artifact_type == "rationale":
                _validate_rationale(value)
            elif artifact_type == "known_limitations":
                _validate_limitations(value)
            elif artifact_type == "impact_statement":
                _validate_impact(value)
            elif artifact_type == "test_result":
                _validate_test(value, artifact)
            elif artifact_type == "agent_activity":
                _validate_agent(value, case)
            elif artifact_type == "contribution_declaration":
                _validate_declaration(value, case)
            elif artifact_type == "human_confirmation":
                _validate_human_confirmation(value)
            validated.append(
                ValidatedArtifact(
                    artifact, content, value, artifact_type, refs, derived_files
                )
            )
        self._cross_validate(case, validated)
        return tuple(validated)

    def _cross_validate(
        self, case: GovernanceCase, artifacts: list[ValidatedArtifact]
    ) -> None:
        diff_files = {
            path
            for item in artifacts
            if item.artifact_type == "unified_diff"
            for path in item.derived_files
        }
        declared_files = {
            path
            for item in artifacts
            if item.artifact_type == "changed_files"
            for path in item.derived_files
        }
        if declared_files and diff_files and declared_files != diff_files:
            raise VNextError("Changed-files artifact does not match verified unified diff")
        if declared_files and not declared_files <= set(case.changed_files):
            raise VNextError("Changed-files artifact exceeds current contribution scope")
