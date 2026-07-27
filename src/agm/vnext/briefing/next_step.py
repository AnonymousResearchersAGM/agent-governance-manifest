"""Compile governance responsibility into a single business-level next step."""

from __future__ import annotations

from typing import Any

from ..models import GovernanceCase
from .models import (
    BriefSemanticState,
    HumanJudgmentItem,
    NextStepBrief,
    RequirementBrief,
    WorkOwner,
)


def _titles(items: tuple[Any, ...]) -> tuple[str, ...]:
    return tuple(item.display_title for item in items)


def compile_next_step(
    case: GovernanceCase,
    requirements: RequirementBrief,
    judgments: tuple[HumanJudgmentItem, ...],
    migration_diagnostic: Any = None,
) -> NextStepBrief:
    """Return one routed next step; never offer a generic action menu."""

    if case.state in {"accepted", "rejected", "closed"}:
        decision = (
            case.final_decision.decision
            if case.final_decision
            else case.state
        )
        accepted = decision == "accept"
        return NextStepBrief(
            status="completed",
            display_title="本次治理案例已经关闭",
            plain_explanation=(
                (
                    "具有最终决定权的人类维护者已经接受本次贡献；"
                    "最终决定和治理记录已经归档。"
                )
                if accepted
                else "最终决定和治理记录已经归档。"
            ),
            responsible_party="无待处理责任方",
            system_will_do=("保留最终决定、关闭记录和完整审计轨迹。",),
            human_should_do=("无需额外 AGM 审查操作。",),
            final_acceptance_state=(
                "accepted"
                if accepted
                else (
                    "rejected"
                    if decision == "reject"
                    else "closed_without_acceptance"
                )
            ),
            owner=WorkOwner.SYSTEM,
            semantic_state=(
                BriefSemanticState.ACCEPTED.value
                if accepted
                else BriefSemanticState.HUMAN_VERIFIED.value
            ),
        )

    policy_changed = bool(
        migration_diagnostic
        and getattr(migration_diagnostic, "policy_changed", False)
    )
    unchanged = (
        len(getattr(migration_diagnostic, "still_valid_obligations", ()))
        if policy_changed
        else 0
    )
    revalidation = (
        len(
            getattr(
                migration_diagnostic,
                "evidence_requiring_revalidation",
                (),
            )
        )
        if policy_changed
        else 0
    )

    contributor_items = (
        requirements.missing + requirements.stale + requirements.invalid
    )
    if contributor_items:
        stale = bool(requirements.stale)
        return NextStepBrief(
            status="awaiting_contributor",
            display_title=(
                "项目规则已变化，当前无需你操作"
                if policy_changed
                else "当前无需你操作"
            ),
            plain_explanation=(
                (
                    f"规则比较显示 {unchanged} 项既有要求没有改变，"
                    f"{revalidation} 份现有材料需要重新核对；"
                    f"贡献侧仍需补充或更新 {len(contributor_items)} 项材料。"
                    "系统不会把全部材料笼统判为失效，也不会静默迁移案例。"
                )
                if policy_changed
                else (
                    f"贡献侧仍需补充或更新 {len(contributor_items)} 项材料；"
                    "材料准备完成后，AGM 才会进入维护者检查阶段。"
                )
                if not stale
                else (
                    "只有"
                    + "、".join(_titles(contributor_items))
                    + "需要按当前版本更新；"
                    "未受影响的有效材料继续保留，当前无需维护者检查。"
                )
            ),
            responsible_party="贡献者或贡献侧智能体",
            system_will_do=(
                "已把需要补充或更新的内容整理为贡献侧待办。",
                "材料更新后重新核对版本绑定、有效期和结构要求。",
                "保留未受影响且仍有效的材料。",
            ),
            human_should_do=(
                "维护者当前无需选择拒绝、退回或修复操作。",
                "等待贡献侧补齐：" + "、".join(_titles(contributor_items)),
            ),
            final_acceptance_state="not_decided",
            owner=WorkOwner.CONTRIBUTION_SIDE,
            semantic_state=BriefSemanticState.SYSTEM_CHECKED.value,
        )

    if requirements.awaiting_accountable_human:
        return NextStepBrief(
            status="awaiting_accountable_human",
            display_title="当前无需你操作",
            plain_explanation=(
                "负责人需要确认已审阅当前版本、智能体行动说明准确，"
                "并愿意对明确范围负责。"
            ),
            responsible_party="人类负责人",
            system_will_do=("确认后核对其版本、材料集合和审阅范围绑定。",),
            human_should_do=("维护者当前无需操作。",),
            final_acceptance_state="not_decided",
            owner=WorkOwner.ACCOUNTABLE_HUMAN,
            semantic_state=BriefSemanticState.SYSTEM_CHECKED.value,
        )

    if policy_changed:
        return NextStepBrief(
            status="policy_migration_attention",
            display_title="项目治理规则已经发生变化",
            plain_explanation=(
                f"规则比较显示 {unchanged} 项既有要求没有改变，"
                f"{revalidation} 份现有材料需要重新核对；"
                "系统不会把全部材料笼统判为失效，也不会静默迁移案例。"
            ),
            responsible_party="项目规则负责人或获授权的人类维护者",
            system_will_do=(
                "保留案例原始规则快照和当前规则比较结果。",
                "明确列出可保留范围和需要重新评估的范围。",
            ),
            human_should_do=(
                "先按项目权限决定是否以及如何迁移；本页面不会执行迁移。",
            ),
            final_acceptance_state="not_decided",
            owner=WorkOwner.MAINTAINER,
            semantic_state=BriefSemanticState.HUMAN_REVIEW_REQUIRED.value,
        )

    if judgments:
        return NextStepBrief(
            status="maintainer_judgment",
            display_title=f"现在需要你检查 {len(judgments)} 项",
            plain_explanation=(
                "形式化检查已经完成到当前阶段；下面只列出系统不能替代"
                "人类作出的判断。"
            ),
            responsible_party="维护者侧检查人员",
            system_will_do=(
                "继续保留已完成形式与绑定核对的材料和未受影响范围。",
                "检查完成后把案例路由到最终人类决定阶段。",
            ),
            human_should_do=tuple(
                f"检查：{item.display_title}" for item in judgments
            ),
            final_acceptance_state="not_decided",
            owner=WorkOwner.MAINTAINER,
            semantic_state=BriefSemanticState.HUMAN_REVIEW_REQUIRED.value,
        )

    if case.state in {
        "verification_complete",
        "ready_for_human_decision",
        "overridden",
    }:
        return NextStepBrief(
            status="awaiting_final_human_decision",
            display_title="治理材料检查已经完成",
            plain_explanation=(
                "下一阶段是由具有最终决定权的人类维护者决定是否接受贡献；"
                "检查完成不等于贡献已被接受。"
            ),
            responsible_party="具有最终决定权的人类维护者",
            system_will_do=("保留检查记录并等待最终人类决定。",),
            human_should_do=("作出明确的最终接受、拒绝、要求修改或关闭决定。",),
            final_acceptance_state="not_decided",
            owner=WorkOwner.FINAL_DECISION_AUTHORITY,
            semantic_state=BriefSemanticState.FINAL_DECISION_PENDING.value,
        )

    if case.overall_risk_level in {"low", "medium"}:
        return NextStepBrief(
            status="normal_code_review",
            display_title="无需额外 AGM 治理判断",
            plain_explanation=(
                "本次无需额外 AGM 治理判断，可以进入正常代码审查。"
            ),
            responsible_party="普通代码审查者",
            system_will_do=("保留已完成的结构与绑定核对结果。",),
            human_should_do=("按项目常规方式审查代码质量和功能影响。",),
            final_acceptance_state="not_decided",
            owner=WorkOwner.MAINTAINER,
            semantic_state=BriefSemanticState.SYSTEM_CHECKED.value,
        )

    return NextStepBrief(
        status="awaiting_maintainer_judgment",
        display_title="等待维护者检查",
        plain_explanation="前置材料已准备，当前等待维护者完成风险相关判断。",
        responsible_party="维护者侧检查人员",
        system_will_do=("保持当前治理结论和材料绑定不变。",),
        human_should_do=("检查页面列出的风险相关材料。",),
        final_acceptance_state="not_decided",
        owner=WorkOwner.MAINTAINER,
        semantic_state=BriefSemanticState.HUMAN_REVIEW_REQUIRED.value,
    )
