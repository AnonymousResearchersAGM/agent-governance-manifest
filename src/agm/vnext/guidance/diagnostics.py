"""Derive plain-language diagnostics exclusively from AGM domain records."""

from __future__ import annotations

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

CHECK_ITEM_LABELS = {
    "contribution_summary": "修改说明",
    "changed_files": "变更文件清单",
    "rationale": "修改理由",
    "test_explanation": "测试说明",
    "test_command": "测试结果",
    "artifact": "可核验制品",
    "known_limitations": "已知限制",
    "security_auth_impact": "登录与安全影响说明",
    "policy_impact": "治理策略影响说明",
    "agent_action_scope": "智能体行动与委派范围",
    "human_attestation": "负责人确认",
    "independent_review": "独立维护者检查",
}

CURRENT_STATE_LABELS = {
    "case_opened": "系统正在识别项目要求",
    "policy_resolved": "系统已识别适用规则",
    "obligations_compiled": "系统已整理本次要求",
    "evidence_incomplete": "等待贡献者补齐材料",
    "awaiting_human_attestation": "等待负责人确认",
    "awaiting_maintainer_verification": "等待维护者检查",
    "repair_requested": "发现问题，等待指定范围修改",
    "resubmitted": "已补交，等待重新检查受影响部分",
    "verification_complete": "维护者检查完成，系统正在确认可决策状态",
    "ready_for_human_decision": "等待人类维护者最终决定",
    "overridden": "有权覆盖已记录，等待人类维护者最终决定",
    "accepted": "人类维护者已接受并关闭",
    "rejected": "人类维护者已拒绝并关闭",
    "closed": "案例已关闭",
    "ordinary_unmanaged": "按普通项目流程处理",
}


def derive_readiness(case: GovernanceCase) -> str:
    """Return the canonical report readiness without implying acceptance."""
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


def check_item_label(obligation: CompiledObligation) -> str:
    return CHECK_ITEM_LABELS.get(
        obligation.evidence_type,
        obligation.description.rstrip(".") or obligation.obligation_id,
    )


def _evidence_for(case: GovernanceCase, obligation_id: str):
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


def _comparison_state(
    case: GovernanceCase,
    obligation: CompiledObligation,
    evidence: list[Any],
    attestations: list[HumanAttestation],
    findings: list[GovernanceFinding],
) -> tuple[str, str, str]:
    if obligation.status == "overridden":
        return (
            "overridden",
            "该要求已由具备权限的人类维护者记录覆盖。",
            "overridden by authorized maintainer",
        )
    if obligation.status == "policy_conflict":
        return (
            "blocked",
            "项目规则之间存在冲突，需要有权角色先处理。",
            "blocked by policy conflict",
        )

    blocking_findings = [
        item for item in findings if item.blocking and item.status == "open"
    ]
    warning_findings = [
        item for item in findings if not item.blocking and item.status == "open"
    ]

    if obligation.type == "evidence":
        if not evidence:
            result = (
                "not_started"
                if case.state
                in {"case_opened", "policy_resolved", "obligations_compiled"}
                else "missing"
            )
            observed = (
                "流程尚未进入材料准备"
                if result == "not_started"
                else "尚未提供与本项绑定的材料"
            )
            return result, observed, "no bound evidence record"
        states = {item.validity_state for item in evidence}
        if "stale" in states or "expired" in states:
            stale = [
                item.id
                for item in evidence
                if item.validity_state in {"stale", "expired"}
            ]
            return (
                "needs_update",
                f"已有材料需要更新：{', '.join(stale)}",
                f"stale or expired evidence: {', '.join(stale)}",
            )
        invalid_states = states & {"invalid", "rejected", "conflicting"}
        if invalid_states:
            invalid = [
                item.id
                for item in evidence
                if item.validity_state in invalid_states
            ]
            return (
                "invalid",
                f"已有材料无效：{', '.join(invalid)}",
                f"invalid evidence: {', '.join(invalid)}",
            )
        if blocking_findings:
            return (
                "blocked",
                blocking_findings[0].message,
                f"open blocking finding: {blocking_findings[0].code}",
            )
        if obligation.status == "verified":
            return (
                "verified",
                "材料已由具备权限的维护者完成检查。",
                "verified by maintainer-side record",
            )
        if warning_findings:
            return (
                "needs_attention",
                warning_findings[0].message,
                f"open non-blocking finding: {warning_findings[0].code}",
            )
        if obligation.status == "satisfied":
            return (
                "meets_requirement",
                "已提供与当前贡献和项目策略绑定的材料。",
                "valid bound evidence is present",
            )
        return (
            "blocked" if obligation.blocking else "needs_attention",
            "现有材料尚未使该要求达到可继续状态。",
            f"obligation status is {obligation.status}",
        )

    if obligation.type == "human_attestation":
        invalidated = [item for item in attestations if item.status == "invalidated"]
        confirmed = [item for item in attestations if item.status == "confirmed"]
        if invalidated and not confirmed:
            return (
                "invalid",
                "已有负责人确认已失效，需要由负责人重新确认受影响范围。",
                "human attestation invalidated",
            )
        if obligation.status in {"satisfied", "verified"} and confirmed:
            return (
                "meets_requirement",
                "负责人已确认当前绑定范围。",
                "confirmed accountable-human attestation is bound",
            )
        if blocking_findings:
            return (
                "blocked",
                blocking_findings[0].message,
                f"open blocking finding: {blocking_findings[0].code}",
            )
        if case.state == "awaiting_human_attestation":
            return (
                "missing",
                "材料已准备，正在等待负责人确认。",
                "awaiting accountable-human attestation",
            )
        return (
            "not_started",
            "尚未到负责人确认阶段。",
            "attestation stage not reached",
        )

    if obligation.type == "maintainer_verification":
        verified = [
            item
            for item in case.maintainer_verifications
            if obligation.obligation_id in item.obligation_ids
            and item.outcome == "verified"
        ]
        if obligation.status == "overridden":
            return (
                "overridden",
                "独立检查要求已由有权维护者记录覆盖。",
                "independent review overridden",
            )
        if verified or obligation.status == "verified":
            return (
                "verified",
                "独立维护者检查已经完成。",
                "independent maintainer verification recorded",
            )
        if blocking_findings:
            return (
                "blocked",
                blocking_findings[0].message,
                f"open blocking finding: {blocking_findings[0].code}",
            )
        return (
            "not_started",
            (
                "已轮到维护者检查，当前尚未完成。"
                if case.state
                in {"awaiting_maintainer_verification", "resubmitted"}
                else "尚未到独立维护者检查阶段。"
            ),
            "independent maintainer verification not recorded",
        )

    return (
        "blocked" if obligation.blocking else "needs_attention",
        f"无法解释的要求类型：{obligation.type}",
        f"unknown obligation type: {obligation.type}",
    )


def build_requirement_comparisons(
    case: GovernanceCase,
) -> list[RequirementComparison]:
    rows: list[RequirementComparison] = []
    for obligation in case.obligations:
        evidence = _evidence_for(case, obligation.obligation_id)
        attestations = _attestations_for(case, obligation)
        findings = _findings_for(case, obligation.obligation_id)
        result, observed, observed_english = _comparison_state(
            case, obligation, evidence, attestations, findings
        )
        evidence_ids = [item.id for item in evidence]
        binding_fingerprints = sorted(
            {
                item.contribution_fingerprint
                for item in evidence
            }
            | {
                item.contribution_fingerprint
                for item in attestations
            }
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
                check_item=check_item_label(obligation),
                project_requirement=(
                    f"项目要求：{obligation.description.rstrip('.')}"
                    + ("（阻断项）" if obligation.blocking else "（关注项）")
                ),
                current_situation=observed,
                result=result,
                result_label=RESULT_LABELS[result],
                raw_status=obligation.status,
                blocking=obligation.blocking,
                source_rule_ids=list(obligation.source_rule_ids),
                interaction_ids=list(obligation.interaction_ids),
                evidence_ids=evidence_ids,
                binding_fingerprints=binding_fingerprints,
                finding_ids=[item.id for item in findings],
                reference_english=obligation.description,
                observed_english=observed_english,
                traceability=traces,
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
        result.append(
            DiagnosticFindingView(
                finding_id=finding.id,
                title=(
                    "阻断问题" if finding.blocking else "需要关注的问题"
                ),
                plain_language=finding.message,
                severity=finding.severity,
                blocking=finding.blocking,
                status=finding.status,
                affected_obligation_ids=list(
                    finding.affected_obligation_ids
                ),
                repair_request_ids=[item.id for item in repairs],
                traceability=[
                    TraceReference("finding", finding.id, "diagnostic"),
                    *[
                        TraceReference("repair_request", item.id, "repair")
                        for item in repairs
                    ],
                ],
            )
        )
    return result
