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

TRANSITION_STEP = {
    "open_case": "identify_requirements",
    "resolve_policy": "identify_requirements",
    "compile_obligations": "identify_requirements",
    "mark_evidence_state": "prepare_materials",
    "prepare_evidence": "prepare_materials",
    "resubmit": "prepare_materials",
    "await_attestation": "accountable_confirmation",
    "confirm_attestation": "accountable_confirmation",
    "decline_attestation": "accountable_confirmation",
    "invalidate_attestation": "accountable_confirmation",
    "request_correction": "accountable_confirmation",
    "submit_for_verification": "maintainer_check",
    "verify_evidence": "maintainer_check",
    "reject_evidence": "maintainer_check",
    "request_repair": "maintainer_check",
    "ask_clarification": "maintainer_check",
    "record_policy_conflict": "maintainer_check",
    "resolve_policy_conflict": "maintainer_check",
    "mark_ready": "human_final_decision",
    "authorized_override": "human_final_decision",
    "decide_accept": "human_final_decision",
    "decide_reject": "human_final_decision",
    "decide_request_changes": "human_final_decision",
    "decide_close": "human_final_decision",
}


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
    repair_scope = sorted(
        {
            obligation_id
            for item in case.repair_requests
            if item.status in {"open", "resubmitted"}
            for obligation_id in item.revalidation_required
        }
    )
    resubmission_inputs_ready = (
        case.state == "resubmitted"
        and all(
            item.type not in {"evidence", "human_attestation"}
            or item.status in {"satisfied", "verified", "overridden"}
            for item in case.obligations
            if item.obligation_id in set(repair_scope)
        )
    )

    identify = (
        ("current", "系统正在解析项目规则。")
        if case.state in {"case_opened", "policy_resolved"}
        else ("completed", "适用规则和本次要求已由 AGM 引擎生成。")
    )

    if case.state == "repair_requested":
        prepare = (
            "return",
            (
                "需要返回修改指定部分"
                + (f"：{', '.join(repair_scope)}" if repair_scope else "。")
            ),
        )
    elif case.state == "resubmitted" and resubmission_inputs_ready:
        prepare = (
            "completed",
            "指定范围已补交并具备可检查材料，未受影响材料继续保留。",
        )
    elif case.state == "resubmitted":
        prepare = (
            "return",
            "补交后仍有缺失、过时或无效材料，需要贡献侧继续处理。",
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
    elif case.state == "repair_requested":
        verify = (
            "return",
            "维护者已发现问题；修改后只重新检查指定修复范围。",
        )
    elif case.state == "resubmitted" and resubmission_inputs_ready:
        verify = (
            "current",
            "当前只重新检查指定修复范围；未受影响的检查结果保留。",
        )
    elif case.state == "resubmitted":
        verify = (
            "return",
            "受影响材料尚未齐备，当前不能开始重新检查。",
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
    traces_by_step: dict[str, list[TraceReference]] = {
        step_id: [] for step_id, _, _ in STEP_DEFINITIONS
    }
    for transition in transitions:
        step_id = TRANSITION_STEP.get(
            transition.action, "identify_requirements"
        )
        traces_by_step[step_id].append(
            TraceReference(
                "state_transition",
                transition.id,
                f"primary:{transition.action}",
            )
        )
    traces_by_step["identify_requirements"].extend(
        [
            *[
                TraceReference("matched_rule", item.id, "risk_matching")
                for item in case.matched_rules
            ],
            *[
                TraceReference(
                    "compiled_obligation", item.id, "obligation_compilation"
                )
                for item in case.obligations
            ],
            *[
                TraceReference(
                    "interaction_rule", interaction_id, "interaction_matching"
                )
                for interaction_id in sorted(
                    {
                        interaction_id
                        for item in case.obligations
                        for interaction_id in item.interaction_ids
                    }
                )
            ],
        ]
    )
    traces_by_step["prepare_materials"].extend(
        [
            *[
                TraceReference("evidence", item.id, "binding_or_retention")
                for item in case.evidence
            ],
            *[
                TraceReference("repair_request", item.id, "repair_scope")
                for item in case.repair_requests
            ],
        ]
    )
    traces_by_step["accountable_confirmation"].extend(
        TraceReference("human_attestation", item.id, item.status)
        for item in case.attestations
    )
    traces_by_step["maintainer_check"].extend(
        [
            *[
                TraceReference(
                    "maintainer_verification", item.id, item.outcome
                )
                for item in case.maintainer_verifications
            ],
            *[
                TraceReference("finding", item.id, item.status)
                for item in case.findings
            ],
        ]
    )
    if case.final_decision:
        traces_by_step["human_final_decision"].append(
            TraceReference(
                "final_decision",
                case.final_decision.id,
                case.final_decision.decision,
            )
        )
    if case.closure_receipt:
        traces_by_step["human_final_decision"].append(
            TraceReference(
                "closure_receipt",
                case.closure_receipt.id,
                "closure",
            )
        )
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
                traceability=traces_by_step[step_id],
            )
        )
    return result
