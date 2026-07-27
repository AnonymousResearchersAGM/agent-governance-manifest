"""Compile agent declarations and accountable-human attestations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..config import VNextConfig
from ..evidence import evidence_set_fingerprint
from ..models import GovernanceCase
from .change_summary import latest_evidence_value, normalize_contribution
from .models import ContributorAccountabilityBrief


PROFILE_VALUE_LABELS = {
    "workspace": "可修改工作区文件并提供命令执行记录",
    "task-bounded": "行动范围限制在本次任务内",
    "project-bounded": "行动范围限制在本项目内",
    "session": "仅在当前工作会话内持续",
    "extended": "可以在较长任务周期内持续",
    "none": "无持续性智能体会话",
}


def _as_lines(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, Mapping):
        return [
            f"{key}：{item}"
            for key, item in value.items()
            if str(item).strip()
        ]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value)]


def _delegation_claim(
    value: Any,
    declaration: Mapping[str, Any],
) -> bool | None:
    explicit = declaration.get("delegation_detected")
    if isinstance(explicit, bool):
        return explicit
    text = " ".join(_as_lines(value)).lower()
    if not text:
        return None
    negatives = (
        "no delegation",
        "no undeclared delegation",
        "not delegated",
        "未委派",
        "无委派",
        "没有继续委派",
    )
    if any(item in text for item in negatives):
        return False
    if "delegat" in text or "委派" in text or "子智能体" in text:
        return True
    return None


def compile_accountability_brief(
    case: GovernanceCase,
    policy_snapshot: Any,
    contribution: Any,
) -> ContributorAccountabilityBrief:
    """Separate recorded behavior, declarations, attestation, and inference."""

    context = normalize_contribution(contribution)
    declaration = context.get("contributor_declaration", {})
    if not isinstance(declaration, Mapping):
        declaration = {}
    observations = context.get("system_observations", {})
    if not isinstance(observations, Mapping):
        observations = {}

    agent_used = bool(
        declaration.get("agent_used")
        if isinstance(declaration.get("agent_used"), bool)
        else (
            case.autonomy_profile != "human_direct"
            or any(
                item.obligation_id == "O-AGENT-SCOPE"
                for item in case.obligations
            )
            or any(
                item.actor_role == "contributor_agent"
                for item in case.attempted_operations
            )
        )
    )
    profile: Mapping[str, Any] = {}
    if isinstance(policy_snapshot, VNextConfig):
        profile = policy_snapshot.autonomy_profiles.get(
            case.autonomy_profile, {}
        )
    capabilities = []
    if agent_used:
        permissions = str(profile.get("permissions", "")).strip()
        action_scope = str(profile.get("action_scope", "")).strip()
        persistence = str(profile.get("persistence", "")).strip()
        if permissions:
            capabilities.append(
                "权限范围："
                + PROFILE_VALUE_LABELS.get(permissions, "已按项目配置记录")
            )
        if action_scope:
            capabilities.append(
                "行动范围："
                + PROFILE_VALUE_LABELS.get(
                    action_scope, "已按项目配置记录"
                )
            )
        if persistence:
            capabilities.append(
                "持续方式："
                + PROFILE_VALUE_LABELS.get(
                    persistence, "已按项目配置记录"
                )
            )
        capabilities.extend(_as_lines(declaration.get("agent_capabilities")))

    scope_value, scope_source = latest_evidence_value(
        case, "agent_action_scope"
    )
    if declaration.get("agent_actions"):
        declared_actions = _as_lines(declaration.get("agent_actions"))
    else:
        declared_actions = _as_lines(scope_value)
    declared_facts = [
        f"智能体或贡献者声明：{item}" for item in declared_actions
    ]
    if agent_used and not declared_facts:
        declared_facts.append("尚未提供智能体行动与委派声明。")

    system_observations = []
    submitted = [
        item
        for item in case.evidence
        if agent_used and "agent" in item.source_actor.lower()
    ]
    denied_agent_actions = [
        item
        for item in case.attempted_operations
        if item.actor_role == "contributor_agent"
    ]
    if denied_agent_actions:
        system_observations.append(
            "系统记录到贡献侧智能体尝试了维护者侧操作，"
            "该操作已被权限边界拒绝。"
        )
    if submitted:
        system_observations.append(
            f"系统记录到智能体身份提交了 {len(submitted)} 份治理材料。"
        )
    commands = [item for item in submitted if item.command]
    if commands:
        system_observations.append(
            f"系统记录到智能体身份提供了 {len(commands)} 条命令执行记录。"
        )
    system_observations.extend(_as_lines(observations.get("agent_actions")))
    agent_actions = tuple(
        system_observations
        + (
            ["另有贡献者声明，见下方“声明事实”分组。"]
            if declared_facts
            else []
        )
    )

    confirmed = [
        item
        for item in case.attestations
        if item.status == "confirmed"
    ]
    current_set = evidence_set_fingerprint(case.evidence)
    current = [
        item
        for item in confirmed
        if item.policy_fingerprint
        == case.policy_snapshot.policy_fingerprint
        and (
            (
                item.contribution_fingerprint
                == case.contribution_fingerprint
                and item.evidence_set_fingerprint == current_set
            )
            or (
                item.retained_for_contribution_fingerprint
                == case.contribution_fingerprint
                and bool(item.retention_reason)
            )
        )
    ]
    latest = (current or confirmed or case.attestations)[-1] if (
        current or confirmed or case.attestations
    ) else None
    if current:
        attestation_status = "已确认当前版本"
        binding = "绑定当前版本"
    elif confirmed:
        attestation_status = "存在确认，但未绑定当前版本"
        binding = "旧版本或旧材料集合"
    elif case.attestations:
        attestation_status = "负责人确认已失效"
        binding = "无有效版本绑定"
    else:
        attestation_status = (
            "尚未确认"
            if any(item.type == "human_attestation" for item in case.obligations)
            else "当前风险路径不要求额外确认"
        )
        binding = "不适用" if latest is None else "无有效版本绑定"
    human_confirmed = []
    if latest and latest.status == "confirmed":
        human_confirmed.append(
            "人类负责人确认审阅了明确列出的当前范围。"
        )
        human_confirmed.append(
            f"确认范围包含当前记录的 {len(latest.reviewed_scope)} 个文件或审阅范围。"
        )
        if latest.reservations:
            human_confirmed.append(
                "保留意见：" + "；".join(latest.reservations)
            )

    declaration_status = (
        "provided"
        if scope_value is not None or declared_actions
        else ("missing" if agent_used else "not_required")
    )
    declaration_source = (
        "贡献侧提供的智能体行动声明"
        if declaration.get("source")
        else (
            "治理材料中的智能体行动与委派声明"
            if scope_source
            else ("未记录" if agent_used else "当前不要求")
        )
    )
    inferences = [
        "能力范围来自治理配置或贡献者声明，不证明每项能力实际被使用。",
        "AGM 不把智能体自述当作系统观察事实，也不检测未披露的智能体使用。",
    ]
    return ContributorAccountabilityBrief(
        agent_used=agent_used,
        agent_capabilities=tuple(dict.fromkeys(capabilities)),
        agent_actions=agent_actions,
        delegation_detected=_delegation_claim(scope_value, declaration),
        declaration_source=declaration_source,
        declaration_status=declaration_status,
        accountable_human="人类负责人" if latest else None,
        attestation_status=attestation_status,
        attestation_scope=tuple(latest.reviewed_scope) if latest else (),
        attestation_version_binding=binding,
        system_observations=tuple(system_observations),
        declared_facts=tuple(declared_facts),
        human_confirmed_facts=tuple(human_confirmed),
        unverified_inferences=tuple(inferences),
    )
