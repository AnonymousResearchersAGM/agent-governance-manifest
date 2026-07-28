"""Generate deterministic D1--D10 PR-native diagnostic artifacts."""
from __future__ import annotations
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from agm.vnext.evidence import evidence_set_fingerprint  # noqa: E402
from agm.vnext.models import FinalDecision, HumanAttestation  # noqa: E402
from agm.vnext.pr_diagnostic import render_pr_diagnostic_html, render_pr_diagnostic_json, render_pr_diagnostic_markdown  # noqa: E402
from agm.vnext.runtime import DemoExecutionContext, use_execution_context  # noqa: E402
from agm.vnext.service import GovernanceService  # noqa: E402
from agm.vnext.storage import atomic_write_text  # noqa: E402
from generate_reviewer_guidance_demos import FIXED_TIME, make_project  # noqa: E402


SCENARIOS = (("D1_low_risk_readme", "README.md", "supervised_agent", {"summary": "README 非功能性文字", "changed_line_ranges": {"README.md": ["12–16"]}, "diff_hunks": {"README.md": "@@ -12 +12 @@\n-typo\n+word"}, "agent_activity": {"verified": True, "type": "coding agent", "modified_files": ["README.md"], "test_runs": [], "network": False}}), ("D2_high_risk_missing", "demo_app/auth.py", "supervised_agent", {"summary": "认证撤销逻辑", "changed_line_ranges": {"demo_app/auth.py": ["84–117"]}, "agent_activity": {"verified": True, "type": "coding agent"}}), ("D3_high_risk_ready", "demo_app/auth.py", "supervised_agent", {"summary": "认证撤销逻辑已测试", "changed_line_ranges": {"demo_app/auth.py": ["84–117"]}, "diff_hunks": {"demo_app/auth.py": "@@ -84,3 +84,4 @@\n+revoke(token)"}, "agent_activity": {"verified": True, "type": "coding agent", "test_runs": ["pytest"]}}), ("D4_no_agent_trace", "README.md", "human_direct", {"summary": "文档修正", "changed_line_ranges": {"README.md": ["5–8"]}}), ("D5_no_agent_high_missing_test", "demo_app/auth.py", "human_direct", {"summary": "认证修改", "changed_line_ranges": {"demo_app/auth.py": ["40–41"]}}), ("D6_declaration_conflict", "demo_app/auth.py", "supervised_agent", {"summary": "认证修改", "agent_activity": {"verified": True, "declared_summary": "只修改 README", "observed_summary": "修改认证代码"}}), ("D7_stale_test", "demo_app/auth.py", "supervised_agent", {"summary": "认证修改", "agent_activity": {"verified": True}}), ("D8_system_handled", "README.md", "human_direct", {"summary": "文档修正"}), ("D9_contributor_waiting", "demo_app/auth.py", "supervised_agent", {"summary": "贡献者补交前等待"}), ("D10_final_recommendation", "README.md", "human_direct", {"summary": "最终建议与平台状态"}))

def _prepare(service, case_id, ready=False, stale=False, final=False):
    case = service.storage.load_case(case_id)
    if ready or stale:
        for obligation in case.obligations:
            if obligation.type == "human_attestation": continue
            service.add_evidence(case_id, actor="contributor", actor_role="contributor", obligation_ids=[obligation.obligation_id], evidence_type=obligation.evidence_type, value="当前材料", command="pytest -q" if obligation.evidence_type == "test_command" else None, observed_at=FIXED_TIME)
        case = service.storage.load_case(case_id)
        if stale:
            for item in case.evidence:
                if item.evidence_type == "test_command": item.contribution_fingerprint = "old-commit"
            service.storage.save_case(case)
        elif any(item.type == "human_attestation" for item in case.obligations):
            case.attestations.append(HumanAttestation("demo-self-review", "contributor-human", "accountable_human", FIXED_TIME, case.changed_files, "已检查当前版本", [], case.policy_snapshot.policy_fingerprint, case.contribution_fingerprint, evidence_set_fingerprint(case.evidence)))
            service.storage.save_case(case)
    if final:
        case = service.storage.load_case(case_id)
        case.final_decision = FinalDecision("demo-final", "maintainer", "maintainer", FIXED_TIME, "accept", "演示建议")
        service.storage.save_case(case)

def generate(output: Path) -> dict[str, str]:
    output.mkdir(parents=True, exist_ok=True); hashes = {}
    with tempfile.TemporaryDirectory(prefix="agm-pr-diagnostic-") as raw:
        for slug, path, profile, context in SCENARIOS:
            with use_execution_context(DemoExecutionContext("pr-" + slug, FIXED_TIME, "demo-key")):
                root = make_project(Path(raw), slug); service = GovernanceService(root)
                case, _ = service.open_case([path], requested_mode="declared_agent_mediated" if profile != "human_direct" else "maintainer_requested", actor="contributor", actor_role="contributor", case_id="case-" + slug, base_commit="d" * 40, autonomy_profile=profile, timestamp=FIXED_TIME); assert case
                _prepare(service, case.id, ready=slug in {"D1_low_risk_readme", "D3_high_risk_ready", "D4_no_agent_trace", "D10_final_recommendation"}, stale=slug == "D7_stale_test", final=slug == "D10_final_recommendation")
                view = service.pr_diagnosis(case.id, contribution=context)
                scenario = output / slug
                files = {"diagnosis.json": render_pr_diagnostic_json(view), "report.md": render_pr_diagnostic_markdown(view), "report.html": render_pr_diagnostic_html(view)}
                for name, text in files.items():
                    target = scenario / name; atomic_write_text(target, text); hashes[(scenario / name).relative_to(output).as_posix()] = hashlib.sha256(text.encode()).hexdigest()
    atomic_write_text(output / "expected_sha256.json", json.dumps(hashes, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return hashes

if __name__ == "__main__":
    result = generate(ROOT / "examples" / "pr_native_diagnostic" / "outputs")
    print(json.dumps({"generated": len(result)}, ensure_ascii=False))
