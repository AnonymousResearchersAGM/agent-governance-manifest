"""Case-bound selector options for maintainer-facing actions."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

from ..models import GovernanceCase, VNextError, canonical_json
from ..runtime import selector_token_secret
from .diagnostics import build_requirement_comparisons
from .models import ContextSelectorOption, RequirementComparison, TraceReference


SELECTOR_ACTIONS = {
    "verify_evidence",
    "reject_evidence",
    "request_repair",
    "ask_clarification",
    "invalidate_attestation",
    "record_policy_conflict",
    "resolve_policy_conflict",
    "resubmit",
    "authorized_override",
}


def _token(
    case: GovernanceCase,
    action: str,
    object_type: str,
    object_ids: list[str],
    obligation_ids: list[str],
) -> str:
    material = canonical_json(
        {
            "case_id": case.id,
            "contribution_fingerprint": case.contribution_fingerprint,
            "action": action,
            "object_type": object_type,
            "object_ids": sorted(object_ids),
            "obligation_ids": sorted(obligation_ids),
        }
    ).encode("utf-8")
    return "sel-" + hmac.new(
        selector_token_secret(),
        material,
        hashlib.sha256,
    ).hexdigest()


def _option(
    case: GovernanceCase,
    *,
    action: str,
    label: str,
    status_label: str,
    affected_scope: list[str],
    obligation_ids: list[str],
    object_type: str,
    object_ids: list[str],
    blocking: bool,
    material_status: str = "",
    workflow_status: str = "",
    technical_details: dict[str, Any] | None = None,
    traces: list[TraceReference] | None = None,
) -> ContextSelectorOption:
    return ContextSelectorOption(
        selector_token=_token(
            case, action, object_type, object_ids, obligation_ids
        ),
        action=action,
        label=label,
        status_label=status_label,
        affected_scope=list(affected_scope),
        obligation_ids=list(obligation_ids),
        object_type=object_type,
        object_ids=list(object_ids),
        blocking=blocking,
        material_status=material_status,
        workflow_status=workflow_status,
        technical_details=dict(technical_details or {}),
        traceability=list(traces or []),
    )


def _comparison_options(
    case: GovernanceCase,
    action: str,
    comparisons: list[RequirementComparison],
    *,
    predicate,
) -> list[ContextSelectorOption]:
    result = []
    for row in comparisons:
        if not predicate(row):
            continue
        result.append(
            _option(
                case,
                action=action,
                label=row.display_name,
                status_label=(
                    f"{row.material_status_label}；"
                    f"{row.workflow_status_label}"
                ),
                affected_scope=row.affected_scope,
                obligation_ids=[row.obligation_id],
                object_type="obligation",
                object_ids=[row.obligation_id],
                blocking=row.blocking_requirement,
                material_status=row.material_status,
                workflow_status=row.workflow_status,
                technical_details={
                    "obligation_id": row.obligation_id,
                    "evidence_ids": row.evidence_ids,
                    "finding_ids": row.finding_ids,
                },
                traces=row.traceability,
            )
        )
    return result


def build_context_selector_options(
    case: GovernanceCase,
    action: str,
    comparisons: list[RequirementComparison] | None = None,
) -> list[ContextSelectorOption]:
    """Return only action-appropriate objects from the current case."""
    rows = comparisons or build_requirement_comparisons(case)
    by_obligation = {item.obligation_id: item for item in rows}
    if action == "verify_evidence":
        repair_scope = {
            obligation_id
            for repair in case.repair_requests
            if repair.status == "resubmitted"
            for obligation_id in repair.revalidation_required
        }
        return _comparison_options(
            case,
            action,
            rows,
            predicate=lambda row: (
                (
                    row.obligation_id == "O-INDEPENDENT-REVIEW"
                    or row.material_status
                    in {"provided", "retained", "verified", "overridden"}
                )
                and (
                    not repair_scope
                    or row.obligation_id in repair_scope
                )
                and (
                    row.obligation_id == "O-INDEPENDENT-REVIEW"
                    or row.raw_status
                    in {"satisfied", "verified", "overridden"}
                )
            ),
        )
    if action == "reject_evidence":
        result = []
        for evidence in case.evidence:
            if evidence.validity_state not in {"valid", "verified"}:
                continue
            obligation_ids = list(evidence.obligation_ids)
            labels = [
                by_obligation[item].display_name
                for item in obligation_ids
                if item in by_obligation
            ]
            result.append(
                _option(
                    case,
                    action=action,
                    label="、".join(labels) or "当前材料",
                    status_label="当前材料有效，可记录拒绝依据",
                    affected_scope=evidence.affected_scope,
                    obligation_ids=obligation_ids,
                    object_type="evidence",
                    object_ids=[evidence.id],
                    blocking=any(
                        by_obligation[item].blocking_requirement
                        for item in obligation_ids
                        if item in by_obligation
                    ),
                    material_status=evidence.validity_state,
                    technical_details={
                        "evidence_id": evidence.id,
                        "evidence_type": evidence.evidence_type,
                    },
                    traces=[
                        TraceReference(
                            "evidence", evidence.id, "action_target"
                        )
                    ],
                )
            )
        return result
    if action in {
        "request_repair",
        "ask_clarification",
        "record_policy_conflict",
    }:
        return _comparison_options(
            case,
            action,
            rows,
            predicate=lambda row: row.result not in {
                "not_applicable",
                "closed",
            },
        )
    if action == "invalidate_attestation":
        result = []
        row = by_obligation.get("O-HUMAN-ATTEST")
        for attestation in case.attestations:
            if attestation.status != "confirmed":
                continue
            result.append(
                _option(
                    case,
                    action=action,
                    label="负责人对当前范围的确认",
                    status_label="当前确认有效",
                    affected_scope=attestation.reviewed_scope,
                    obligation_ids=["O-HUMAN-ATTEST"],
                    object_type="human_attestation",
                    object_ids=[attestation.id],
                    blocking=bool(row and row.blocking_requirement),
                    material_status="provided",
                    technical_details={
                        "attestation_id": attestation.id,
                        "actor": attestation.actor,
                        "timestamp": attestation.timestamp,
                    },
                    traces=[
                        TraceReference(
                            "human_attestation",
                            attestation.id,
                            "action_target",
                        )
                    ],
                )
            )
        return result
    if action == "resolve_policy_conflict":
        result = []
        for finding in case.findings:
            if finding.code != "policy_conflict" or finding.status != "open":
                continue
            labels = [
                by_obligation[item].display_name
                for item in finding.affected_obligation_ids
                if item in by_obligation
            ]
            result.append(
                _option(
                    case,
                    action=action,
                    label="、".join(labels) or "项目规则冲突",
                    status_label="等待有权角色解决",
                    affected_scope=sorted(
                        {
                            path
                            for item in finding.affected_obligation_ids
                            if item in by_obligation
                            for path in by_obligation[item].affected_scope
                        }
                    ),
                    obligation_ids=finding.affected_obligation_ids,
                    object_type="finding",
                    object_ids=[finding.id],
                    blocking=finding.blocking,
                    material_status="invalid",
                    workflow_status="blocks_progression",
                    technical_details={
                        "finding_id": finding.id,
                        "finding_code": finding.code,
                    },
                    traces=[
                        TraceReference(
                            "finding", finding.id, "action_target"
                        )
                    ],
                )
            )
        return result
    if action == "resubmit":
        result = []
        for repair in case.repair_requests:
            if repair.status != "open":
                continue
            labels = [
                by_obligation[item].display_name
                for item in repair.affected_obligation_ids
                if item in by_obligation
            ]
            result.append(
                _option(
                    case,
                    action=action,
                    label="补交：" + ("、".join(labels) or "指定修复范围"),
                    status_label="等待贡献侧补交",
                    affected_scope=sorted(
                        {
                            path
                            for item in repair.affected_obligation_ids
                            if item in by_obligation
                            for path in by_obligation[item].affected_scope
                        }
                    ),
                    obligation_ids=repair.affected_obligation_ids,
                    object_type="repair_request",
                    object_ids=[repair.id],
                    blocking=True,
                    workflow_status="awaiting_contributor",
                    technical_details={
                        "repair_request_id": repair.id,
                        "finding_ids": repair.finding_ids,
                    },
                    traces=[
                        TraceReference(
                            "repair_request", repair.id, "action_target"
                        )
                    ],
                )
            )
        return result
    if action == "authorized_override":
        result = _comparison_options(
            case,
            action,
            rows,
            predicate=lambda row: row.blocking_requirement
            and row.raw_status
            not in {"satisfied", "verified", "overridden"},
        )
        for finding in case.findings:
            if finding.status != "open":
                continue
            labels = [
                by_obligation[item].display_name
                for item in finding.affected_obligation_ids
                if item in by_obligation
            ]
            result.append(
                _option(
                    case,
                    action=action,
                    label="覆盖 finding：" + (
                        "、".join(labels) or finding.code
                    ),
                    status_label="开放问题",
                    affected_scope=[],
                    obligation_ids=finding.affected_obligation_ids,
                    object_type="finding",
                    object_ids=[finding.id],
                    blocking=finding.blocking,
                    technical_details={
                        "finding_id": finding.id,
                        "finding_code": finding.code,
                    },
                    traces=[
                        TraceReference(
                            "finding", finding.id, "action_target"
                        )
                    ],
                )
            )
        return result
    return []


def resolve_selector_tokens(
    case: GovernanceCase,
    action: str,
    selector_tokens: list[str] | str,
    comparisons: list[RequirementComparison] | None = None,
) -> dict[str, list[str] | str]:
    """Resolve opaque tokens against the current case and action.

    Tokens are never trusted: valid choices are rebuilt from the current case,
    so a forged, stale, other-case, or wrong-action token is rejected.
    """
    raw = [selector_tokens] if isinstance(selector_tokens, str) else selector_tokens
    tokens = list(dict.fromkeys(item for item in raw if item))
    options = {
        item.selector_token: item
        for item in build_context_selector_options(
            case, action, comparisons
        )
    }
    unknown = [item for item in tokens if item not in options]
    if unknown:
        raise VNextError(
            "选择的对象不属于当前案例、操作或允许范围；请刷新页面后重新选择。"
        )
    selected = [options[item] for item in tokens]
    obligation_ids = list(
        dict.fromkeys(
            obligation_id
            for option in selected
            for obligation_id in option.obligation_ids
        )
    )
    object_ids = list(
        dict.fromkeys(
            object_id
            for option in selected
            for object_id in option.object_ids
        )
    )
    object_types = {option.object_type for option in selected}
    result: dict[str, list[str] | str] = {
        "obligation_ids": obligation_ids,
        "object_ids": object_ids,
    }
    if len(object_ids) == 1:
        result["object_id"] = object_ids[0]
    if object_types == {"finding"}:
        result["finding_ids"] = object_ids
    return result
