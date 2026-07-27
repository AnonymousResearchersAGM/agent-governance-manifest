"""Reviewer Guidance Layer public API."""

from .action_planner import (
    action_views,
    preview_reviewer_action,
)
from .models import (
    ActionPreview,
    ActionPreviewDisplayEffect,
    ActorContext,
    AvailableAction,
    ContributionSummary,
    ContextSelectorOption,
    DiagnosticFindingView,
    GuidanceUtilityAction,
    GuidanceExplanation,
    GuidanceReasonPresentation,
    MaterialityDeclarationView,
    RejectedOperationView,
    RequirementComparison,
    ResponsibilityView,
    ReviewerGuidanceView,
    TraceReference,
    UnavailableAction,
    WorkflowStepView,
)
from .responsibility import derive_current_responsibility
from .selectors import (
    build_context_selector_options,
    resolve_selector_tokens,
)
from .utilities import build_guidance_utilities, utility_output
from .term_presentations import (
    PresentedTerm,
    present_action,
    present_obligation,
    present_record_type,
    present_role,
    present_state,
    present_workflow_node,
)
from .presenters import (
    build_no_package_guidance,
    build_reviewer_guidance,
    render_guidance_html,
    render_guidance_markdown,
    render_action_preview_markdown,
)

__all__ = [
    "ActionPreview",
    "ActionPreviewDisplayEffect",
    "ActorContext",
    "AvailableAction",
    "ContributionSummary",
    "ContextSelectorOption",
    "DiagnosticFindingView",
    "GuidanceUtilityAction",
    "GuidanceExplanation",
    "GuidanceReasonPresentation",
    "MaterialityDeclarationView",
    "PresentedTerm",
    "RejectedOperationView",
    "RequirementComparison",
    "ResponsibilityView",
    "ReviewerGuidanceView",
    "TraceReference",
    "UnavailableAction",
    "WorkflowStepView",
    "action_views",
    "build_no_package_guidance",
    "build_context_selector_options",
    "build_guidance_utilities",
    "build_reviewer_guidance",
    "derive_current_responsibility",
    "preview_reviewer_action",
    "present_action",
    "present_obligation",
    "present_record_type",
    "present_role",
    "present_state",
    "present_workflow_node",
    "resolve_selector_tokens",
    "render_guidance_html",
    "render_guidance_markdown",
    "render_action_preview_markdown",
    "utility_output",
]
