"""Build and render the maintainer-facing reviewer guidance view."""

from __future__ import annotations

import html
import json
from typing import Any

from ..config import VNextConfig
from ..migration import MigrationDiagnostic
from ..models import GovernanceCase, StateTransition, fingerprint
from .action_planner import action_views, normalize_actor
from .diagnostics import (
    CURRENT_STATE_LABELS,
    RESULT_LABELS,
    build_finding_views,
    build_requirement_comparisons,
    derive_readiness,
)
from .models import (
    ActionPreview,
    ActorContext,
    AvailableAction,
    ContributionSummary,
    GuidanceUtilityAction,
    GuidanceExplanation,
    MaterialityDeclarationView,
    RejectedOperationView,
    RequirementComparison,
    ResponsibilityView,
    ReviewerGuidanceView,
    TraceReference,
    UnavailableAction,
    WorkflowStepView,
)
from .responsibility import (
    ROLE_LABELS,
    derive_current_responsibility,
)
from .reason_presentations import present_reason
from .utilities import build_guidance_utilities
from .workflow import STEP_DEFINITIONS, STEP_STYLES, build_workflow_steps


AUTHORITY_NOTICE = (
    "本页面只把 AGM 的真实状态、依据和合法操作整理成人类可读形式。"
    "材料齐备、核验完成或 eligible 均不等于接受；最终决定只属于获授权的"
    "人类维护者。"
)

RISK_LABELS = {
    "low": "低",
    "medium": "中",
    "high": "较高",
    "critical": "关键",
    "not_applicable": "本次不适用",
}

RISK_AREA_LABELS = {
    "authentication": "登录与认证",
    "authorization": "权限控制",
    "configuration": "配置",
    "governance": "项目治理",
    "documentation": "文档",
    "runtime": "运行时",
}

AUTONOMY_LABELS = {
    "human_direct": "由人直接完成或直接控制",
    "supervised_agent": "智能体执行、有人监督",
    "delegated_agent": "存在继续委派的智能体工作",
    "autonomous_agent": "智能体具有较高独立行动范围",
}

OPERATION_LABELS = {
    "verify_evidence": "维护者检查",
    "decide_accept": "接受决定",
    "decide_reject": "拒绝决定",
    "decide_request_changes": "要求修改的最终决定",
    "decide_close": "关闭决定",
    "final_decision": "最终决定",
    "authorized_override": "有权覆盖",
}


def _matched_interactions(
    case: GovernanceCase, policy: VNextConfig
) -> list[dict[str, Any]]:
    ids = {
        interaction_id
        for item in case.obligations
        for interaction_id in item.interaction_ids
    }
    return [
        item for item in policy.interaction_rules if item["id"] in ids
    ]


def _path_kind(case: GovernanceCase) -> tuple[str, str]:
    has_attestation = any(
        item.type == "human_attestation" for item in case.obligations
    )
    has_independent = any(
        item.obligation_id == "O-INDEPENDENT-REVIEW"
        for item in case.obligations
    )
    if case.mode == "ordinary" or case.state == "ordinary_unmanaged":
        return "ordinary", "普通项目流程"
    if (
        case.overall_risk_level in {"low", "medium"}
        and not has_attestation
        and not has_independent
    ):
        return "lightweight", "轻量审核"
    return "full", "完整治理流程"


def _summary(
    case: GovernanceCase,
    comparisons: list[RequirementComparison],
    responsibility: ResponsibilityView,
    migration: MigrationDiagnostic | None = None,
) -> ContributionSummary:
    blocking_results = {
        "missing",
        "needs_update",
        "invalid",
        "blocked",
    }
    blocking_count = sum(
        1
        for item in comparisons
        if item.blocking_requirement and item.result in blocking_results
    )
    warning_count = sum(
        1
        for item in comparisons
        if item.result == "needs_attention"
    ) + sum(
        1
        for item in case.findings
        if not item.blocking and item.status == "open"
    )
    if migration and migration.policy_changed:
        warning_count += 1
    path_kind, path_label = _path_kind(case)
    current_stage = CURRENT_STATE_LABELS.get(case.state, case.state)
    if any(
        item.blocking_requirement
        and item.material_status in {"missing", "stale", "invalid"}
        and item.workflow_status == "awaiting_contributor"
        for item in comparisons
    ):
        current_stage = "等待贡献侧补齐或更新材料"
    elif any(
        item.workflow_status == "awaiting_revalidation"
        for item in comparisons
    ):
        current_stage = "等待维护者重新检查指定范围"
    elif any(
        item.raw_status == "policy_conflict" for item in comparisons
    ):
        current_stage = "等待有权角色解决项目规则冲突"
    return ContributionSummary(
        case_id=case.id,
        changed_files=list(case.changed_files),
        risk_level=case.overall_risk_level,
        risk_areas=sorted(
            {
                (
                    f"{RISK_AREA_LABELS.get(item.zone, item.zone)}"
                    f"（{item.zone}）"
                )
                for item in case.matched_rules
            }
        ),
        autonomy_profile=case.autonomy_profile,
        path_kind=path_kind,
        path_label=path_label,
        current_stage=current_stage,
        blocking_issue_count=blocking_count,
        warning_count=warning_count,
        current_responsible_parties=[
            ROLE_LABELS.get(item, item)
            for item in responsibility.primary_roles
        ],
        next_authorized_actor_roles=responsibility.primary_roles,
        raw_state=case.state,
        raw_readiness=derive_readiness(case),
    )


def _materiality_declaration(
    case: GovernanceCase,
    comparisons: list[RequirementComparison],
) -> MaterialityDeclarationView | None:
    latest_repair = next(
        (
            repair
            for repair in reversed(case.repair_requests)
            if repair.attempts
        ),
        None,
    )
    if latest_repair is None:
        return None
    attempt = latest_repair.attempts[-1]
    assessment = attempt.get("change_assessment", attempt)
    classification = str(
        assessment.get("change_classification", "not_declared")
    )
    labels = {
        "unrelated": "无关变化",
        "non_material": "非实质变化",
        "no_material_change": "未检测到贡献指纹变化",
        "material": "实质变化",
        "partial_material_change": "局部实质变化",
        "full_material_change": "完整实质变化",
        "not_declared": "未声明",
    }
    affected = list(
        assessment.get(
            "required_revalidation_scope",
            attempt.get("affected_obligation_ids", []),
        )
    )
    by_id = {
        item.obligation_id: item.display_name for item in comparisons
    }
    unaffected = [
        item.obligation_id
        for item in comparisons
        if item.obligation_id not in set(affected)
    ]
    reason_code = str(
        assessment.get("change_reason_code")
        or (
            "partial_affected_scope"
            if classification == "partial_material_change"
            else (
                "wording_only_clarification"
                if classification in {"non_material", "no_material_change"}
                and affected == ["O-AGENT-SCOPE"]
                else classification
            )
        )
    )
    traces = [
        TraceReference("repair_request", latest_repair.id, "source"),
        TraceReference(
            "resubmission_attempt",
            str(attempt.get("id", "unrecorded")),
            "materiality_declaration",
        ),
    ]
    reason = present_reason(
        reason_code=reason_code,
        source_english=str(
            assessment.get("change_reason", "No source reason recorded.")
        ),
        trace_refs=traces,
    )
    return MaterialityDeclarationView(
        classification=classification,
        classification_label=labels.get(classification, classification),
        declared_by=str(attempt.get("actor", "未记录")),
        reason=reason.display_plain,
        reason_presentation=reason,
        affected_obligation_ids=affected,
        affected_labels=[by_id.get(item, item) for item in affected],
        unaffected_obligation_ids=unaffected,
        unaffected_labels=[by_id.get(item, item) for item in unaffected],
        retained_evidence_ids=list(
            assessment.get("retained_evidence_ids", [])
        ),
        stale_evidence_ids=list(
            assessment.get("stale_evidence_ids", [])
        ),
        invalidated_attestation_ids=list(
            assessment.get("invalidated_attestation_ids", [])
        ),
        requires_maintainer_verification=True,
        traceability=traces,
    )


def _rejected_operation_notice(
    case: GovernanceCase,
) -> RejectedOperationView | None:
    attempt = next(
        (
            item
            for item in reversed(case.attempted_operations)
            if item.result == "denied"
        ),
        None,
    )
    if attempt is None:
        return None
    actor_label = ROLE_LABELS.get(attempt.actor_role, attempt.actor_role)
    operation_label = OPERATION_LABELS.get(
        attempt.operation,
        "受治理控制的操作",
    )
    permission_denied = attempt.actor_role not in attempt.required_roles
    reason_plain = (
        "系统已拒绝该操作，因为该角色没有执行此操作所需的权限。"
        if permission_denied
        else "系统已拒绝该操作，因为操作范围或当前流程位置不符合要求。"
    )
    return RejectedOperationView(
        attempt_id=attempt.id,
        operation=attempt.operation,
        actor=attempt.actor,
        actor_role=attempt.actor_role,
        attempted_at=attempt.attempted_at,
        result=attempt.result,
        display_title="最近一次操作未生效",
        display_message=f"{actor_label}尝试执行{operation_label}。",
        reason_plain=reason_plain,
        reason_raw=attempt.reason_raw,
        state_changed=attempt.state_changed,
        current_state=attempt.state_after,
        current_state_label=CURRENT_STATE_LABELS.get(
            attempt.state_after,
            attempt.state_after,
        ),
        required_roles=list(attempt.required_roles),
        trace_refs=[
            TraceReference(
                "attempted_operation",
                attempt.id,
                "denied_audit_event",
            )
        ],
    )


def _explanations(
    case: GovernanceCase,
    comparisons: list[RequirementComparison],
    migration: MigrationDiagnostic | None = None,
) -> list[GuidanceExplanation]:
    result = []
    path_kind, _ = _path_kind(case)
    if path_kind == "lightweight":
        traces = [
            TraceReference(
                "matched_rule", item.id, "path_intensity"
            )
            for item in case.matched_rules
        ]
        reason = present_reason(
            reason_code="lightweight_path",
            source_english=case.mode_reason,
            trace_refs=traces,
        )
        result.append(
            GuidanceExplanation(
                title="为什么本次采用轻量审核？",
                technical_term="lightweight path",
                plain_language=(
                    "本次修改未触发高风险规则，也不要求负责人确认或独立维护者"
                    "检查；所需材料较少，但最终项目决定仍由人类维护者作出。"
                ),
                source_references=traces,
                reason_presentation=reason,
            )
        )
    by_result = {item.result for item in comparisons}
    if "needs_update" in by_result:
        stale_ids = [
            item.id
            for item in case.evidence
            if item.validity_state in {"stale", "expired"}
        ]
        result.append(
            GuidanceExplanation(
                title="这份材料已经过时",
                technical_term="stale evidence",
                plain_language=(
                    "现有材料对应旧的代码、策略或有效期，不能直接支持当前修改。"
                ),
                source_references=[
                    TraceReference("evidence", item, "stale_binding")
                    for item in stale_ids
                ],
            )
        )
    if any(item.status == "invalidated" for item in case.attestations):
        traces = [
            TraceReference(
                "human_attestation", item.id, "invalidated"
            )
            for item in case.attestations
            if item.status == "invalidated"
        ]
        result.append(
            GuidanceExplanation(
                title="旧的负责人确认已不能使用",
                technical_term="invalidated attestation",
                plain_language=(
                    "受影响范围或材料绑定发生变化，需要负责人对当前范围重新确认。"
                ),
                source_references=traces,
                reason_presentation=present_reason(
                    reason_code="invalidated_attestation",
                    source_english=next(
                        (
                            item.invalidation_reason
                            for item in reversed(case.attestations)
                            if item.status == "invalidated"
                        ),
                        None,
                    ),
                    trace_refs=traces,
                ),
            )
        )
    for repair in case.repair_requests:
        if repair.status not in {"open", "resubmitted"}:
            continue
        latest = repair.attempts[-1] if repair.attempts else {}
        retained = latest.get("retained_evidence_ids", [])
        traces = [
            TraceReference("repair_request", repair.id, "scope"),
            *[
                TraceReference("evidence", item, "retained")
                for item in retained
            ],
        ]
        result.append(
            GuidanceExplanation(
                title="本次只重新检查受影响部分",
                technical_term="scoped repair and revalidation",
                plain_language=(
                    f"需要重新检查：{', '.join(repair.revalidation_required) or '未指定'}。"
                    f" 保留的材料：{', '.join(retained) or '由绑定状态决定'}。"
                ),
                source_references=traces,
                reason_presentation=present_reason(
                    reason_code="retained_unaffected_evidence",
                    source_english=(
                        "Unaffected evidence remains bound to the current "
                        "contribution fingerprint."
                    ),
                    trace_refs=traces,
                ),
            )
        )
    if migration and migration.policy_changed:
        traces = [
            TraceReference(
                "policy_snapshot",
                migration.original_policy_fingerprint,
                "recorded",
            ),
            TraceReference(
                "policy_snapshot",
                migration.current_policy_fingerprint,
                "current",
            ),
        ]
        reason = present_reason(
            reason_code="policy_migration_warning",
            source_english=migration.reason,
            trace_refs=traces,
        )
        result.append(
            GuidanceExplanation(
                title="项目规则在案例打开后发生了变化",
                technical_term="policy migration warning",
                plain_language=(
                    reason.display_plain
                    + " 迁移需要按角色权限另行决定。"
                ),
                source_references=traces,
                reason_presentation=reason,
            )
        )
    return result


def _technical_details(
    case: GovernanceCase,
    policy: VNextConfig,
    transitions: list[StateTransition],
    migration: MigrationDiagnostic | None,
) -> dict[str, Any]:
    interactions = _matched_interactions(case, policy)
    return {
        "raw_state": case.state,
        "readiness": derive_readiness(case),
        "risk_rules": [item.to_dict() for item in case.matched_rules],
        "autonomy_profile": policy.autonomy_profiles.get(
            case.autonomy_profile, {"id": case.autonomy_profile}
        ),
        "assurance_profile": policy.assurance_profiles.get(
            case.assurance_profile, {"id": case.assurance_profile}
        ),
        "interaction_rules": interactions,
        "compiled_obligations": [
            item.to_dict() for item in case.obligations
        ],
        "evidence_records": [item.to_dict() for item in case.evidence],
        "attestation_records": [
            item.to_dict() for item in case.attestations
        ],
        "verification_records": [
            item.to_dict() for item in case.maintainer_verifications
        ],
        "findings": [item.to_dict() for item in case.findings],
        "repair_requests": [
            item.to_dict() for item in case.repair_requests
        ],
        "attempted_operations": [
            item.to_dict() for item in case.attempted_operations
        ],
        "contribution_fingerprint": case.contribution_fingerprint,
        "policy_fingerprint": case.policy_snapshot.policy_fingerprint,
        "policy_snapshot": case.policy_snapshot.to_dict(),
        "transition_history": [item.to_dict() for item in transitions],
        "final_decision": (
            case.final_decision.to_dict() if case.final_decision else None
        ),
        "closure_receipt": (
            case.closure_receipt.to_dict()
            if case.closure_receipt
            else None
        ),
        "policy_migration_diagnostic": (
            migration.to_dict() if migration else None
        ),
        "raw_english_specification_text": {
            "obligations": {
                item.obligation_id: item.description
                for item in case.obligations
            },
            "matched_rule_reasons": {
                item.rule_id: item.selector_reasons
                for item in case.matched_rules
            },
            "interaction_rules": {
                item["id"]: item.get("description", "")
                for item in interactions
            },
            "authority_notice": (
                "Verification or readiness is not acceptance. Final decisions "
                "remain with authorized human maintainers."
            ),
        },
    }


def build_reviewer_guidance(
    case: GovernanceCase,
    policy: VNextConfig,
    transitions: list[StateTransition],
    current_actor: ActorContext,
    *,
    migration_diagnostic: MigrationDiagnostic | None = None,
) -> ReviewerGuidanceView:
    """Build a pure, serializable view from canonical case and policy data."""
    actor = normalize_actor(policy, current_actor)
    comparisons = build_requirement_comparisons(case)
    responsibility = derive_current_responsibility(
        case,
        comparisons,
        case.findings,
        case.repair_requests,
        case.attestations,
        actor,
    )
    available, unavailable = action_views(case, policy, actor)
    current_actions = [
        item for item in available if item.group == "current_relevant"
    ][:4]
    current_ids = {item.action for item in current_actions}
    other_actions = [
        item
        for item in available
        if item.action not in current_ids
    ]
    return ReviewerGuidanceView(
        schema_version="agm.reviewer_guidance/v0.2-dev",
        generated_from_case_fingerprint=case.contribution_fingerprint,
        actor=actor,
        summary=_summary(
            case, comparisons, responsibility, migration_diagnostic
        ),
        workflow_steps=build_workflow_steps(case, transitions),
        requirement_comparisons=comparisons,
        diagnostics=build_finding_views(case),
        available_actions=available,
        unavailable_actions=unavailable,
        explanations=_explanations(
            case, comparisons, migration_diagnostic
        ),
        delegation_help=GuidanceExplanation(
            title="是否把具有独立行动能力的工作交给了另一个智能体？",
            technical_term="agent action and delegation scope",
            plain_language=(
                "通常算作继续委派：子智能体修改文件、执行命令、自主生成被直接"
                "采用的代码或配置、拥有独立工具权限或行动范围，或其产出直接进入"
                "当前贡献。通常不算：普通函数或工具调用、文件读取、搜索、没有"
                "独立行动权的模型调用，或只提供建议且没有修改/提交产出的辅助模型。"
            ),
            source_references=[
                TraceReference(
                    "autonomy_profile",
                    case.autonomy_profile,
                    "delegation_definition",
                ),
                *[
                    TraceReference(
                        "compiled_obligation",
                        item.id,
                        "agent_scope_requirement",
                    )
                    for item in case.obligations
                    if item.obligation_id == "O-AGENT-SCOPE"
                ],
            ],
        ),
        repair_loop=[
            "维护者发现问题",
            "返回修改指定部分",
            "重新检查受影响部分",
            "继续原流程",
        ],
        technical_details=_technical_details(
            case, policy, transitions, migration_diagnostic
        ),
        authority_notice=AUTHORITY_NOTICE,
        responsibility=responsibility,
        current_relevant_actions=current_actions,
        other_available_actions=other_actions,
        unavailable_action_summary=(
            f"还有 {len(unavailable)} 项操作因当前阶段、权限或对象范围暂不可用"
        ),
        utility_actions=build_guidance_utilities(
            case, comparisons, responsibility
        ),
        materiality_declaration=_materiality_declaration(
            case, comparisons
        ),
        rejected_operation_notice=_rejected_operation_notice(case),
    )


def build_no_package_guidance(
    simulation: dict[str, Any],
    policy: VNextConfig,
    current_actor: ActorContext,
) -> ReviewerGuidanceView:
    """Represent the ordinary no-package path as a valid non-failure result."""
    actor = normalize_actor(policy, current_actor)
    matched_rules = simulation.get("matched_rules", [])
    changed_files = sorted(
        {
            path
            for item in matched_rules
            for path in item.get("affected_paths", [])
        }
    )
    requirement = RequirementComparison(
        obligation_id="AGM-PACKAGE",
        check_item="完整 AGM 材料包",
        project_requirement="本次修改不要求完整 AGM 材料。",
        current_situation="未提交 AGM package；按普通项目流程继续。",
        result="not_applicable",
        result_label=RESULT_LABELS["not_applicable"],
        raw_status="no_agm_package_submitted",
        blocking_requirement=False,
        source_rule_ids=[
            item.get("rule_id", "") for item in matched_rules
        ],
        interaction_ids=list(simulation.get("interaction_rules", [])),
        evidence_ids=[],
        binding_fingerprints=[],
        finding_ids=[],
        reference_english="No AGM package required.",
        observed_english=(
            "No AGM package submitted. This does not confirm human authorship."
        ),
        traceability=[
            TraceReference(
                "intake_decision",
                simulation.get("intake", {}).get(
                    "package_status", "no_agm_package_submitted"
                ),
                "ordinary_path",
            )
        ],
        display_name="完整 AGM 材料包",
        reference_plain="本次修改不要求完整 AGM 材料。",
        observed_plain="未提交 AGM 材料包；这不是失败，按普通项目流程继续。",
        observed_raw=(
            "No AGM package submitted. This does not confirm human authorship."
        ),
        material_status="not_applicable",
        material_status_label="本次不要求",
        workflow_status="completed",
        workflow_status_label="已完成",
        currently_blocks_progression=False,
        affected_scope=changed_files,
    )
    workflow = []
    statuses = [
        ("completed", "系统已识别本次不要求完整 AGM package。"),
        ("skipped", "本次按普通项目贡献流程准备内容。"),
        ("skipped", "AGM 本次不要求负责人确认。"),
        ("skipped", "AGM 本次不要求独立维护者核验。"),
        ("current", "最终接受或合并仍由人类维护者按项目流程决定。"),
    ]
    for number, ((step_id, title, internal), (status, explanation)) in enumerate(
        zip(STEP_DEFINITIONS, statuses), start=1
    ):
        symbol, label = STEP_STYLES[status]
        workflow.append(
            WorkflowStepView(
                number=number,
                step_id=step_id,
                title=title,
                status=status,
                status_label=label,
                symbol=symbol,
                explanation=explanation,
                internal_stages=internal,
                traceability=(
                    requirement.traceability if number == 1 else []
                ),
            )
        )
    view_action = AvailableAction(
        action="view_change_scope",
        title="查看变化范围",
        description="查看普通路径的风险识别与 intake 依据。",
        consequence="只读操作，不改变任何状态。",
        mutates_state=False,
        actor_role=actor.role,
        traceability=requirement.traceability,
    )
    unavailable = [
        UnavailableAction(
            action=item,
            title=title,
            description="该操作属于 Governance Case 生命周期。",
            reason="本次没有创建 Governance Case，因此该操作不适用。",
            next_actor_roles=["maintainer"],
            mutates_state=True,
            traceability=requirement.traceability,
        )
        for item, title in (
            ("verify_evidence", "检查 AGM 材料"),
            ("authorized_override", "执行有权覆盖"),
            ("decide_accept", "在 AGM Case 中记录接受"),
        )
    ]
    responsibility = ResponsibilityView(
        primary_roles=["maintainer"],
        display_label="人类维护者",
        reason=(
            "本次不要求完整 AGM 材料，最终项目决定仍由人类维护者按普通流程作出。"
        ),
        blocking_items=[],
        next_handoff_roles=[],
    )
    utilities = [
        GuidanceUtilityAction(
            action_id="view_change_scope",
            label="查看变化范围",
            description="查看普通路径的 changed files 和 intake 依据。",
            output_type="application/json",
            output=json.dumps(simulation, ensure_ascii=False, indent=2),
            trace_refs=requirement.traceability,
        ),
        GuidanceUtilityAction(
            action_id="copy_handoff_note",
            label="复制当前责任方说明",
            description="生成普通路径的只读 handoff note。",
            output_type="text/plain",
            output=responsibility.reason,
            trace_refs=requirement.traceability,
        ),
    ]
    return ReviewerGuidanceView(
        schema_version="agm.reviewer_guidance/v0.2-dev",
        generated_from_case_fingerprint=fingerprint(simulation),
        actor=actor,
        summary=ContributionSummary(
            case_id=None,
            changed_files=changed_files,
            risk_level=simulation.get("overall_risk_level", "low"),
            risk_areas=sorted(
                {
                    f"{item.get('zone')} ({item.get('rule_id')})"
                    for item in matched_rules
                }
            ),
            autonomy_profile="human_direct",
            path_kind="ordinary",
            path_label="普通流程（无需完整 AGM 材料）",
            current_stage="等待人类维护者按普通项目流程决定",
            blocking_issue_count=0,
            warning_count=0,
            current_responsible_parties=["人类维护者"],
            next_authorized_actor_roles=["maintainer"],
            raw_state="ordinary_unmanaged",
            raw_readiness="no_agm_package_submitted",
        ),
        workflow_steps=workflow,
        requirement_comparisons=[requirement],
        diagnostics=[],
        available_actions=[view_action],
        unavailable_actions=unavailable,
        explanations=[
            GuidanceExplanation(
                title="本次修改不要求完整 AGM 材料",
                technical_term="No AGM package required",
                plain_language=(
                    "no package 是普通路径结果，不是失败，也不能据此推断贡献由"
                    "人类独立完成。"
                ),
                source_references=requirement.traceability,
                reason_presentation=present_reason(
                    reason_code="no_package",
                    source_english=requirement.observed_english,
                    trace_refs=requirement.traceability,
                ),
            )
        ],
        delegation_help=GuidanceExplanation(
            title="普通路径不改变角色权限",
            technical_term="risk and authority remain orthogonal",
            plain_language=(
                "治理要求可以因任务简单而降低，但贡献侧智能体仍不能冒充"
                "维护者作 verification、override 或 final decision。"
            ),
            source_references=requirement.traceability,
        ),
        repair_loop=[],
        technical_details={
            "raw_state": "ordinary_unmanaged",
            "readiness": "no_agm_package_submitted",
            "simulation": simulation,
            "policy_fingerprint": policy.policy_fingerprint,
            "raw_english_specification_text": {
                "no_package": (
                    "No AGM package submitted. This does not confirm human "
                    "authorship."
                ),
                "final_authority": (
                    "Final decisions remain with authorized human maintainers."
                ),
            },
        },
        authority_notice=AUTHORITY_NOTICE,
        responsibility=responsibility,
        current_relevant_actions=[],
        other_available_actions=[view_action],
        unavailable_action_summary=(
            f"还有 {len(unavailable)} 项 AGM Case 操作在普通路径不适用"
        ),
        utility_actions=utilities,
        materiality_declaration=None,
        rejected_operation_notice=None,
    )


def render_guidance_markdown(view: ReviewerGuidanceView) -> str:
    lines = [
        "# AGM Reviewer Guidance Layer",
        "",
        f"- 案例: `{view.summary.case_id or '普通路径 / 无 AGM Case'}`",
        f"- 本次路径: {view.summary.path_label}",
        f"- 当前阶段: {view.summary.current_stage}",
        f"- 风险: {RISK_LABELS.get(view.summary.risk_level, view.summary.risk_level)}",
        f"- 阻断问题: {view.summary.blocking_issue_count}",
        f"- 需要关注: {view.summary.warning_count}",
        (
            "- 当前责任方: "
            + (
                view.responsibility.display_label
                if view.responsibility
                else "未推导"
            )
        ),
        (
            "- 责任方依据: "
            + (
                view.responsibility.reason
                if view.responsibility
                else "无"
            )
        ),
        "",
        "## 五步流程",
        "",
    ]
    for item in view.workflow_steps:
        lines.append(
            f"{item.number}. {item.symbol} **{item.title}** — "
            f"{item.status_label}：{item.explanation}"
        )
    if view.rejected_operation_notice:
        notice = view.rejected_operation_notice
        lines.extend(
            [
                "",
                f"## {notice.display_title}",
                "",
                notice.display_message,
                "",
                notice.reason_plain,
                "",
                "- 案例状态没有变化"
                if not notice.state_changed
                else "- 案例状态发生变化，请核对审计记录",
                f"- 当前仍处于：{notice.current_state_label}",
                "- 下一步需要："
                + "、".join(
                    ROLE_LABELS.get(role, role)
                    for role in notice.required_roles
                ),
            ]
        )
    lines.extend(
        [
            "",
            "## 项目要求对比",
            "",
            "| 检查项 | 项目要求 | 当前情况 | 材料状态 | 流程状态 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in view.requirement_comparisons:
        values = [
            item.check_item,
            item.reference_plain,
            item.observed_plain,
            item.material_status_label,
            item.workflow_status_label,
        ]
        lines.append(
            "| "
            + " | ".join(
                value.replace("|", "\\|").replace("\n", " ")
                for value in values
            )
            + " |"
        )
    lines.extend(["", "## 当前相关操作", ""])
    if not view.current_relevant_actions:
        lines.append("- 当前角色没有直接改变状态的相关操作；可使用下方只读交接工具。")
    for item in view.current_relevant_actions:
        lines.append(
            f"- **{item.title}** (`{item.action}`): {item.consequence}"
        )
    lines.extend(["", "## 其他可用操作（折叠区内容）", ""])
    for item in view.other_available_actions:
        lines.append(f"- **{item.title}**: {item.consequence}")
    lines.extend(["", "## 只读交接工具", ""])
    for item in view.utility_actions:
        lines.append(f"- **{item.label}**: {item.description}")
    lines.extend(["", "## 暂不可用操作摘要", ""])
    lines.append(f"- {view.unavailable_action_summary}")
    for item in view.unavailable_actions:
        lines.append(
            f"  - {item.title}: {item.reason}"
        )
    lines.extend(
        [
            "",
            "## Authority boundary",
            "",
            view.authority_notice,
            "",
        ]
    )
    return "\n".join(lines)


def render_action_preview_markdown(preview: ActionPreview) -> str:
    """Render the preview display layer first and fold raw identifiers."""

    lines = [
        "## 操作预览",
        "",
        f"你准备执行：**{preview.title}**",
        "",
        preview.authorization_reason,
        "",
        "### 将处理",
        "",
        *(
            [f"- {item}" for item in preview.affected_items]
            or ["- 无"]
        ),
        "",
        "### 将保留",
        "",
        *(
            [f"- {item}" for item in preview.retained_items]
            or ["- 无"]
        ),
        "",
        "### 预计变化",
        "",
        *(
            [
                (
                    f"- {item.display_label}：{item.before_label} → "
                    f"{item.after_label}。{item.display_description}"
                )
                for item in preview.display_effects
            ]
            or ["- 案例不会发生变化。"]
        ),
        "",
        "### 执行后",
        "",
        *([f"- {item}" for item in preview.next_steps] or ["- 无"]),
        "",
        "<details>",
        "<summary>技术操作、内部 ID 与原始状态</summary>",
        "",
        "```json",
        json.dumps(
            preview.technical_details,
            indent=2,
            ensure_ascii=False,
        ),
        "```",
        "",
        "</details>",
    ]
    return "\n".join(lines)


def _json_block(value: Any) -> str:
    return html.escape(
        json.dumps(value, ensure_ascii=False, indent=2, default=str)
    )


def _trace_details(row: RequirementComparison) -> str:
    payload = {
        "obligation_id": row.obligation_id,
        "source_rules": row.source_rule_ids,
        "interaction_rules": row.interaction_ids,
        "evidence_ids": row.evidence_ids,
        "binding_fingerprints": row.binding_fingerprints,
        "finding_ids": row.finding_ids,
        "reference_english": row.reference_english,
        "observed_raw": row.observed_raw,
        "raw_status": row.raw_status,
        "material_status": row.material_status,
        "workflow_status": row.workflow_status,
        "blocking_requirement": row.blocking_requirement,
        "currently_blocks_progression": row.currently_blocks_progression,
        "traceability": [
            item.to_dict() for item in row.traceability
        ],
    }
    return (
        "<details><summary>查看原始依据</summary>"
        f"<pre>{_json_block(payload)}</pre></details>"
    )


def _action_preview_html(
    preview: ActionPreview,
    *,
    action_token: str | None,
    form_values: dict[str, list[str]] | None,
) -> str:
    effects = "".join(
        "<li>"
        f"<strong>{html.escape(item.display_label)}</strong>: "
        f"{html.escape(item.before_label)} → "
        f"{html.escape(item.after_label)}"
        f"<br>{html.escape(item.display_description)}"
        "</li>"
        for item in preview.display_effects
    )
    affected = "、".join(preview.affected_items) or "无"
    retained = "、".join(preview.retained_items) or "无"
    invalidated = "、".join(preview.invalidated_items) or "无"
    next_steps = "".join(
        f"<li>{html.escape(item)}</li>" for item in preview.next_steps
    )
    confirmation = ""
    if (
        preview.authorized
        and preview.requires_confirmation
        and action_token
        and form_values is not None
    ):
        hidden = [
            (
                '<input type="hidden" name="action_token" value="'
                + html.escape(action_token, quote=True)
                + '">'
            ),
            (
                '<input type="hidden" name="confirm" value="execute">'
            ),
            (
                '<input type="hidden" name="preview_fingerprint" value="'
                + html.escape(preview.preview_fingerprint, quote=True)
                + '">'
            ),
        ]
        for key, values in form_values.items():
            if key in {
                "action_token",
                "confirm",
                "preview_fingerprint",
            }:
                continue
            for value in values:
                hidden.append(
                    f'<input type="hidden" name="{html.escape(key, quote=True)}" '
                    f'value="{html.escape(value, quote=True)}">'
                )
        confirmation = (
            '<form method="post" class="confirm-form">'
            + "".join(hidden)
            + '<button class="danger" type="submit">确认执行</button>'
            + '<a class="button-link" href="/">返回重新选择</a>'
            + "</form>"
        )
    return (
        '<section class="preview" id="action-preview">'
        "<h2>操作前预览</h2>"
        f"<p>你准备执行：<strong>{html.escape(preview.title)}</strong></p>"
        f"<p>{html.escape(preview.authorization_reason)}</p>"
        f"<p><strong>将处理：</strong>{html.escape(affected)}</p>"
        f"<ul>{effects or '<li>不会改变案例。</li>'}</ul>"
        f"<p><strong>保留的未受影响材料：</strong>{html.escape(retained)}</p>"
        f"<p><strong>将失效：</strong>{html.escape(invalidated)}</p>"
        "<p><strong>责任方变化：</strong>"
        f"{html.escape(preview.responsibility_before.display_label if preview.responsibility_before else '未推导')}"
        " → "
        f"{html.escape(preview.responsibility_after.display_label if preview.responsibility_after else '未推导')}</p>"
        "<p><strong>流程位置变化：</strong>"
        f"{html.escape(preview.workflow_position_before)} → "
        f"{html.escape(preview.workflow_position_after)}</p>"
        f"<p><strong>执行后：</strong></p><ul>{next_steps}</ul>"
        "<p><strong>后续仍需负责人确认：</strong>"
        f"{'是' if preview.requires_human_attestation_after else '否'}；"
        "<strong>后续仍需维护者检查：</strong>"
        f"{'是' if preview.requires_maintainer_verification_after else '否'}；"
        "<strong>最终接受是否已经发生：</strong>"
        f"{'是' if preview.final_acceptance_recorded else '否'}</p>"
        "<p><strong>此预览本身不会修改案例：</strong>是</p>"
        "<details><summary>技术操作、内部 ID 与原始状态</summary>"
        f"<pre>{_json_block(preview.technical_details)}</pre></details>"
        f"{confirmation}</section>"
    )


def _single_action_form(
    view: ReviewerGuidanceView,
    item: AvailableAction,
    action_token: str | None,
) -> str:
    if (
        not action_token
        or not item.mutates_state
        or not view.summary.case_id
    ):
        return ""
    selector = ""
    if item.selector_options:
        options = "".join(
            '<option value="'
            + html.escape(option.selector_token, quote=True)
            + '">'
            + html.escape(
                f"{option.label} — {option.status_label}"
                + ("（阻断）" if option.blocking else "")
            )
            + "</option>"
            for option in item.selector_options
        )
        selector = (
            "<label>选择要处理的问题或材料"
            '<select name="selector_token" required'
            + (" multiple" if item.action in {
                "verify_evidence",
                "request_repair",
                "ask_clarification",
                "record_policy_conflict",
                "authorized_override",
            } else "")
            + f">{options}</select></label>"
            "<details><summary>查看选择项的范围和内部标识</summary>"
            f"<pre>{_json_block([option.to_dict() for option in item.selector_options])}</pre>"
            "</details>"
        )
    elif any(
        parameter in item.required_parameters
        for parameter in {"object_id", "obligation_ids"}
    ):
        return (
            '<p class="selector-empty">'
            "当前没有符合此操作范围的对象；后端不会接受任意内部 ID。"
            "</p>"
        )
    action_specific = ""
    if item.action == "resubmit":
        action_specific = """
<label>本次变化声明
<select name="change_classification" required>
<option value="unrelated">与 repair 范围无关</option>
<option value="non_material">非实质变化</option>
<option value="material">实质变化</option>
</select></label>
<label>为什么这样声明
<textarea name="change_reason" required></textarea></label>"""
    if item.action == "confirm_attestation":
        action_specific = "".join(
            f'<input type="hidden" name="scope" value="{html.escape(path, quote=True)}">'
            for path in view.summary.changed_files
        )
    return f"""
<form method="post" class="action-form" id="action-{html.escape(item.action, quote=True)}">
<input type="hidden" name="action_token" value="{html.escape(action_token, quote=True)}">
<input type="hidden" name="action" value="{html.escape(item.action, quote=True)}">
<input type="hidden" name="role" value="{html.escape(view.actor.role, quote=True)}">
<label>执行者（必须是真实身份）
<input name="actor" value="{html.escape(view.actor.actor, quote=True)}" required>
</label>
{selector}
{action_specific}
<label>事实依据或原因
<textarea name="reason" required></textarea>
</label>
<button type="submit">预览操作影响</button>
</form>"""


def _action_card(
    view: ReviewerGuidanceView,
    item: AvailableAction,
    action_token: str | None,
) -> str:
    return (
        '<article class="action-card available">'
        f"<h3>{html.escape(item.title)}</h3>"
        f"<p>{html.escape(item.description)}</p>"
        f"<p><strong>为什么现在相关：</strong>"
        f"{html.escape(item.primary_reason)}</p>"
        f"<p><strong>执行后：</strong>{html.escape(item.consequence)}</p>"
        f"{_single_action_form(view, item, action_token)}"
        "<details><summary>技术操作标识与依据</summary>"
        f"<pre>{_json_block({'action': item.action, 'traceability': [trace.to_dict() for trace in item.traceability]})}</pre>"
        "</details></article>"
    )


def render_guidance_html(
    view: ReviewerGuidanceView,
    *,
    action_token: str | None = None,
    preview: ActionPreview | None = None,
    form_values: dict[str, list[str]] | None = None,
) -> str:
    summary = view.summary
    workflow = "".join(
        f'<li class="workflow-step status-{html.escape(item.status)}" '
        f'data-status="{html.escape(item.status)}">'
        f'<span class="symbol" aria-hidden="true">{html.escape(item.symbol)}</span>'
        f"<strong>{item.number}. {html.escape(item.title)}</strong>"
        f'<span class="state-text">{html.escape(item.status_label)}</span>'
        f"<p>{html.escape(item.explanation)}</p>"
        "<details><summary>内部阶段与依据</summary>"
        f"<p>{html.escape(', '.join(item.internal_stages))}</p>"
        f"<pre>{_json_block([trace.to_dict() for trace in item.traceability])}</pre>"
        "</details></li>"
        for item in view.workflow_steps
    )
    comparison_rows = "".join(
        "<tr>"
        f"<td><strong>{html.escape(item.display_name)}</strong></td>"
        f"<td>{html.escape(item.reference_plain)}</td>"
        f"<td>{html.escape(item.observed_plain)}</td>"
        f'<td><span class="result material-{html.escape(item.material_status)}">'
        f"{html.escape(item.material_status_label)}</span></td>"
        f'<td><span class="result workflow-{html.escape(item.workflow_status)}">'
        f"{html.escape(item.workflow_status_label)}</span>"
        + (
            "<br><strong>案例暂时不能继续</strong>"
            if item.currently_blocks_progression
            else ""
        )
        + f"{_trace_details(item)}</td>"
        "</tr>"
        for item in view.requirement_comparisons
    )
    current_available = "".join(
        _action_card(view, item, action_token)
        for item in view.current_relevant_actions
    ) or (
        "<p>当前角色没有直接改变治理状态的相关操作。"
        "可使用下方交接工具查看和导出真实待办。</p>"
    )
    other_available = "".join(
        _action_card(view, item, action_token)
        for item in view.other_available_actions
    )
    unavailable = "".join(
        '<article class="action-card unavailable" aria-disabled="true">'
        f"<h3>{html.escape(item.title)} <span>当前不可用</span></h3>"
        f"<p>{html.escape(item.description)}</p>"
        f"<p><strong>原因：</strong>{html.escape(item.reason)}</p>"
        f"<p><strong>所需角色：</strong>"
        f"{html.escape('、'.join(ROLE_LABELS.get(role, role) for role in item.required_role) or '无')}</p>"
        f"<p><strong>所需技术状态：</strong>"
        f"{html.escape('、'.join(item.required_state) or '无')}</p>"
        f"<p><strong>以后是否可能可用：</strong>"
        f"{html.escape(item.future_availability)}</p>"
        "<details><summary>技术操作标识与依据</summary>"
        f"<pre>{_json_block(item.to_dict())}</pre></details>"
        "</article>"
        for item in view.unavailable_actions
    )
    utilities = "".join(
        '<article class="action-card utility">'
        f"<h3>{html.escape(item.label)}</h3>"
        f"<p>{html.escape(item.description)}</p>"
        f'<a class="button-link" href="/utility?action_id={html.escape(item.action_id, quote=True)}">'
        "打开只读输出</a>"
        "<details><summary>在页面中预览</summary>"
        f"<pre>{html.escape(item.output)}</pre></details>"
        "</article>"
        for item in view.utility_actions
    )
    explanations = "".join(
        "<details class=\"explanation\"><summary>"
        f"{html.escape(item.title)} "
        f"<small>{html.escape(item.technical_term)}</small></summary>"
        f"<p>{html.escape(item.plain_language)}</p>"
        f"<pre>{_json_block([ref.to_dict() for ref in item.source_references])}</pre>"
        "</details>"
        for item in [*view.explanations, view.delegation_help]
    )
    diagnostics = "".join(
        "<li>"
        f"<strong>{html.escape(item.title)}</strong>: "
        f"{html.escape(item.plain_language)}"
        "<details><summary>finding 与 repair 原始依据</summary>"
        f"<pre>{_json_block(item.to_dict())}</pre></details>"
        "</li>"
        for item in view.diagnostics
    ) or "<li>当前没有已记录的问题。</li>"
    rejected_notice = ""
    if view.rejected_operation_notice:
        notice = view.rejected_operation_notice
        required = "、".join(
            ROLE_LABELS.get(role, role)
            for role in notice.required_roles
        ) or "具备相应权限的角色"
        rejected_notice = (
            '<section class="rejected-notice">'
            f"<h2>{html.escape(notice.display_title)}</h2>"
            f"<p>{html.escape(notice.display_message)}</p>"
            f"<p>{html.escape(notice.reason_plain)}</p>"
            "<ul>"
            f"<li>案例状态{'没有变化' if not notice.state_changed else '发生了变化'}</li>"
            f"<li>当前仍在：{html.escape(notice.current_state_label)}</li>"
            f"<li>下一步需要由：{html.escape(required)}处理</li>"
            "</ul>"
            "<details><summary>查看操作、权限和审计依据</summary>"
            f"<pre>{_json_block(notice.to_dict())}</pre></details>"
            "</section>"
        )
    preview_html = (
        _action_preview_html(
            preview,
            action_token=action_token,
            form_values=form_values,
        )
        if preview
        else ""
    )
    materiality = ""
    if view.materiality_declaration:
        item = view.materiality_declaration
        materiality = (
            "<section><h2>变化影响声明</h2>"
            f"<p><strong>本次变化被声明为：</strong>"
            f"{html.escape(item.classification_label)}</p>"
            f"<p><strong>声明者：</strong>{html.escape(item.declared_by)}</p>"
            f"<p><strong>声明理由：</strong>{html.escape(item.reason)}</p>"
            "<p><strong>尚需维护者核验：</strong>"
            f"{'是' if item.requires_maintainer_verification else '否'}</p>"
            f"<p><strong>受影响：</strong>"
            f"{html.escape('、'.join(item.affected_labels) or '未声明')}</p>"
            f"<p><strong>未受影响：</strong>"
            f"{html.escape('、'.join(item.unaffected_labels) or '无')}</p>"
            "<details><summary>材料保留、失效和原始依据</summary>"
            f"<pre>{_json_block(item.to_dict())}</pre></details></section>"
        )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AGM 简明审核视图 — {html.escape(summary.case_id or 'ordinary')}</title>
<style>
:root {{ color-scheme: light; font-family: system-ui, "Microsoft YaHei", sans-serif; }}
body {{ margin: 0; background: #f5f7fa; color: #172033; line-height: 1.55; }}
main {{ max-width: 1240px; margin: 0 auto; padding: 1.4rem; }}
section, header {{ background: white; border: 1px solid #d8e0ea; border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem; }}
.hero {{ border-top: 6px solid #2855a5; }}
.view-switch {{ display: flex; gap: .5rem; margin-bottom: 1rem; }}
.view-switch a, .button-link {{ display: inline-block; padding: .55rem .75rem; border: 1px solid #2855a5; border-radius: 6px; text-decoration: none; color: #173c7a; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(190px,1fr)); gap: .7rem; }}
.metric {{ background: #eef3fa; border-radius: 8px; padding: .75rem; overflow-wrap: anywhere; }}
.workflow {{ list-style: none; padding: 0; display: grid; grid-template-columns: repeat(5,minmax(0,1fr)); gap: .55rem; }}
.workflow-step {{ border: 2px solid #8996a8; border-radius: 9px; padding: .75rem; }}
.workflow-step .symbol {{ font-size: 1.25rem; margin-right: .4rem; }}
.state-text {{ display: block; font-weight: 700; }}
.status-current {{ border-color: #2855a5; }}
.status-problem, .status-return {{ border-color: #9b3d23; }}
.status-completed {{ border-color: #26734d; }}
.status-pending, .status-skipped {{ border-style: dashed; }}
table {{ width: 100%; border-collapse: collapse; font-size: .94rem; }}
th, td {{ border-bottom: 1px solid #d8e0ea; padding: .7rem; text-align: left; vertical-align: top; }}
th {{ background: #eef3fa; }}
.result {{ font-weight: 800; }}
.material-missing, .material-stale, .material-invalid, .workflow-blocks_progression {{ color: #8c2818; }}
.material-provided, .material-retained, .material-verified, .workflow-completed {{ color: #17633e; }}
.actions {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(260px,1fr)); gap: .7rem; }}
.action-card {{ border: 1px solid #bac5d3; border-radius: 9px; padding: .8rem; }}
.action-card.unavailable {{ background: #f0f1f3; color: #4f5968; border-style: dashed; }}
.action-form label {{ display: block; font-weight: 700; margin-top: .7rem; }}
input, select, textarea {{ box-sizing: border-box; width: 100%; padding: .6rem; margin-top: .25rem; }}
button {{ padding: .65rem .9rem; margin-top: .8rem; cursor: pointer; }}
button.danger {{ background: #8c2818; color: white; border: 0; border-radius: 5px; margin-right: .6rem; }}
.preview {{ border: 3px solid #9b6a00; }}
.rejected-notice {{ border: 3px solid #9b3d23; }}
.authority {{ border-left: 7px solid #9b6a00; }}
details {{ margin-top: .45rem; }}
summary {{ cursor: pointer; font-weight: 700; }}
pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #111827; color: #eef2f7; padding: .8rem; border-radius: 7px; max-height: 34rem; overflow: auto; }}
code {{ overflow-wrap: anywhere; }}
@media (max-width: 850px) {{ .workflow {{ grid-template-columns: 1fr; }} table {{ display: block; overflow-x: auto; }} }}
</style>
</head>
<body><main id="plain">
<nav class="view-switch" aria-label="视图切换">
<a href="#plain">简明审核视图</a><a href="#technical">技术详情视图</a>
</nav>
<header class="hero">
<h1>维护者审核引导</h1>
<div class="grid">
<div class="metric"><strong>贡献 / 案例</strong><br>{html.escape(summary.case_id or '普通路径（无 AGM 案例）')}</div>
<div class="metric"><strong>风险</strong><br>{html.escape(RISK_LABELS.get(summary.risk_level, summary.risk_level))}</div>
<div class="metric"><strong>本次路径</strong><br>{html.escape(summary.path_label)}</div>
<div class="metric"><strong>当前阶段</strong><br>{html.escape(summary.current_stage)}</div>
<div class="metric"><strong>阻断问题</strong><br>{summary.blocking_issue_count} 项</div>
<div class="metric"><strong>需要关注</strong><br>{summary.warning_count} 项</div>
<div class="metric"><strong>当前责任方</strong><br>{html.escape('、'.join(summary.current_responsible_parties) or '流程已结束')}</div>
<div class="metric"><strong>智能体参与方式</strong><br>{html.escape(AUTONOMY_LABELS.get(summary.autonomy_profile, summary.autonomy_profile))}</div>
</div>
<p><strong>变更文件：</strong>{html.escape(', '.join(summary.changed_files) or '无')}</p>
<p><strong>风险区域：</strong>{html.escape(', '.join(summary.risk_areas) or '无')}</p>
<p><strong>为什么现在轮到这一方：</strong>{html.escape(view.responsibility.reason if view.responsibility else '未推导')}</p>
<details><summary>技术状态</summary><p>State: <code>{html.escape(summary.raw_state)}</code> · Readiness: <code>{html.escape(summary.raw_readiness)}</code> · Autonomy: <code>{html.escape(summary.autonomy_profile)}</code></p></details>
</header>
{rejected_notice}
<section>
<h2>治理流程导航器</h2>
<ol class="workflow">{workflow}</ol>
{('<p><strong>修复回路：</strong>' + html.escape(' → '.join(view.repair_loop)) + '</p>') if view.repair_loop else ''}
</section>
<section>
<h2>项目要求对比报告</h2>
<table>
<thead><tr><th>检查项</th><th>项目要求</th><th>当前情况</th><th>材料状态</th><th>流程状态 / 整体影响</th></tr></thead>
<tbody>{comparison_rows}</tbody>
</table>
</section>
{materiality}
<section><h2>问题与说明</h2><ul>{diagnostics}</ul>{explanations}</section>
{preview_html}
<section>
<h2>当前相关操作</h2>
<p>这里列出合法选择及影响，不替维护者作决定。后端仍会重新检查角色、状态和对象范围。</p>
<div class="actions">{current_available}</div>
</section>
<section>
<details><summary>其他可用操作（{len(view.other_available_actions)} 项）</summary>
<div class="actions">{other_available or '<p>无其他可用操作。</p>'}</div>
</details>
</section>
<section>
<h2>交接与导出工具</h2>
<p>这些工具只读取当前 guidance，不修改案例，也不增加 transition。</p>
<div class="actions">{utilities}</div>
</section>
<section>
<details><summary>{html.escape(view.unavailable_action_summary)}</summary>
<p>展开后可查看不可用原因、所需角色、所需状态及以后是否可能开放。后端权限检查始终保留。</p>
<div class="actions">{unavailable}</div>
</details>
</section>
<section id="technical">
<details class="technical-details"><summary>技术详情（默认折叠）</summary>
<pre>{_json_block(view.technical_details)}</pre>
</details>
</section>
<section class="authority"><h2>权限边界</h2><p>{html.escape(view.authority_notice)}</p></section>
</main></body></html>"""
