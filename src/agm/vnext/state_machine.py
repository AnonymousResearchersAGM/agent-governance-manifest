"""Authority-typed state transitions for Governance Cases."""

from __future__ import annotations

from typing import Any

from .config import VNextConfig
from .models import GovernanceCase, StateTransition, VNextError, new_id, utc_now


def authorize(config: VNextConfig, *, role: str, action: str) -> None:
    if role not in config.roles:
        raise VNextError(f"Unknown actor role: {role}")
    if action not in config.permissions.get(role, set()):
        raise VNextError(f"Role {role} is not authorized for action {action}")


def allowed_actions(
    config: VNextConfig,
    *,
    state: str,
    role: str | None = None,
) -> list[str]:
    result = []
    for item in config.state_machine["transitions"]:
        if state not in item["from"]:
            continue
        if role is not None and role not in item["roles"]:
            continue
        result.append(item["action"])
    return sorted(set(result))


def transition_case(
    config: VNextConfig,
    case: GovernanceCase,
    *,
    action: str,
    actor: str,
    role: str,
    reason: str,
    related_object_ids: list[str] | None = None,
    timestamp: str | None = None,
) -> StateTransition:
    if not actor.strip():
        raise VNextError("State transition actor is required")
    if not reason.strip():
        raise VNextError("State transition reason is required")
    authorize(config, role=role, action=action)
    candidates = [
        item
        for item in config.state_machine["transitions"]
        if item["action"] == action and case.state in item["from"]
    ]
    if not candidates:
        raise VNextError(
            f"Action {action} is not valid from case state {case.state}"
        )
    transition_definition: dict[str, Any] = candidates[0]
    if role not in transition_definition["roles"]:
        raise VNextError(
            f"Role {role} cannot perform {action} from state {case.state}"
        )
    if case.state in set(config.state_machine["terminal_states"]):
        raise VNextError(f"Terminal case state {case.state} cannot transition")
    source_state = case.state
    target_state = transition_definition["to"]
    occurred_at = timestamp or utc_now()
    transition = StateTransition(
        id=new_id("transition"),
        case_id=case.id,
        actor=actor,
        role=role,
        source_state=source_state,
        target_state=target_state,
        action=action,
        reason=reason,
        related_object_ids=list(related_object_ids or []),
        timestamp=occurred_at,
    )
    case.state = target_state
    case.updated_at = occurred_at
    return transition
