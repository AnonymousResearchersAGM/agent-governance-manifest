"""Immutable records for item-bound maintainer review actions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ..models import ReviewBriefView


class ActionRecord:
    """Serialize action-layer records without exposing mutable domain objects."""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class JudgmentOption(ActionRecord):
    option_id: str
    display_label: str
    plain_consequence: str
    requires_reason: bool
    consequence_type: str
    authorized: bool
    unavailable_reason: str | None
    existing_operation_ref: str | None


@dataclass(frozen=True)
class InteractiveJudgmentItem(ActionRecord):
    judgment_id: str
    display_title: str
    why_human_is_needed: str
    contribution_claim: str
    system_observation: str
    evidence_summary: str
    review_focus: tuple[str, ...]
    options: tuple[JudgmentOption, ...]
    blocking: bool
    requirement_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ReviewActionView(ActionRecord):
    case_id: str
    actor_id: str
    role: str
    contribution_fingerprint: str
    policy_snapshot_fingerprint: str
    case_state: str
    items: tuple[InteractiveJudgmentItem, ...]
    live_actions_enabled: bool
    can_save_draft: bool
    can_preview: bool
    unavailable_reason: str | None
    maintainer_stage_ready: bool
    current_stage: str
    stage_unavailable_reason: str | None
    current_next_step: dict[str, Any]
    system_handled_anomalies: tuple[dict[str, Any], ...] = ()
    final_decision_entry_available: bool = False
    schema_version: str = "agm.review_action_view/v0.2-dev"


@dataclass(frozen=True)
class JudgmentDecision(ActionRecord):
    judgment_id: str
    selected_option_id: str
    reason: str | None
    requirement_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ReviewDecisionDraft(ActionRecord):
    draft_id: str
    case_id: str
    actor_id: str
    role: str
    contribution_fingerprint: str
    policy_snapshot_fingerprint: str
    judgment_decisions: tuple[JudgmentDecision, ...]
    created_at: str
    updated_at: str
    status: str = "draft"


@dataclass(frozen=True)
class DraftAssessment(ActionRecord):
    stale: bool
    complete: bool
    reasons: tuple[str, ...]
    missing_judgment_ids: tuple[str, ...]
    changed_judgment_ids: tuple[str, ...]


@dataclass(frozen=True)
class ExistingOperationPlan(ActionRecord):
    operation: str
    consequence_type: str
    obligation_ids: tuple[str, ...]
    judgment_ids: tuple[str, ...]
    reason: str
    responsible_role: str | None = None


@dataclass(frozen=True)
class ReviewSubmissionPreview(ActionRecord):
    case_id: str
    actor_id: str
    role: str
    draft_id: str
    authorized: bool
    unavailable_reason: str | None
    summary_lines: tuple[str, ...]
    operation_plans: tuple[ExistingOperationPlan, ...]
    retained_evidence_count: int
    affected_requirement_refs: tuple[str, ...]
    contribution_fingerprint: str
    policy_snapshot_fingerprint: str
    case_state: str
    preview_fingerprint: str
    preview_token: str | None
    expires_at: str | None
    schema_version: str = "agm.review_submission_preview/v0.2-dev"


@dataclass(frozen=True)
class ReviewSubmissionResult(ActionRecord):
    case_id: str
    submitted: bool
    message: str
    executed_operations: tuple[str, ...]
    submission_id: str
    submitted_at: str
    next_review_brief: ReviewBriefView
    replay_safe: bool = True
    schema_version: str = "agm.review_submission_result/v0.2-dev"


@dataclass(frozen=True)
class FinalDecisionOption(ActionRecord):
    decision_id: str
    display_label: str
    plain_consequence: str
    requires_reason: bool
    authorized: bool
    unavailable_reason: str | None
    existing_operation_ref: str | None


@dataclass(frozen=True)
class FinalDecisionView(ActionRecord):
    case_id: str
    actor_id: str
    role: str
    case_state: str
    contribution_summary: str
    risk_summary: str
    requirement_summary: str
    verification_summary: str
    unresolved_finding_summary: str
    final_authority_summary: str
    acceptance_boundary: str
    options: tuple[FinalDecisionOption, ...]
    available: bool
    unavailable_reason: str | None
    schema_version: str = "agm.final_decision_view/v0.2-dev"


@dataclass(frozen=True)
class FinalDecisionPreview(ActionRecord):
    case_id: str
    actor_id: str
    role: str
    decision_id: str
    display_label: str
    reason: str
    summary_lines: tuple[str, ...]
    contribution_fingerprint: str
    policy_snapshot_fingerprint: str
    case_state: str
    preview_fingerprint: str
    preview_token: str | None
    expires_at: str | None
    authorized: bool
    unavailable_reason: str | None
    schema_version: str = "agm.final_decision_preview/v0.2-dev"


@dataclass(frozen=True)
class FinalDecisionResult(ActionRecord):
    case_id: str
    decision: str
    message: str
    executed_operation: str
    decided_at: str
    next_review_brief: ReviewBriefView
    schema_version: str = "agm.final_decision_result/v0.2-dev"


@dataclass
class StoredPreviewToken:
    token: str
    kind: str
    case_id: str
    actor_id: str
    role: str
    preview_fingerprint: str
    payload: dict[str, Any]
    issued_at: str
    expires_at: str
    used: bool = False
    result_fingerprint: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
