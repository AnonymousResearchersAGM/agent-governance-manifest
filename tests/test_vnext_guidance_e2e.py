from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_reviewer_guidance_demos import generate  # noqa: E402


class _ParticipantTextParser(HTMLParser):
    """Collect visible participant text while excluding folded details."""

    def __init__(self):
        super().__init__()
        self.folded_depth = 0
        self.ignored_depth = 0
        self.values: list[str] = []

    def handle_starttag(self, tag, attrs):
        del attrs
        if tag == "details":
            self.folded_depth += 1
        elif tag in {"style", "script"}:
            self.ignored_depth += 1

    def handle_endtag(self, tag):
        if tag == "details":
            self.folded_depth -= 1
        elif tag in {"style", "script"}:
            self.ignored_depth -= 1

    def handle_data(self, data):
        if not self.folded_depth and not self.ignored_depth:
            self.values.append(data)


def _participant_text(rendered: str) -> str:
    parser = _ParticipantTextParser()
    parser.feed(rendered)
    return " ".join(" ".join(parser.values).split())


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


def test_material_change_preview_is_chinese_first_with_raw_terms_folded(
    generated_scenarios,
):
    output, results, payloads = generated_scenarios
    slug = "02_material_partial_invalidation"
    result = next(item for item in results if item["scenario"] == slug)
    rendered = (output / result["html"]).read_text(encoding="utf-8")
    visible = _participant_text(rendered)
    preview = payloads[slug]["action_preview"]

    assert "修改说明" in visible
    assert "当前还不能进行维护者检查" in visible
    assert "贡献侧智能体" in visible
    assert "verify_evidence" not in visible
    assert "O-SUMMARY" not in visible
    assert "verify_evidence" in rendered
    assert "O-SUMMARY" in rendered
    assert preview["technical_details"]["operation"] == "verify_evidence"
    assert preview["technical_details"]["current_role"] == (
        "maintainer_verifier"
    )
    assert preview["technical_details"]["affected_obligation_ids"] == [
        "O-SUMMARY"
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
    assert payload["action_preview"]["technical_details"][
        "affected_obligation_ids"
    ] == [
        "O-AGENT-SCOPE"
    ]
    row = next(
        item
        for item in payload["expected_requirement_comparison"]
        if item["obligation_id"] == "O-AGENT-SCOPE"
    )
    assert row["material_status"] in {"provided", "retained", "verified"}
    assert row["workflow_status"] == "awaiting_revalidation"


def test_scoped_repair_preview_keeps_ids_out_of_participant_layer(
    generated_scenarios,
):
    output, results, _ = generated_scenarios
    slug = "03_scoped_repair"
    result = next(item for item in results if item["scenario"] == slug)
    rendered = (output / result["html"]).read_text(encoding="utf-8")
    visible = _participant_text(rendered)

    assert "智能体行动与委派说明" in visible
    assert "保留的未受影响材料" in visible
    assert "等待人类维护者最终决定" in visible
    assert "不等于代码已经被项目接受" in visible
    assert "evidence-" not in visible
    assert "finding-" not in visible


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


def test_unauthorized_notice_presents_action_and_roles_without_raw_terms(
    generated_scenarios,
):
    output, results, payloads = generated_scenarios
    slug = "04_unauthorized_agent_verification"
    result = next(item for item in results if item["scenario"] == slug)
    rendered = (output / result["html"]).read_text(encoding="utf-8")
    visible = _participant_text(rendered)
    notice = payloads[slug]["guidance_view"][
        "rejected_operation_notice"
    ]

    assert "最近一次操作未生效" in visible
    assert "检查提交材料" in visible
    assert "贡献侧智能体" in visible
    assert "维护者侧检查人员" in visible
    assert "案例状态没有变化" in visible
    assert "verify_evidence" not in visible
    assert "contributor_agent" not in visible
    assert "maintainer_verifier" not in visible
    assert notice["operation"] == "verify_evidence"
    assert notice["actor_role"] == "contributor_agent"
    assert "maintainer_verifier" in notice["required_roles"]


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
    assert payload["action_preview"]["technical_details"][
        "target_state"
    ] == (
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
    assert payload["action_preview"]["technical_details"][
        "operation"
    ] == "decide_accept"
    assert payload["action_preview"]["authorized"] is True
    assert view["summary"]["raw_state"] == "accepted"
    assert view["technical_details"]["final_decision"]["decision"] == "accept"
    assert view["technical_details"]["closure_receipt"] is not None


def _output_hashes(output: Path) -> dict[str, str]:
    return {
        str(path.relative_to(output)): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(output.rglob("*"))
        if path.is_file() and ".git" not in path.parts
    }


def test_deterministic_generation_is_byte_stable_and_git_clean(tmp_path):
    output = tmp_path / "deterministic-outputs"
    generate(output)
    first = _output_hashes(output)
    subprocess.run(["git", "init", "-q"], cwd=output, check=True)
    subprocess.run(
        ["git", "config", "user.email", "agm-test@example.invalid"],
        cwd=output,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "AGM Test"],
        cwd=output,
        check=True,
    )
    subprocess.run(["git", "add", "."], cwd=output, check=True)
    subprocess.run(
        ["git", "commit", "-qm", "freeze deterministic fixtures"],
        cwd=output,
        check=True,
    )

    generate(output)
    second = _output_hashes(output)
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=output,
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    assert second == first
    assert status == ""


def test_deterministic_payload_stabilizes_runtime_values_and_namespaces(
    generated_scenarios,
    tmp_path,
):
    first_payloads = generated_scenarios[2]
    second_output = tmp_path / "second"
    second_results = generate(second_output)
    second_payloads = {
        item["scenario"]: json.loads(
            (second_output / item["json"]).read_text(encoding="utf-8")
        )
        for item in second_results
    }

    assert second_payloads == first_payloads
    notice = first_payloads[
        "04_unauthorized_agent_verification"
    ]["guidance_view"]["rejected_operation_notice"]
    assert notice["attempted_at"] == "2026-07-26T00:00:00Z"
    scenario_tokens = {}
    scenario_ids = {}
    for slug, payload in first_payloads.items():
        technical = payload["guidance_view"]["technical_details"]
        scenario_ids[slug] = {
            item["id"] for item in technical["evidence_records"]
        }
        scenario_tokens[slug] = {
            option["selector_token"]
            for options in payload["context_selector_data"].values()
            for option in options
        }
    assert all(
        scenario_ids[left].isdisjoint(scenario_ids[right])
        for index, left in enumerate(scenario_ids)
        for right in list(scenario_ids)[index + 1 :]
    )
    assert all(
        scenario_tokens[left].isdisjoint(scenario_tokens[right])
        for index, left in enumerate(scenario_tokens)
        for right in list(scenario_tokens)[index + 1 :]
    )


def test_runtime_random_mode_keeps_scenario_semantics(
    generated_scenarios,
    tmp_path,
):
    random_output = tmp_path / "runtime-random"
    results = generate(random_output, deterministic=False)
    random_payloads = {
        item["scenario"]: json.loads(
            (random_output / item["json"]).read_text(encoding="utf-8")
        )
        for item in results
    }
    deterministic_payloads = generated_scenarios[2]

    for slug, random_payload in random_payloads.items():
        deterministic = deterministic_payloads[slug]
        assert random_payload["expected_workflow_steps"] == deterministic[
            "expected_workflow_steps"
        ]
        assert [
            (
                item["obligation_id"],
                item["material_status"],
                item["workflow_status"],
                item["blocking_requirement"],
                item["currently_blocks_progression"],
            )
            for item in random_payload["expected_requirement_comparison"]
        ] == [
            (
                item["obligation_id"],
                item["material_status"],
                item["workflow_status"],
                item["blocking_requirement"],
                item["currently_blocks_progression"],
            )
            for item in deterministic[
                "expected_requirement_comparison"
            ]
        ]
        assert random_payload["action_preview"]["authorized"] == (
            deterministic["action_preview"]["authorized"]
        )

    deterministic_id = deterministic_payloads[
        "05_lightweight_low_risk"
    ]["guidance_view"]["technical_details"]["evidence_records"][0]["id"]
    random_id = random_payloads[
        "05_lightweight_low_risk"
    ]["guidance_view"]["technical_details"]["evidence_records"][0]["id"]
    assert random_id != deterministic_id


def test_guidance_json_uses_only_clear_blocking_field_names(
    generated_scenarios,
):
    for payload in generated_scenarios[2].values():
        for row in payload["expected_requirement_comparison"]:
            assert "blocking_requirement" in row
            assert "currently_blocks_progression" in row
            assert "blocking" not in row
            assert "blocks_progression" not in row

    for path in (
        ROOT / "docs" / "AGM_REVIEWER_GUIDANCE_LAYER.md",
        ROOT / "docs" / "AGM_MAINTAINER_GUIDE.md",
        ROOT / "docs" / "AGM_VNEXT_DESIGN.md",
        ROOT / "docs" / "AGM_VNEXT_SPEC.md",
    ):
        text = path.read_text(encoding="utf-8")
        assert "blocking_requirement" in text
        assert "currently_blocks_progression" in text
