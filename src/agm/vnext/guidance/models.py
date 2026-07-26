"""Serializable presentation records for the reviewer guidance layer."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


class GuidanceRecord:
    """JSON-ready serialization shared by immutable guidance records."""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ActorContext(GuidanceRecord):
    actor: str
    role: str
    human: bool = False


@dataclass(frozen=True)
class TraceReference(GuidanceRecord):
    kind: str
    object_id: str
    relationship: str


@dataclass(frozen=True)
class GuidanceExplanation(GuidanceRecord):
    title: str
    technical_term: str
    plain_language: str
    source_references: list[TraceReference] = field(default_factory=list)


@dataclass(frozen=True)
class ContributionSummary(GuidanceRecord):
    case_id: str | None
    changed_files: list[str]
    risk_level: str
    risk_areas: list[str]
    autonomy_profile: str
    path_kind: str
    path_label: str
    current_stage: str
    blocking_issue_count: int
    warning_count: int
    current_responsible_parties: list[str]
    next_authorized_actor_roles: list[str]
    raw_state: str
    raw_readiness: str


@dataclass(frozen=True)
class WorkflowStepView(GuidanceRecord):
    number: int
    step_id: str
    title: str
    status: str
    status_label: str
    symbol: str
    explanation: str
    internal_stages: list[str]
    traceability: list[TraceReference] = field(default_factory=list)


@dataclass(frozen=True)
class RequirementComparison(GuidanceRecord):
    obligation_id: str
    check_item: str
    project_requirement: str
    current_situation: str
    result: str
    result_label: str
    raw_status: str
    blocking: bool
    source_rule_ids: list[str]
    interaction_ids: list[str]
    evidence_ids: list[str]
    binding_fingerprints: list[str]
    finding_ids: list[str]
    reference_english: str
    observed_english: str
    traceability: list[TraceReference] = field(default_factory=list)


@dataclass(frozen=True)
class DiagnosticFindingView(GuidanceRecord):
    finding_id: str
    title: str
    plain_language: str
    severity: str
    blocking: bool
    status: str
    affected_obligation_ids: list[str]
    repair_request_ids: list[str]
    traceability: list[TraceReference] = field(default_factory=list)


@dataclass(frozen=True)
class ActionEffect(GuidanceRecord):
    target: str
    before: str
    after: str
    explanation: str
    source_object_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AvailableAction(GuidanceRecord):
    action: str
    title: str
    description: str
    consequence: str
    mutates_state: bool
    actor_role: str
    default_obligation_ids: list[str] = field(default_factory=list)
    required_parameters: list[str] = field(default_factory=list)
    traceability: list[TraceReference] = field(default_factory=list)


@dataclass(frozen=True)
class UnavailableAction(GuidanceRecord):
    action: str
    title: str
    description: str
    reason: str
    next_actor_roles: list[str]
    mutates_state: bool
    traceability: list[TraceReference] = field(default_factory=list)


@dataclass(frozen=True)
class ActionPreview(GuidanceRecord):
    action: str
    title: str
    actor: ActorContext
    authorized: bool
    authorization_reason: str
    source_state: str
    target_state: str
    effects: list[ActionEffect]
    affected_obligation_ids: list[str]
    retained_evidence_ids: list[str]
    invalidated_attestation_ids: list[str]
    next_authorized_actor_roles: list[str]
    requires_confirmation: bool
    mutates_case: bool
    preview_fingerprint: str
    traceability: list[TraceReference] = field(default_factory=list)


@dataclass(frozen=True)
class ReviewerGuidanceView(GuidanceRecord):
    schema_version: str
    generated_from_case_fingerprint: str
    actor: ActorContext
    summary: ContributionSummary
    workflow_steps: list[WorkflowStepView]
    requirement_comparisons: list[RequirementComparison]
    diagnostics: list[DiagnosticFindingView]
    available_actions: list[AvailableAction]
    unavailable_actions: list[UnavailableAction]
    explanations: list[GuidanceExplanation]
    delegation_help: GuidanceExplanation
    repair_loop: list[str]
    technical_details: dict[str, Any]
    authority_notice: str
