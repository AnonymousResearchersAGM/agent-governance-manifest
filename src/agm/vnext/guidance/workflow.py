"""Map the internal lifecycle to a five-step maintainer-facing workflow."""

from __future__ import annotations

from ..models import GovernanceCase, StateTransition
from .models import TraceReference, WorkflowStepView


STEP_STYLES = {
    "completed": ("✓", "已完成"),
    "current": ("●", "当前阶段"),
    "problem": ("!", "有问题"),
    "pending": ("○", "尚未开始"),
    "return": ("↺", "返回修改"),
    "skipped": ("—", "本次不要求"),
    "not_required": ("—", "本次不要求"),
}

STEP_DEFINITIONS = [
    (
        "identify_requirements",
        "系统识别要求",
        ["Resolve", "Compile"],
    ),
    (
        "prepare_materials",
        "贡献者准备材料",
        ["Bind", "Repair"],
    ),
    (
        "accountable_confirmation",
        "负责人确认",
        ["Attest"],
    ),
    (
        "maintainer_check",
        "维护者检查",
        ["Verify", "Repair"],
    ),
    (
        "human_final_decision",
        "人类维护者最终决定",
        ["Decide", "Record"],
    ),
]


def _has_required_type(case: GovernanceCase, obligation_type: str) -> bool:
    return any(item.type == obligation_type for item in case.obligations)


def _status_by_step(case: GovernanceCase) -> dict[str, tuple[str, str]]:
    terminal = case.state in {"accepted", "rejected", "closed"}
    has_attestation = _has_required_type(case, "human_attestation")
    has_verification = bool(case.obligations)
    invalid_attestation = any(
        item.status == "invalidated" for item in case.attestations
    )
    invalid_evidence = any(
        item.validity_state
        in {"stale", "expired", "invalid", "rejected", "conflicting"}
        for item in case.evidence
    )
    repair_active = case.state in {"repair_requested", "resubmitted"}
    repair_scope = sorted(
        {
            obligation_id
            for item in case.repair_requests
            if item.status in {"open", "resubmitted"}
            for obligation_id in item.revalidation_required
        }
    )

    identify = (
        ("current", "系统正在解析项目规则。")
        if case.state in {"case_opened", "policy_resolved"}
        else ("completed", "适用规则和本次要求已由 AGM 引擎生成。")
    )

    if repair_active:
        prepare = (
            "return",
            (
                "需要返回修改指定部分"
                + (f"：{', '.join(repair_scope)}" if repair_scope else "。")
            ),
        )
    elif invalid_evidence:
        prepare = ("problem", "已有材料过时、无效或被拒绝。")
    elif case.state == "evidence_incomplete":
        prepare = ("current", "贡献者正在准备或补齐本次所需材料。")
    elif case.state in {"case_opened", "policy_resolved", "obligations_compiled"}:
        prepare = ("pending", "系统完成要求识别后开始准备材料。")
    else:
        prepare = ("completed", "本次所需材料已提交到后续流程。")

    if not has_attestation:
        attest = ("skipped", "当前义务集合不要求负责人确认。")
    elif invalid_attestation:
        attest = ("problem", "旧的负责人确认已失效，需要重新确认受影响范围。")
    elif case.state == "awaiting_human_attestation":
        attest = ("current", "当前轮到负责人核对并确认明确范围。")
    elif any(item.status == "confirmed" for item in case.attestations):
        attest = ("completed", "负责人确认记录已绑定到当前有效范围。")
    elif case.state in {
        "awaiting_maintainer_verification",
        "verification_complete",
        "ready_for_human_decision",
        "overridden",
        "accepted",
        "rejected",
        "closed",
    }:
        attest = ("completed", "负责人确认要求已通过。")
    else:
        attest = ("pending", "材料准备完成后才进入负责人确认。")

    if not has_verification:
        verify = ("skipped", "本次没有 AGM 维护者核验义务。")
    elif repair_active:
        verify = (
            "return",
            "维护者已发现问题；修改后只重新检查 repair 影响范围。",
        )
    elif case.state == "awaiting_maintainer_verification":
        verify = ("current", "当前轮到有权限的维护者检查材料与绑定。")
    elif case.state in {
        "verification_complete",
        "ready_for_human_decision",
        "overridden",
        "accepted",
        "rejected",
        "closed",
    }:
        verify = ("completed", "维护者核验阶段已完成；这不等于接受贡献。")
    else:
        verify = ("pending", "贡献侧要求完成后才进入维护者检查。")

    if terminal:
        decide = ("completed", "已记录人类维护者最终决定和关闭信息。")
    elif case.state in {"ready_for_human_decision", "overridden"}:
        decide = ("current", "当前只能由人类维护者作出最终决定。")
    else:
        decide = ("pending", "前序治理要求完成后才进入最终决定。")

    return {
        "identify_requirements": identify,
        "prepare_materials": prepare,
        "accountable_confirmation": attest,
        "maintainer_check": verify,
        "human_final_decision": decide,
    }


def build_workflow_steps(
    case: GovernanceCase,
    transitions: list[StateTransition],
) -> list[WorkflowStepView]:
    statuses = _status_by_step(case)
    transition_refs = [
        TraceReference("state_transition", item.id, item.action)
        for item in transitions
    ]
    result = []
    for number, (step_id, title, internal_stages) in enumerate(
        STEP_DEFINITIONS, start=1
    ):
        status, explanation = statuses[step_id]
        symbol, label = STEP_STYLES[status]
        result.append(
            WorkflowStepView(
                number=number,
                step_id=step_id,
                title=title,
                status=status,
                status_label=label,
                symbol=symbol,
                explanation=explanation,
                internal_stages=internal_stages,
                traceability=transition_refs,
            )
        )
    return result
