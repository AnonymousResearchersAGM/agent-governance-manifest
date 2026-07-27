"""Compile evidence bindings into requirements and automatic check results."""

from __future__ import annotations

from typing import Any

from ..evidence import evidence_set_fingerprint
from ..guidance.models import RequirementComparison
from ..models import BoundEvidence, GovernanceCase
from .models import (
    AutomaticCheckResult,
    RequirementBrief,
    RequirementItem,
)


STATUS_LABELS = {
    "system_satisfied": "系统已确认",
    "provided_requires_human_judgment": "已提供，需要人判断",
    "missing": "缺少",
    "stale": "需要更新",
    "invalid": "无效",
    "awaiting_accountable_human": "等待负责人确认",
    "awaiting_independent_review": "等待独立维护者检查",
    "not_applicable": "本次不适用",
}

KEYS_BY_EVIDENCE_TYPE = {
    "contribution_summary": "change-summary",
    "changed_files": "changed-files",
    "rationale": "change-rationale",
    "test_explanation": "test-explanation",
    "test_command": "test-command-result",
    "artifact": "reviewable-artifact",
    "known_limitations": "known-limitations",
    "security_auth_impact": "auth-impact",
    "policy_impact": "governance-impact",
    "agent_action_scope": "agent-actions-delegation",
    "human_attestation": "accountable-human-confirmation",
    "independent_review": "independent-review",
}

SEMANTIC_JUDGMENT_TYPES = {
    "rationale",
    "known_limitations",
    "security_auth_impact",
    "policy_impact",
    "agent_action_scope",
}


def _requirement_status(
    case: GovernanceCase,
    comparison: RequirementComparison,
) -> str:
    obligation = case.obligation(comparison.obligation_id)
    if comparison.result == "not_applicable":
        return "not_applicable"
    if obligation.type == "human_attestation":
        if comparison.material_status in {"provided", "retained", "verified"}:
            return "system_satisfied"
        return "awaiting_accountable_human"
    if obligation.type == "maintainer_verification":
        if comparison.material_status in {"verified", "overridden"}:
            return "system_satisfied"
        return "awaiting_independent_review"
    if comparison.material_status == "missing":
        return "missing"
    if comparison.material_status == "stale":
        return "stale"
    if comparison.material_status == "invalid":
        return "invalid"
    if comparison.material_status in {"verified", "overridden"}:
        return "system_satisfied"
    needs_semantic_judgment = (
        obligation.evidence_type in SEMANTIC_JUDGMENT_TYPES
        and (
            comparison.workflow_status == "awaiting_revalidation"
            or case.overall_risk_level in {"high", "critical"}
            or any(
                item.obligation_id == "O-INDEPENDENT-REVIEW"
                for item in case.obligations
            )
        )
    )
    if needs_semantic_judgment:
        return "provided_requires_human_judgment"
    return "system_satisfied"


def compile_requirement_brief(
    case: GovernanceCase,
    comparisons: list[RequirementComparison],
) -> RequirementBrief:
    """Use the guidance comparison outcome instead of revalidating evidence."""

    items: list[RequirementItem] = []
    used_keys: dict[str, int] = {}
    for comparison in comparisons:
        obligation = case.obligation(comparison.obligation_id)
        status = _requirement_status(case, comparison)
        base_key = KEYS_BY_EVIDENCE_TYPE.get(
            obligation.evidence_type,
            f"project-requirement-{len(items) + 1}",
        )
        used_keys[base_key] = used_keys.get(base_key, 0) + 1
        key = (
            base_key
            if used_keys[base_key] == 1
            else f"{base_key}-{used_keys[base_key]}"
        )
        plain_status = {
            "system_satisfied": comparison.observed_plain,
            "provided_requires_human_judgment": (
                "材料已提供且结构有效；其内容是否与实际修改一致，需要人类判断。"
            ),
            "missing": "当前没有可用于这项要求的材料。",
            "stale": "现有材料对应旧版本；贡献侧需要更新后再继续。",
            "invalid": "现有材料未通过结构、范围或绑定检查。",
            "awaiting_accountable_human": (
                "需要人类负责人确认自己已审阅当前版本和明确范围。"
            ),
            "awaiting_independent_review": (
                "需要与贡献侧分离的维护者完成独立检查；完成检查不等于接受。"
            ),
            "not_applicable": "当前贡献不触发这项项目要求。",
        }[status]
        items.append(
            RequirementItem(
                requirement_key=key,
                display_title=comparison.display_name,
                status=status,
                status_label=STATUS_LABELS[status],
                plain_status=plain_status,
                blocking=comparison.blocking_requirement,
                trace_refs=(f"trace:requirement:{key}",),
            )
        )
    buckets = {
        status: tuple(item for item in items if item.status == status)
        for status in STATUS_LABELS
    }
    return RequirementBrief(
        total_required=len(items),
        items=tuple(items),
        system_satisfied=buckets["system_satisfied"],
        provided_requires_human_judgment=buckets[
            "provided_requires_human_judgment"
        ],
        missing=buckets["missing"],
        stale=buckets["stale"],
        invalid=buckets["invalid"],
        awaiting_accountable_human=buckets[
            "awaiting_accountable_human"
        ],
        awaiting_independent_review=buckets[
            "awaiting_independent_review"
        ],
        not_applicable=buckets["not_applicable"],
    )


def _evidence_for(
    case: GovernanceCase,
    evidence_type: str,
) -> list[BoundEvidence]:
    return [
        item
        for item in case.evidence
        if item.evidence_type == evidence_type
    ]


def _is_current(case: GovernanceCase, item: BoundEvidence) -> bool:
    return (
        item.contribution_fingerprint == case.contribution_fingerprint
        or (
            item.retained_for_contribution_fingerprint
            == case.contribution_fingerprint
            and bool(item.retention_reason)
        )
    )


def _check(
    check_type: str,
    title: str,
    status: str,
    result: str,
    *,
    evidence: tuple[str, ...] = (),
    limitations: tuple[str, ...] = (),
    human: bool = False,
) -> AutomaticCheckResult:
    return AutomaticCheckResult(
        check_type=check_type,
        display_title=title,
        status=status,
        plain_result=result,
        supporting_evidence=evidence,
        limitations=limitations,
        requires_human_action=human,
        trace_refs=(f"trace:automatic-check:{check_type}",),
    )


def compile_automatic_checks(
    case: GovernanceCase,
    requirements: RequirementBrief,
) -> tuple[AutomaticCheckResult, ...]:
    """Report formal checks without translating them into code correctness."""

    results: list[AutomaticCheckResult] = []
    bound = list(case.evidence)
    non_current = [item for item in bound if not _is_current(case, item)]
    if non_current:
        results.append(
            _check(
                "material_version_binding",
                "材料与当前修改版本一致",
                "problem",
                f"有 {len(non_current)} 份材料仍绑定旧版本。",
                evidence=("系统比较了材料记录与当前贡献版本绑定。",),
                human=True,
            )
        )
    elif bound:
        results.append(
            _check(
                "material_version_binding",
                "材料与当前修改版本一致",
                "confirmed",
                "所有已提供材料都绑定当前版本，或已记录为受影响范围外的保留材料。",
                evidence=("系统核对了当前版本绑定和受控保留记录。",),
            )
        )
    else:
        results.append(
            _check(
                "material_version_binding",
                "材料与当前修改版本一致",
                "not_applicable",
                "当前还没有可核对的材料。",
                limitations=("缺少材料由项目要求清单单独显示。",),
            )
        )

    test_required = any(
        item.evidence_type in {"test_command", "test_explanation"}
        for item in case.obligations
    )
    tests = _evidence_for(case, "test_command") + _evidence_for(
        case, "test_explanation"
    )
    complete_tests = [
        item
        for item in tests
        if bool(item.command or item.evidence_type == "test_explanation")
        and bool(str(item.value).strip())
        and item.validity_state in {"valid", "verified"}
    ]
    if complete_tests:
        commands = tuple(
            (
                f"已记录测试命令：{item.command}；"
                f"已记录结果：{item.value}"
            )
            if item.command
            else f"已记录测试说明和结果：{item.value}"
            for item in complete_tests
        )
        results.append(
            _check(
                "test_command_and_result",
                "测试是否包含命令和结果",
                "confirmed",
                "测试材料同时包含可检查的执行说明和结果记录。",
                evidence=commands,
                limitations=(
                    "系统确认的是记录完整性，不代表代码正确性，也不证明测试覆盖充分。",
                ),
            )
        )
    elif test_required:
        results.append(
            _check(
                "test_command_and_result",
                "测试是否包含命令和结果",
                "problem",
                "项目要求测试记录，但当前缺少完整的命令或结果。",
                human=True,
            )
        )
    else:
        results.append(
            _check(
                "test_command_and_result",
                "测试是否包含命令和结果",
                "not_applicable",
                "当前风险路径没有额外要求测试命令记录。",
            )
        )

    current_tests = [item for item in complete_tests if _is_current(case, item)]
    if current_tests:
        results.append(
            _check(
                "test_version_binding",
                "测试材料是否对应当前版本",
                "confirmed",
                "现有测试材料对应当前贡献版本或已按未受影响范围保留。",
                evidence=("系统核对了测试材料的版本绑定。",),
                limitations=("版本一致不代表测试覆盖了所有行为风险。",),
            )
        )
    elif test_required and tests:
        results.append(
            _check(
                "test_version_binding",
                "测试材料是否对应当前版本",
                "problem",
                "测试材料没有有效绑定当前贡献版本。",
                human=True,
            )
        )
    else:
        results.append(
            _check(
                "test_version_binding",
                "测试材料是否对应当前版本",
                "not_applicable",
                "当前没有需要核对版本绑定的测试材料。",
            )
        )

    expired = [
        item for item in bound if item.validity_state == "expired"
    ]
    if expired:
        results.append(
            _check(
                "evidence_freshness",
                "材料是否仍在有效期内",
                "problem",
                f"系统发现 {len(expired)} 份材料已过期。",
                human=True,
            )
        )
    elif bound:
        results.append(
            _check(
                "evidence_freshness",
                "材料是否仍在有效期内",
                "confirmed",
                "现有材料记录没有过期状态。",
                evidence=("系统读取了材料有效期和当前有效性状态。",),
            )
        )
    else:
        results.append(
            _check(
                "evidence_freshness",
                "材料是否仍在有效期内",
                "not_applicable",
                "当前没有可核对有效期的材料。",
            )
        )

    attestation_required = any(
        item.type == "human_attestation" for item in case.obligations
    )
    current_evidence_set = evidence_set_fingerprint(case.evidence)
    current_attestations = [
        item
        for item in case.attestations
        if item.status == "confirmed"
        and item.policy_fingerprint
        == case.policy_snapshot.policy_fingerprint
        and (
            (
                item.contribution_fingerprint
                == case.contribution_fingerprint
                and item.evidence_set_fingerprint == current_evidence_set
            )
            or (
                item.retained_for_contribution_fingerprint
                == case.contribution_fingerprint
                and bool(item.retention_reason)
            )
        )
    ]
    if current_attestations:
        results.append(
            _check(
                "attestation_version_binding",
                "负责人确认是否绑定当前版本",
                "confirmed",
                "负责人确认绑定当前贡献版本、规则快照和材料集合。",
                evidence=tuple(
                    f"{item.actor} 确认了 {len(item.reviewed_scope)} 个审阅范围"
                    for item in current_attestations
                ),
                limitations=("系统确认绑定关系，不代替对确认内容真实性的判断。",),
            )
        )
    elif attestation_required:
        results.append(
            _check(
                "attestation_version_binding",
                "负责人确认是否绑定当前版本",
                "problem",
                "项目要求负责人确认，但当前没有绑定当前版本的有效确认。",
                human=True,
            )
        )
    else:
        results.append(
            _check(
                "attestation_version_binding",
                "负责人确认是否绑定当前版本",
                "not_applicable",
                "当前风险路径不要求额外负责人确认。",
            )
        )

    changed_records = _evidence_for(case, "changed_files")
    matching_scope = [
        item
        for item in changed_records
        if isinstance(item.value, list)
        and set(map(str, item.value)) == set(case.changed_files)
        and item.validity_state in {"valid", "verified"}
    ]
    if matching_scope:
        results.append(
            _check(
                "changed_file_scope_match",
                "声明范围与实际变更文件一致",
                "confirmed",
                "材料中的变更文件清单与治理案例记录的实际范围一致。",
                evidence=(f"当前记录包含 {len(case.changed_files)} 个变更文件。",),
            )
        )
    elif changed_records:
        results.append(
            _check(
                "changed_file_scope_match",
                "声明范围与实际变更文件一致",
                "problem",
                "变更文件声明与治理案例记录不一致。",
                human=True,
            )
        )
    else:
        results.append(
            _check(
                "changed_file_scope_match",
                "声明范围与实际变更文件一致",
                "problem",
                "尚未提供变更文件清单，系统无法完成一致性核对。",
                human=True,
            )
        )

    agent_used = (
        case.autonomy_profile != "human_direct"
        or any(
            item.obligation_id == "O-AGENT-SCOPE"
            for item in case.obligations
        )
        or any(
            item.actor_role == "contributor_agent"
            for item in case.attempted_operations
        )
    )
    results.append(
        _check(
            "agent_involvement",
            "是否记录了智能体参与",
            "confirmed",
            (
                "治理案例明确记录为智能体参与路径。"
                if agent_used
                else "治理案例采用直接人类贡献配置，未声明智能体参与。"
            ),
            evidence=(f"记录的参与配置：{case.autonomy_profile}",),
            limitations=(
                "AGM 只呈现治理记录和声明，不是智能体使用检测器。",
            ),
        )
    )

    scope_records = _evidence_for(case, "agent_action_scope")
    if not agent_used:
        delegation_status = _check(
            "recorded_delegation",
            "是否记录继续委派",
            "not_applicable",
            "当前案例未声明智能体参与，因此不触发委派说明要求。",
        )
    elif not scope_records:
        delegation_status = _check(
            "recorded_delegation",
            "是否记录继续委派",
            "problem",
            "智能体参与路径缺少行动与委派说明。",
            human=True,
        )
    else:
        delegation_status = _check(
            "recorded_delegation",
            "是否记录继续委派",
            "confirmed",
            "系统确认已提供行动与委派声明。",
            evidence=("已存在智能体行动范围材料。",),
            limitations=("声明不是系统观察到的完整智能体行动日志。",),
        )
    results.append(delegation_status)

    denied = [
        item
        for item in case.attempted_operations
        if item.result == "denied"
    ]
    if denied:
        unchanged = all(not item.state_changed for item in denied)
        results.append(
            _check(
                "authority_boundary",
                "是否存在越权操作",
                "problem",
                (
                    f"系统拒绝了 {len(denied)} 次越权操作；"
                    + ("治理状态没有变化。" if unchanged else "请核对状态审计。")
                ),
                evidence=tuple(
                    f"{item.actor_role} 尝试执行受限的维护者侧操作"
                    for item in denied
                ),
                limitations=("被拒绝事件不会替代对当前贡献材料的正常检查。",),
            )
        )
    else:
        results.append(
            _check(
                "authority_boundary",
                "是否存在越权操作",
                "confirmed",
                "当前案例审计记录中没有被拒绝的越权操作。",
                limitations=("结论范围仅限 AGM 已记录的操作。",),
            )
        )

    incomplete = (
        len(requirements.missing)
        + len(requirements.stale)
        + len(requirements.invalid)
        + len(requirements.awaiting_accountable_human)
    )
    if incomplete:
        results.append(
            _check(
                "structural_obligations",
                "结构性项目要求是否满足",
                "problem",
                f"还有 {incomplete} 项材料或负责人确认未达到当前要求。",
                human=True,
            )
        )
    else:
        results.append(
            _check(
                "structural_obligations",
                "结构性项目要求是否满足",
                "confirmed",
                "当前材料的结构、必填范围和前置确认已达到进入人类判断的条件。",
                limitations=(
                    "结构满足不等于语义正确，也不等于贡献已被项目接受。",
                ),
            )
        )
    semantic_items = (
        requirements.provided_requires_human_judgment
        + requirements.awaiting_independent_review
    )
    if semantic_items:
        results.append(
            _check(
                "semantic_declaration_consistency",
                "声明内容是否与实际修改一致",
                "needs_human_judgment",
                (
                    "系统已完成结构和绑定检查，但以下内容仍需人类语义判断："
                    + "、".join(
                        item.display_title for item in semantic_items
                    )
                    + "。"
                ),
                evidence=tuple(
                    f"已准备：{item.display_title}"
                    for item in semantic_items
                ),
                limitations=(
                    "系统不会把文件路径推断、贡献者声明或智能体自述当作代码语义证明。",
                ),
                human=True,
            )
        )
    return tuple(results)
