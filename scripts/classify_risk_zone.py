"""CLI wrapper for AGM risk-zone classification."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.governance import AGMError, classify_changed_files, load_governance_config  # noqa: E402


def load_manifest(path: Path | None = None) -> dict:
    """Compatibility helper for older tests/scripts."""
    return load_governance_config(ROOT).manifest


def classify_files(changed_files: list[str], manifest: dict | None = None, inspect_content: bool = False) -> dict:
    """Compatibility helper that returns the previous top-level names too."""
    result = classify_changed_files(changed_files, load_governance_config(ROOT))
    return {
        **result,
        "highest_risk_level": result["risk_level"],
        "matched_risk_zones": [
            {
                "file": item["file"],
                "zone": item["zone"],
                "level": item["risk_level"],
                "reason": item["reason"],
            }
            for item in result["detected_risk_zones"]
        ],
        "risk_escalations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify changed files under AGM risk zones.")
    parser.add_argument("changed_files", nargs="+", help="Changed file paths relative to the repository root.")
    args = parser.parse_args()

    try:
        result = classify_changed_files(args.changed_files, load_governance_config(ROOT))
    except AGMError as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
