"""Stable participant-facing labels for canonical governance terms.

The registry changes presentation only. Canonical identifiers remain available
to authority checks, state transitions, audit records, and folded technical
details.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping


@dataclass(frozen=True)
class PresentedTerm:
    """Pair a plain-language label with its unchanged canonical value."""

    display_plain: str
    canonical: str


def _registry(values: Mapping[str, str]) -> dict[str, PresentedTerm]:
    return {
        canonical: PresentedTerm(display_plain, canonical)
        for canonical, display_plain in values.items()
    }


ACTION_PRESENTATIONS = _registry(
    {
        "view_change_scope": "查看变化范围",
        "verify_evidence": "检查提交材料",
        "reject_evidence": "拒绝当前材料",
        "request_repair": "要求补充或修改",
        "ask_clarification": "请求补充说明",
        "confirm_attestation": "确认负责人声明",
        "invalidate_attestation": "将旧负责人确认标记为失效",
        "resubmit": "重新提交修改后的材料",
        "authorized_override": "由有权维护者执行覆盖处理",
        "override": "由有权维护者执行覆盖处理",
        "decide_accept": "最终接受",
        "final_accept": "最终接受",
        "decide_reject": "最终拒绝",
        "final_reject": "最终拒绝",
        "decide_request_changes": "要求继续修改",
        "request_changes": "要求继续修改",
        "decide_close": "关闭本次审核记录",
        "close_case": "关闭本次审核记录",
        "record_policy_conflict": "记录项目规则冲突",
        "resolve_policy_conflict": "处理项目规则冲突",
        "submit_for_verification": "提交维护者检查",
        "prepare_evidence": "准备提交材料",
        "request_correction": "要求更正",
        "decline_attestation": "拒绝负责人确认",
        "resolve_policy": "识别适用项目规则",
        "compile_obligations": "整理本次要求",
        "mark_evidence_state": "记录材料状态",
        "await_attestation": "等待负责人确认",
        "mark_ready": "标记为等待人类最终决定",
        "record_closure": "记录审核关闭",
    }
)

ROLE_PRESENTATIONS = _registry(
    {
        "contributor_agent": "贡献侧智能体",
        "contributor": "人类贡献者",
        "accountable_human": "负责人",
        "maintainer_verifier": "维护者侧检查人员",
        "maintainer": "人类维护者",
        "policy_steward": "项目规则负责人",
        "system": "确定性系统",
    }
)

OBLIGATION_PRESENTATIONS = _registry(
    {
        "O-SUMMARY": "修改说明",
        "O-CHANGED-FILES": "变更文件清单",
        "O-RATIONALE": "修改原因",
        "O-TEST-EXPLANATION": "测试覆盖说明",
        "O-TEST-COMMAND": "测试命令与结果",
        "O-ARTIFACT": "可检查的测试输出或文件",
        "O-LIMITATIONS": "已知限制",
        "O-AUTH-IMPACT": "登录、认证与权限影响说明",
        "O-POLICY-IMPACT": "项目规则影响说明",
        "O-AGENT-SCOPE": "智能体行动与委派说明",
        "O-HUMAN-ATTEST": "负责人确认",
        "O-INDEPENDENT-REVIEW": "独立维护者检查",
    }
)

WORKFLOW_PRESENTATIONS = _registry(
    {
        "identify_requirements": "识别本次要求",
        "prepare_materials": "准备和更新材料",
        "accountable_confirmation": "负责人确认",
        "maintainer_check": "维护者检查",
        "human_decision": "人类维护者最终决定",
    }
)

RECORD_TYPE_PRESENTATIONS = _registry(
    {
        "state_transition": "状态变化记录",
        "maintainer_verification": "维护者检查记录",
        "repair_request": "补充或修改请求",
        "closure_receipt": "审核关闭记录",
        "finding": "问题记录",
        "final_decision": "人类最终决定记录",
        "attempted_operation": "未生效操作审计记录",
        "bound_evidence": "材料绑定记录",
        "human_attestation": "负责人确认记录",
    }
)

STATE_PRESENTATIONS = _registry(
    {
        "case_opened": "系统正在识别项目要求",
        "policy_resolved": "系统已识别适用规则",
        "obligations_compiled": "系统已整理本次要求",
        "evidence_incomplete": "等待贡献者补齐材料",
        "awaiting_human_attestation": "等待负责人确认",
        "awaiting_maintainer_verification": "等待维护者检查",
        "repair_requested": "发现问题，等待指定范围修改",
        "resubmitted": "已补交，等待确认材料是否齐备",
        "verification_complete": "维护者检查完成，正在确认可决策状态",
        "ready_for_human_decision": "等待人类维护者最终决定",
        "overridden": "有权覆盖已记录，等待人类维护者最终决定",
        "accepted": "人类维护者已接受并关闭",
        "rejected": "人类维护者已拒绝并关闭",
        "closed": "案例已关闭",
        "ordinary_unmanaged": "按普通项目流程处理",
    }
)


def _present(
    registry: Mapping[str, PresentedTerm],
    canonical: str,
    fallback: str,
) -> PresentedTerm:
    return registry.get(canonical, PresentedTerm(fallback, canonical))


def present_action(action_id: str) -> PresentedTerm:
    return _present(ACTION_PRESENTATIONS, action_id, "某项维护者操作")


def present_role(role_id: str) -> PresentedTerm:
    return _present(ROLE_PRESENTATIONS, role_id, "某个有权角色")


def present_obligation(obligation_id: str) -> PresentedTerm:
    return _present(OBLIGATION_PRESENTATIONS, obligation_id, "某项项目要求")


def present_workflow_node(node_id: str) -> PresentedTerm:
    return _present(WORKFLOW_PRESENTATIONS, node_id, "某个审核步骤")


def present_record_type(record_type: str) -> PresentedTerm:
    return _present(
        RECORD_TYPE_PRESENTATIONS,
        record_type,
        "某类治理记录",
    )


def present_state(state_id: str) -> PresentedTerm:
    return _present(STATE_PRESENTATIONS, state_id, "当前审核阶段")


def format_presented_terms(
    values: list[str] | tuple[str, ...],
    presenter: Callable[[str], PresentedTerm],
    *,
    conjunction: str = "或",
) -> str:
    """Format canonical values as a natural Chinese participant-facing list."""

    labels = [presenter(value).display_plain for value in values]
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    return "、".join(labels[:-1]) + conjunction + labels[-1]


ROLE_LABELS = {
    canonical: term.display_plain
    for canonical, term in ROLE_PRESENTATIONS.items()
}

CURRENT_STATE_LABELS = {
    canonical: term.display_plain
    for canonical, term in STATE_PRESENTATIONS.items()
}
