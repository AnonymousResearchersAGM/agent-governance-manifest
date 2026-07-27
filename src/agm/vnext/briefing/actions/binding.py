"""Case, actor, policy, and judgment binding helpers."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from ...guidance import ActorContext
from ...models import GovernanceCase, fingerprint
from ..models import ReviewBriefView
from .models import ReviewDecisionDraft


def actor_from_context(value: Any) -> ActorContext:
    if isinstance(value, ActorContext):
        return value
    if isinstance(value, dict):
        return ActorContext(
            actor=str(value.get("actor", "")),
            role=str(value.get("role", "")),
            human=bool(value.get("human", False)),
        )
    return ActorContext(
        actor=str(getattr(value, "actor", "")),
        role=str(getattr(value, "role", "")),
        human=bool(getattr(value, "human", False)),
    )


def judgment_binding(view: ReviewBriefView) -> str:
    return fingerprint(
        [
            {
                "judgment_id": item.judgment_id,
                "blocking": item.blocking,
                "requirement_refs": item.requirement_refs,
                "provenance": item.provenance,
                "review_focus": item.review_focus,
            }
            for item in view.human_judgments
        ]
    )


def case_binding(
    case: GovernanceCase,
    *,
    actor: ActorContext,
    review_brief: ReviewBriefView,
) -> dict[str, str]:
    return {
        "case_id": case.id,
        "actor_id": actor.actor,
        "role": actor.role,
        "case_state": case.state,
        "contribution_fingerprint": case.contribution_fingerprint,
        "policy_snapshot_fingerprint": (
            case.policy_snapshot.policy_fingerprint
        ),
        "judgment_binding": judgment_binding(review_brief),
    }


def draft_fingerprint(draft: ReviewDecisionDraft) -> str:
    return fingerprint(asdict(draft))
