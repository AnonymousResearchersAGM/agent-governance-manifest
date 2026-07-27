"""Compile evidence bindings into requirements and automatic check results."""

from __future__ import annotations

from typing import Any

from ..evidence import evidence_set_fingerprint
from ..guidance.models import RequirementComparison
from ..models import BoundEvidence, GovernanceCase
from .models import (
    AutomaticCheckResult,
    BriefSemanticState,
    RequirementBrief,
    RequirementItem,
    WorkOwner,
)


SEMANTIC_STATUS_LABELS = {
    "material_available": "材料已提供",
    "structure_valid": "形式要求已满足",
    "version_bound": "已对应当前版本",
    "system_checked": "材料与版本已核对",
    "human_review_required": "材料齐备，内容待人工检查",
    "human_verified": "维护者已完成检查",
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


def _semantic_status(
    case: GovernanceCase,
    comparison: RequirementComparison,
    compatibility_status: str,
) -> str:
    obligation = case.obligation(comparison.obligation_id)
    if compatibility_status == "provided_requires_human_judgment":
        return BriefSemanticState.HUMAN_REVIEW_REQUIRED.value
    if compatibility_status == "system_satisfied":
        if (
            comparison.material_status in {"verified", "overridden"}
            or (
                obligation.type == "maintainer_verification"
                and comparison.result in {"verified", "overridden"}
            )
        ):
            return BriefSemanticState.HUMAN_VERIFIED.value
        return BriefSemanticState.SYSTEM_CHECKED.value
    return compatibility_status


def _semantic_states(
    case: GovernanceCase,
    comparison: RequirementComparison,
    semantic_status: str,
) -> tuple[str, ...]:
    """Describe formal checks without claiming semantic content validity."""

    obligation = case.obligation(comparison.obligation_id)
    states: list[str] = []
    material_present = comparison.material_status in {
        "provided",
        "retained",
        "verified",
        "overridden",
    }
    if material_present:
        states.extend(
            [
                BriefSemanticState.MATERIAL_AVAILABLE.value,
                BriefSemanticState.STRUCTURE_VALID.value,
            ]
        )
        if obligation.type != "maintainer_verification":
            states.append(BriefSemanticState.VERSION_BOUND.value)
    if semantic_status == "system_checked":
        states.append(BriefSemanticState.SYSTEM_CHECKED.value)
    elif semantic_status == "human_review_required":
        states.append(BriefSemanticState.HUMAN_REVIEW_REQUIRED.value)
    elif semantic_status == "human_verified":
        states.append(BriefSemanticState.HUMAN_VERIFIED.value)
    return tuple(dict.fromkeys(states))


def _owner_for_requirement(status: str) -> WorkOwner:
    if status in {"missing", "stale", "invalid"}:
        return WorkOwner.CONTRIBUTION_SIDE
    if status == "awaiting_accountable_human":
        return WorkOwner.ACCOUNTABLE_HUMAN
    if status in {
        "human_review_required",
        "awaiting_independent_review",
    }:
        return WorkOwner.MAINTAINER
    return WorkOwner.SYSTEM


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
        semantic_status = _semantic_status(case, comparison, status)
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
            "system_checked": (
                "材料已提供，形式要求有效且对应当前版本；"
                "这只表示系统完成了可自动执行的核对，不表示内容正确。"
            ),
            "human_review_required": (
                "材料已提供，形式要求有效且对应当前版本；"
                "内容是否与实际修改一致仍需维护者判断。"
            ),
            "human_verified": (
                "具备权限的维护者已完成本项检查；"
                "检查完成不等于贡献已经被最终接受。"
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
        }[semantic_status]
        items.append(
            RequirementItem(
                requirement_key=key,
                display_title=comparison.display_name,
                status=status,
                status_label=SEMANTIC_STATUS_LABELS[semantic_status],
                plain_status=plain_status,
                blocking=comparison.currently_blocks_progression,
                trace_refs=(f"trace:requirement:{key}",),
                semantic_states=_semantic_states(
                    case, comparison, semantic_status
                ),
                owner=_owner_for_requirement(semantic_status),
                semantic_status=semantic_status,
            )
        )
    buckets = {
        status: tuple(item for item in items if item.status == status)
        for status in {
            "system_satisfied",
            "provided_requires_human_judgment",
            "missing",
            "stale",
            "invalid",
            "awaiting_accountable_human",
            "awaiting_independent_review",
            "not_applicable",
        }
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
    policy_required: bool = False,
    blocking: bool = False,
    requirement_refs: tuple[str, ...] = (),
    informational_only: bool = False,
    owner: WorkOwner = WorkOwner.SYSTEM,
    system_handled: bool = False,
) -> AutomaticCheckResult:
    compatibility_status = {
        "system_checked": "confirmed",
        "human_review_required": "needs_human_judgment",
        "system_handled": "problem",
        "informational": "not_applicable",
    }.get(status, status)
    return AutomaticCheckResult(
        check_type=check_type,
        display_title=title,
        status=compatibility_status,
        plain_result=result,
        supporting_evidence=evidence,
        limitations=limitations,
        requires_human_action=human,
        trace_refs=(f"trace:automatic-check:{check_type}",),
        policy_required=policy_required,
        blocking=blocking,
        requirement_refs=requirement_refs,
        informational_only=informational_only,
        owner=owner,
        system_handled=system_handled,
        semantic_status=status,
    )


def _requirement_refs(
    requirements: RequirementBrief,
    *evidence_types: str,
) -> tuple[str, ...]:
    keys = {
        KEYS_BY_EVIDENCE_TYPE[item]
        for item in evidence_types
        if item in KEYS_BY_EVIDENCE_TYPE
    }
    return tuple(
        item.requirement_key
        for item in requirements.items
        if any(
            item.requirement_key == key
            or item.requirement_key.startswith(f"{key}-")
            for key in keys
        )
    )


def compile_automatic_checks(
    case: GovernanceCase,
    requirements: RequirementBrief,
) -> tuple[AutomaticCheckResult, ...]:
    """Report formal checks without translating them into code correctness."""

    results: list[AutomaticCheckResult] = []
    canonical_obligation_ids = {
        item.obligation_id for item in case.obligations
    }
    bound = [
        item
        for item in case.evidence
        if canonical_obligation_ids.intersection(item.obligation_ids)
    ]
    non_current = [item for item in bound if not _is_current(case, item)]
    all_requirement_refs = tuple(
        item.requirement_key for item in requirements.items
    )
    if non_current:
        results.append(
            _check(
                "material_version_binding",
                "材料与当前修改版本一致",
                "problem",
                f"有 {len(non_current)} 份材料仍绑定旧版本。",
                evidence=("系统比较了材料记录与当前贡献版本绑定。",),
                human=True,
                policy_required=True,
                blocking=True,
                requirement_refs=all_requirement_refs,
                owner=WorkOwner.CONTRIBUTION_SIDE,
            )
        )
    elif bound:
        results.append(
            _check(
                "material_version_binding",
                "材料与当前修改版本一致",
                "system_checked",
                "所有已提供材料都绑定当前版本，或已记录为受影响范围外的保留材料。",
                evidence=("系统核对了当前版本绑定和受控保留记录。",),
                policy_required=True,
                requirement_refs=all_requirement_refs,
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
    test_refs = _requirement_refs(
        requirements, "test_command", "test_explanation"
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
                "system_checked",
                "测试材料同时包含可检查的执行说明和结果记录。",
                evidence=commands,
                limitations=(
                    "系统确认的是记录完整性，不代表代码正确性，也不证明测试覆盖充分。",
                ),
                policy_required=test_required,
                requirement_refs=test_refs,
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
                policy_required=True,
                blocking=True,
                requirement_refs=test_refs,
                owner=WorkOwner.CONTRIBUTION_SIDE,
            )
        )
    else:
        results.append(
            _check(
                "test_command_and_result",
                "测试是否包含命令和结果",
                "not_applicable",
                "当前风险路径没有额外要求测试命令记录。",
                informational_only=True,
            )
        )

    current_tests = [item for item in complete_tests if _is_current(case, item)]
    if current_tests:
        results.append(
            _check(
                "test_version_binding",
                "测试材料是否对应当前版本",
                "system_checked",
                "现有测试材料对应当前贡献版本或已按未受影响范围保留。",
                evidence=("系统核对了测试材料的版本绑定。",),
                limitations=("版本一致不代表测试覆盖了所有行为风险。",),
                policy_required=test_required,
                requirement_refs=test_refs,
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
                policy_required=True,
                blocking=True,
                requirement_refs=test_refs,
                owner=WorkOwner.CONTRIBUTION_SIDE,
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
                policy_required=True,
                blocking=True,
                requirement_refs=all_requirement_refs,
                owner=WorkOwner.CONTRIBUTION_SIDE,
            )
        )
    elif bound:
        results.append(
            _check(
                "evidence_freshness",
                "材料是否仍在有效期内",
                "system_checked",
                "现有材料记录没有过期状态。",
                evidence=("系统读取了材料有效期和当前有效性状态。",),
                policy_required=True,
                requirement_refs=all_requirement_refs,
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
    attestation_refs = _requirement_refs(
        requirements, "human_attestation"
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
                "system_checked",
                "负责人确认绑定当前贡献版本、规则快照和材料集合。",
                evidence=tuple(
                    f"{item.actor} 确认了 {len(item.reviewed_scope)} 个审阅范围"
                    for item in current_attestations
                ),
                limitations=("系统确认绑定关系，不代替对确认内容真实性的判断。",),
                policy_required=attestation_required,
                requirement_refs=attestation_refs,
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
                policy_required=True,
                blocking=True,
                requirement_refs=attestation_refs,
                owner=WorkOwner.ACCOUNTABLE_HUMAN,
            )
        )
    else:
        results.append(
            _check(
                "attestation_version_binding",
                "负责人确认是否绑定当前版本",
                "not_applicable",
                "当前风险路径不要求额外负责人确认。",
                informational_only=True,
            )
        )

    changed_records = _evidence_for(case, "changed_files")
    changed_files_required = any(
        item.evidence_type == "changed_files" for item in case.obligations
    )
    changed_file_refs = _requirement_refs(
        requirements, "changed_files"
    )
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
                "system_checked",
                "材料中的变更文件清单与治理案例记录的实际范围一致。",
                evidence=(f"当前记录包含 {len(case.changed_files)} 个变更文件。",),
                policy_required=changed_files_required,
                requirement_refs=changed_file_refs,
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
                policy_required=changed_files_required,
                blocking=changed_files_required,
                requirement_refs=changed_file_refs,
                owner=WorkOwner.CONTRIBUTION_SIDE,
            )
        )
    elif changed_files_required:
        results.append(
            _check(
                "changed_file_scope_match",
                "声明范围与实际变更文件一致",
                "problem",
                "尚未提供变更文件清单，系统无法完成一致性核对。",
                human=True,
                policy_required=True,
                blocking=True,
                requirement_refs=changed_file_refs,
                owner=WorkOwner.CONTRIBUTION_SIDE,
            )
        )
    else:
        results.append(
            _check(
                "changed_file_scope_match",
                "声明范围与实际变更文件一致",
                "not_applicable",
                "当前项目规则没有要求单独提交变更文件清单。",
                informational_only=True,
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
    agent_scope_required = any(
        item.obligation_id == "O-AGENT-SCOPE"
        for item in case.obligations
    )
    agent_scope_refs = _requirement_refs(
        requirements, "agent_action_scope"
    )
    results.append(
        _check(
            "agent_involvement",
            "是否记录了智能体参与",
            "informational",
            (
                "治理案例明确记录为智能体参与路径。"
                if agent_used
                else "治理案例采用直接人类贡献配置，未声明智能体参与。"
            ),
            evidence=("系统读取了案例中记录的参与方式。",),
            limitations=(
                "AGM 只呈现治理记录和声明，不是智能体使用检测器。",
            ),
            policy_required=agent_scope_required,
            requirement_refs=agent_scope_refs,
            informational_only=True,
        )
    )

    scope_records = _evidence_for(case, "agent_action_scope")
    if not agent_used:
        delegation_status = _check(
            "recorded_delegation",
            "是否记录继续委派",
            "not_applicable",
            "当前案例未声明智能体参与，因此不触发委派说明要求。",
            policy_required=agent_scope_required,
            requirement_refs=agent_scope_refs,
            informational_only=True,
        )
    elif not scope_records and agent_scope_required:
        delegation_status = _check(
            "recorded_delegation",
            "是否记录继续委派",
            "problem",
            "项目当前规则要求智能体行动与委派说明，但材料尚未提供。",
            human=True,
            policy_required=True,
            blocking=True,
            requirement_refs=agent_scope_refs,
            owner=WorkOwner.CONTRIBUTION_SIDE,
        )
    elif not scope_records:
        delegation_status = _check(
            "recorded_delegation",
            "是否记录继续委派",
            "informational",
            (
                "本次贡献记录了智能体参与，但当前项目规则未要求单独提交"
                "智能体行动与委派说明。"
            ),
            limitations=(
                "这是一项附加信息，不构成缺失材料、finding 或流程阻断。",
            ),
            informational_only=True,
        )
    else:
        delegation_status = _check(
            "recorded_delegation",
            "是否记录继续委派",
            "system_checked",
            "行动与委派声明材料已提供，并通过形式与版本核对。",
            evidence=("已存在智能体行动范围材料。",),
            limitations=("声明不是系统观察到的完整智能体行动日志。",),
            policy_required=agent_scope_required,
            requirement_refs=agent_scope_refs,
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
                "system_handled",
                (
                    f"系统拒绝了 {len(denied)} 次越权操作；"
                    + ("治理状态没有变化。" if unchanged else "请核对状态审计。")
                ),
                evidence=tuple(
                    "贡献侧智能体尝试执行受限的维护者侧操作"
                    for item in denied
                ),
                limitations=("被拒绝事件不会替代对当前贡献材料的正常检查。",),
                informational_only=False,
                owner=WorkOwner.SYSTEM,
                system_handled=True,
            )
        )
    else:
        results.append(
            _check(
                "authority_boundary",
                "是否存在越权操作",
                "system_checked",
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
                policy_required=True,
                blocking=True,
                requirement_refs=tuple(
                    item.requirement_key
                    for item in (
                        requirements.missing
                        + requirements.stale
                        + requirements.invalid
                        + requirements.awaiting_accountable_human
                    )
                ),
                owner=(
                    WorkOwner.ACCOUNTABLE_HUMAN
                    if requirements.awaiting_accountable_human
                    and not (
                        requirements.missing
                        or requirements.stale
                        or requirements.invalid
                    )
                    else WorkOwner.CONTRIBUTION_SIDE
                ),
            )
        )
    else:
        results.append(
            _check(
                "structural_obligations",
                "结构性项目要求是否满足",
                "system_checked",
                "当前材料的结构、必填范围和前置确认已达到进入人类判断的条件。",
                limitations=(
                    "结构满足不等于语义正确，也不等于贡献已被项目接受。",
                ),
                policy_required=True,
                requirement_refs=all_requirement_refs,
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
                "human_review_required",
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
                policy_required=True,
                blocking=any(item.blocking for item in semantic_items),
                requirement_refs=tuple(
                    item.requirement_key for item in semantic_items
                ),
                owner=WorkOwner.MAINTAINER,
            )
        )
    return tuple(results)
