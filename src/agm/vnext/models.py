"""Typed domain records for AGM vNext development."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, TypeVar

from .runtime import current_timestamp, new_record_id


RISK_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
VNextRecord = TypeVar("VNextRecord", bound="RecordMixin")


class VNextError(ValueError):
    """Raised when vNext policy or case data is invalid."""


def utc_now() -> str:
    """Return a stable, timezone-explicit UTC timestamp."""
    return current_timestamp()


def new_id(prefix: str) -> str:
    """Return an opaque record ID with a readable type prefix."""
    return new_record_id(prefix)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


class RecordMixin:
    """Small serialization helper shared by all records."""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls: type[VNextRecord], data: dict[str, Any]) -> VNextRecord:
        return cls(**data)


@dataclass
class PolicySnapshot(RecordMixin):
    id: str
    schema_version: str
    manifest_version: str
    base_commit: str
    policy_fingerprint: str
    resolved_at: str
    source_paths: list[str] = field(default_factory=list)


@dataclass
class MatchedRule(RecordMixin):
    id: str
    rule_id: str
    zone: str
    risk_level: str
    affected_paths: list[str]
    selector_reasons: list[str]
    obligation_ids: list[str]
    case_required: bool = False
    source: str = "risk_rule"
    obligation_overrides: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class CompiledObligation(RecordMixin):
    id: str
    obligation_id: str
    source_rule_ids: list[str]
    type: str
    severity: str
    blocking: bool
    verifier_roles: list[str]
    evidence_type: str
    description: str
    affected_scope: list[str] = field(default_factory=list)
    status: str = "unsatisfied"
    interaction_ids: list[str] = field(default_factory=list)


@dataclass
class BoundEvidence(RecordMixin):
    id: str
    obligation_ids: list[str]
    affected_scope: list[str]
    contribution_fingerprint: str
    policy_fingerprint: str
    evidence_type: str
    value: Any
    command: str | None
    environment: str | None
    artifact_path: str | None
    artifact_hash: str | None
    observed_at: str
    expires_at: str | None
    source_actor: str
    source_tool: str | None
    retained_for_contribution_fingerprint: str | None = None
    retention_reason: str | None = None
    rejected_at: str | None = None
    rejected_by: str | None = None
    rejection_reason: str | None = None
    validity_state: str = "unverified"
    invalid_reasons: list[str] = field(default_factory=list)


@dataclass
class HumanAttestation(RecordMixin):
    id: str
    actor: str
    role: str
    timestamp: str
    reviewed_scope: list[str]
    statement: str
    reservations: list[str]
    policy_fingerprint: str
    contribution_fingerprint: str
    evidence_set_fingerprint: str
    retained_for_contribution_fingerprint: str | None = None
    retention_reason: str | None = None
    status: str = "confirmed"
    invalidated_at: str | None = None
    invalidation_reason: str | None = None


@dataclass
class GovernanceFinding(RecordMixin):
    id: str
    code: str
    severity: str
    message: str
    blocking: bool
    related_object_ids: list[str]
    affected_obligation_ids: list[str]
    status: str = "open"
    created_at: str = field(default_factory=utc_now)
    resolved_at: str | None = None
    resolution: str | None = None


@dataclass
class RepairRequest(RecordMixin):
    id: str
    finding_ids: list[str]
    responsible_role: str
    affected_obligation_ids: list[str]
    requested_correction: str
    revalidation_required: list[str]
    requested_by: str
    requested_at: str
    status: str = "open"
    attempts: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class StateTransition(RecordMixin):
    id: str
    case_id: str
    actor: str
    role: str
    source_state: str
    target_state: str
    action: str
    reason: str
    related_object_ids: list[str]
    timestamp: str


@dataclass
class AttemptedOperation(RecordMixin):
    """Append-only audit fact for an operation that did not take effect."""

    id: str
    case_id: str
    operation: str
    actor: str
    actor_role: str
    attempted_at: str
    result: str
    reason_raw: str
    state_before: str
    state_after: str
    state_changed: bool
    required_roles: list[str] = field(default_factory=list)


@dataclass
class MaintainerVerification(RecordMixin):
    id: str
    actor: str
    role: str
    timestamp: str
    obligation_ids: list[str]
    evidence_ids: list[str]
    outcome: str
    reason: str
    policy_fingerprint: str
    contribution_fingerprint: str


@dataclass
class FinalDecision(RecordMixin):
    id: str
    actor: str
    role: str
    timestamp: str
    decision: str
    reason: str
    override: bool = False
    unresolved_exception_ids: list[str] = field(default_factory=list)


@dataclass
class ClosureReceipt(RecordMixin):
    id: str
    case_id: str
    created_at: str
    policy_fingerprint: str
    contribution_fingerprint: str
    final_state: str
    final_decision_id: str
    matched_rule_ids: list[str]
    obligation_statuses: dict[str, str]
    evidence_ids: list[str]
    attestation_ids: list[str]
    verification_ids: list[str]
    repair_request_ids: list[str]
    unresolved_exception_ids: list[str]
    transition_log_hash: str


@dataclass
class GovernanceCase(RecordMixin):
    id: str
    mode: str
    mode_reason: str
    state: str
    created_at: str
    updated_at: str
    base_commit: str
    changed_files: list[str]
    change_tags: list[str]
    semantic_targets: list[str]
    autonomy_profile: str
    assurance_profile: str
    contribution_fingerprint: str
    policy_snapshot: PolicySnapshot
    overall_risk_level: str
    matched_rules: list[MatchedRule]
    obligations: list[CompiledObligation]
    evidence: list[BoundEvidence] = field(default_factory=list)
    attestations: list[HumanAttestation] = field(default_factory=list)
    findings: list[GovernanceFinding] = field(default_factory=list)
    repair_requests: list[RepairRequest] = field(default_factory=list)
    attempted_operations: list[AttemptedOperation] = field(default_factory=list)
    maintainer_verifications: list[MaintainerVerification] = field(default_factory=list)
    final_decision: FinalDecision | None = None
    closure_receipt: ClosureReceipt | None = None
    schema_version: str = "agm.governance_case/v0.2-dev"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GovernanceCase":
        payload = dict(data)
        payload["policy_snapshot"] = PolicySnapshot.from_dict(payload["policy_snapshot"])
        payload["matched_rules"] = [MatchedRule.from_dict(item) for item in payload.get("matched_rules", [])]
        payload["obligations"] = [
            CompiledObligation.from_dict(item) for item in payload.get("obligations", [])
        ]
        payload["evidence"] = [BoundEvidence.from_dict(item) for item in payload.get("evidence", [])]
        payload["attestations"] = [
            HumanAttestation.from_dict(item) for item in payload.get("attestations", [])
        ]
        payload["findings"] = [
            GovernanceFinding.from_dict(item) for item in payload.get("findings", [])
        ]
        payload["repair_requests"] = [
            RepairRequest.from_dict(item) for item in payload.get("repair_requests", [])
        ]
        payload["attempted_operations"] = [
            AttemptedOperation.from_dict(item)
            for item in payload.get("attempted_operations", [])
        ]
        payload["maintainer_verifications"] = [
            MaintainerVerification.from_dict(item)
            for item in payload.get("maintainer_verifications", [])
        ]
        if payload.get("final_decision"):
            payload["final_decision"] = FinalDecision.from_dict(payload["final_decision"])
        if payload.get("closure_receipt"):
            payload["closure_receipt"] = ClosureReceipt.from_dict(payload["closure_receipt"])
        return cls(**payload)

    def obligation(self, obligation_id: str) -> CompiledObligation:
        for item in self.obligations:
            if item.obligation_id == obligation_id:
                return item
        raise VNextError(f"Unknown obligation '{obligation_id}' in case {self.id}")

    def open_blocking_findings(self) -> list[GovernanceFinding]:
        return [item for item in self.findings if item.blocking and item.status == "open"]

    def unresolved_blocking_obligations(self) -> list[CompiledObligation]:
        return [
            item
            for item in self.obligations
            if item.blocking and item.status not in {"satisfied", "verified", "overridden"}
        ]
