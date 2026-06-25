"""Small AGM governance engine for the artifact prototype.

The module intentionally stays local and file-based: YAML manifests in, YAML
evidence packages in, JSON/Markdown review packets out.
"""

from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
AGM_DIR = ROOT / ".agm"
RISK_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
REQUIRED_PACKAGE_KEYS = [
    "schema_version",
    "contribution_id",
    "changed_files",
    "summary",
    "rationale",
    "risk_zone_assessment",
    "evidence_index",
    "tests_run",
    "artifacts",
    "known_limitations",
    "human_review_declaration",
    "generated_at",
]
PLACEHOLDER_TERMS = [
    "todo",
    "tbd",
    "placeholder",
    "lorem ipsum",
    "fill me",
    "to be filled",
    "not provided",
]
PLACEHOLDER_EXACT = {"", "n/a", "na", "none yet", "unknown"}
HUMAN_REVIEW_STATUSES = {
    "not_required",
    "pending_human_review",
    "human_reviewed",
    "maintainer_review_required",
}
GOVERNANCE_ENTRYPOINT_PATTERNS = [
    ".agm/**",
    "AGENTS.md",
    "CLAUDE.md",
    "skills/**",
]


class AGMError(ValueError):
    """Raised when AGM configuration or evidence package input is malformed."""


@dataclass(frozen=True)
class GovernanceConfig:
    root: Path
    manifest: dict[str, Any]
    risk_zones: dict[str, Any]
    evidence_requirements: dict[str, Any]


def normalize_path(path: str | Path) -> str:
    normalized = str(path).replace("\\", "/")
    if normalized.startswith("./"):
        return normalized[2:]
    return normalized


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AGMError(f"Required AGM file not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise AGMError(f"Malformed YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AGMError(f"Expected a YAML mapping in {path}")
    return data


def load_governance_config(root: Path = ROOT) -> GovernanceConfig:
    manifest_path = root / ".agm" / "manifest.yml"
    manifest = load_yaml(manifest_path)

    for key in [
        "schema_version",
        "project",
        "governance_scope",
        "risk_zone_reference",
        "evidence_requirement_reference",
        "human_review_policy",
        "final_decision_authority",
    ]:
        if key not in manifest:
            raise AGMError(f"Malformed manifest: missing required key '{key}'")

    risk_path = root / normalize_path(manifest["risk_zone_reference"])
    evidence_path = root / normalize_path(manifest["evidence_requirement_reference"])
    risk_zones = load_yaml(risk_path)
    evidence_requirements = load_yaml(evidence_path)

    if "risk_zones" not in risk_zones or not isinstance(risk_zones["risk_zones"], list):
        raise AGMError("Malformed risk_zones.yml: expected 'risk_zones' list")
    if "requirements" not in evidence_requirements or not isinstance(evidence_requirements["requirements"], dict):
        raise AGMError("Malformed evidence_requirements.yml: expected 'requirements' mapping")

    return GovernanceConfig(
        root=root,
        manifest=manifest,
        risk_zones=risk_zones,
        evidence_requirements=evidence_requirements,
    )


def path_matches(pattern: str, path: str) -> bool:
    normalized_pattern = normalize_path(pattern)
    normalized_path = normalize_path(path)
    return fnmatch.fnmatch(normalized_path, normalized_pattern)


def classify_changed_files(changed_files: list[str], config: GovernanceConfig | None = None) -> dict[str, Any]:
    config = config or load_governance_config()
    if not changed_files:
        raise AGMError("Cannot classify an empty changed_files list")

    default_risk = config.risk_zones.get("default_risk_level", "high")
    if default_risk not in RISK_RANK:
        raise AGMError(f"Unknown default risk level: {default_risk}")

    detected = []
    highest = "low"
    normalized_files = [normalize_path(path) for path in changed_files]

    for changed_file in normalized_files:
        matched_any = False
        for zone in config.risk_zones["risk_zones"]:
            zone_id = zone.get("risk_zone_id") or zone.get("id")
            level = zone.get("risk_level") or zone.get("level")
            patterns = zone.get("path_patterns") or zone.get("patterns", [])
            if not zone_id or level not in RISK_RANK or not isinstance(patterns, list):
                raise AGMError(f"Malformed risk zone entry: {zone}")
            if any(path_matches(pattern, changed_file) for pattern in patterns):
                matched_any = True
                detected.append(
                    {
                        "file": changed_file,
                        "zone": zone_id,
                        "risk_level": level,
                        "reason": "matched path pattern",
                    }
                )
                if RISK_RANK[level] > RISK_RANK[highest]:
                    highest = level
        if not matched_any:
            detected.append(
                {
                    "file": changed_file,
                    "zone": "unclassified_path",
                    "risk_level": default_risk,
                    "reason": "no explicit risk-zone pattern matched; conservative default applied",
                }
            )
            if RISK_RANK[default_risk] > RISK_RANK[highest]:
                highest = default_risk

    requirements = config.evidence_requirements["requirements"].get(highest)
    if not requirements:
        raise AGMError(f"No evidence requirements configured for risk level '{highest}'")

    return {
        "changed_files": normalized_files,
        "detected_risk_zones": detected,
        "risk_level": highest,
        "governance_entrypoint_changes": governance_entrypoint_changes(normalized_files),
        "required_fields": requirements.get("required_evidence_package_fields") or requirements.get("required_fields", []),
        "required_evidence": requirements.get("required_evidence_items") or requirements.get("required_evidence", []),
    }


def governance_entrypoint_changes(changed_files: list[str]) -> list[str]:
    return sorted(
        {
            normalize_path(path)
            for path in changed_files
            if any(path_matches(pattern, normalize_path(path)) for pattern in GOVERNANCE_ENTRYPOINT_PATTERNS)
        }
    )


def value_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return " ".join(value_text(item) for item in value).strip()
    if isinstance(value, dict):
        return " ".join(f"{key} {value_text(item)}" for key, item in value.items()).strip()
    return str(value).strip()


def is_placeholder(value: Any) -> bool:
    text = value_text(value)
    lowered = text.lower().strip()
    if lowered in PLACEHOLDER_EXACT:
        return True
    if lowered.startswith("todo") or lowered.startswith("tbd"):
        return True
    if any(term in lowered for term in PLACEHOLDER_TERMS):
        return True
    if lowered in {"tests passed", "test passed"}:
        return True
    return False


def load_evidence_package(path: Path) -> dict[str, Any]:
    package = load_yaml(path)
    if "schema_version" not in package:
        raise AGMError(f"Malformed evidence package {path}: missing schema_version")
    if "changed_files" not in package or not isinstance(package["changed_files"], list):
        raise AGMError(f"Malformed evidence package {path}: changed_files must be a list")
    return package


def artifact_path(artifact: Any) -> str | None:
    if isinstance(artifact, str):
        return artifact
    if isinstance(artifact, dict):
        raw = artifact.get("path") or artifact.get("file")
        return str(raw) if raw else None
    return None


def tests_have_command(tests_run: Any) -> bool:
    if isinstance(tests_run, list):
        return any(isinstance(item, dict) and not is_placeholder(item.get("command")) for item in tests_run)
    if isinstance(tests_run, dict):
        return not is_placeholder(tests_run.get("command"))
    return False


def tests_have_explanation(tests_run: Any) -> bool:
    if isinstance(tests_run, str):
        return not is_placeholder(tests_run)
    if isinstance(tests_run, list):
        return any(not is_placeholder(item) for item in tests_run)
    if isinstance(tests_run, dict):
        return not is_placeholder(tests_run)
    return False


def default_human_review_declaration(risk_level: str) -> dict[str, Any]:
    required = risk_level == "critical"
    return {
        "required": required,
        "status": "pending_human_review" if required else "not_required",
        "reviewer": None,
        "reviewed_at": None,
        "review_scope": None,
        "statement": "Human review is required before final acceptance."
        if required
        else "Human review declaration is not required for this risk level.",
    }


def normalize_human_review_declaration(raw: Any, risk_level: str) -> tuple[dict[str, Any], list[str]]:
    issues: list[str] = []
    if raw in (None, {}):
        declaration = default_human_review_declaration(risk_level)
        if risk_level == "critical":
            issues.append("human_review_declaration missing for critical risk")
        return declaration, issues
    if not isinstance(raw, dict):
        declaration = default_human_review_declaration(risk_level)
        issues.append("human_review_declaration must be a mapping")
        return declaration, issues

    status = value_text(raw.get("status")).lower()
    if status in {"declared", "confirmed"}:
        status = "human_reviewed"
    if status not in HUMAN_REVIEW_STATUSES:
        issues.append(f"unsupported human_review_declaration status: {status or 'missing'}")
        status = "pending_human_review" if risk_level in {"high", "critical"} else "not_required"

    required = raw.get("required")
    if required is None:
        required = risk_level == "critical"

    declaration = {
        "required": bool(required),
        "status": status,
        "reviewer": raw.get("reviewer") or raw.get("reviewer_role"),
        "reviewed_at": raw.get("reviewed_at"),
        "review_scope": raw.get("review_scope"),
        "statement": raw.get("statement"),
    }

    if declaration["status"] == "human_reviewed":
        if is_placeholder(declaration["reviewer"]):
            issues.append("human_review_declaration reviewer is required for human_reviewed")
        if is_placeholder(declaration["reviewed_at"]):
            issues.append("human_review_declaration reviewed_at is required for human_reviewed")
        if not isinstance(declaration["review_scope"], list) or not declaration["review_scope"]:
            issues.append("human_review_declaration review_scope is required for human_reviewed")
        if is_placeholder(declaration["statement"]):
            issues.append("human_review_declaration statement is required for human_reviewed")
    elif declaration["status"] in {"pending_human_review", "maintainer_review_required"}:
        if is_placeholder(declaration["statement"]):
            declaration["statement"] = "Human review is required before final acceptance."

    return declaration, issues


def validate_evidence_package(
    package_path: Path,
    config: GovernanceConfig | None = None,
) -> dict[str, Any]:
    config = config or load_governance_config()
    package = load_evidence_package(package_path)
    classification = classify_changed_files([str(path) for path in package["changed_files"]], config)
    risk_level = classification["risk_level"]
    requirement = config.evidence_requirements["requirements"][risk_level]
    required_fields = list(requirement.get("required_fields", []))

    missing = []
    placeholders = []
    incomplete = []
    field_results = []

    for key in REQUIRED_PACKAGE_KEYS:
        if key not in package:
            incomplete.append(f"schema key missing: {key}")

    for field in required_fields:
        value = package.get(field)
        if field not in package or value is None or value_text(value) == "":
            missing.append(field)
            status = "Missing"
            observed = "Missing"
        elif is_placeholder(value):
            placeholders.append(field)
            status = "Placeholder"
            observed = value_text(value)
        else:
            status = "Pass"
            observed = compact_observed(value)
        field_results.append(
            {
                "field": field,
                "reference": requirement.get("field_reference", {}).get(field, "Required evidence must be provided"),
                "observed": observed,
                "status": status,
            }
        )

    tests_run = package.get("tests_run")
    if "tests_run" in required_fields:
        if risk_level in {"high", "critical"} and not tests_have_command(tests_run):
            incomplete.append("tests_run must include a concrete test command for high/critical risk")
        if not tests_have_explanation(tests_run):
            missing.append("tests_run")

    artifacts = package.get("artifacts", [])
    artifact_checks = []
    if "artifacts" in required_fields:
        if not isinstance(artifacts, list) or not artifacts:
            missing.append("artifacts")
        else:
            for artifact in artifacts:
                raw_path = artifact_path(artifact)
                if not raw_path:
                    incomplete.append("artifact entry missing path")
                    artifact_checks.append({"path": "Missing", "exists": False})
                    continue
                resolved = config.root / normalize_path(raw_path)
                exists = resolved.exists()
                artifact_checks.append({"path": normalize_path(raw_path), "exists": exists})
                if not exists:
                    incomplete.append(f"referenced artifact does not exist: {normalize_path(raw_path)}")

    declared_level = None
    assessment = package.get("risk_zone_assessment")
    if isinstance(assessment, dict):
        declared_level = assessment.get("declared_risk_level")
    if declared_level and declared_level != risk_level:
        placeholders.append(
            f"risk_zone_assessment declared {declared_level} but changed files classify as {risk_level}"
        )

    human_declaration, human_review_issues = normalize_human_review_declaration(
        package.get("human_review_declaration"), risk_level
    )
    human_review_status = human_declaration["status"]
    if human_review_issues:
        incomplete.extend(human_review_issues)
    if risk_level == "critical" and human_review_status != "human_reviewed":
        incomplete.append("critical risk requires human_reviewed declaration before final acceptance readiness")
    if risk_level == "high" and human_declaration["required"] and human_review_status != "human_reviewed":
        incomplete.append("high risk human review declaration remains pending")

    for row in field_results:
        if row["field"] == "human_review_declaration":
            row["observed"] = human_review_status
            if risk_level == "critical" and human_review_status != "human_reviewed":
                row["status"] = "Blocked"
            elif human_review_issues:
                row["status"] = "Needs evidence"
            else:
                row["status"] = "Pass"

    evidence_status = "complete"
    if missing:
        evidence_status = "missing"
    if incomplete and evidence_status == "complete":
        evidence_status = "incomplete"
    if placeholders:
        evidence_status = "placeholder"

    if placeholders or (risk_level == "critical" and human_review_status != "human_reviewed"):
        gate_status = "blocked"
    elif missing or incomplete:
        gate_status = "needs_evidence"
    else:
        gate_status = "pass"

    technical_readiness = {
        "pass": "ready",
        "needs_evidence": "limited",
        "blocked": "not_ready",
    }[gate_status]
    final_readiness = {
        "pass": "eligible_for_human_decision",
        "needs_evidence": "not_eligible_missing_evidence",
        "blocked": "blocked_by_policy",
    }[gate_status]

    gate_state = {
        "risk_level": risk_level,
        "evidence_status": evidence_status,
        "human_review_status": human_review_status,
        "governance_gate_status": gate_status,
        "technical_review_readiness": technical_readiness,
        "final_acceptance_readiness": final_readiness,
    }

    return {
        "valid": gate_status == "pass",
        "package_path": normalize_path(package_path),
        "contribution_id": package.get("contribution_id"),
        "changed_files": classification["changed_files"],
        "detected_risk_zones": classification["detected_risk_zones"],
        "governance_entrypoint_changes": classification["governance_entrypoint_changes"],
        "risk_level": risk_level,
        "required_fields": required_fields,
        "required_evidence": requirement.get("required_evidence", []),
        "field_results": field_results,
        "missing_evidence": sorted(set(missing)),
        "placeholder_warnings": sorted(set(placeholders)),
        "incomplete_evidence": sorted(set(incomplete)),
        "artifact_checks": artifact_checks,
        "human_review_declaration": human_declaration,
        "gate_state": gate_state,
        "final_decision_authority": config.manifest["final_decision_authority"],
    }


def placeholder_for(field: str) -> str:
    return f"TODO: provide {field.replace('_', ' ')}."


def build_contribution_evidence_package(
    *,
    contribution_id: str,
    changed_files: list[str],
    summary: str,
    rationale: str = "",
    tests_run: list[dict[str, str]] | None = None,
    artifacts: list[dict[str, str]] | None = None,
    known_limitations: str = "",
    security_auth_impact_statement: str = "",
    human_review_declaration: dict[str, str] | None = None,
    generated_at: str | None = None,
    config: GovernanceConfig | None = None,
) -> dict[str, Any]:
    """Simulate a contribution-side agent reading AGM and drafting evidence.

    This is intentionally deterministic: it uses the AGM files and supplied
    contribution facts, not model calls, network services, or platform APIs.
    Missing required facts are represented as placeholders so validation can
    block incomplete packages instead of silently passing them.
    """
    config = config or load_governance_config()
    classification = classify_changed_files(changed_files, config)
    risk_level = classification["risk_level"]
    zones = sorted({item["zone"] for item in classification["detected_risk_zones"]})
    required_fields = set(classification["required_fields"])

    package: dict[str, Any] = {
        "schema_version": "agm.evidence_package/v0.1",
        "contribution_id": contribution_id,
        "changed_files": classification["changed_files"],
        "summary": summary or placeholder_for("summary"),
        "rationale": rationale or (placeholder_for("rationale") if "rationale" in required_fields else ""),
        "risk_zone_assessment": {
            "declared_risk_level": risk_level,
            "declared_risk_zones": zones,
            "agent_read_agm_files": [
                ".agm/manifest.yml",
                normalize_path(config.manifest["risk_zone_reference"]),
                normalize_path(config.manifest["evidence_requirement_reference"]),
            ],
            "required_evidence": classification["required_evidence"],
        },
        "evidence_index": [],
        "tests_run": tests_run if tests_run is not None else ([] if "tests_run" not in required_fields else placeholder_for("tests_run")),
        "artifacts": artifacts if artifacts is not None else ([] if "artifacts" not in required_fields else []),
        "known_limitations": known_limitations
        or (placeholder_for("known_limitations") if "known_limitations" in required_fields else ""),
        "human_review_declaration": human_review_declaration or {},
        "generated_at": generated_at or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }

    if "security_auth_impact_statement" in required_fields:
        package["security_auth_impact_statement"] = security_auth_impact_statement or placeholder_for(
            "security_auth_impact_statement"
        )
    if artifacts:
        package["evidence_index"] = [
            {
                "label": artifact.get("description", "artifact"),
                "path": artifact.get("path", ""),
            }
            for artifact in artifacts
        ]
    if risk_level == "critical" and not package["human_review_declaration"]:
        package["human_review_declaration"] = {
            "required": True,
            "status": "pending_human_review",
            "reviewer": None,
            "reviewed_at": None,
            "review_scope": None,
            "statement": "Human review is required before final acceptance.",
        }
    return package


def mark_human_review(
    package_path: Path,
    *,
    reviewer: str,
    scopes: list[str],
    statement: str,
    reviewed_at: str | None = None,
) -> Path:
    package = load_evidence_package(package_path)
    if not reviewer.strip():
        raise AGMError("reviewer is required")
    if not scopes:
        raise AGMError("at least one review scope is required")
    if not statement.strip():
        raise AGMError("statement is required")
    package["human_review_declaration"] = {
        "required": True,
        "status": "human_reviewed",
        "reviewer": reviewer,
        "reviewed_at": reviewed_at
        or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "review_scope": scopes,
        "statement": statement,
    }
    return write_evidence_package(package, package_path)


def write_evidence_package(package: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(package, sort_keys=False), encoding="utf-8")
    return output_path


def compact_observed(value: Any) -> str:
    text = value_text(value)
    if len(text) > 100:
        return text[:97] + "..."
    return text


def status_from_issue(pass_condition: bool, blocked: bool = False) -> str:
    if pass_condition:
        return "Pass"
    return "Blocked" if blocked else "Needs evidence"


def governance_table(validation: dict[str, Any]) -> list[dict[str, str]]:
    zones = sorted({item["zone"] for item in validation["detected_risk_zones"]})
    required_tests = "Tests run with command/artifact" if validation["risk_level"] in {"high", "critical"} else "Tests run or explanation"
    has_missing_artifact = any(not item["exists"] for item in validation["artifact_checks"])
    human_status = validation["gate_state"]["human_review_status"]
    entrypoint_changes = validation["governance_entrypoint_changes"]
    if validation["risk_level"] == "critical":
        human_reference = "Required and must be human_reviewed for critical risk"
        human_blocked = human_status != "human_reviewed"
    elif validation["risk_level"] == "high":
        human_reference = "Optional; pending_human_review lowers readiness if required"
        human_blocked = False
    else:
        human_reference = "Not required unless project policy says otherwise"
        human_blocked = False

    rows = [
        {
            "indicator": "AGM reference source",
            "reference": "Base branch .agm/manifest.yml",
            "observed": "Used current repository .agm/manifest.yml",
            "status": "Pass",
        },
        {
            "indicator": "Governance entrypoint change",
            "reference": "Must be reviewed if changed",
            "observed": ", ".join(entrypoint_changes) if entrypoint_changes else "None detected",
            "status": "Needs maintainer attention" if entrypoint_changes else "Pass",
        },
        {
            "indicator": "Risk-zone classification",
            "reference": "Must identify affected risk zone",
            "observed": ", ".join(zones),
            "status": "Pass",
        },
        {
            "indicator": "Required tests",
            "reference": required_tests,
            "observed": "Missing command or artifact" if has_missing_artifact else "Provided",
            "status": status_from_issue(not has_missing_artifact and "tests_run" not in validation["missing_evidence"]),
        },
        {
            "indicator": "Human review declaration",
            "reference": human_reference,
            "observed": human_status,
            "status": status_from_issue(not human_blocked, blocked=human_blocked),
        },
        {
            "indicator": "Placeholder evidence",
            "reference": "Must be absent",
            "observed": "; ".join(validation["placeholder_warnings"]) if validation["placeholder_warnings"] else "Absent",
            "status": status_from_issue(not validation["placeholder_warnings"], blocked=bool(validation["placeholder_warnings"])),
        },
        {
            "indicator": "Final decision authority",
            "reference": "Human maintainer",
            "observed": "Human decision required",
            "status": "Pass",
        },
    ]
    return rows


def reviewer_attention_points(validation: dict[str, Any]) -> list[str]:
    points = []
    if validation["risk_level"] == "critical":
        points.append("Inspect auth/security behavior and confirm the human review declaration before final decision.")
    if validation["missing_evidence"]:
        points.append("Request missing required evidence before treating the contribution as review-ready.")
    if validation["placeholder_warnings"]:
        points.append("Replace placeholder or inconsistent evidence with factual, checkable evidence.")
    if validation["incomplete_evidence"]:
        if validation["gate_state"]["human_review_status"] == "pending_human_review":
            points.append("Human review remains pending; do not treat the contribution as final-acceptance ready.")
        if any("artifact" in item or "test" in item for item in validation["incomplete_evidence"]):
            points.append("Resolve incomplete test or artifact evidence before treating the package as review-ready.")
    return points or ["No additional AGM attention points beyond normal technical review."]


def generate_review_packet(
    package_path: Path,
    output_dir: Path,
    config: GovernanceConfig | None = None,
) -> dict[str, Path]:
    config = config or load_governance_config()
    validation = validate_evidence_package(package_path, config)
    package = load_evidence_package(package_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    table = governance_table(validation)
    packet = {
        "contribution_id": validation["contribution_id"],
        "summary": package.get("summary"),
        "changed_files": validation["changed_files"],
        "detected_risk_zones": validation["detected_risk_zones"],
        "governance_entrypoint_changes": validation["governance_entrypoint_changes"],
        "required_evidence": validation["required_evidence"],
        "provided_evidence": [row["field"] for row in validation["field_results"] if row["status"] == "Pass"],
        "missing_evidence": validation["missing_evidence"],
        "placeholder_warnings": validation["placeholder_warnings"],
        "human_review_declaration_status": validation["gate_state"]["human_review_status"],
        "governance_gate_status": validation["gate_state"]["governance_gate_status"],
        "technical_review_readiness": validation["gate_state"]["technical_review_readiness"],
        "final_acceptance_readiness": validation["gate_state"]["final_acceptance_readiness"],
        "governance_indicators": table,
        "reviewer_attention_points": reviewer_attention_points(validation),
        "final_decision_authority": config.manifest["final_decision_authority"],
    }

    json_path = output_dir / "review_packet.json"
    md_path = output_dir / "review_packet.md"
    json_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_review_packet_markdown(packet), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


def render_review_packet_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# AGM Review Packet",
        "",
        "## Contribution Summary",
        "",
        str(packet["summary"]),
        "",
        "## Changed Files",
        "",
        *[f"- {path}" for path in packet["changed_files"]],
        "",
        "## Detected Risk Zones",
        "",
        *[
            f"- {item['file']}: {item['zone']} ({item['risk_level']})"
            for item in packet["detected_risk_zones"]
        ],
        "",
        "## Governance Entrypoint Changes",
        "",
        *([f"- {path}" for path in packet["governance_entrypoint_changes"]] or ["- none"]),
        "",
        "## Governance Indicators",
        "",
        "| Governance Indicator | Reference / Required Value | Observed / Provided Value | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in packet["governance_indicators"]:
        lines.append(f"| {row['indicator']} | {row['reference']} | {row['observed']} | {row['status']} |")

    lines.extend(
        [
            "",
            "## Required Evidence Checklist",
            "",
            *[f"- {item}" for item in packet["required_evidence"]],
            "",
            "## Provided Evidence Checklist",
            "",
            *([f"- {item}" for item in packet["provided_evidence"]] or ["- none"]),
            "",
            "## Missing Evidence",
            "",
            *([f"- {item}" for item in packet["missing_evidence"]] or ["- none"]),
            "",
            "## Placeholder Warnings",
            "",
            *([f"- {item}" for item in packet["placeholder_warnings"]] or ["- none"]),
            "",
            "## Gate State",
            "",
            f"- human_review_declaration_status: {packet['human_review_declaration_status']}",
            f"- governance_gate_status: {packet['governance_gate_status']}",
            f"- technical_review_readiness: {packet['technical_review_readiness']}",
            f"- final_acceptance_readiness: {packet['final_acceptance_readiness']}",
            "",
            "## Reviewer Attention Points",
            "",
            *[f"- {point}" for point in packet["reviewer_attention_points"]],
            "",
            "## Final Decision Authority",
            "",
            packet["final_decision_authority"],
            "",
            "AGM reports governance readiness only. Final acceptance remains with human maintainers.",
            "",
        ]
    )
    return "\n".join(lines)
