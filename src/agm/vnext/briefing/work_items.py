"""Compile business-level work ownership from existing briefing facts."""

from __future__ import annotations

from .models import (
    AutomaticCheckResult,
    HumanJudgmentItem,
    NextStepBrief,
    RequirementBrief,
    WorkItemSummary,
    WorkOwner,
)


def compile_work_items(
    requirements: RequirementBrief,
    automatic_checks: tuple[AutomaticCheckResult, ...],
    judgments: tuple[HumanJudgmentItem, ...],
    next_step: NextStepBrief,
) -> tuple[WorkItemSummary, ...]:
    """Expose owners without creating obligations, findings, or new work."""

    items: list[WorkItemSummary] = []
    include_requirement_work = (
        next_step.status != "policy_migration_attention"
    )
    for requirement in requirements.items:
        if not include_requirement_work:
            continue
        if requirement.owner not in {
            WorkOwner.CONTRIBUTION_SIDE,
            WorkOwner.ACCOUNTABLE_HUMAN,
        }:
            continue
        items.append(
            WorkItemSummary(
                owner=requirement.owner,
                display_title=requirement.display_title,
                plain_explanation=requirement.plain_status,
                blocking=requirement.blocking,
                system_handled=False,
                requirement_refs=(requirement.requirement_key,),
                trace_refs=requirement.trace_refs,
            )
        )

    for judgment in judgments:
        items.append(
            WorkItemSummary(
                owner=WorkOwner.MAINTAINER,
                display_title=judgment.display_title,
                plain_explanation=judgment.why_human_is_needed,
                blocking=judgment.blocking,
                system_handled=False,
                requirement_refs=judgment.requirement_refs,
                trace_refs=judgment.trace_refs,
            )
        )

    for check in automatic_checks:
        if not check.system_handled:
            continue
        items.append(
            WorkItemSummary(
                owner=WorkOwner.SYSTEM,
                display_title=check.display_title,
                plain_explanation=check.plain_result,
                blocking=False,
                system_handled=True,
                requirement_refs=check.requirement_refs,
                trace_refs=check.trace_refs,
            )
        )

    if next_step.owner == WorkOwner.FINAL_DECISION_AUTHORITY:
        items.append(
            WorkItemSummary(
                owner=WorkOwner.FINAL_DECISION_AUTHORITY,
                display_title=next_step.display_title,
                plain_explanation=next_step.plain_explanation,
                blocking=False,
                system_handled=False,
            )
        )
    elif next_step.status == "policy_migration_attention":
        items.append(
            WorkItemSummary(
                owner=WorkOwner.MAINTAINER,
                display_title=next_step.display_title,
                plain_explanation=next_step.plain_explanation,
                blocking=True,
                system_handled=False,
            )
        )

    return tuple(items)
