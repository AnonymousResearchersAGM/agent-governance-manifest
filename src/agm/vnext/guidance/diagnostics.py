"""Derive participant-facing diagnostics from AGM domain records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..models import (
    CompiledObligation,
    GovernanceCase,
    GovernanceFinding,
    HumanAttestation,
)
from .models import (
    DiagnosticFindingView,
    RequirementComparison,
    TraceReference,
)
from .reason_presentations import present_reason
from .term_presentations import (
    CURRENT_STATE_LABELS,
    OBLIGATION_PRESENTATIONS,
)


RESULT_LABELS = {
    "meets_requirement": "符合要求",
    "needs_attention": "需要关注",
    "not_started": "尚未进行",
    "missing": "缺少",
    "needs_update": "需要更新",
    "invalid": "无效",
    "blocked": "阻止继续",
    "not_applicable": "本次不要求",
    "verified": "维护者已检查",
    "overridden": "已由有权维护者覆盖",
    "closed": "已完成并关闭",
}

MATERIAL_STATUS_LABELS = {
    "missing": "缺少",
    "invalid": "无效",
    "stale": "需要更新",
    "provided": "已提供",
    "retained": "仍然有效",
    "verified": "已检查",
    "overridden": "已由有权维护者覆盖",
    "not_applicable": "本次不要求",
}

WORKFLOW_STATUS_LABELS = {
    "blocks_progression": "阻止继续",
    "awaiting_contributor": "等待贡献者处理",
    "awaiting_attestation": "等待负责人确认",
    "awaiting_revalidation": "等待维护者重新检查",
    "awaiting_final_decision": "等待人类维护者最终决定",
    "completed": "已完成",
}

CHECK_ITEM_LABELS = {
    "contribution_summary": "修改说明",
    "changed_files": "变更文件清单",
    "rationale": "修改理由",
    "test_explanation": "测试说明",
    "test_command": "测试命令与结果",
    "artifact": "可核验制品",
    "known_limitations": "已知限制",
    "security_auth_impact": "登录与安全影响说明",
    "policy_impact": "项目规则影响说明",
    "agent_action_scope": "智能体行动与委派说明",
    "human_attestation": "负责人确认",
    "independent_review": "独立维护者检查",
}

# Canonical English remains in CompiledObligation.description. These
# presentation descriptions never rewrite the .agm policy.
OBLIGATION_DESCRIPTIONS = {
    "O-SUMMARY": "简要说明这次修改做了什么。",
    "O-CHANGED-FILES": "列出这次修改涉及的文件和范围。",
    "O-RATIONALE": "说明为什么需要这次修改。",
    "O-TEST-EXPLANATION": "说明测试覆盖了什么，以及它如何支持本次修改。",
    "O-TEST-COMMAND": "提供测试命令、运行环境和实际结果。",
    "O-ARTIFACT": "提供可以实际检查的测试输出或文件。",
    "O-LIMITATIONS": "说明已知限制；没有已知限制也要明确说明。",
    "O-AUTH-IMPACT": "说明本次修改是否改变登录、认证或权限行为。",
    "O-POLICY-IMPACT": "说明本次修改是否影响项目规则或治理流程。",
    "O-AGENT-SCOPE": (
        "说明智能体做了什么、用了哪些权限、是否有人监督，以及是否把具有"
        "独立行动能力的工作继续交给了另一个智能体。"
    ),
    "O-HUMAN-ATTEST": "由负责人确认自己审阅了当前代码版本、材料和明确范围。",
    "O-INDEPENDENT-REVIEW": "由另一名具备权限且与贡献侧分离的维护者独立检查。",
}

OBLIGATION_PRESENTATION = {
    canonical: (
        term.display_plain,
        OBLIGATION_DESCRIPTIONS[canonical],
    )
    for canonical, term in OBLIGATION_PRESENTATIONS.items()
}


@dataclass(frozen=True)
class _ComparisonState:
    result: str
    observed_plain: str
    observed_raw: str
    material_status: str
    workflow_status: str
    blocks_progression: bool


def derive_readiness(case: GovernanceCase) -> str:
    """Return readiness without ever converting readiness into acceptance."""
    if case.state in {"accepted", "rejected", "closed"}:
        return f"closed:{case.state}"
    if case.state == "ordinary_unmanaged":
        return "no_agm_package_submitted"
    if case.open_blocking_findings():
        return "repair_required"
    if case.unresolved_blocking_obligations():
        return "not_ready"
    if case.state == "ready_for_human_decision":
        return "eligible_for_human_decision"
    if case.state == "overridden":
        return "authorized_override_pending_final_decision"
    return "verification_in_progress"


def obligation_presentation(
    obligation: CompiledObligation,
) -> tuple[str, str]:
    """Return stable Chinese display text with a safe non-empty fallback."""
    configured = OBLIGATION_PRESENTATION.get(obligation.obligation_id)
    if configured:
        return configured
    name = CHECK_ITEM_LABELS.get(
        obligation.evidence_type,
        "某项项目要求",
    )
    plain = (
        f"请按照项目记录完成“{name}”，英文原文和完整依据见技术详情。"
    )
    return name, plain


def check_item_label(obligation: CompiledObligation) -> str:
    return obligation_presentation(obligation)[0]


def _evidence_for(case: GovernanceCase, obligation_id: str) -> list[Any]:
    return [
        item for item in case.evidence if obligation_id in item.obligation_ids
    ]


def _attestations_for(
    case: GovernanceCase, obligation: CompiledObligation
) -> list[HumanAttestation]:
    return list(case.attestations) if obligation.type == "human_attestation" else []


def _findings_for(
    case: GovernanceCase, obligation_id: str
) -> list[GovernanceFinding]:
    return [
        item
        for item in case.findings
        if obligation_id in item.affected_obligation_ids
        and item.status in {"open", "overridden"}
    ]


def _open_revalidation(case: GovernanceCase, obligation_id: str) -> bool:
    return any(
        item.status == "resubmitted"
        and obligation_id in item.revalidation_required
        and any(
            finding.id in item.finding_ids
            and finding.status == "open"
            for finding in case.findings
        )
        for item in case.repair_requests
    )


def _terminal_workflow(case: GovernanceCase) -> str:
    if case.state in {"accepted", "rejected", "closed"}:
        return "completed"
    return "awaiting_final_decision"


def _comparison_state(
    case: GovernanceCase,
    obligation: CompiledObligation,
    evidence: list[Any],
    attestations: list[HumanAttestation],
    findings: list[GovernanceFinding],
) -> _ComparisonState:
    if obligation.status == "overridden":
        return _ComparisonState(
            "overridden",
            "该要求已有具备权限的人类维护者记录覆盖；覆盖不等于接受贡献。",
            "overridden by authorized maintainer",
            "overridden",
            _terminal_workflow(case),
            False,
        )
    if obligation.status == "policy_conflict":
        return _ComparisonState(
            "blocked",
            "项目规则之间存在未解决的冲突，需要有权角色先处理。",
            "blocked by policy conflict",
            "invalid",
            "blocks_progression",
            True,
        )

    blocking_findings = [
        item for item in findings if item.blocking and item.status == "open"
    ]
    warning_findings = [
        item for item in findings if not item.blocking and item.status == "open"
    ]
    awaiting_revalidation = _open_revalidation(
        case, obligation.obligation_id
    )

    if obligation.type == "evidence":
        if not evidence:
            initial = case.state in {
                "case_opened",
                "policy_resolved",
                "obligations_compiled",
            }
            return _ComparisonState(
                "not_started" if initial else "missing",
                "流程尚未进入材料准备。" if initial else "尚未提供。",
                "no bound evidence record",
                "missing",
                "awaiting_contributor",
                bool(obligation.blocking and not initial),
            )
        states = {item.validity_state for item in evidence}
        if states & {"stale", "expired"}:
            return _ComparisonState(
                "needs_update",
                "现有材料对应旧版本或已过有效期，需要更新后再继续。",
                "stale or expired evidence: "
                + ", ".join(
                    item.id
                    for item in evidence
                    if item.validity_state in {"stale", "expired"}
                ),
                "stale",
                "awaiting_contributor",
                obligation.blocking,
            )
        if states & {"invalid", "rejected", "conflicting"}:
            return _ComparisonState(
                "invalid",
                "现有材料不能支持当前修改，需要更正或替换。",
                "invalid evidence: "
                + ", ".join(
                    item.id
                    for item in evidence
                    if item.validity_state
                    in {"invalid", "rejected", "conflicting"}
                ),
                "invalid",
                "awaiting_contributor",
                obligation.blocking,
            )

        retained = any(
            item.retained_for_contribution_fingerprint
            == case.contribution_fingerprint
            for item in evidence
        )
        verified = (
            obligation.status == "verified"
            or any(item.validity_state == "verified" for item in evidence)
        )
        material = "retained" if retained else (
            "verified" if verified else "provided"
        )
        if awaiting_revalidation or (
            blocking_findings and case.state == "resubmitted"
        ):
            return _ComparisonState(
                "blocked" if obligation.blocking else "needs_attention",
                (
                    "材料已补充或仍然有效；当前等待维护者重新检查这一项。"
                ),
                "valid material present; open repair awaits revalidation",
                material,
                "awaiting_revalidation",
                obligation.blocking,
            )
        if blocking_findings:
            return _ComparisonState(
                "blocked",
                "维护者已记录一个需要贡献侧处理的问题。",
                f"open blocking finding: {blocking_findings[0].code}",
                material,
                "awaiting_contributor",
                True,
            )
        if verified:
            return _ComparisonState(
                "verified",
                "材料已由具备权限的维护者完成检查。",
                "verified by maintainer-side record",
                material,
                "completed",
                False,
            )
        if warning_findings:
            return _ComparisonState(
                "needs_attention",
                "材料已提供，但维护者记录了一个非阻断关注项。",
                f"open non-blocking finding: {warning_findings[0].code}",
                material,
                "completed",
                False,
            )
        if obligation.status == "satisfied":
            return _ComparisonState(
                "meets_requirement",
                "已提供与当前贡献和项目规则绑定的材料。",
                "valid bound evidence is present",
                material,
                "completed",
                False,
            )
        return _ComparisonState(
            "blocked" if obligation.blocking else "needs_attention",
            "材料记录存在，但尚未达到本项要求。",
            f"obligation status is {obligation.status}",
            material,
            "blocks_progression" if obligation.blocking else "completed",
            obligation.blocking,
        )

    if obligation.type == "human_attestation":
        confirmed = [item for item in attestations if item.status == "confirmed"]
        invalidated = [
            item for item in attestations if item.status == "invalidated"
        ]
        if invalidated and not confirmed:
            return _ComparisonState(
                "invalid",
                "旧的负责人确认已经失效，需要负责人确认当前版本和范围。",
                "human attestation invalidated",
                "invalid",
                "awaiting_attestation",
                obligation.blocking,
            )
        if confirmed and obligation.status in {"satisfied", "verified"}:
            retained = any(
                item.retained_for_contribution_fingerprint
                == case.contribution_fingerprint
                for item in confirmed
            )
            return _ComparisonState(
                "meets_requirement",
                "负责人已确认当前版本、材料和明确范围。",
                "confirmed accountable-human attestation is bound",
                "retained" if retained else "provided",
                "completed" if not awaiting_revalidation else "awaiting_revalidation",
                False,
            )
        if case.state == "awaiting_human_attestation" or blocking_findings:
            return _ComparisonState(
                "missing",
                "材料已准备，正在等待负责人确认当前版本和范围。",
                "awaiting accountable-human attestation",
                "missing",
                "awaiting_attestation",
                obligation.blocking,
            )
        return _ComparisonState(
            "not_started",
            "尚未到负责人确认阶段。",
            "attestation stage not reached",
            "missing",
            "awaiting_attestation",
            False,
        )

    if obligation.type == "maintainer_verification":
        verified_records = [
            item
            for item in case.maintainer_verifications
            if obligation.obligation_id in item.obligation_ids
            and item.outcome == "verified"
        ]
        if verified_records or obligation.status == "verified":
            return _ComparisonState(
                "verified",
                "独立维护者检查已经完成；这不等于最终接受。",
                "independent maintainer verification recorded",
                "verified",
                "completed",
                False,
            )
        if case.state in {"awaiting_maintainer_verification", "resubmitted"}:
            return _ComparisonState(
                "not_started",
                "前序材料满足后，由具备权限且与贡献侧分离的维护者检查。",
                "independent maintainer verification not recorded",
                "missing",
                "awaiting_revalidation"
                if case.state == "resubmitted"
                else "blocks_progression",
                obligation.blocking,
            )
        return _ComparisonState(
            "not_started",
            "尚未到独立维护者检查阶段。",
            "independent maintainer verification not recorded",
            "missing",
            "blocks_progression" if obligation.blocking else "completed",
            False,
        )

    return _ComparisonState(
        "blocked" if obligation.blocking else "needs_attention",
        "当前界面无法解释这种要求类型，请在技术详情中核对原始记录。",
        f"unknown obligation type: {obligation.type}",
        "invalid",
        "blocks_progression",
        obligation.blocking,
    )


def build_requirement_comparisons(
    case: GovernanceCase,
) -> list[RequirementComparison]:
    rows: list[RequirementComparison] = []
    for obligation in case.obligations:
        evidence = _evidence_for(case, obligation.obligation_id)
        attestations = _attestations_for(case, obligation)
        findings = _findings_for(case, obligation.obligation_id)
        state = _comparison_state(
            case, obligation, evidence, attestations, findings
        )
        display_name, reference_plain = obligation_presentation(obligation)
        evidence_ids = [item.id for item in evidence]
        binding_fingerprints = sorted(
            {item.contribution_fingerprint for item in evidence}
            | {item.contribution_fingerprint for item in attestations}
        )
        traces = [
            TraceReference("compiled_obligation", obligation.id, "reference")
        ]
        traces.extend(
            TraceReference("risk_or_profile_rule", item, "source")
            for item in obligation.source_rule_ids
        )
        traces.extend(
            TraceReference("interaction_rule", item, "source")
            for item in obligation.interaction_ids
        )
        traces.extend(
            TraceReference("evidence", item.id, "observed")
            for item in evidence
        )
        traces.extend(
            TraceReference("human_attestation", item.id, "observed")
            for item in attestations
        )
        traces.extend(
            TraceReference("finding", item.id, "diagnostic")
            for item in findings
        )
        rows.append(
            RequirementComparison(
                obligation_id=obligation.obligation_id,
                check_item=display_name,
                project_requirement=reference_plain,
                current_situation=state.observed_plain,
                result=state.result,
                result_label=RESULT_LABELS[state.result],
                raw_status=obligation.status,
                blocking_requirement=obligation.blocking,
                source_rule_ids=list(obligation.source_rule_ids),
                interaction_ids=list(obligation.interaction_ids),
                evidence_ids=evidence_ids,
                binding_fingerprints=binding_fingerprints,
                finding_ids=[item.id for item in findings],
                reference_english=obligation.description,
                observed_english=state.observed_raw,
                traceability=traces,
                display_name=display_name,
                reference_plain=reference_plain,
                observed_plain=state.observed_plain,
                observed_raw=state.observed_raw,
                material_status=state.material_status,
                material_status_label=MATERIAL_STATUS_LABELS[
                    state.material_status
                ],
                workflow_status=state.workflow_status,
                workflow_status_label=WORKFLOW_STATUS_LABELS[
                    state.workflow_status
                ],
                currently_blocks_progression=state.blocks_progression,
                affected_scope=list(obligation.affected_scope),
            )
        )
    return rows


def build_finding_views(case: GovernanceCase) -> list[DiagnosticFindingView]:
    result: list[DiagnosticFindingView] = []
    for finding in case.findings:
        repairs = [
            item
            for item in case.repair_requests
            if finding.id in item.finding_ids
        ]
        traces = [
            TraceReference("finding", finding.id, "diagnostic"),
            *[
                TraceReference("repair_request", item.id, "repair")
                for item in repairs
            ],
        ]
        reason = present_reason(
            reason_code=finding.code,
            source_english=finding.message,
            trace_refs=traces,
        )
        result.append(
            DiagnosticFindingView(
                finding_id=finding.id,
                title="阻断问题" if finding.blocking else "需要关注的问题",
                plain_language=reason.display_plain,
                reason_presentation=reason,
                severity=finding.severity,
                blocking=finding.blocking,
                status=finding.status,
                affected_obligation_ids=list(
                    finding.affected_obligation_ids
                ),
                repair_request_ids=[item.id for item in repairs],
                traceability=traces,
            )
        )
    return result
