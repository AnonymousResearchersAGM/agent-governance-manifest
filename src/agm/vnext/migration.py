"""Read-only migration diagnostics for open Governance Cases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import VNextConfig
from .models import CompiledObligation, GovernanceCase, RISK_RANK
from .obligations import compile_obligations
from .risk import resolve_risk


@dataclass(frozen=True)
class MigrationDiagnostic:
    case_id: str
    policy_changed: bool
    original_policy_fingerprint: str
    current_policy_fingerprint: str
    still_valid_obligations: list[str]
    changed_obligations: list[str]
    added_obligations: list[str]
    removed_obligations: list[str]
    evidence_requiring_revalidation: list[str]
    attestations_invalidated_if_migrated: list[str]
    may_remain_on_original_snapshot: bool
    must_migrate: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            key: getattr(self, key)
            for key in self.__dataclass_fields__
        }


def obligation_signature(item: CompiledObligation) -> dict[str, Any]:
    return {
        "type": item.type,
        "severity": item.severity,
        "blocking": item.blocking,
        "verifier_roles": sorted(item.verifier_roles),
        "evidence_type": item.evidence_type,
        "description": item.description,
    }


def check_migration(
    case: GovernanceCase,
    current_config: VNextConfig,
) -> MigrationDiagnostic:
    policy_changed = (
        case.policy_snapshot.policy_fingerprint
        != current_config.policy_fingerprint
    )
    if not policy_changed:
        obligation_ids = sorted(item.obligation_id for item in case.obligations)
        return MigrationDiagnostic(
            case_id=case.id,
            policy_changed=False,
            original_policy_fingerprint=case.policy_snapshot.policy_fingerprint,
            current_policy_fingerprint=current_config.policy_fingerprint,
            still_valid_obligations=obligation_ids,
            changed_obligations=[],
            added_obligations=[],
            removed_obligations=[],
            evidence_requiring_revalidation=[],
            attestations_invalidated_if_migrated=[],
            may_remain_on_original_snapshot=True,
            must_migrate=False,
            reason="The canonical policy fingerprint is unchanged.",
        )

    resolution = resolve_risk(
        current_config,
        case.changed_files,
        change_tags=case.change_tags,
        semantic_targets=case.semantic_targets,
    )
    current_compilation = compile_obligations(
        current_config,
        resolution.matched_rules,
        resolution.interaction_rules,
        autonomy_profile_id=case.autonomy_profile,
        assurance_profile_id=case.assurance_profile,
    )
    original = {item.obligation_id: item for item in case.obligations}
    current = {
        item.obligation_id: item for item in current_compilation.obligations
    }
    shared = set(original) & set(current)
    changed = sorted(
        obligation_id
        for obligation_id in shared
        if obligation_signature(original[obligation_id])
        != obligation_signature(current[obligation_id])
    )
    still_valid = sorted(shared - set(changed))
    added = sorted(set(current) - set(original))
    removed = sorted(set(original) - set(current))
    affected_obligations = set(changed) | set(removed)
    evidence_revalidation = sorted(
        item.id
        for item in case.evidence
        if set(item.obligation_ids) & affected_obligations
    )
    affected_scope = {
        path
        for obligation_id in affected_obligations
        for path in original.get(
            obligation_id,
            current.get(obligation_id),
        ).affected_scope
    }
    attestation_ids = sorted(
        item.id
        for item in case.attestations
        if item.status == "confirmed"
        and (
            not affected_scope
            or set(item.reviewed_scope) & affected_scope
            or "O-HUMAN-ATTEST" in affected_obligations
        )
    )
    added_critical = any(
        current[item].blocking
        and RISK_RANK[current[item].severity] >= RISK_RANK["critical"]
        for item in added
    )
    policy_setting = (
        current_config.manifest.get("vnext", {}).get("migration_policy")
    )
    must_migrate = policy_setting == "must_follow_current" or added_critical
    if must_migrate:
        reason = (
            "Migration is required because current policy mandates it or adds a "
            "new critical blocking obligation."
        )
    else:
        reason = (
            "Policy changed, but the case may remain on its recorded snapshot; "
            "migration must be an explicit maintainer decision."
        )
    return MigrationDiagnostic(
        case_id=case.id,
        policy_changed=True,
        original_policy_fingerprint=case.policy_snapshot.policy_fingerprint,
        current_policy_fingerprint=current_config.policy_fingerprint,
        still_valid_obligations=still_valid,
        changed_obligations=changed,
        added_obligations=added,
        removed_obligations=removed,
        evidence_requiring_revalidation=evidence_revalidation,
        attestations_invalidated_if_migrated=attestation_ids,
        may_remain_on_original_snapshot=not must_migrate,
        must_migrate=must_migrate,
        reason=reason,
    )
