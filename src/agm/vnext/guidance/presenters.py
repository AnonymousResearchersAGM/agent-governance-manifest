"""Build and render the maintainer-facing reviewer guidance view."""

from __future__ import annotations

import html
import json
from typing import Any

from ..config import VNextConfig
from ..migration import MigrationDiagnostic
from ..models import GovernanceCase, StateTransition, fingerprint
from .action_planner import action_views, next_actor_roles, normalize_actor
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
    GuidanceExplanation,
    RequirementComparison,
    ReviewerGuidanceView,
    TraceReference,
    UnavailableAction,
    WorkflowStepView,
)
from .workflow import STEP_DEFINITIONS, STEP_STYLES, build_workflow_steps


AUTHORITY_NOTICE = (
    "本页面只把 AGM 的真实状态、依据和合法操作整理成人类可读形式。"
    "材料齐备、核验完成或 eligible 均不等于接受；最终决定只属于获授权的"
    "人类维护者。"
)

ROLE_LABELS = {
    "system": "AGM 系统",
    "contributor_agent": "贡献侧智能体",
    "contributor": "贡献者",
    "accountable_human": "负责人",
    "maintainer_verifier": "维护者核验人",
    "policy_steward": "策略负责人",
    "maintainer": "人类维护者",
}

RISK_LABELS = {
    "low": "低",
    "medium": "中",
    "high": "较高",
    "critical": "关键",
    "not_applicable": "本次不适用",
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
    migration: MigrationDiagnostic | None = None,
) -> ContributionSummary:
    roles = next_actor_roles(case)
    blocking_results = {
        "missing",
        "needs_update",
        "invalid",
        "blocked",
    }
    blocking_count = sum(
        1
        for item in comparisons
        if item.blocking and item.result in blocking_results
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
    return ContributionSummary(
        case_id=case.id,
        changed_files=list(case.changed_files),
        risk_level=case.overall_risk_level,
        risk_areas=sorted(
            {
                f"{item.zone} ({item.rule_id})"
                for item in case.matched_rules
            }
        ),
        autonomy_profile=case.autonomy_profile,
        path_kind=path_kind,
        path_label=path_label,
        current_stage=CURRENT_STATE_LABELS.get(case.state, case.state),
        blocking_issue_count=blocking_count,
        warning_count=warning_count,
        current_responsible_parties=[
            ROLE_LABELS.get(item, item) for item in roles
        ],
        next_authorized_actor_roles=roles,
        raw_state=case.state,
        raw_readiness=derive_readiness(case),
    )


def _explanations(
    case: GovernanceCase,
    comparisons: list[RequirementComparison],
    migration: MigrationDiagnostic | None = None,
) -> list[GuidanceExplanation]:
    result = []
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
        result.append(
            GuidanceExplanation(
                title="旧的负责人确认已不能使用",
                technical_term="invalidated attestation",
                plain_language=(
                    "受影响范围或材料绑定发生变化，需要负责人对当前范围重新确认。"
                ),
                source_references=[
                    TraceReference(
                        "human_attestation", item.id, "invalidated"
                    )
                    for item in case.attestations
                    if item.status == "invalidated"
                ],
            )
        )
    for repair in case.repair_requests:
        if repair.status not in {"open", "resubmitted"}:
            continue
        latest = repair.attempts[-1] if repair.attempts else {}
        retained = latest.get("retained_evidence_ids", [])
        result.append(
            GuidanceExplanation(
                title="本次只重新检查受影响部分",
                technical_term="scoped repair and revalidation",
                plain_language=(
                    f"需要重新检查：{', '.join(repair.revalidation_required) or '未指定'}。"
                    f" 保留的材料：{', '.join(retained) or '由绑定状态决定'}。"
                ),
                source_references=[
                    TraceReference("repair_request", repair.id, "scope"),
                    *[
                        TraceReference("evidence", item, "retained")
                        for item in retained
                    ],
                ],
            )
        )
    if migration and migration.policy_changed:
        result.append(
            GuidanceExplanation(
                title="项目规则在案例打开后发生了变化",
                technical_term="policy migration warning",
                plain_language=(
                    migration.reason
                    + " 迁移不会由诊断层静默执行，需要按权限另行决定。"
                ),
                source_references=[
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
                ],
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
    available, unavailable = action_views(case, policy, actor)
    return ReviewerGuidanceView(
        schema_version="agm.reviewer_guidance/v0.2-dev",
        generated_from_case_fingerprint=case.contribution_fingerprint,
        actor=actor,
        summary=_summary(case, comparisons, migration_diagnostic),
        workflow_steps=build_workflow_steps(case, transitions),
        requirement_comparisons=comparisons,
        diagnostics=build_finding_views(case),
        available_actions=available,
        unavailable_actions=unavailable,
        explanations=_explanations(
            case, comparisons, migration_diagnostic
        ),
        delegation_help=GuidanceExplanation(
            title="怎样判断是否发生了智能体委派？",
            technical_term="agent action and delegation scope",
            plain_language=(
                "通常属于委派：子智能体修改文件、执行命令、自主生成并提交被采用"
                "的产出，或另一个智能体拥有独立行动范围/工具权限。通常不属于"
                "委派：普通工具函数、读取、搜索、无独立行动权的模型调用，或只"
                "返回建议且未自主修改贡献的辅助模型。"
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
        blocking=False,
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
                traceability=requirement.traceability,
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
    )


def render_guidance_markdown(view: ReviewerGuidanceView) -> str:
    lines = [
        "# AGM Reviewer Guidance Layer",
        "",
        f"- Case: `{view.summary.case_id or 'ordinary/no-case'}`",
        f"- 本次路径: {view.summary.path_label}",
        f"- 当前阶段: {view.summary.current_stage}",
        f"- 风险: {RISK_LABELS.get(view.summary.risk_level, view.summary.risk_level)}",
        f"- 阻断问题: {view.summary.blocking_issue_count}",
        f"- 需要关注: {view.summary.warning_count}",
        "",
        "## 五步流程",
        "",
    ]
    for item in view.workflow_steps:
        lines.append(
            f"{item.number}. {item.symbol} **{item.title}** — "
            f"{item.status_label}：{item.explanation}"
        )
    lines.extend(
        [
            "",
            "## 项目要求对比",
            "",
            "| 检查项 | 项目要求 | 当前情况 | 结果 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in view.requirement_comparisons:
        values = [
            item.check_item,
            item.project_requirement,
            item.current_situation,
            f"{item.result_label} (`{item.result}`)",
        ]
        lines.append(
            "| "
            + " | ".join(
                value.replace("|", "\\|").replace("\n", " ")
                for value in values
            )
            + " |"
        )
    lines.extend(["", "## 当前可执行操作", ""])
    for item in view.available_actions:
        lines.append(
            f"- **{item.title}** (`{item.action}`): {item.consequence}"
        )
    lines.extend(["", "## 当前不可执行操作", ""])
    for item in view.unavailable_actions:
        lines.append(
            f"- {item.title} (`{item.action}`): {item.reason}"
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
        "observed_english_state": row.observed_english,
        "raw_status": row.raw_status,
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
        f"<strong>{html.escape(item.target)}</strong>: "
        f"{html.escape(item.before)} → {html.escape(item.after)}"
        f"<br>{html.escape(item.explanation)}"
        "</li>"
        for item in preview.effects
    )
    retained = ", ".join(preview.retained_evidence_ids) or "无"
    invalidated = ", ".join(preview.invalidated_attestation_ids) or "无"
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
        f"<ul>{effects or '<li>不会改变案例。</li>'}</ul>"
        f"<p><strong>保留的未受影响材料：</strong>{html.escape(retained)}</p>"
        f"<p><strong>将失效的负责人确认：</strong>{html.escape(invalidated)}</p>"
        "<p><strong>此预览本身不会修改案例：</strong>"
        f"{'是' if not preview.mutates_case else '否'}</p>"
        f"{confirmation}</section>"
    )


def _action_form(
    view: ReviewerGuidanceView,
    action_token: str | None,
) -> str:
    mutable = [
        item for item in view.available_actions if item.mutates_state
    ]
    if not action_token or not mutable or not view.summary.case_id:
        return ""
    options = "".join(
        f'<option value="{html.escape(item.action, quote=True)}">'
        f"{html.escape(item.title)} ({html.escape(item.action)})</option>"
        for item in mutable
    )
    obligations = "".join(
        f'<option value="{html.escape(item.obligation_id, quote=True)}">'
        f"{html.escape(item.check_item)} ({html.escape(item.obligation_id)})"
        "</option>"
        for item in view.requirement_comparisons
        if item.obligation_id != "AGM-PACKAGE"
    )
    return f"""
<form method="post" class="action-form">
<input type="hidden" name="action_token" value="{html.escape(action_token, quote=True)}">
<input type="hidden" name="role" value="{html.escape(view.actor.role, quote=True)}">
<label>操作
<select name="action" required>{options}</select>
</label>
<label>执行者（必须是真实身份）
<input name="actor" value="" placeholder="{html.escape(view.actor.actor, quote=True)}" required>
</label>
<label>受影响检查项（需要 scope 的操作使用）
<select name="obligation"><option value="">未选择</option>{obligations}</select>
</label>
<label>Evidence、attestation 或 finding ID（按操作需要）
<input name="object_id">
</label>
<label>事实依据或原因
<textarea name="reason" required></textarea>
</label>
<button type="submit">预览操作影响</button>
</form>"""


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
        f"<td><strong>{html.escape(item.check_item)}</strong>"
        f"<br><code>{html.escape(item.obligation_id)}</code></td>"
        f"<td>{html.escape(item.project_requirement)}</td>"
        f"<td>{html.escape(item.current_situation)}</td>"
        f'<td><span class="result result-{html.escape(item.result)}">'
        f"{html.escape(item.result_label)}</span>"
        f"<br><code>{html.escape(item.result)}</code>"
        f"{_trace_details(item)}</td>"
        "</tr>"
        for item in view.requirement_comparisons
    )
    available = "".join(
        '<article class="action-card available">'
        f"<h3>{html.escape(item.title)}</h3>"
        f"<p>{html.escape(item.description)}</p>"
        f"<p><strong>执行后：</strong>{html.escape(item.consequence)}</p>"
        f"<code>{html.escape(item.action)}</code>"
        "</article>"
        for item in view.available_actions
    )
    unavailable = "".join(
        '<article class="action-card unavailable" aria-disabled="true">'
        f"<h3>{html.escape(item.title)} <span>当前不可用</span></h3>"
        f"<p>{html.escape(item.description)}</p>"
        f"<p><strong>原因：</strong>{html.escape(item.reason)}</p>"
        f"<p><strong>可能需要的角色：</strong>"
        f"{html.escape(', '.join(item.next_actor_roles) or '无')}</p>"
        f"<code>{html.escape(item.action)}</code>"
        "</article>"
        for item in view.unavailable_actions
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
        f"{html.escape(item.plain_language)} "
        f"<code>{html.escape(item.finding_id)}</code>"
        "</li>"
        for item in view.diagnostics
    ) or "<li>当前没有 finding record。</li>"
    preview_html = (
        _action_preview_html(
            preview,
            action_token=action_token,
            form_values=form_values,
        )
        if preview
        else ""
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
.result-missing, .result-needs_update, .result-invalid, .result-blocked {{ color: #8c2818; }}
.result-meets_requirement, .result-verified, .result-closed {{ color: #17633e; }}
.actions {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(260px,1fr)); gap: .7rem; }}
.action-card {{ border: 1px solid #bac5d3; border-radius: 9px; padding: .8rem; }}
.action-card.unavailable {{ background: #f0f1f3; color: #4f5968; border-style: dashed; }}
.action-form label {{ display: block; font-weight: 700; margin-top: .7rem; }}
input, select, textarea {{ box-sizing: border-box; width: 100%; padding: .6rem; margin-top: .25rem; }}
button {{ padding: .65rem .9rem; margin-top: .8rem; cursor: pointer; }}
button.danger {{ background: #8c2818; color: white; border: 0; border-radius: 5px; margin-right: .6rem; }}
.preview {{ border: 3px solid #9b6a00; }}
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
<div class="metric"><strong>贡献 / Case</strong><br>{html.escape(summary.case_id or '无 Case（普通路径）')}</div>
<div class="metric"><strong>风险</strong><br>{html.escape(RISK_LABELS.get(summary.risk_level, summary.risk_level))}</div>
<div class="metric"><strong>本次路径</strong><br>{html.escape(summary.path_label)}</div>
<div class="metric"><strong>当前阶段</strong><br>{html.escape(summary.current_stage)}</div>
<div class="metric"><strong>阻断问题</strong><br>{summary.blocking_issue_count} 项</div>
<div class="metric"><strong>需要关注</strong><br>{summary.warning_count} 项</div>
<div class="metric"><strong>当前责任方</strong><br>{html.escape('、'.join(summary.current_responsible_parties) or '流程已结束')}</div>
<div class="metric"><strong>智能体范围</strong><br>{html.escape(summary.autonomy_profile)}</div>
</div>
<p><strong>Changed files：</strong>{html.escape(', '.join(summary.changed_files) or '无')}</p>
<p><strong>风险区域：</strong>{html.escape(', '.join(summary.risk_areas) or '无')}</p>
<small>Raw state: <code>{html.escape(summary.raw_state)}</code> · Readiness: <code>{html.escape(summary.raw_readiness)}</code></small>
</header>
<section>
<h2>治理流程导航器</h2>
<ol class="workflow">{workflow}</ol>
{('<p><strong>Repair 回路：</strong>' + html.escape(' → '.join(view.repair_loop)) + '</p>') if view.repair_loop else ''}
</section>
<section>
<h2>项目要求对比报告</h2>
<table>
<thead><tr><th>检查项</th><th>项目要求</th><th>当前情况</th><th>结果</th></tr></thead>
<tbody>{comparison_rows}</tbody>
</table>
</section>
<section><h2>问题与说明</h2><ul>{diagnostics}</ul>{explanations}</section>
{preview_html}
<section>
<h2>当前可执行操作</h2>
<p>这里列出合法选择及影响，不替维护者选择“正确答案”。后端仍会重新检查角色、状态和对象范围。</p>
<div class="actions">{available}</div>
{_action_form(view, action_token)}
</section>
<section>
<h2>当前不可执行操作</h2>
<p>不可用操作保留显示，以说明权限或流程原因。</p>
<div class="actions">{unavailable}</div>
</section>
<section id="technical">
<details class="technical-details"><summary>技术详情（默认折叠）</summary>
<pre>{_json_block(view.technical_details)}</pre>
</details>
</section>
<section class="authority"><h2>权限边界</h2><p>{html.escape(view.authority_notice)}</p></section>
</main></body></html>"""
