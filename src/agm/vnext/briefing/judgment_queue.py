"""Compile only irreducibly human review work into a stable queue."""

from __future__ import annotations

from typing import Any

from ..guidance.models import RequirementComparison
from ..models import CompiledObligation, GovernanceCase
from .change_summary import latest_evidence_value
from .models import (
    ContributorAccountabilityBrief,
    HumanJudgmentItem,
    RequirementBrief,
    RequirementItem,
)


FOCUS_BY_TYPE = {
    "security_auth_impact": (
        "是否改变用户身份失效或令牌刷新逻辑",
        "是否扩大令牌有效范围或身份权限边界",
        "是否影响权限撤销、会话终止或异常路径",
    ),
    "policy_impact": (
        "治理规则与执行逻辑是否仍然一致",
        "是否需要兼容或迁移既有治理案例",
        "自修改是否可能削弱职责分离或权威边界",
    ),
    "agent_action_scope": (
        "声明范围是否覆盖实际变更和命令记录",
        "是否存在未披露的子智能体行动或继续委派",
        "负责人审阅范围是否覆盖当前版本和智能体行动说明",
    ),
    "rationale": (
        "修改理由是否与实际范围一致",
        "理由是否遗漏关键风险或兼容性影响",
    ),
    "known_limitations": (
        "限制说明是否覆盖当前风险范围",
        "是否存在会影响合并决定但未披露的限制",
    ),
    "independent_review": (
        "贡献侧与检查者是否保持职责分离",
        "高风险联动影响是否得到独立检查",
        "检查结论是否只代表 verification，而非最终接受",
    ),
    "contribution_summary": (
        "修改说明是否覆盖实际变更文件",
        "说明是否遗漏与风险相关的行为变化",
    ),
}

OBSERVATION_BY_TYPE = {
    "security_auth_impact": "系统记录的变更范围涉及登录、认证或权限相关路径。",
    "policy_impact": "系统记录到治理规则、入口或治理执行逻辑发生变化。",
    "agent_action_scope": "治理案例记录为智能体参与路径，并存在相应行动范围材料。",
    "rationale": "系统只能确认修改理由已提供，不能证明理由与代码语义一致。",
    "known_limitations": "系统只能确认限制说明已提供，不能证明其完整性。",
    "independent_review": "现有治理结论要求职责分离的独立维护者检查。",
    "contribution_summary": "系统记录了修改说明和实际变更文件，但不能判断说明是否完整。",
}

OUTCOMES = (
    "说明与修改一致，可以记录本项检查完成",
    "需要贡献侧补充或更正说明",
    "发现不可接受风险，交由有权人类维护者处理",
)


def _claim(case: GovernanceCase, evidence_type: str) -> str:
    value, _ = latest_evidence_value(case, evidence_type)
    if value is None:
        return "没有可引用的贡献者说明。"
    if isinstance(value, list):
        return "、".join(map(str, value))
    if isinstance(value, dict):
        return "；".join(f"{key}：{item}" for key, item in value.items())
    return str(value)


def _evidence_summary(
    case: GovernanceCase,
    obligation: CompiledObligation,
) -> str:
    records = [
        item
        for item in case.evidence
        if obligation.obligation_id in item.obligation_ids
        and item.validity_state in {"valid", "verified"}
    ]
    if obligation.type == "maintainer_verification":
        return "前置材料已达到进入独立检查的结构条件。"
    if not records:
        return "没有可用于本项判断的有效材料。"
    retained = sum(
        1
        for item in records
        if item.retained_for_contribution_fingerprint
        == case.contribution_fingerprint
    )
    message = f"系统记录有 {len(records)} 份形式有效且对应当前版本的材料。"
    if retained:
        message += f"其中 {retained} 份按未受影响范围保留。"
    return message


def _judgment(
    case: GovernanceCase,
    obligation: CompiledObligation,
    requirement: RequirementItem,
    *,
    reason: str | None = None,
    provenance: tuple[str, ...],
) -> HumanJudgmentItem:
    evidence_type = obligation.evidence_type
    priority = (
        "critical"
        if obligation.severity == "critical"
        else ("high" if obligation.blocking else "normal")
    )
    return HumanJudgmentItem(
        judgment_id=f"judgment-{requirement.requirement_key}",
        display_title=requirement.display_title,
        why_human_is_needed=reason or (
            "系统能确认材料结构、范围和版本绑定，但不能自动判断声明"
            "是否准确描述代码行为和风险。"
        ),
        contribution_claim=_claim(case, evidence_type),
        system_observation=OBSERVATION_BY_TYPE.get(
            evidence_type,
            "系统只能确认治理记录存在，不能完成所需的语义判断。",
        ),
        evidence_summary=_evidence_summary(case, obligation),
        review_focus=FOCUS_BY_TYPE.get(
            evidence_type,
            (
                "材料内容是否与实际修改一致",
                "是否存在未披露的风险或范围缺口",
            ),
        ),
        possible_outcomes=OUTCOMES,
        priority=priority,
        blocking=obligation.blocking,
        trace_refs=(
            f"trace:judgment:{requirement.requirement_key}",
        ),
        requirement_refs=(requirement.requirement_key,),
        provenance=provenance,
    )


def compile_human_judgment_queue(
    case: GovernanceCase,
    comparisons: list[RequirementComparison],
    requirements: RequirementBrief,
    accountability: ContributorAccountabilityBrief,
    contribution: Any,
) -> tuple[HumanJudgmentItem, ...]:
    """Exclude contributor repairs, stale material, and already verified work."""

    del accountability, contribution  # Provenance remains available in the brief.
    if case.state in {
        "verification_complete",
        "ready_for_human_decision",
        "overridden",
        "accepted",
        "rejected",
        "closed",
    }:
        return ()
    if (
        requirements.missing
        or requirements.stale
        or requirements.invalid
        or requirements.awaiting_accountable_human
    ):
        return ()

    open_revalidation_scope = {
        obligation_id
        for repair in case.repair_requests
        if repair.status == "resubmitted"
        for obligation_id in repair.revalidation_required
        if any(
            finding.id in repair.finding_ids
            and finding.status == "open"
            for finding in case.findings
        )
    }
    if (
        not open_revalidation_scope
        and case.state
        not in {"awaiting_maintainer_verification", "resubmitted"}
    ):
        return ()

    candidates: list[
        tuple[
            CompiledObligation,
            RequirementComparison,
            RequirementItem,
        ]
    ] = []
    for obligation, comparison, requirement in zip(
        case.obligations,
        comparisons,
        requirements.items,
        strict=True,
    ):
        if open_revalidation_scope:
            if obligation.obligation_id not in open_revalidation_scope:
                continue
        elif requirement.status not in {
            "provided_requires_human_judgment",
            "awaiting_independent_review",
        }:
            continue
        if requirement.status in {
            "provided_requires_human_judgment",
            "awaiting_independent_review",
        }:
            candidates.append((obligation, comparison, requirement))

    if candidates:
        judgments = []
        for obligation, comparison, requirement in candidates:
            provenance = ["compiled_requirement"]
            if obligation.obligation_id in open_revalidation_scope:
                provenance.append("scoped_revalidation")
            if obligation.type == "maintainer_verification":
                provenance.append("independent_review_requirement")
            if comparison.finding_ids:
                provenance.append("existing_finding")
            if case.state == "awaiting_maintainer_verification":
                provenance.append("maintainer_review_stage")
            judgments.append(
                _judgment(
                    case,
                    obligation,
                    requirement,
                    provenance=tuple(provenance),
                )
            )
        return tuple(judgments)

    # A denied operation is an audit fact, not provenance for new human work.
    return ()
