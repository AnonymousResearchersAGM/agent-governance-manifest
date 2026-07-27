"""Structured Chinese-first presentation for reviewer-facing reasons."""

from __future__ import annotations

from collections.abc import Iterable

from .models import GuidanceReasonPresentation, TraceReference


UNKNOWN_REASON_FALLBACK = "系统记录了一项需要维护者查看的说明。"

# Presentation metadata only.  Canonical policy and source records remain
# untouched, and the English input is always retained in the returned record.
REASON_PRESENTATIONS = {
    "material_scope_change": (
        "代码范围发生实质变化后，需要更新修改说明。"
    ),
    "partial_affected_scope": (
        "本次变化只影响列出的材料；其他材料仍然有效。"
    ),
    "wording_only_clarification": (
        "本次只澄清文字表述，不改变贡献行为。"
    ),
    "agent_delegation_clarification": (
        "只需澄清智能体行动、权限和继续委派的范围。"
    ),
    "retained_unaffected_evidence": (
        "未受本次变化影响的材料继续有效，无需重复提交。"
    ),
    "invalidated_attestation": (
        "旧的负责人确认已失效，需要对当前版本和范围重新确认。"
    ),
    "unauthorized_operation": (
        "系统拒绝了这次操作，因为当前角色没有执行该操作所需的权限。"
    ),
    "policy_migration_warning": (
        "案例记录的项目规则版本与当前版本不同；系统不会静默迁移。"
    ),
    "lightweight_path": (
        "本次未触发完整治理流程，只需完成轻量审核要求。"
    ),
    "no_package": (
        "本次不要求完整 AGM 材料包；这不是失败，也不能据此判断贡献者身份。"
    ),
    "evidence_invalid": (
        "现有材料不能支持当前修改，需要更正或替换。"
    ),
    "evidence_rejected": (
        "维护者已拒绝这份材料，需要按指定范围更正。"
    ),
    "attestation_declined": (
        "负责人没有确认当前范围，需要先处理其说明。"
    ),
    "attestation_correction_requested": (
        "负责人要求先更正指定范围，再重新确认。"
    ),
    "clarification_requested": (
        "维护者要求补充说明指定范围。"
    ),
    "policy_conflict": (
        "项目规则之间存在冲突，需要有权限的角色处理。"
    ),
    "maintainer_requested_changes": (
        "人类维护者要求修改指定范围后再继续。"
    ),
    "repair_required": (
        "维护者要求更正指定范围后再重新检查。"
    ),
}


def present_reason(
    *,
    reason_code: str | None,
    source_english: str | None,
    trace_refs: Iterable[TraceReference] = (),
) -> GuidanceReasonPresentation:
    """Return Chinese primary text plus complete source and trace metadata."""

    display = REASON_PRESENTATIONS.get(
        reason_code or "",
        UNKNOWN_REASON_FALLBACK,
    )
    return GuidanceReasonPresentation(
        reason_code=reason_code,
        display_plain=display,
        source_english=source_english,
        source_code=reason_code,
        trace_refs=list(trace_refs),
    )
