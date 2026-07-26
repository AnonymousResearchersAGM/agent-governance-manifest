"""Application service that enacts the vNext lifecycle without crossing authority boundaries."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .attestations import (
    apply_attestation_status,
    create_human_attestation,
    invalidate_attestation,
    invalidate_stale_attestations,
)
from .config import VNextConfig, load_vnext_config
from .evidence import (
    bind_evidence,
    evidence_set_fingerprint,
    validate_evidence_set,
)
from .migration import MigrationDiagnostic, check_migration
from .models import (
    ClosureReceipt,
    FinalDecision,
    GovernanceCase,
    GovernanceFinding,
    MaintainerVerification,
    RISK_RANK,
    VNextError,
    new_id,
    utc_now,
)
from .obligations import CompilationResult, compile_obligations
from .policy import (
    IntakeDecision,
    contribution_fingerprint,
    decide_intake,
    make_policy_snapshot,
    repository_head,
)
from .repair import (
    create_finding,
    create_repair_request,
    record_resubmission,
    resolve_finding,
)
from .risk import RiskResolution, resolve_risk
from .state_machine import authorize, transition_case
from .storage import CaseStorage


class GovernanceService:
    def __init__(
        self,
        root: Path,
        *,
        work_root: Path | None = None,
        config: VNextConfig | None = None,
    ):
        self.root = root.resolve()
        self.config = config or load_vnext_config(self.root)
        self.storage = CaseStorage(self.root, work_root=work_root)

    def simulate(
        self,
        changed_files: list[str],
        *,
        requested_mode: str = "ordinary",
        change_tags: list[str] | None = None,
        semantic_targets: list[str] | None = None,
        autonomy_profile: str = "human_direct",
        assurance_profile: str = "standard",
    ) -> dict[str, Any]:
        resolution = resolve_risk(
            self.config,
            changed_files,
            change_tags=change_tags,
            semantic_targets=semantic_targets,
        )
        intake = decide_intake(requested_mode, resolution)
        compilation = compile_obligations(
            self.config,
            resolution.matched_rules,
            resolution.interaction_rules,
            autonomy_profile_id=autonomy_profile,
            assurance_profile_id=assurance_profile,
        )
        return {
            "intake": intake.__dict__,
            "overall_risk_level": resolution.overall_risk_level,
            "matched_rules": [
                item.to_dict() for item in resolution.matched_rules
            ],
            "interaction_rules": [
                item["id"] for item in resolution.interaction_rules
            ],
            "compiled_obligations": [
                item.to_dict() for item in compilation.obligations
            ],
            "findings": [item.to_dict() for item in compilation.findings],
        }

    def open_case(
        self,
        changed_files: list[str],
        *,
        requested_mode: str,
        actor: str,
        actor_role: str,
        case_id: str | None = None,
        base_commit: str | None = None,
        change_tags: list[str] | None = None,
        semantic_targets: list[str] | None = None,
        autonomy_profile: str = "supervised_agent",
        assurance_profile: str = "standard",
        diff_material: str | None = None,
        timestamp: str | None = None,
    ) -> tuple[GovernanceCase | None, IntakeDecision]:
        authorize(self.config, role=actor_role, action="open_case")
        resolution = resolve_risk(
            self.config,
            changed_files,
            change_tags=change_tags,
            semantic_targets=semantic_targets,
        )
        intake = decide_intake(requested_mode, resolution)
        if not intake.case_required:
            return None, intake
        compilation = compile_obligations(
            self.config,
            resolution.matched_rules,
            resolution.interaction_rules,
            autonomy_profile_id=autonomy_profile,
            assurance_profile_id=assurance_profile,
        )
        effective_base = base_commit or repository_head(self.root)
        case_fingerprint = contribution_fingerprint(
            self.root,
            resolution.changed_files,
            base_commit=effective_base,
            change_tags=change_tags,
            semantic_targets=semantic_targets,
            diff_material=diff_material,
        )
        occurred_at = timestamp or utc_now()
        case = GovernanceCase(
            id=case_id or new_id("case"),
            mode=intake.effective_mode,
            mode_reason=intake.reason,
            state=self.config.state_machine["initial_state"],
            created_at=occurred_at,
            updated_at=occurred_at,
            base_commit=effective_base,
            changed_files=resolution.changed_files,
            change_tags=list(change_tags or []),
            semantic_targets=list(semantic_targets or []),
            autonomy_profile=autonomy_profile,
            assurance_profile=assurance_profile,
            contribution_fingerprint=case_fingerprint,
            policy_snapshot=make_policy_snapshot(
                self.config,
                base_commit=effective_base,
                resolved_at=occurred_at,
            ),
            overall_risk_level=resolution.overall_risk_level,
            matched_rules=resolution.matched_rules,
            obligations=compilation.obligations,
            findings=compilation.findings,
        )
        self.storage.create_case(case)
        self._transition(
            case,
            action="resolve_policy",
            actor="agm-engine",
            role="system",
            reason="Resolved canonical policy against the contribution.",
            related_object_ids=[case.policy_snapshot.id],
            timestamp=occurred_at,
        )
        self._transition(
            case,
            action="compile_obligations",
            actor="agm-engine",
            role="system",
            reason="Compiled the union of matched, profile, and interaction obligations.",
            related_object_ids=[item.id for item in case.obligations],
            timestamp=occurred_at,
        )
        self._transition(
            case,
            action="mark_evidence_state",
            actor="agm-engine",
            role="system",
            reason="The new case has unsatisfied evidence obligations.",
            related_object_ids=[
                item.id
                for item in case.obligations
                if item.type == "evidence"
            ],
            timestamp=occurred_at,
        )
        self.storage.save_case(case)
        return case, intake

    def add_evidence(
        self,
        case_id: str,
        *,
        actor: str,
        actor_role: str,
        obligation_ids: list[str],
        evidence_type: str,
        value: Any,
        affected_scope: list[str] | None = None,
        command: str | None = None,
        environment: str | None = None,
        artifact_path: str | None = None,
        source_tool: str | None = None,
        observed_at: str | None = None,
        expires_at: str | None = None,
        evidence_id: str | None = None,
    ):
        authorize(self.config, role=actor_role, action="prepare_evidence")
        case = self.storage.load_case(case_id)
        previous_evidence_fingerprint = evidence_set_fingerprint(case.evidence)
        item = bind_evidence(
            case,
            obligation_ids=obligation_ids,
            evidence_type=evidence_type,
            value=value,
            source_actor=actor,
            affected_scope=affected_scope,
            command=command,
            environment=environment,
            artifact_path_value=artifact_path,
            source_tool=source_tool,
            observed_at=observed_at,
            expires_at=expires_at,
            evidence_id=evidence_id,
            root=self.root,
        )
        case.evidence.append(item)
        validate_evidence_set(case, root=self.root)
        invalidate_stale_attestations(
            case,
            previous_contribution_fingerprint=case.contribution_fingerprint,
            previous_evidence_set_fingerprint=previous_evidence_fingerprint,
            affected_scope=item.affected_scope,
            reason="The bound evidence set changed after attestation.",
        )
        if item.invalid_reasons:
            existing = any(
                finding.code == "evidence_invalid"
                and item.id in finding.related_object_ids
                and finding.status == "open"
                for finding in case.findings
            )
            if not existing:
                create_finding(
                    case,
                    code="evidence_invalid",
                    severity=max(
                        (
                            case.obligation(obligation_id).severity
                            for obligation_id in item.obligation_ids
                        ),
                        default="high",
                        key=lambda value: RISK_RANK[value],
                    ),
                    message="; ".join(item.invalid_reasons),
                    blocking=True,
                    related_object_ids=[item.id],
                    affected_obligation_ids=item.obligation_ids,
                )
        self.storage.save_case(case)
        return item

    def prepare_case(
        self,
        case_id: str,
        *,
        actor: str,
        actor_role: str,
    ) -> GovernanceCase:
        case = self.storage.load_case(case_id)
        validate_evidence_set(case, root=self.root)
        apply_attestation_status(case)
        evidence_blockers = [
            item
            for item in case.obligations
            if item.type == "evidence"
            and item.blocking
            and item.status not in {"satisfied", "verified", "overridden"}
        ]
        if evidence_blockers:
            if case.state == "resubmitted":
                self._transition(
                    case,
                    action="mark_evidence_state",
                    actor="agm-engine",
                    role="system",
                    reason="Resubmitted evidence remains incomplete.",
                    related_object_ids=[item.id for item in evidence_blockers],
                )
            self.storage.save_case(case)
            return case

        attestation_required = any(
            item.type == "human_attestation"
            and item.blocking
            and item.status not in {"satisfied", "verified", "overridden"}
            for item in case.obligations
        )
        if attestation_required:
            if case.state in {
                "obligations_compiled",
                "evidence_incomplete",
                "resubmitted",
            }:
                self._transition(
                    case,
                    action="await_attestation",
                    actor="agm-engine",
                    role="system",
                    reason="Evidence is prepared; explicit accountable-human attestation is required.",
                )
        elif case.state in {
            "obligations_compiled",
            "evidence_incomplete",
            "resubmitted",
        }:
            self._transition(
                case,
                action="submit_for_verification",
                actor=actor,
                role=actor_role,
                reason="Contributor submitted prepared evidence for maintainer verification.",
                related_object_ids=[item.id for item in case.evidence],
            )
        self.storage.save_case(case)
        return case

    def attest(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        reviewed_scope: list[str],
        statement: str,
        reservations: list[str] | None = None,
        timestamp: str | None = None,
    ):
        if role != "accountable_human":
            raise VNextError(
                "Human attestation requires the accountable_human role; agents cannot attest"
            )
        authorize(self.config, role=role, action="confirm_attestation")
        case = self.storage.load_case(case_id)
        validate_evidence_set(case, root=self.root)
        evidence_blockers = [
            item
            for item in case.obligations
            if item.type == "evidence"
            and item.blocking
            and item.status not in {"satisfied", "verified", "overridden"}
        ]
        if evidence_blockers:
            raise VNextError(
                "Human attestation cannot be confirmed while evidence obligations are incomplete"
            )
        attestation = create_human_attestation(
            self.config,
            case,
            actor=actor,
            role=role,
            reviewed_scope=reviewed_scope,
            statement=statement,
            reservations=reservations,
            timestamp=timestamp,
        )
        case.attestations.append(attestation)
        apply_attestation_status(case)
        self._transition(
            case,
            action="confirm_attestation",
            actor=actor,
            role=role,
            reason="Accountable human confirmed the explicitly reviewed scope.",
            related_object_ids=[attestation.id],
            timestamp=timestamp,
        )
        self.storage.save_case(case)
        return attestation

    def invalidate_attestation(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        attestation_id: str,
        reason: str,
    ):
        authorize(self.config, role=role, action="invalidate_attestation")
        case = self.storage.load_case(case_id)
        result = invalidate_attestation(
            case, attestation_id=attestation_id, reason=reason
        )
        finding = create_finding(
            case,
            code="attestation_invalidated",
            severity="high",
            message=f"{actor} invalidated attestation {attestation_id}: {reason}",
            blocking=True,
            related_object_ids=[attestation_id],
            affected_obligation_ids=[
                item.obligation_id
                for item in case.obligations
                if item.type == "human_attestation"
            ],
        )
        repair = create_repair_request(
            case,
            finding_ids=[finding.id],
            responsible_role="accountable_human",
            requested_correction="Provide a new scoped attestation after correction.",
            requested_by=actor,
        )
        self._transition(
            case,
            action="invalidate_attestation",
            actor=actor,
            role=role,
            reason=reason,
            related_object_ids=[attestation_id, finding.id, repair.id],
        )
        self.storage.save_case(case)
        return result

    def decline_attestation(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        reason: str,
    ):
        authorize(self.config, role=role, action="decline_attestation")
        case = self.storage.load_case(case_id)
        finding = create_finding(
            case,
            code="attestation_declined",
            severity="high",
            message=reason,
            blocking=True,
            affected_obligation_ids=[
                item.obligation_id
                for item in case.obligations
                if item.type == "human_attestation"
            ],
        )
        repair = create_repair_request(
            case,
            finding_ids=[finding.id],
            responsible_role="contributor",
            requested_correction=reason,
            requested_by=actor,
        )
        self._transition(
            case,
            action="decline_attestation",
            actor=actor,
            role=role,
            reason=reason,
            related_object_ids=[finding.id, repair.id],
        )
        self.storage.save_case(case)
        return repair

    def request_correction(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        reason: str,
        affected_obligation_ids: list[str],
    ):
        authorize(self.config, role=role, action="request_correction")
        case = self.storage.load_case(case_id)
        finding = create_finding(
            case,
            code="attestation_correction_requested",
            severity="high",
            message=reason,
            blocking=True,
            affected_obligation_ids=affected_obligation_ids,
        )
        repair = create_repair_request(
            case,
            finding_ids=[finding.id],
            responsible_role="contributor",
            requested_correction=reason,
            requested_by=actor,
        )
        self._transition(
            case,
            action="request_correction",
            actor=actor,
            role=role,
            reason=reason,
            related_object_ids=[finding.id, repair.id],
        )
        self.storage.save_case(case)
        return repair

    def reject_evidence(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        evidence_id: str,
        reason: str,
    ):
        authorize(self.config, role=role, action="reject_evidence")
        case = self.storage.load_case(case_id)
        evidence = next(
            (item for item in case.evidence if item.id == evidence_id), None
        )
        if evidence is None:
            raise VNextError(f"Unknown evidence: {evidence_id}")
        evidence.rejected_at = utc_now()
        evidence.rejected_by = actor
        evidence.rejection_reason = reason
        validate_evidence_set(case, root=self.root)
        finding = create_finding(
            case,
            code="evidence_rejected",
            severity=max(
                (
                    case.obligation(obligation_id).severity
                    for obligation_id in evidence.obligation_ids
                ),
                default="high",
                key=lambda value: RISK_RANK[value],
            ),
            message=reason,
            blocking=True,
            related_object_ids=[evidence.id],
            affected_obligation_ids=evidence.obligation_ids,
        )
        repair = create_repair_request(
            case,
            finding_ids=[finding.id],
            responsible_role="contributor",
            requested_correction=reason,
            requested_by=actor,
        )
        self._transition(
            case,
            action="reject_evidence",
            actor=actor,
            role=role,
            reason=reason,
            related_object_ids=[evidence.id, finding.id, repair.id],
        )
        self.storage.save_case(case)
        return repair

    def ask_clarification(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        question: str,
        affected_obligation_ids: list[str],
    ):
        authorize(self.config, role=role, action="ask_clarification")
        case = self.storage.load_case(case_id)
        finding = create_finding(
            case,
            code="clarification_requested",
            severity="medium",
            message=question,
            blocking=True,
            affected_obligation_ids=affected_obligation_ids,
        )
        repair = create_repair_request(
            case,
            finding_ids=[finding.id],
            responsible_role="contributor",
            requested_correction=question,
            requested_by=actor,
        )
        self._transition(
            case,
            action="ask_clarification",
            actor=actor,
            role=role,
            reason=question,
            related_object_ids=[finding.id, repair.id],
        )
        self.storage.save_case(case)
        return repair

    def record_policy_conflict(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        message: str,
        affected_obligation_ids: list[str],
    ):
        authorize(self.config, role=role, action="record_policy_conflict")
        case = self.storage.load_case(case_id)
        finding = create_finding(
            case,
            code="policy_conflict",
            severity="critical",
            message=message,
            blocking=True,
            affected_obligation_ids=affected_obligation_ids,
        )
        repair = create_repair_request(
            case,
            finding_ids=[finding.id],
            responsible_role="policy_steward",
            requested_correction=message,
            requested_by=actor,
        )
        self._transition(
            case,
            action="record_policy_conflict",
            actor=actor,
            role=role,
            reason=message,
            related_object_ids=[finding.id, repair.id],
        )
        self.storage.save_case(case)
        return finding

    def resolve_policy_conflict(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        finding_id: str,
        resolution: str,
    ):
        authorize(self.config, role=role, action="resolve_policy_conflict")
        case = self.storage.load_case(case_id)
        candidate = next(
            (item for item in case.findings if item.id == finding_id),
            None,
        )
        if candidate is None:
            raise VNextError(f"Unknown finding: {finding_id}")
        if candidate.code != "policy_conflict" or candidate.status != "open":
            raise VNextError(
                "Policy conflict resolution requires an open policy_conflict finding in this case"
            )
        finding = resolve_finding(
            case, finding_id=finding_id, resolution=resolution
        )
        self._transition(
            case,
            action="resolve_policy_conflict",
            actor=actor,
            role=role,
            reason=resolution,
            related_object_ids=[finding.id],
        )
        self.storage.save_case(case)
        return finding

    def request_repair(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        message: str,
        affected_obligation_ids: list[str],
        responsible_role: str = "contributor",
        finding_code: str = "repair_required",
    ):
        authorize(self.config, role=role, action="request_repair")
        case = self.storage.load_case(case_id)
        finding = create_finding(
            case,
            code=finding_code,
            severity="high",
            message=message,
            blocking=True,
            affected_obligation_ids=affected_obligation_ids,
        )
        repair = create_repair_request(
            case,
            finding_ids=[finding.id],
            responsible_role=responsible_role,
            requested_correction=message,
            requested_by=actor,
            affected_obligation_ids=affected_obligation_ids,
            revalidation_required=affected_obligation_ids,
        )
        self._transition(
            case,
            action="request_repair",
            actor=actor,
            role=role,
            reason=message,
            related_object_ids=[finding.id, repair.id],
        )
        self.storage.save_case(case)
        return repair

    def resubmit(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        summary: str,
        affected_obligation_ids: list[str],
        evidence_ids: list[str] | None = None,
        diff_material: str | None = None,
        change_classification: str = "material",
        change_reason: str | None = None,
    ) -> GovernanceCase:
        authorize(self.config, role=role, action="resubmit")
        case = self.storage.load_case(case_id)
        if change_classification not in {
            "unrelated",
            "non_material",
            "material",
        }:
            raise VNextError(
                "change_classification must be unrelated, non_material, or material"
            )
        affected_ids = list(dict.fromkeys(affected_obligation_ids))
        if not affected_ids:
            raise VNextError(
                "Resubmission must identify an open repair scope"
            )
        for obligation_id in affected_ids:
            case.obligation(obligation_id)
        open_repair_scope = {
            obligation_id
            for item in case.repair_requests
            if item.status == "open"
            for obligation_id in item.affected_obligation_ids
        }
        outside_repair = sorted(set(affected_ids) - open_repair_scope)
        if outside_repair:
            raise VNextError(
                "Resubmission references obligations outside the open repair scope: "
                + ", ".join(outside_repair)
            )
        if evidence_ids:
            known_evidence = {item.id: item for item in case.evidence}
            unknown_evidence = sorted(set(evidence_ids) - set(known_evidence))
            if unknown_evidence:
                raise VNextError(
                    "Resubmission references evidence outside this case: "
                    + ", ".join(unknown_evidence)
                )
            wrong_scope = sorted(
                evidence_id
                for evidence_id in evidence_ids
                if not (
                    set(known_evidence[evidence_id].obligation_ids)
                    & set(affected_ids)
                )
            )
            if wrong_scope:
                raise VNextError(
                    "Resubmission evidence is outside the selected repair scope: "
                    + ", ".join(wrong_scope)
                )
        affected_scope = sorted(
            {
                path
                for obligation_id in affected_ids
                for path in case.obligation(obligation_id).affected_scope
            }
        )
        previous_contribution = case.contribution_fingerprint
        previous_evidence = evidence_set_fingerprint(case.evidence)
        case.contribution_fingerprint = contribution_fingerprint(
            self.root,
            case.changed_files,
            base_commit=case.base_commit,
            change_tags=case.change_tags,
            semantic_targets=case.semantic_targets,
            diff_material=diff_material,
        )
        contribution_changed = (
            previous_contribution != case.contribution_fingerprint
        )
        if contribution_changed:
            for item in case.evidence:
                evidence_affected = bool(
                    set(item.obligation_ids) & set(affected_ids)
                )
                retain = (
                    change_classification in {"unrelated", "non_material"}
                    or not evidence_affected
                )
                if retain:
                    item.retained_for_contribution_fingerprint = (
                        case.contribution_fingerprint
                    )
                    item.retention_reason = (
                        change_reason
                        or (
                            "The evidence scope is unaffected by the recorded "
                            f"{change_classification} change."
                        )
                    )
                else:
                    item.retained_for_contribution_fingerprint = None
                    item.retention_reason = None
        validate_evidence_set(
            case,
            root=self.root,
            current_contribution_fingerprint=case.contribution_fingerprint,
        )
        invalidated_attestation_ids = invalidate_stale_attestations(
            case,
            previous_contribution_fingerprint=previous_contribution,
            previous_evidence_set_fingerprint=previous_evidence,
            affected_scope=(
                []
                if change_classification in {"unrelated", "non_material"}
                else affected_scope
            ),
            reason=(
                change_reason
                or "The contribution or repaired evidence changed after attestation."
            ),
        )
        stale_evidence_ids = sorted(
            item.id
            for item in case.evidence
            if item.validity_state in {"stale", "expired"}
        )
        retained_evidence_ids = sorted(
            item.id
            for item in case.evidence
            if not set(item.obligation_ids) & set(affected_ids)
            and item.validity_state in {"valid", "verified"}
            and (
                not contribution_changed
                or item.retained_for_contribution_fingerprint
                == case.contribution_fingerprint
            )
        )
        if not contribution_changed:
            effective_classification = "no_material_change"
        elif change_classification == "material":
            affected_blocking = {
                item.obligation_id
                for item in case.obligations
                if item.blocking
            } & set(affected_ids)
            effective_classification = (
                "full_material_change"
                if affected_blocking
                == {
                    item.obligation_id
                    for item in case.obligations
                    if item.blocking
                }
                else "partial_material_change"
            )
        else:
            effective_classification = change_classification
        change_assessment = {
            "change_classification": effective_classification,
            "change_reason": (
                change_reason
                or (
                    "Contribution fingerprint unchanged."
                    if not contribution_changed
                    else "Recorded by the resubmitting actor."
                )
            ),
            "previous_contribution_fingerprint": previous_contribution,
            "new_contribution_fingerprint": case.contribution_fingerprint,
            "stale_evidence_ids": stale_evidence_ids,
            "retained_evidence_ids": retained_evidence_ids,
            "invalidated_attestation_ids": invalidated_attestation_ids,
            "required_revalidation_scope": affected_ids,
        }
        attempt = record_resubmission(
            case,
            actor=actor,
            summary=summary,
            affected_obligation_ids=affected_ids,
            evidence_ids=evidence_ids,
            change_assessment=change_assessment,
        )
        self._transition(
            case,
            action="resubmit",
            actor=actor,
            role=role,
            reason=summary,
            related_object_ids=[attempt["id"]],
        )
        self.storage.save_case(case)
        return case

    def verify(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        reason: str,
        obligation_ids: list[str] | None = None,
        timestamp: str | None = None,
    ) -> MaintainerVerification:
        authorize(self.config, role=role, action="verify_evidence")
        case = self.storage.load_case(case_id)
        validate_evidence_set(case, root=self.root)
        apply_attestation_status(case)
        requested = set(
            obligation_ids
            or [item.obligation_id for item in case.obligations if item.blocking]
        )
        unknown = requested - {item.obligation_id for item in case.obligations}
        if unknown:
            raise VNextError(
                f"Verification references unknown obligations: {', '.join(sorted(unknown))}"
            )
        unresolved_inputs = [
            item
            for item in case.obligations
            if item.obligation_id in requested
            and item.type in {"evidence", "human_attestation"}
            and item.status not in {"satisfied", "verified", "overridden"}
        ]
        if unresolved_inputs:
            raise VNextError(
                "Cannot verify while required evidence or attestation obligations are unresolved"
            )
        independent = any(
            item.obligation_id == "O-INDEPENDENT-REVIEW"
            and item.obligation_id in requested
            for item in case.obligations
        )
        if independent:
            if role != "maintainer":
                raise VNextError(
                    "Independent review obligation requires the maintainer role"
                )
            source_actors = {item.source_actor for item in case.evidence} | {
                item.actor for item in case.attestations
            }
            if actor in source_actors:
                raise VNextError(
                    "Independent review requires separation from evidence and attestation actors"
                )

        evidence_ids = sorted(
            item.id
            for item in case.evidence
            if set(item.obligation_ids) & requested
            and item.validity_state in {"valid", "verified"}
        )
        verification = MaintainerVerification(
            id=new_id("verification"),
            actor=actor,
            role=role,
            timestamp=timestamp or utc_now(),
            obligation_ids=sorted(requested),
            evidence_ids=evidence_ids,
            outcome="verified",
            reason=reason,
            policy_fingerprint=case.policy_snapshot.policy_fingerprint,
            contribution_fingerprint=case.contribution_fingerprint,
        )
        case.maintainer_verifications.append(verification)
        for evidence in case.evidence:
            if evidence.id in evidence_ids:
                evidence.validity_state = "verified"
        for obligation in case.obligations:
            if obligation.obligation_id in requested:
                if obligation.type == "human_attestation":
                    continue
                obligation.status = "verified"
        for finding in list(case.findings):
            if (
                finding.status == "open"
                and finding.code != "policy_conflict"
                and set(finding.affected_obligation_ids) <= requested
            ):
                resolve_finding(
                    case,
                    finding_id=finding.id,
                    resolution="Correction verified by maintainer-side operation.",
                    timestamp=timestamp,
                )
        self._transition(
            case,
            action="verify_evidence",
            actor=actor,
            role=role,
            reason=reason,
            related_object_ids=[verification.id],
            timestamp=timestamp,
        )
        if (
            not case.unresolved_blocking_obligations()
            and not case.open_blocking_findings()
        ):
            self._transition(
                case,
                action="mark_ready",
                actor="agm-engine",
                role="system",
                reason=(
                    "All blocking obligations are satisfied or verified; the case "
                    "is ready for an authorized human decision, not accepted."
                ),
                related_object_ids=[verification.id],
                timestamp=timestamp,
            )
        self.storage.save_case(case)
        return verification

    def override(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        reason: str,
        obligation_ids: list[str] | None = None,
        finding_ids: list[str] | None = None,
    ) -> GovernanceCase:
        authorize(self.config, role=role, action="authorized_override")
        case = self.storage.load_case(case_id)
        selected_obligations = set(obligation_ids or [])
        selected_findings = set(finding_ids or [])
        if not selected_obligations and not selected_findings:
            raise VNextError("Override must identify obligations or findings")
        known_finding_ids = {item.id for item in case.findings}
        unknown_findings = sorted(selected_findings - known_finding_ids)
        if unknown_findings:
            raise VNextError(
                f"Override references unknown findings: {', '.join(unknown_findings)}"
            )
        open_findings = {
            item.id: item
            for item in case.findings
            if item.status == "open"
        }
        ineligible_findings = sorted(
            selected_findings - set(open_findings)
        )
        if ineligible_findings:
            raise VNextError(
                "Override requires open findings: "
                + ", ".join(ineligible_findings)
            )
        eligible_obligations = {
            item.obligation_id
            for item in case.obligations
            if item.blocking
            and item.status not in {"satisfied", "verified", "overridden"}
        } | {
            obligation_id
            for finding_id in selected_findings
            for obligation_id in open_findings[finding_id].affected_obligation_ids
        }
        ineligible_obligations = sorted(
            selected_obligations - eligible_obligations
        )
        if ineligible_obligations:
            raise VNextError(
                "Override references obligations outside the current exception scope: "
                + ", ".join(ineligible_obligations)
            )
        for obligation_id in selected_obligations:
            case.obligation(obligation_id).status = "overridden"
        for finding in case.findings:
            if finding.id in selected_findings:
                finding.status = "overridden"
                finding.resolution = reason
                finding.resolved_at = utc_now()
        self._transition(
            case,
            action="authorized_override",
            actor=actor,
            role=role,
            reason=reason,
            related_object_ids=sorted(selected_obligations | selected_findings),
        )
        self.storage.save_case(case)
        return case

    def decide(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        decision: str,
        reason: str,
        timestamp: str | None = None,
    ) -> FinalDecision | None:
        action_map = {
            "accept": "decide_accept",
            "reject": "decide_reject",
            "request_changes": "decide_request_changes",
            "close": "decide_close",
        }
        if decision not in action_map:
            raise VNextError(f"Unknown final decision: {decision}")
        action = action_map[decision]
        authorize(self.config, role=role, action=action)
        case = self.storage.load_case(case_id)
        if decision == "request_changes":
            finding = create_finding(
                case,
                code="maintainer_requested_changes",
                severity="high",
                message=reason,
                blocking=True,
                affected_obligation_ids=[
                    item.obligation_id
                    for item in case.obligations
                    if item.blocking
                ],
            )
            repair = create_repair_request(
                case,
                finding_ids=[finding.id],
                responsible_role="contributor",
                requested_correction=reason,
                requested_by=actor,
            )
            self._transition(
                case,
                action=action,
                actor=actor,
                role=role,
                reason=reason,
                related_object_ids=[finding.id, repair.id],
                timestamp=timestamp,
            )
            self.storage.save_case(case)
            return None

        overridden_objects = [
            item.id for item in case.findings if item.status == "overridden"
        ] + [
            item.id for item in case.obligations if item.status == "overridden"
        ]
        final_decision = FinalDecision(
            id=new_id("decision"),
            actor=actor,
            role=role,
            timestamp=timestamp or utc_now(),
            decision=decision,
            reason=reason,
            override=case.state == "overridden",
            unresolved_exception_ids=sorted(overridden_objects),
        )
        case.final_decision = final_decision
        self._transition(
            case,
            action=action,
            actor=actor,
            role=role,
            reason=reason,
            related_object_ids=[final_decision.id],
            timestamp=timestamp,
        )
        case.closure_receipt = self._closure_receipt(case)
        self.storage.save_case(case)
        return final_decision

    def migration_check(self, case_id: str) -> MigrationDiagnostic:
        return check_migration(self.storage.load_case(case_id), self.config)

    def reviewer_guidance(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
    ):
        """Build a read-only reviewer view from the stored canonical case."""
        from .guidance import ActorContext, build_reviewer_guidance

        case = self.storage.load_case(case_id)
        return build_reviewer_guidance(
            case,
            self.config,
            self.storage.read_transitions(case_id),
            ActorContext(actor=actor, role=role),
            migration_diagnostic=check_migration(case, self.config),
        )

    def preview_reviewer_action(
        self,
        case_id: str,
        *,
        actor: str,
        role: str,
        action: str,
        parameters: dict[str, Any] | None = None,
    ):
        """Return a deterministic action plan without saving any mutation."""
        from .guidance import ActorContext, preview_reviewer_action

        case = self.storage.load_case(case_id)
        return preview_reviewer_action(
            case,
            self.config,
            self.storage.read_transitions(case_id),
            ActorContext(actor=actor, role=role),
            action,
            parameters,
        )

    def _transition(self, case: GovernanceCase, **kwargs):
        transition = transition_case(self.config, case, **kwargs)
        self.storage.append_transition(transition)
        return transition

    def _closure_receipt(self, case: GovernanceCase) -> ClosureReceipt:
        if not case.final_decision:
            raise VNextError("Closure receipt requires a final decision")
        return ClosureReceipt(
            id=new_id("closure"),
            case_id=case.id,
            created_at=utc_now(),
            policy_fingerprint=case.policy_snapshot.policy_fingerprint,
            contribution_fingerprint=case.contribution_fingerprint,
            final_state=case.state,
            final_decision_id=case.final_decision.id,
            matched_rule_ids=sorted(item.rule_id for item in case.matched_rules),
            obligation_statuses={
                item.obligation_id: item.status for item in case.obligations
            },
            evidence_ids=sorted(item.id for item in case.evidence),
            attestation_ids=sorted(item.id for item in case.attestations),
            verification_ids=sorted(
                item.id for item in case.maintainer_verifications
            ),
            repair_request_ids=sorted(item.id for item in case.repair_requests),
            unresolved_exception_ids=list(
                case.final_decision.unresolved_exception_ids
            ),
            transition_log_hash=self.storage.transition_log_hash(case.id),
        )
