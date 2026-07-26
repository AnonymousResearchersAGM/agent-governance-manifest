from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_reviewer_guidance_demos import generate  # noqa: E402


@pytest.fixture(scope="module")
def generated_scenarios(tmp_path_factory):
    output = tmp_path_factory.mktemp("guidance-e2e") / "outputs"
    results = generate(output)
    payloads = {
        item["scenario"]: json.loads(
            (output / item["json"]).read_text(encoding="utf-8")
        )
        for item in results
    }
    return output, results, payloads


@pytest.mark.parametrize(
    "scenario",
    [
        "01_multi_risk_missing",
        "02_material_partial_invalidation",
        "03_scoped_repair",
        "04_unauthorized_agent_verification",
        "05_lightweight_low_risk",
        "06_governance_self_modification",
        "07_policy_migration_warning",
        "08_human_final_decision_closure",
    ],
)
def test_each_scenario_outputs_complete_json_and_html(
    generated_scenarios,
    scenario,
):
    output, results, payloads = generated_scenarios
    result = next(item for item in results if item["scenario"] == scenario)
    payload = payloads[scenario]
    rendered = (output / result["html"]).read_text(encoding="utf-8")
    markdown = (output / result["markdown"]).read_text(
        encoding="utf-8"
    )

    assert len(payload["expected_workflow_steps"]) == 5
    assert payload["expected_requirement_comparison"]
    assert "available_actions" in payload
    assert payload["unavailable_actions"]
    assert payload["action_preview"]["mutates_case"] is False
    assert "final_verification_record" in payload
    assert payload["current_responsibility"]
    assert "current_relevant_actions" in payload
    assert payload["unavailable_action_summary"]
    assert "context_selector_data" in payload
    assert len(payload["trace_mapping"]) == 5
    assert rendered.startswith("<!doctype html>")
    assert "治理流程导航器" in rendered
    assert "项目要求对比报告" in rendered
    assert "technical-details" in rendered
    assert markdown.startswith("# AGM Reviewer Guidance Layer")


def test_multi_risk_scenario_keeps_union_and_interaction(
    generated_scenarios,
):
    payload = generated_scenarios[2]["01_multi_risk_missing"]
    rows = {
        item["obligation_id"]: item
        for item in payload["expected_requirement_comparison"]
    }
    technical = payload["guidance_view"]["technical_details"]

    assert rows["O-AUTH-IMPACT"]["result"] == "missing"
    assert "O-INDEPENDENT-REVIEW" in rows
    assert {
        item["id"] for item in technical["interaction_rules"]
    } == {"authentication-configuration"}


def test_material_change_scenario_records_partial_invalidation(
    generated_scenarios,
):
    payload = generated_scenarios[2][
        "02_material_partial_invalidation"
    ]
    repair = payload["guidance_view"]["technical_details"][
        "repair_requests"
    ][0]
    attempt = repair["attempts"][-1]

    assert attempt["change_classification"] == "partial_material_change"
    assert attempt["stale_evidence_ids"]
    assert attempt["retained_evidence_ids"]
    assert set(attempt["required_revalidation_scope"]) == {"O-SUMMARY"}
    assert payload["current_responsibility"]["primary_roles"] == [
        "contributor",
        "contributor_agent",
    ]


def test_scoped_repair_scenario_preserves_unaffected_records(
    generated_scenarios,
):
    payload = generated_scenarios[2]["03_scoped_repair"]
    repair = payload["guidance_view"]["technical_details"][
        "repair_requests"
    ][0]
    attempt = repair["attempts"][-1]

    assert repair["revalidation_required"] == ["O-AGENT-SCOPE"]
    assert attempt["retained_evidence_ids"]
    assert payload["action_preview"]["authorized"] is True
    assert payload["action_preview"]["affected_obligation_ids"] == [
        "O-AGENT-SCOPE"
    ]
    row = next(
        item
        for item in payload["expected_requirement_comparison"]
        if item["obligation_id"] == "O-AGENT-SCOPE"
    )
    assert row["material_status"] in {"provided", "retained", "verified"}
    assert row["workflow_status"] == "awaiting_revalidation"


def test_e2e_transition_traces_have_one_primary_step(generated_scenarios):
    for payload in generated_scenarios[2].values():
        transition_refs = [
            trace
            for traces in payload["trace_mapping"].values()
            for trace in traces
            if trace["kind"] == "state_transition"
        ]
        ids = [item["object_id"] for item in transition_refs]
        assert len(ids) == len(set(ids))
        assert all(
            item["relationship"].startswith("primary:")
            for item in transition_refs
        )


def test_unauthorized_agent_scenario_does_not_advance_state(
    generated_scenarios,
):
    payload = generated_scenarios[2][
        "04_unauthorized_agent_verification"
    ]
    notes = payload["notes"]

    assert payload["action_preview"]["authorized"] is False
    assert "not authorized" in notes["backend_rejection"]
    assert notes["state_before"] == notes["state_after"]
    assert "verify_evidence" in {
        item["action"] for item in payload["unavailable_actions"]
    }


def test_lightweight_scenario_separates_intensity_from_authority(
    generated_scenarios,
):
    payload = generated_scenarios[2]["05_lightweight_low_risk"]
    view = payload["guidance_view"]
    workflow = {
        item["step_id"]: item for item in view["workflow_steps"]
    }

    assert view["summary"]["path_kind"] == "lightweight"
    assert (
        workflow["accountable_confirmation"]["status"] == "skipped"
    )
    assert view["authority_notice"]
    assert payload["action_preview"]["target_state"] == (
        "ready_for_human_decision"
    )


def test_governance_self_modification_requires_independent_review(
    generated_scenarios,
):
    payload = generated_scenarios[2][
        "06_governance_self_modification"
    ]
    technical = payload["guidance_view"]["technical_details"]
    obligation_ids = {
        item["obligation_id"]
        for item in technical["compiled_obligations"]
    }

    assert {
        item["id"] for item in technical["interaction_rules"]
    } == {"governance-self-modification"}
    assert "O-INDEPENDENT-REVIEW" in obligation_ids
    assert payload["action_preview"]["actor"]["role"] == "maintainer"
    assert payload["action_preview"]["authorized"] is True


def test_policy_migration_scenario_surfaces_warning_without_mutation(
    generated_scenarios,
):
    payload = generated_scenarios[2]["07_policy_migration_warning"]
    view = payload["guidance_view"]
    migration = view["technical_details"][
        "policy_migration_diagnostic"
    ]

    assert migration["policy_changed"] is True
    assert view["summary"]["warning_count"] >= 1
    assert any(
        item["technical_term"] == "policy migration warning"
        for item in view["explanations"]
    )
    assert payload["action_preview"]["mutates_case"] is False


def test_human_final_scenario_has_separate_verification_and_closure(
    generated_scenarios,
):
    payload = generated_scenarios[2][
        "08_human_final_decision_closure"
    ]
    view = payload["guidance_view"]

    assert payload["final_verification_record"]["outcome"] == "verified"
    assert payload["action_preview"]["action"] == "decide_accept"
    assert payload["action_preview"]["authorized"] is True
    assert view["summary"]["raw_state"] == "accepted"
    assert view["technical_details"]["final_decision"]["decision"] == "accept"
    assert view["technical_details"]["closure_receipt"] is not None
