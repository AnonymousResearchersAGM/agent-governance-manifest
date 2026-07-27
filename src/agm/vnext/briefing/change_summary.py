"""Compile changed paths and declarations into a provenance-aware summary."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from pathlib import PurePosixPath
from typing import Any

from ..models import GovernanceCase
from .models import ContributionBrief


def normalize_contribution(contribution: Any) -> dict[str, Any]:
    """Normalize optional presentation input without changing governance data."""

    if contribution is None:
        return {}
    if isinstance(contribution, Mapping):
        return dict(contribution)
    if is_dataclass(contribution):
        return asdict(contribution)
    if hasattr(contribution, "to_dict"):
        value = contribution.to_dict()
        return dict(value) if isinstance(value, Mapping) else {}
    return {}


def latest_evidence_value(
    case: GovernanceCase,
    evidence_type: str,
) -> tuple[Any, str] | tuple[None, str]:
    """Return the latest usable declaration and its source description."""

    usable_states = {"valid", "verified"}
    candidates = [
        item
        for item in case.evidence
        if item.evidence_type == evidence_type
        and item.validity_state in usable_states
    ]
    if not candidates:
        return None, ""
    item = candidates[-1]
    source = f"{item.source_actor}"
    if item.source_tool:
        source += f"（通过 {item.source_tool} 记录）"
    return item.value, source


def _classify_path(path: str) -> tuple[str, str]:
    normalized = path.replace("\\", "/")
    lowered = normalized.lower()
    name = PurePosixPath(normalized).name.lower()
    if (
        normalized.startswith(".agm/")
        or normalized in {"AGENTS.md", "CLAUDE.md"}
        or normalized.startswith("skills/")
        or normalized.startswith("src/agm/")
    ):
        return "governance", "AGM 治理与执行支持"
    if (
        normalized.startswith("tests/")
        or "/tests/" in lowered
        or name.startswith("test_")
        or name.endswith("_test.py")
    ):
        return "tests", "测试与验证"
    if (
        "/auth" in lowered
        or name.startswith("auth.")
        or "token" in lowered
        or "permission" in lowered
        or "security" in lowered
    ):
        return "security", "用户认证与权限控制"
    if (
        name in {"requirements.txt", "pyproject.toml", "package.json"}
        or "config" in name
        or normalized.startswith(".github/")
        or "deployment" in lowered
    ):
        return "configuration", "项目配置与依赖"
    if normalized.startswith("docs/") or name in {"readme.md", "citation.cff"}:
        return "documentation", "文档与说明"
    if normalized.startswith("demo_app/"):
        return "application", "应用行为"
    if normalized.startswith("src/"):
        return "runtime", "运行时代码"
    return "other", "其他项目内容"


def _path_phrase(path: str, category: str) -> str:
    labels = {
        "governance": "更新治理或治理运行时文件",
        "security": "修改登录、认证或权限相关文件",
        "configuration": "调整配置、依赖或部署相关文件",
        "tests": "更新测试或验证文件",
        "documentation": "更新项目文档",
        "application": "修改应用代码",
        "runtime": "修改运行时代码",
        "other": "修改项目文件",
    }
    return f"{labels[category]}：{path}"


def _behavioral_impacts(
    case: GovernanceCase,
    categories: set[str],
) -> tuple[str, ...]:
    impacts: list[str] = []
    zone_labels = {
        "authentication": "可能影响登录与身份认证路径",
        "authorization": "可能影响权限判断边界",
        "configuration": "可能影响配置或部署兼容性",
        "test_strategy": "可能影响测试策略与验证覆盖",
        "project_governance": "可能影响项目治理要求",
        "governance_runtime": "可能影响治理规则的执行结果",
        "task_logic": "可能影响应用业务逻辑",
        "documentation": "主要影响文档和说明",
    }
    for rule in case.matched_rules:
        label = zone_labels.get(rule.zone)
        if label and label not in impacts:
            impacts.append(label)
    target_labels = {
        "authentication": "贡献者声明涉及身份认证语义",
        "authorization": "贡献者声明涉及权限控制语义",
        "task_logic": "贡献者声明涉及业务逻辑语义",
    }
    for target in case.semantic_targets:
        label = target_labels.get(target)
        if label and label not in impacts:
            impacts.append(label)
    if not impacts and "documentation" in categories:
        impacts.append("主要影响文档和说明")
    return tuple(impacts)


def compile_contribution_brief(
    case: GovernanceCase,
    contribution: Any,
) -> ContributionBrief:
    """Summarize recorded paths without claiming code-level semantic proof."""

    context = normalize_contribution(contribution)
    declaration = context.get("contributor_declaration", {})
    if not isinstance(declaration, Mapping):
        declaration = {}
    declared_summary, summary_source = latest_evidence_value(
        case, "contribution_summary"
    )
    if declared_summary is None:
        latest_attempt = next(
            (
                repair.attempts[-1]
                for repair in reversed(case.repair_requests)
                if repair.attempts
                and str(repair.attempts[-1].get("summary", "")).strip()
            ),
            None,
        )
        if latest_attempt:
            declared_summary = latest_attempt["summary"]
            summary_source = "贡献侧重新提交记录"
    if declaration.get("summary"):
        declared_summary = declaration["summary"]
        summary_source = str(
            declaration.get("source", "贡献者提供的 contribution 输入")
        )

    categorized = [
        (path, *_classify_path(path)) for path in case.changed_files
    ]
    categories = {category for _, category, _ in categorized}
    components = tuple(
        dict.fromkeys(component for _, _, component in categorized)
    )
    inferred_phrases = tuple(
        _path_phrase(path, category)
        for path, category, _ in categorized
    )
    system_inferred_summary = (
        "；".join(inferred_phrases)
        if inferred_phrases
        else "当前案例没有记录变更文件。"
    )
    plain_summary = (
        str(declared_summary)
        if declared_summary is not None
        else system_inferred_summary
    )
    source = (
        f"贡献者声明，来源：{summary_source}"
        if declared_summary is not None
        else "系统根据已记录的变更路径归纳"
    )
    agent_used = (
        case.autonomy_profile != "human_direct"
        or any(
            item.obligation_id == "O-AGENT-SCOPE"
            for item in case.obligations
        )
    )
    claims = []
    for key, label in (
        ("behavioral_impacts", "贡献者声明的行为影响"),
        ("security_sensitive_changes", "贡献者声明的安全影响"),
        ("configuration_changes", "贡献者声明的配置影响"),
        ("governance_changes", "贡献者声明的治理影响"),
    ):
        value = declaration.get(key)
        if isinstance(value, str) and value.strip():
            claims.append(f"{label}：{value.strip()}")
        elif isinstance(value, list):
            claims.extend(
                f"{label}：{str(item).strip()}"
                for item in value
                if str(item).strip()
            )
    return ContributionBrief(
        title=str(context.get("title") or "本次贡献"),
        plain_summary=plain_summary,
        changed_files=tuple(case.changed_files),
        changed_components=components,
        behavioral_impacts=_behavioral_impacts(case, categories),
        security_sensitive_changes=tuple(
            _path_phrase(path, category)
            for path, category, _ in categorized
            if category == "security"
        ),
        configuration_changes=tuple(
            _path_phrase(path, category)
            for path, category, _ in categorized
            if category == "configuration"
        ),
        governance_changes=tuple(
            _path_phrase(path, category)
            for path, category, _ in categorized
            if category == "governance"
        ),
        agent_involvement=(
            "治理案例记录为智能体参与路径"
            if agent_used
            else "治理案例未声明智能体参与"
        ),
        summary_source=source,
        system_inferred_summary=system_inferred_summary,
        inference_limitations=(
            "系统归纳只依据文件路径、已匹配风险区域和明确声明，"
            "不代表系统已经证明代码的真实语义或行为。"
        ),
        contributor_claims=tuple(claims),
    )
