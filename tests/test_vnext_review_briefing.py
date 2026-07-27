from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from agm.vnext.briefing import (  # noqa: E402
    compile_review_brief,
    render_review_brief_html,
)
from agm.vnext.cli import main  # noqa: E402
from agm.vnext.guidance import ActorContext  # noqa: E402
from agm.vnext.runtime import (  # noqa: E402
    DemoExecutionContext,
    use_execution_context,
)
from agm.vnext.service import GovernanceService  # noqa: E402
from generate_review_briefing_demos import generate  # noqa: E402
from generate_reviewer_guidance_demos import (  # noqa: E402
    DEMO_TOKEN_SECRET,
    FIXED_TIME,
    add_all_evidence,
    make_project,
    open_case,
    prepare_for_verification,
    lightweight_low_risk,
)


SCENARIOS = [
    "01_multi_risk_missing",
    "02_material_partial_invalidation",
    "03_scoped_repair",
    "04_unauthorized_agent_verification",
    "05_lightweight_low_risk",
    "06_governance_self_modification",
    "07_policy_migration_warning",
    "08_human_final_decision_closure",
]


class _ParticipantTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.folded = 0
        self.ignored = 0
        self.values: list[str] = []

    def handle_starttag(self, tag, attrs):
        del attrs
        if tag == "details":
            self.folded += 1
        elif tag in {"style", "script"}:
            self.ignored += 1

    def handle_endtag(self, tag):
        if tag == "details":
            self.folded -= 1
        elif tag in {"style", "script"}:
            self.ignored -= 1

    def handle_data(self, data):
        if not self.folded and not self.ignored:
            self.values.append(data)


def participant_text(rendered: str) -> str:
    parser = _ParticipantTextParser()
    parser.feed(rendered)
    return " ".join(" ".join(parser.values).split())


@pytest.fixture(scope="module")
def generated_briefs(tmp_path_factory):
    output = tmp_path_factory.mktemp("review-briefing") / "outputs"
    results = generate(output)
    payloads = {
        item["scenario"]: json.loads(
            (output / item["json"]).read_text(encoding="utf-8")
        )
        for item in results
    }
    return output, results, payloads


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_eight_scenarios_emit_all_three_brief_formats(
    generated_briefs,
    scenario,
):
    output, results, payloads = generated_briefs
    result = next(
        item for item in results if item["scenario"] == scenario
    )
    assert set(result) == {"scenario", "json", "markdown", "html"}
    assert (output / result["json"]).is_file()
    assert (output / result["markdown"]).is_file()
    assert (output / result["html"]).is_file()
    assert payloads[scenario]["schema_version"] == (
        "agm.review_brief/v0.2-dev"
    )


@pytest.mark.parametrize(
    ("scenario", "component"),
    [
        ("01_multi_risk_missing", "用户认证与权限控制"),
        ("01_multi_risk_missing", "项目配置与依赖"),
        ("05_lightweight_low_risk", "文档与说明"),
        ("06_governance_self_modification", "AGM 治理与执行支持"),
    ],
)
def test_changed_files_are_compiled_into_readable_components(
    generated_briefs,
    scenario,
    component,
):
    contribution = generated_briefs[2][scenario]["contribution"]
    assert component in contribution["changed_components"]
    assert contribution["system_inferred_summary"]
    assert "不代表系统已经证明代码" in contribution[
        "inference_limitations"
    ]


def test_security_configuration_governance_and_test_changes_are_classified(
    generated_briefs,
):
    multi = generated_briefs[2]["01_multi_risk_missing"][
        "contribution"
    ]
    governance = generated_briefs[2][
        "06_governance_self_modification"
    ]["contribution"]
    assert multi["security_sensitive_changes"]
    assert multi["configuration_changes"]
    assert governance["governance_changes"]


def test_test_path_takes_test_category_even_when_filename_mentions_auth(
    tmp_path,
):
    root = make_project(tmp_path, "test-category")
    test_path = root / "tests" / "test_auth.py"
    test_path.parent.mkdir()
    test_path.write_text("def test_auth(): pass\n", encoding="utf-8")
    service = GovernanceService(root)
    open_case(
        service,
        "test-category",
        ["tests/test_auth.py"],
        autonomy_profile="supervised_agent",
    )
    view = service.review_brief(
        "test-category",
        actor="human-maintainer",
        role="maintainer",
    )
    assert "测试与验证" in view.contribution.changed_components
    assert view.contribution.security_sensitive_changes == ()


def test_declared_summary_and_system_inference_remain_distinct(
    generated_briefs,
):
    contribution = generated_briefs[2]["05_lightweight_low_risk"][
        "contribution"
    ]
    assert contribution["plain_summary"] == (
        "本次贡献修正文档中的命令拼写，并更新一个失效链接；"
        "未修改代码、配置、依赖或执行逻辑。"
    )
    assert contribution["summary_source"].startswith("贡献者声明")
    assert contribution["system_inferred_summary"] != contribution[
        "plain_summary"
    ]


def test_multi_risk_union_and_interaction_are_explained(
    generated_briefs,
):
    risk = generated_briefs[2]["01_multi_risk_missing"]["risk"]
    assert risk["overall_level"] == "critical"
    assert {"登录与身份认证", "配置与依赖"} <= set(
        risk["triggered_risk_areas"]
    )
    assert any("组合影响" in item for item in risk["interaction_effects"])
    assert risk["requires_independent_review"] is True
    assert all("触发" in item for item in risk["plain_reasons"])


def test_governance_self_modification_explains_interaction(
    generated_briefs,
):
    risk = generated_briefs[2][
        "06_governance_self_modification"
    ]["risk"]
    assert any("自修改联动" in item for item in risk["interaction_effects"])
    assert risk["requires_independent_review"] is True


def test_requirement_brief_exposes_all_required_status_buckets(
    generated_briefs,
):
    requirements = generated_briefs[2]["01_multi_risk_missing"][
        "requirements"
    ]
    expected = {
        "system_satisfied",
        "provided_requires_human_judgment",
        "missing",
        "stale",
        "invalid",
        "awaiting_accountable_human",
        "awaiting_independent_review",
        "not_applicable",
    }
    assert expected <= set(requirements)
    assert requirements["missing"]
    assert requirements["awaiting_accountable_human"]
    assert requirements["awaiting_independent_review"]


def test_automatic_checks_cover_phase_one_contract(generated_briefs):
    checks = generated_briefs[2][
        "06_governance_self_modification"
    ]["automatic_checks"]
    check_types = {item["check_type"] for item in checks}
    assert {
        "material_version_binding",
        "test_command_and_result",
        "test_version_binding",
        "evidence_freshness",
        "attestation_version_binding",
        "changed_file_scope_match",
        "agent_involvement",
        "recorded_delegation",
        "authority_boundary",
        "structural_obligations",
    } <= check_types


def test_current_binding_and_test_records_are_system_confirmed(
    generated_briefs,
):
    checks = {
        item["check_type"]: item
        for item in generated_briefs[2][
            "06_governance_self_modification"
        ]["automatic_checks"]
    }
    assert checks["material_version_binding"]["status"] == "confirmed"
    assert checks["test_command_and_result"]["status"] == "confirmed"
    assert checks["test_version_binding"]["status"] == "confirmed"
    assert "不代表代码正确性" in checks["test_command_and_result"][
        "limitations"
    ][0]


def test_stale_evidence_is_a_system_problem_not_human_judgment(
    generated_briefs,
):
    payload = generated_briefs[2][
        "02_material_partial_invalidation"
    ]
    checks = {
        item["check_type"]: item for item in payload["automatic_checks"]
    }
    assert checks["material_version_binding"]["status"] == "problem"
    assert payload["requirements"]["stale"]
    assert payload["human_judgments"] == []


def test_changed_file_declaration_mismatch_is_detected(tmp_path):
    root = make_project(tmp_path, "scope-mismatch")
    service = GovernanceService(root)
    open_case(service, "scope-mismatch", ["docs/guide.md"])
    service.add_evidence(
        "scope-mismatch",
        actor="contributor",
        actor_role="contributor",
        obligation_ids=["O-CHANGED-FILES"],
        evidence_type="changed_files",
        value=["docs/not-actually-changed.md"],
        source_tool="unit-test",
    )
    view = service.review_brief(
        "scope-mismatch",
        actor="human-maintainer",
        role="maintainer",
    )
    check = next(
        item
        for item in view.automatic_checks
        if item.check_type == "changed_file_scope_match"
    )
    assert check.status == "problem"
    assert "不一致" in check.plain_result


def test_expired_evidence_is_detected_automatically(tmp_path):
    root = make_project(tmp_path, "expired-material")
    service = GovernanceService(root)
    open_case(service, "expired-material", ["docs/guide.md"])
    service.add_evidence(
        "expired-material",
        actor="contributor",
        actor_role="contributor",
        obligation_ids=["O-CHANGED-FILES"],
        evidence_type="changed_files",
        value=["docs/guide.md"],
        source_tool="unit-test",
        observed_at="2026-01-01T00:00:00Z",
        expires_at="2026-01-02T00:00:00Z",
    )
    view = service.review_brief(
        "expired-material",
        actor="human-maintainer",
        role="maintainer",
    )
    check = next(
        item
        for item in view.automatic_checks
        if item.check_type == "evidence_freshness"
    )
    assert check.status == "problem"
    assert "已过期" in check.plain_result


def test_attestation_binding_is_checked_against_current_version(tmp_path):
    root = make_project(tmp_path, "attestation-binding")
    service = GovernanceService(root)
    open_case(
        service,
        "attestation-binding",
        ["demo_app/auth.py", "demo_app/config.py"],
        autonomy_profile="supervised_agent",
    )
    add_all_evidence(service, "attestation-binding")
    prepare_for_verification(service, "attestation-binding")
    view = service.review_brief(
        "attestation-binding",
        actor="human-maintainer",
        role="maintainer",
    )
    check = next(
        item
        for item in view.automatic_checks
        if item.check_type == "attestation_version_binding"
    )
    assert check.status == "confirmed"
    assert view.contributor_accountability.attestation_version_binding == (
        "绑定当前版本"
    )


def test_recorded_delegation_presence_and_truth_are_separated(
    generated_briefs,
):
    payload = generated_briefs[2]["03_scoped_repair"]
    check = next(
        item
        for item in payload["automatic_checks"]
        if item["check_type"] == "recorded_delegation"
    )
    assert check["status"] == "confirmed"
    assert "已提供" in check["plain_result"]
    semantic = next(
        item
        for item in payload["automatic_checks"]
        if item["check_type"] == "semantic_declaration_consistency"
    )
    assert semantic["status"] == "needs_human_judgment"
    accountability = payload["contributor_accountability"]
    assert accountability["declared_facts"]
    assert any(
        "不把智能体自述当作系统观察事实" in item
        for item in accountability["unverified_inferences"]
    )


def test_unauthorized_attempt_is_rejected_without_state_change(
    generated_briefs,
):
    payload = generated_briefs[2][
        "04_unauthorized_agent_verification"
    ]
    check = next(
        item
        for item in payload["automatic_checks"]
        if item["check_type"] == "authority_boundary"
    )
    assert check["status"] == "problem"
    assert check["semantic_status"] == "system_handled"
    assert check["system_handled"] is True
    assert check["blocking"] is False
    assert "治理状态没有变化" in check["plain_result"]
    attempts = payload["governance_details"]["attempted_operations"]
    assert attempts[-1]["state_changed"] is False


@pytest.mark.parametrize(
    ("scenario", "expected_count"),
    [
        ("01_multi_risk_missing", 0),
        ("02_material_partial_invalidation", 0),
        ("03_scoped_repair", 1),
        ("05_lightweight_low_risk", 0),
    ],
)
def test_human_judgment_queue_excludes_non_judgment_work(
    generated_briefs,
    scenario,
    expected_count,
):
    assert len(
        generated_briefs[2][scenario]["human_judgments"]
    ) == expected_count


def test_scoped_repair_only_revalidates_agent_action_statement(
    generated_briefs,
):
    payload = generated_briefs[2]["03_scoped_repair"]
    assert [
        item["display_title"] for item in payload["human_judgments"]
    ] == ["智能体行动与委派说明"]
    satisfied = {
        item["display_title"]
        for item in payload["requirements"]["system_satisfied"]
    }
    assert {"修改说明", "变更文件清单"} <= satisfied


def test_only_system_unanswerable_content_enters_queue(generated_briefs):
    item = generated_briefs[2]["03_scoped_repair"][
        "human_judgments"
    ][0]
    assert "不能自动判断" in item["why_human_is_needed"]
    assert item["contribution_claim"]
    assert item["system_observation"]
    assert item["review_focus"]
    assert item["possible_outcomes"]


@pytest.mark.parametrize(
    ("scenario", "status"),
    [
        ("01_multi_risk_missing", "awaiting_contributor"),
        ("02_material_partial_invalidation", "awaiting_contributor"),
        ("03_scoped_repair", "maintainer_judgment"),
        ("04_unauthorized_agent_verification", "normal_code_review"),
        ("05_lightweight_low_risk", "normal_code_review"),
        ("06_governance_self_modification", "maintainer_judgment"),
        ("07_policy_migration_warning", "awaiting_contributor"),
        ("08_human_final_decision_closure", "completed"),
    ],
)
def test_next_step_compiler_routes_each_scenario(
    generated_briefs,
    scenario,
    status,
):
    assert generated_briefs[2][scenario]["current_next_step"][
        "status"
    ] == status


def test_low_risk_path_explicitly_returns_to_normal_code_review(
    generated_briefs,
):
    step = generated_briefs[2]["05_lightweight_low_risk"][
        "current_next_step"
    ]
    assert "无需额外 AGM 治理判断" in step["plain_explanation"]
    assert step["final_acceptance_state"] == "not_decided"


def test_verification_and_final_acceptance_remain_distinct(
    generated_briefs,
):
    scoped = generated_briefs[2]["03_scoped_repair"][
        "current_next_step"
    ]
    final = generated_briefs[2][
        "08_human_final_decision_closure"
    ]["current_next_step"]
    assert scoped["final_acceptance_state"] == "not_decided"
    assert final["final_acceptance_state"] == "accepted"
    assert "人类维护者" in final["plain_explanation"]


FORBIDDEN_MAIN_TERMS = (
    "O-SUMMARY",
    "O-AUTH-IMPACT",
    "awaiting_maintainer_verification",
    "verify_evidence",
    "request_repair",
    "contribution_fingerprint",
    "policy_fingerprint",
    "finding_id",
    "repair_request_ids",
)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_participant_visible_html_hides_governance_internals(
    generated_briefs,
    scenario,
):
    output, results, _ = generated_briefs
    result = next(
        item for item in results if item["scenario"] == scenario
    )
    rendered = (output / result["html"]).read_text(encoding="utf-8")
    visible = participant_text(rendered)
    assert not any(term in visible for term in FORBIDDEN_MAIN_TERMS)
    assert "<form" not in rendered
    assert "本次修改与风险" in visible
    assert "当前结论" in visible


def test_json_main_uses_safe_refs_and_technical_details_keep_raw_ids(
    generated_briefs,
):
    payload = generated_briefs[2]["03_scoped_repair"]
    public = {
        key: value
        for key, value in payload.items()
        if key != "governance_details"
    }
    public_text = json.dumps(public, ensure_ascii=False)
    assert "O-AGENT-SCOPE" not in public_text
    assert "contribution_fingerprint" not in public_text
    technical = payload["governance_details"]
    assert technical["contribution_fingerprint"]
    assert any(
        item["obligation_id"] == "O-AGENT-SCOPE"
        for item in technical["compiled_obligations"]
    )
    assert technical["trace_index"]


def test_html_escapes_contributor_content_and_has_no_action_route(tmp_path):
    root = make_project(tmp_path, "escape-brief")
    service = GovernanceService(root)
    open_case(service, "escape-brief", ["docs/guide.md"])
    add_all_evidence(service, "escape-brief")
    case = service.storage.load_case("escape-brief")
    summary = next(
        item
        for item in case.evidence
        if item.evidence_type == "contribution_summary"
    )
    summary.value = "<script>alert('x')</script>"
    service.storage.save_case(case)
    view = service.review_brief(
        "escape-brief",
        actor="human-maintainer",
        role="maintainer",
    )
    rendered = render_review_brief_html(view)
    assert "<script>alert" not in rendered
    assert "&lt;script&gt;" in rendered
    assert "<form" not in rendered


def test_core_api_supports_immutable_policy_snapshot_input(tmp_path):
    root = make_project(tmp_path, "domain-only")
    service = GovernanceService(root)
    open_case(service, "domain-only", ["docs/guide.md"])
    case = service.storage.load_case("domain-only")
    view = compile_review_brief(
        governance_case=case,
        policy_snapshot=case.policy_snapshot,
        contribution={},
        actor_context=ActorContext(
            actor="human-maintainer", role="maintainer"
        ),
    )
    assert view.contribution.changed_files == ("docs/guide.md",)
    assert view.governance_details.reviewer_guidance[
        "schema_version"
    ] == "agm.reviewer_guidance/reference-only"


def test_cli_writes_brief_artifacts_without_changing_case(tmp_path, capsys):
    with use_execution_context(
        DemoExecutionContext(
            scenario_namespace="brief-cli",
            fixed_timestamp=FIXED_TIME,
            token_secret=DEMO_TOKEN_SECRET,
        )
    ):
        root = make_project(tmp_path, "brief-cli")
        service = GovernanceService(root)
        scenario = lightweight_low_risk(service)
        case_path = service.storage.case_dir(
            scenario["case_id"]
        ) / "case.yml"
        before = case_path.read_bytes()
        result = main(
            [
                "--root",
                str(root),
                "maintainer",
                "brief",
                "--case",
                scenario["case_id"],
                "--actor",
                "human-maintainer",
                "--role",
                "maintainer",
            ]
        )
        captured = capsys.readouterr().out
        assert result == 0
        assert case_path.read_bytes() == before
        paths = json.loads(captured)
        assert Path(paths["json"]).name == "brief.json"
        assert Path(paths["markdown"]).name == "brief.md"
        assert Path(paths["html"]).name == "brief.html"
        assert all(Path(path).is_file() for path in paths.values())


def test_generated_outputs_are_deterministic(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    generate(first)
    generate(second)
    for relative in [
        Path(scenario) / filename
        for scenario in SCENARIOS
        for filename in ("brief.json", "brief.md", "brief.html")
    ]:
        assert (first / relative).read_bytes() == (
            second / relative
        ).read_bytes()
