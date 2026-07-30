"""Check deterministic participant scenarios for cross-scenario leakage."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_pr_diagnostic_demos import SCENARIOS  # noqa: E402

OUTPUT = ROOT / "examples" / "pr_native_diagnostic" / "outputs"


def _visible(slug: str) -> str:
    return (OUTPUT / slug / "report.html").read_text(encoding="utf8").split(
        "<details>", 1
    )[0]


def main() -> int:
    expected = {item[0] for item in SCENARIOS}
    actual = {item.name for item in OUTPUT.iterdir() if item.is_dir()}
    if actual != expected:
        raise SystemExit(
            f"Scenario directories differ: missing={sorted(expected-actual)} "
            f"extra={sorted(actual-expected)}"
        )
    if "D3_high_risk_ready" in _visible("D3_high_risk_ready"):
        raise SystemExit("D3 leaks its scenario slug")
    d4 = _visible("D4_no_agent_trace")
    if "实现逻辑" not in d4 or any(
        token in d4 for token in ("文字准确性", "命令示例和链接")
    ):
        raise SystemExit("D4 normal-review wording is not code-specific")
    d6b = _visible("D6B_repair_requested")
    if "维护者已经要求贡献者修正工具使用说明" not in d6b or "由维护者决定是否要求" in d6b:
        raise SystemExit("D6B repair wording is inconsistent")
    d7 = (
        (OUTPUT / "D7_stale_test" / "diagnosis.json").read_text(encoding="utf8")
        + (OUTPUT / "D7_stale_test" / "case.json").read_text(encoding="utf8")
    )
    if "demo_app/tasks.py" not in d7 or any(
        token in d7.lower()
        for token in ("token revocation", "tests/test_auth.py", "authentication")
    ):
        raise SystemExit("D7 contains non-task scenario material")
    d8 = _visible("D8_system_handled")
    if "系统已阻止一次未经授权的操作" not in d8 or "verify_evidence" in d8:
        raise SystemExit("D8 denied-operation wording is invalid")
    d9 = json.loads(
        (OUTPUT / "D9_contributor_waiting" / "diagnosis.json").read_text(
            encoding="utf8"
        )
    )
    kinds = {item["object_type"] for item in d9["inspection_objects"]}
    if not {
        "ContributionSummaryInspectionObject",
        "ChangedFilesInspectionObject",
    } <= kinds:
        raise SystemExit("D9 does not use distinct summary and changed-files material")
    d10 = _visible("D10_final_recommendation")
    if not all(
        token in d10
        for token in ("未连接代码托管平台", "未通过本页批准 PR", "未通过本页合并 PR")
    ):
        raise SystemExit("D10 host-platform boundary is missing")
    print("PR diagnostic scenario consistency passed for 11 pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
