"""Run the maintainer-side AGM review packet helper."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.governance import AGMError, generate_review_packet, load_governance_config, validate_evidence_package  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate maintainer-facing AGM review packet files.")
    parser.add_argument("evidence_package", help="Path to one evidence package YAML file.")
    parser.add_argument("--output-dir", default=str(ROOT / "review_packets"), help="Output directory.")
    args = parser.parse_args()

    try:
        config = load_governance_config(ROOT)
        validation = validate_evidence_package(Path(args.evidence_package), config)
        outputs = generate_review_packet(Path(args.evidence_package), Path(args.output_dir), config)
    except AGMError as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 2

    result = {
        "contribution_id": validation["contribution_id"],
        "risk_level": validation["risk_level"],
        "gate_state": validation["gate_state"],
        "review_packet_json": str(outputs["json"]),
        "review_packet_markdown": str(outputs["markdown"]),
        "human_maintainer_final_decision_reminder": validation["final_decision_authority"],
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
