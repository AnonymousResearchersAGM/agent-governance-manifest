from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.vnext.models import VNextError  # noqa: E402
from agm.vnext.service import GovernanceService  # noqa: E402
from agm.vnext.state_machine import allowed_actions, transition_case  # noqa: E402
from agm.vnext.storage import CaseStorage, validate_case_id  # noqa: E402


def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    shutil.copytree(ROOT / ".agm", root / ".agm")
    (root / "docs").mkdir()
    (root / "docs" / "guide.md").write_text("guide", encoding="utf-8")
    (root / "demo_app").mkdir()
    (root / "demo_app" / "auth.py").write_text("AUTH = True\n", encoding="utf-8")
    (root / "src" / "agm" / "vnext").mkdir(parents=True)
    (root / "src" / "agm" / "vnext" / "risk.py").write_text(
        "# runtime\n", encoding="utf-8"
    )
    return root


def open_docs(service: GovernanceService, case_id="docs-case"):
    case, intake = service.open_case(
        ["docs/guide.md"],
        requested_mode="declared_agent_mediated",
        actor="agent-1",
        actor_role="contributor_agent",
        case_id=case_id,
        base_commit="base",
        autonomy_profile="supervised_agent",
        timestamp="2026-07-25T00:00:00Z",
    )
    assert case is not None
    assert intake.case_required
    return case


def add_docs_evidence(service: GovernanceService, case_id="docs-case"):
    rows = [
        ("O-SUMMARY", "contribution_summary", "Updated the guide."),
        ("O-CHANGED-FILES", "changed_files", ["docs/guide.md"]),
        (
            "O-AGENT-SCOPE",
            "agent_action_scope",
            "Task-bounded workspace change under active supervision.",
        ),
    ]
    for obligation_id, evidence_type, value in rows:
        service.add_evidence(
            case_id,
            actor="agent-1",
            actor_role="contributor_agent",
            obligation_ids=[obligation_id],
            evidence_type=evidence_type,
            value=value,
            source_tool="codex",
            observed_at="2026-07-25T00:00:00Z",
        )


def add_auth_evidence(service: GovernanceService, root: Path, case_id="auth-case"):
    artifact = root / "auth-test.txt"
    artifact.write_text("1 passed", encoding="utf-8")
    rows = [
        ("O-SUMMARY", "contribution_summary", "Updated authentication behavior.", {}),
        ("O-CHANGED-FILES", "changed_files", ["demo_app/auth.py"], {}),
        ("O-RATIONALE", "rationale", "Harden token validation.", {}),
        (
            "O-AUTH-IMPACT",
            "security_auth_impact",
            "Authentication validation is affected; authorization is unchanged.",
            {},
        ),
        (
            "O-TEST-COMMAND",
            "test_command",
            "Authentication regression passed.",
            {
                "command": "python -m pytest demo_app/tests/test_auth.py",
                "environment": "Python 3.14 / Windows",
            },
        ),
        (
            "O-ARTIFACT",
            "artifact",
            "Recorded auth regression output.",
            {"artifact_path": "auth-test.txt"},
        ),
        ("O-LIMITATIONS", "known_limitations", "No network boundary is modeled.", {}),
        (
            "O-AGENT-SCOPE",
            "agent_action_scope",
            "Task-bounded workspace change under active supervision.",
            {},
        ),
    ]
    for obligation_id, evidence_type, value, extra in rows:
        service.add_evidence(
            case_id,
            actor="agent-1",
            actor_role="contributor_agent",
            obligation_ids=[obligation_id],
            evidence_type=evidence_type,
            value=value,
            source_tool="pytest" if extra else "codex",
            observed_at="2026-07-25T00:00:00Z",
            **extra,
        )


def test_case_id_rejects_path_traversal():
    with pytest.raises(VNextError, match="Case ID"):
        validate_case_id("../escape")


def test_storage_round_trips_typed_case_and_artifacts(tmp_path):
    service = GovernanceService(project(tmp_path))
    opened = open_docs(service)
    loaded = service.storage.load_case(opened.id)
    directory = service.storage.case_dir(opened.id)

    assert loaded.to_dict() == opened.to_dict()
    assert (directory / "policy_snapshot.yml").is_file()
    assert (directory / "obligations.yml").is_file()
    assert (directory / "transitions.jsonl").is_file()


def test_case_open_records_three_lifecycle_transitions(tmp_path):
    service = GovernanceService(project(tmp_path))
    case = open_docs(service)

    transitions = service.storage.read_transitions(case.id)

    assert [item.action for item in transitions] == [
        "resolve_policy",
        "compile_obligations",
        "mark_evidence_state",
    ]


def test_ordinary_documentation_path_creates_no_case_directory(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    case, intake = service.open_case(
        ["docs/guide.md"],
        requested_mode="ordinary",
        actor="human",
        actor_role="contributor",
        base_commit="base",
    )

    assert case is None
    assert intake.package_status == "no_agm_package_submitted"
    assert not (root / ".agm-work").exists()


def test_agent_cannot_make_final_decision(tmp_path):
    service = GovernanceService(project(tmp_path))
    case = open_docs(service)

    with pytest.raises(VNextError, match="not authorized"):
        transition_case(
            service.config,
            case,
            action="decide_accept",
            actor="agent-1",
            role="contributor_agent",
            reason="Agent attempted acceptance.",
        )


def test_allowed_actions_are_state_and_role_specific(tmp_path):
    service = GovernanceService(project(tmp_path))
    case = open_docs(service)

    assert allowed_actions(
        service.config, state=case.state, role="contributor_agent"
    ) == ["submit_for_verification"]
    assert "verify_evidence" not in allowed_actions(
        service.config, state=case.state, role="contributor_agent"
    )
    assert "submit_for_verification" in allowed_actions(
        service.config, state=case.state, role="contributor"
    )


def test_low_risk_end_to_end_produces_closure_receipt(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_docs(service)
    add_docs_evidence(service)

    prepared = service.prepare_case(
        "docs-case", actor="agent-1", actor_role="contributor_agent"
    )
    assert prepared.state == "awaiting_maintainer_verification"
    service.verify(
        "docs-case",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Evidence bindings independently checked.",
        timestamp="2026-07-25T01:00:00Z",
    )
    ready = service.storage.load_case("docs-case")
    assert ready.state == "ready_for_human_decision"

    service.decide(
        "docs-case",
        actor="maintainer-1",
        role="maintainer",
        decision="accept",
        reason="Human maintainer accepted after technical and governance review.",
        timestamp="2026-07-25T02:00:00Z",
    )
    closed = service.storage.load_case("docs-case")

    assert closed.state == "accepted"
    assert closed.closure_receipt is not None
    assert closed.final_decision is not None
    assert closed.final_decision.actor == "maintainer-1"
    assert (service.storage.case_dir("docs-case") / "closure_receipt.yml").is_file()


def test_critical_case_requires_explicit_human_attestation(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    case, _ = service.open_case(
        ["demo_app/auth.py"],
        requested_mode="declared_agent_mediated",
        actor="agent-1",
        actor_role="contributor_agent",
        case_id="auth-case",
        base_commit="base",
        autonomy_profile="supervised_agent",
    )
    assert case is not None
    add_auth_evidence(service, root)
    prepared = service.prepare_case(
        "auth-case", actor="agent-1", actor_role="contributor_agent"
    )
    assert prepared.state == "awaiting_human_attestation"

    with pytest.raises(VNextError, match="agents cannot attest"):
        service.attest(
            "auth-case",
            actor="agent-1",
            role="contributor_agent",
            reviewed_scope=["demo_app/auth.py"],
            statement="I reviewed the authentication change.",
        )

    attestation = service.attest(
        "auth-case",
        actor="human-1",
        role="accountable_human",
        reviewed_scope=["demo_app/auth.py"],
        statement="I reviewed the authentication-sensitive change and test evidence.",
        timestamp="2026-07-25T01:00:00Z",
    )
    assert attestation.status == "confirmed"
    assert (
        service.storage.load_case("auth-case").state
        == "awaiting_maintainer_verification"
    )


def test_attestation_is_invalidated_when_bound_evidence_changes(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    case, _ = service.open_case(
        ["demo_app/auth.py"],
        requested_mode="declared_agent_mediated",
        actor="agent-1",
        actor_role="contributor_agent",
        case_id="auth-case",
        base_commit="base",
        autonomy_profile="supervised_agent",
    )
    assert case is not None
    add_auth_evidence(service, root)
    service.prepare_case(
        "auth-case", actor="agent-1", actor_role="contributor_agent"
    )
    attestation = service.attest(
        "auth-case",
        actor="human-1",
        role="accountable_human",
        reviewed_scope=["demo_app/auth.py"],
        statement="I reviewed the authentication-sensitive change and evidence.",
    )

    service.add_evidence(
        "auth-case",
        actor="agent-1",
        actor_role="contributor_agent",
        obligation_ids=["O-AUTH-IMPACT"],
        evidence_type="security_auth_impact",
        value="A second impact statement.",
        source_tool="codex",
    )
    loaded = service.storage.load_case("auth-case")

    assert next(item for item in loaded.attestations if item.id == attestation.id).status == "invalidated"


def test_repair_resubmission_preserves_history_and_returns_to_ready(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_docs(service)
    add_docs_evidence(service)
    service.prepare_case(
        "docs-case", actor="agent-1", actor_role="contributor_agent"
    )
    service.verify(
        "docs-case",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Initial evidence verified.",
    )
    repair = service.request_repair(
        "docs-case",
        actor="verifier-1",
        role="maintainer_verifier",
        message="Clarify the declared agent action scope.",
        affected_obligation_ids=["O-AGENT-SCOPE"],
    )
    assert repair.status == "open"
    service.resubmit(
        "docs-case",
        actor="agent-1",
        role="contributor_agent",
        summary="Clarified the existing action-scope evidence.",
        affected_obligation_ids=["O-AGENT-SCOPE"],
    )
    service.verify(
        "docs-case",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Clarification verified.",
    )
    loaded = service.storage.load_case("docs-case")

    assert loaded.state == "ready_for_human_decision"
    assert loaded.repair_requests[0].attempts
    assert len(service.storage.read_transitions("docs-case")) >= 8


def test_independent_review_enforces_separation_of_duty(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    case, _ = service.open_case(
        [".agm/manifest.yml", "src/agm/vnext/risk.py"],
        requested_mode="policy_required",
        actor="agent-1",
        actor_role="contributor_agent",
        case_id="self-mod-case",
        base_commit="base",
        autonomy_profile="human_direct",
    )
    assert case is not None
    artifact = root / "policy-test.txt"
    artifact.write_text("50 passed", encoding="utf-8")
    evidence_values = {
        "O-SUMMARY": ("contribution_summary", "Updated policy and runtime."),
        "O-CHANGED-FILES": (
            "changed_files",
            [".agm/manifest.yml", "src/agm/vnext/risk.py"],
        ),
        "O-RATIONALE": ("rationale", "Implement vNext governance."),
        "O-TEST-COMMAND": ("test_command", "Policy tests passed."),
        "O-ARTIFACT": ("artifact", "Test output."),
        "O-LIMITATIONS": ("known_limitations", "Local prototype only."),
        "O-POLICY-IMPACT": (
            "policy_impact",
            "Development policy and runtime change together.",
        ),
    }
    for obligation_id, (evidence_type, value) in evidence_values.items():
        extra = {}
        if obligation_id == "O-TEST-COMMAND":
            extra = {
                "command": "python -m pytest -q",
                "environment": "Python 3.14 / Windows",
            }
        if obligation_id == "O-ARTIFACT":
            extra = {"artifact_path": "policy-test.txt"}
        service.add_evidence(
            "self-mod-case",
            actor="agent-1",
            actor_role="contributor_agent",
            obligation_ids=[obligation_id],
            evidence_type=evidence_type,
            value=value,
            source_tool="pytest" if extra else "codex",
            **extra,
        )
    service.prepare_case(
        "self-mod-case", actor="agent-1", actor_role="contributor_agent"
    )

    with pytest.raises(VNextError, match="maintainer role"):
        service.verify(
            "self-mod-case",
            actor="verifier-1",
            role="maintainer_verifier",
            reason="Attempted non-independent verification.",
        )
    with pytest.raises(VNextError, match="separation"):
        service.verify(
            "self-mod-case",
            actor="agent-1",
            role="maintainer",
            reason="Same actor attempted independent verification.",
        )

    service.verify(
        "self-mod-case",
        actor="maintainer-2",
        role="maintainer",
        reason="Independent policy/runtime verification completed.",
    )
    assert (
        service.storage.load_case("self-mod-case").state
        == "ready_for_human_decision"
    )


def test_authorized_override_is_distinct_from_final_decision(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_docs(service)
    add_docs_evidence(service)
    service.prepare_case(
        "docs-case", actor="agent-1", actor_role="contributor_agent"
    )
    service.verify(
        "docs-case",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Evidence verified.",
    )
    repair = service.request_repair(
        "docs-case",
        actor="verifier-1",
        role="maintainer_verifier",
        message="Non-blocking project exception needs a decision.",
        affected_obligation_ids=["O-SUMMARY"],
    )
    finding_id = service.storage.load_case("docs-case").repair_requests[0].finding_ids[0]
    overridden = service.override(
        "docs-case",
        actor="maintainer-1",
        role="maintainer",
        reason="Accepted documented exception for this prototype.",
        finding_ids=[finding_id],
        obligation_ids=["O-SUMMARY"],
    )

    assert overridden.state == "overridden"
    assert overridden.final_decision is None
    service.decide(
        "docs-case",
        actor="maintainer-1",
        role="maintainer",
        decision="accept",
        reason="Accepted after recording the authorized exception.",
    )
    final = service.storage.load_case("docs-case")
    assert final.final_decision is not None and final.final_decision.override
    assert repair.id in final.closure_receipt.repair_request_ids


def test_reject_evidence_records_rejection_and_repair_transition(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_docs(service)
    add_docs_evidence(service)
    service.prepare_case(
        "docs-case", actor="agent-1", actor_role="contributor_agent"
    )
    case = service.storage.load_case("docs-case")
    evidence_id = next(
        item.id
        for item in case.evidence
        if "O-SUMMARY" in item.obligation_ids
    )

    service.reject_evidence(
        "docs-case",
        actor="verifier-1",
        role="maintainer_verifier",
        evidence_id=evidence_id,
        reason="Summary does not match the observed change.",
    )
    loaded = service.storage.load_case("docs-case")

    rejected = next(item for item in loaded.evidence if item.id == evidence_id)
    assert loaded.state == "repair_requested"
    assert rejected.validity_state == "rejected"
    assert rejected.rejected_by == "verifier-1"
    assert loaded.repair_requests


def test_clarification_is_an_authorized_audited_operation(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_docs(service)
    add_docs_evidence(service)
    service.prepare_case(
        "docs-case", actor="agent-1", actor_role="contributor_agent"
    )

    repair = service.ask_clarification(
        "docs-case",
        actor="verifier-1",
        role="maintainer_verifier",
        question="Which documentation section is intentionally unchanged?",
        affected_obligation_ids=["O-SUMMARY"],
    )
    transitions = service.storage.read_transitions("docs-case")

    assert repair.status == "open"
    assert transitions[-1].action == "ask_clarification"
    assert transitions[-1].role == "maintainer_verifier"


def test_policy_conflict_can_only_be_resolved_by_authorized_role(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_docs(service)
    finding = service.record_policy_conflict(
        "docs-case",
        actor="policy-reviewer",
        role="policy_steward",
        message="Two policy authorities disagree about the summary obligation.",
        affected_obligation_ids=["O-SUMMARY"],
    )

    with pytest.raises(VNextError, match="not authorized"):
        service.resolve_policy_conflict(
            "docs-case",
            actor="agent-1",
            role="contributor_agent",
            finding_id=finding.id,
            resolution="Agent attempted resolution.",
        )

    resolved = service.resolve_policy_conflict(
        "docs-case",
        actor="policy-reviewer",
        role="policy_steward",
        finding_id=finding.id,
        resolution="Canonical project policy was clarified by the policy steward.",
    )
    loaded = service.storage.load_case("docs-case")

    assert resolved.status == "resolved"
    assert loaded.state == "resubmitted"
    assert service.storage.read_transitions("docs-case")[-1].action == "resolve_policy_conflict"
