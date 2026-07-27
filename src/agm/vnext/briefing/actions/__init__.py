"""Contextual actions for the AGM Review Briefing Layer."""

from .compiler import (
    compile_contextual_actions,
    compile_final_decision_view,
)
from .draft import MAX_REASON_LENGTH, ReviewDraftStore, normalize_reason
from .executor import (
    execute_final_decision,
    execute_review_submission,
)
from .models import (
    DraftAssessment,
    ExistingOperationPlan,
    FinalDecisionOption,
    FinalDecisionPreview,
    FinalDecisionResult,
    FinalDecisionView,
    InteractiveJudgmentItem,
    JudgmentDecision,
    JudgmentOption,
    ReviewActionView,
    ReviewDecisionDraft,
    ReviewSubmissionPreview,
    ReviewSubmissionResult,
)
from .presenters import (
    render_final_decision_html,
    render_final_preview_html,
    render_final_result_html,
    render_interactive_review_html,
    render_review_preview_html,
    render_review_result_html,
)
from .preview import (
    PreviewTokenRegistry,
    preview_final_decision,
    preview_review_submission,
)

__all__ = [
    "DraftAssessment",
    "ExistingOperationPlan",
    "FinalDecisionOption",
    "FinalDecisionPreview",
    "FinalDecisionResult",
    "FinalDecisionView",
    "InteractiveJudgmentItem",
    "JudgmentDecision",
    "JudgmentOption",
    "MAX_REASON_LENGTH",
    "PreviewTokenRegistry",
    "ReviewActionView",
    "ReviewDecisionDraft",
    "ReviewDraftStore",
    "ReviewSubmissionPreview",
    "ReviewSubmissionResult",
    "compile_contextual_actions",
    "compile_final_decision_view",
    "execute_final_decision",
    "execute_review_submission",
    "normalize_reason",
    "preview_final_decision",
    "preview_review_submission",
    "render_final_decision_html",
    "render_final_preview_html",
    "render_final_result_html",
    "render_interactive_review_html",
    "render_review_preview_html",
    "render_review_result_html",
]
