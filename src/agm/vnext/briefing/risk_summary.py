"""Present the risk conclusion already recorded by the governance engine."""

from __future__ import annotations

from typing import Any

from ..config import VNextConfig
from ..models import GovernanceCase
from .models import RiskBrief


RISK_LABELS = {
    "low": "低",
    "medium": "中",
    "high": "高",
    "critical": "关键",
}

ZONE_LABELS = {
    "documentation": "文档与说明",
    "task_logic": "业务逻辑",
    "configuration": "配置与依赖",
    "test_strategy": "测试策略",
    "authentication": "登录与身份认证",
    "authorization": "权限控制",
    "project_governance": "项目治理规则",
    "governance_runtime": "治理执行逻辑",
    "unclassified_surface": "未分类项目范围",
}


def _policy_interactions(policy_snapshot: Any) -> dict[str, dict[str, Any]]:
    if isinstance(policy_snapshot, VNextConfig):
        return {
            str(item["id"]): item
            for item in policy_snapshot.interaction_rules
        }
    return {}


def compile_risk_brief(
    case: GovernanceCase,
    policy_snapshot: Any,
) -> RiskBrief:
    """Explain engine-produced matched rules; never resolve selectors here."""

    areas: list[str] = []
    reasons: list[str] = []
    refs: list[str] = []
    for rule in case.matched_rules:
        area = ZONE_LABELS.get(rule.zone, "项目风险范围")
        if area not in areas:
            areas.append(area)
        paths = "、".join(rule.affected_paths)
        if paths:
            reasons.append(f"{paths} 触发了“{area}”风险范围。")
        else:
            reasons.append(f"治理引擎已匹配“{area}”风险范围。")
        refs.append(f"{area}规则（风险级别：{RISK_LABELS.get(rule.risk_level, rule.risk_level)}）")

    interaction_map = _policy_interactions(policy_snapshot)
    interaction_ids = list(
        dict.fromkeys(
            interaction_id
            for obligation in case.obligations
            for interaction_id in obligation.interaction_ids
        )
    )
    interaction_labels = {
        "authentication-configuration": (
            "认证行为与配置同时变化，组合影响需要独立维护者检查。"
        ),
        "governance-self-modification": (
            "治理规则与治理执行逻辑同时变化，形成自修改联动，"
            "需要职责分离的独立检查。"
        ),
    }
    effects = []
    for interaction_id in interaction_ids:
        configured = interaction_map.get(interaction_id, {})
        effects.append(
            interaction_labels.get(
                interaction_id,
                str(configured.get("description") or "多项风险范围发生联动。"),
            )
        )
    independent = any(
        item.obligation_id == "O-INDEPENDENT-REVIEW"
        for item in case.obligations
    )
    if independent and not effects:
        effects.append("当前治理结论要求由独立维护者进行检查。")
    return RiskBrief(
        overall_level=case.overall_risk_level,
        display_level=RISK_LABELS.get(
            case.overall_risk_level, case.overall_risk_level
        ),
        triggered_risk_areas=tuple(areas),
        plain_reasons=tuple(reasons),
        matched_rule_refs=tuple(refs),
        interaction_effects=tuple(effects),
        requires_independent_review=independent,
    )
