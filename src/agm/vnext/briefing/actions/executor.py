"""Execute only previously previewed contextual review operations."""

from __future__ import annotations

from ...models import VNextError, new_id, utc_now
from ...service import GovernanceService
from .binding import actor_from_context, draft_fingerprint
from .draft import ReviewDraftStore
from .models import FinalDecisionResult, ReviewSubmissionResult
from .preview import (
    PreviewTokenRegistry,
    _build_review_preview,
    preview_final_decision,
)


def execute_review_submission(
    *,
    service: GovernanceService,
    actor_context: object,
    case_id: str,
    preview_token: str | None,
    token_registry: PreviewTokenRegistry,
    draft_store: ReviewDraftStore | None = None,
) -> ReviewSubmissionResult:
    """Consume one token, revalidate all bindings, and use domain operations."""

    actor = actor_from_context(actor_context)
    store = draft_store or ReviewDraftStore(service.storage)
    try:
        if not preview_token:
            raise VNextError("没有 preview token 不得执行维护者检查。")
        consumed = token_registry.consume(
            preview_token,
            kind="review",
            case_id=case_id,
            actor_id=actor.actor,
            role=actor.role,
        )
        draft = store.restore(
            case_id=case_id,
            actor_id=actor.actor,
            role=actor.role,
        )
        if draft is None:
            raise VNextError("Preview 对应的 review draft 不存在。")
        if draft.draft_id != consumed.payload.get("draft_id", draft.draft_id):
            raise VNextError("Review draft identity 已变化。")
        if (
            draft_fingerprint(draft)
            != consumed.payload.get("draft_fingerprint")
        ):
            raise VNextError("Review draft 在 preview 后发生变化。")
        current_preview = _build_review_preview(
            service=service,
            actor=actor,
            draft=draft,
            token_registry=None,
            issue_token=False,
        )
        if (
            current_preview.preview_fingerprint
            != consumed.preview_fingerprint
        ):
            raise VNextError(
                "案例、判断来源或操作计划在 preview 后发生变化。"
            )
        executed = []
        for plan in current_preview.operation_plans:
            if plan.operation == "verify_evidence":
                service.verify(
                    case_id,
                    actor=actor.actor,
                    role=actor.role,
                    reason=plan.reason,
                    obligation_ids=list(plan.obligation_ids),
                )
            elif plan.operation == "request_repair":
                service.request_repair(
                    case_id,
                    actor=actor.actor,
                    role=actor.role,
                    message=plan.reason,
                    affected_obligation_ids=list(plan.obligation_ids),
                    responsible_role=plan.responsible_role or "contributor",
                )
            else:
                raise VNextError(
                    "Contextual compiler produced an unsupported operation."
                )
            executed.append(plan.operation)
        submitted_at = utc_now()
        submission_id = new_id("review-submission")
        next_brief = service.review_brief(
            case_id,
            actor=actor.actor,
            role=actor.role,
        )
        store.archive_submitted(
            draft,
            submission={
                "submission_id": submission_id,
                "submitted_at": submitted_at,
                "actor_id": actor.actor,
                "role": actor.role,
                "preview_fingerprint": (
                    current_preview.preview_fingerprint
                ),
                "executed_operations": executed,
                "resulting_case_state": (
                    next_brief.governance_details.raw_state
                ),
            },
        )
        consumed.result_fingerprint = submission_id
        return ReviewSubmissionResult(
            case_id=case_id,
            submitted=True,
            message="你的维护者检查已提交",
            executed_operations=tuple(executed),
            submission_id=submission_id,
            submitted_at=submitted_at,
            next_review_brief=next_brief,
        )
    except VNextError as exc:
        if case_id:
            store.record_rejected_attempt(
                case_id=case_id,
                actor_id=actor.actor,
                role=actor.role,
                reason=str(exc),
                operation="execute_review_submission",
            )
        raise


def execute_final_decision(
    *,
    service: GovernanceService,
    actor_context: object,
    case_id: str,
    preview_token: str | None,
    token_registry: PreviewTokenRegistry,
    draft_store: ReviewDraftStore | None = None,
) -> FinalDecisionResult:
    """Execute a final decision using a separate one-time preview."""

    actor = actor_from_context(actor_context)
    store = draft_store or ReviewDraftStore(service.storage)
    try:
        consumed = token_registry.consume(
            preview_token,
            kind="final",
            case_id=case_id,
            actor_id=actor.actor,
            role=actor.role,
        )
        payload = consumed.payload
        current_preview = preview_final_decision(
            service=service,
            actor_context=actor,
            case_id=case_id,
            decision_id=str(payload["decision_id"]),
            reason=str(payload["reason"]),
            token_registry=None,
            issue_token=False,
        )
        if (
            current_preview.preview_fingerprint
            != consumed.preview_fingerprint
        ):
            raise VNextError(
                "最终决定 preview 已因 case 或 policy 变化而失效。"
            )
        service.decide(
            case_id,
            actor=actor.actor,
            role=actor.role,
            decision=current_preview.decision_id,
            reason=current_preview.reason,
        )
        decided_at = utc_now()
        next_brief = service.review_brief(
            case_id,
            actor=actor.actor,
            role=actor.role,
        )
        return FinalDecisionResult(
            case_id=case_id,
            decision=current_preview.decision_id,
            message="最终人类决定已提交",
            executed_operation=str(payload["operation"]),
            decided_at=decided_at,
            next_review_brief=next_brief,
        )
    except VNextError as exc:
        store.record_rejected_attempt(
            case_id=case_id,
            actor_id=actor.actor,
            role=actor.role,
            reason=str(exc),
            operation="execute_final_decision",
        )
        raise
