"""Authority-aligned action presentation and deterministic dry-run previews."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from ..config import VNextConfig
from ..models import GovernanceCase, StateTransition, fingerprint
from ..state_machine import allowed_actions
from .models import (
    ActionEffect,
    ActionPreview,
    ActionPreviewDisplayEffect,
    ActorContext,
    AvailableAction,
    ResponsibilityView,
    TraceReference,
    UnavailableAction,
)
from .diagnostics import (
    CURRENT_STATE_LABELS,
    build_requirement_comparisons,
)
from .responsibility import derive_current_responsibility
from .selectors import build_context_selector_options
from .term_presentations import (
    format_presented_terms,
    present_action,
    present_obligation,
    present_role,
    present_state,
)
from .workflow import build_workflow_steps


@dataclass(frozen=True)
class _ActionDefinition:
    action: str
    title: str
    description: str
    consequence: str
    mutates_state: bool = True
    required_parameters: tuple[str, ...] = ()


ACTION_DEFINITIONS = (
    _ActionDefinition(
        "view_change_scope",
        present_action("view_change_scope").display_plain,
        "查看变更文件、风险规则、影响范围和绑定指纹。",
        "只读操作，不改变案例状态。",
        mutates_state=False,
    ),
    _ActionDefinition(
        "verify_evidence",
        present_action("verify_evidence").display_plain,
        "记录维护者对指定项目要求及其绑定材料的检查结果。",
        "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
        required_parameters=("reason",),
    ),
    _ActionDefinition(
        "request_repair",
        present_action("request_repair").display_plain,
        "指出问题和受影响义务，返回贡献侧修复。",
        "仅指定范围需要修复和重新检查，未受影响材料保留。",
        required_parameters=("obligation_ids", "reason"),
    ),
    _ActionDefinition(
        "reject_evidence",
        present_action("reject_evidence").display_plain,
        "拒绝一条不能支持当前修改的具体材料。",
        "该材料将标记为已拒绝，并建立指定范围的补充或修改请求。",
        required_parameters=("object_id", "reason"),
    ),
    _ActionDefinition(
        "ask_clarification",
        present_action("ask_clarification").display_plain,
        "针对指定要求提出可审计的澄清问题。",
        "案例返回贡献侧回答，所选范围需要重新检查。",
        required_parameters=("obligation_ids", "reason"),
    ),
    _ActionDefinition(
        "invalidate_attestation",
        present_action("invalidate_attestation").display_plain,
        "使一条过时或不正确的负责人确认失效。",
        "负责人需要在修复后重新确认明确范围。",
        required_parameters=("object_id", "reason"),
    ),
    _ActionDefinition(
        "record_policy_conflict",
        present_action("record_policy_conflict").display_plain,
        "记录无法由普通材料修复的策略冲突。",
        "案例转入补充处理，由项目规则负责人或维护者处理。",
        required_parameters=("obligation_ids", "reason"),
    ),
    _ActionDefinition(
        "resolve_policy_conflict",
        present_action("resolve_policy_conflict").display_plain,
        "由有权限的角色记录策略冲突的解决依据。",
        "案例进入重新提交后的检查阶段，继续检查受影响范围。",
        required_parameters=("object_id", "reason"),
    ),
    _ActionDefinition(
        "resubmit",
        present_action("resubmit").display_plain,
        "贡献侧提交补充或修改影响范围和新增材料。",
        "案例进入重新检查；未受影响的有效材料保留。",
        required_parameters=("obligation_ids", "reason"),
    ),
    _ActionDefinition(
        "confirm_attestation",
        present_action("confirm_attestation").display_plain,
        "由负责人对明确范围作出事实确认。",
        "确认记录绑定当前贡献、策略和材料集合；不等于接受贡献。",
        required_parameters=("reason",),
    ),
    _ActionDefinition(
        "authorized_override",
        present_action("authorized_override").display_plain,
        "记录具备权限的维护者对明确项目要求或问题的例外处理。",
        "案例记录有权覆盖，但仍须人类维护者另行作最终决定。",
        required_parameters=("obligation_ids", "reason"),
    ),
    _ActionDefinition(
        "decide_accept",
        present_action("decide_accept").display_plain,
        "由人类维护者记录接受决定。",
        "案例记录接受状态并生成审核关闭记录；该动作不是自动合并。",
        required_parameters=("reason",),
    ),
    _ActionDefinition(
        "decide_reject",
        present_action("decide_reject").display_plain,
        "由人类维护者记录拒绝决定。",
        "案例记录拒绝状态并生成审核关闭记录。",
        required_parameters=("reason",),
    ),
    _ActionDefinition(
        "decide_request_changes",
        present_action("decide_request_changes").display_plain,
        "由人类维护者要求贡献侧继续修改。",
        "建立补充或修改请求并返回贡献侧。",
        required_parameters=("reason",),
    ),
    _ActionDefinition(
        "decide_close",
        present_action("decide_close").display_plain,
        "由人类维护者关闭案例而不表示接受或合并。",
        "案例记录关闭状态并生成审核关闭记录。",
        required_parameters=("reason",),
    ),
)


def normalize_actor(config: VNextConfig, actor: ActorContext) -> ActorContext:
    role = config.roles.get(actor.role, {})
    return ActorContext(
        actor=actor.actor,
        role=actor.role,
        human=bool(role.get("human", False)),
    )


def next_actor_roles(case: GovernanceCase) -> list[str]:
    if case.state in {"case_opened", "policy_resolved", "obligations_compiled"}:
        return ["system"]
    if case.state == "evidence_incomplete":
        return ["contributor", "contributor_agent"]
    if case.state == "awaiting_human_attestation":
        return ["accountable_human"]
    if case.state in {
        "awaiting_maintainer_verification",
        "verification_complete",
    }:
        return ["maintainer_verifier", "policy_steward", "maintainer"]
    if case.state == "repair_requested":
        roles = sorted(
            {
                item.responsible_role
                for item in case.repair_requests
                if item.status == "open"
            }
        )
        return roles or ["contributor", "contributor_agent"]
    if case.state == "resubmitted":
        return ["maintainer_verifier", "policy_steward", "maintainer"]
    if case.state in {"ready_for_human_decision", "overridden"}:
        return ["maintainer"]
    return []


def _transition_definition(
    config: VNextConfig,
    case: GovernanceCase,
    action: str,
) -> dict[str, Any] | None:
    return next(
        (
            item
            for item in config.state_machine["transitions"]
            if item["action"] == action and case.state in item["from"]
        ),
        None,
    )


def _repair_scope(case: GovernanceCase) -> list[str]:
    return sorted(
        {
            obligation_id
            for item in case.repair_requests
            if item.status in {"open", "resubmitted"}
            for obligation_id in item.revalidation_required
        }
    )


def default_action_scope(case: GovernanceCase, action: str) -> list[str]:
    if action == "verify_evidence":
        repair_scope = _repair_scope(case)
        if repair_scope:
            return repair_scope
        return [
            item.obligation_id
            for item in case.obligations
            if item.blocking
        ]
    if action in {
        "request_repair",
        "ask_clarification",
        "record_policy_conflict",
        "resubmit",
        "authorized_override",
    }:
        repair_scope = _repair_scope(case)
        if repair_scope:
            return repair_scope
        unresolved = [
            item.obligation_id
            for item in case.obligations
            if item.blocking
            and item.status not in {"satisfied", "verified", "overridden"}
        ]
        return unresolved[:1]
    return []


def _domain_unavailability(
    case: GovernanceCase,
    definition: _ActionDefinition,
    actor: ActorContext,
    scope: list[str],
) -> str | None:
    action = definition.action
    if action == "verify_evidence":
        requested = set(scope)
        unresolved = [
            item
            for item in case.obligations
            if item.obligation_id in requested
            and item.type in {"evidence", "human_attestation"}
            and item.status not in {"satisfied", "verified", "overridden"}
        ]
        if unresolved:
            comparison_by_id = {
                item.obligation_id: item
                for item in build_requirement_comparisons(case)
            }
            labels = [
                present_obligation(item.obligation_id).display_plain
                for item in unresolved
            ]
            if len(labels) == 1:
                material_reason = f"“{labels[0]}”"
            else:
                material_reason = "“" + "、".join(labels) + "”"
            material_statuses = {
                comparison_by_id[item.obligation_id].material_status
                for item in unresolved
                if item.obligation_id in comparison_by_id
            }
            if "stale" in material_statuses:
                material_reason += "仍需要更新"
            elif "invalid" in material_statuses:
                material_reason += "当前无效"
            else:
                material_reason += "尚未提供"
            participant_roles = (
                ["accountable_human"]
                if all(item.type == "human_attestation" for item in unresolved)
                else ["contributor", "contributor_agent"]
            )
            return (
                "当前还不能进行维护者检查。"
                f"原因：{material_reason}。"
                "当前可以继续处理的角色："
                + format_presented_terms(
                    participant_roles,
                    present_role,
                )
                + "。"
            )
        independent = "O-INDEPENDENT-REVIEW" in requested
        if independent and actor.role != "maintainer":
            return "独立维护者检查必须由人类维护者执行。"
        source_actors = {item.source_actor for item in case.evidence} | {
            item.actor for item in case.attestations
        }
        if independent and actor.actor in source_actors:
            return "独立检查要求执行者与材料或确认记录的提供者分离。"
    if action == "reject_evidence" and not case.evidence:
        return "当前没有可引用的材料记录。"
    if action == "invalidate_attestation" and not any(
        item.status == "confirmed" for item in case.attestations
    ):
        return "当前没有仍然有效的负责人确认可供失效处理。"
    if action == "resolve_policy_conflict" and not any(
        item.code == "policy_conflict" and item.status == "open"
        for item in case.findings
    ):
        return "当前没有待解决的项目规则冲突记录。"
    if action == "resubmit" and not any(
        item.status == "open" for item in case.repair_requests
    ):
        return "当前没有待处理的补充或修改请求。"
    if action == "authorized_override":
        open_findings = [
            item for item in case.findings if item.status == "open"
        ]
        eligible_obligations = {
            item.obligation_id
            for item in case.obligations
            if item.blocking
            and item.status not in {"satisfied", "verified", "overridden"}
        } | {
            obligation_id
            for finding in open_findings
            for obligation_id in finding.affected_obligation_ids
        }
        candidates = bool(open_findings) or any(
            item.blocking
            and item.status not in {"satisfied", "verified", "overridden"}
            for item in case.obligations
        )
        if not candidates:
            return "当前没有明确的项目要求或问题记录可供覆盖。"
        outside = sorted(set(scope) - eligible_obligations)
        if outside:
            return (
                "所选要求不属于当前可覆盖的开放异常范围："
                + "、".join(
                    present_obligation(item).display_plain
                    for item in outside
                )
                + "。"
            )
    if action == "confirm_attestation":
        unresolved_evidence = [
            item.obligation_id
            for item in case.obligations
            if item.type == "evidence"
            and item.blocking
            and item.status not in {"satisfied", "verified", "overridden"}
        ]
        if unresolved_evidence:
            return "材料尚未齐备，负责人不能确认当前范围。"
    return None


def _authority_reason(
    config: VNextConfig,
    case: GovernanceCase,
    definition: _ActionDefinition,
    actor: ActorContext,
    scope: list[str],
) -> str | None:
    if not definition.mutates_state:
        return None
    action = definition.action
    if actor.role not in config.roles:
        return "当前角色未被项目规则识别，后端不会授权该操作。"
    if action not in config.permissions.get(actor.role, set()):
        authorized_roles = sorted(
            role
            for role, actions in config.permissions.items()
            if action in actions
        )
        suffix = (
            "可以执行这一步的角色："
            + format_presented_terms(authorized_roles, present_role)
            + "。"
            if authorized_roles
            else ""
        )
        action_label = present_action(action).display_plain
        return f"当前角色没有“{action_label}”的权限。{suffix}".strip()
    transition = _transition_definition(config, case, action)
    if transition is None:
        return (
            f"当前处于“{present_state(case.state).display_plain}”，"
            f"还不能执行“{present_action(action).display_plain}”。"
        )
    if actor.role not in transition["roles"]:
        return (
            f"当前角色不能在“{present_state(case.state).display_plain}”"
            f"执行“{present_action(action).display_plain}”；"
            "可以执行这一步的角色："
            + format_presented_terms(transition["roles"], present_role)
            + "。"
        )
    return _domain_unavailability(case, definition, actor, scope)


def action_views(
    case: GovernanceCase,
    config: VNextConfig,
    actor: ActorContext,
) -> tuple[list[AvailableAction], list[UnavailableAction]]:
    normalized = normalize_actor(config, actor)
    comparisons = build_requirement_comparisons(case)
    available: list[AvailableAction] = []
    unavailable: list[UnavailableAction] = []
    state_actions = set(
        allowed_actions(config, state=case.state, role=normalized.role)
    )
    for definition in ACTION_DEFINITIONS:
        scope = default_action_scope(case, definition.action)
        reason = _authority_reason(
            config, case, definition, normalized, scope
        )
        traces = [
            TraceReference(
                "permission_rule",
                f"{normalized.role}:{definition.action}",
                "authority",
            )
        ]
        transition = _transition_definition(
            config, case, definition.action
        )
        if transition:
            traces.append(
                TraceReference(
                    "state_machine_rule",
                    f"{case.state}:{definition.action}:{transition['to']}",
                    "transition",
                )
            )
        if reason is None:
            relevance, group, primary_reason = _action_relevance(
                case, definition.action
            )
            available.append(
                AvailableAction(
                    action=definition.action,
                    title=definition.title,
                    description=definition.description,
                    consequence=definition.consequence,
                    mutates_state=definition.mutates_state,
                    actor_role=normalized.role,
                    default_obligation_ids=scope,
                    required_parameters=list(definition.required_parameters),
                    traceability=traces,
                    relevance=relevance,
                    group=group,
                    primary_reason=primary_reason,
                    selector_options=build_context_selector_options(
                        case, definition.action, comparisons
                    ),
                )
            )
        else:
            authorized_roles = sorted(
                role
                for role, actions in config.permissions.items()
                if definition.action in actions
            )
            if (
                definition.action not in state_actions
                and normalized.role in authorized_roles
                and transition is None
            ):
                roles = next_actor_roles(case)
            else:
                roles = authorized_roles or next_actor_roles(case)
            unavailable.append(
                UnavailableAction(
                    action=definition.action,
                    title=definition.title,
                    description=definition.description,
                    reason=reason,
                    next_actor_roles=roles,
                    mutates_state=definition.mutates_state,
                    traceability=traces,
                    category=_unavailable_category(reason),
                    required_role=authorized_roles,
                    required_state=_required_states(
                        config, definition.action
                    ),
                    future_availability=_future_availability(
                        case, definition.action, reason
                    ),
                )
            )
    return available, unavailable


def _action_relevance(
    case: GovernanceCase, action: str
) -> tuple[str, str, str]:
    state_relevant: dict[str, set[str]] = {
        "evidence_incomplete": set(),
        "awaiting_human_attestation": {
            "confirm_attestation",
            "invalidate_attestation",
        },
        "awaiting_maintainer_verification": {
            "verify_evidence",
            "request_repair",
            "reject_evidence",
            "ask_clarification",
        },
        "repair_requested": {"resubmit", "resolve_policy_conflict"},
        "resubmitted": {
            "verify_evidence",
            "request_repair",
            "reject_evidence",
        },
        "verification_complete": {"verify_evidence"},
        "ready_for_human_decision": {
            "decide_accept",
            "decide_reject",
            "decide_request_changes",
            "decide_close",
        },
        "overridden": {
            "decide_accept",
            "decide_reject",
            "decide_request_changes",
            "decide_close",
        },
    }
    if any(
        item.code == "policy_conflict" and item.status == "open"
        for item in case.findings
    ) and action == "resolve_policy_conflict":
        return (
            "current",
            "current_relevant",
            "当前存在未解决的项目规则冲突。",
        )
    if action in state_relevant.get(case.state, set()):
        return (
            "current",
            "current_relevant",
            "该操作直接对应当前流程阶段或开放问题。",
        )
    return (
        "secondary",
        "other_available",
        "后端允许此操作，但它不直接处理当前主要阻断项。",
    )


def _required_states(config: VNextConfig, action: str) -> list[str]:
    return sorted(
        {
            state
            for item in config.state_machine["transitions"]
            if item["action"] == action
            for state in item["from"]
        }
    )


def _unavailable_category(reason: str) -> str:
    if "没有" in reason and "权限" in reason:
        return "permission"
    if "当前状态" in reason or "不能从" in reason:
        return "stage"
    if "没有可" in reason or "没有待" in reason:
        return "object"
    if "范围" in reason or "项目" in reason:
        return "scope"
    return "authority"


def _future_availability(
    case: GovernanceCase, action: str, reason: str
) -> str:
    if "权限" in reason:
        return "切换流程阶段不会改变角色权限；需要由列出的有权角色执行。"
    if "没有" in reason and ("记录" in reason or "finding" in reason):
        return "仅在当前案例出现相应有效对象时可用。"
    if action.startswith("decide_"):
        return "前序阻断要求完成并进入人类最终决定阶段后可用。"
    if case.state in {"accepted", "rejected", "closed"}:
        return "案例已关闭，后续阶段不再开放此操作。"
    return "到达所需状态且对象范围满足后可能可用。"


def _selected_scope(
    case: GovernanceCase,
    action: str,
    parameters: dict[str, Any],
) -> list[str]:
    raw = parameters.get("obligation_ids")
    if raw is None:
        raw = parameters.get("obligation")
    if isinstance(raw, str):
        raw = [raw] if raw else []
    scope = list(dict.fromkeys(raw or default_action_scope(case, action)))
    known = {item.obligation_id for item in case.obligations}
    return [item for item in scope if item in known]


def _scope_error(
    case: GovernanceCase,
    action: str,
    parameters: dict[str, Any],
) -> str | None:
    raw = parameters.get("obligation_ids")
    if raw is None:
        raw = parameters.get("obligation")
    if isinstance(raw, str):
        raw = [raw] if raw else []
    supplied = set(raw or [])
    known = {item.obligation_id for item in case.obligations}
    unknown = sorted(supplied - known)
    if unknown:
        return "操作范围包含当前案例不存在的项目要求；具体标识见技术详情。"
    if action == "resubmit" and supplied:
        open_scope = {
            obligation_id
            for item in case.repair_requests
            if item.status == "open"
            for obligation_id in item.affected_obligation_ids
        }
        outside = sorted(supplied - open_scope)
        if outside:
            return "补交范围不属于当前待处理的补充或修改请求。"
    return None


def _object_error(
    case: GovernanceCase,
    action: str,
    parameters: dict[str, Any],
) -> str | None:
    object_id = str(parameters.get("object_id", "") or "")
    if action == "reject_evidence":
        evidence = next(
            (item for item in case.evidence if item.id == object_id),
            None,
        )
        if evidence is None:
            return "请选择当前案例中可拒绝的材料。"
        if evidence.validity_state not in {"valid", "verified"}:
            return "所选材料当前不是可拒绝的有效候选。"
    if action == "invalidate_attestation":
        attestation = next(
            (
                item
                for item in case.attestations
                if item.id == object_id
            ),
            None,
        )
        if attestation is None or attestation.status != "confirmed":
            return "请选择当前案例中仍然有效的负责人确认。"
    if action == "resolve_policy_conflict":
        finding = next(
            (
                item
                for item in case.findings
                if item.id == object_id
            ),
            None,
        )
        if (
            finding is None
            or finding.code != "policy_conflict"
            or finding.status != "open"
        ):
            return "请选择当前案例中开放的项目规则冲突。"
    if action == "authorized_override":
        finding_ids = set(parameters.get("finding_ids", []) or [])
        known_open = {
            item.id
            for item in case.findings
            if item.status == "open"
        }
        if finding_ids - known_open:
            return "覆盖范围包含当前案例中不存在或已关闭的问题。"
    return None


def _predicted_target(
    case: GovernanceCase,
    config: VNextConfig,
    action: str,
    scope: list[str],
) -> str:
    transition = _transition_definition(config, case, action)
    if transition is None:
        return case.state
    target = transition["to"]
    if action != "verify_evidence":
        return target
    requested = set(scope)
    remaining_obligations = [
        item
        for item in case.obligations
        if item.blocking
        and item.obligation_id not in requested
        and item.status not in {"satisfied", "verified", "overridden"}
    ]
    remaining_findings = [
        item
        for item in case.findings
        if item.blocking
        and item.status == "open"
        and not set(item.affected_obligation_ids) <= requested
    ]
    if not remaining_obligations and not remaining_findings:
        return "ready_for_human_decision"
    return target


def _current_workflow_step(
    case: GovernanceCase, transitions: list[StateTransition]
) -> str:
    steps = build_workflow_steps(case, transitions)
    current = next(
        (
            item
            for item in steps
            if item.status in {"current", "problem", "return"}
        ),
        steps[-1],
    )
    return current.step_id


def _workflow_step_title(
    case: GovernanceCase,
    transitions: list[StateTransition],
) -> str:
    steps = build_workflow_steps(case, transitions)
    current = next(
        (
            item
            for item in steps
            if item.status in {"current", "problem", "return"}
        ),
        steps[-1],
    )
    return current.title


def _status_label(value: str) -> str:
    return {
        "unsatisfied": "尚未满足",
        "satisfied": "材料已满足",
        "verified": "已检查",
        "overridden": "已由有权维护者覆盖",
        "needs_update": "需要更新",
        "policy_conflict": "项目规则冲突",
        "revalidation_required": "等待重新检查",
        "valid": "有效",
        "rejected": "已拒绝",
        "confirmed": "已确认",
        "invalidated": "已失效",
        "resolved": "已关闭",
        "open": "待处理",
        "resubmitted": "已补充，等待重新检查",
        "unchanged": "不变",
    }.get(value, CURRENT_STATE_LABELS.get(value, value))


def _project_action(
    case: GovernanceCase,
    action: str,
    scope: list[str],
    target_state: str,
    parameters: dict[str, Any],
) -> tuple[GovernanceCase, list[str], list[str], list[str]]:
    projected = copy.deepcopy(case)
    invalidated_evidence: list[str] = []
    invalidated_attestations: list[str] = []
    creates_records: list[str] = ["state_transition"]
    requested = set(scope)
    if action == "verify_evidence":
        creates_records.append("maintainer_verification")
        for evidence in projected.evidence:
            if (
                set(evidence.obligation_ids) & requested
                and evidence.validity_state in {"valid", "verified"}
            ):
                evidence.validity_state = "verified"
        for obligation in projected.obligations:
            if (
                obligation.obligation_id in requested
                and obligation.type != "human_attestation"
            ):
                obligation.status = "verified"
        for finding in projected.findings:
            if (
                finding.status == "open"
                and finding.code != "policy_conflict"
                and set(finding.affected_obligation_ids) <= requested
            ):
                finding.status = "resolved"
        finding_statuses = {
            item.id: item.status for item in projected.findings
        }
        for repair in projected.repair_requests:
            if (
                repair.status in {"open", "resubmitted"}
                and repair.finding_ids
                and all(
                    finding_statuses.get(finding_id) != "open"
                    for finding_id in repair.finding_ids
                )
            ):
                repair.status = "resolved"
    elif action in {
        "request_repair",
        "ask_clarification",
        "record_policy_conflict",
    }:
        creates_records.extend(["finding", "repair_request"])
        if action == "record_policy_conflict":
            for obligation in projected.obligations:
                if obligation.obligation_id in requested:
                    obligation.status = "policy_conflict"
    elif action == "reject_evidence":
        creates_records.extend(["finding", "repair_request"])
        object_id = str(parameters.get("object_id", ""))
        evidence = next(
            (item for item in projected.evidence if item.id == object_id),
            None,
        )
        if evidence:
            evidence.validity_state = "rejected"
            invalidated_evidence.append(evidence.id)
            for obligation_id in evidence.obligation_ids:
                projected.obligation(obligation_id).status = "unsatisfied"
    elif action == "invalidate_attestation":
        creates_records.extend(["finding", "repair_request"])
        object_id = str(parameters.get("object_id", ""))
        attestation = next(
            (
                item
                for item in projected.attestations
                if item.id == object_id
            ),
            None,
        )
        if attestation:
            attestation.status = "invalidated"
            invalidated_attestations.append(attestation.id)
            for obligation in projected.obligations:
                if obligation.type == "human_attestation":
                    obligation.status = "unsatisfied"
    elif action == "resolve_policy_conflict":
        object_id = str(parameters.get("object_id", ""))
        for finding in projected.findings:
            if finding.id == object_id:
                finding.status = "resolved"
    elif action == "resubmit":
        for repair in projected.repair_requests:
            if (
                repair.status == "open"
                and set(repair.affected_obligation_ids) & requested
            ):
                repair.status = "resubmitted"
    elif action == "authorized_override":
        for obligation in projected.obligations:
            if obligation.obligation_id in requested:
                obligation.status = "overridden"
        for finding_id in parameters.get("finding_ids", []) or []:
            for finding in projected.findings:
                if finding.id == finding_id:
                    finding.status = "overridden"
    elif action.startswith("decide_"):
        creates_records.append("final_decision")
        if action != "decide_request_changes":
            creates_records.append("closure_receipt")
        else:
            creates_records.extend(["finding", "repair_request"])
    projected.state = target_state
    return (
        projected,
        invalidated_evidence,
        invalidated_attestations,
        creates_records,
    )


def preview_reviewer_action(
    case: GovernanceCase,
    policy: VNextConfig,
    transitions: list[StateTransition],
    actor: ActorContext,
    action: str,
    parameters: dict[str, Any] | None = None,
) -> ActionPreview:
    """Plan an action without changing the case, storage, or transitions."""
    parameters = dict(parameters or {})
    normalized = normalize_actor(policy, actor)
    definition = next(
        (item for item in ACTION_DEFINITIONS if item.action == action),
        _ActionDefinition(
            action,
            present_action(action).display_plain,
            "未知操作。",
            "不会执行。",
        ),
    )
    scope = _selected_scope(case, action, parameters)
    reason = (
        _scope_error(case, action, parameters)
        or _object_error(case, action, parameters)
        or _authority_reason(
            policy, case, definition, normalized, scope
        )
    )
    authorized = reason is None
    target_state = (
        _predicted_target(case, policy, action, scope)
        if authorized
        else case.state
    )
    effects: list[ActionEffect] = []
    retained_evidence = [
        item.id
        for item in case.evidence
        if not set(item.obligation_ids) & set(scope)
    ]
    invalidated_attestations: list[str] = []
    invalidated_evidence: list[str] = []
    creates_records: list[str] = []
    responsibility_before = derive_current_responsibility(
        case,
        build_requirement_comparisons(case),
        actor_context=normalized,
    )
    projected = copy.deepcopy(case)

    if authorized and definition.mutates_state:
        (
            projected,
            invalidated_evidence,
            invalidated_attestations,
            creates_records,
        ) = _project_action(
            case, action, scope, target_state, parameters
        )
        effects.append(
            ActionEffect(
                target="案例状态",
                before=case.state,
                after=target_state,
                explanation=definition.consequence,
                source_object_ids=[item.id for item in transitions[-1:]],
            )
        )
        for obligation_id in scope:
            obligation = case.obligation(obligation_id)
            after = {
                "verify_evidence": "verified",
                "authorized_override": "overridden",
                "request_repair": "needs_update",
                "ask_clarification": "needs_update",
                "record_policy_conflict": "policy_conflict",
                "resubmit": "revalidation_required",
            }.get(action, obligation.status)
            effects.append(
                ActionEffect(
                    target=obligation_id,
                    before=obligation.status,
                    after=after,
                    explanation=definition.consequence,
                    source_object_ids=[obligation.id],
                )
            )
        if action == "verify_evidence":
            resolved_finding_ids: set[str] = set()
            for repair in case.repair_requests:
                affected_findings = [
                    finding
                    for finding in case.findings
                    if finding.id in repair.finding_ids
                ]
                if (
                    repair.status in {"open", "resubmitted"}
                    and affected_findings
                    and all(
                        set(finding.affected_obligation_ids)
                        <= set(scope)
                        for finding in affected_findings
                        if finding.status == "open"
                    )
                ):
                    for finding in affected_findings:
                        if (
                            finding.status == "open"
                            and finding.id not in resolved_finding_ids
                        ):
                            effects.append(
                                ActionEffect(
                                    target=finding.id,
                                    before=finding.status,
                                    after="resolved",
                                    explanation=(
                                        "本次重新检查通过后，关联问题将关闭。"
                                    ),
                                    source_object_ids=[finding.id],
                                )
                            )
                            resolved_finding_ids.add(finding.id)
                    effects.append(
                        ActionEffect(
                            target="指定修复请求",
                            before=repair.status,
                            after="resolved",
                            explanation=(
                                "所关联的问题在本次重新检查后关闭。"
                            ),
                            source_object_ids=[repair.id],
                        )
                    )
        if action == "reject_evidence":
            object_id = str(parameters.get("object_id", ""))
            evidence = next(
                (item for item in case.evidence if item.id == object_id),
                None,
            )
            if evidence:
                effects.append(
                    ActionEffect(
                        target=evidence.id,
                        before=evidence.validity_state,
                        after="rejected",
                        explanation="该材料不再支持其绑定义务。",
                        source_object_ids=[evidence.id],
                    )
                )
        if action == "invalidate_attestation":
            object_id = str(parameters.get("object_id", ""))
            attestation = next(
                (item for item in case.attestations if item.id == object_id),
                None,
            )
            if attestation:
                effects.append(
                    ActionEffect(
                        target=attestation.id,
                        before=attestation.status,
                        after="invalidated",
                        explanation="负责人需要重新确认受影响范围。",
                        source_object_ids=[attestation.id],
                    )
                )
    elif not definition.mutates_state:
        effects.append(
            ActionEffect(
                target="案例数据",
                before="unchanged",
                after="unchanged",
                explanation=definition.consequence,
                source_object_ids=[case.id],
            )
        )

    responsibility_after = derive_current_responsibility(
        projected,
        build_requirement_comparisons(projected),
        actor_context=normalized,
    )
    before_step = _current_workflow_step(case, transitions)
    after_step = _current_workflow_step(projected, transitions)
    before_step_title = _workflow_step_title(case, transitions)
    after_step_title = _workflow_step_title(projected, transitions)
    attestation_required = any(
        item.type == "human_attestation"
        and item.blocking
        and item.status not in {"satisfied", "verified", "overridden"}
        for item in projected.obligations
    )
    verification_required = (
        projected.state
        not in {
            "ready_for_human_decision",
            "overridden",
            "accepted",
            "rejected",
            "closed",
        }
        and (
            any(
                item.blocking
                and item.status not in {"verified", "overridden"}
                for item in projected.obligations
                if item.type != "human_attestation"
            )
            or bool(projected.open_blocking_findings())
        )
    )
    final_acceptance_recorded = (
        action == "decide_accept"
        and authorized
        and definition.mutates_state
    )

    preview_material = {
        "case_id": case.id,
        "case_updated_at": case.updated_at,
        "contribution_fingerprint": case.contribution_fingerprint,
        "policy_fingerprint": case.policy_snapshot.policy_fingerprint,
        "actor": normalized.to_dict(),
        "action": action,
        "parameters": parameters,
        "source_state": case.state,
        "target_state": target_state,
        "transition_count": len(transitions),
    }
    traceability = [
        TraceReference(
            "permission_rule",
            f"{normalized.role}:{action}",
            "authority",
        ),
        TraceReference(
            "governance_case",
            case.id,
            "source_state",
        ),
    ]
    transition = _transition_definition(policy, case, action)
    if transition:
        traceability.append(
            TraceReference(
                "state_machine_rule",
                f"{case.state}:{action}:{transition['to']}",
                "transition_plan",
            )
        )
    comparisons = {
        item.obligation_id: item
        for item in build_requirement_comparisons(case)
    }
    display_effects: list[ActionPreviewDisplayEffect] = []
    for effect in effects:
        if effect.target == "案例状态":
            label = "案例流程"
        elif effect.target in comparisons:
            label = comparisons[effect.target].display_name
        elif effect.target == "指定修复请求":
            label = "本次修复请求"
        elif any(
            item.id == effect.target for item in case.evidence
        ):
            evidence = next(
                item for item in case.evidence if item.id == effect.target
            )
            labels = [
                comparisons[item].display_name
                for item in evidence.obligation_ids
                if item in comparisons
            ]
            label = "、".join(labels) or "指定材料"
        elif any(
            item.id == effect.target for item in case.attestations
        ):
            label = "负责人确认"
        elif any(
            item.id == effect.target for item in case.findings
        ):
            label = "本次问题"
        else:
            label = "案例数据"
        display_effects.append(
            ActionPreviewDisplayEffect(
                display_label=label,
                before_label=_status_label(effect.before),
                after_label=_status_label(effect.after),
                display_description=effect.explanation,
            )
        )

    affected_items = [
        comparisons[item].display_name
        for item in scope
        if item in comparisons
    ]
    retained_items = list(
        dict.fromkeys(
            comparisons[obligation_id].display_name
            for evidence in case.evidence
            if evidence.id in retained_evidence
            for obligation_id in evidence.obligation_ids
            if obligation_id in comparisons
        )
    )
    invalidated_items = list(
        dict.fromkeys(
            [
                comparisons[obligation_id].display_name
                for evidence in case.evidence
                if evidence.id in invalidated_evidence
                for obligation_id in evidence.obligation_ids
                if obligation_id in comparisons
            ]
            + (
                ["负责人确认"]
                if invalidated_attestations
                else []
            )
        )
    )
    next_steps: list[str] = []
    if not authorized:
        next_steps.extend(
            [
                "本次操作不会改变案例状态。",
                (
                    "当前责任方仍是"
                    f"{responsibility_before.display_label}。"
                ),
            ]
        )
    else:
        if action == "verify_evidence":
            next_steps.append("本次指定材料将被标记为已检查。")
            if any(
                item.target == "指定修复请求"
                and item.after == "resolved"
                for item in effects
            ):
                next_steps.append("关联的问题和修复请求将被关闭。")
        if responsibility_after != responsibility_before:
            next_steps.append(
                "当前责任方将转交给"
                f"{responsibility_after.display_label}。"
            )
        next_steps.append(f"案例将进入“{after_step_title}”。")
    if not final_acceptance_recorded:
        next_steps.append("这不等于代码已经被项目接受。")

    requested_obligation_ids = parameters.get("obligation_ids", []) or []
    if isinstance(requested_obligation_ids, str):
        requested_obligation_ids = [requested_obligation_ids]
    technical_details = {
        "operation": action,
        "current_role": normalized.role,
        "required_roles": sorted(
            role
            for role, actions in policy.permissions.items()
            if action in actions
        ),
        "source_state": case.state,
        "target_state": target_state,
        "effects": [item.to_dict() for item in effects],
        "affected_obligation_ids": scope,
        "requested_obligation_ids": list(
            dict.fromkeys(requested_obligation_ids)
        ),
        "retained_evidence_ids": retained_evidence,
        "invalidated_attestation_ids": invalidated_attestations,
        "invalidated_evidence_ids": invalidated_evidence,
        "processed_objects": [
            *scope,
            *(
                [str(parameters.get("object_id"))]
                if parameters.get("object_id")
                else []
            ),
        ],
        "workflow_step_before": before_step,
        "workflow_step_after": after_step,
        "creates_records": creates_records,
        "preview_fingerprint": fingerprint(preview_material),
        "traceability": [item.to_dict() for item in traceability],
    }
    preview_title = definition.title
    if action == "verify_evidence" and affected_items:
        preview_title = (
            f"只重新检查“{affected_items[0]}”"
            if len(affected_items) == 1
            else "检查指定范围：" + "、".join(affected_items)
        )
    return ActionPreview(
        title=preview_title,
        actor=normalized,
        authorized=authorized,
        authorization_reason=(
            "当前角色和案例状态允许生成此操作计划。"
            if authorized
            else reason or "操作不可用。"
        ),
        display_effects=display_effects,
        affected_items=affected_items,
        retained_items=retained_items,
        invalidated_items=invalidated_items,
        next_authorized_actor_roles=(
            responsibility_before.primary_roles
            if not authorized
            else responsibility_after.primary_roles
        ),
        requires_confirmation=authorized and definition.mutates_state,
        mutates_case=False,
        technical_details=technical_details,
        responsibility_before=responsibility_before,
        responsibility_after=responsibility_after,
        workflow_position_before=before_step_title,
        workflow_position_after=after_step_title,
        next_steps=next_steps,
        requires_human_attestation_after=attestation_required,
        requires_maintainer_verification_after=verification_required,
        final_acceptance_recorded=final_acceptance_recorded,
        final_acceptance_still_required=(
            projected.state
            not in {"accepted", "rejected", "closed"}
            and not final_acceptance_recorded
        ),
    )
