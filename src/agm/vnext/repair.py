"""First-class findings, repair requests, and resubmission attempts."""

from __future__ import annotations

from typing import Any

from .models import (
    GovernanceCase,
    GovernanceFinding,
    RepairRequest,
    VNextError,
    new_id,
    utc_now,
)


def create_finding(
    case: GovernanceCase,
    *,
    code: str,
    severity: str,
    message: str,
    blocking: bool,
    related_object_ids: list[str] | None = None,
    affected_obligation_ids: list[str] | None = None,
    created_at: str | None = None,
) -> GovernanceFinding:
    if not code.strip() or not message.strip():
        raise VNextError("Finding code and message are required")
    known_obligations = {item.obligation_id for item in case.obligations}
    affected = list(dict.fromkeys(affected_obligation_ids or []))
    unknown = sorted(set(affected) - known_obligations)
    if unknown:
        raise VNextError(f"Finding references unknown obligations: {', '.join(unknown)}")
    finding = GovernanceFinding(
        id=new_id("finding"),
        code=code,
        severity=severity,
        message=message,
        blocking=blocking,
        related_object_ids=list(related_object_ids or []),
        affected_obligation_ids=affected,
        created_at=created_at or utc_now(),
    )
    case.findings.append(finding)
    return finding


def create_repair_request(
    case: GovernanceCase,
    *,
    finding_ids: list[str],
    responsible_role: str,
    requested_correction: str,
    requested_by: str,
    affected_obligation_ids: list[str] | None = None,
    revalidation_required: list[str] | None = None,
    requested_at: str | None = None,
) -> RepairRequest:
    if not finding_ids:
        raise VNextError("Repair request requires at least one finding")
    known_findings = {item.id for item in case.findings}
    unknown_findings = sorted(set(finding_ids) - known_findings)
    if unknown_findings:
        raise VNextError(
            f"Repair request references unknown findings: {', '.join(unknown_findings)}"
        )
    if not requested_correction.strip():
        raise VNextError("Repair request requires a requested correction")
    inferred_obligations = sorted(
        {
            obligation_id
            for item in case.findings
            if item.id in finding_ids
            for obligation_id in item.affected_obligation_ids
        }
    )
    repair = RepairRequest(
        id=new_id("repair"),
        finding_ids=list(dict.fromkeys(finding_ids)),
        responsible_role=responsible_role,
        affected_obligation_ids=list(
            dict.fromkeys(affected_obligation_ids or inferred_obligations)
        ),
        requested_correction=requested_correction,
        revalidation_required=list(
            dict.fromkeys(revalidation_required or inferred_obligations)
        ),
        requested_by=requested_by,
        requested_at=requested_at or utc_now(),
    )
    case.repair_requests.append(repair)
    return repair


def record_resubmission(
    case: GovernanceCase,
    *,
    actor: str,
    summary: str,
    affected_obligation_ids: list[str],
    evidence_ids: list[str] | None = None,
    change_assessment: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    if not summary.strip():
        raise VNextError("Resubmission requires a summary")
    open_repairs = [item for item in case.repair_requests if item.status == "open"]
    if not open_repairs:
        raise VNextError("Case has no open repair request to resubmit")
    attempt = {
        "id": new_id("attempt"),
        "actor": actor,
        "timestamp": timestamp or utc_now(),
        "summary": summary,
        "affected_obligation_ids": list(dict.fromkeys(affected_obligation_ids)),
        "evidence_ids": list(dict.fromkeys(evidence_ids or [])),
    }
    if change_assessment:
        attempt["change_assessment"] = dict(change_assessment)
        attempt.update(
            {
                key: value
                for key, value in change_assessment.items()
                if key
                in {
                    "change_classification",
                    "change_reason",
                    "previous_contribution_fingerprint",
                    "new_contribution_fingerprint",
                    "stale_evidence_ids",
                    "retained_evidence_ids",
                    "invalidated_attestation_ids",
                    "required_revalidation_scope",
                }
            }
        )
    for repair in open_repairs:
        if set(repair.affected_obligation_ids) & set(affected_obligation_ids):
            repair.attempts.append(attempt)
            repair.status = "resubmitted"
    return attempt


def resolve_finding(
    case: GovernanceCase,
    *,
    finding_id: str,
    resolution: str,
    timestamp: str | None = None,
) -> GovernanceFinding:
    if not resolution.strip():
        raise VNextError("Finding resolution is required")
    for finding in case.findings:
        if finding.id == finding_id:
            finding.status = "resolved"
            finding.resolution = resolution
            finding.resolved_at = timestamp or utc_now()
            return finding
    raise VNextError(f"Unknown finding: {finding_id}")
