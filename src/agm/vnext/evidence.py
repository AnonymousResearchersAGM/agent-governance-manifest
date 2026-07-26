"""Evidence binding, validation, freshness, and conflict detection."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .config import normalize_path, safe_project_path
from .models import (
    BoundEvidence,
    GovernanceCase,
    VNextError,
    canonical_json,
    fingerprint,
    new_id,
    utc_now,
)


PLACEHOLDER_TERMS = (
    "todo",
    "tbd",
    "placeholder",
    "lorem ipsum",
    "fill me",
    "to be filled",
    "not provided",
)
PLACEHOLDER_EXACT = {
    "",
    "n/a",
    "na",
    "none",
    "unknown",
    "tests passed",
    "test passed",
}


def parse_timestamp(value: str, *, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise VNextError(f"Invalid {label} timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise VNextError(f"{label} timestamp must include a timezone")
    return parsed.astimezone(UTC)


def value_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return " ".join(value_text(item) for item in value).strip()
    if isinstance(value, dict):
        return " ".join(
            f"{key} {value_text(item)}" for key, item in value.items()
        ).strip()
    return str(value).strip()


def is_placeholder(value: Any, *, allow_explicit_none: bool = False) -> bool:
    lowered = value_text(value).lower()
    if allow_explicit_none and lowered == "none":
        return False
    return (
        lowered in PLACEHOLDER_EXACT
        or lowered.startswith("todo")
        or lowered.startswith("tbd")
        or any(term in lowered for term in PLACEHOLDER_TERMS)
    )


def artifact_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_set_fingerprint(evidence: list[BoundEvidence]) -> str:
    material = []
    for item in sorted(evidence, key=lambda record: record.id):
        payload = item.to_dict()
        payload.pop("validity_state", None)
        payload.pop("invalid_reasons", None)
        payload.pop("retained_for_contribution_fingerprint", None)
        payload.pop("retention_reason", None)
        material.append(payload)
    return fingerprint(material)


def bind_evidence(
    case: GovernanceCase,
    *,
    obligation_ids: list[str],
    evidence_type: str,
    value: Any,
    source_actor: str,
    affected_scope: list[str] | None = None,
    command: str | None = None,
    environment: str | None = None,
    artifact_path_value: str | None = None,
    source_tool: str | None = None,
    observed_at: str | None = None,
    expires_at: str | None = None,
    evidence_id: str | None = None,
    root: Path,
) -> BoundEvidence:
    if not obligation_ids:
        raise VNextError("Evidence must satisfy at least one obligation")
    if not source_actor.strip():
        raise VNextError("Evidence source_actor is required")
    known = {item.obligation_id for item in case.obligations}
    unknown = sorted(set(obligation_ids) - known)
    if unknown:
        raise VNextError(f"Evidence references unknown obligations: {', '.join(unknown)}")
    scope = list(dict.fromkeys(affected_scope or []))
    if not scope:
        scope = sorted(
            {
                path
                for obligation_id in obligation_ids
                for path in case.obligation(obligation_id).affected_scope
            }
        ) or list(case.changed_files)

    normalized_artifact: str | None = None
    calculated_hash: str | None = None
    if artifact_path_value:
        normalized_artifact = normalize_path(artifact_path_value)
        resolved_artifact = safe_project_path(root, normalized_artifact)
        if resolved_artifact.is_file():
            calculated_hash = artifact_hash(resolved_artifact)

    timestamp = observed_at or utc_now()
    parse_timestamp(timestamp, label="observed_at")
    if expires_at:
        parse_timestamp(expires_at, label="expires_at")

    item = BoundEvidence(
        id=evidence_id or new_id("evidence"),
        obligation_ids=list(dict.fromkeys(obligation_ids)),
        affected_scope=scope,
        contribution_fingerprint=case.contribution_fingerprint,
        policy_fingerprint=case.policy_snapshot.policy_fingerprint,
        evidence_type=evidence_type,
        value=value,
        command=command,
        environment=environment,
        artifact_path=normalized_artifact,
        artifact_hash=calculated_hash,
        observed_at=timestamp,
        expires_at=expires_at,
        source_actor=source_actor,
        source_tool=source_tool,
    )
    validate_bound_evidence(
        item,
        case,
        root=root,
        current_contribution_fingerprint=case.contribution_fingerprint,
    )
    return item


def validate_bound_evidence(
    item: BoundEvidence,
    case: GovernanceCase,
    *,
    root: Path,
    current_contribution_fingerprint: str,
    now: str | None = None,
) -> list[str]:
    reasons: list[str] = []
    obligations = {entry.obligation_id: entry for entry in case.obligations}
    known_ids = set(obligations)
    referenced_ids = set(item.obligation_ids)
    unknown = sorted(referenced_ids - known_ids)
    if unknown:
        reasons.append(f"unknown obligations: {', '.join(unknown)}")
    if not referenced_ids:
        reasons.append("evidence satisfies no known obligation")
    expected_types = {
        obligations[obligation_id].evidence_type
        for obligation_id in referenced_ids & known_ids
    }
    if expected_types and (
        len(expected_types) != 1 or item.evidence_type not in expected_types
    ):
        reasons.append(
            "evidence type does not match referenced obligation definitions"
        )
    if is_placeholder(
        item.value,
        allow_explicit_none=item.evidence_type == "known_limitations",
    ):
        reasons.append("evidence value is a placeholder")
    if item.contribution_fingerprint != current_contribution_fingerprint:
        retained = (
            item.retained_for_contribution_fingerprint
            == current_contribution_fingerprint
            and bool(item.retention_reason and item.retention_reason.strip())
        )
        if not retained:
            reasons.append(
                "evidence is bound to a stale contribution fingerprint"
            )
    if (
        item.retained_for_contribution_fingerprint
        and not (item.retention_reason and item.retention_reason.strip())
    ):
        reasons.append("retained evidence binding is missing a reason")
    if item.policy_fingerprint != case.policy_snapshot.policy_fingerprint:
        reasons.append("evidence is bound to a different policy snapshot")
    case_scope = set(case.changed_files)
    file_scope = {
        normalize_path(scope)
        for scope in item.affected_scope
        if not scope.startswith(("symbol:", "tag:"))
    }
    if not item.affected_scope:
        reasons.append("evidence affected scope is empty")
    if file_scope and not file_scope <= case_scope:
        reasons.append("evidence scope includes files outside the contribution")
    if not item.source_actor.strip():
        reasons.append("evidence source actor is missing")
    if (item.command or item.artifact_path) and not item.source_tool:
        reasons.append("evidence source tool is missing")
    if item.command and not item.environment:
        reasons.append("command evidence environment is missing")
    if item.rejection_reason:
        reasons.append(f"evidence was rejected: {item.rejection_reason}")

    if item.artifact_path:
        try:
            path = safe_project_path(root, item.artifact_path)
        except VNextError as exc:
            reasons.append(str(exc))
        else:
            if not path.is_file():
                reasons.append("referenced artifact is missing")
            else:
                observed_hash = artifact_hash(path)
                if item.artifact_hash and item.artifact_hash != observed_hash:
                    reasons.append("referenced artifact hash does not match")
                elif not item.artifact_hash:
                    reasons.append("referenced artifact hash is missing")

    parse_timestamp(item.observed_at, label="observed_at")
    if item.expires_at:
        expiry = parse_timestamp(item.expires_at, label="expires_at")
        current = parse_timestamp(now or utc_now(), label="now")
        if expiry <= current:
            reasons.append("evidence has expired")

    item.invalid_reasons = reasons
    if item.rejection_reason:
        item.validity_state = "rejected"
    elif any("stale contribution" in reason for reason in reasons):
        item.validity_state = "stale"
    elif any("expired" in reason for reason in reasons):
        item.validity_state = "expired"
    elif reasons:
        item.validity_state = "invalid"
    else:
        item.validity_state = "valid"
    return reasons


def validate_evidence_set(
    case: GovernanceCase,
    *,
    root: Path,
    current_contribution_fingerprint: str | None = None,
    now: str | None = None,
) -> list[str]:
    current_fingerprint = (
        current_contribution_fingerprint or case.contribution_fingerprint
    )
    findings: list[str] = []
    for item in case.evidence:
        findings.extend(
            f"{item.id}: {reason}"
            for reason in validate_bound_evidence(
                item,
                case,
                root=root,
                current_contribution_fingerprint=current_fingerprint,
                now=now,
            )
        )

    grouped: dict[tuple[str, str], list[BoundEvidence]] = {}
    for item in case.evidence:
        if item.validity_state not in {"valid", "verified"}:
            continue
        for obligation_id in item.obligation_ids:
            grouped.setdefault((obligation_id, item.evidence_type), []).append(item)
    for (obligation_id, evidence_type), items in grouped.items():
        distinct_values = {canonical_json(item.value) for item in items}
        if len(distinct_values) <= 1:
            continue
        for item in items:
            item.validity_state = "conflicting"
            reason = (
                f"conflicting evidence values for {obligation_id}/{evidence_type}"
            )
            if reason not in item.invalid_reasons:
                item.invalid_reasons.append(reason)
            findings.append(f"{item.id}: {reason}")

    for obligation in case.obligations:
        if obligation.status == "policy_conflict":
            continue
        if obligation.type != "evidence":
            continue
        candidates = [
            item
            for item in case.evidence
            if obligation.obligation_id in item.obligation_ids
            and item.evidence_type == obligation.evidence_type
            and item.validity_state in {"valid", "verified"}
        ]
        if any(item.validity_state == "verified" for item in candidates):
            obligation.status = "verified"
        elif candidates:
            obligation.status = "satisfied"
        else:
            obligation.status = "unsatisfied"
    return findings
