"""Deterministic, read-only human-readable projections for structured artifacts."""
from __future__ import annotations

import html
import json
from dataclasses import dataclass
from typing import Any

import yaml

from ..models import fingerprint

PROJECTION_TEMPLATE_VERSION = "agm.structured-artifact-projection/v1"

STRUCTURED_ARTIFACT_TYPES = {
    "change_summary",
    "changed_files",
    "rationale",
    "known_limitations",
    "impact_statement",
    "test_result",
    "agent_activity",
    "contribution_declaration",
    "human_confirmation",
    "repair_record",
    "final_receipt",
}

TEMPLATES: dict[str, tuple[tuple[str, tuple[tuple[str, str], ...]], ...]] = {
    "change_summary": (
        ("修改内容", (("summary", "修改说明"), ("behavioral_change", "行为变化"))),
        ("影响文件", (("affected_components", "影响组件"), ("affected_files", "影响文件"))),
        ("修改理由", (("rationale", "修改理由"),)),
        ("已知限制", (("known_limitations", "已知限制"),)),
        ("当前版本绑定", (("head_commit_sha", "对应版本"), ("contribution_fingerprint", "当前 contribution 绑定"))),
    ),
    "changed_files": (
        ("文件路径", (("files", "文件"),)),
        ("修改类型", (("change_type", "修改类型"),)),
        ("修改范围", (("affected_scope", "修改范围"),)),
        ("当前 contribution 绑定", (("contribution_fingerprint", "Contribution"), ("head_commit_sha", "对应版本"))),
    ),
    "rationale": (
        ("修改理由", (("reason", "原因"), ("intended_outcome", "预期结果"))),
        ("当前版本绑定", (("contribution_fingerprint", "Contribution"), ("head_commit_sha", "对应版本"))),
    ),
    "known_limitations": (
        ("已知限制", (("limitations", "限制"), ("no_known_limitations", "无已知限制"))),
        ("声明信息", (("declared_by", "声明人"),)),
        ("当前版本绑定", (("contribution_fingerprint", "Contribution"), ("head_commit_sha", "对应版本"))),
    ),
    "impact_statement": (
        ("影响说明", (("security_impact", "安全影响"), ("compatibility_impact", "兼容性影响"), ("data_impact", "数据影响"), ("operational_impact", "运行影响"))),
        ("当前版本绑定", (("contribution_fingerprint", "Contribution"), ("head_commit_sha", "对应版本"))),
    ),
    "test_result": (
        ("测试命令", (("command", "命令"),)),
        ("通过/失败结果", (("result_summary", "结果"), ("exit_code", "退出码"), ("tests_passed", "通过"), ("tests_failed", "失败"))),
        ("测试覆盖范围", (("affected_scope", "覆盖范围"), ("environment", "环境"))),
        ("对应 contribution/version", (("contribution_fingerprint", "Contribution"), ("head_commit_sha", "对应版本"))),
        ("未执行的测试", (("tests_not_run", "未执行测试"),)),
        ("限制说明", (("limitations", "限制"),)),
    ),
    "agent_activity": (
        ("是否使用编码助手", (("agent_type", "助手类型"),)),
        ("使用的工具", (("other_agents_or_tools_used", "是否使用其他工具"), ("tools_used", "工具"))),
        ("活动覆盖范围", (("activity_scope", "覆盖范围"), ("files_modified", "修改文件"))),
        ("完成的工作", (("task_summary", "任务摘要"), ("commands_executed", "运行命令"), ("tests_executed", "运行测试"))),
        ("未完成或未验证的工作", (("unfinished_work", "未完成工作"), ("unverified_work", "未验证工作"))),
        ("当前版本绑定", (("contribution_fingerprint", "Contribution"), ("head_commit_sha", "对应版本"))),
    ),
    "contribution_declaration": (
        ("贡献者声明", (("statement", "声明"), ("declared_by", "声明人"))),
        ("声明覆盖范围", (("declaration_scope", "覆盖范围"),)),
        ("是否使用其他工具", (("other_agents_or_tools_used", "使用其他工具"), ("declared_tools", "声明工具"))),
        ("已知限制", (("known_limitations", "已知限制"),)),
        ("声明对应版本", (("contribution_fingerprint", "Contribution"), ("head_commit_sha", "对应版本"))),
    ),
    "human_confirmation": (
        ("贡献者确认", (("statement", "确认内容"), ("confirmed_by", "确认人"), ("confirmed_at", "确认时间"))),
        ("确认覆盖范围", (("confirmation_scope", "覆盖范围"),)),
        ("确认对应版本", (("contribution_fingerprint", "Contribution"), ("head_commit_sha", "对应版本"))),
    ),
    "repair_record": (
        ("原问题", (("original_issue", "原问题"), ("finding", "原问题"))),
        ("修复内容", (("repair", "修复内容"), ("changes", "修复内容"))),
        ("修复后版本", (("head_commit_sha", "修复后版本"), ("contribution_fingerprint", "Contribution"))),
        ("重新验证结果", (("revalidation_result", "重新验证结果"),)),
    ),
    "final_receipt": (
        ("AGM 建议", (("agm_final_recommendation", "建议"),)),
        ("建议依据", (("risk_summary", "风险摘要"), ("agent_involvement", "助手参与"), ("contributor_self_review_status", "贡献者检查"), ("maintainer_review_status", "维护者检查"))),
        ("package/contribution/policy 绑定", (("evidence_package_digest", "Package"), ("contribution_fingerprint", "Contribution"), ("policy_fingerprint", "Policy"))),
        ("人工决定状态", (("final_decision_id", "人工决定记录"),)),
        ("平台边界说明", (("host_platform_status", "代码托管平台状态"),)),
    ),
}

TECHNICAL_KEYS = {
    "schema_version",
    "artifact_type",
    "observed_at",
    "source_tool",
    "obligation_refs",
    "case_id",
    "policy_fingerprint",
}


class _IndentedSafeDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False):
        return super().increase_indent(flow, False)


@dataclass(frozen=True)
class StructuredArtifactProjection:
    artifact_id: str
    artifact_type: str
    source_digest: str
    package_digest: str
    contribution_fingerprint: str
    source_format: str
    raw_text: str
    formatted_text: str
    markdown: str | None
    rendered_html: str | None
    parse_error: str | None
    template_version: str = PROJECTION_TEMPLATE_VERSION

    @property
    def readable_available(self) -> bool:
        return self.markdown is not None and self.rendered_html is not None


def _source_format(media_type: str, content: str, artifact_type: str) -> str | None:
    lowered = media_type.lower()
    if "yaml" in lowered or "yml" in lowered:
        return "yaml"
    if "json" in lowered:
        return "json"
    if artifact_type in STRUCTURED_ARTIFACT_TYPES:
        stripped = content.lstrip()
        return "json" if stripped.startswith(("{", "[")) else "yaml"
    return None


def _parse(content: str, source_format: str) -> Any:
    if source_format == "json":
        value = json.loads(content)
    else:
        value = yaml.safe_load(content)
    _validate_structure(value)
    return value


def _validate_structure(value: Any) -> None:
    """Bound recursive work and reject cyclic/constructor-like YAML graphs."""
    active: set[int] = set()
    visited = 0

    def visit(item: Any, depth: int) -> None:
        nonlocal visited
        visited += 1
        if depth > 64 or visited > 10000:
            raise ValueError("structured artifact exceeds projection limits")
        if isinstance(item, (dict, list)):
            identity = id(item)
            if identity in active:
                raise ValueError("structured artifact contains a recursive alias")
            active.add(identity)
            if isinstance(item, dict):
                for key, nested in item.items():
                    if not isinstance(key, (str, int, float, bool)) and key is not None:
                        raise ValueError("structured artifact has an unsupported mapping key")
                    visit(nested, depth + 1)
            else:
                for nested in item:
                    visit(nested, depth + 1)
            active.remove(identity)
        elif not isinstance(item, (str, int, float, bool)) and item is not None:
            raise ValueError("structured artifact contains an unsupported value")

    visit(value, 0)


def _pretty(value: Any, source_format: str) -> str:
    if source_format == "json":
        return json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    return yaml.dump(
        value,
        Dumper=_IndentedSafeDumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        indent=2,
    )


def _markdown_text(value: Any) -> str:
    text = str(value).replace("\\", "\\\\").replace("`", "\\`")
    return text.replace("\r", "\\r").replace("\n", "  \n")


def _value_lines(label: str, value: Any, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    if isinstance(value, dict):
        lines = [f"{prefix}- **{_markdown_text(label)}:**"]
        for key, nested in value.items():
            lines.extend(_value_lines(str(key), nested, indent + 1))
        return lines
    if isinstance(value, list):
        lines = [f"{prefix}- **{_markdown_text(label)}:**"]
        if not value:
            return [lines[0] + " []"]
        for item in value:
            if isinstance(item, (dict, list)):
                lines.extend(_value_lines("项目", item, indent + 1))
            else:
                lines.append(f"{prefix}  - {_markdown_text(item)}")
        return lines
    rendered = "null" if value is None else (
        "true" if value is True else "false" if value is False else _markdown_text(value)
    )
    return [f"{prefix}- **{_markdown_text(label)}:** {rendered}"]


def _build_markdown(
    value: Any,
    *,
    title: str,
    artifact_type: str,
    artifact_id: str,
    source_digest: str,
) -> str:
    lines = [
        f"# {_markdown_text(title)}",
        "",
        "Derived human-readable projection",
        "",
        f"- **Artifact type:** {_markdown_text(artifact_type)}",
        "",
        "此可读视图由当前结构化材料自动生成，不是独立证据。",
    ]
    used: set[str] = set()
    if isinstance(value, dict) and artifact_type in TEMPLATES:
        for heading, fields in TEMPLATES[artifact_type]:
            present = [(key, label) for key, label in fields if key in value]
            if not present:
                continue
            lines.extend(("", f"## {heading}", ""))
            for key, label in present:
                used.add(key)
                lines.extend(_value_lines(label, value[key]))
    else:
        lines.extend(("", "## 材料内容", ""))
        if isinstance(value, dict):
            for key, nested in value.items():
                used.add(str(key))
                lines.extend(_value_lines(str(key), nested))
        elif isinstance(value, list):
            lines.extend(_value_lines("列表", value))
        else:
            lines.extend(_value_lines("值", value))

    technical = (
        [(key, value[key]) for key in value if key not in used]
        if isinstance(value, dict)
        else []
    )
    lines.extend(("", "## 技术详情", ""))
    for key, nested in technical:
        lines.extend(_value_lines(key, nested))
    lines.extend(
        (
            f"- **Source artifact ID:** {_markdown_text(artifact_id)}",
            f"- **Source digest:** {_markdown_text(source_digest)}",
            f"- **Projection template version:** {PROJECTION_TEMPLATE_VERSION}",
        )
    )
    return "\n".join(lines) + "\n"


def render_safe_markdown(markdown: str) -> str:
    """Render only the deterministic Markdown subset emitted above."""
    blocks: list[str] = []
    list_open = False
    details_open = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line:
            if list_open:
                blocks.append("</ul>")
                list_open = False
            continue
        if line == "## 技术详情":
            if list_open:
                blocks.append("</ul>")
                list_open = False
            blocks.append("<details class=\"technical\"><summary>技术详情</summary>")
            details_open = True
            continue
        if line.startswith("# "):
            blocks.append(f"<h1>{html.escape(line[2:])}</h1>")
            continue
        if line.startswith("## "):
            if list_open:
                blocks.append("</ul>")
                list_open = False
            blocks.append(f"<h2>{html.escape(line[3:])}</h2>")
            continue
        stripped = line.lstrip()
        if stripped.startswith("- "):
            if not list_open:
                blocks.append("<ul>")
                list_open = True
            item = stripped[2:]
            if item.startswith("**") and ":**" in item:
                label, _, rest = item[2:].partition(":**")
                body = f"<strong>{html.escape(label)}:</strong>{html.escape(rest)}"
            else:
                body = html.escape(item)
            depth = (len(line) - len(stripped)) // 2
            blocks.append(f'<li class="depth-{min(depth, 6)}">{body}</li>')
            continue
        if list_open:
            blocks.append("</ul>")
            list_open = False
        marker = ' class="projection-marker"' if line == "Derived human-readable projection" else ""
        blocks.append(f"<p{marker}>{html.escape(line)}</p>")
    if list_open:
        blocks.append("</ul>")
    if details_open:
        blocks.append("</details>")
    return "".join(blocks)


def project_structured_artifact(
    *,
    metadata: dict[str, Any],
    content: str,
    package_digest: str,
) -> StructuredArtifactProjection | None:
    artifact_type = str(metadata.get("artifact_type") or "structured_artifact")
    source_format = _source_format(str(metadata.get("media_type") or ""), content, artifact_type)
    if source_format is None:
        return None
    artifact_id = str(metadata.get("artifact_id") or "")
    source_digest = str(metadata.get("content_digest") or fingerprint(content))
    contribution = str(metadata.get("contribution_fingerprint") or "")
    try:
        value = _parse(content, source_format)
        formatted = _pretty(value, source_format)
        markdown = _build_markdown(
            value,
            title=str(metadata.get("title") or artifact_type),
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            source_digest=source_digest,
        )
        rendered = render_safe_markdown(markdown)
        error = None
    except (json.JSONDecodeError, yaml.YAMLError, TypeError, ValueError) as exc:
        formatted = content
        markdown = rendered = None
        error = f"{type(exc).__name__}: structured content could not be safely parsed"
    return StructuredArtifactProjection(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        source_digest=source_digest,
        package_digest=package_digest,
        contribution_fingerprint=contribution,
        source_format=source_format,
        raw_text=content,
        formatted_text=formatted,
        markdown=markdown,
        rendered_html=rendered,
        parse_error=error,
    )
