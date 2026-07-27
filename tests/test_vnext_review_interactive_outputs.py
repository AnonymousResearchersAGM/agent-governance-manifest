from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from check_review_interactive_demo_hashes import (  # noqa: E402
    check_hashes,
)
from generate_review_interactive_demos import generate  # noqa: E402


SCENARIOS = (
    "01_multi_risk_missing",
    "02_material_partial_invalidation",
    "03_scoped_repair",
    "04_unauthorized_agent_verification",
    "05_lightweight_low_risk",
    "06_governance_self_modification",
    "07_policy_migration_warning",
    "08_human_final_decision_closure",
    "09_pre_final_decision",
)


class ParticipantText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.folded = 0
        self.ignored = 0
        self.values = []

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
    parser = ParticipantText()
    parser.feed(rendered)
    return " ".join(" ".join(parser.values).split())


@pytest.fixture(scope="module")
def interactive_outputs(tmp_path_factory):
    output = tmp_path_factory.mktemp("interactive-output") / "outputs"
    manifest = generate(output)
    models = {
        item["scenario"]: json.loads(
            (output / item["model"]).read_text(encoding="utf-8")
        )
        for item in manifest
    }
    rendered = {
        item["scenario"]: (output / item["html"]).read_text(
            encoding="utf-8"
        )
        for item in manifest
    }
    return output, models, rendered


def test_all_scenarios_and_pre_final_fixture_are_deterministic(
    interactive_outputs,
):
    output, models, rendered = interactive_outputs
    assert tuple(models) == SCENARIOS
    assert tuple(rendered) == SCENARIOS
    expected = (
        ROOT
        / "examples"
        / "review_briefing"
        / "interactive_expected_sha256.json"
    )
    assert check_hashes(output, expected) == []


def test_static_outputs_never_contain_runtime_secrets(
    interactive_outputs,
):
    _, models, rendered = interactive_outputs
    for scenario in SCENARIOS:
        raw = json.dumps(models[scenario], ensure_ascii=False)
        assert '"live_actions_enabled": true' not in raw.lower()
        assert "csrf_token" not in rendered[scenario]
        assert "preview_token" not in rendered[scenario]
        assert "session_id" not in rendered[scenario]


@pytest.mark.parametrize(
    ("scenario", "item_count"),
    [
        ("01_multi_risk_missing", 0),
        ("02_material_partial_invalidation", 0),
        ("03_scoped_repair", 1),
        ("04_unauthorized_agent_verification", 0),
        ("05_lightweight_low_risk", 0),
        ("06_governance_self_modification", 4),
        ("07_policy_migration_warning", 0),
        ("08_human_final_decision_closure", 0),
    ],
)
def test_existing_scenario_governance_meaning_is_preserved(
    interactive_outputs,
    scenario,
    item_count,
):
    model = interactive_outputs[1][scenario]
    assert len(model["items"]) == item_count


def test_interactive_case_state_matches_read_only_brief(
    interactive_outputs,
):
    for scenario in SCENARIOS[:8]:
        committed_brief = json.loads(
            (
                ROOT
                / "examples"
                / "review_briefing"
                / "outputs"
                / scenario
                / "brief.json"
            ).read_text(encoding="utf-8")
        )
        assert interactive_outputs[1][scenario]["case_state"] == (
            committed_brief["governance_details"]["raw_state"]
        )
        assert interactive_outputs[1][scenario][
            "contribution_fingerprint"
        ] == committed_brief["governance_details"][
            "contribution_fingerprint"
        ]
        assert interactive_outputs[1][scenario][
            "policy_snapshot_fingerprint"
        ] == committed_brief["governance_details"][
            "policy_fingerprint"
        ]


def test_scoped_repair_is_item_bound_with_three_business_results(
    interactive_outputs,
):
    model = interactive_outputs[1]["03_scoped_repair"]
    item = model["items"][0]
    assert item["display_title"] == "智能体行动与委派说明"
    assert [option["display_label"] for option in item["options"]] == [
        "确认材料充分",
        "要求补充或修正",
        "标记重大风险",
    ]
    assert model["case_state"] == "awaiting_maintainer_verification"
    assert model["maintainer_stage_ready"] is True
    assert all(option["authorized"] for option in item["options"])
    assert all(
        option["unavailable_reason"] is None
        for option in item["options"]
    )


def test_system_anomaly_and_low_risk_paths_have_no_mutation_controls(
    interactive_outputs,
):
    anomaly_model = interactive_outputs[1][
        "04_unauthorized_agent_verification"
    ]
    anomaly_text = participant_text(
        interactive_outputs[2][
            "04_unauthorized_agent_verification"
        ]
    )
    low_text = participant_text(
        interactive_outputs[2]["05_lightweight_low_risk"]
    )
    assert anomaly_model["system_handled_anomalies"]
    assert "系统已自动拒绝 1 次越权操作" in anomaly_text
    assert "该操作未生效" in anomaly_text
    assert "无需额外 AGM 治理判断" in low_text
    assert "可以进入正常代码审查" in low_text
    assert "<button" not in interactive_outputs[2][
        "04_unauthorized_agent_verification"
    ]
    assert "<button" not in interactive_outputs[2][
        "05_lightweight_low_risk"
    ]


def test_pre_final_fixture_uses_distinct_final_decision_page(
    interactive_outputs,
):
    model = interactive_outputs[1]["09_pre_final_decision"]
    rendered = interactive_outputs[2]["09_pre_final_decision"]
    assert model["review_actions"]["items"] == []
    assert model["review_actions"][
        "final_decision_entry_available"
    ] is True
    assert model["final_decision"]["available"] is True
    assert "最终人类决定" in rendered
    assert "维护者逐项检查" not in participant_text(rendered)
    assert "治理材料和维护者检查已经完成" in (
        participant_text(rendered)
    )


def test_participant_surface_has_no_raw_governance_ids_or_fixture_actor(
    interactive_outputs,
):
    forbidden = (
        "O-INDEPENDENT-REVIEW",
        "transition-",
        "evidence-",
        "finding-",
        "human-maintainer",
        "independent-human",
    )
    for scenario, rendered in interactive_outputs[2].items():
        visible = participant_text(rendered)
        for token in forbidden:
            assert token not in visible, (scenario, token)


def test_no_generic_action_menu_and_draft_state_is_explicit(
    interactive_outputs,
):
    forbidden = (
        "检查提交材料",
        "拒绝当前材料",
        "执行覆盖处理",
    )
    for scenario, rendered in interactive_outputs[2].items():
        visible = participant_text(rendered)
        for token in forbidden:
            assert token not in visible, (scenario, token)
        assert ">最终接受<" not in rendered.split("<details>", 1)[0]
    scoped = participant_text(
        interactive_outputs[2]["03_scoped_repair"]
    )
    assert "尚未选择处理结果" in scoped
    assert "检查不等于最终接受" in scoped


def test_no_task_scenarios_do_not_show_draft_banner(
    interactive_outputs,
):
    for scenario in (
        "01_multi_risk_missing",
        "02_material_partial_invalidation",
        "04_unauthorized_agent_verification",
        "05_lightweight_low_risk",
        "07_policy_migration_warning",
        "08_human_final_decision_closure",
    ):
        visible = participant_text(interactive_outputs[2][scenario])
        assert "尚未选择处理结果" not in visible
        assert "你的选择尚未提交" not in visible


def test_final_decision_static_surface_has_no_internal_terms(
    interactive_outputs,
):
    visible = participant_text(
        interactive_outputs[2]["09_pre_final_decision"]
    )
    required = (
        "最终人类决定",
        "治理材料和维护者检查已经完成",
        "接受本次贡献",
        "拒绝本次贡献",
        "要求修改后重新决定",
    )
    forbidden = (
        "actor",
        "canonical maintainer",
        "authority-controlled",
        "finding",
        "verification operation",
        "final-decision operation",
        "closure operation",
        "transition",
        "obligation",
        "compiler",
        "CSRF",
        "preview token",
        "live_actions_enabled",
    )
    for text in required:
        assert text in visible
    lowered = visible.lower()
    for text in forbidden:
        assert text.lower() not in lowered


def test_technical_details_are_folded_and_mobile_css_is_present(
    interactive_outputs,
):
    rendered = interactive_outputs[2]["03_scoped_repair"]
    assert "<details>" in rendered
    assert "<details open" not in rendered
    assert "@media(max-width:720px)" in rendered
    assert "grid-template-columns:1fr" in rendered
    assert "overflow-wrap:anywhere" in rendered
