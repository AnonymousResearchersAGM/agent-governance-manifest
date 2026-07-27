from __future__ import annotations

import copy
import json
import re
import shutil
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.vnext.guidance import (  # noqa: E402
    ActorContext,
    TraceReference,
    build_context_selector_options,
    build_no_package_guidance,
    build_reviewer_guidance,
    preview_reviewer_action,
    render_guidance_html,
    resolve_selector_tokens,
)
from agm.vnext.guidance.diagnostics import (  # noqa: E402
    OBLIGATION_PRESENTATION,
    build_requirement_comparisons,
    obligation_presentation,
)
from agm.vnext.guidance.reason_presentations import (  # noqa: E402
    UNKNOWN_REASON_FALLBACK,
    present_reason,
)
from agm.vnext.models import (  # noqa: E402
    CompiledObligation,
    VNextError,
)
from agm.vnext.repair import create_finding  # noqa: E402
from agm.vnext.service import GovernanceService  # noqa: E402


EVIDENCE_VALUES = {
    "contribution_summary": "Implemented the described contribution.",
    "changed_files": ["docs/guide.md"],
    "rationale": "The change is needed for the requested behavior.",
    "test_explanation": "The scoped behavior was inspected and tested.",
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
    return root


def open_case(
    service: GovernanceService,
    case_id: str,
    changed_files: list[str] | None = None,
    *,
    autonomy_profile: str = "human_direct",
):
    case, _ = service.open_case(
        changed_files or ["docs/guide.md"],
        requested_mode="declared_agent_mediated",
        actor="agent-1",
        actor_role="contributor_agent",
        case_id=case_id,
        base_commit="base",
        autonomy_profile=autonomy_profile,
        diff_material=f"{case_id}:initial",
        timestamp="2026-07-26T00:00:00Z",
    )
    assert case is not None
    return case


def add_all_evidence(
    service: GovernanceService, case_id: str
) -> None:
    case = service.storage.load_case(case_id)
    artifact = service.root / f"{case_id}-artifact.txt"
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
                "environment": "Python test fixture",
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
            observed_at="2026-07-26T00:05:00Z",
            **extra,
        )


def view(
    service: GovernanceService,
    case_id: str,
    *,
    actor: str = "human-maintainer",
    role: str = "maintainer",
):
    return service.reviewer_guidance(
        case_id, actor=actor, role=role
    )


def prepare_docs_for_verification(
    service: GovernanceService, case_id: str
) -> None:
    open_case(service, case_id)
    add_all_evidence(service, case_id)
    service.prepare_case(
        case_id, actor="agent-1", actor_role="contributor_agent"
    )


def test_all_twelve_canonical_obligations_have_plain_chinese_presentations():
    assert set(OBLIGATION_PRESENTATION) == {
        "O-SUMMARY",
        "O-CHANGED-FILES",
        "O-RATIONALE",
        "O-TEST-EXPLANATION",
        "O-TEST-COMMAND",
        "O-ARTIFACT",
        "O-LIMITATIONS",
        "O-AUTH-IMPACT",
        "O-POLICY-IMPACT",
        "O-AGENT-SCOPE",
        "O-HUMAN-ATTEST",
        "O-INDEPENDENT-REVIEW",
    }
    assert all(
        name.strip() and plain.strip()
        for name, plain in OBLIGATION_PRESENTATION.values()
    )


def test_unknown_obligation_uses_nonempty_fallback_and_keeps_english():
    obligation = CompiledObligation(
        id="obl-unknown",
        obligation_id="O-FUTURE",
        source_rule_ids=["future-rule"],
        type="evidence",
        severity="medium",
        blocking=True,
        verifier_roles=["maintainer"],
        evidence_type="future_evidence",
        description="Future canonical English requirement.",
    )

    name, plain = obligation_presentation(obligation)

    assert name and plain
    assert name == "某项项目要求"
    assert "O-FUTURE" not in name
    assert obligation.obligation_id == "O-FUTURE"
    assert obligation.description == "Future canonical English requirement."


def test_comparison_carries_plain_and_raw_text_without_policy_rewrite(
    tmp_path,
):
    service = GovernanceService(project(tmp_path))
    case = open_case(service, "plain-raw")
    original = {
        item.obligation_id: item.description for item in case.obligations
    }

    rows = build_requirement_comparisons(case)

    assert all(item.display_name and item.reference_plain for item in rows)
    assert {
        item.obligation_id: item.reference_english for item in rows
    } == original
    assert {
        item.obligation_id: item.description for item in case.obligations
    } == original


def test_responsibility_evidence_incomplete_is_contributor_side(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_case(service, "incomplete")

    guidance = view(service, "incomplete")

    assert guidance.responsibility.primary_roles == [
        "contributor",
        "contributor_agent",
    ]
    assert guidance.responsibility.blocking_items


def test_responsibility_pending_attestation_is_accountable_human(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_case(service, "attest", ["demo_app/auth.py"])
    add_all_evidence(service, "attest")
    service.prepare_case(
        "attest", actor="agent-1", actor_role="contributor_agent"
    )

    guidance = view(service, "attest")

    assert guidance.summary.raw_state == "awaiting_human_attestation"
    assert guidance.responsibility.primary_roles == ["accountable_human"]


def test_resubmitted_but_stale_material_remains_contributor_side(tmp_path):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "resubmit-incomplete")
    service.verify(
        "resubmit-incomplete",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Initial check.",
    )
    service.request_repair(
        "resubmit-incomplete",
        actor="verifier-1",
        role="maintainer_verifier",
        message="Update summary.",
        affected_obligation_ids=["O-SUMMARY"],
    )
    service.resubmit(
        "resubmit-incomplete",
        actor="agent-1",
        role="contributor_agent",
        summary="Declared changed summary without replacement evidence.",
        affected_obligation_ids=["O-SUMMARY"],
        diff_material="resubmit-incomplete:changed",
        change_classification="material",
        change_reason="Summary-bearing contribution changed.",
    )

    guidance = view(
        service,
        "resubmit-incomplete",
        actor="verifier-1",
        role="maintainer_verifier",
    )
    row = next(
        item
        for item in guidance.requirement_comparisons
        if item.obligation_id == "O-SUMMARY"
    )

    assert row.material_status == "stale"
    assert guidance.responsibility.primary_roles == [
        "contributor",
        "contributor_agent",
    ]


def test_resubmitted_valid_material_waits_for_scoped_revalidation(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_case(
        service,
        "resubmit-ready",
        autonomy_profile="supervised_agent",
    )
    add_all_evidence(service, "resubmit-ready")
    service.prepare_case(
        "resubmit-ready",
        actor="agent-1",
        actor_role="contributor_agent",
    )
    service.verify(
        "resubmit-ready",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Initial check.",
    )
    service.request_repair(
        "resubmit-ready",
        actor="verifier-1",
        role="maintainer_verifier",
        message="Clarify delegation wording only.",
        affected_obligation_ids=["O-AGENT-SCOPE"],
    )
    service.resubmit(
        "resubmit-ready",
        actor="agent-1",
        role="contributor_agent",
        summary="Clarified wording.",
        affected_obligation_ids=["O-AGENT-SCOPE"],
        diff_material="resubmit-ready:initial",
        change_classification="non_material",
        change_reason="Wording only.",
    )

    guidance = view(
        service,
        "resubmit-ready",
        actor="verifier-1",
        role="maintainer_verifier",
    )
    row = next(
        item
        for item in guidance.requirement_comparisons
        if item.obligation_id == "O-AGENT-SCOPE"
    )

    assert row.material_status in {"provided", "retained", "verified"}
    assert row.workflow_status == "awaiting_revalidation"
    assert "重新检查" in row.workflow_status_label
    assert "maintainer_verifier" in guidance.responsibility.primary_roles
    preview = service.preview_reviewer_action(
        "resubmit-ready",
        actor="verifier-1",
        role="maintainer_verifier",
        action="verify_evidence",
        parameters={
            "obligation_ids": ["O-AGENT-SCOPE"],
            "reason": "Scoped revalidation.",
        },
    )
    assert any(
        effect.target == "指定修复请求"
        and effect.after == "resolved"
        for effect in preview.effects
    )
    service.verify(
        "resubmit-ready",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Scoped revalidation.",
        obligation_ids=["O-AGENT-SCOPE"],
    )
    assert (
        service.storage.load_case("resubmit-ready")
        .repair_requests[-1]
        .status
        == "resolved"
    )


def test_ready_for_decision_responsibility_is_human_maintainer(tmp_path):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "ready")
    service.verify(
        "ready",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Bindings checked.",
    )

    guidance = view(service, "ready")

    assert guidance.summary.raw_state == "ready_for_human_decision"
    assert guidance.responsibility.primary_roles == ["maintainer"]


def test_material_and_workflow_statuses_are_independent(tmp_path):
    service = GovernanceService(project(tmp_path))
    case = open_case(service, "status-model")
    add_all_evidence(service, "status-model")
    loaded = service.storage.load_case(case.id)
    rows = build_requirement_comparisons(loaded)
    provided = next(item for item in rows if item.obligation_id == "O-SUMMARY")
    evidence = next(
        item for item in loaded.evidence if "O-SUMMARY" in item.obligation_ids
    )
    evidence.retained_for_contribution_fingerprint = (
        loaded.contribution_fingerprint
    )
    evidence.retention_reason = "Unaffected scope."
    retained = next(
        item
        for item in build_requirement_comparisons(loaded)
        if item.obligation_id == "O-SUMMARY"
    )
    loaded.obligation("O-SUMMARY").status = "overridden"
    overridden = next(
        item
        for item in build_requirement_comparisons(loaded)
        if item.obligation_id == "O-SUMMARY"
    )

    assert provided.material_status == "provided"
    assert retained.material_status == "retained"
    assert overridden.material_status == "overridden"


def test_action_grouping_limits_current_cards_and_folds_unavailable(tmp_path):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "grouping")

    guidance = view(
        service,
        "grouping",
        actor="verifier-1",
        role="maintainer_verifier",
    )
    rendered = render_guidance_html(guidance, action_token="token")

    assert len(guidance.current_relevant_actions) <= 4
    assert all(
        item.group == "current_relevant"
        for item in guidance.current_relevant_actions
    )
    assert guidance.unavailable_action_summary
    assert (
        f"<summary>{guidance.unavailable_action_summary}</summary>"
        in rendered
    )


def test_context_selectors_reject_forged_wrong_case_and_wrong_action(
    tmp_path,
):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "selector-a")
    open_case(service, "selector-b")
    case_a = service.storage.load_case("selector-a")
    case_b = service.storage.load_case("selector-b")
    option = build_context_selector_options(
        case_a, "verify_evidence"
    )[0]

    resolved = resolve_selector_tokens(
        case_a, "verify_evidence", option.selector_token
    )

    assert resolved["obligation_ids"]
    with pytest.raises(VNextError, match="不属于当前案例"):
        resolve_selector_tokens(
            case_a, "verify_evidence", "sel-forged"
        )
    with pytest.raises(VNextError, match="不属于当前案例"):
        resolve_selector_tokens(
            case_b, "verify_evidence", option.selector_token
        )
    with pytest.raises(VNextError, match="不属于当前案例"):
        resolve_selector_tokens(
            case_a, "request_repair", option.selector_token
        )


def test_web_html_uses_opaque_selectors_and_has_no_internal_id_input(
    tmp_path,
):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "selector-html")
    guidance = view(
        service,
        "selector-html",
        actor="verifier-1",
        role="maintainer_verifier",
    )

    rendered = render_guidance_html(guidance, action_token="token")

    assert 'name="selector_token"' in rendered
    assert 'name="object_id"' not in rendered
    assert 'name="obligation"' not in rendered
    assert "手填内部 ID" not in rendered


def test_utility_actions_are_traceable_and_do_not_mutate_case(tmp_path):
    service = GovernanceService(project(tmp_path))
    open_case(service, "utilities")
    before_case = copy.deepcopy(
        service.storage.load_case("utilities").to_dict()
    )
    before_transitions = [
        item.to_dict()
        for item in service.storage.read_transitions("utilities")
    ]

    guidance = view(service, "utilities")

    assert {
        "copy_missing_requirements",
        "export_contributor_checklist",
        "export_reviewer_summary",
        "view_change_scope",
        "copy_handoff_note",
    } == {item.action_id for item in guidance.utility_actions}
    assert all(not item.state_changing for item in guidance.utility_actions)
    assert all(item.output.strip() for item in guidance.utility_actions)
    assert any(item.trace_refs for item in guidance.utility_actions)
    assert service.storage.load_case("utilities").to_dict() == before_case
    assert [
        item.to_dict()
        for item in service.storage.read_transitions("utilities")
    ] == before_transitions


def test_each_transition_is_attached_to_one_primary_workflow_step(tmp_path):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "trace-map")
    guidance = view(
        service,
        "trace-map",
        actor="verifier-1",
        role="maintainer_verifier",
    )
    transitions = service.storage.read_transitions("trace-map")
    attached = [
        trace.object_id
        for step in guidance.workflow_steps
        for trace in step.traceability
        if trace.kind == "state_transition"
    ]

    assert sorted(attached) == sorted(item.id for item in transitions)
    assert len(attached) == len(set(attached))
    assert all(
        trace.relationship.startswith("primary:")
        for step in guidance.workflow_steps
        for trace in step.traceability
        if trace.kind == "state_transition"
    )


def test_preview_matches_execution_and_updates_responsibility_without_mutation(
    tmp_path,
):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "preview-accuracy")
    case = service.storage.load_case("preview-accuracy")
    before = copy.deepcopy(case.to_dict())
    transitions_before = service.storage.read_transitions(case.id)

    preview = preview_reviewer_action(
        case,
        service.config,
        transitions_before,
        ActorContext("verifier-1", "maintainer_verifier"),
        "verify_evidence",
        {"reason": "Preview bindings."},
    )

    assert case.to_dict() == before
    assert len(service.storage.read_transitions(case.id)) == len(
        transitions_before
    )
    assert preview.responsibility_after.primary_roles == ["maintainer"]
    assert preview.final_acceptance_recorded is False
    assert preview.final_acceptance_still_required is True
    service.verify(
        case.id,
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Execute bindings.",
    )
    assert service.storage.load_case(case.id).state == preview.target_state


def test_unauthorized_preview_keeps_state_and_explains_authority(tmp_path):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "preview-denied")
    case = service.storage.load_case("preview-denied")

    preview = preview_reviewer_action(
        case,
        service.config,
        service.storage.read_transitions(case.id),
        ActorContext("agent-1", "contributor_agent"),
        "verify_evidence",
        {"reason": "Unauthorized."},
    )

    assert preview.authorized is False
    assert preview.target_state == case.state
    assert "权限" in preview.authorization_reason
    assert preview.responsibility_after == preview.responsibility_before


def test_backend_rejects_resubmission_outside_open_repair_scope(tmp_path):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "wrong-scope")
    service.verify(
        "wrong-scope",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Initial.",
    )
    service.request_repair(
        "wrong-scope",
        actor="verifier-1",
        role="maintainer_verifier",
        message="Summary only.",
        affected_obligation_ids=["O-SUMMARY"],
    )

    with pytest.raises(VNextError, match="outside the open repair scope"):
        service.resubmit(
            "wrong-scope",
            actor="agent-1",
            role="contributor_agent",
            summary="Wrong scope.",
            affected_obligation_ids=["O-CHANGED-FILES"],
            change_classification="non_material",
        )


def test_no_package_remains_non_failure_with_human_final_authority(tmp_path):
    service = GovernanceService(project(tmp_path))
    simulation = service.simulate(
        ["docs/guide.md"],
        requested_mode="ordinary",
        autonomy_profile="human_direct",
    )
    guidance = build_no_package_guidance(
        simulation,
        service.config,
        ActorContext("human-maintainer", "maintainer"),
    )
    row = guidance.requirement_comparisons[0]

    assert row.material_status == "not_applicable"
    assert row.currently_blocks_progression is False
    assert guidance.responsibility.primary_roles == ["maintainer"]
    assert guidance.summary.blocking_issue_count == 0


@pytest.mark.parametrize(
    ("reason_code", "expected"),
    [
        ("material_scope_change", "实质变化"),
        ("partial_affected_scope", "只影响"),
        ("wording_only_clarification", "文字表述"),
        ("agent_delegation_clarification", "继续委派"),
        ("retained_unaffected_evidence", "继续有效"),
        ("invalidated_attestation", "已失效"),
        ("unauthorized_operation", "没有执行"),
        ("policy_migration_warning", "不会静默迁移"),
        ("lightweight_path", "轻量审核"),
        ("no_package", "不要求完整 AGM"),
    ],
)
def test_known_reason_codes_are_chinese_first_and_keep_source(
    reason_code,
    expected,
):
    trace = TraceReference("finding", "finding-source", "source")
    presented = present_reason(
        reason_code=reason_code,
        source_english="Canonical English source.",
        trace_refs=[trace],
    )

    assert expected in presented.display_plain
    assert presented.source_english == "Canonical English source."
    assert presented.source_code == reason_code
    assert presented.trace_refs == [trace]


def test_unknown_reason_uses_safe_fallback_without_losing_source():
    presented = present_reason(
        reason_code="future_reason_code",
        source_english="Future reason supplied by a policy extension.",
    )

    assert presented.display_plain == UNKNOWN_REASON_FALLBACK
    assert (
        presented.source_english
        == "Future reason supplied by a policy extension."
    )


def test_reason_presentation_does_not_depend_on_demo_filename_or_edit_policy(
    tmp_path,
):
    service = GovernanceService(project(tmp_path))
    before = service.config.policy_fingerprint

    first = present_reason(
        reason_code="material_scope_change",
        source_english="Source A.",
    )
    second = present_reason(
        reason_code="material_scope_change",
        source_english="Source B.",
    )

    assert first.display_plain == second.display_plain
    assert "01_multi_risk" not in first.display_plain
    assert service.config.policy_fingerprint == before


def _scoped_repair_preview(service: GovernanceService, case_id: str):
    open_case(
        service,
        case_id,
        autonomy_profile="supervised_agent",
    )
    add_all_evidence(service, case_id)
    service.prepare_case(
        case_id,
        actor="agent-1",
        actor_role="contributor_agent",
    )
    service.verify(
        case_id,
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Initial evidence check.",
    )
    service.request_repair(
        case_id,
        actor="verifier-1",
        role="maintainer_verifier",
        message="Clarify agent action and delegation scope only.",
        affected_obligation_ids=["O-AGENT-SCOPE"],
        finding_code="agent_delegation_clarification",
    )
    service.resubmit(
        case_id,
        actor="agent-1",
        role="contributor_agent",
        summary="Clarified wording.",
        affected_obligation_ids=["O-AGENT-SCOPE"],
        diff_material=f"{case_id}:initial",
        change_classification="non_material",
        change_reason="Wording only.",
    )
    case = service.storage.load_case(case_id)
    before = copy.deepcopy(case.to_dict())
    transitions = service.storage.read_transitions(case_id)
    preview = preview_reviewer_action(
        case,
        service.config,
        transitions,
        ActorContext("verifier-1", "maintainer_verifier"),
        "verify_evidence",
        {
            "obligation_ids": ["O-AGENT-SCOPE"],
            "reason": "Scoped revalidation.",
        },
    )
    return case, before, transitions, preview


def test_preview_separates_plain_effects_from_canonical_ids(tmp_path):
    service = GovernanceService(project(tmp_path))
    case, before, transitions, preview = _scoped_repair_preview(
        service,
        "preview-layers",
    )

    display = json.dumps(
        [item.to_dict() for item in preview.display_effects],
        ensure_ascii=False,
    )
    assert not re.search(
        r"(?:evidence|finding|repair|transition)-[0-9a-f]{16,}",
        display,
    )
    assert preview.affected_items == ["智能体行动与委派说明"]
    assert {"修改说明", "变更文件清单"} <= set(
        preview.retained_items
    )
    assert preview.technical_details["affected_obligation_ids"] == [
        "O-AGENT-SCOPE"
    ]
    assert preview.technical_details["retained_evidence_ids"]
    assert any(
        effect["source_object_ids"]
        for effect in preview.technical_details["effects"]
    )
    assert {
        effect["target"]
        for effect in preview.technical_details["effects"]
        if effect["after"] == "resolved"
    } >= {
        case.findings[-1].id,
        "指定修复请求",
    }
    assert preview.responsibility_after.primary_roles == ["maintainer"]
    assert any("修复请求将被关闭" in item for item in preview.next_steps)
    assert any("不等于代码已经被项目接受" in item for item in preview.next_steps)
    assert preview.final_acceptance_recorded is False
    assert case.to_dict() == before
    assert service.storage.read_transitions(case.id) == transitions


def test_preview_display_and_execution_stay_aligned(tmp_path):
    service = GovernanceService(project(tmp_path))
    case, _, _, preview = _scoped_repair_preview(
        service,
        "preview-aligned",
    )

    service.verify(
        case.id,
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Scoped revalidation.",
        obligation_ids=["O-AGENT-SCOPE"],
    )
    after = service.storage.load_case(case.id)

    assert after.state == preview.technical_details["target_state"]
    assert after.obligation("O-AGENT-SCOPE").status == "verified"
    assert all(
        item.status == "resolved" for item in after.repair_requests
    )


def test_denied_verification_creates_audit_notice_not_transition_or_finding(
    tmp_path,
):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "denied-verification")
    before = service.storage.load_case("denied-verification")
    transitions = service.storage.read_transitions(before.id)
    finding_ids = [item.id for item in before.findings]

    with pytest.raises(VNextError, match="not authorized"):
        service.verify(
            before.id,
            actor="agent-1",
            role="contributor_agent",
            reason="Attempted verification.",
        )

    after = service.storage.load_case(before.id)
    guidance = view(
        service,
        before.id,
        actor="agent-1",
        role="contributor_agent",
    )
    notice = guidance.rejected_operation_notice
    assert after.state == before.state
    assert service.storage.read_transitions(before.id) == transitions
    assert [item.id for item in after.findings] == finding_ids
    assert len(after.attempted_operations) == 1
    audit_path = (
        service.storage.case_dir(before.id)
        / "attempted_operations.jsonl"
    )
    assert audit_path.is_file()
    assert len(audit_path.read_text(encoding="utf-8").splitlines()) == 1
    assert notice is not None
    assert notice.operation == "verify_evidence"
    assert notice.state_changed is False
    assert "maintainer_verifier" in notice.required_roles
    assert notice.current_state_label == "等待维护者检查"
    assert guidance.diagnostics == []


def test_denied_final_decision_is_audited_without_state_change(tmp_path):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "denied-decision")
    service.verify(
        "denied-decision",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Evidence checked.",
    )
    before = service.storage.load_case("denied-decision")

    with pytest.raises(VNextError, match="not authorized"):
        service.decide(
            before.id,
            actor="agent-1",
            role="contributor_agent",
            decision="accept",
            reason="Attempted acceptance.",
        )

    after = service.storage.load_case(before.id)
    assert after.state == before.state
    assert after.final_decision is None
    assert after.attempted_operations[-1].operation == "decide_accept"
    assert after.attempted_operations[-1].required_roles == ["maintainer"]


def test_invalid_override_is_audited_without_fake_transition(tmp_path):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "invalid-override")
    before = service.storage.load_case("invalid-override")
    transitions = service.storage.read_transitions(before.id)

    with pytest.raises(VNextError, match="unknown findings"):
        service.override(
            before.id,
            actor="human-maintainer",
            role="maintainer",
            reason="Invalid scope.",
            finding_ids=["finding-does-not-exist"],
        )

    after = service.storage.load_case(before.id)
    assert after.state == before.state
    assert service.storage.read_transitions(before.id) == transitions
    assert (
        after.attempted_operations[-1].operation
        == "authorized_override"
    )
    assert after.attempted_operations[-1].state_changed is False


def test_successful_operation_is_not_added_to_rejected_audit(tmp_path):
    service = GovernanceService(project(tmp_path))
    prepare_docs_for_verification(service, "successful-verification")

    service.verify(
        "successful-verification",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Authorized verification.",
    )

    after = service.storage.load_case("successful-verification")
    guidance = view(service, after.id)
    assert after.attempted_operations == []
    assert guidance.rejected_operation_notice is None


def test_blocking_requirement_missing_currently_blocks(tmp_path):
    service = GovernanceService(project(tmp_path))
    case = open_case(service, "blocking-missing")
    row = next(
        item
        for item in build_requirement_comparisons(case)
        if item.obligation_id == "O-SUMMARY"
    )

    assert row.blocking_requirement is True
    assert row.currently_blocks_progression is True


def test_satisfied_blocking_requirement_no_longer_blocks(tmp_path):
    service = GovernanceService(project(tmp_path))
    case = open_case(service, "blocking-satisfied")
    add_all_evidence(service, case.id)
    case = service.storage.load_case(case.id)
    row = next(
        item
        for item in build_requirement_comparisons(case)
        if item.obligation_id == "O-SUMMARY"
    )

    assert row.blocking_requirement is True
    assert row.currently_blocks_progression is False


def test_nonblocking_warning_has_both_blocking_axes_false(tmp_path):
    service = GovernanceService(project(tmp_path))
    case = open_case(service, "nonblocking-warning")
    obligation = case.obligation("O-SUMMARY")
    obligation.blocking = False
    create_finding(
        case,
        code="future_warning",
        severity="low",
        message="Future non-blocking warning.",
        blocking=False,
        affected_obligation_ids=["O-SUMMARY"],
    )
    row = next(
        item
        for item in build_requirement_comparisons(case)
        if item.obligation_id == "O-SUMMARY"
    )

    assert row.blocking_requirement is False
    assert row.currently_blocks_progression is False


def test_scoped_revalidation_and_override_keep_blocking_axes_distinct(
    tmp_path,
):
    service = GovernanceService(project(tmp_path))
    case, _, _, preview = _scoped_repair_preview(
        service,
        "blocking-scoped",
    )
    row = next(
        item
        for item in build_requirement_comparisons(case)
        if item.obligation_id == "O-AGENT-SCOPE"
    )
    assert row.blocking_requirement is True
    assert row.currently_blocks_progression is True
    assert preview.final_acceptance_still_required is True

    prepare_docs_for_verification(service, "blocking-override")
    service.verify(
        "blocking-override",
        actor="verifier-1",
        role="maintainer_verifier",
        reason="Initial evidence check.",
    )
    service.request_repair(
        "blocking-override",
        actor="verifier-1",
        role="maintainer_verifier",
        message="Summary exception.",
        affected_obligation_ids=["O-SUMMARY"],
    )
    override_case = service.storage.load_case("blocking-override")
    finding_id = override_case.findings[-1].id
    service.override(
        override_case.id,
        actor="human-maintainer",
        role="maintainer",
        reason="Authorized exception.",
        obligation_ids=["O-SUMMARY"],
        finding_ids=[finding_id],
    )
    overridden = service.storage.load_case(override_case.id)
    row = next(
        item
        for item in build_requirement_comparisons(overridden)
        if item.obligation_id == "O-SUMMARY"
    )
    assert row.blocking_requirement is True
    assert row.currently_blocks_progression is False


def test_blocking_compatibility_alias_is_deprecated_and_not_serialized(
    tmp_path,
):
    service = GovernanceService(project(tmp_path))
    row = build_requirement_comparisons(
        open_case(service, "blocking-alias")
    )[0]

    with pytest.warns(DeprecationWarning):
        assert row.blocking == row.blocking_requirement
    with pytest.warns(DeprecationWarning):
        assert (
            row.blocks_progression
            == row.currently_blocks_progression
        )
    payload = row.to_dict()
    assert "blocking" not in payload
    assert "blocks_progression" not in payload
