"""Run ten deterministic AGM vNext development scenarios in a temporary project."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.vnext.config import load_vnext_config  # noqa: E402
from agm.vnext.evidence import validate_bound_evidence  # noqa: E402
from agm.vnext.models import MatchedRule  # noqa: E402
from agm.vnext.obligations import compile_obligations  # noqa: E402
from agm.vnext.policy import contribution_fingerprint  # noqa: E402
from agm.vnext.service import GovernanceService  # noqa: E402


def make_project(destination: Path) -> Path:
    shutil.copytree(ROOT / ".agm", destination / ".agm")
    shutil.copytree(ROOT / "skills", destination / "skills")
    (destination / "docs").mkdir()
    (destination / "docs" / "guide.md").write_text("guide\n", encoding="utf-8")
    (destination / "demo_app").mkdir()
    (destination / "demo_app" / "auth.py").write_text(
        "AUTH_ENABLED = True\n", encoding="utf-8"
    )
    (destination / "demo_app" / "config.py").write_text(
        "MODE = 'demo'\n", encoding="utf-8"
    )
    (destination / "src" / "agm" / "vnext").mkdir(parents=True)
    (destination / "src" / "agm" / "vnext" / "risk.py").write_text(
        "# governance runtime\n", encoding="utf-8"
    )
    return destination


def add_complete_evidence(
    service: GovernanceService,
    case_id: str,
    *,
    actor: str,
) -> None:
    case = service.storage.load_case(case_id)
    artifact = service.root / f"{case_id}-tests.txt"
    artifact.write_text("deterministic demo test output\n", encoding="utf-8")
    values = {
        "contribution_summary": "Deterministic vNext demonstration contribution.",
        "changed_files": case.changed_files,
        "rationale": "Exercise contribution-level governance behavior.",
        "test_explanation": "No executable behavior changed in this scenario.",
        "test_command": "Deterministic demonstration checks completed.",
        "artifact": "Local deterministic demonstration artifact.",
        "known_limitations": "Local file-based prototype; no hosted identity service.",
        "security_auth_impact": "Authentication-sensitive behavior is in demonstration scope.",
        "policy_impact": "Development policy and runtime compatibility were considered.",
        "agent_action_scope": "Task-bounded workspace action under active supervision.",
    }
    for obligation in case.obligations:
        if obligation.type != "evidence":
            continue
        extra = {}
        if obligation.evidence_type == "test_command":
            extra = {
                "command": "python scripts/run_vnext_demo.py",
                "environment": "local deterministic Python runtime",
            }
        if obligation.evidence_type == "artifact":
            extra = {"artifact_path": artifact.name}
        service.add_evidence(
            case_id,
            actor=actor,
            actor_role="contributor_agent",
            obligation_ids=[obligation.obligation_id],
            evidence_type=obligation.evidence_type,
            value=values[obligation.evidence_type],
            source_tool="run_vnext_demo.py",
            observed_at="2026-07-25T00:00:00Z",
            **extra,
        )


def open_managed(
    service: GovernanceService,
    *,
    case_id: str,
    changed_files: list[str],
    autonomy_profile: str = "supervised_agent",
):
    case, _ = service.open_case(
        changed_files,
        requested_mode="declared_agent_mediated",
        actor="demo-agent",
        actor_role="contributor_agent",
        case_id=case_id,
        base_commit="demo-base",
        autonomy_profile=autonomy_profile,
        timestamp="2026-07-25T00:00:00Z",
    )
    assert case is not None
    return case


def ready_low_case(
    service: GovernanceService,
    case_id: str,
) -> None:
    open_managed(
        service,
        case_id=case_id,
        changed_files=["docs/guide.md"],
    )
    add_complete_evidence(service, case_id, actor="demo-agent")
    service.prepare_case(
        case_id, actor="demo-agent", actor_role="contributor_agent"
    )
    service.verify(
        case_id,
        actor=f"{case_id}-verifier",
        role="maintainer_verifier",
        reason="Deterministic bindings checked.",
        timestamp="2026-07-25T01:00:00Z",
    )


def run_scenarios(project_root: Path) -> dict[str, object]:
    service = GovernanceService(project_root)
    results: dict[str, object] = {}

    ordinary, ordinary_intake = service.open_case(
        ["docs/guide.md"],
        requested_mode="ordinary",
        actor="demo-human",
        actor_role="contributor",
        base_commit="demo-base",
    )
    results["01_ordinary_human_documentation"] = {
        "case_created": ordinary is not None,
        "package_status": ordinary_intake.package_status,
    }

    low = open_managed(
        service,
        case_id="scenario-02",
        changed_files=["docs/guide.md"],
    )
    results["02_agent_low_risk_documentation"] = {
        "risk": low.overall_risk_level,
        "obligations": [item.obligation_id for item in low.obligations],
    }

    multi = service.simulate(
        ["demo_app/auth.py", "demo_app/config.py"],
        requested_mode="declared_agent_mediated",
        autonomy_profile="supervised_agent",
    )
    results["03_authentication_and_configuration"] = {
        "risk": multi["overall_risk_level"],
        "matched_rules": [item["rule_id"] for item in multi["matched_rules"]],
        "obligations": [
            item["obligation_id"] for item in multi["compiled_obligations"]
        ],
    }

    self_modification = service.simulate(
        [".agm/manifest.yml", "src/agm/vnext/risk.py"],
        requested_mode="policy_required",
        autonomy_profile="human_direct",
    )
    results["04_governance_self_modification"] = {
        "risk": self_modification["overall_risk_level"],
        "interactions": self_modification["interaction_rules"],
    }

    stale = open_managed(
        service,
        case_id="scenario-05",
        changed_files=["docs/guide.md"],
        autonomy_profile="human_direct",
    )
    evidence = service.add_evidence(
        stale.id,
        actor="demo-agent",
        actor_role="contributor_agent",
        obligation_ids=["O-SUMMARY"],
        evidence_type="contribution_summary",
        value="Evidence before the file changed.",
        source_tool="run_vnext_demo.py",
    )
    (project_root / "docs" / "guide.md").write_text(
        "guide changed after evidence\n", encoding="utf-8"
    )
    current_fingerprint = contribution_fingerprint(
        project_root,
        stale.changed_files,
        base_commit=stale.base_commit,
        change_tags=stale.change_tags,
        semantic_targets=stale.semantic_targets,
    )
    validate_bound_evidence(
        evidence,
        stale,
        root=project_root,
        current_contribution_fingerprint=current_fingerprint,
    )
    results["05_stale_evidence"] = {
        "validity": evidence.validity_state,
        "reasons": evidence.invalid_reasons,
    }
    (project_root / "docs" / "guide.md").write_text("guide\n", encoding="utf-8")

    auth = open_managed(
        service,
        case_id="scenario-06",
        changed_files=["demo_app/auth.py"],
    )
    add_complete_evidence(service, auth.id, actor="demo-agent")
    service.prepare_case(
        auth.id, actor="demo-agent", actor_role="contributor_agent"
    )
    before = service.storage.load_case(auth.id).state
    service.attest(
        auth.id,
        actor="demo-accountable-human",
        role="accountable_human",
        reviewed_scope=["demo_app/auth.py"],
        statement="I reviewed the exact authentication change and bound evidence.",
        timestamp="2026-07-25T02:00:00Z",
    )
    after = service.storage.load_case(auth.id).state
    results["06_pending_then_confirmed_attestation"] = {
        "before": before,
        "after": after,
    }

    ready_low_case(service, "scenario-07")
    repair = service.request_repair(
        "scenario-07",
        actor="scenario-07-verifier",
        role="maintainer_verifier",
        message="Clarify the declared agent action scope.",
        affected_obligation_ids=["O-AGENT-SCOPE"],
    )
    service.resubmit(
        "scenario-07",
        actor="demo-agent",
        role="contributor_agent",
        summary="Clarified action scope.",
        affected_obligation_ids=["O-AGENT-SCOPE"],
    )
    service.verify(
        "scenario-07",
        actor="scenario-07-verifier",
        role="maintainer_verifier",
        reason="Repair verified.",
    )
    service.decide(
        "scenario-07",
        actor="demo-maintainer",
        role="maintainer",
        decision="accept",
        reason="Accepted after repair and revalidation.",
    )
    repaired = service.storage.load_case("scenario-07")
    results["07_repair_resubmit_final_decision"] = {
        "repair_id": repair.id,
        "attempts": len(repaired.repair_requests[0].attempts),
        "final_state": repaired.state,
    }

    ready_low_case(service, "scenario-08")
    service.request_repair(
        "scenario-08",
        actor="scenario-08-verifier",
        role="maintainer_verifier",
        message="Documented prototype exception requires explicit override.",
        affected_obligation_ids=["O-SUMMARY"],
    )
    override_case = service.storage.load_case("scenario-08")
    finding_id = override_case.repair_requests[0].finding_ids[0]
    service.override(
        "scenario-08",
        actor="demo-maintainer",
        role="maintainer",
        reason="Authorized documented prototype exception.",
        obligation_ids=["O-SUMMARY"],
        finding_ids=[finding_id],
    )
    state_before_decision = service.storage.load_case("scenario-08").state
    service.decide(
        "scenario-08",
        actor="demo-maintainer",
        role="maintainer",
        decision="accept",
        reason="Accepted after separately recorded override.",
    )
    overridden = service.storage.load_case("scenario-08")
    results["08_authorized_override"] = {
        "state_before_decision": state_before_decision,
        "final_state": overridden.state,
        "override_recorded": overridden.final_decision.override,
    }

    migration_case = open_managed(
        service,
        case_id="scenario-09",
        changed_files=["docs/guide.md"],
        autonomy_profile="human_direct",
    )
    messages_path = project_root / ".agm" / "interfaces" / "messages.yml"
    messages = yaml.safe_load(messages_path.read_text(encoding="utf-8"))
    messages["messages"]["ready"] = (
        "Eligible for a human decision after a policy wording change."
    )
    messages_path.write_text(
        yaml.safe_dump(messages, sort_keys=False), encoding="utf-8"
    )
    changed_config = load_vnext_config(project_root)
    changed_service = GovernanceService(project_root, config=changed_config)
    migration = changed_service.migration_check(migration_case.id)
    results["09_policy_changes_while_open"] = migration.to_dict()

    conflict_rule = MatchedRule(
        id="conflict-match",
        rule_id="conflict-rule",
        zone="example",
        risk_level="high",
        affected_paths=["docs/guide.md"],
        selector_reasons=["deterministic conflict fixture"],
        obligation_ids=["O-SUMMARY"],
        obligation_overrides={
            "O-SUMMARY": {"evidence_type": "contradictory_type"}
        },
    )
    conflict = compile_obligations(
        service.config,
        [conflict_rule],
        [],
        autonomy_profile_id="human_direct",
        assurance_profile_id="standard",
    )
    results["10_conflicting_rules"] = {
        "obligation_status": conflict.obligations[0].status,
        "finding": conflict.findings[0].to_dict(),
    }
    return results


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="agm-vnext-demo-") as temporary:
        project_root = make_project(Path(temporary))
        results = run_scenarios(project_root)
    checks = {
        "ordinary_no_case": not results["01_ordinary_human_documentation"]["case_created"],
        "multi_risk_critical": results["03_authentication_and_configuration"]["risk"] == "critical",
        "self_modification_interaction": results["04_governance_self_modification"]["interactions"]
        == ["governance-self-modification"],
        "stale_evidence_detected": results["05_stale_evidence"]["validity"] == "stale",
        "attestation_explicit": results["06_pending_then_confirmed_attestation"]
        == {
            "before": "awaiting_human_attestation",
            "after": "awaiting_maintainer_verification",
        },
        "repair_closed": results["07_repair_resubmit_final_decision"]["final_state"]
        == "accepted",
        "override_separate": results["08_authorized_override"]["state_before_decision"]
        == "overridden",
        "policy_change_detected": results["09_policy_changes_while_open"][
            "policy_changed"
        ],
        "conflict_blocks": results["10_conflicting_rules"]["obligation_status"]
        == "policy_conflict",
    }
    output = {"ok": all(checks.values()), "checks": checks, "scenarios": results}
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
