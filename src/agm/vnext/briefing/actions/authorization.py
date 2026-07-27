"""Fail-closed authority checks for contextual review actions."""

from __future__ import annotations

from ...config import VNextConfig
from ...guidance import ActorContext
from ...models import CompiledObligation, GovernanceCase
from ...state_machine import allowed_actions


def is_human_role(config: VNextConfig, actor: ActorContext) -> bool:
    configured = config.roles.get(actor.role)
    return bool(actor.human and configured and configured.get("human"))


def authorize_item_operation(
    *,
    config: VNextConfig,
    case: GovernanceCase,
    actor: ActorContext,
    obligation: CompiledObligation,
    operation: str,
) -> tuple[bool, str | None]:
    if not actor.actor.strip():
        return False, "缺少当前人类参与者身份。"
    if not is_human_role(config, actor):
        return False, "当前参与者不是 canonical policy 中的人类角色。"
    if actor.role not in obligation.verifier_roles:
        return False, "当前角色不在该项目要求的维护者检查权限范围内。"
    if operation not in config.permissions.get(actor.role, set()):
        return False, "当前角色没有执行该治理操作的权限。"
    if operation not in allowed_actions(
        config,
        state=case.state,
        role=actor.role,
    ):
        return False, "当前案例阶段不允许执行该治理操作。"
    if (
        obligation.obligation_id == "O-INDEPENDENT-REVIEW"
        and actor.role != "maintainer"
    ):
        return False, "该项目只允许具有独立检查权限的人类维护者处理。"
    if obligation.obligation_id == "O-INDEPENDENT-REVIEW":
        source_actors = {item.source_actor for item in case.evidence} | {
            item.actor for item in case.attestations
        }
        if actor.actor in source_actors:
            return False, "独立检查者不能是材料或负责人确认的原始参与者。"
    return True, None


def authorize_final_operation(
    *,
    config: VNextConfig,
    case: GovernanceCase,
    actor: ActorContext,
    operation: str,
) -> tuple[bool, str | None]:
    if not actor.actor.strip() or not is_human_role(config, actor):
        return False, "最终决定只允许 canonical policy 中的人类角色。"
    if actor.role != "maintainer":
        return False, "维护者检查权限不等于最终决定权限。"
    if operation not in config.permissions.get(actor.role, set()):
        return False, "当前角色没有该项最终决定权限。"
    if operation not in allowed_actions(
        config,
        state=case.state,
        role=actor.role,
    ):
        return False, "当前案例尚未进入支持该决定的阶段。"
    return True, None
