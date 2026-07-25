from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.governance import classify_changed_files  # noqa: E402
from agm.vnext.config import load_vnext_config  # noqa: E402
from agm.vnext.models import MatchedRule  # noqa: E402
from agm.vnext.obligations import compile_obligations  # noqa: E402
from agm.vnext.risk import resolve_risk  # noqa: E402


def compile_for(files, *, autonomy="human_direct", assurance="standard"):
    config = load_vnext_config(ROOT)
    resolution = resolve_risk(config, files)
    compiled = compile_obligations(
        config,
        resolution.matched_rules,
        resolution.interaction_rules,
        autonomy_profile_id=autonomy,
        assurance_profile_id=assurance,
    )
    return resolution, compiled


def test_v01_compatibility_retains_zones_but_selects_highest_profile():
    result = classify_changed_files(["docs/guide.md", "demo_app/auth.py"])

    assert {item["zone"] for item in result["detected_risk_zones"]} == {
        "documentation",
        "authentication",
    }
    assert result["risk_level"] == "critical"
    assert "security_auth_impact_statement" in result["required_fields"]


def test_low_and_critical_rules_are_both_preserved():
    resolution, compiled = compile_for(["docs/guide.md", "demo_app/auth.py"])

    assert resolution.overall_risk_level == "critical"
    assert {item.rule_id for item in resolution.matched_rules} == {
        "documentation-low",
        "authentication-critical",
    }
    assert {"O-SUMMARY", "O-AUTH-IMPACT", "O-HUMAN-ATTEST"} <= {
        item.obligation_id for item in compiled.obligations
    }


def test_two_high_zones_retain_distinct_policy_obligation():
    resolution, compiled = compile_for([".agm/manifest.yml", "requirements.txt"])

    assert resolution.overall_risk_level == "high"
    assert {"governance-policy-high", "configuration-high"} <= {
        item.rule_id for item in resolution.matched_rules
    }
    assert "O-POLICY-IMPACT" in {
        item.obligation_id for item in compiled.obligations
    }


def test_governance_self_modification_requires_independent_review():
    resolution, compiled = compile_for(
        [".agm/manifest.yml", "src/agm/vnext/risk.py"]
    )

    assert resolution.overall_risk_level == "critical"
    assert [item["id"] for item in resolution.interaction_rules] == [
        "governance-self-modification"
    ]
    independent = next(
        item
        for item in compiled.obligations
        if item.obligation_id == "O-INDEPENDENT-REVIEW"
    )
    assert independent.blocking
    assert independent.interaction_ids == ["governance-self-modification"]


def test_duplicate_obligations_are_deduplicated_with_all_sources():
    resolution, compiled = compile_for(
        ["demo_app/config.py", "demo_app/tests/test_auth.py"]
    )

    summaries = [
        item for item in compiled.obligations if item.obligation_id == "O-SUMMARY"
    ]
    assert len(summaries) == 1
    assert summaries[0].source_rule_ids == [
        "configuration-high",
        "test-strategy-high",
    ]


def test_unknown_path_fallback_does_not_discard_documentation_rule():
    resolution, compiled = compile_for(["docs/guide.md", "new/plugin.py"])

    assert {item.rule_id for item in resolution.matched_rules} == {
        "documentation-low",
        "unclassified-surface",
    }
    assert resolution.overall_risk_level == "high"
    assert "O-LIMITATIONS" in {
        item.obligation_id for item in compiled.obligations
    }


def test_change_type_selector_is_an_extension_point():
    config = load_vnext_config(ROOT)
    resolution = resolve_risk(
        config,
        ["unknown/settings.dat"],
        change_tags=["deployment_configuration"],
    )

    assert "configuration-high" in {
        item.rule_id for item in resolution.matched_rules
    }


def test_semantic_target_selector_is_an_extension_point():
    config = load_vnext_config(ROOT)
    resolution = resolve_risk(
        config,
        ["unknown/identity.logic"],
        semantic_targets=["authentication"],
    )

    assert resolution.overall_risk_level == "critical"
    assert "authentication-critical" in {
        item.rule_id for item in resolution.matched_rules
    }


def test_autonomy_adds_obligations_without_changing_technical_risk():
    resolution, compiled = compile_for(
        ["docs/guide.md"], autonomy="autonomous_agent"
    )

    assert resolution.overall_risk_level == "low"
    assert {"O-AGENT-SCOPE", "O-HUMAN-ATTEST"} <= {
        item.obligation_id for item in compiled.obligations
    }


def test_heightened_assurance_adds_independent_review():
    resolution, compiled = compile_for(
        ["docs/guide.md"], assurance="heightened"
    )

    assert resolution.overall_risk_level == "low"
    assert "O-INDEPENDENT-REVIEW" in {
        item.obligation_id for item in compiled.obligations
    }


def test_blocking_overrides_warning_for_compatible_duplicates():
    config = load_vnext_config(ROOT)
    rules = [
        MatchedRule(
            id="one",
            rule_id="one",
            zone="one",
            risk_level="low",
            affected_paths=["a"],
            selector_reasons=["test"],
            obligation_ids=["O-SUMMARY"],
            obligation_overrides={"O-SUMMARY": {"blocking": False}},
        ),
        MatchedRule(
            id="two",
            rule_id="two",
            zone="two",
            risk_level="high",
            affected_paths=["b"],
            selector_reasons=["test"],
            obligation_ids=["O-SUMMARY"],
            obligation_overrides={"O-SUMMARY": {"blocking": True}},
        ),
    ]
    result = compile_obligations(
        config,
        rules,
        [],
        autonomy_profile_id="human_direct",
        assurance_profile_id="standard",
    )

    assert result.obligations[0].blocking
    assert not result.findings


def test_contradictory_obligation_override_creates_blocking_finding():
    config = load_vnext_config(ROOT)
    rule = MatchedRule(
        id="conflict",
        rule_id="conflict",
        zone="test",
        risk_level="high",
        affected_paths=["a"],
        selector_reasons=["test"],
        obligation_ids=["O-SUMMARY"],
        obligation_overrides={"O-SUMMARY": {"evidence_type": "different_type"}},
    )
    result = compile_obligations(
        config,
        [rule],
        [],
        autonomy_profile_id="human_direct",
        assurance_profile_id="standard",
    )

    assert result.obligations[0].status == "policy_conflict"
    assert result.findings[0].blocking
    assert result.findings[0].code == "policy_conflict"
