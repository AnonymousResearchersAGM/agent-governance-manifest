"""Compile human judgment items into contextual, authorized business options."""

from __future__ import annotations

from ...config import VNextConfig
from ...models import CompiledObligation, GovernanceCase
from ..models import ReviewBriefView
from .authorization import (
    authorize_final_operation,
    authorize_item_operation,
)
from .binding import actor_from_context
from .models import (
    FinalDecisionOption,
    FinalDecisionView,
    InteractiveJudgmentItem,
    JudgmentOption,
    ReviewActionView,
)


OPTION_DEFINITIONS = (
    (
        "sufficient",
        "确认材料充分",
        "你确认该说明与当前贡献基本一致，可以完成此项维护者检查。",
        False,
        "sufficient",
        "verify_evidence",
    ),
    (
        "supplement",
        "要求补充或修正",
        "该材料不足以支持当前检查。AGM 将针对这一项生成贡献侧待办。",
        True,
        "supplement",
        "request_repair",
    ),
    (
        "material-risk",
        "标记重大风险",
        "你认为该项暴露出需要阻断当前进展的实质风险。",
        True,
        "material_risk",
        "request_repair",
    ),
)

FINAL_DEFINITIONS = (
    (
        "accept",
        "接受本次贡献",
        "项目正式接受本次贡献。",
        "decide_accept",
    ),
    (
        "reject",
        "拒绝本次贡献",
        "项目不接受本次贡献，并记录拒绝原因。",
        "decide_reject",
    ),
    (
        "request_changes",
        "要求修改后重新决定",
        "本次不作最终接受决定，贡献者需要根据意见修改后重新提交。",
        "decide_request_changes",
    ),
    (
        "close",
        "关闭本次审查",
        "结束本次治理案例并归档当前决定。",
        "decide_close",
    ),
)

MAINTAINER_REVIEW_STAGE = "awaiting_maintainer_verification"


def _canonical_judgments(
    review_brief: ReviewBriefView,
    case: GovernanceCase,
) -> list[tuple[object, CompiledObligation]]:
    requirement_map = {
        requirement.requirement_key: obligation
        for requirement, obligation in zip(
            review_brief.requirements.items,
            case.obligations,
            strict=True,
        )
    }
    result = []
    for judgment in review_brief.human_judgments:
        if len(judgment.requirement_refs) != 1:
            continue
        obligation = requirement_map.get(judgment.requirement_refs[0])
        if obligation is None:
            continue
        if "compiled_requirement" not in judgment.provenance:
            continue
        result.append((judgment, obligation))
    return result


def _interactive_next_step(
    review_brief: ReviewBriefView,
    case: GovernanceCase,
) -> dict[str, object]:
    if case.state != "resubmitted":
        return review_brief.current_next_step.to_dict()
    return {
        "status": "contribution_preparation",
        "display_title": "当前无需你操作",
        "responsible_party": "贡献侧",
        "plain_explanation": (
            "贡献侧已经补交材料，AGM 正在重新编译要求并提交维护者检查。"
            "材料正式进入维护者阶段后，你将收到需要检查的具体事项。"
        ),
        "participant_should_do": (),
        "system_will_do": (
            "重新校验材料结构、版本绑定和当前要求。",
            "使用既有贡献侧提交操作进入维护者检查阶段。",
        ),
        "blocking": False,
    }


def compile_contextual_actions(
    *,
    review_brief: ReviewBriefView,
    governance_case: GovernanceCase,
    actor_context: object,
    policy_config: VNextConfig,
    live_actions_enabled: bool = True,
) -> ReviewActionView:
    """Compile options only for canonical, currently active judgment items."""

    case = governance_case
    actor = actor_from_context(actor_context)
    maintainer_stage_ready = case.state == MAINTAINER_REVIEW_STAGE
    stage_unavailable_reason = (
        None
        if maintainer_stage_ready
        else (
            "材料已经补交，等待 AGM 提交维护者检查。"
            if case.state == "resubmitted"
            else "当前案例尚未进入维护者检查阶段。"
        )
    )
    items = []
    canonical_judgments = (
        _canonical_judgments(review_brief, case)
        if maintainer_stage_ready
        else ()
    )
    for judgment, obligation in canonical_judgments:
        options = []
        for (
            option_id,
            label,
            consequence,
            requires_reason,
            consequence_type,
            operation,
        ) in OPTION_DEFINITIONS:
            authorized, unavailable = authorize_item_operation(
                config=policy_config,
                case=case,
                actor=actor,
                obligation=obligation,
                operation=operation,
            )
            options.append(
                JudgmentOption(
                    option_id=option_id,
                    display_label=label,
                    plain_consequence=consequence,
                    requires_reason=requires_reason,
                    consequence_type=consequence_type,
                    authorized=authorized,
                    unavailable_reason=unavailable,
                    existing_operation_ref=(
                        operation if authorized else None
                    ),
                )
            )
        items.append(
            InteractiveJudgmentItem(
                judgment_id=judgment.judgment_id,
                display_title=judgment.display_title,
                why_human_is_needed=judgment.why_human_is_needed,
                contribution_claim=judgment.contribution_claim,
                system_observation=judgment.system_observation,
                evidence_summary=judgment.evidence_summary,
                review_focus=judgment.review_focus,
                options=tuple(options),
                blocking=judgment.blocking,
                requirement_refs=judgment.requirement_refs,
                provenance_refs=judgment.provenance,
            )
        )
    all_items_authorized = bool(items) and all(
        any(option.authorized for option in item.options)
        for item in items
    )
    unavailable_reason = None
    if not items:
        unavailable_reason = (
            stage_unavailable_reason
            or "当前没有需要该参与者完成的人类治理判断。"
        )
    elif not all_items_authorized:
        unavailable_reason = "当前参与者无权完成至少一项必需判断。"
    anomalies = tuple(
        item.to_dict()
        for item in review_brief.work_items
        if item.system_handled
    )
    return ReviewActionView(
        case_id=case.id,
        actor_id=actor.actor,
        role=actor.role,
        contribution_fingerprint=case.contribution_fingerprint,
        policy_snapshot_fingerprint=(
            case.policy_snapshot.policy_fingerprint
        ),
        case_state=case.state,
        items=tuple(items),
        live_actions_enabled=live_actions_enabled,
        can_save_draft=live_actions_enabled and all_items_authorized,
        can_preview=live_actions_enabled and all_items_authorized,
        unavailable_reason=unavailable_reason,
        maintainer_stage_ready=maintainer_stage_ready,
        current_stage=case.state,
        stage_unavailable_reason=stage_unavailable_reason,
        current_next_step=_interactive_next_step(review_brief, case),
        system_handled_anomalies=anomalies,
        final_decision_entry_available=(
            case.state in {"ready_for_human_decision", "overridden"}
            and actor.role == "maintainer"
            and actor.human
        ),
    )


def compile_final_decision_view(
    *,
    review_brief: ReviewBriefView,
    governance_case: GovernanceCase,
    actor_context: object,
    policy_config: VNextConfig,
) -> FinalDecisionView:
    """Expose final-decision operations only on a separate, eligible view."""

    case = governance_case
    actor = actor_from_context(actor_context)
    stage_available = case.state in {
        "ready_for_human_decision",
        "overridden",
    }
    options = []
    for decision, label, consequence, operation in FINAL_DEFINITIONS:
        authorized, reason = authorize_final_operation(
            config=policy_config,
            case=case,
            actor=actor,
            operation=operation,
        )
        options.append(
            FinalDecisionOption(
                decision_id=decision,
                display_label=label,
                plain_consequence=consequence,
                requires_reason=True,
                authorized=authorized,
                unavailable_reason=reason,
                existing_operation_ref=(
                    operation if authorized else None
                ),
            )
        )
    authorized = stage_available and any(item.authorized for item in options)
    unavailable = None
    if not stage_available:
        unavailable = "案例尚未进入最终人类决定阶段。"
    elif not authorized:
        unavailable = "当前参与者没有最终决定权限。"
    open_findings = [
        item for item in case.findings if item.status == "open"
    ]
    verified = len(case.maintainer_verifications)
    return FinalDecisionView(
        case_id=case.id,
        actor_id=actor.actor,
        role=actor.role,
        case_state=case.state,
        contribution_summary=review_brief.contribution.plain_summary,
        risk_summary=(
            f"风险等级：{review_brief.risk.display_level}。"
            + "主要风险："
            + "；".join(review_brief.risk.plain_reasons)
        ),
        requirement_summary="项目要求的材料已经齐备。",
        verification_summary=(
            "负责人已经确认当前版本，维护者已经完成必要检查。"
            if verified
            else "当前版本尚未完成必要的维护者检查。"
        ),
        unresolved_finding_summary=(
            f"仍有 {len(open_findings)} 项阻断问题需要处理。"
            if open_findings
            else "当前没有尚未解决的阻断问题。"
        ),
        final_authority_summary=(
            "现在需要由具有最终决定权限的人类维护者决定，"
            "本次贡献是否可以被项目接受。"
        ),
        acceptance_boundary=(
            "完成本页决定前，项目尚未接受本次贡献；"
            "接受后仍需按项目流程完成代码合并。"
        ),
        options=tuple(options),
        available=authorized,
        unavailable_reason=unavailable,
    )
