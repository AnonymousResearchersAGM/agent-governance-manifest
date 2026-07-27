"""Read-only reviewer handoff utilities derived from the guidance view."""

from __future__ import annotations

import json

from ..models import GovernanceCase
from .models import (
    GuidanceUtilityAction,
    RequirementComparison,
    ResponsibilityView,
    TraceReference,
)


def _trace_rows(
    rows: list[RequirementComparison],
) -> list[TraceReference]:
    result: list[TraceReference] = []
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        for trace in row.traceability:
            key = (trace.kind, trace.object_id, trace.relationship)
            if key not in seen:
                seen.add(key)
                result.append(trace)
    return result


def _row_line(row: RequirementComparison) -> str:
    scope = "、".join(row.affected_scope) or "当前贡献范围"
    return (
        f"- {row.display_name}：{row.material_status_label}；"
        f"{row.workflow_status_label}；范围：{scope}"
    )


def build_guidance_utilities(
    case: GovernanceCase,
    comparisons: list[RequirementComparison],
    responsibility: ResponsibilityView,
) -> list[GuidanceUtilityAction]:
    """Build immutable exports without changing the case or transition log."""
    blocking = [
        item for item in comparisons if item.currently_blocks_progression
    ]
    contributor_items = [
        item
        for item in comparisons
        if item.workflow_status
        in {"awaiting_contributor", "awaiting_attestation"}
        and item.material_status in {"missing", "stale", "invalid"}
    ]
    missing_output = (
        "\n".join(_row_line(item) for item in contributor_items)
        or "当前没有需要贡献侧补充或更新的材料。"
    )
    checklist = [
        "# 贡献者待办清单",
        "",
        f"案例：{case.id}",
        f"当前责任方：{responsibility.display_label}",
        f"原因：{responsibility.reason}",
        "",
        "## 待处理项",
        "",
        missing_output,
        "",
        "完成后请按当前 repair/提交范围交回；最终决定仍由人类维护者作出。",
    ]
    summary = [
        "# 维护者审核摘要",
        "",
        f"案例：{case.id}",
        f"当前状态：{case.state}",
        f"风险：{case.overall_risk_level}",
        f"当前责任方：{responsibility.display_label}",
        f"责任方依据：{responsibility.reason}",
        "",
        "## 阻断或待检查项",
        "",
        *([_row_line(item) for item in blocking] or ["- 当前没有阻断项。"]),
        "",
        "本摘要是治理状态说明，不是接受决定。",
    ]
    handoff = [
        f"案例 {case.id} 当前交给：{responsibility.display_label}。",
        responsibility.reason,
    ]
    if responsibility.blocking_items:
        handoff.append(
            "涉及：" + "、".join(responsibility.blocking_items) + "。"
        )
    if responsibility.next_handoff_roles:
        handoff.append(
            "完成后交给角色："
            + "、".join(responsibility.next_handoff_roles)
            + "。"
        )
    change_scope = json.dumps(
        {
            "case_id": case.id,
            "changed_files": case.changed_files,
            "matched_risk_rules": [
                {
                    "rule_id": item.rule_id,
                    "zone": item.zone,
                    "affected_paths": item.affected_paths,
                }
                for item in case.matched_rules
            ],
            "requirement_scopes": {
                item.obligation_id: item.affected_scope
                for item in comparisons
            },
        },
        ensure_ascii=False,
        indent=2,
    )
    return [
        GuidanceUtilityAction(
            action_id="copy_missing_requirements",
            label="复制缺失项清单",
            description="生成可直接交给贡献侧的缺失、过时或无效材料清单。",
            output_type="text/plain",
            output=missing_output,
            trace_refs=_trace_rows(contributor_items),
        ),
        GuidanceUtilityAction(
            action_id="export_contributor_checklist",
            label="导出贡献者待办清单",
            description="导出包含责任方、待处理项和范围的 Markdown 清单。",
            output_type="text/markdown",
            output="\n".join(checklist),
            trace_refs=_trace_rows(contributor_items),
        ),
        GuidanceUtilityAction(
            action_id="export_reviewer_summary",
            label="下载维护者摘要",
            description="导出当前风险、责任方和阻断项摘要，不作接受判断。",
            output_type="text/markdown",
            output="\n".join(summary),
            trace_refs=_trace_rows(comparisons),
        ),
        GuidanceUtilityAction(
            action_id="view_change_scope",
            label="查看变化范围",
            description="查看变更文件、匹配规则和各要求的影响范围。",
            output_type="application/json",
            output=change_scope,
            trace_refs=[
                TraceReference("matched_rule", item.id, "change_scope")
                for item in case.matched_rules
            ],
        ),
        GuidanceUtilityAction(
            action_id="copy_handoff_note",
            label="复制当前责任方说明",
            description="生成不改变案例状态的 handoff note。",
            output_type="text/plain",
            output="\n".join(handoff),
            trace_refs=_trace_rows(blocking or comparisons),
        ),
    ]


def utility_output(
    utilities: list[GuidanceUtilityAction],
    action_id: str,
) -> GuidanceUtilityAction:
    for item in utilities:
        if item.action_id == action_id:
            return item
    raise KeyError(action_id)
