from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ten_scenario_demo_runs_in_fresh_temporary_project():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_vnext_demo.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = json.loads(result.stdout)

    assert output["ok"]
    assert len(output["scenarios"]) == 10
    assert output["checks"]["ordinary_no_case"]
    assert output["checks"]["multi_risk_critical"]
    assert output["checks"]["conflict_blocks"]
