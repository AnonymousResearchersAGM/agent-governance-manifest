"""Deterministically simulate a contribution-side agent producing AGM evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.governance import (  # noqa: E402
    AGMError,
    build_contribution_evidence_package,
    load_governance_config,
    validate_evidence_package,
    write_evidence_package,
)


def parse_artifacts(values: list[str] | None) -> list[dict[str, str]]:
    artifacts = []
    for value in values or []:
        if "::" in value:
            path, description = value.split("::", 1)
        else:
            path, description = value, "contribution artifact"
        artifacts.append({"path": path, "description": description})
    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Simulate a contribution-side agent reading AGM and writing one evidence package."
    )
    parser.add_argument("--contribution-id", required=True)
    parser.add_argument("--changed-files", nargs="+", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--rationale", default="")
    parser.add_argument("--test-command", default="")
    parser.add_argument("--test-outcome", default="")
    parser.add_argument(
        "--artifact",
        action="append",
        help="Artifact path, optionally as path::description. May be repeated.",
    )
    parser.add_argument("--known-limitations", default="")
    parser.add_argument("--security-auth-impact", default="")
    parser.add_argument("--human-review-status", choices=["pending_human_review", "human_reviewed"], default="")
    parser.add_argument("--human-reviewer-role", default="")
    parser.add_argument("--human-review-statement", default="")
    parser.add_argument("--output", required=True, help="Path for the generated evidence package YAML.")
    args = parser.parse_args()

    tests_run = []
    if args.test_command or args.test_outcome:
        tests_run.append(
            {
                "command": args.test_command,
                "outcome": args.test_outcome or "not recorded",
            }
        )
        artifacts = parse_artifacts(args.artifact)
        if artifacts:
            tests_run[0]["artifact"] = artifacts[0]["path"]
    else:
        artifacts = parse_artifacts(args.artifact)

    human_declaration = None
    if args.human_review_status or args.human_reviewer_role or args.human_review_statement:
        human_declaration = {
            "required": True,
            "status": args.human_review_status or "pending_human_review",
            "reviewer": args.human_reviewer_role or None,
            "reviewed_at": None,
            "review_scope": None,
            "statement": args.human_review_statement or "Human review is required before final acceptance.",
        }

    try:
        config = load_governance_config(ROOT)
        package = build_contribution_evidence_package(
            contribution_id=args.contribution_id,
            changed_files=args.changed_files,
            summary=args.summary,
            rationale=args.rationale,
            tests_run=tests_run if tests_run else None,
            artifacts=artifacts,
            known_limitations=args.known_limitations,
            security_auth_impact_statement=args.security_auth_impact,
            human_review_declaration=human_declaration,
            config=config,
        )
        output = write_evidence_package(package, Path(args.output))
        validation = validate_evidence_package(output, config)
    except AGMError as exc:
        print(json.dumps({"generated": False, "error": str(exc)}, indent=2))
        return 2

    result = {
        "generated": True,
        "evidence_package": str(output),
        "agent_read_agm_files": package["risk_zone_assessment"]["agent_read_agm_files"],
        "detected_risk_level": package["risk_zone_assessment"]["declared_risk_level"],
        "required_evidence": package["risk_zone_assessment"]["required_evidence"],
        "post_generation_gate_state": validation["gate_state"],
        "missing_evidence": validation["missing_evidence"],
        "placeholder_warnings": validation["placeholder_warnings"],
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
