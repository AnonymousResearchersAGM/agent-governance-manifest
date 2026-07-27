from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from agm.vnext.briefing import risk_css_class  # noqa: E402
from agm.vnext.runtime import (  # noqa: E402
    DemoExecutionContext,
    use_execution_context,
)
from agm.vnext.service import GovernanceService  # noqa: E402
from check_review_briefing_demo_hashes import check_hashes  # noqa: E402
from generate_review_briefing_demos import generate  # noqa: E402
from generate_reviewer_guidance_demos import (  # noqa: E402
    DEMO_TOKEN_SECRET,
    FIXED_TIME,
    lightweight_low_risk,
    make_project,
)


SCENARIOS = (
    "01_multi_risk_missing",
    "02_material_partial_invalidation",
    "03_scoped_repair",
    "04_unauthorized_agent_verification",
    "05_lightweight_low_risk",
    "06_governance_self_modification",
    "07_policy_migration_warning",
    "08_human_final_decision_closure",
)


class _VisibleText(HTMLParser):
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


def visible_text(rendered: str) -> str:
    parser = _VisibleText()
    parser.feed(rendered)
    return " ".join(" ".join(parser.values).split())


@pytest.fixture(scope="module")
def phase_1_1_briefs(tmp_path_factory):
    output = tmp_path_factory.mktemp("brief-phase-1-1") / "outputs"
    manifest = generate(output)
    payloads = {
        item["scenario"]: json.loads(
            (output / item["json"]).read_text(encoding="utf-8")
        )
        for item in manifest
    }
    html = {
        item["scenario"]: (output / item["html"]).read_text(
            encoding="utf-8"
        )
        for item in manifest
    }
    return output, payloads, html


def test_current_status_precedes_all_detailed_sections(phase_1_1_briefs):
    rendered = phase_1_1_briefs[2]["03_scoped_repair"]
    current = rendered.index('id="current-status"')
    judgment = rendered.index('id="judgments"')
    change = rendered.index('id="change-risk"')
    requirements = rendered.index('id="requirements"')
    automatic = rendered.index('id="automatic-checks"')
    assert current < judgment < change < requirements < automatic


def test_missing_material_first_screen_routes_away_from_maintainer(
    phase_1_1_briefs,
):
    visible = visible_text(phase_1_1_briefs[2]["01_multi_risk_missing"])
    assert "当前无需你操作" in visible
    assert "贡献侧仍需补充或更新 8 项材料" in visible
    assert "当前责任方： 贡献者或贡献侧智能体" in visible


def test_judgment_first_screen_names_count_item_and_acceptance_boundary(
    phase_1_1_briefs,
):
    visible = visible_text(phase_1_1_briefs[2]["03_scoped_repair"])
    assert "现在需要你检查 1 项" in visible
    assert "智能体行动与委派说明" in visible
    assert "检查完成不等于贡献已被接受" in visible


def test_low_risk_first_screen_returns_to_normal_code_review(
    phase_1_1_briefs,
):
    visible = visible_text(
        phase_1_1_briefs[2]["05_lightweight_low_risk"]
    )
    assert "无需额外 AGM 治理判断" in visible
    assert "可以进入正常代码审查" in visible


@pytest.mark.parametrize(
    ("scenario", "level", "css_class"),
    [
        ("05_lightweight_low_risk", "低", "risk-low"),
        ("06_governance_self_modification", "关键", "risk-critical"),
    ],
)
def test_risk_level_uses_stable_semantic_class(
    phase_1_1_briefs,
    scenario,
    level,
    css_class,
):
    rendered = phase_1_1_briefs[2][scenario]
    visible = visible_text(rendered)
    assert f'class="risk-level {css_class}"' in rendered
    assert f"综合风险：{level}" in visible


def test_high_and_unknown_risk_classes_are_safe():
    assert risk_css_class("medium") == "risk-medium"
    assert risk_css_class("high") == "risk-high"
    assert risk_css_class("unexpected") == "risk-unknown"
    assert risk_css_class("") == "risk-unknown"


def test_low_risk_does_not_use_high_or_critical_class(
    phase_1_1_briefs,
):
    rendered = phase_1_1_briefs[2]["05_lightweight_low_risk"]
    assert 'class="risk-level risk-low"' in rendered
    assert 'class="risk-level risk-high"' not in rendered
    assert 'class="risk-level risk-critical"' not in rendered


def test_formal_and_binding_checks_do_not_claim_content_confirmation(
    phase_1_1_briefs,
):
    item = phase_1_1_briefs[1]["03_scoped_repair"]["requirements"][
        "provided_requires_human_judgment"
    ][0]
    assert item["status"] == "provided_requires_human_judgment"
    assert item["semantic_status"] == "human_review_required"
    assert {
        "material_available",
        "structure_valid",
        "version_bound",
        "human_review_required",
    } <= set(item["semantic_states"])
    assert "human_verified" not in item["semantic_states"]
    assert "内容是否与实际修改一致仍需维护者判断" in item[
        "plain_status"
    ]


def test_human_verified_and_accepted_are_distinct_states(
    phase_1_1_briefs,
):
    payload = phase_1_1_briefs[1][
        "08_human_final_decision_closure"
    ]
    assert all(
        item["semantic_status"] == "human_verified"
        for item in payload["requirements"]["items"]
    )
    assert payload["current_next_step"]["semantic_state"] == "accepted"
    assert payload["current_next_step"]["final_acceptance_state"] == (
        "accepted"
    )


def test_test_record_check_never_claims_code_correctness(
    phase_1_1_briefs,
):
    check = next(
        item
        for item in phase_1_1_briefs[1][
            "06_governance_self_modification"
        ]["automatic_checks"]
        if item["check_type"] == "test_command_and_result"
    )
    assert check["status"] == "confirmed"
    assert check["semantic_status"] == "system_checked"
    assert any("不代表代码正确性" in item for item in check["limitations"])


def test_agent_declaration_remains_separate_from_system_observation(
    phase_1_1_briefs,
):
    accountability = phase_1_1_briefs[1]["03_scoped_repair"][
        "contributor_accountability"
    ]
    declared = " ".join(accountability["declared_facts"])
    observed = " ".join(accountability["system_observations"])
    assert "没有继续委派" in declared
    assert "没有继续委派" not in observed


def test_denied_attempt_does_not_create_arbitrary_judgment(
    phase_1_1_briefs,
):
    payload = phase_1_1_briefs[1][
        "04_unauthorized_agent_verification"
    ]
    assert payload["human_judgments"] == []
    anomaly = next(
        item
        for item in payload["automatic_checks"]
        if item["check_type"] == "authority_boundary"
    )
    assert anomaly["status"] == "problem"
    assert anomaly["semantic_status"] == "system_handled"
    assert anomaly["owner"] == "system"
    assert anomaly["blocking"] is False
    assert len(payload["human_judgments"]) == 0


def test_denied_attempt_is_visible_in_top_status_without_changing_work(
    phase_1_1_briefs,
):
    payload = phase_1_1_briefs[1][
        "04_unauthorized_agent_verification"
    ]
    rendered = phase_1_1_briefs[2][
        "04_unauthorized_agent_verification"
    ]
    status_end = rendered.index("</section>", rendered.index(
        'id="current-status"'
    ))
    status_html = rendered[rendered.index('id="current-status"'):status_end]
    visible = visible_text(rendered)
    assert "系统已自动拒绝 1 次越权检查尝试" in status_html
    assert "该操作未生效，你无需额外处理" in status_html
    assert "操作未生效" in visible
    assert payload["current_next_step"]["status"] == "normal_code_review"
    anomaly = next(
        item
        for item in payload["work_items"]
        if item["system_handled"]
    )
    assert anomaly["owner"] == "system"
    assert anomaly["blocking"] is False
    assert len(payload["human_judgments"]) == 0


def test_every_judgment_has_requirement_and_governance_provenance(
    phase_1_1_briefs,
):
    for scenario in SCENARIOS:
        for item in phase_1_1_briefs[1][scenario]["human_judgments"]:
            assert item["requirement_refs"]
            assert "compiled_requirement" in item["provenance"]
            assert any(
                source
                in {
                    "maintainer_review_stage",
                    "scoped_revalidation",
                    "independent_review_requirement",
                    "existing_finding",
                }
                for source in item["provenance"]
            )


def test_scoped_repair_provenance_and_scope_remain_narrow(
    phase_1_1_briefs,
):
    items = phase_1_1_briefs[1]["03_scoped_repair"][
        "human_judgments"
    ]
    assert len(items) == 1
    assert items[0]["display_title"] == "智能体行动与委派说明"
    assert "scoped_revalidation" in items[0]["provenance"]


def test_non_required_agent_scope_is_informational_only(
    phase_1_1_briefs,
):
    payload = phase_1_1_briefs[1][
        "04_unauthorized_agent_verification"
    ]
    check = next(
        item
        for item in payload["automatic_checks"]
        if item["check_type"] == "recorded_delegation"
    )
    assert check["status"] == "not_applicable"
    assert check["semantic_status"] == "informational"
    assert check["policy_required"] is False
    assert check["informational_only"] is True
    assert check["blocking"] is False
    assert payload["current_next_step"]["status"] == "normal_code_review"


def test_canonical_agent_scope_remains_required_when_compiled(
    phase_1_1_briefs,
):
    check = next(
        item
        for item in phase_1_1_briefs[1]["01_multi_risk_missing"][
            "automatic_checks"
        ]
        if item["check_type"] == "recorded_delegation"
    )
    assert check["status"] == "problem"
    assert check["policy_required"] is True
    assert check["blocking"] is True
    assert check["requirement_refs"] == ["agent-actions-delegation"]


@pytest.mark.parametrize(
    ("scenario", "title", "owner"),
    [
        ("01_multi_risk_missing", "修改说明", "contribution_side"),
        (
            "01_multi_risk_missing",
            "负责人确认",
            "accountable_human",
        ),
        (
            "03_scoped_repair",
            "智能体行动与委派说明",
            "maintainer",
        ),
        (
            "04_unauthorized_agent_verification",
            "是否存在越权操作",
            "system",
        ),
    ],
)
def test_work_items_have_explicit_owners(
    phase_1_1_briefs,
    scenario,
    title,
    owner,
):
    item = next(
        item
        for item in phase_1_1_briefs[1][scenario]["work_items"]
        if item["display_title"] == title
    )
    assert item["owner"] == owner


def test_final_decision_pending_has_distinct_owner_and_language(tmp_path):
    with use_execution_context(
        DemoExecutionContext(
            scenario_namespace="phase-1-1-final-pending",
            fixed_timestamp=FIXED_TIME,
            token_secret=DEMO_TOKEN_SECRET,
        )
    ):
        root = make_project(tmp_path, "final-pending")
        service = GovernanceService(root)
        scenario = lightweight_low_risk(service)
        service.verify(
            scenario["case_id"],
            actor="maintainer-reviewer",
            role="maintainer_verifier",
            reason="材料内容已经完成人工检查。",
        )
        view = service.review_brief(
            scenario["case_id"],
            actor="human-maintainer",
            role="maintainer",
        )
    assert view.current_next_step.status == (
        "awaiting_final_human_decision"
    )
    assert view.current_next_step.owner == "final_decision_authority"
    assert view.current_next_step.semantic_state == "final_decision_pending"
    assert "不等于贡献已被接受" in view.current_next_step.plain_explanation


def test_requirement_check_and_technical_sections_are_closed_by_default(
    phase_1_1_briefs,
):
    rendered = phase_1_1_briefs[2]["03_scoped_repair"]
    for identifier in (
        "requirements",
        "automatic-checks",
        "accountability",
        "technical",
    ):
        assert f'<details id="{identifier}">' in rendered
        assert f'<details id="{identifier}" open' not in rendered


def test_html_keeps_status_visible_and_stacks_content_on_narrow_screens(
    phase_1_1_briefs,
):
    rendered = phase_1_1_briefs[2]["03_scoped_repair"]
    assert "@media (max-width:720px)" in rendered
    assert ".grid,.two-col { grid-template-columns:1fr; }" in rendered
    assert "overflow-wrap:anywhere" in rendered
    assert '<section id="current-status"' in rendered
    assert "<details" not in rendered[
        rendered.index('<section id="current-status"') :
        rendered.index('id="judgments"')
    ]


def test_blocking_problems_visible_but_passed_check_details_folded(
    phase_1_1_briefs,
):
    missing_visible = visible_text(
        phase_1_1_briefs[2]["01_multi_risk_missing"]
    )
    low_visible = visible_text(
        phase_1_1_briefs[2]["05_lightweight_low_risk"]
    )
    assert "阻断性问题" in missing_visible
    assert "现有材料记录没有过期状态" not in low_visible


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_participant_layer_has_no_raw_ids_or_fixture_language(
    phase_1_1_briefs,
    scenario,
):
    visible = visible_text(phase_1_1_briefs[2][scenario])
    forbidden = (
        "O-SUMMARY",
        "obl-",
        "finding-",
        "transition-",
        "fingerprint",
        "contributor-agent",
        "scenario-generator",
        "Implemented the scenario contribution",
        "Task-bounded workspace access",
        "系统已确认",
    )
    assert not any(item in visible for item in forbidden)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_public_json_has_no_raw_actor_or_fixture_language(
    phase_1_1_briefs,
    scenario,
):
    payload = {
        key: value
        for key, value in phase_1_1_briefs[1][scenario].items()
        if key != "governance_details"
    }
    public_text = json.dumps(payload, ensure_ascii=False)
    forbidden = (
        "contributor-agent",
        "contributor_agent",
        "scenario-generator",
        "Implemented the scenario contribution",
        "Task-bounded workspace access",
        "awaiting_maintainer_verification",
        "O-SUMMARY",
        "obl-",
        "finding-",
        "transition-",
    )
    assert not any(item in public_text for item in forbidden)


def test_scenario_two_names_only_affected_summary_and_retention(
    phase_1_1_briefs,
):
    payload = phase_1_1_briefs[1][
        "02_material_partial_invalidation"
    ]
    assert [item["display_title"] for item in payload["requirements"]["stale"]] == [
        "修改说明"
    ]
    assert len(payload["requirements"]["system_satisfied"]) == 2
    visible = visible_text(
        phase_1_1_briefs[2]["02_material_partial_invalidation"]
    )
    assert "只有修改说明需要按当前版本更新" in visible
    assert "未受影响的有效材料继续保留" in visible


def test_policy_migration_is_specific_and_does_not_invalidate_everything(
    phase_1_1_briefs,
):
    step = phase_1_1_briefs[1]["07_policy_migration_warning"][
        "current_next_step"
    ]
    assert step["status"] == "awaiting_contributor"
    assert "项目规则已变化" in step["display_title"]
    assert "2 项既有要求没有改变" in step["plain_explanation"]
    assert "不会把全部材料笼统判为失效" in step["plain_explanation"]


def test_closed_scenario_distinguishes_verification_acceptance_and_archive(
    phase_1_1_briefs,
):
    step = phase_1_1_briefs[1][
        "08_human_final_decision_closure"
    ]["current_next_step"]
    assert step["status"] == "completed"
    assert step["final_acceptance_state"] == "accepted"
    assert "已经接受" in step["plain_explanation"]
    assert "归档" in step["plain_explanation"]


def test_governance_self_modification_requires_independent_attention(
    phase_1_1_briefs,
):
    payload = phase_1_1_briefs[1][
        "06_governance_self_modification"
    ]
    assert payload["risk"]["requires_independent_review"] is True
    assert any(
        "independent_review_requirement" in item["provenance"]
        for item in payload["human_judgments"]
    )


def test_brief_owner_agrees_with_reviewer_guidance_responsibility(
    phase_1_1_briefs,
):
    owner_by_role = {
        "contributor": "contribution_side",
        "contributor_agent": "contribution_side",
        "accountable_human": "accountable_human",
        "maintainer_verifier": "maintainer",
        "policy_steward": "maintainer",
        "maintainer": "maintainer",
    }
    for scenario in SCENARIOS[:-1]:
        payload = phase_1_1_briefs[1][scenario]
        guidance = payload["governance_details"]["reviewer_guidance"]
        responsibility = guidance.get("responsibility")
        assert responsibility
        expected = {
            owner_by_role[role]
            for role in responsibility["primary_roles"]
            if role in owner_by_role
        }
        assert payload["current_next_step"]["owner"] in expected


def test_consecutive_generation_is_byte_identical_including_manifest(
    tmp_path,
):
    first = tmp_path / "first"
    second = tmp_path / "second"
    generate(first)
    generate(second)
    first_files = {
        path.relative_to(first).as_posix(): path.read_bytes()
        for path in first.rglob("*")
        if path.is_file()
    }
    second_files = {
        path.relative_to(second).as_posix(): path.read_bytes()
        for path in second.rglob("*")
        if path.is_file()
    }
    assert first_files == second_files
    assert len(first_files) == 25


def test_regenerated_outputs_match_committed_frozen_hashes(
    phase_1_1_briefs,
):
    expected = (
        ROOT / "examples" / "review_briefing" / "expected_sha256.json"
    )
    assert check_hashes(phase_1_1_briefs[0], expected) == []
