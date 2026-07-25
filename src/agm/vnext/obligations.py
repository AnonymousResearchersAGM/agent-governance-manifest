"""Compile contribution-specific obligations from every applicable source."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import VNextConfig, expanded_profile
from .models import (
    CompiledObligation,
    GovernanceFinding,
    MatchedRule,
    RISK_RANK,
    new_id,
)


COMPATIBLE_STRONGEST_FIELDS = {"blocking", "severity", "verifier_roles"}
CONFLICT_FIELDS = {"type", "evidence_type"}
ALLOWED_OVERRIDE_FIELDS = COMPATIBLE_STRONGEST_FIELDS | CONFLICT_FIELDS | {
    "description"
}


@dataclass(frozen=True)
class CompilationResult:
    obligations: list[CompiledObligation]
    findings: list[GovernanceFinding]
    interaction_ids: list[str]


def _source_map(
    matched_rules: list[MatchedRule],
    interactions: list[dict[str, Any]],
    autonomy_profile: dict[str, Any],
    assurance_profile: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for rule in matched_rules:
        for obligation_id in rule.obligation_ids:
            result.setdefault(obligation_id, []).append(
                {
                    "source_id": rule.rule_id,
                    "scope": rule.affected_paths,
                    "override": rule.obligation_overrides.get(obligation_id, {}),
                    "interaction_id": None,
                }
            )
    for interaction in interactions:
        for obligation_id in interaction.get("obligation_ids", []):
            result.setdefault(obligation_id, []).append(
                {
                    "source_id": interaction["id"],
                    "scope": sorted(
                        {
                            path
                            for rule in matched_rules
                            if rule.rule_id in interaction.get("all_rule_ids", [])
                            for path in rule.affected_paths
                        }
                    ),
                    "override": interaction.get("obligation_overrides", {}).get(
                        obligation_id, {}
                    ),
                    "interaction_id": interaction["id"],
                }
            )
    for profile_kind, profile in (
        ("autonomy", autonomy_profile),
        ("assurance", assurance_profile),
    ):
        for obligation_id in profile.get("obligation_ids", []):
            result.setdefault(obligation_id, []).append(
                {
                    "source_id": f"{profile_kind}:{profile['id']}",
                    "scope": [],
                    "override": {},
                    "interaction_id": None,
                }
            )
    return result


def compile_obligations(
    config: VNextConfig,
    matched_rules: list[MatchedRule],
    interactions: list[dict[str, Any]],
    *,
    autonomy_profile_id: str,
    assurance_profile_id: str,
) -> CompilationResult:
    autonomy = expanded_profile(config.autonomy_profiles, autonomy_profile_id)
    assurance = expanded_profile(config.assurance_profiles, assurance_profile_id)
    sources = _source_map(matched_rules, interactions, autonomy, assurance)
    obligations: list[CompiledObligation] = []
    findings: list[GovernanceFinding] = []

    for obligation_id in sorted(sources):
        definition = dict(config.obligations[obligation_id])
        source_items = sources[obligation_id]
        conflict_messages: list[str] = []
        severity_values = [definition["severity"]]
        blocking_values = [definition["blocking"]]
        verifier_roles = set(definition["verifier_roles"])
        conflict_values: dict[str, set[str]] = {
            "type": {str(definition["type"])},
            "evidence_type": {str(definition["evidence_type"])},
        }
        description = str(definition.get("description", ""))

        for source in source_items:
            override = source.get("override") or {}
            unknown = sorted(set(override) - ALLOWED_OVERRIDE_FIELDS)
            if unknown:
                conflict_messages.append(
                    f"{source['source_id']} supplied unknown override fields "
                    f"{', '.join(unknown)}"
                )
            if "severity" in override:
                if override["severity"] in RISK_RANK:
                    severity_values.append(override["severity"])
                else:
                    conflict_messages.append(
                        f"{source['source_id']} supplied invalid severity"
                    )
            if "blocking" in override:
                if isinstance(override["blocking"], bool):
                    blocking_values.append(override["blocking"])
                else:
                    conflict_messages.append(
                        f"{source['source_id']} supplied non-boolean blocking value"
                    )
            if "verifier_roles" in override:
                raw_roles = override["verifier_roles"]
                if isinstance(raw_roles, list) and all(
                    role in config.roles for role in raw_roles
                ):
                    verifier_roles.update(raw_roles)
                else:
                    conflict_messages.append(
                        f"{source['source_id']} supplied invalid verifier roles"
                    )
            for field_name in CONFLICT_FIELDS:
                if field_name in override:
                    conflict_values[field_name].add(str(override[field_name]))
            if "description" in override and override["description"] != description:
                conflict_messages.append(
                    f"{source['source_id']} supplied a contradictory description"
                )

        for field_name, values in conflict_values.items():
            if len(values) > 1:
                conflict_messages.append(
                    f"incompatible {field_name} values: {', '.join(sorted(values))}"
                )

        severity = max(severity_values, key=lambda value: RISK_RANK[value])
        blocking = any(blocking_values)
        status = "policy_conflict" if conflict_messages else "unsatisfied"
        source_ids = sorted({item["source_id"] for item in source_items})
        interaction_ids = sorted(
            {
                item["interaction_id"]
                for item in source_items
                if item.get("interaction_id")
            }
        )
        affected_scope = sorted(
            {
                scope
                for item in source_items
                for scope in item.get("scope", [])
            }
        )
        obligation = CompiledObligation(
            id=f"obl-{obligation_id.lower()}",
            obligation_id=obligation_id,
            source_rule_ids=source_ids,
            type=definition["type"],
            severity=severity,
            blocking=blocking,
            verifier_roles=sorted(verifier_roles),
            evidence_type=definition["evidence_type"],
            description=description,
            affected_scope=affected_scope,
            status=status,
            interaction_ids=interaction_ids,
        )
        obligations.append(obligation)
        if conflict_messages:
            findings.append(
                GovernanceFinding(
                    id=new_id("finding"),
                    code="policy_conflict",
                    severity=severity,
                    message=(
                        f"Obligation {obligation_id} has contradictory policy inputs: "
                        + "; ".join(conflict_messages)
                    ),
                    blocking=True,
                    related_object_ids=[obligation.id],
                    affected_obligation_ids=[obligation_id],
                )
            )

    return CompilationResult(
        obligations=obligations,
        findings=findings,
        interaction_ids=sorted(item["id"] for item in interactions),
    )
