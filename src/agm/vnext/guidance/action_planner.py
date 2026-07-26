"""Authority-aligned action presentation and deterministic dry-run previews."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..config import VNextConfig
from ..models import GovernanceCase, StateTransition, fingerprint
from ..state_machine import allowed_actions
from .models import (
    ActionEffect,
    ActionPreview,
    ActorContext,
    AvailableAction,
    TraceReference,
    UnavailableAction,
)


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
        "查看变化范围",
        "查看 changed files、风险规则、影响范围和绑定 fingerprint。",
        "只读操作，不改变案例状态。",
        mutates_state=False,
    ),
    _ActionDefinition(
        "verify_evidence",
        "检查待核验项",
        "记录维护者对指定义务及其绑定材料的检查结果。",
        "受影响项会记录 verification；全部阻断项完成后进入人类最终决定。",
        required_parameters=("reason",),
    ),
    _ActionDefinition(
        "request_repair",
        "请求补充或更新材料",
        "指出问题和受影响义务，返回贡献侧修复。",
        "仅指定范围需要修复和重新检查，未受影响材料保留。",
        required_parameters=("obligation_ids", "reason"),
    ),
    _ActionDefinition(
        "reject_evidence",
        "拒绝无效材料",
        "拒绝一条不能支持当前修改的具体材料。",
        "该材料标记为 rejected，并建立 scoped repair。",
        required_parameters=("object_id", "reason"),
    ),
    _ActionDefinition(
        "ask_clarification",
        "请求说明",
        "针对指定要求提出可审计的澄清问题。",
        "案例返回贡献侧回答，所选范围需要重新检查。",
        required_parameters=("obligation_ids", "reason"),
    ),
    _ActionDefinition(
        "invalidate_attestation",
        "要求负责人重新确认",
        "使一条过时或不正确的负责人确认失效。",
        "负责人需要在修复后重新确认明确范围。",
        required_parameters=("object_id", "reason"),
    ),
    _ActionDefinition(
        "record_policy_conflict",
        "记录项目规则冲突",
        "记录无法由普通材料修复的策略冲突。",
        "案例转入 repair，由 policy steward 或维护者处理。",
        required_parameters=("obligation_ids", "reason"),
    ),
    _ActionDefinition(
        "resolve_policy_conflict",
        "解决项目规则冲突",
        "由有权限的角色记录策略冲突的解决依据。",
        "案例进入 resubmitted，继续检查受影响范围。",
        required_parameters=("object_id", "reason"),
    ),
    _ActionDefinition(
        "resubmit",
        "补交指定范围",
        "贡献侧提交 repair 影响范围和新增材料。",
        "案例进入重新检查；未受影响的有效材料保留。",
        required_parameters=("obligation_ids", "reason"),
    ),
    _ActionDefinition(
        "confirm_attestation",
        "负责人确认当前范围",
        "由 accountable human 对明确范围作出事实确认。",
        "确认记录绑定当前贡献、策略和材料集合；不等于接受贡献。",
        required_parameters=("reason",),
    ),
    _ActionDefinition(
        "authorized_override",
        "执行有权覆盖",
        "记录具备权限的维护者对明确义务或 finding 的例外处理。",
        "案例进入 overridden，但仍须人类维护者另行作最终决定。",
        required_parameters=("obligation_ids", "reason"),
    ),
    _ActionDefinition(
        "decide_accept",
        "提交人类最终接受决定",
        "由人类维护者记录接受决定。",
        "案例 accepted 并生成 closure receipt；该动作不是自动合并。",
        required_parameters=("reason",),
    ),
    _ActionDefinition(
        "decide_reject",
        "提交人类最终拒绝决定",
        "由人类维护者记录拒绝决定。",
        "案例 rejected 并生成 closure receipt。",
        required_parameters=("reason",),
    ),
    _ActionDefinition(
        "decide_request_changes",
        "提交人类修改决定",
        "由人类维护者要求贡献侧继续修改。",
        "建立 repair request 并返回贡献侧。",
        required_parameters=("reason",),
    ),
    _ActionDefinition(
        "decide_close",
        "关闭案例",
        "由人类维护者关闭案例而不表示接受或合并。",
        "案例 closed 并生成 closure receipt。",
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
            item.obligation_id
            for item in case.obligations
            if item.obligation_id in requested
            and item.type in {"evidence", "human_attestation"}
            and item.status not in {"satisfied", "verified", "overridden"}
        ]
        if unresolved:
            return (
                "这些项目的材料或负责人确认尚未满足，当前不能核验："
                + ", ".join(unresolved)
            )
        independent = "O-INDEPENDENT-REVIEW" in requested
        if independent and actor.role != "maintainer":
            return "独立检查要求必须由 maintainer 角色执行。"
        source_actors = {item.source_actor for item in case.evidence} | {
            item.actor for item in case.attestations
        }
        if independent and actor.actor in source_actors:
            return "独立检查要求执行者与材料或确认记录的提供者分离。"
    if action == "reject_evidence" and not case.evidence:
        return "当前没有可引用的 evidence record。"
    if action == "invalidate_attestation" and not any(
        item.status == "confirmed" for item in case.attestations
    ):
        return "当前没有仍然有效的负责人确认可供失效处理。"
    if action == "resolve_policy_conflict" and not any(
        item.code == "policy_conflict" and item.status == "open"
        for item in case.findings
    ):
        return "当前没有待解决的 policy_conflict finding。"
    if action == "resubmit" and not any(
        item.status == "open" for item in case.repair_requests
    ):
        return "当前没有开放的 repair request。"
    if action == "authorized_override":
        candidates = any(
            item.status == "open" for item in case.findings
        ) or any(
            item.blocking
            and item.status not in {"satisfied", "verified", "overridden"}
            for item in case.obligations
        )
        if not candidates:
            return "当前没有明确的 obligation 或 finding 可供覆盖。"
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
        return f"未知角色 {actor.role}，后端不会授权该操作。"
    if action not in config.permissions.get(actor.role, set()):
        authorized_roles = sorted(
            role
            for role, actions in config.permissions.items()
            if action in actions
        )
        suffix = (
            f" 可执行角色：{', '.join(authorized_roles)}。"
            if authorized_roles
            else ""
        )
        return f"当前角色没有 {action} 权限。{suffix}".strip()
    transition = _transition_definition(config, case, action)
    if transition is None:
        return f"操作 {action} 不能从当前状态 {case.state} 执行。"
    if actor.role not in transition["roles"]:
        return (
            f"当前角色不能从 {case.state} 执行 {action}；"
            f"允许角色：{', '.join(transition['roles'])}。"
        )
    return _domain_unavailability(case, definition, actor, scope)


def action_views(
    case: GovernanceCase,
    config: VNextConfig,
    actor: ActorContext,
) -> tuple[list[AvailableAction], list[UnavailableAction]]:
    normalized = normalize_actor(config, actor)
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
                )
            )
    return available, unavailable


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
            action,
            "未知操作。",
            "不会执行。",
        ),
    )
    scope = _selected_scope(case, action, parameters)
    reason = _authority_reason(
        policy, case, definition, normalized, scope
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

    if authorized and definition.mutates_state:
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
                invalidated_attestations.append(attestation.id)
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
    return ActionPreview(
        action=action,
        title=definition.title,
        actor=normalized,
        authorized=authorized,
        authorization_reason=(
            "当前角色和案例状态允许生成此操作计划。"
            if authorized
            else reason or "操作不可用。"
        ),
        source_state=case.state,
        target_state=target_state,
        effects=effects,
        affected_obligation_ids=scope,
        retained_evidence_ids=retained_evidence,
        invalidated_attestation_ids=invalidated_attestations,
        next_authorized_actor_roles=(
            next_actor_roles(case)
            if not authorized
            else (
                ["maintainer"]
                if target_state in {"ready_for_human_decision", "overridden"}
                else next_actor_roles(case)
            )
        ),
        requires_confirmation=authorized and definition.mutates_state,
        mutates_case=False,
        preview_fingerprint=fingerprint(preview_material),
        traceability=traceability,
    )
