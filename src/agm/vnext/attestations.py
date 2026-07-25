"""Explicit accountable-human attestation events and scoped invalidation."""

from __future__ import annotations

from .config import VNextConfig, normalize_path
from .evidence import evidence_set_fingerprint, is_placeholder
from .models import (
    GovernanceCase,
    HumanAttestation,
    VNextError,
    new_id,
    utc_now,
)


def create_human_attestation(
    config: VNextConfig,
    case: GovernanceCase,
    *,
    actor: str,
    role: str,
    reviewed_scope: list[str],
    statement: str,
    reservations: list[str] | None = None,
    timestamp: str | None = None,
) -> HumanAttestation:
    role_definition = config.roles.get(role)
    if role != "accountable_human" or not role_definition or not role_definition["human"]:
        raise VNextError(
            "Human attestation requires the accountable_human role; agents cannot attest"
        )
    if "confirm_attestation" not in config.permissions.get(role, set()):
        raise VNextError("Role is not authorized to confirm attestation")
    if not actor.strip():
        raise VNextError("Attestation actor is required")
    if not reviewed_scope or any(not item.strip() for item in reviewed_scope):
        raise VNextError("Attestation requires a non-empty reviewed scope")
    if is_placeholder(statement):
        raise VNextError("Attestation statement must be factual and non-placeholder")
    normalized_scope = [
        normalize_path(item)
        if not item.startswith(("symbol:", "tag:"))
        else item
        for item in reviewed_scope
    ]
    allowed_file_scope = set(case.changed_files)
    supplied_file_scope = {
        item
        for item in normalized_scope
        if not item.startswith(("symbol:", "tag:"))
    }
    if not supplied_file_scope <= allowed_file_scope:
        raise VNextError("Attestation scope includes files outside the contribution")
    return HumanAttestation(
        id=new_id("attestation"),
        actor=actor,
        role=role,
        timestamp=timestamp or utc_now(),
        reviewed_scope=list(dict.fromkeys(normalized_scope)),
        statement=statement,
        reservations=list(reservations or []),
        policy_fingerprint=case.policy_snapshot.policy_fingerprint,
        contribution_fingerprint=case.contribution_fingerprint,
        evidence_set_fingerprint=evidence_set_fingerprint(case.evidence),
    )


def apply_attestation_status(case: GovernanceCase) -> None:
    current_evidence_fingerprint = evidence_set_fingerprint(case.evidence)
    valid = [
        item
        for item in case.attestations
        if item.status == "confirmed"
        and item.policy_fingerprint == case.policy_snapshot.policy_fingerprint
        and item.contribution_fingerprint == case.contribution_fingerprint
        and item.evidence_set_fingerprint == current_evidence_fingerprint
    ]
    for obligation in case.obligations:
        if obligation.type != "human_attestation":
            continue
        obligation.status = "satisfied" if valid else "unsatisfied"


def invalidate_attestation(
    case: GovernanceCase,
    *,
    attestation_id: str,
    reason: str,
    timestamp: str | None = None,
) -> HumanAttestation:
    if not reason.strip():
        raise VNextError("Attestation invalidation requires a reason")
    for item in case.attestations:
        if item.id == attestation_id:
            if item.status == "invalidated":
                return item
            item.status = "invalidated"
            item.invalidated_at = timestamp or utc_now()
            item.invalidation_reason = reason
            apply_attestation_status(case)
            return item
    raise VNextError(f"Unknown attestation: {attestation_id}")


def invalidate_stale_attestations(
    case: GovernanceCase,
    *,
    previous_contribution_fingerprint: str,
    previous_evidence_set_fingerprint: str,
    affected_scope: list[str] | None = None,
    reason: str,
    timestamp: str | None = None,
) -> list[str]:
    current_evidence = evidence_set_fingerprint(case.evidence)
    contribution_changed = (
        previous_contribution_fingerprint != case.contribution_fingerprint
    )
    evidence_changed = previous_evidence_set_fingerprint != current_evidence
    if not contribution_changed and not evidence_changed:
        return []
    affected = set(affected_scope or case.changed_files)
    invalidated: list[str] = []
    for item in case.attestations:
        if item.status != "confirmed":
            continue
        if affected and not (set(item.reviewed_scope) & affected):
            continue
        invalidate_attestation(
            case,
            attestation_id=item.id,
            reason=reason,
            timestamp=timestamp,
        )
        invalidated.append(item.id)
    apply_attestation_status(case)
    return invalidated
