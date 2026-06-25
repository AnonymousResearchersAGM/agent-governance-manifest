import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.governance import (  # noqa: E402
    AGMError,
    build_contribution_evidence_package,
    classify_changed_files,
    generate_review_packet,
    load_governance_config,
    mark_human_review,
    validate_evidence_package,
    write_evidence_package,
)


def test_low_risk_complete_evidence_passes_and_is_human_decision_eligible():
    result = validate_evidence_package(ROOT / "evidence_packages" / "valid_low_risk.yml")

    assert result["risk_level"] == "low"
    assert result["gate_state"]["governance_gate_status"] == "pass"
    assert result["gate_state"]["final_acceptance_readiness"] == "eligible_for_human_decision"


def test_critical_auth_complete_evidence_is_eligible_but_not_accepted():
    result = validate_evidence_package(ROOT / "evidence_packages" / "valid_critical_auth.yml")

    assert result["risk_level"] == "critical"
    assert result["gate_state"]["human_review_status"] == "human_reviewed"
    assert result["gate_state"]["governance_gate_status"] == "pass"
    assert result["gate_state"]["final_acceptance_readiness"] == "eligible_for_human_decision"
    assert "Final approval" in result["final_decision_authority"]


def test_high_risk_missing_required_evidence_needs_evidence_or_blocks():
    result = validate_evidence_package(ROOT / "evidence_packages" / "missing_evidence.yml")

    assert result["risk_level"] == "high"
    assert result["gate_state"]["governance_gate_status"] in {"needs_evidence", "blocked"}
    assert "rationale" in result["missing_evidence"]
    assert "known_limitations" in result["missing_evidence"]


def test_critical_without_human_review_declaration_blocks(tmp_path):
    package = tmp_path / "critical_no_human.yml"
    package.write_text(
        """
schema_version: "agm.evidence_package/v0.1"
contribution_id: "critical-no-human"
changed_files:
  - "demo_app/auth.py"
summary: "Auth change with tests."
rationale: "Security-sensitive change needs explicit evidence."
risk_zone_assessment:
  declared_risk_level: "critical"
  declared_risk_zones: ["authentication"]
evidence_index: []
security_auth_impact_statement: "Token validation behavior changes."
tests_run:
  - command: "python -m pytest demo_app/tests/test_auth.py"
    outcome: "passed"
artifacts:
  - path: "review_packets/artifacts/critical_auth_pytest.txt"
known_limitations: "No network boundary is represented."
human_review_declaration: {}
generated_at: "2026-06-24T00:00:00Z"
""",
        encoding="utf-8",
    )

    result = validate_evidence_package(package)

    assert result["gate_state"]["human_review_status"] == "pending_human_review"
    assert result["gate_state"]["governance_gate_status"] == "blocked"


def test_placeholder_evidence_package_blocks():
    result = validate_evidence_package(ROOT / "evidence_packages" / "placeholder_evidence.yml")

    assert result["gate_state"]["evidence_status"] == "placeholder"
    assert result["gate_state"]["governance_gate_status"] == "blocked"
    assert result["placeholder_warnings"]


def test_missing_artifact_needs_evidence():
    result = validate_evidence_package(ROOT / "evidence_packages" / "missing_artifact.yml")

    assert result["risk_level"] == "high"
    assert result["gate_state"]["governance_gate_status"] == "needs_evidence"
    assert any("referenced artifact does not exist" in item for item in result["incomplete_evidence"])


def test_unknown_changed_file_path_uses_conservative_default_risk():
    result = classify_changed_files(["unknown/new_surface.py"])

    assert result["risk_level"] == "high"
    assert result["detected_risk_zones"][0]["zone"] == "unclassified_path"


def test_malformed_manifest_reports_clear_error(tmp_path):
    agm_dir = tmp_path / ".agm"
    agm_dir.mkdir()
    (agm_dir / "manifest.yml").write_text("schema_version: agm.manifest/v0.1\n", encoding="utf-8")

    with pytest.raises(AGMError, match="Malformed manifest"):
        load_governance_config(tmp_path)


def test_malformed_evidence_package_reports_clear_error(tmp_path):
    package = tmp_path / "bad.yml"
    package.write_text("contribution_id: missing-schema\nchanged_files: []\n", encoding="utf-8")

    with pytest.raises(AGMError, match="missing schema_version"):
        validate_evidence_package(package)


def test_generated_review_packet_contains_reference_vs_observed_table(tmp_path):
    outputs = generate_review_packet(ROOT / "evidence_packages" / "valid_critical_auth.yml", tmp_path)
    markdown = outputs["markdown"].read_text(encoding="utf-8")

    assert "| Governance Indicator | Reference / Required Value | Observed / Provided Value | Status |" in markdown
    assert "Final acceptance remains with human maintainers" in markdown


def test_contribution_side_agent_simulation_reads_agm_and_generates_valid_package(tmp_path):
    package = build_contribution_evidence_package(
        contribution_id="simulated-critical-auth",
        changed_files=["demo_app/auth.py", "demo_app/tests/test_auth.py"],
        summary="Simulated contribution-side agent evidence for auth token behavior.",
        rationale="Auth token behavior is security-sensitive and needs explicit regression evidence.",
        tests_run=[
            {
                "command": "python -m pytest demo_app/tests/test_auth.py",
                "outcome": "passed",
                "artifact": "review_packets/artifacts/critical_auth_pytest.txt",
            }
        ],
        artifacts=[
            {
                "path": "review_packets/artifacts/critical_auth_pytest.txt",
                "description": "Auth pytest output.",
            }
        ],
        known_limitations="No persistent session store or network boundary is implemented in this prototype.",
        security_auth_impact_statement="Token authentication and role checks remain the security-sensitive surface.",
        human_review_declaration={
            "required": True,
            "status": "human_reviewed",
            "reviewer": "human contributor",
            "reviewed_at": "2026-06-24T00:00:00Z",
            "review_scope": [
                "Reviewed auth-sensitive logic",
                "Checked test output",
            ],
            "statement": "Human review is complete and the change is ready for maintainer review.",
        },
        generated_at="2026-06-24T00:00:00Z",
    )
    output = write_evidence_package(package, tmp_path / "agent_generated.yml")
    validation = validate_evidence_package(output)

    assert package["risk_zone_assessment"]["agent_read_agm_files"] == [
        ".agm/manifest.yml",
        ".agm/risk_zones.yml",
        ".agm/evidence_requirements.yml",
    ]
    assert package["risk_zone_assessment"]["declared_risk_level"] == "critical"
    assert validation["gate_state"]["governance_gate_status"] == "pass"


def test_contribution_side_agent_simulation_marks_missing_facts_as_placeholders(tmp_path):
    package = build_contribution_evidence_package(
        contribution_id="simulated-incomplete-auth",
        changed_files=["demo_app/auth.py"],
        summary="Auth change without enough evidence.",
        generated_at="2026-06-24T00:00:00Z",
    )
    output = write_evidence_package(package, tmp_path / "agent_skeleton.yml")
    validation = validate_evidence_package(output)

    assert validation["gate_state"]["governance_gate_status"] == "blocked"
    assert validation["placeholder_warnings"]


def test_pending_human_review_is_not_human_reviewed_for_critical(tmp_path):
    package = build_contribution_evidence_package(
        contribution_id="pending-critical-auth",
        changed_files=["demo_app/auth.py"],
        summary="Auth change with pending human review.",
        rationale="Auth behavior is security-sensitive.",
        tests_run=[
            {
                "command": "python -m pytest demo_app/tests/test_auth.py",
                "outcome": "passed",
                "artifact": "review_packets/artifacts/critical_auth_pytest.txt",
            }
        ],
        artifacts=[
            {
                "path": "review_packets/artifacts/critical_auth_pytest.txt",
                "description": "Auth pytest output.",
            }
        ],
        known_limitations="No network boundary is represented.",
        security_auth_impact_statement="Token authentication behavior is affected.",
        human_review_declaration={
            "required": True,
            "status": "pending_human_review",
            "reviewer": None,
            "reviewed_at": None,
            "review_scope": None,
            "statement": "Human review is required before final acceptance.",
        },
        generated_at="2026-06-24T00:00:00Z",
    )
    output = write_evidence_package(package, tmp_path / "pending_critical.yml")
    validation = validate_evidence_package(output)

    assert validation["gate_state"]["human_review_status"] == "pending_human_review"
    assert validation["gate_state"]["governance_gate_status"] == "blocked"
    assert validation["gate_state"]["final_acceptance_readiness"] == "blocked_by_policy"


def test_governance_entrypoint_changes_are_flagged():
    result = classify_changed_files([".agm/manifest.yml", "AGENTS.md", "CLAUDE.md"])

    assert result["risk_level"] == "high"
    assert result["governance_entrypoint_changes"] == [".agm/manifest.yml", "AGENTS.md", "CLAUDE.md"]


def test_review_packet_contains_human_review_and_entrypoint_rows(tmp_path):
    package = build_contribution_evidence_package(
        contribution_id="entrypoint-change",
        changed_files=["AGENTS.md"],
        summary="Update AGM discovery pointer.",
        rationale="The agent entrypoint needs to point to .agm.",
        tests_run=[
            {
                "command": "python -m pytest tests/test_validation_hardening.py",
                "outcome": "passed",
                "artifact": "review_packets/artifacts/critical_auth_pytest.txt",
            }
        ],
        artifacts=[
            {
                "path": "review_packets/artifacts/critical_auth_pytest.txt",
                "description": "Pytest output placeholder artifact for governance-entrypoint example.",
            }
        ],
        known_limitations="Documentation and entrypoint behavior only.",
        generated_at="2026-06-24T00:00:00Z",
    )
    output = write_evidence_package(package, tmp_path / "entrypoint.yml")
    outputs = generate_review_packet(output, tmp_path / "packet")
    markdown = outputs["markdown"].read_text(encoding="utf-8")

    assert "| Human review declaration |" in markdown
    assert "| Governance entrypoint change |" in markdown
    assert "Needs maintainer attention" in markdown


def test_mark_human_review_updates_pending_declaration(tmp_path):
    package = build_contribution_evidence_package(
        contribution_id="mark-reviewed-critical",
        changed_files=["demo_app/auth.py"],
        summary="Auth change awaiting human declaration.",
        rationale="Auth behavior is security-sensitive.",
        tests_run=[
            {
                "command": "python -m pytest demo_app/tests/test_auth.py",
                "outcome": "passed",
                "artifact": "review_packets/artifacts/critical_auth_pytest.txt",
            }
        ],
        artifacts=[
            {
                "path": "review_packets/artifacts/critical_auth_pytest.txt",
                "description": "Auth pytest output.",
            }
        ],
        known_limitations="No network boundary is represented.",
        security_auth_impact_statement="Token authentication behavior is affected.",
        generated_at="2026-06-24T00:00:00Z",
    )
    output = write_evidence_package(package, tmp_path / "pending.yml")

    mark_human_review(
        output,
        reviewer="human contributor",
        scopes=["Reviewed auth-sensitive logic", "Checked test output"],
        statement="I reviewed this change and confirm it is ready for maintainer review.",
        reviewed_at="2026-06-24T00:00:00Z",
    )
    validation = validate_evidence_package(output)

    assert validation["gate_state"]["human_review_status"] == "human_reviewed"
    assert validation["gate_state"]["final_acceptance_readiness"] == "eligible_for_human_decision"
    assert "accepted" not in validation["gate_state"].values()
