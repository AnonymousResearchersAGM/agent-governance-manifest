from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.vnext.evidence import (  # noqa: E402
    bind_evidence,
    is_placeholder,
    validate_bound_evidence,
    validate_evidence_set,
)
from agm.vnext.models import BoundEvidence, VNextError  # noqa: E402
from agm.vnext.service import GovernanceService  # noqa: E402


def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    shutil.copytree(ROOT / ".agm", root / ".agm")
    shutil.copytree(ROOT / "skills", root / "skills")
    (root / "docs").mkdir()
    (root / "docs" / "guide.md").write_text("guide", encoding="utf-8")
    return root


def opened_case(tmp_path: Path):
    root = project(tmp_path)
    service = GovernanceService(root)
    case, _ = service.open_case(
        ["docs/guide.md"],
        requested_mode="declared_agent_mediated",
        actor="agent-1",
        actor_role="contributor_agent",
        case_id="evidence-case",
        base_commit="base",
        autonomy_profile="human_direct",
        timestamp="2026-07-25T00:00:00Z",
    )
    assert case is not None
    return root, service, case


def test_valid_evidence_is_bound_to_case_and_policy(tmp_path):
    root, _, case = opened_case(tmp_path)
    evidence = bind_evidence(
        case,
        obligation_ids=["O-SUMMARY"],
        evidence_type="contribution_summary",
        value="Updated the contributor guide.",
        source_actor="agent-1",
        affected_scope=["docs/guide.md"],
        root=root,
        observed_at="2026-07-25T00:00:00Z",
    )

    assert evidence.validity_state == "valid"
    assert evidence.contribution_fingerprint == case.contribution_fingerprint
    assert evidence.policy_fingerprint == case.policy_snapshot.policy_fingerprint


def test_evidence_rejects_unknown_obligation(tmp_path):
    root, _, case = opened_case(tmp_path)

    with pytest.raises(VNextError, match="unknown obligations"):
        bind_evidence(
            case,
            obligation_ids=["O-NOT-REAL"],
            evidence_type="x",
            value="value",
            source_actor="agent-1",
            root=root,
        )


def test_placeholder_evidence_is_invalid(tmp_path):
    root, _, case = opened_case(tmp_path)
    evidence = bind_evidence(
        case,
        obligation_ids=["O-SUMMARY"],
        evidence_type="contribution_summary",
        value="TODO: fill me",
        source_actor="agent-1",
        root=root,
    )

    assert evidence.validity_state == "invalid"
    assert "evidence value is a placeholder" in evidence.invalid_reasons


def test_explicit_none_is_allowed_for_known_limitations():
    assert is_placeholder("none")
    assert not is_placeholder("none", allow_explicit_none=True)


def test_stale_diff_binding_is_detected(tmp_path):
    root, _, case = opened_case(tmp_path)
    evidence = bind_evidence(
        case,
        obligation_ids=["O-SUMMARY"],
        evidence_type="contribution_summary",
        value="A factual summary.",
        source_actor="agent-1",
        root=root,
    )

    validate_bound_evidence(
        evidence,
        case,
        root=root,
        current_contribution_fingerprint="different",
    )

    assert evidence.validity_state == "stale"


def test_expired_evidence_is_detected(tmp_path):
    root, _, case = opened_case(tmp_path)
    evidence = bind_evidence(
        case,
        obligation_ids=["O-SUMMARY"],
        evidence_type="contribution_summary",
        value="A factual summary.",
        source_actor="agent-1",
        root=root,
        observed_at="2026-07-24T00:00:00Z",
        expires_at="2026-07-25T00:00:00Z",
    )

    validate_bound_evidence(
        evidence,
        case,
        root=root,
        current_contribution_fingerprint=case.contribution_fingerprint,
        now="2026-07-26T00:00:00Z",
    )

    assert evidence.validity_state == "expired"


def test_missing_artifact_is_invalid(tmp_path):
    root, _, case = opened_case(tmp_path)
    evidence = bind_evidence(
        case,
        obligation_ids=["O-SUMMARY"],
        evidence_type="contribution_summary",
        value="A factual summary.",
        source_actor="agent-1",
        artifact_path_value="artifacts/missing.txt",
        source_tool="pytest",
        root=root,
    )

    assert "referenced artifact is missing" in evidence.invalid_reasons


def test_artifact_path_traversal_is_rejected(tmp_path):
    root, _, case = opened_case(tmp_path)

    with pytest.raises(VNextError, match="escapes project root"):
        bind_evidence(
            case,
            obligation_ids=["O-SUMMARY"],
            evidence_type="contribution_summary",
            value="A factual summary.",
            source_actor="agent-1",
            artifact_path_value="../outside.txt",
            source_tool="pytest",
            root=root,
        )


def test_artifact_hash_mismatch_is_detected_after_mutation(tmp_path):
    root, _, case = opened_case(tmp_path)
    artifact = root / "artifact.txt"
    artifact.write_text("first", encoding="utf-8")
    evidence = bind_evidence(
        case,
        obligation_ids=["O-SUMMARY"],
        evidence_type="contribution_summary",
        value="A factual summary.",
        source_actor="agent-1",
        artifact_path_value="artifact.txt",
        source_tool="pytest",
        root=root,
    )
    artifact.write_text("second", encoding="utf-8")

    validate_bound_evidence(
        evidence,
        case,
        root=root,
        current_contribution_fingerprint=case.contribution_fingerprint,
    )

    assert "referenced artifact hash does not match" in evidence.invalid_reasons


def test_file_scope_mismatch_is_invalid(tmp_path):
    root, _, case = opened_case(tmp_path)
    evidence = bind_evidence(
        case,
        obligation_ids=["O-SUMMARY"],
        evidence_type="contribution_summary",
        value="A factual summary.",
        source_actor="agent-1",
        affected_scope=["outside.py"],
        root=root,
    )

    assert "outside the contribution" in " ".join(evidence.invalid_reasons)


def test_command_evidence_requires_environment_and_source_tool(tmp_path):
    root, _, case = opened_case(tmp_path)
    evidence = bind_evidence(
        case,
        obligation_ids=["O-SUMMARY"],
        evidence_type="contribution_summary",
        value="A factual summary.",
        source_actor="agent-1",
        command="pytest -q",
        root=root,
    )

    assert "evidence source tool is missing" in evidence.invalid_reasons
    assert "command evidence environment is missing" in evidence.invalid_reasons


def test_policy_snapshot_mismatch_is_invalid(tmp_path):
    root, _, case = opened_case(tmp_path)
    evidence = bind_evidence(
        case,
        obligation_ids=["O-SUMMARY"],
        evidence_type="contribution_summary",
        value="A factual summary.",
        source_actor="agent-1",
        root=root,
    )
    evidence.policy_fingerprint = "old-policy"

    validate_bound_evidence(
        evidence,
        case,
        root=root,
        current_contribution_fingerprint=case.contribution_fingerprint,
    )

    assert "different policy snapshot" in " ".join(evidence.invalid_reasons)


def test_conflicting_evidence_marks_both_items(tmp_path):
    root, _, case = opened_case(tmp_path)
    for evidence_id, value in [("one", "First summary"), ("two", "Second summary")]:
        case.evidence.append(
            bind_evidence(
                case,
                obligation_ids=["O-SUMMARY"],
                evidence_type="contribution_summary",
                value=value,
                source_actor="agent-1",
                evidence_id=evidence_id,
                root=root,
            )
        )

    findings = validate_evidence_set(case, root=root)

    assert all(item.validity_state == "conflicting" for item in case.evidence)
    assert any("conflicting evidence values" in item for item in findings)


def test_evidence_satisfying_no_obligation_is_invalid(tmp_path):
    root, _, case = opened_case(tmp_path)
    item = BoundEvidence(
        id="orphan",
        obligation_ids=[],
        affected_scope=["docs/guide.md"],
        contribution_fingerprint=case.contribution_fingerprint,
        policy_fingerprint=case.policy_snapshot.policy_fingerprint,
        evidence_type="contribution_summary",
        value="Orphan evidence",
        command=None,
        environment=None,
        artifact_path=None,
        artifact_hash=None,
        observed_at="2026-07-25T00:00:00Z",
        expires_at=None,
        source_actor="agent-1",
        source_tool=None,
    )

    validate_bound_evidence(
        item,
        case,
        root=root,
        current_contribution_fingerprint=case.contribution_fingerprint,
    )

    assert "evidence satisfies no known obligation" in item.invalid_reasons
