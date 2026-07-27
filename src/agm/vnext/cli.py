"""Discoverable command-line interface for AGM vNext development."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .briefing import (
    render_review_brief_html,
    render_review_brief_json,
    render_review_brief_markdown,
)
from .briefing.server import serve_review_brief
from .briefing.actions import (
    compile_contextual_actions,
    compile_final_decision_view,
    render_final_decision_html,
    render_interactive_review_html,
)
from .briefing.actions.server import serve_interactive_review
from .config import load_vnext_config
from .guidance import ActorContext
from .guidance.presenters import (
    render_guidance_html,
    render_guidance_markdown,
)
from .models import VNextError
from .reporting import readiness, render_html, render_markdown
from .service import GovernanceService
from .storage import atomic_write_text
from .ui import serve_panel


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))


def add_actor_arguments(
    parser: argparse.ArgumentParser,
    *,
    default_role: str,
) -> None:
    parser.add_argument("--actor", required=True, help="Explicit actor identifier.")
    parser.add_argument("--role", default=default_role, help="Actor role used for authorization.")


def add_case_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--case", required=True, dest="case_id")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m agm.vnext.cli",
        description=(
            "AGM vNext development lifecycle. Readiness is not acceptance; "
            "final decisions remain with authorized human maintainers."
        ),
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root containing canonical .agm/ policy (default: current directory).",
    )
    groups = parser.add_subparsers(dest="group", required=True)

    project = groups.add_parser("project", help="Validate and simulate canonical project policy.")
    project_commands = project.add_subparsers(dest="command", required=True)
    project_commands.add_parser("validate", help="Validate all vNext policy references and cross-links.")
    simulate = project_commands.add_parser(
        "simulate", help="Resolve rules and compile obligations without creating a case."
    )
    simulate.add_argument("--changed-file", action="append", required=True)
    simulate.add_argument(
        "--mode",
        default="ordinary",
        choices=[
            "ordinary",
            "declared_agent_mediated",
            "policy_required",
            "maintainer_requested",
        ],
    )
    simulate.add_argument("--change-tag", action="append")
    simulate.add_argument("--semantic-target", action="append")
    simulate.add_argument("--autonomy-profile", default="human_direct")
    simulate.add_argument("--assurance-profile", default="standard")

    contributor = groups.add_parser(
        "contributor", help="Prepare evidence and expose explicit human attestation."
    )
    contributor_commands = contributor.add_subparsers(dest="command", required=True)
    open_case = contributor_commands.add_parser(
        "open-case", help="Resolve policy and open a Governance Case when required."
    )
    open_case.add_argument("--changed-file", action="append", required=True)
    open_case.add_argument(
        "--mode",
        default="declared_agent_mediated",
        choices=[
            "ordinary",
            "declared_agent_mediated",
            "policy_required",
            "maintainer_requested",
        ],
    )
    open_case.add_argument("--case", dest="case_id")
    open_case.add_argument("--base-commit")
    open_case.add_argument("--change-tag", action="append")
    open_case.add_argument("--semantic-target", action="append")
    open_case.add_argument("--autonomy-profile", default="supervised_agent")
    open_case.add_argument("--assurance-profile", default="standard")
    open_case.add_argument("--diff-material")
    add_actor_arguments(open_case, default_role="contributor_agent")

    add_evidence = contributor_commands.add_parser(
        "add-evidence", help="Bind one evidence record to one or more obligations."
    )
    add_case_argument(add_evidence)
    add_actor_arguments(add_evidence, default_role="contributor_agent")
    add_evidence.add_argument("--obligation", action="append", required=True)
    add_evidence.add_argument("--evidence-type", required=True)
    add_evidence.add_argument("--value", required=True)
    add_evidence.add_argument(
        "--value-json",
        action="store_true",
        help="Parse --value as JSON instead of a string.",
    )
    add_evidence.add_argument("--scope", action="append")
    add_evidence.add_argument("--command")
    add_evidence.add_argument("--environment")
    add_evidence.add_argument("--artifact-path")
    add_evidence.add_argument("--source-tool")
    add_evidence.add_argument("--observed-at")
    add_evidence.add_argument("--expires-at")

    prepare = contributor_commands.add_parser(
        "prepare", help="Validate evidence and advance to attestation or verification."
    )
    add_case_argument(prepare)
    add_actor_arguments(prepare, default_role="contributor_agent")

    review = contributor_commands.add_parser(
        "review", help="Generate the contributor panel and optionally serve it locally."
    )
    add_case_argument(review)
    review.add_argument("--serve", action="store_true")
    review.add_argument("--host", default="127.0.0.1")
    review.add_argument("--port", type=int, default=8765)

    attest = contributor_commands.add_parser(
        "attest", help="Record an explicit accountable-human attestation operation."
    )
    add_case_argument(attest)
    add_actor_arguments(attest, default_role="accountable_human")
    attest.add_argument("--scope", action="append", required=True)
    attest.add_argument("--statement", required=True)
    attest.add_argument("--reservation", action="append")
    attest.add_argument("--timestamp")

    decline = contributor_commands.add_parser(
        "decline-attestation", help="Decline to attest and create a repair request."
    )
    add_case_argument(decline)
    add_actor_arguments(decline, default_role="accountable_human")
    decline.add_argument("--reason", required=True)

    correction = contributor_commands.add_parser(
        "request-correction", help="Request correction before human attestation."
    )
    add_case_argument(correction)
    add_actor_arguments(correction, default_role="accountable_human")
    correction.add_argument("--reason", required=True)
    correction.add_argument("--obligation", action="append", required=True)

    case_group = groups.add_parser("case", help="Inspect, resubmit, and diagnose a case.")
    case_commands = case_group.add_subparsers(dest="command", required=True)
    status = case_commands.add_parser("status", help="Show case state and readiness.")
    add_case_argument(status)
    migrate = case_commands.add_parser(
        "migrate-check", help="Compare an open case with current canonical policy."
    )
    add_case_argument(migrate)
    resubmit = case_commands.add_parser(
        "resubmit", help="Record a scoped repair attempt and recompute bindings."
    )
    add_case_argument(resubmit)
    add_actor_arguments(resubmit, default_role="contributor_agent")
    resubmit.add_argument("--summary", required=True)
    resubmit.add_argument("--obligation", action="append", required=True)
    resubmit.add_argument("--evidence-id", action="append")
    resubmit.add_argument("--diff-material")
    resubmit.add_argument(
        "--change-classification",
        choices=["unrelated", "non_material", "material"],
        default="material",
        help="Declared materiality used for scoped evidence retention.",
    )
    resubmit.add_argument(
        "--change-reason",
        help="Factual reason for the declared materiality and affected scope.",
    )

    maintainer = groups.add_parser(
        "maintainer", help="Inspect and execute authorized maintainer operations."
    )
    maintainer_commands = maintainer.add_subparsers(dest="command", required=True)
    inspect = maintainer_commands.add_parser(
        "inspect", help="Generate the maintainer governance laboratory report."
    )
    add_case_argument(inspect)
    inspect.add_argument("--serve", action="store_true")
    inspect.add_argument("--host", default="127.0.0.1")
    inspect.add_argument("--port", type=int, default=8766)
    inspect.add_argument(
        "--actor",
        default="maintainer-reviewer",
        help="Actor identifier used to calculate the displayed operation surface.",
    )
    inspect.add_argument(
        "--role",
        default="maintainer",
        choices=[
            "contributor_agent",
            "contributor",
            "accountable_human",
            "maintainer_verifier",
            "policy_steward",
            "maintainer",
        ],
        help="Role used for guidance; every mutation is re-authorized.",
    )
    brief = maintainer_commands.add_parser(
        "brief",
        help="Compile the read-only human-work review briefing.",
    )
    add_case_argument(brief)
    brief.add_argument("--serve", action="store_true")
    brief.add_argument("--host", default="127.0.0.1")
    brief.add_argument("--port", type=int, default=8767)
    brief.add_argument(
        "--actor",
        default="maintainer-reviewer",
        help="Human actor identifier shown in the briefing context.",
    )
    brief.add_argument(
        "--role",
        default="maintainer",
        choices=[
            "maintainer_verifier",
            "policy_steward",
            "maintainer",
        ],
        help="Read-only maintainer-side role used for briefing context.",
    )
    interactive_review = maintainer_commands.add_parser(
        "review",
        help=(
            "Compile item-bound human judgment actions and optionally serve "
            "the loopback interactive review."
        ),
    )
    add_case_argument(interactive_review)
    interactive_review.add_argument("--serve", action="store_true")
    interactive_review.add_argument("--host", default="127.0.0.1")
    interactive_review.add_argument("--port", type=int, default=8768)
    interactive_review.add_argument(
        "--actor",
        default="human-maintainer",
        help="Human actor identifier bound to drafts and previews.",
    )
    interactive_review.add_argument(
        "--role",
        default="maintainer",
        choices=[
            "maintainer_verifier",
            "policy_steward",
            "maintainer",
        ],
        help="Canonical human role used for server-side authorization.",
    )

    verify = maintainer_commands.add_parser(
        "verify", help="Record independent maintainer verification."
    )
    add_case_argument(verify)
    add_actor_arguments(verify, default_role="maintainer_verifier")
    verify.add_argument("--reason", required=True)
    verify.add_argument("--obligation", action="append")

    request_repair = maintainer_commands.add_parser(
        "request-repair", help="Create a finding and scoped repair request."
    )
    add_case_argument(request_repair)
    add_actor_arguments(request_repair, default_role="maintainer_verifier")
    request_repair.add_argument("--message", required=True)
    request_repair.add_argument("--obligation", action="append", required=True)
    request_repair.add_argument("--responsible-role", default="contributor")

    reject = maintainer_commands.add_parser(
        "reject-evidence", help="Reject evidence with a reason and request repair."
    )
    add_case_argument(reject)
    add_actor_arguments(reject, default_role="maintainer_verifier")
    reject.add_argument("--evidence-id", required=True)
    reject.add_argument("--reason", required=True)

    clarification = maintainer_commands.add_parser(
        "ask-clarification", help="Ask a scoped clarification as an audited operation."
    )
    add_case_argument(clarification)
    add_actor_arguments(clarification, default_role="maintainer_verifier")
    clarification.add_argument("--question", required=True)
    clarification.add_argument("--obligation", action="append", required=True)

    invalidate = maintainer_commands.add_parser(
        "invalidate-attestation", help="Invalidate a stale or incorrect attestation."
    )
    add_case_argument(invalidate)
    add_actor_arguments(invalidate, default_role="maintainer_verifier")
    invalidate.add_argument("--attestation-id", required=True)
    invalidate.add_argument("--reason", required=True)

    conflict = maintainer_commands.add_parser(
        "record-policy-conflict", help="Record a blocking policy conflict."
    )
    add_case_argument(conflict)
    add_actor_arguments(conflict, default_role="policy_steward")
    conflict.add_argument("--message", required=True)
    conflict.add_argument("--obligation", action="append", required=True)

    resolve_conflict = maintainer_commands.add_parser(
        "resolve-policy-conflict", help="Resolve a recorded policy conflict."
    )
    add_case_argument(resolve_conflict)
    add_actor_arguments(resolve_conflict, default_role="policy_steward")
    resolve_conflict.add_argument("--finding-id", required=True)
    resolve_conflict.add_argument("--resolution", required=True)

    override = maintainer_commands.add_parser(
        "override", help="Record an authorized override; this is not final acceptance."
    )
    add_case_argument(override)
    add_actor_arguments(override, default_role="maintainer")
    override.add_argument("--reason", required=True)
    override.add_argument("--obligation", action="append")
    override.add_argument("--finding-id", action="append")

    decide = maintainer_commands.add_parser(
        "decide", help="Record an authorized human-maintainer decision."
    )
    add_case_argument(decide)
    add_actor_arguments(decide, default_role="maintainer")
    decide.add_argument(
        "--decision",
        required=True,
        choices=["accept", "reject", "request_changes", "close"],
    )
    decide.add_argument("--reason", required=True)
    decide.add_argument("--timestamp")
    return parser


def report_case(
    service: GovernanceService,
    *,
    case_id: str,
    audience: str,
    current_actor: ActorContext | None = None,
) -> dict[str, str]:
    case = service.storage.load_case(case_id)
    transitions = service.storage.read_transitions(case_id)
    guidance_json = None
    if audience == "maintainer":
        actor = current_actor or ActorContext(
            actor="maintainer-reviewer",
            role="maintainer",
        )
        view = service.reviewer_guidance(
            case_id,
            actor=actor.actor,
            role=actor.role,
        )
        markdown = render_guidance_markdown(view)
        html_report = render_guidance_html(view)
        guidance_json = json.dumps(
            view.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
    else:
        markdown = render_markdown(
            case,
            transitions,
            audience=audience,
            config=service.config,
            current_actor=current_actor,
        )
        html_report = render_html(
            case,
            transitions,
            audience=audience,
            config=service.config,
            current_actor=current_actor,
        )
    paths = service.storage.write_report(
        case_id,
        markdown=markdown,
        html=html_report,
        guidance_json=guidance_json,
    )
    return {key: str(value) for key, value in paths.items()}


def report_review_brief(
    service: GovernanceService,
    *,
    case_id: str,
    actor: str,
    role: str,
) -> dict[str, str]:
    """Compile and persist Phase 1 artifacts without changing the case."""

    view = service.review_brief(
        case_id,
        actor=actor,
        role=role,
    )
    paths = service.storage.write_review_brief(
        case_id,
        brief_json=render_review_brief_json(view),
        markdown=render_review_brief_markdown(view),
        html=render_review_brief_html(view),
    )
    return {key: str(value) for key, value in paths.items()}


def report_interactive_review(
    service: GovernanceService,
    *,
    case_id: str,
    actor: str,
    role: str,
) -> dict[str, str]:
    """Write deterministic static views without runtime secrets."""

    case = service.storage.load_case(case_id)
    actor_context = ActorContext(
        actor=actor,
        role=role,
        human=True,
    )
    brief = service.review_brief(
        case_id,
        actor=actor,
        role=role,
    )
    action_view = compile_contextual_actions(
        review_brief=brief,
        governance_case=case,
        actor_context=actor_context,
        policy_config=service.config,
        live_actions_enabled=False,
    )
    case_root = service.storage.case_dir(case_id)
    model_path = case_root / "review_action_model.json"
    html_path = case_root / "review_interactive.html"
    atomic_write_text(
        model_path,
        json.dumps(
            action_view.to_dict(),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    atomic_write_text(
        html_path,
        render_interactive_review_html(action_view),
    )
    paths = {
        "review_action_model": str(model_path),
        "review_interactive_html": str(html_path),
    }
    final_view = compile_final_decision_view(
        review_brief=brief,
        governance_case=case,
        actor_context=actor_context,
        policy_config=service.config,
    )
    if final_view.available:
        final_path = case_root / "final_decision.html"
        atomic_write_text(
            final_path,
            render_final_decision_html(final_view),
        )
        paths["final_decision_html"] = str(final_path)
    return paths


def dispatch(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if args.group == "project" and args.command == "validate":
        config = load_vnext_config(root)
        print_json(
            {
                "valid": True,
                "schema_version": config.manifest["schema_version"],
                "policy_fingerprint": config.policy_fingerprint,
                "risk_rule_count": len(config.risk_rules),
                "obligation_count": len(config.obligations),
                "role_count": len(config.roles),
                "transition_count": len(config.state_machine["transitions"]),
                "status": "development",
            }
        )
        return 0

    service = GovernanceService(root)
    if args.group == "project":
        print_json(
            service.simulate(
                args.changed_file,
                requested_mode=args.mode,
                change_tags=args.change_tag,
                semantic_targets=args.semantic_target,
                autonomy_profile=args.autonomy_profile,
                assurance_profile=args.assurance_profile,
            )
        )
        return 0

    if args.group == "contributor":
        if args.command == "open-case":
            case, intake = service.open_case(
                args.changed_file,
                requested_mode=args.mode,
                actor=args.actor,
                actor_role=args.role,
                case_id=args.case_id,
                base_commit=args.base_commit,
                change_tags=args.change_tag,
                semantic_targets=args.semantic_target,
                autonomy_profile=args.autonomy_profile,
                assurance_profile=args.assurance_profile,
                diff_material=args.diff_material,
            )
            print_json(
                {
                    "case_created": case is not None,
                    "case_id": case.id if case else None,
                    "state": case.state if case else "ordinary_unmanaged",
                    "intake": intake.__dict__,
                    "next_action": (
                        f"python -m agm.vnext.cli contributor prepare --case {case.id} "
                        f"--actor {args.actor}"
                        if case
                        else "Continue through the project's ordinary contribution workflow."
                    ),
                }
            )
        elif args.command == "add-evidence":
            value = json.loads(args.value) if args.value_json else args.value
            item = service.add_evidence(
                args.case_id,
                actor=args.actor,
                actor_role=args.role,
                obligation_ids=args.obligation,
                evidence_type=args.evidence_type,
                value=value,
                affected_scope=args.scope,
                command=args.command,
                environment=args.environment,
                artifact_path=args.artifact_path,
                source_tool=args.source_tool,
                observed_at=args.observed_at,
                expires_at=args.expires_at,
            )
            print_json(item.to_dict())
        elif args.command == "prepare":
            case = service.prepare_case(
                args.case_id, actor=args.actor, actor_role=args.role
            )
            print_json(
                {
                    "case_id": case.id,
                    "state": case.state,
                    "readiness": readiness(case),
                    "unresolved_blocking_obligations": [
                        item.obligation_id
                        for item in case.unresolved_blocking_obligations()
                    ],
                    "next_action": (
                        f"Open the contributor review panel for case {case.id}; "
                        "an agent cannot perform human attestation."
                        if case.state == "awaiting_human_attestation"
                        else "Await authorized maintainer verification."
                    ),
                }
            )
        elif args.command == "review":
            paths = report_case(
                service, case_id=args.case_id, audience="contributor"
            )
            print_json(paths)
            if args.serve:
                serve_panel(
                    service,
                    case_id=args.case_id,
                    audience="contributor",
                    host=args.host,
                    port=args.port,
                )
        elif args.command == "attest":
            item = service.attest(
                args.case_id,
                actor=args.actor,
                role=args.role,
                reviewed_scope=args.scope,
                statement=args.statement,
                reservations=args.reservation,
                timestamp=args.timestamp,
            )
            print_json(
                {
                    "attestation": item.to_dict(),
                    "note": "Human attestation is not final acceptance.",
                }
            )
        elif args.command == "decline-attestation":
            print_json(
                service.decline_attestation(
                    args.case_id,
                    actor=args.actor,
                    role=args.role,
                    reason=args.reason,
                ).to_dict()
            )
        elif args.command == "request-correction":
            print_json(
                service.request_correction(
                    args.case_id,
                    actor=args.actor,
                    role=args.role,
                    reason=args.reason,
                    affected_obligation_ids=args.obligation,
                ).to_dict()
            )
        return 0

    if args.group == "case":
        if args.command == "status":
            case = service.storage.load_case(args.case_id)
            print_json(
                {
                    "case_id": case.id,
                    "mode": case.mode,
                    "state": case.state,
                    "readiness": readiness(case),
                    "overall_risk_level": case.overall_risk_level,
                    "policy_fingerprint": case.policy_snapshot.policy_fingerprint,
                    "contribution_fingerprint": case.contribution_fingerprint,
                    "obligation_statuses": {
                        item.obligation_id: item.status
                        for item in case.obligations
                    },
                    "open_findings": [
                        item.to_dict()
                        for item in case.findings
                        if item.status == "open"
                    ],
                }
            )
        elif args.command == "migrate-check":
            print_json(service.migration_check(args.case_id).to_dict())
        elif args.command == "resubmit":
            case = service.resubmit(
                args.case_id,
                actor=args.actor,
                role=args.role,
                summary=args.summary,
                affected_obligation_ids=args.obligation,
                evidence_ids=args.evidence_id,
                diff_material=args.diff_material,
                change_classification=args.change_classification,
                change_reason=args.change_reason,
            )
            print_json({"case_id": case.id, "state": case.state})
        return 0

    if args.group == "maintainer":
        if args.command == "inspect":
            current_actor = ActorContext(
                actor=args.actor,
                role=args.role,
            )
            paths = report_case(
                service,
                case_id=args.case_id,
                audience="maintainer",
                current_actor=current_actor,
            )
            print_json(paths)
            if args.serve:
                serve_panel(
                    service,
                    case_id=args.case_id,
                    audience="maintainer",
                    host=args.host,
                    port=args.port,
                    actor=args.actor,
                    role=args.role,
                )
        elif args.command == "brief":
            paths = report_review_brief(
                service,
                case_id=args.case_id,
                actor=args.actor,
                role=args.role,
            )
            print_json(paths)
            if args.serve:
                serve_review_brief(
                    service,
                    case_id=args.case_id,
                    actor=args.actor,
                    role=args.role,
                    host=args.host,
                    port=args.port,
                )
        elif args.command == "review":
            paths = report_interactive_review(
                service,
                case_id=args.case_id,
                actor=args.actor,
                role=args.role,
            )
            print_json(paths)
            if args.serve:
                serve_interactive_review(
                    service,
                    case_id=args.case_id,
                    actor=args.actor,
                    role=args.role,
                    host=args.host,
                    port=args.port,
                )
        elif args.command == "verify":
            print_json(
                service.verify(
                    args.case_id,
                    actor=args.actor,
                    role=args.role,
                    reason=args.reason,
                    obligation_ids=args.obligation,
                ).to_dict()
            )
        elif args.command == "request-repair":
            print_json(
                service.request_repair(
                    args.case_id,
                    actor=args.actor,
                    role=args.role,
                    message=args.message,
                    affected_obligation_ids=args.obligation,
                    responsible_role=args.responsible_role,
                ).to_dict()
            )
        elif args.command == "reject-evidence":
            print_json(
                service.reject_evidence(
                    args.case_id,
                    actor=args.actor,
                    role=args.role,
                    evidence_id=args.evidence_id,
                    reason=args.reason,
                ).to_dict()
            )
        elif args.command == "ask-clarification":
            print_json(
                service.ask_clarification(
                    args.case_id,
                    actor=args.actor,
                    role=args.role,
                    question=args.question,
                    affected_obligation_ids=args.obligation,
                ).to_dict()
            )
        elif args.command == "invalidate-attestation":
            print_json(
                service.invalidate_attestation(
                    args.case_id,
                    actor=args.actor,
                    role=args.role,
                    attestation_id=args.attestation_id,
                    reason=args.reason,
                ).to_dict()
            )
        elif args.command == "record-policy-conflict":
            print_json(
                service.record_policy_conflict(
                    args.case_id,
                    actor=args.actor,
                    role=args.role,
                    message=args.message,
                    affected_obligation_ids=args.obligation,
                ).to_dict()
            )
        elif args.command == "resolve-policy-conflict":
            print_json(
                service.resolve_policy_conflict(
                    args.case_id,
                    actor=args.actor,
                    role=args.role,
                    finding_id=args.finding_id,
                    resolution=args.resolution,
                ).to_dict()
            )
        elif args.command == "override":
            case = service.override(
                args.case_id,
                actor=args.actor,
                role=args.role,
                reason=args.reason,
                obligation_ids=args.obligation,
                finding_ids=args.finding_id,
            )
            print_json(
                {
                    "case_id": case.id,
                    "state": case.state,
                    "note": "Override recorded; no final decision has been made.",
                }
            )
        elif args.command == "decide":
            decision = service.decide(
                args.case_id,
                actor=args.actor,
                role=args.role,
                decision=args.decision,
                reason=args.reason,
                timestamp=args.timestamp,
            )
            case = service.storage.load_case(args.case_id)
            print_json(
                {
                    "decision": decision.to_dict() if decision else None,
                    "case_state": case.state,
                    "closure_receipt": (
                        case.closure_receipt.to_dict()
                        if case.closure_receipt
                        else None
                    ),
                }
            )
        return 0
    raise VNextError("Unsupported command")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return dispatch(args)
    except (VNextError, json.JSONDecodeError) as exc:
        print_json({"ok": False, "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
