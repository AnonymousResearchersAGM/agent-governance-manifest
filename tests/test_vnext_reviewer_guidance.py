from __future__ import annotations

import copy
import re
import shutil
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.vnext.guidance import (  # noqa: E402
    ActorContext,
    build_no_package_guidance,
    build_reviewer_guidance,
    preview_reviewer_action,
    render_guidance_html,
)
from agm.vnext.models import VNextError  # noqa: E402
from agm.vnext.repair import create_finding  # noqa: E402
from agm.vnext.service import GovernanceService  # noqa: E402
from agm.vnext.state_machine import allowed_actions  # noqa: E402
from agm.vnext.ui import handler_class  # noqa: E402


def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    shutil.copytree(ROOT / ".agm", root / ".agm")
    shutil.copytree(ROOT / "skills", root / "skills")
    (root / "docs").mkdir()
    (root / "docs" / "guide.md").write_text("guide", encoding="utf-8")
    (root / "demo_app").mkdir()
    (root / "demo_app" / "auth.py").write_text(
        "AUTH = True\n", encoding="utf-8"
    )
    (root / "demo_app" / "config.py").write_text(
        "SECURE = True\n", encoding="utf-8"
    )
    (root / "src" / "agm" / "vnext").mkdir(parents=True)
    (root / "src" / "agm" / "vnext" / "risk.py").write_text(
        "# runtime\n", encoding="utf-8"
    )
    return root


def open_case(
    service: GovernanceService,
    changed_files: list[str],
    *,
    case_id: str,
    autonomy_profile: str = "human_direct",
):
    case, _ = service.open_case(
        changed_files,
        requested_mode="declared_agent_mediated",
        actor="agent-1",
        actor_role="contributor_agent",
        case_id=case_id,
        base_commit="base",
        autonomy_profile=autonomy_profile,
        diff_material="initial",
        timestamp="2026-07-25T00:00:00Z",
    )
    assert case is not None
    return case


EVIDENCE_VALUES = {
    "contribution_summary": "Implemented the described contribution.",
    "changed_files": ["docs/guide.md"],
    "rationale": "The change is needed for the requested behavior.",
    "test_explanation": "Documentation inspection completed.",
    "test_command": "The scoped regression tests passed.",
    "artifact": "Recorded local test output.",
    "known_limitations": "No distributed identity integration is modeled.",
    "security_auth_impact": (
        "Authentication behavior changes; authorization impact was checked."
    ),
    "policy_impact": "Policy compatibility and migration impact were assessed.",
    "agent_action_scope": (
        "Task-bounded workspace action under active human supervision; "
        "no undeclared delegation."
    ),
}


def add_all_evidence(
    service: GovernanceService,
    case_id: str,
    root: Path,
) -> None:
    case = service.storage.load_case(case_id)
    artifact = root / f"{case_id}-test-output.txt"
    artifact.write_text("all checks passed", encoding="utf-8")
    for obligation in case.obligations:
        if obligation.type != "evidence":
            continue
        value = EVIDENCE_VALUES[obligation.evidence_type]
        if obligation.evidence_type == "changed_files":
            value = list(case.changed_files)
        extra = {}
        if obligation.evidence_type == "test_command":
            extra = {
                "command": "python -m pytest -q",
                "environment": "Python / test fixture",
            }
        elif obligation.evidence_type == "artifact":
            extra = {"artifact_path": artifact.name}
        service.add_evidence(
            case_id,
            actor="agent-1",
            actor_role="contributor_agent",
            obligation_ids=[obligation.obligation_id],
            evidence_type=obligation.evidence_type,
            value=value,
            source_tool="pytest",
            observed_at="2026-07-25T00:10:00Z",
            **extra,
        )


def guidance(
    service: GovernanceService,
    case_id: str,
    role: str = "maintainer",
    actor: str = "human-maintainer",
):
    case = service.storage.load_case(case_id)
    return build_reviewer_guidance(
        case,
        service.config,
        service.storage.read_transitions(case_id),
        ActorContext(actor=actor, role=role),
        migration_diagnostic=service.migration_check(case_id),
    )


def prepare_ready_docs(
    service: GovernanceService,
    root: Path,
    case_id: str = "docs-ready",
) -> None:
    open_case(service, ["docs/guide.md"], case_id=case_id)
    add_all_evidence(service, case_id, root)
    service.prepare_case(
        case_id,
        actor="agent-1",
        actor_role="contributor_agent",
    )
    service.verify(
        case_id,
        actor="verifier-1",
        role="maintainer_verifier",
        reason="All lightweight bindings checked.",
    )


def test_workflow_maps_internal_lifecycle_to_exactly_five_steps(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_case(service, ["docs/guide.md"], case_id="workflow")

    view = guidance(service, "workflow")

    assert [item.title for item in view.workflow_steps] == [
        "系统识别要求",
        "贡献者准备材料",
        "负责人确认",
        "维护者检查",
        "人类维护者最终决定",
    ]
    assert view.workflow_steps[0].status == "completed"
    assert view.workflow_steps[1].status == "current"
    assert view.workflow_steps[2].status == "skipped"


def test_missing_evidence_is_distinct_from_not_started_attestation(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_case(
        service,
        ["demo_app/auth.py"],
        case_id="missing-not-started",
    )

    view = guidance(service, "missing-not-started")
    rows = {
        item.obligation_id: item
        for item in view.requirement_comparisons
    }

    assert rows["O-AUTH-IMPACT"].result == "missing"
    assert rows["O-HUMAN-ATTEST"].result == "not_started"


def test_stale_evidence_is_needs_update_not_missing(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_case(service, ["docs/guide.md"], case_id="stale")
    add_all_evidence(service, "stale", service.root)
    case = service.storage.load_case("stale")
    summary_evidence = next(
        item for item in case.evidence if "O-SUMMARY" in item.obligation_ids
    )
    summary_evidence.validity_state = "stale"
    summary_evidence.invalid_reasons = [
        "evidence is bound to a stale contribution fingerprint"
    ]

    view = build_reviewer_guidance(
        case,
        service.config,
        service.storage.read_transitions(case.id),
        ActorContext("human-maintainer", "maintainer"),
    )
    row = next(
        item
        for item in view.requirement_comparisons
        if item.obligation_id == "O-SUMMARY"
    )

    assert row.result == "needs_update"
    assert row.evidence_ids == [summary_evidence.id]


def test_invalidated_attestation_is_explained_and_traced(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    open_case(service, ["demo_app/auth.py"], case_id="invalid-attestation")
    add_all_evidence(service, "invalid-attestation", root)
    service.prepare_case(
        "invalid-attestation",
        actor="agent-1",
        actor_role="contributor_agent",
    )
    attestation = service.attest(
        "invalid-attestation",
        actor="accountable-1",
        role="accountable_human",
        reviewed_scope=["demo_app/auth.py"],
        statement="I reviewed the current authentication change and evidence.",
    )
    service.invalidate_attestation(
        "invalid-attestation",
        actor="verifier-1",
        role="maintainer_verifier",
        attestation_id=attestation.id,
        reason="The confirmation refers to an obsolete security assessment.",
    )

    view = guidance(service, "invalid-attestation")
    row = next(
        item
        for item in view.requirement_comparisons
        if item.obligation_id == "O-HUMAN-ATTEST"
    )

    assert row.result == "invalid"
    assert any(
        item.technical_term == "invalidated attestation"
        for item in view.explanations
    )
    assert any(
        ref.object_id == attestation.id for ref in row.traceability
    )


def test_blocking_and_nonblocking_findings_have_different_results(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    case = open_case(service, ["docs/guide.md"], case_id="finding-levels")
    add_all_evidence(service, case.id, root)
    case = service.storage.load_case(case.id)
    create_finding(
        case,
        code="blocking_problem",
        severity="high",
        message="The summary conflicts with the observed diff.",
        blocking=True,
        affected_obligation_ids=["O-SUMMARY"],
    )
    create_finding(
        case,
        code="warning_only",
        severity="low",
        message="The file list wording could be clearer.",
        blocking=False,
        affected_obligation_ids=["O-CHANGED-FILES"],
    )

    view = build_reviewer_guidance(
        case,
        service.config,
        service.storage.read_transitions(case.id),
        ActorContext("human-maintainer", "maintainer"),
    )
    rows = {
        item.obligation_id: item.result
        for item in view.requirement_comparisons
    }

    assert rows["O-SUMMARY"] == "blocked"
    assert rows["O-CHANGED-FILES"] == "needs_attention"


def test_lightweight_path_keeps_final_decision_human(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    open_case(service, ["docs/guide.md"], case_id="lightweight")

    view = guidance(service, "lightweight")

    assert view.summary.path_kind == "lightweight"
    assert len(view.requirement_comparisons) == 2
    assert view.workflow_steps[2].status == "skipped"
    assert view.workflow_steps[3].status == "pending"
    assert view.summary.next_authorized_actor_roles != ["maintainer"]


def test_ordinary_no_package_is_not_rendered_as_failure(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    simulation = service.simulate(
        ["docs/guide.md"],
        requested_mode="ordinary",
        autonomy_profile="human_direct",
    )

    view = build_no_package_guidance(
        simulation,
        service.config,
        ActorContext("human-maintainer", "maintainer"),
    )

    assert view.summary.raw_readiness == "no_agm_package_submitted"
    assert view.summary.blocking_issue_count == 0
    assert view.requirement_comparisons[0].result == "not_applicable"
    assert "不要求完整 AGM 材料" in view.explanations[0].title


def test_multi_risk_view_preserves_union_and_interaction(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_case(
        service,
        ["demo_app/auth.py", "demo_app/config.py"],
        case_id="multi-risk",
    )

    view = guidance(service, "multi-risk")
    obligations = {
        item.obligation_id for item in view.requirement_comparisons
    }

    assert any("authentication" in item for item in view.summary.risk_areas)
    assert any("configuration" in item for item in view.summary.risk_areas)
    assert {
        "O-AUTH-IMPACT",
        "O-TEST-COMMAND",
        "O-INDEPENDENT-REVIEW",
        "O-HUMAN-ATTEST",
    } <= obligations
    assert "authentication-configuration" in {
        item
        for row in view.requirement_comparisons
        for item in row.interaction_ids
    }


def test_scoped_material_repair_retains_unaffected_evidence(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    prepare_ready_docs(service, root, case_id="scoped")
    service.request_repair(
        "scoped",
        actor="verifier-1",
        role="maintainer_verifier",
        message="Clarify the contribution summary only.",
        affected_obligation_ids=["O-SUMMARY"],
    )
    before = service.storage.load_case("scoped")
    changed_id = next(
        item.id
        for item in before.evidence
        if "O-SUMMARY" in item.obligation_ids
    )
    unaffected_ids = {
        item.id
        for item in before.evidence
        if "O-SUMMARY" not in item.obligation_ids
    }

    service.resubmit(
        "scoped",
        actor="agent-1",
        role="contributor_agent",
        summary="Updated the contribution summary.",
        affected_obligation_ids=["O-SUMMARY"],
        diff_material="material change to summary scope",
        change_classification="material",
        change_reason="Only the summary-bearing scope changed.",
    )
    after = service.storage.load_case("scoped")
    attempt = after.repair_requests[0].attempts[-1]

    assert changed_id in attempt["stale_evidence_ids"]
    assert unaffected_ids <= set(attempt["retained_evidence_ids"])
    assert all(
        item.validity_state in {"valid", "verified"}
        for item in after.evidence
        if item.id in unaffected_ids
    )


def test_material_change_invalidates_only_intersecting_attestation_scope(
    tmp_path,
):
    root = project(tmp_path)
    service = GovernanceService(root)
    open_case(
        service,
        ["demo_app/auth.py", "demo_app/config.py"],
        case_id="material-attestation",
    )
    add_all_evidence(service, "material-attestation", root)
    service.prepare_case(
        "material-attestation",
        actor="agent-1",
        actor_role="contributor_agent",
    )
    attestation = service.attest(
        "material-attestation",
        actor="accountable-1",
        role="accountable_human",
        reviewed_scope=["demo_app/auth.py"],
        statement="I reviewed the authentication scope and current evidence.",
    )
    service.request_repair(
        "material-attestation",
        actor="human-maintainer",
        role="maintainer",
        message="Authentication impact changed materially.",
        affected_obligation_ids=["O-AUTH-IMPACT"],
    )
    service.resubmit(
        "material-attestation",
        actor="agent-1",
        role="contributor_agent",
        summary="Changed authentication behavior.",
        affected_obligation_ids=["O-AUTH-IMPACT"],
        diff_material="new authentication behavior",
        change_classification="material",
        change_reason="Authentication semantics changed.",
    )
    loaded = service.storage.load_case("material-attestation")
    recorded = next(
        item for item in loaded.attestations if item.id == attestation.id
    )
    attempt = loaded.repair_requests[-1].attempts[-1]

    assert recorded.status == "invalidated"
    assert attestation.id in attempt["invalidated_attestation_ids"]
    assert any(
        item.id in attempt["retained_evidence_ids"]
        for item in loaded.evidence
        if "O-AUTH-IMPACT" not in item.obligation_ids
    )


def test_non_material_change_retains_confirmed_attestation(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    open_case(
        service,
        ["demo_app/auth.py"],
        case_id="nonmaterial-attestation",
    )
    add_all_evidence(service, "nonmaterial-attestation", root)
    service.prepare_case(
        "nonmaterial-attestation",
        actor="agent-1",
        actor_role="contributor_agent",
    )
    attestation = service.attest(
        "nonmaterial-attestation",
        actor="accountable-1",
        role="accountable_human",
        reviewed_scope=["demo_app/auth.py"],
        statement="I reviewed the authentication scope and current evidence.",
    )
    service.request_repair(
        "nonmaterial-attestation",
        actor="human-maintainer",
        role="maintainer",
        message="Clarify wording without changing behavior.",
        affected_obligation_ids=["O-AUTH-IMPACT"],
    )
    service.resubmit(
        "nonmaterial-attestation",
        actor="agent-1",
        role="contributor_agent",
        summary="Clarified wording only.",
        affected_obligation_ids=["O-AUTH-IMPACT"],
        diff_material="wording-only fingerprint change",
        change_classification="non_material",
        change_reason="No authentication behavior or reviewed scope changed.",
    )
    loaded = service.storage.load_case("nonmaterial-attestation")
    recorded = next(
        item for item in loaded.attestations if item.id == attestation.id
    )

    assert recorded.status == "confirmed"
    assert (
        recorded.retained_for_contribution_fingerprint
        == loaded.contribution_fingerprint
    )
    assert loaded.obligation("O-HUMAN-ATTEST").status == "satisfied"


def test_unauthorized_contributor_agent_action_is_visible_and_rejected(
    tmp_path,
):
    root = project(tmp_path)
    service = GovernanceService(root)
    open_case(service, ["docs/guide.md"], case_id="unauthorized")
    add_all_evidence(service, "unauthorized", root)
    service.prepare_case(
        "unauthorized",
        actor="agent-1",
        actor_role="contributor_agent",
    )
    before = service.storage.load_case("unauthorized").state

    view = guidance(
        service,
        "unauthorized",
        role="contributor_agent",
        actor="agent-1",
    )
    unavailable = {
        item.action: item for item in view.unavailable_actions
    }
    with pytest.raises(VNextError, match="not authorized"):
        service.verify(
            "unauthorized",
            actor="agent-1",
            role="contributor_agent",
            reason="Agent attempted maintainer verification.",
        )

    assert "verify_evidence" in unavailable
    assert (
        unavailable["verify_evidence"].reason
        == "当前角色没有“检查提交材料”的权限。"
        "可以执行这一步的角色：人类维护者、维护者侧检查人员或项目规则负责人。"
    )
    assert "maintainer" in unavailable["verify_evidence"].next_actor_roles
    assert service.storage.load_case("unauthorized").state == before


def test_action_preview_is_pure_and_does_not_mutate_case(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    open_case(service, ["docs/guide.md"], case_id="preview")
    add_all_evidence(service, "preview", root)
    service.prepare_case(
        "preview",
        actor="agent-1",
        actor_role="contributor_agent",
    )
    case = service.storage.load_case("preview")
    before = copy.deepcopy(case.to_dict())
    transitions = service.storage.read_transitions(case.id)

    preview = preview_reviewer_action(
        case,
        service.config,
        transitions,
        ActorContext("verifier-1", "maintainer_verifier"),
        "verify_evidence",
        {"reason": "Preview only."},
    )

    assert preview.authorized
    assert preview.mutates_case is False
    assert case.to_dict() == before
    assert service.storage.load_case(case.id).to_dict() == before


def test_available_mutations_match_backend_permission_and_transition(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    open_case(service, ["docs/guide.md"], case_id="available")
    add_all_evidence(service, "available", root)
    service.prepare_case(
        "available",
        actor="agent-1",
        actor_role="contributor_agent",
    )
    case = service.storage.load_case("available")
    view = guidance(
        service,
        "available",
        role="maintainer_verifier",
        actor="verifier-1",
    )
    backend = set(
        allowed_actions(
            service.config,
            state=case.state,
            role="maintainer_verifier",
        )
    )

    for item in view.available_actions:
        if item.mutates_state:
            assert item.action in backend
            assert item.action in service.config.permissions[
                "maintainer_verifier"
            ]


def test_unavailable_actions_always_include_readable_reason(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_case(service, ["docs/guide.md"], case_id="reasons")

    view = guidance(
        service,
        "reasons",
        role="contributor_agent",
        actor="agent-1",
    )

    assert view.unavailable_actions
    assert all(item.reason.strip() for item in view.unavailable_actions)
    assert all(item.next_actor_roles for item in view.unavailable_actions)


def test_final_decision_remains_human_authorized(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    prepare_ready_docs(service, root, case_id="final-authority")

    contributor_view = guidance(
        service,
        "final-authority",
        role="contributor_agent",
        actor="agent-1",
    )
    maintainer_view = guidance(
        service,
        "final-authority",
        role="maintainer",
        actor="human-maintainer",
    )

    assert "decide_accept" in {
        item.action for item in contributor_view.unavailable_actions
    }
    assert "decide_accept" in {
        item.action for item in maintainer_view.available_actions
    }
    assert maintainer_view.summary.raw_readiness == (
        "eligible_for_human_decision"
    )
    assert maintainer_view.summary.raw_state != "accepted"


def test_technical_details_and_every_row_remain_traceable(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_case(
        service,
        ["demo_app/auth.py", "demo_app/config.py"],
        case_id="trace",
    )

    view = guidance(service, "trace")

    assert {
        "raw_state",
        "readiness",
        "risk_rules",
        "autonomy_profile",
        "interaction_rules",
        "compiled_obligations",
        "evidence_records",
        "attestation_records",
        "verification_records",
        "findings",
        "repair_requests",
        "contribution_fingerprint",
        "policy_fingerprint",
        "transition_history",
        "closure_receipt",
        "raw_english_specification_text",
    } <= set(view.technical_details)
    assert all(item.traceability for item in view.requirement_comparisons)


def test_guidance_html_has_five_steps_table_collapsed_details_and_no_answer(
    tmp_path,
):
    service = GovernanceService(project(tmp_path))
    open_case(service, ["docs/guide.md"], case_id="html")
    view = guidance(service, "html")

    rendered = render_guidance_html(view, action_token="token")

    assert rendered.count('class="workflow-step ') == 5
    assert "<th>检查项</th>" in rendered
    assert '<details class="technical-details">' in rendered
    assert '<details class="technical-details" open' not in rendered
    assert "status-current" in rendered
    assert "推荐操作" not in rendered
    assert "预览操作影响" in rendered


def test_local_panel_requires_preview_before_state_mutation(tmp_path):
    root = project(tmp_path)
    service = GovernanceService(root)
    open_case(service, ["docs/guide.md"], case_id="two-stage")
    add_all_evidence(service, "two-stage", root)
    service.prepare_case(
        "two-stage",
        actor="agent-1",
        actor_role="contributor_agent",
    )
    token = "test-action-token"
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        handler_class(
            service,
            case_id="two-stage",
            audience="maintainer",
            action_token=token,
            current_actor=ActorContext(
                "verifier-1", "maintainer_verifier"
            ),
        ),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/"
    form = {
        "action_token": token,
        "action": "verify_evidence",
        "actor": "verifier-1",
        "role": "maintainer_verifier",
        "obligation": "",
        "object_id": "",
        "reason": "Bindings checked in the two-stage UI test.",
    }
    try:
        preview_response = urlopen(
            Request(
                url,
                data=urlencode(form).encode("utf-8"),
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                },
            ),
            timeout=5,
        ).read().decode("utf-8")
        assert "操作前预览" in preview_response
        assert (
            service.storage.load_case("two-stage").state
            == "awaiting_maintainer_verification"
        )
        match = re.search(
            r'name="preview_fingerprint" value="([^"]+)"',
            preview_response,
        )
        assert match
        confirm_form = {
            **form,
            "confirm": "execute",
            "preview_fingerprint": match.group(1),
        }
        urlopen(
            Request(
                url,
                data=urlencode(confirm_form).encode("utf-8"),
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                },
            ),
            timeout=5,
        ).read()
        assert (
            service.storage.load_case("two-stage").state
            == "ready_for_human_decision"
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
