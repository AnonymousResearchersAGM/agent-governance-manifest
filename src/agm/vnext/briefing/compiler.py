"""Pure compiler from canonical governance records to human review work."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..config import VNextConfig
from ..guidance import ActorContext, build_reviewer_guidance
from ..guidance.diagnostics import (
    build_requirement_comparisons,
    derive_readiness,
)
from ..guidance.responsibility import derive_current_responsibility
from ..migration import MigrationDiagnostic, check_migration
from ..models import GovernanceCase, StateTransition
from .accountability import compile_accountability_brief
from .change_summary import (
    compile_contribution_brief,
    normalize_contribution,
)
from .evidence_summary import (
    compile_automatic_checks,
    compile_requirement_brief,
)
from .judgment_queue import compile_human_judgment_queue
from .models import GovernanceTechnicalDetails, ReviewBriefView
from .next_step import compile_next_step
from .risk_summary import compile_risk_brief


def _actor(value: Any) -> ActorContext:
    if isinstance(value, ActorContext):
        return value
    if isinstance(value, Mapping):
        return ActorContext(
            actor=str(value.get("actor", "maintainer-reviewer")),
            role=str(value.get("role", "maintainer")),
            human=bool(value.get("human", True)),
        )
    return ActorContext(
        actor=str(getattr(value, "actor", "maintainer-reviewer")),
        role=str(getattr(value, "role", "maintainer")),
        human=bool(getattr(value, "human", True)),
    )


def _transitions(context: dict[str, Any]) -> list[StateTransition]:
    result = []
    for item in context.get("transitions", ()):
        if isinstance(item, StateTransition):
            result.append(item)
        elif isinstance(item, Mapping):
            result.append(StateTransition.from_dict(dict(item)))
    return result


def _migration(
    case: GovernanceCase,
    policy_snapshot: Any,
    context: dict[str, Any],
) -> MigrationDiagnostic | None:
    supplied = context.get("migration_diagnostic")
    if isinstance(supplied, MigrationDiagnostic):
        return supplied
    if isinstance(supplied, Mapping):
        return MigrationDiagnostic(**dict(supplied))
    if isinstance(policy_snapshot, VNextConfig):
        return check_migration(case, policy_snapshot)
    return None


def _technical_trace_index(
    case: GovernanceCase,
    comparisons: list[Any],
    brief: ReviewBriefView | None = None,
) -> dict[str, tuple[dict[str, str], ...]]:
    traces: dict[str, tuple[dict[str, str], ...]] = {}
    comparison_by_title = {
        item.display_name: item for item in comparisons
    }
    if brief is not None:
        for requirement in brief.requirements.items:
            comparison = comparison_by_title.get(requirement.display_title)
            if comparison is None:
                continue
            objects = [
                {
                    "kind": "compiled_obligation",
                    "object_id": case.obligation(
                        comparison.obligation_id
                    ).id,
                    "relationship": "source",
                }
            ]
            objects.extend(
                {
                    "kind": trace.kind,
                    "object_id": trace.object_id,
                    "relationship": trace.relationship,
                }
                for trace in comparison.traceability
            )
            traces[requirement.trace_refs[0]] = tuple(objects)
        for check in brief.automatic_checks:
            related: list[dict[str, str]] = []
            if check.check_type in {
                "material_version_binding",
                "evidence_freshness",
                "structural_obligations",
            }:
                related.extend(
                    {
                        "kind": "evidence",
                        "object_id": item.id,
                        "relationship": check.check_type,
                    }
                    for item in case.evidence
                )
            elif check.check_type.startswith("test_"):
                related.extend(
                    {
                        "kind": "evidence",
                        "object_id": item.id,
                        "relationship": check.check_type,
                    }
                    for item in case.evidence
                    if item.evidence_type
                    in {"test_command", "test_explanation"}
                )
            elif check.check_type == "attestation_version_binding":
                related.extend(
                    {
                        "kind": "human_attestation",
                        "object_id": item.id,
                        "relationship": check.check_type,
                    }
                    for item in case.attestations
                )
            elif check.check_type == "authority_boundary":
                related.extend(
                    {
                        "kind": "attempted_operation",
                        "object_id": item.id,
                        "relationship": "denied",
                    }
                    for item in case.attempted_operations
                )
            elif check.check_type == "semantic_declaration_consistency":
                related.extend(
                    {
                        "kind": "compiled_obligation",
                        "object_id": item.id,
                        "relationship": check.check_type,
                    }
                    for item in case.obligations
                    if item.evidence_type
                    in {
                        "rationale",
                        "known_limitations",
                        "security_auth_impact",
                        "policy_impact",
                        "agent_action_scope",
                        "independent_review",
                    }
                )
            traces[check.trace_refs[0]] = tuple(related)
        for judgment in brief.human_judgments:
            comparison = comparison_by_title.get(judgment.display_title)
            related = []
            if comparison:
                related.extend(
                    {
                        "kind": trace.kind,
                        "object_id": trace.object_id,
                        "relationship": trace.relationship,
                    }
                    for trace in comparison.traceability
                )
            traces[judgment.trace_refs[0]] = tuple(related)
    return traces


def compile_review_brief(
    *,
    governance_case: GovernanceCase,
    policy_snapshot: Any,
    contribution: Any,
    actor_context: Any,
) -> ReviewBriefView:
    """Compile one read-only maintainer brief from existing governance facts.

    ``policy_snapshot`` normally receives the already-loaded ``VNextConfig`` so
    the compiler can reuse Reviewer Guidance. Passing the immutable
    ``PolicySnapshot`` remains supported for domain-only callers; in that mode
    the same stable requirement comparison functions are used.
    """

    case = governance_case
    context = normalize_contribution(contribution)
    actor = _actor(actor_context)
    transitions = _transitions(context)
    migration = _migration(case, policy_snapshot, context)

    if isinstance(policy_snapshot, VNextConfig):
        guidance = build_reviewer_guidance(
            case,
            policy_snapshot,
            transitions,
            actor,
            migration_diagnostic=migration,
        )
        comparisons = guidance.requirement_comparisons
        guidance_dict = guidance.to_dict()
    else:
        comparisons = build_requirement_comparisons(case)
        responsibility = derive_current_responsibility(
            case,
            comparisons,
            case.findings,
            case.repair_requests,
            case.attestations,
            actor,
        )
        guidance_dict = {
            "schema_version": "agm.reviewer_guidance/reference-only",
            "requirement_comparisons": [
                item.to_dict() for item in comparisons
            ],
            "responsibility": responsibility.to_dict(),
            "note": (
                "Full Reviewer Guidance technical data requires VNextConfig; "
                "requirement and responsibility conclusions remain shared."
            ),
        }

    contribution_brief = compile_contribution_brief(case, context)
    risk = compile_risk_brief(case, policy_snapshot)
    requirements = compile_requirement_brief(case, comparisons)
    automatic_checks = compile_automatic_checks(case, requirements)
    accountability = compile_accountability_brief(
        case, policy_snapshot, context
    )
    judgments = compile_human_judgment_queue(
        case,
        comparisons,
        requirements,
        accountability,
        context,
    )
    next_step = compile_next_step(
        case, requirements, judgments, migration
    )

    migration_dict = migration.to_dict() if migration else None
    details = GovernanceTechnicalDetails(
        case_id=case.id,
        raw_state=case.state,
        raw_readiness=derive_readiness(case),
        contribution_fingerprint=case.contribution_fingerprint,
        policy_fingerprint=case.policy_snapshot.policy_fingerprint,
        policy_snapshot=case.policy_snapshot.to_dict(),
        matched_rules=tuple(item.to_dict() for item in case.matched_rules),
        compiled_obligations=tuple(
            item.to_dict() for item in case.obligations
        ),
        evidence_records=tuple(item.to_dict() for item in case.evidence),
        attestation_records=tuple(
            item.to_dict() for item in case.attestations
        ),
        findings=tuple(item.to_dict() for item in case.findings),
        repair_requests=tuple(
            item.to_dict() for item in case.repair_requests
        ),
        attempted_operations=tuple(
            item.to_dict() for item in case.attempted_operations
        ),
        verification_records=tuple(
            item.to_dict() for item in case.maintainer_verifications
        ),
        transition_history=tuple(
            item.to_dict() for item in transitions
        ),
        final_decision=(
            case.final_decision.to_dict() if case.final_decision else None
        ),
        closure_receipt=(
            case.closure_receipt.to_dict()
            if case.closure_receipt
            else None
        ),
        policy_migration_diagnostic=migration_dict,
        reviewer_guidance=guidance_dict,
        trace_index={},
    )
    initial = ReviewBriefView(
        contribution=contribution_brief,
        risk=risk,
        requirements=requirements,
        automatic_checks=automatic_checks,
        contributor_accountability=accountability,
        human_judgments=judgments,
        current_next_step=next_step,
        governance_details=details,
    )
    details_with_traces = GovernanceTechnicalDetails(
        **{
            **details.to_dict(),
            "trace_index": _technical_trace_index(
                case, comparisons, initial
            ),
        }
    )
    return ReviewBriefView(
        contribution=contribution_brief,
        risk=risk,
        requirements=requirements,
        automatic_checks=automatic_checks,
        contributor_accountability=accountability,
        human_judgments=judgments,
        current_next_step=next_step,
        governance_details=details_with_traces,
    )
