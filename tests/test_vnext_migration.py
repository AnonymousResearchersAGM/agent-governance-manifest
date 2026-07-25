from __future__ import annotations

import shutil
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.vnext.config import load_vnext_config  # noqa: E402
from agm.vnext.migration import check_migration  # noqa: E402
from agm.vnext.service import GovernanceService  # noqa: E402


def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    shutil.copytree(ROOT / ".agm", root / ".agm")
    shutil.copytree(ROOT / "skills", root / "skills")
    (root / "docs").mkdir()
    (root / "docs" / "guide.md").write_text("guide", encoding="utf-8")
    return root


def rewrite(path: Path, mutator) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    mutator(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def open_case(root: Path):
    service = GovernanceService(root)
    case, _ = service.open_case(
        ["docs/guide.md"],
        requested_mode="declared_agent_mediated",
        actor="agent-1",
        actor_role="contributor_agent",
        case_id="migration-case",
        base_commit="base",
        autonomy_profile="human_direct",
    )
    assert case is not None
    return service, case


def test_unchanged_policy_needs_no_migration(tmp_path):
    root = project(tmp_path)
    service, case = open_case(root)

    diagnostic = service.migration_check(case.id)

    assert not diagnostic.policy_changed
    assert not diagnostic.must_migrate
    assert diagnostic.may_remain_on_original_snapshot


def test_unrelated_interface_change_preserves_obligations(tmp_path):
    root = project(tmp_path)
    _, case = open_case(root)
    rewrite(
        root / ".agm" / "interfaces" / "contributor_panel.yml",
        lambda data: data.update(title="Reworded panel title"),
    )

    diagnostic = check_migration(case, load_vnext_config(root))

    assert diagnostic.policy_changed
    assert diagnostic.added_obligations == []
    assert diagnostic.removed_obligations == []
    assert diagnostic.changed_obligations == []
    assert diagnostic.may_remain_on_original_snapshot


def test_changed_obligation_marks_bound_evidence_for_revalidation(tmp_path):
    root = project(tmp_path)
    service, case = open_case(root)
    evidence = service.add_evidence(
        case.id,
        actor="agent-1",
        actor_role="contributor_agent",
        obligation_ids=["O-SUMMARY"],
        evidence_type="contribution_summary",
        value="Updated the guide.",
        source_tool="codex",
    )

    def change_summary(data):
        next(item for item in data["obligations"] if item["id"] == "O-SUMMARY")[
            "description"
        ] = "A changed summary definition."

    rewrite(
        root / ".agm" / "policies" / "evidence_profiles.yml",
        change_summary,
    )
    diagnostic = check_migration(
        service.storage.load_case(case.id), load_vnext_config(root)
    )

    assert "O-SUMMARY" in diagnostic.changed_obligations
    assert evidence.id in diagnostic.evidence_requiring_revalidation
    assert not diagnostic.must_migrate


def test_new_critical_blocking_obligation_requires_migration(tmp_path):
    root = project(tmp_path)
    _, case = open_case(root)

    def add_obligation(data):
        data["obligations"].append(
            {
                "id": "O-NEW-CRITICAL",
                "type": "evidence",
                "severity": "critical",
                "blocking": True,
                "verifier_roles": ["maintainer"],
                "evidence_type": "critical_new",
                "description": "New critical requirement.",
            }
        )

    def attach_to_docs(data):
        next(
            item for item in data["risk_rules"] if item["id"] == "documentation-low"
        )["obligation_ids"].append("O-NEW-CRITICAL")

    rewrite(
        root / ".agm" / "policies" / "evidence_profiles.yml",
        add_obligation,
    )
    rewrite(root / ".agm" / "policies" / "risk_rules.yml", attach_to_docs)

    diagnostic = check_migration(case, load_vnext_config(root))

    assert diagnostic.added_obligations == ["O-NEW-CRITICAL"]
    assert diagnostic.must_migrate
    assert not diagnostic.may_remain_on_original_snapshot
