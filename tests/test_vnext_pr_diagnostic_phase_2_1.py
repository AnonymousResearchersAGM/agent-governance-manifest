from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from agm.vnext.models import VNextError  # noqa: E402
from agm.vnext.pr_diagnostic import SidecarEvidenceStore  # noqa: E402
from agm.vnext.pr_diagnostic.presenters import render_pr_diagnostic_html  # noqa: E402
from agm.vnext.runtime import DemoExecutionContext, use_execution_context  # noqa: E402
from agm.vnext.service import GovernanceService  # noqa: E402
from generate_reviewer_guidance_demos import FIXED_TIME, make_project  # noqa: E402


def _case(tmp_path, *, path: str, profile: str = "supervised_agent"):
    root = make_project(tmp_path, "pr-diagnostic")
    service = GovernanceService(root)
    case, _ = service.open_case(
        [path], requested_mode="declared_agent_mediated", actor="contributor",
        actor_role="contributor", case_id="pr-case", base_commit="a" * 40,
        autonomy_profile=profile, timestamp=FIXED_TIME,
    )
    assert case is not None
    return root, service, case


def test_low_risk_readme_keeps_compiled_requirements_without_extra_tests(tmp_path):
    with use_execution_context(DemoExecutionContext("pr-low", FIXED_TIME, "key")):
        _, service, _ = _case(tmp_path, path="README.md")
        view = service.pr_diagnosis("pr-case", contribution={"summary": "修正 README 文字", "changed_line_ranges": {"README.md": ["12–16"]}, "agent_activity": {"verified": True, "type": "coding", "modified_files": ["README.md"]}})
    assert view.diagnostic_status == "需要贡献者先处理"  # direct unit case intentionally has no materials
    assert {item["obligation_ref"] for item in view.expected_requirements} == {"O-SUMMARY", "O-CHANGED-FILES", "O-AGENT-SCOPE"}
    assert "O-TEST-COMMAND" not in {item["obligation_ref"] for item in view.expected_requirements}
    assert view.risk_findings[0].affected_line_ranges == ("12–16",)


def test_high_risk_missing_test_is_derived_from_compiled_obligation(tmp_path):
    with use_execution_context(DemoExecutionContext("pr-high", FIXED_TIME, "key")):
        _, service, _ = _case(tmp_path, path="demo_app/auth.py")
        view = service.pr_diagnosis("pr-case", contribution={"changed_line_ranges": {"demo_app/auth.py": ["84–117"]}, "agent_activity": {"verified": True}})
    test_gap = next(item for item in view.evidence_gaps if "O-TEST-COMMAND" in item.obligation_refs)
    assert test_gap.blocking and test_gap.responsibility == "contributor"
    assert "authentication-critical" in test_gap.risk_rule_refs
    assert view.diagnostic_status == "需要贡献者先处理"


def test_missing_diff_is_never_invented_and_main_layer_has_local_boundary(tmp_path):
    with use_execution_context(DemoExecutionContext("pr-diff", FIXED_TIME, "key")):
        _, service, _ = _case(tmp_path, path="demo_app/auth.py")
        view = service.pr_diagnosis("pr-case")
    diff = next(item for item in view.inspection_objects if item.object_type == "DiffInspectionObject")
    assert diff.availability == "unavailable" and diff.inline_content is None
    page = render_pr_diagnostic_html(view)
    assert "当前未提供可查看的代码差异" in page
    assert "不会修改代码，不会执行 git merge" in page
    assert "state machine" not in page.split("<details>")[0]


def test_no_agent_trace_does_not_assert_human_authorship(tmp_path):
    with use_execution_context(DemoExecutionContext("pr-none", FIXED_TIME, "key")):
        _, service, _ = _case(tmp_path, path="README.md", profile="human_direct")
        view = service.pr_diagnosis("pr-case")
    assert view.agent_involvement["status"] == "none"
    assert "可能主要由人工完成" in view.agent_involvement["message"]


def test_sidecar_is_immutable_untracked_and_rejects_private_material(tmp_path):
    store = SidecarEvidenceStore(tmp_path)
    receipt = store.write_package(case_id="c", contribution_fingerprint="f", policy_fingerprint="p", producer="test", created_at=FIXED_TIME, artifacts=[{"type": "test", "summary": "pytest passed", "digest": "x"}])
    package = tmp_path / ".agm-work" / "evidence_store" / receipt.package_digest / "package.json"
    assert package.is_file() and ".agm-work" in package.as_posix()
    again = store.write_package(case_id="c", contribution_fingerprint="f", policy_fingerprint="p", producer="test", created_at=FIXED_TIME, artifacts=[{"type": "test", "summary": "pytest passed", "digest": "x"}])
    assert again.package_digest == receipt.package_digest
    with pytest.raises(VNextError):
        store.write_package(case_id="c", contribution_fingerprint="f", policy_fingerprint="p", producer="test", artifacts=[{"summary": "raw prompt: secret"}])
