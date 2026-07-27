"""Generate eight reproducible Reviewer Guidance Layer demonstration outputs."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from contextlib import nullcontext
from pathlib import Path
from typing import Any, Callable


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from agm.vnext.guidance import (  # noqa: E402
    ActorContext,
    build_reviewer_guidance,
    render_action_preview_markdown,
    render_guidance_html,
    render_guidance_markdown,
)
from agm.vnext.models import VNextError  # noqa: E402
from agm.vnext.runtime import (  # noqa: E402
    DemoExecutionContext,
    use_execution_context,
)
from agm.vnext.service import GovernanceService  # noqa: E402
from agm.vnext.storage import atomic_write_text  # noqa: E402


FIXED_TIME = "2026-07-26T00:00:00Z"
# This key is intentionally confined to generated public research fixtures.  It
# is never installed in the default/production execution context.
DEMO_TOKEN_SECRET = b"agm-reviewer-guidance-public-demo-fixtures-v1"

EVIDENCE_VALUES = {
    "contribution_summary": "Implemented the scenario contribution.",
    "changed_files": [],
    "rationale": "The scenario change is required by its stated objective.",
    "test_explanation": "The changed documentation was inspected.",
    "test_command": "The complete local regression suite passed.",
    "artifact": "Local regression output is attached.",
    "known_limitations": "This remains a local research prototype.",
    "security_auth_impact": (
        "Authentication behavior is affected; authorization boundaries were "
        "checked separately."
    ),
    "policy_impact": (
        "Governance compatibility, self-modification, and migration were "
        "assessed."
    ),
    "agent_action_scope": (
        "Task-bounded workspace access under active supervision; no "
        "undeclared delegation."
    ),
}


def make_project(parent: Path, name: str) -> Path:
    root = parent / name
    shutil.copytree(REPOSITORY_ROOT / ".agm", root / ".agm")
    shutil.copytree(REPOSITORY_ROOT / "skills", root / "skills")
    (root / "docs").mkdir()
    (root / "docs" / "guide.md").write_text(
        "reviewer guidance\n", encoding="utf-8"
    )
    (root / "demo_app").mkdir()
    (root / "demo_app" / "auth.py").write_text(
        "AUTH = True\n", encoding="utf-8"
    )
    (root / "demo_app" / "config.py").write_text(
        "SECURE = True\n", encoding="utf-8"
    )
    (root / "src" / "agm" / "vnext").mkdir(parents=True)
    (root / "src" / "agm" / "vnext" / "risk.py").write_text(
        "# governance runtime\n", encoding="utf-8"
    )
    return root


def open_case(
    service: GovernanceService,
    case_id: str,
    changed_files: list[str],
    *,
    autonomy_profile: str = "human_direct",
    requested_mode: str = "declared_agent_mediated",
) -> None:
    case, _ = service.open_case(
        changed_files,
        requested_mode=requested_mode,
        actor="contributor-agent",
        actor_role="contributor_agent",
        case_id=case_id,
        base_commit="demo-base",
        autonomy_profile=autonomy_profile,
        diff_material=f"{case_id}:initial",
        timestamp=FIXED_TIME,
    )
    if case is None:
        raise RuntimeError(f"Scenario did not create case {case_id}")


def add_all_evidence(
    service: GovernanceService,
    case_id: str,
) -> None:
    case = service.storage.load_case(case_id)
    artifact = service.root / f"{case_id}-tests.txt"
    artifact.write_text("all tests passed\n", encoding="utf-8")
    for obligation in case.obligations:
        if obligation.type != "evidence":
            continue
        value = EVIDENCE_VALUES[obligation.evidence_type]
        if obligation.evidence_type == "changed_files":
            value = list(case.changed_files)
        extra: dict[str, Any] = {}
        if obligation.evidence_type == "test_command":
            extra = {
                "command": "python -m pytest -q",
                "environment": "Python / local scenario",
            }
        if obligation.evidence_type == "artifact":
            extra = {"artifact_path": artifact.name}
        service.add_evidence(
            case_id,
            actor="contributor-agent",
            actor_role="contributor_agent",
            obligation_ids=[obligation.obligation_id],
            evidence_type=obligation.evidence_type,
            value=value,
            source_tool="scenario-generator",
            observed_at="2026-07-26T00:05:00Z",
            **extra,
        )


def prepare_for_verification(
    service: GovernanceService,
    case_id: str,
) -> None:
    service.prepare_case(
        case_id,
        actor="contributor-agent",
        actor_role="contributor_agent",
    )
    case = service.storage.load_case(case_id)
    if case.state == "awaiting_human_attestation":
        service.attest(
            case_id,
            actor="accountable-human",
            role="accountable_human",
            reviewed_scope=list(case.changed_files),
            statement=(
                "I reviewed the explicitly listed contribution and current "
                "evidence set."
            ),
            timestamp="2026-07-26T00:10:00Z",
        )


def multi_risk_missing(service: GovernanceService) -> dict[str, Any]:
    open_case(
        service,
        "multi-risk-missing",
        ["demo_app/auth.py", "demo_app/config.py"],
        autonomy_profile="supervised_agent",
    )
    return {
        "case_id": "multi-risk-missing",
        "actor": ActorContext("human-maintainer", "maintainer"),
        "preview_action": "request_repair",
        "preview_parameters": {
            "obligation_ids": ["O-AUTH-IMPACT"],
            "reason": "Preview a request for the missing security impact.",
        },
        "notes": "Union includes authentication, configuration, autonomy, and interaction obligations.",
    }


def material_partial_invalidation(
    service: GovernanceService,
) -> dict[str, Any]:
    open_case(
        service,
        "material-partial",
        ["docs/guide.md"],
        autonomy_profile="supervised_agent",
    )
    add_all_evidence(service, "material-partial")
    prepare_for_verification(service, "material-partial")
    service.verify(
        "material-partial",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Initial evidence checked.",
    )
    service.request_repair(
        "material-partial",
        actor="verifier-1",
        role="maintainer_verifier",
        message="The summary must be updated after a material scope change.",
        affected_obligation_ids=["O-SUMMARY"],
        finding_code="material_scope_change",
    )
    service.resubmit(
        "material-partial",
        actor="contributor-agent",
        role="contributor_agent",
        summary="Resubmitted the changed summary scope.",
        affected_obligation_ids=["O-SUMMARY"],
        diff_material="material-partial:changed-summary",
        change_classification="material",
        change_reason="Only the summary obligation is affected.",
    )
    return {
        "case_id": "material-partial",
        "actor": ActorContext("verifier-1", "maintainer_verifier"),
        "preview_action": "verify_evidence",
        "preview_parameters": {
            "obligation_ids": ["O-SUMMARY"],
            "reason": "Show why stale material cannot yet be verified.",
        },
        "notes": "The changed summary evidence is stale; unrelated bound evidence is retained.",
    }


def scoped_repair(service: GovernanceService) -> dict[str, Any]:
    open_case(
        service,
        "scoped-repair",
        ["docs/guide.md"],
        autonomy_profile="supervised_agent",
    )
    add_all_evidence(service, "scoped-repair")
    prepare_for_verification(service, "scoped-repair")
    service.verify(
        "scoped-repair",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Initial evidence checked.",
    )
    service.request_repair(
        "scoped-repair",
        actor="verifier-1",
        role="maintainer_verifier",
        message="Clarify agent action and delegation scope only.",
        affected_obligation_ids=["O-AGENT-SCOPE"],
        finding_code="agent_delegation_clarification",
    )
    service.resubmit(
        "scoped-repair",
        actor="contributor-agent",
        role="contributor_agent",
        summary="Clarified delegation wording without changing the contribution.",
        affected_obligation_ids=["O-AGENT-SCOPE"],
        diff_material="scoped-repair:initial",
        change_classification="non_material",
        change_reason="Wording clarification does not change contribution behavior.",
    )
    return {
        "case_id": "scoped-repair",
        "actor": ActorContext("verifier-1", "maintainer_verifier"),
        "preview_action": "verify_evidence",
        "preview_parameters": {
            "obligation_ids": ["O-AGENT-SCOPE"],
            "reason": "Revalidate only the repair scope.",
        },
        "notes": "Repair history records the revalidation scope and retained evidence IDs.",
    }


def unauthorized_agent_verification(
    service: GovernanceService,
) -> dict[str, Any]:
    open_case(service, "unauthorized-agent", ["docs/guide.md"])
    add_all_evidence(service, "unauthorized-agent")
    prepare_for_verification(service, "unauthorized-agent")
    state_before = service.storage.load_case("unauthorized-agent").state
    rejection = ""
    try:
        service.verify(
            "unauthorized-agent",
            actor="contributor-agent",
            role="contributor_agent",
            reason="Unauthorized verification attempt.",
        )
    except VNextError as exc:
        rejection = str(exc)
    state_after = service.storage.load_case("unauthorized-agent").state
    return {
        "case_id": "unauthorized-agent",
        "actor": ActorContext(
            "contributor-agent", "contributor_agent"
        ),
        "preview_action": "verify_evidence",
        "preview_parameters": {
            "reason": "Agent attempted maintainer verification.",
        },
        "notes": {
            "backend_rejection": rejection,
            "state_before": state_before,
            "state_after": state_after,
        },
    }


def lightweight_low_risk(service: GovernanceService) -> dict[str, Any]:
    open_case(service, "lightweight-low", ["docs/guide.md"])
    add_all_evidence(service, "lightweight-low")
    prepare_for_verification(service, "lightweight-low")
    return {
        "case_id": "lightweight-low",
        "actor": ActorContext("verifier-1", "maintainer_verifier"),
        "preview_action": "verify_evidence",
        "preview_parameters": {
            "reason": "Check the two lightweight evidence requirements.",
        },
        "notes": "No attestation or independent-review obligation; final decision remains human.",
    }


def governance_self_modification(
    service: GovernanceService,
) -> dict[str, Any]:
    open_case(
        service,
        "governance-self-mod",
        [".agm/manifest.yml", "src/agm/vnext/risk.py"],
        requested_mode="policy_required",
    )
    add_all_evidence(service, "governance-self-mod")
    prepare_for_verification(service, "governance-self-mod")
    return {
        "case_id": "governance-self-mod",
        "actor": ActorContext("independent-maintainer", "maintainer"),
        "preview_action": "verify_evidence",
        "preview_parameters": {
            "reason": "Independent policy/runtime verification.",
        },
        "notes": "The governance-self-modification interaction requires separation of duty.",
    }


def policy_migration_warning(
    service: GovernanceService,
) -> dict[str, Any]:
    open_case(service, "policy-migration", ["docs/guide.md"])
    case = service.storage.load_case("policy-migration")
    case.policy_snapshot.policy_fingerprint = (
        "recorded-policy-fingerprint-before-change"
    )
    service.storage.save_case(case)
    return {
        "case_id": "policy-migration",
        "actor": ActorContext("policy-reviewer", "policy_steward"),
        "preview_action": "record_policy_conflict",
        "preview_parameters": {
            "obligation_ids": ["O-SUMMARY"],
            "reason": "Preview a conflict record without silently migrating.",
        },
        "notes": "Migration check is read-only and exposes recorded versus current policy.",
    }


def human_final_decision_and_closure(
    service: GovernanceService,
) -> dict[str, Any]:
    open_case(service, "human-final-closure", ["docs/guide.md"])
    add_all_evidence(service, "human-final-closure")
    prepare_for_verification(service, "human-final-closure")
    verification = service.verify(
        "human-final-closure",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Evidence independently checked.",
        timestamp="2026-07-26T00:20:00Z",
    )
    preview = service.preview_reviewer_action(
        "human-final-closure",
        actor="human-maintainer",
        role="maintainer",
        action="decide_accept",
        parameters={"reason": "Human final decision preview."},
    )
    service.decide(
        "human-final-closure",
        actor="human-maintainer",
        role="maintainer",
        decision="accept",
        reason="Human maintainer accepted after independent review.",
        timestamp="2026-07-26T00:30:00Z",
    )
    return {
        "case_id": "human-final-closure",
        "actor": ActorContext("human-maintainer", "maintainer"),
        "prepared_preview": preview,
        "final_verification_record": verification.to_dict(),
        "notes": "Verification, final decision, and closure receipt remain separate records.",
    }


SCENARIOS: list[tuple[str, Callable[[GovernanceService], dict[str, Any]]]] = [
    ("01_multi_risk_missing", multi_risk_missing),
    ("02_material_partial_invalidation", material_partial_invalidation),
    ("03_scoped_repair", scoped_repair),
    ("04_unauthorized_agent_verification", unauthorized_agent_verification),
    ("05_lightweight_low_risk", lightweight_low_risk),
    ("06_governance_self_modification", governance_self_modification),
    ("07_policy_migration_warning", policy_migration_warning),
    ("08_human_final_decision_closure", human_final_decision_and_closure),
]


def generate(
    output_root: Path,
    *,
    deterministic: bool = True,
) -> list[dict[str, str]]:
    output_root.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="agm-guidance-demos-") as raw:
        temporary = Path(raw)
        for slug, builder in SCENARIOS:
            execution = (
                use_execution_context(
                    DemoExecutionContext(
                        scenario_namespace=slug,
                        fixed_timestamp=FIXED_TIME,
                        token_secret=DEMO_TOKEN_SECRET,
                    )
                )
                if deterministic
                else nullcontext()
            )
            with execution:
                root = make_project(temporary, slug)
                service = GovernanceService(root)
                scenario = builder(service)
                case_id = scenario["case_id"]
                actor: ActorContext = scenario["actor"]
                case = service.storage.load_case(case_id)
                transitions = service.storage.read_transitions(case_id)
                view = build_reviewer_guidance(
                    case,
                    service.config,
                    transitions,
                    actor,
                    migration_diagnostic=service.migration_check(case_id),
                )
                preview = scenario.get("prepared_preview")
                if preview is None:
                    preview = service.preview_reviewer_action(
                        case_id,
                        actor=actor.actor,
                        role=actor.role,
                        action=scenario["preview_action"],
                        parameters=scenario.get("preview_parameters"),
                    )
                final_verification = scenario.get(
                    "final_verification_record",
                    (
                        case.maintainer_verifications[-1].to_dict()
                        if case.maintainer_verifications
                        else None
                    ),
                )
                payload = {
                    "schema_version": "agm.reviewer_guidance_demo/v0.2-dev",
                    "scenario": slug,
                    "notes": scenario.get("notes"),
                    "guidance_view": view.to_dict(),
                    "expected_workflow_steps": [
                        {
                            "step_id": item.step_id,
                            "title": item.title,
                            "status": item.status,
                        }
                        for item in view.workflow_steps
                    ],
                    "expected_requirement_comparison": [
                        item.to_dict()
                        for item in view.requirement_comparisons
                    ],
                    "current_responsibility": (
                        view.responsibility.to_dict()
                        if view.responsibility
                        else None
                    ),
                    "current_relevant_actions": [
                        item.to_dict()
                        for item in view.current_relevant_actions
                    ],
                    "unavailable_action_summary": (
                        view.unavailable_action_summary
                    ),
                    "context_selector_data": {
                        item.action: [
                            option.to_dict()
                            for option in item.selector_options
                        ]
                        for item in view.available_actions
                        if item.selector_options
                    },
                    "trace_mapping": {
                        item.step_id: [
                            trace.to_dict()
                            for trace in item.traceability
                        ]
                        for item in view.workflow_steps
                    },
                    "available_actions": [
                        item.to_dict() for item in view.available_actions
                    ],
                    "unavailable_actions": [
                        item.to_dict() for item in view.unavailable_actions
                    ],
                    "action_preview": preview.to_dict(),
                    "final_verification_record": final_verification,
                }
                scenario_root = output_root / slug
                scenario_root.mkdir(parents=True, exist_ok=True)
                json_path = scenario_root / "guidance.json"
                markdown_path = scenario_root / "report.md"
                html_path = scenario_root / "report.html"
                atomic_write_text(
                    json_path,
                    json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                )
                atomic_write_text(
                    markdown_path,
                    render_guidance_markdown(view)
                    + "\n\n"
                    + render_action_preview_markdown(preview)
                    + "\n",
                )
                atomic_write_text(
                    html_path,
                    render_guidance_html(view, preview=preview),
                )
                results.append(
                    {
                        "scenario": slug,
                        "json": str(json_path.relative_to(output_root)),
                        "markdown": str(
                            markdown_path.relative_to(output_root)
                        ),
                        "html": str(html_path.relative_to(output_root)),
                    }
                )
    manifest_path = output_root / "manifest.json"
    atomic_write_text(
        manifest_path,
        json.dumps(
            {
                "schema_version": "agm.reviewer_guidance_demo_manifest/v0.2-dev",
                "scenario_count": len(results),
                "scenarios": results,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
    )
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            REPOSITORY_ROOT
            / "examples"
            / "reviewer_guidance"
            / "outputs"
        ),
    )
    parser.add_argument(
        "--runtime-random",
        action="store_true",
        help=(
            "Use normal runtime randomness for debugging. The default public "
            "research-demo mode is deterministic."
        ),
    )
    args = parser.parse_args()
    results = generate(
        args.output.resolve(),
        deterministic=not args.runtime_random,
    )
    print(
        json.dumps(
            {"generated": len(results), "outputs": results},
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
