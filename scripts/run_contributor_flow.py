"""Run the contribution-side AGM validation helper."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.governance import AGMError, load_governance_config, validate_evidence_package  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a contribution-side AGM evidence package.")
    parser.add_argument("evidence_package", help="Path to one evidence package YAML file.")
    args = parser.parse_args()

    try:
        result = validate_evidence_package(Path(args.evidence_package), load_governance_config(ROOT))
    except AGMError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2))
        return 2

    response = {
        "contribution_id": result["contribution_id"],
        "risk_level": result["risk_level"],
        "gate_state": result["gate_state"],
        "missing_evidence": result["missing_evidence"],
        "placeholder_warnings": result["placeholder_warnings"],
        "next_steps_for_contributor": [
            "Provide factual, independently checkable evidence for any missing fields.",
            "Replace placeholder values such as TODO, TBD, N/A, or lorem ipsum.",
            "For critical risk, include a human review declaration before maintainer decision.",
            "Do not include private prompts, chain-of-thought, or agent trace logs.",
        ],
    }
    print(json.dumps(response, indent=2))
    return 0 if result["gate_state"]["governance_gate_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
