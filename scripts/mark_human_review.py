"""Mark an AGM evidence package as human-reviewed.

This records a governance declaration only. It is not approval, rejection, or
merge authorization.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.governance import AGMError, load_governance_config, mark_human_review, validate_evidence_package  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Update human review declaration in an AGM evidence package.")
    parser.add_argument("evidence_package")
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--scope", action="append", required=True, help="Review scope item. May be repeated.")
    parser.add_argument("--statement", required=True)
    parser.add_argument("--reviewed-at", default=None)
    args = parser.parse_args()

    try:
        output = mark_human_review(
            Path(args.evidence_package),
            reviewer=args.reviewer,
            scopes=args.scope,
            statement=args.statement,
            reviewed_at=args.reviewed_at,
        )
        validation = validate_evidence_package(output, load_governance_config(ROOT))
    except AGMError as exc:
        print(json.dumps({"updated": False, "error": str(exc)}, indent=2))
        return 2

    print(
        json.dumps(
            {
                "updated": True,
                "evidence_package": str(output),
                "human_review_declaration": validation["human_review_declaration"],
                "gate_state": validation["gate_state"],
                "note": "This declaration is not approval. Final decisions remain with human maintainers.",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
