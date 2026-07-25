"""Contribution fingerprinting, policy snapshots, and intake semantics."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import VNextConfig, normalize_path, safe_project_path
from .models import PolicySnapshot, VNextError, fingerprint, new_id, utc_now
from .risk import RiskResolution


INTAKE_MODES = {
    "ordinary",
    "declared_agent_mediated",
    "policy_required",
    "maintainer_requested",
}


@dataclass(frozen=True)
class IntakeDecision:
    requested_mode: str
    effective_mode: str
    case_required: bool
    package_status: str
    reason: str


def repository_head(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise VNextError("Cannot determine repository base commit") from exc
    return result.stdout.strip()


def contribution_fingerprint(
    root: Path,
    changed_files: list[str],
    *,
    base_commit: str,
    change_tags: list[str] | None = None,
    semantic_targets: list[str] | None = None,
    diff_material: str | None = None,
) -> str:
    records: list[dict[str, Any]] = []
    for raw_path in sorted(set(normalize_path(item) for item in changed_files)):
        path = safe_project_path(root, raw_path)
        if path.is_file():
            content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            state = "file"
        elif path.exists():
            content_hash = None
            state = "non_file"
        else:
            content_hash = None
            state = "missing_or_deleted"
        records.append(
            {"path": raw_path, "state": state, "content_hash": content_hash}
        )
    payload = {
        "base_commit": base_commit,
        "files": records,
        "change_tags": sorted(set(change_tags or [])),
        "semantic_targets": sorted(set(semantic_targets or [])),
        "diff_material_hash": hashlib.sha256(
            (diff_material or "").encode("utf-8")
        ).hexdigest(),
    }
    return fingerprint(payload)


def decide_intake(requested_mode: str, resolution: RiskResolution) -> IntakeDecision:
    if requested_mode not in INTAKE_MODES:
        raise VNextError(f"Unknown contribution intake mode: {requested_mode}")
    if resolution.policy_required:
        return IntakeDecision(
            requested_mode=requested_mode,
            effective_mode="policy_required",
            case_required=True,
            package_status="agm_case_required",
            reason=(
                "Project policy requires a Governance Case for at least one matched "
                "change rule; this requirement is based on the change, not inferred authorship."
            ),
        )
    if requested_mode == "ordinary":
        return IntakeDecision(
            requested_mode=requested_mode,
            effective_mode="ordinary",
            case_required=False,
            package_status="no_agm_package_submitted",
            reason=(
                "No AGM package was submitted and no matched rule requires one. "
                "This does not confirm human authorship."
            ),
        )
    if requested_mode == "policy_required":
        return IntakeDecision(
            requested_mode=requested_mode,
            effective_mode="policy_required",
            case_required=True,
            package_status="agm_case_required",
            reason="The caller explicitly identified a policy-required case.",
        )
    return IntakeDecision(
        requested_mode=requested_mode,
        effective_mode=requested_mode,
        case_required=True,
        package_status="agm_case_opened",
        reason=(
            "Structured AGM preparation was explicitly declared or requested; no "
            "claim about contributor identity is inferred."
        ),
    )


def make_policy_snapshot(
    config: VNextConfig,
    *,
    base_commit: str,
    resolved_at: str | None = None,
) -> PolicySnapshot:
    return PolicySnapshot(
        id=new_id("policy"),
        schema_version="agm.policy_snapshot/v0.2-dev",
        manifest_version=str(config.manifest["schema_version"]),
        base_commit=base_commit,
        policy_fingerprint=config.policy_fingerprint,
        resolved_at=resolved_at or utc_now(),
        source_paths=list(config.source_paths),
    )
