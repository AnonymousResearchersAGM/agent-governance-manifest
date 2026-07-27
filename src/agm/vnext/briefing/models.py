"""Immutable, serializable records for the AGM Review Briefing Layer."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


class BriefRecord:
    """Return JSON-ready dictionaries without exposing mutable domain objects."""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ContributionBrief(BriefRecord):
    title: str
    plain_summary: str
    changed_files: tuple[str, ...]
    changed_components: tuple[str, ...]
    behavioral_impacts: tuple[str, ...]
    security_sensitive_changes: tuple[str, ...]
    configuration_changes: tuple[str, ...]
    governance_changes: tuple[str, ...]
    agent_involvement: str
    summary_source: str
    system_inferred_summary: str
    inference_limitations: str
    contributor_claims: tuple[str, ...] = ()


@dataclass(frozen=True)
class RiskBrief(BriefRecord):
    overall_level: str
    display_level: str
    triggered_risk_areas: tuple[str, ...]
    plain_reasons: tuple[str, ...]
    matched_rule_refs: tuple[str, ...]
    interaction_effects: tuple[str, ...]
    requires_independent_review: bool


@dataclass(frozen=True)
class RequirementItem(BriefRecord):
    requirement_key: str
    display_title: str
    status: str
    status_label: str
    plain_status: str
    blocking: bool
    trace_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class RequirementBrief(BriefRecord):
    total_required: int
    items: tuple[RequirementItem, ...]
    system_satisfied: tuple[RequirementItem, ...] = ()
    provided_requires_human_judgment: tuple[RequirementItem, ...] = ()
    missing: tuple[RequirementItem, ...] = ()
    stale: tuple[RequirementItem, ...] = ()
    invalid: tuple[RequirementItem, ...] = ()
    awaiting_accountable_human: tuple[RequirementItem, ...] = ()
    awaiting_independent_review: tuple[RequirementItem, ...] = ()
    not_applicable: tuple[RequirementItem, ...] = ()


@dataclass(frozen=True)
class AutomaticCheckResult(BriefRecord):
    check_type: str
    display_title: str
    status: str
    plain_result: str
    supporting_evidence: tuple[str, ...]
    limitations: tuple[str, ...]
    requires_human_action: bool
    trace_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContributorAccountabilityBrief(BriefRecord):
    agent_used: bool
    agent_capabilities: tuple[str, ...]
    agent_actions: tuple[str, ...]
    delegation_detected: bool | None
    declaration_source: str
    declaration_status: str
    accountable_human: str | None
    attestation_status: str
    attestation_scope: tuple[str, ...]
    attestation_version_binding: str
    system_observations: tuple[str, ...] = ()
    declared_facts: tuple[str, ...] = ()
    human_confirmed_facts: tuple[str, ...] = ()
    unverified_inferences: tuple[str, ...] = ()


@dataclass(frozen=True)
class HumanJudgmentItem(BriefRecord):
    judgment_id: str
    display_title: str
    why_human_is_needed: str
    contribution_claim: str
    system_observation: str
    evidence_summary: str
    review_focus: tuple[str, ...]
    possible_outcomes: tuple[str, ...]
    priority: str
    blocking: bool
    trace_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class NextStepBrief(BriefRecord):
    status: str
    display_title: str
    plain_explanation: str
    responsible_party: str
    system_will_do: tuple[str, ...]
    human_should_do: tuple[str, ...]
    final_acceptance_state: str


@dataclass(frozen=True)
class GovernanceTechnicalDetails(BriefRecord):
    case_id: str
    raw_state: str
    raw_readiness: str
    contribution_fingerprint: str
    policy_fingerprint: str
    policy_snapshot: dict[str, Any]
    matched_rules: tuple[dict[str, Any], ...]
    compiled_obligations: tuple[dict[str, Any], ...]
    evidence_records: tuple[dict[str, Any], ...]
    attestation_records: tuple[dict[str, Any], ...]
    findings: tuple[dict[str, Any], ...]
    repair_requests: tuple[dict[str, Any], ...]
    attempted_operations: tuple[dict[str, Any], ...]
    verification_records: tuple[dict[str, Any], ...]
    transition_history: tuple[dict[str, Any], ...]
    final_decision: dict[str, Any] | None
    closure_receipt: dict[str, Any] | None
    policy_migration_diagnostic: dict[str, Any] | None
    reviewer_guidance: dict[str, Any]
    trace_index: dict[str, tuple[dict[str, str], ...]] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class ReviewBriefView(BriefRecord):
    contribution: ContributionBrief
    risk: RiskBrief
    requirements: RequirementBrief
    automatic_checks: tuple[AutomaticCheckResult, ...]
    contributor_accountability: ContributorAccountabilityBrief
    human_judgments: tuple[HumanJudgmentItem, ...]
    current_next_step: NextStepBrief
    governance_details: GovernanceTechnicalDetails
    schema_version: str = "agm.review_brief/v0.2-dev"
    authority_notice: str = (
        "系统确认、维护者检查完成或具备最终决定条件，都不等于贡献已被接受；"
        "最终接受、拒绝或合并决定仍由获授权的人类维护者作出。"
    )
