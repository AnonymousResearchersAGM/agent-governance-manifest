from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.vnext.config import (  # noqa: E402
    expanded_profile,
    load_vnext_config,
    safe_project_path,
)
from agm.vnext.models import VNextError  # noqa: E402
from agm.vnext.policy import (  # noqa: E402
    contribution_fingerprint,
    decide_intake,
    make_policy_snapshot,
)
from agm.vnext.risk import resolve_risk  # noqa: E402


def copied_policy(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    shutil.copytree(ROOT / ".agm", root / ".agm")
    shutil.copytree(ROOT / "skills", root / "skills")
    return root


def rewrite_yaml(path: Path, mutator) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    mutator(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def test_vnext_config_loads_development_policy():
    config = load_vnext_config(ROOT)

    assert config.manifest["schema_version"] == "agm.manifest/v0.2-dev"
    assert len(config.risk_rules) == 7
    assert "O-HUMAN-ATTEST" in config.obligations
    assert len(config.policy_fingerprint) == 64


def test_config_rejects_non_development_schema(tmp_path):
    root = copied_policy(tmp_path)
    rewrite_yaml(
        root / ".agm" / "manifest.yml",
        lambda data: data.update(schema_version="agm.manifest/v0.1"),
    )

    with pytest.raises(VNextError, match="invalid schema_version"):
        load_vnext_config(root)


def test_config_rejects_duplicate_role_ids(tmp_path):
    root = copied_policy(tmp_path)

    def duplicate(data):
        data["roles"].append(dict(data["roles"][0]))

    rewrite_yaml(root / ".agm" / "roles" / "roles.yml", duplicate)

    with pytest.raises(VNextError, match="Duplicate role id"):
        load_vnext_config(root)


def test_config_rejects_unknown_obligation_verifier_role(tmp_path):
    root = copied_policy(tmp_path)

    def corrupt(data):
        data["obligations"][0]["verifier_roles"] = ["ghost"]

    rewrite_yaml(root / ".agm" / "policies" / "evidence_profiles.yml", corrupt)

    with pytest.raises(VNextError, match="unknown verifier roles"):
        load_vnext_config(root)


def test_config_rejects_profile_inheritance_cycle(tmp_path):
    root = copied_policy(tmp_path)

    def cycle(data):
        data["autonomy_profiles"][1]["extends"] = "autonomous_agent"

    rewrite_yaml(root / ".agm" / "profiles" / "autonomy_profiles.yml", cycle)

    with pytest.raises(VNextError, match="Cyclic Autonomy profile"):
        load_vnext_config(root)


def test_config_rejects_unknown_transition_state(tmp_path):
    root = copied_policy(tmp_path)

    def corrupt(data):
        data["transitions"][0]["to"] = "missing-state"

    rewrite_yaml(root / ".agm" / "workflows" / "state_machine.yml", corrupt)

    with pytest.raises(VNextError, match="unknown target state"):
        load_vnext_config(root)


def test_config_rejects_transition_without_role_permission(tmp_path):
    root = copied_policy(tmp_path)

    def corrupt(data):
        data["permissions"]["system"].remove("resolve_policy")

    rewrite_yaml(root / ".agm" / "roles" / "permissions.yml", corrupt)

    with pytest.raises(VNextError, match="without matching permission"):
        load_vnext_config(root)


def test_safe_project_path_rejects_traversal(tmp_path):
    with pytest.raises(VNextError, match="escapes project root"):
        safe_project_path(tmp_path, "../outside.yml")


def test_profile_expansion_unions_parent_obligations():
    config = load_vnext_config(ROOT)
    profile = expanded_profile(config.autonomy_profiles, "autonomous_agent")

    assert profile["obligation_ids"] == ["O-AGENT-SCOPE", "O-HUMAN-ATTEST"]


def test_policy_snapshot_binds_base_and_policy():
    config = load_vnext_config(ROOT)
    snapshot = make_policy_snapshot(
        config, base_commit="abc123", resolved_at="2026-07-25T00:00:00Z"
    )

    assert snapshot.base_commit == "abc123"
    assert snapshot.policy_fingerprint == config.policy_fingerprint
    assert snapshot.schema_version == "agm.policy_snapshot/v0.2-dev"


def test_ordinary_intake_means_no_package_not_human_authorship():
    config = load_vnext_config(ROOT)
    resolution = resolve_risk(config, ["docs/guide.md"])
    intake = decide_intake("ordinary", resolution)

    assert not intake.case_required
    assert intake.package_status == "no_agm_package_submitted"
    assert "does not confirm human authorship" in intake.reason


def test_policy_required_rule_overrides_requested_ordinary_mode():
    config = load_vnext_config(ROOT)
    resolution = resolve_risk(config, ["demo_app/auth.py"])
    intake = decide_intake("ordinary", resolution)

    assert intake.case_required
    assert intake.effective_mode == "policy_required"
    assert "change, not inferred authorship" in intake.reason


def test_declared_agent_mode_opens_case_without_identity_inference():
    config = load_vnext_config(ROOT)
    resolution = resolve_risk(config, ["docs/guide.md"])
    intake = decide_intake("declared_agent_mediated", resolution)

    assert intake.case_required
    assert intake.effective_mode == "declared_agent_mediated"
    assert "no claim" in intake.reason


def test_contribution_fingerprint_changes_when_file_content_changes(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("before", encoding="utf-8")
    first = contribution_fingerprint(
        tmp_path, ["sample.txt"], base_commit="base"
    )
    path.write_text("after", encoding="utf-8")
    second = contribution_fingerprint(
        tmp_path, ["sample.txt"], base_commit="base"
    )

    assert first != second


def test_contribution_fingerprint_is_order_independent(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")

    first = contribution_fingerprint(
        tmp_path, ["a.txt", "b.txt"], base_commit="base"
    )
    second = contribution_fingerprint(
        tmp_path, ["b.txt", "a.txt"], base_commit="base"
    )

    assert first == second
