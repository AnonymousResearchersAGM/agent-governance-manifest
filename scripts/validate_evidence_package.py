"""CLI wrapper for AGM evidence-package validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.governance import AGMError, load_governance_config, validate_evidence_package  # noqa: E402


def validate_package(package_path: Path | str) -> dict:
    return validate_evidence_package(Path(package_path), load_governance_config(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one AGM evidence package YAML file.")
    parser.add_argument("evidence_package", help="Path to an evidence package YAML file.")
    args = parser.parse_args()

    try:
        result = validate_package(args.evidence_package)
    except AGMError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["gate_state"]["governance_gate_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
