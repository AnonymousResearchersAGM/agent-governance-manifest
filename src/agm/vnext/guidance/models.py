"""Serializable presentation records for the reviewer guidance layer."""

from __future__ import annotations

import warnings
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
class GuidanceReasonPresentation(GuidanceRecord):
    reason_code: str | None
    display_plain: str
    source_english: str | None
    source_code: str | None
    trace_refs: list[TraceReference] = field(default_factory=list)


@dataclass(frozen=True)
class GuidanceExplanation(GuidanceRecord):
    title: str
    technical_term: str
    plain_language: str
    source_references: list[TraceReference] = field(default_factory=list)
    reason_presentation: GuidanceReasonPresentation | None = None


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
class ResponsibilityView(GuidanceRecord):
    primary_roles: list[str]
    display_label: str
    reason: str
    blocking_items: list[str] = field(default_factory=list)
    next_handoff_roles: list[str] = field(default_factory=list)


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
    blocking_requirement: bool
    source_rule_ids: list[str]
    interaction_ids: list[str]
    evidence_ids: list[str]
    binding_fingerprints: list[str]
    finding_ids: list[str]
    reference_english: str
    observed_english: str
    traceability: list[TraceReference] = field(default_factory=list)
    display_name: str = ""
    reference_plain: str = ""
    observed_plain: str = ""
    observed_raw: str = ""
    material_status: str = "missing"
    material_status_label: str = "缺少"
    workflow_status: str = "awaiting_contributor"
    workflow_status_label: str = "等待贡献者处理"
    currently_blocks_progression: bool = False
    affected_scope: list[str] = field(default_factory=list)

    @property
    def blocking(self) -> bool:
        """Deprecated alias for the policy-level requirement property."""

        warnings.warn(
            "RequirementComparison.blocking is deprecated; use "
            "blocking_requirement",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.blocking_requirement

    @property
    def blocks_progression(self) -> bool:
        """Deprecated alias for the current workflow consequence."""

        warnings.warn(
            "RequirementComparison.blocks_progression is deprecated; use "
            "currently_blocks_progression",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.currently_blocks_progression


@dataclass(frozen=True)
class DiagnosticFindingView(GuidanceRecord):
    finding_id: str
    title: str
    plain_language: str
    reason_presentation: GuidanceReasonPresentation
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
class ActionPreviewDisplayEffect(GuidanceRecord):
    display_label: str
    before_label: str
    after_label: str
    display_description: str


@dataclass(frozen=True)
class ContextSelectorOption(GuidanceRecord):
    selector_token: str
    action: str
    label: str
    status_label: str
    affected_scope: list[str]
    obligation_ids: list[str]
    object_type: str
    object_ids: list[str]
    blocking: bool
    material_status: str = ""
    workflow_status: str = ""
    technical_details: dict[str, Any] = field(default_factory=dict)
    traceability: list[TraceReference] = field(default_factory=list)


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
    relevance: str = "other"
    group: str = "other_available"
    primary_reason: str = ""
    selector_options: list[ContextSelectorOption] = field(default_factory=list)


@dataclass(frozen=True)
class UnavailableAction(GuidanceRecord):
    action: str
    title: str
    description: str
    reason: str
    next_actor_roles: list[str]
    mutates_state: bool
    traceability: list[TraceReference] = field(default_factory=list)
    category: str = "stage"
    required_role: list[str] = field(default_factory=list)
    required_state: list[str] = field(default_factory=list)
    future_availability: str = ""


@dataclass(frozen=True)
class GuidanceUtilityAction(GuidanceRecord):
    action_id: str
    label: str
    description: str
    output_type: str
    output: str
    trace_refs: list[TraceReference] = field(default_factory=list)
    state_changing: bool = False


@dataclass(frozen=True)
class MaterialityDeclarationView(GuidanceRecord):
    classification: str
    classification_label: str
    declared_by: str
    reason: str
    reason_presentation: GuidanceReasonPresentation
    affected_obligation_ids: list[str]
    affected_labels: list[str]
    unaffected_obligation_ids: list[str]
    unaffected_labels: list[str]
    retained_evidence_ids: list[str]
    stale_evidence_ids: list[str]
    invalidated_attestation_ids: list[str]
    requires_maintainer_verification: bool
    traceability: list[TraceReference] = field(default_factory=list)


@dataclass(frozen=True)
class RejectedOperationView(GuidanceRecord):
    attempt_id: str
    operation: str
    actor: str
    actor_role: str
    attempted_at: str
    result: str
    display_title: str
    display_message: str
    reason_plain: str
    reason_raw: str
    state_changed: bool
    current_state: str
    current_state_label: str
    required_roles: list[str]
    trace_refs: list[TraceReference] = field(default_factory=list)


@dataclass(frozen=True)
class ActionPreview(GuidanceRecord):
    title: str
    actor: ActorContext
    authorized: bool
    authorization_reason: str
    display_effects: list[ActionPreviewDisplayEffect]
    affected_items: list[str]
    retained_items: list[str]
    invalidated_items: list[str]
    next_authorized_actor_roles: list[str]
    requires_confirmation: bool
    mutates_case: bool
    technical_details: dict[str, Any]
    responsibility_before: ResponsibilityView | None = None
    responsibility_after: ResponsibilityView | None = None
    workflow_position_before: str = ""
    workflow_position_after: str = ""
    next_steps: list[str] = field(default_factory=list)
    requires_human_attestation_after: bool = False
    requires_maintainer_verification_after: bool = False
    final_acceptance_recorded: bool = False
    final_acceptance_still_required: bool = True

    @property
    def action(self) -> str:
        return str(self.technical_details.get("operation", ""))

    @property
    def source_state(self) -> str:
        return str(self.technical_details.get("source_state", ""))

    @property
    def target_state(self) -> str:
        return str(self.technical_details.get("target_state", ""))

    @property
    def effects(self) -> list[ActionEffect]:
        return [
            ActionEffect(**item)
            for item in self.technical_details.get("effects", [])
        ]

    @property
    def affected_obligation_ids(self) -> list[str]:
        return list(
            self.technical_details.get("affected_obligation_ids", [])
        )

    @property
    def retained_evidence_ids(self) -> list[str]:
        return list(
            self.technical_details.get("retained_evidence_ids", [])
        )

    @property
    def invalidated_attestation_ids(self) -> list[str]:
        return list(
            self.technical_details.get(
                "invalidated_attestation_ids",
                [],
            )
        )

    @property
    def preview_fingerprint(self) -> str:
        return str(self.technical_details.get("preview_fingerprint", ""))

    @property
    def traceability(self) -> list[TraceReference]:
        return [
            TraceReference(**item)
            for item in self.technical_details.get("traceability", [])
        ]

    @property
    def processed_objects(self) -> list[str]:
        return list(self.technical_details.get("processed_objects", []))

    @property
    def invalidated_evidence_ids(self) -> list[str]:
        return list(
            self.technical_details.get("invalidated_evidence_ids", [])
        )

    @property
    def workflow_step_before(self) -> str:
        return str(
            self.technical_details.get("workflow_step_before", "")
        )

    @property
    def workflow_step_after(self) -> str:
        return str(
            self.technical_details.get("workflow_step_after", "")
        )

    @property
    def creates_records(self) -> list[str]:
        return list(self.technical_details.get("creates_records", []))


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
    responsibility: ResponsibilityView | None = None
    current_relevant_actions: list[AvailableAction] = field(default_factory=list)
    other_available_actions: list[AvailableAction] = field(default_factory=list)
    unavailable_action_summary: str = ""
    utility_actions: list[GuidanceUtilityAction] = field(default_factory=list)
    materiality_declaration: MaterialityDeclarationView | None = None
    rejected_operation_notice: RejectedOperationView | None = None
