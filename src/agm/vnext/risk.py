"""Complete rule matching and interaction resolution for vNext."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import Any

from .config import VNextConfig, normalize_path
from .models import MatchedRule, RISK_RANK, VNextError


GOVERNANCE_ENTRYPOINT_PATTERNS = [".agm/**", "AGENTS.md", "CLAUDE.md"]


@dataclass(frozen=True)
class RiskResolution:
    changed_files: list[str]
    matched_rules: list[MatchedRule]
    interaction_rules: list[dict[str, Any]]
    overall_risk_level: str
    policy_required: bool


def path_matches(pattern: str, path: str) -> bool:
    return fnmatch.fnmatch(normalize_path(path), normalize_path(pattern))


def _matched_paths(patterns: list[str], changed_files: list[str]) -> list[str]:
    return sorted(
        {
            changed_file
            for changed_file in changed_files
            if any(path_matches(pattern, changed_file) for pattern in patterns)
        }
    )


def _rule_match(
    rule: dict[str, Any],
    changed_files: list[str],
    change_tags: set[str],
    semantic_targets: set[str],
) -> tuple[list[str], list[str], set[str]]:
    selectors = rule["selectors"]
    affected: set[str] = set()
    reasons: list[str] = []
    path_affected: set[str] = set()

    patterns = selectors.get("paths", [])
    if patterns:
        matched = _matched_paths(patterns, changed_files)
        if matched:
            affected.update(matched)
            path_affected.update(matched)
            reasons.append(f"path selectors matched: {', '.join(matched)}")

    configured_tags = set(selectors.get("change_types", []))
    matched_tags = sorted(change_tags & configured_tags)
    if matched_tags:
        affected.update(changed_files)
        reasons.append(f"change-type tags matched: {', '.join(matched_tags)}")

    configured_targets = set(selectors.get("semantic_targets", []))
    matched_targets = sorted(semantic_targets & configured_targets)
    if matched_targets:
        affected.update(changed_files)
        reasons.append(f"semantic targets matched: {', '.join(matched_targets)}")

    if selectors.get("governance_entrypoint"):
        entrypoints = _matched_paths(GOVERNANCE_ENTRYPOINT_PATTERNS, changed_files)
        if entrypoints:
            affected.update(entrypoints)
            path_affected.update(entrypoints)
            reasons.append(f"governance entrypoints matched: {', '.join(entrypoints)}")

    return sorted(affected), reasons, path_affected


def resolve_risk(
    config: VNextConfig,
    changed_files: list[str],
    *,
    change_tags: list[str] | None = None,
    semantic_targets: list[str] | None = None,
) -> RiskResolution:
    if not changed_files:
        raise VNextError("Cannot resolve risk for an empty changed-file set")
    normalized_files = list(dict.fromkeys(normalize_path(item) for item in changed_files))
    if any(not item or item.startswith("/") for item in normalized_files):
        raise VNextError("Changed files must be non-empty repository-relative paths")

    tags = set(change_tags or [])
    targets = set(semantic_targets or [])
    matched: list[MatchedRule] = []
    files_with_path_match: set[str] = set()

    for rule in config.risk_rules:
        affected, reasons, path_affected = _rule_match(
            rule, normalized_files, tags, targets
        )
        files_with_path_match.update(path_affected)
        if not affected:
            continue
        overrides_raw = rule.get("obligation_overrides", {})
        overrides = {
            obligation_id: dict(value)
            for obligation_id, value in overrides_raw.items()
            if isinstance(value, dict)
        }
        matched.append(
            MatchedRule(
                id=f"match-{rule['id']}",
                rule_id=rule["id"],
                zone=rule["zone"],
                risk_level=rule["risk_level"],
                affected_paths=affected,
                selector_reasons=reasons,
                obligation_ids=list(rule.get("obligation_ids", [])),
                case_required=bool(rule.get("case_required", False)),
                obligation_overrides=overrides,
            )
        )

    unmatched_paths = sorted(set(normalized_files) - files_with_path_match)
    if unmatched_paths:
        fallback = config.fallback_rule
        matched.append(
            MatchedRule(
                id=f"match-{fallback['rule_id']}",
                rule_id=fallback["rule_id"],
                zone=fallback.get("zone", "unclassified_surface"),
                risk_level=fallback["risk_level"],
                affected_paths=unmatched_paths,
                selector_reasons=[
                    "no explicit path selector matched; conservative fallback applied"
                ],
                obligation_ids=list(fallback.get("obligation_ids", [])),
                case_required=bool(fallback.get("case_required", False)),
            )
        )

    if not matched:
        raise VNextError("Risk resolution produced no matched or fallback rules")

    matched_ids = {item.rule_id for item in matched}
    interactions = [
        item
        for item in config.interaction_rules
        if set(item.get("all_rule_ids", [])) <= matched_ids
    ]
    levels = [item.risk_level for item in matched] + [
        item["risk_level"] for item in interactions
    ]
    overall = max(levels, key=lambda value: RISK_RANK[value])
    policy_required = any(item.case_required for item in matched)

    return RiskResolution(
        changed_files=normalized_files,
        matched_rules=matched,
        interaction_rules=interactions,
        overall_risk_level=overall,
        policy_required=policy_required,
    )
