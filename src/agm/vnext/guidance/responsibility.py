"""Derive the current handoff from complete governance diagnostics."""

from __future__ import annotations

from ..models import (
    GovernanceCase,
    GovernanceFinding,
    HumanAttestation,
    RepairRequest,
)
from .models import (
    ActorContext,
    RequirementComparison,
    ResponsibilityView,
)
from .term_presentations import present_role


def _label(roles: list[str]) -> str:
    return "、".join(
        present_role(item).display_plain for item in roles
    )


def _view(
    roles: list[str],
    reason: str,
    blocking_items: list[str],
    next_handoff_roles: list[str],
) -> ResponsibilityView:
    return ResponsibilityView(
        primary_roles=roles,
        display_label=_label(roles) if roles else "流程已结束",
        reason=reason,
        blocking_items=blocking_items,
        next_handoff_roles=next_handoff_roles,
    )


def derive_current_responsibility(
    case: GovernanceCase | None,
    requirement_comparisons: list[RequirementComparison],
    findings: list[GovernanceFinding] | None = None,
    repair_requests: list[RepairRequest] | None = None,
    attestations: list[HumanAttestation] | None = None,
    actor_context: ActorContext | None = None,
) -> ResponsibilityView:
    """Use material, workflow, repair and authority facts—not state alone."""
    del actor_context  # Responsibility is a case fact, not viewer-dependent.
    if case is None:
        return _view(
            ["maintainer"],
            "本次不要求完整 AGM 材料，最终项目决定仍由人类维护者按普通流程作出。",
            [],
            [],
        )
    findings = findings if findings is not None else case.findings
    repairs = (
        repair_requests
        if repair_requests is not None
        else case.repair_requests
    )
    attestations = (
        attestations if attestations is not None else case.attestations
    )
    if case.state in {"accepted", "rejected", "closed"}:
        return _view(
            [],
            "人类最终决定和关闭记录已经生成，当前没有待交接操作。",
            [],
            [],
        )

    conflicts = [
        item
        for item in findings
        if item.code == "policy_conflict" and item.status == "open"
    ]
    if conflicts or any(
        item.raw_status == "policy_conflict"
        for item in requirement_comparisons
    ):
        items = [
            row.display_name
            for row in requirement_comparisons
            if row.raw_status == "policy_conflict"
        ]
        return _view(
            ["policy_steward", "maintainer"],
            "项目规则之间存在未解决冲突，需要具备相应权限的人类角色先记录解决依据。",
            items,
            ["contributor", "maintainer_verifier"],
        )

    contribution_rows = [
        row
        for row in requirement_comparisons
        if row.blocking_requirement
        and row.material_status in {"missing", "stale", "invalid"}
        and row.workflow_status
        in {"awaiting_contributor", "blocks_progression"}
        and row.obligation_id
        not in {"O-HUMAN-ATTEST", "O-INDEPENDENT-REVIEW"}
    ]
    if contribution_rows:
        return _view(
            ["contributor", "contributor_agent"],
            "受影响材料尚未准备或更新完成，当前还不能进入维护者检查。",
            [row.display_name for row in contribution_rows],
            ["accountable_human", "maintainer_verifier", "maintainer"],
        )

    open_repairs = [
        item for item in repairs if item.status in {"open", "resubmitted"}
    ]
    open_repairs_waiting_contributor = [
        item for item in open_repairs if item.status == "open"
    ]
    if open_repairs_waiting_contributor:
        roles = sorted(
            {
                item.responsible_role
                for item in open_repairs_waiting_contributor
            }
        ) or ["contributor"]
        ids = {
            obligation_id
            for repair in open_repairs_waiting_contributor
            for obligation_id in repair.affected_obligation_ids
        }
        items = [
            row.display_name
            for row in requirement_comparisons
            if row.obligation_id in ids
        ]
        return _view(
            roles,
            "维护者已指定需要修改的范围，当前等待责任方补充或更正。",
            items,
            ["maintainer_verifier", "maintainer"],
        )

    attestation_rows = [
        row
        for row in requirement_comparisons
        if row.obligation_id == "O-HUMAN-ATTEST"
        and row.material_status in {"missing", "invalid", "stale"}
        and row.blocking_requirement
    ]
    invalidated = any(item.status == "invalidated" for item in attestations)
    if attestation_rows and (
        case.state == "awaiting_human_attestation" or invalidated
    ):
        return _view(
            ["accountable_human"],
            "材料范围已经明确，但负责人尚未确认当前版本，或旧确认已经失效。",
            [row.display_name for row in attestation_rows],
            ["maintainer_verifier", "maintainer"],
        )

    revalidation_rows = [
        row
        for row in requirement_comparisons
        if row.workflow_status == "awaiting_revalidation"
        and row.material_status
        in {"provided", "retained", "verified", "overridden"}
    ]
    if revalidation_rows:
        roles = (
            ["maintainer"]
            if any(
                row.obligation_id == "O-INDEPENDENT-REVIEW"
                for row in revalidation_rows
            )
            else ["maintainer_verifier", "policy_steward", "maintainer"]
        )
        return _view(
            roles,
            "受影响材料已补充或仍然有效；当前只需重新检查指定修复范围。",
            [row.display_name for row in revalidation_rows],
            ["maintainer"],
        )

    if case.state in {
        "ready_for_human_decision",
        "overridden",
        "verification_complete",
    } and not case.unresolved_blocking_obligations():
        return _view(
            ["maintainer"],
            "治理检查已经达到可决策状态，但最终接受、拒绝或要求修改仍须由人类维护者明确记录。",
            [],
            [],
        )

    verification_rows = [
        row
        for row in requirement_comparisons
        if row.blocking_requirement
        and (
            row.obligation_id == "O-INDEPENDENT-REVIEW"
            or row.workflow_status
            in {"blocks_progression", "awaiting_revalidation"}
        )
        and row.material_status not in {"missing", "stale", "invalid"}
    ]
    if case.state in {
        "awaiting_maintainer_verification",
        "resubmitted",
    } or verification_rows:
        roles = (
            ["maintainer"]
            if any(
                row.obligation_id == "O-INDEPENDENT-REVIEW"
                for row in requirement_comparisons
            )
            else ["maintainer_verifier", "policy_steward", "maintainer"]
        )
        return _view(
            roles,
            "贡献侧要求已经满足，当前轮到有权限的维护者检查；检查完成仍不等于接受。",
            [row.display_name for row in verification_rows],
            ["maintainer"],
        )

    if case.state in {"case_opened", "policy_resolved"}:
        return _view(
            ["system"],
            "系统正在根据项目规则识别风险和本次要求。",
            [],
            ["contributor", "contributor_agent"],
        )
    if case.state == "awaiting_human_attestation":
        return _view(
            ["accountable_human"],
            "当前材料已齐备，等待负责人确认当前版本和范围。",
            ["负责人确认"],
            ["maintainer_verifier", "maintainer"],
        )
    return _view(
        ["contributor", "contributor_agent"],
        "当前仍有贡献侧要求未完成；完成后再交给负责人或维护者。",
        [
            row.display_name
            for row in requirement_comparisons
            if row.currently_blocks_progression
        ],
        ["accountable_human", "maintainer_verifier", "maintainer"],
    )
