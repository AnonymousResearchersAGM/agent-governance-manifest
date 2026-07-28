"""Immutable participant-facing records; internal identifiers stay in details."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


class DiagnosticRecord:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InspectionObject(DiagnosticRecord):
    title: str
    object_type: str
    plain_language_summary: str
    source: str
    bound_commit: str
    content_digest: str | None
    availability: str
    freshness: str
    view_href: str | None = None
    inline_content: str | None = None
    technical_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiagnosticFinding(DiagnosticRecord):
    finding_id: str
    category: str
    severity: str
    headline: str
    plain_language_explanation: str
    affected_files: tuple[str, ...]
    affected_line_ranges: tuple[str, ...]
    expected_state: str
    observed_state: str
    gap: str
    risk_rule_refs: tuple[str, ...]
    obligation_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    responsibility: str
    recommended_route: str
    blocking: bool
    source_state_refs: tuple[str, ...]


@dataclass(frozen=True)
class ActionEffectBoundary(DiagnosticRecord):
    label: str
    existing_operation: str
    will_do: tuple[str, ...]
    will_not_do: tuple[str, ...]


@dataclass(frozen=True)
class PRDiagnosticView(DiagnosticRecord):
    case_id: str
    contribution_fingerprint: str
    policy_fingerprint: str
    diagnostic_status: str
    change_summary: dict[str, Any]
    risk_findings: tuple[DiagnosticFinding, ...]
    expected_requirements: tuple[dict[str, Any], ...]
    observed_evidence: tuple[dict[str, Any], ...]
    evidence_gaps: tuple[DiagnosticFinding, ...]
    agent_involvement: dict[str, Any]
    human_review_status: dict[str, Any]
    review_readiness: dict[str, Any]
    recommended_route: dict[str, Any]
    inspection_objects: tuple[InspectionObject, ...]
    action_effect_boundaries: tuple[ActionEffectBoundary, ...]
    technical_derivation: dict[str, Any]
    schema_version: str = "agm.pr_diagnostic/v0.2-dev"
