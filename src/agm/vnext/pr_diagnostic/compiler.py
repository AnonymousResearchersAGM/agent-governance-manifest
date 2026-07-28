"""Deterministic projection: every diagnosis starts with compiled case state."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..evidence import evidence_set_fingerprint
from ..models import GovernanceCase, fingerprint
from .models import ActionEffectBoundary, DiagnosticFinding, InspectionObject, PRDiagnosticView


RISK_TEXT = {
    "authentication": "该位置决定认证或权限边界；错误修改可能让已撤销的权限继续有效。",
    "documentation": "该位置是项目使用说明；需要确认文字、命令和链接准确。",
    "task_logic": "该位置影响应用的业务行为。",
    "configuration": "该位置影响配置、依赖或部署兼容性。",
    "governance_runtime": "该位置影响本地 AGM 运行时的执行结果。",
}


def _context(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _current(evidence: Any, case: GovernanceCase) -> bool:
    return evidence.contribution_fingerprint == case.contribution_fingerprint and evidence.policy_fingerprint == case.policy_snapshot.policy_fingerprint and evidence.validity_state in {"valid", "verified", "unverified"}


def _lines(context: dict[str, Any], path: str) -> tuple[str, ...]:
    ranges = context.get("changed_line_ranges", {})
    value = ranges.get(path, ()) if isinstance(ranges, Mapping) else ()
    if isinstance(value, str): return (value,)
    return tuple(str(item) for item in value)


def _object(title: str, object_type: str, summary: str, *, commit: str, content: str | None = None, source: str = "当前案例材料", href: str | None = None, metadata: dict[str, Any] | None = None) -> InspectionObject:
    return InspectionObject(title, object_type, summary, source, commit, fingerprint(content) if content is not None else None, "available" if content or href else "unavailable", "current" if content or href else "unknown", href, content, metadata or {})


def compile_pr_diagnostic(*, governance_case: GovernanceCase, contribution: Any = None) -> PRDiagnosticView:
    """Project immutable compiled state without adding policy, risk, or obligations."""
    case, context = governance_case, _context(contribution)
    commit = str(context.get("commit_sha") or case.base_commit)
    requirements, observed, gaps, risk_findings, objects = [], [], [], [], []
    evidence_by_obligation: dict[str, list[Any]] = {}
    for item in case.evidence:
        for oid in item.obligation_ids: evidence_by_obligation.setdefault(oid, []).append(item)
    for matched in case.matched_rules:
        line_ranges = tuple(line for path in matched.affected_paths for line in _lines(context, path))
        risk_findings.append(DiagnosticFinding(
            finding_id=f"risk:{matched.id}", category="risk_area", severity=matched.risk_level,
            headline=f"{matched.risk_level.upper()}：{', '.join(matched.affected_paths)}",
            plain_language_explanation=RISK_TEXT.get(matched.zone, "此位置被项目风险规则命中，需要按项目要求检查相关材料。"),
            affected_files=tuple(matched.affected_paths), affected_line_ranges=line_ranges,
            expected_state="按项目规则提供并检查该区域的材料。", observed_state="已从当前贡献编译风险区域。", gap="",
            risk_rule_refs=(matched.rule_id,), obligation_refs=tuple(matched.obligation_ids), evidence_refs=(), responsibility="maintainer", recommended_route="inspect_risk", blocking=False, source_state_refs=(matched.id,)))
    for obligation in case.obligations:
        records = evidence_by_obligation.get(obligation.obligation_id, [])
        current = [item for item in records if _current(item, case)]
        current_confirmation = obligation.type == "human_attestation" and any(
            item.status == "confirmed"
            and item.contribution_fingerprint == case.contribution_fingerprint
            and item.policy_fingerprint == case.policy_snapshot.policy_fingerprint
            for item in case.attestations
        )
        state = "current" if current or current_confirmation else ("stale" if records else "missing")
        requirements.append({"title": obligation.description, "required_by": tuple(obligation.source_rule_ids), "obligation_ref": obligation.obligation_id, "blocking": obligation.blocking, "state": state})
        for item in records:
            observed.append({"title": obligation.description, "evidence_type": item.evidence_type, "state": "current" if item in current else "stale", "source": item.source_actor, "bound_commit": item.contribution_fingerprint, "artifact": item.artifact_path})
            objects.append(_object(f"{obligation.description}：材料", "EvidenceArtifactInspectionObject", "项目材料；不可用时不会生成内容。", commit=commit, content=str(item.value) if item in current else None, source=item.source_actor, href=item.artifact_path, metadata={"evidence_id": item.id, "evidence_type": item.evidence_type}))
        if state != "current":
            gaps.append(DiagnosticFinding(
                finding_id=f"gap:{obligation.id}", category="evidence_gap", severity=obligation.severity,
                headline=("材料属于旧版本" if state == "stale" else "缺少项目要求的材料"),
                plain_language_explanation=obligation.description, affected_files=tuple(obligation.affected_scope), affected_line_ranges=(),
                expected_state="当前提交应有可核对的材料。", observed_state="找到旧提交材料。" if state == "stale" else "当前未找到材料。",
                gap="请贡献者补充或更新后重新提交。", risk_rule_refs=tuple(obligation.source_rule_ids), obligation_refs=(obligation.obligation_id,), evidence_refs=tuple(item.id for item in records), responsibility="contributor", recommended_route="request_repair", blocking=obligation.blocking, source_state_refs=(obligation.id, *[item.id for item in records])))
    diff_hunks = context.get("diff_hunks", {})
    for path in case.changed_files:
        raw = diff_hunks.get(path) if isinstance(diff_hunks, Mapping) else None
        objects.append(_object(f"查看相关修改：{path}", "DiffInspectionObject", "绑定当前贡献的代码差异。" if raw else "当前未提供可查看的代码差异。", commit=commit, content=str(raw) if raw else None, source="贡献差异", metadata={"path": path, "line_ranges": _lines(context, path)}))
    for item in case.evidence:
        if item.evidence_type in {"test_command", "test_explanation"}:
            objects.append(_object("测试结果", "TestInspectionObject", "当前提交对应的测试命令和结果。" if _current(item, case) else "测试材料属于旧提交。", commit=commit, content=str(item.value) if _current(item, case) else None, source=item.source_actor, metadata={"command": item.command, "evidence_id": item.id}))
    activity = context.get("agent_activity") if isinstance(context.get("agent_activity"), Mapping) else {}
    agent_state = "verifiable" if activity.get("verified") else ("indirect" if activity else "none")
    agent_summary = {"status": agent_state, "message": "检测到可验证的编码 Agent 活动。" if agent_state == "verifiable" else ("发现可能与 Agent 有关的公开信号，但没有完整、可验证的 AGM 行动记录。" if agent_state == "indirect" else "未检测到可验证的 Agent 参与记录。该贡献可能主要由人工完成，也可能存在未被记录的辅助工具使用。"), "details": dict(activity)}
    if activity: objects.append(_object("Agent 行动摘要", "AgentActivityInspectionObject", agent_summary["message"], commit=commit, content=str(dict(activity)) if activity.get("verified") else None, source="Agent 活动记录"))
    declared = str(activity.get("declared_summary", "")).strip()
    observed_action = str(activity.get("observed_summary", "")).strip()
    if declared and observed_action and declared != observed_action:
        gaps.append(DiagnosticFinding(
            finding_id="agent-declaration-conflict", category="agent_record_conflict", severity="high",
            headline="Agent 声明与行动记录不一致", plain_language_explanation="贡献者声明和可验证行动记录描述了不同的操作范围，需要先核对。",
            affected_files=tuple(case.changed_files), affected_line_ranges=(), expected_state="声明应与可验证行动记录一致。", observed_state="发现相互矛盾的两份记录。", gap="请贡献者核对并更正行动范围说明。",
            risk_rule_refs=tuple(rule.rule_id for rule in case.matched_rules), obligation_refs=tuple(item.obligation_id for item in case.obligations if item.evidence_type == "agent_action_scope"), evidence_refs=(), responsibility="contributor", recommended_route="request_repair", blocking=True, source_state_refs=("agent_activity",)))
    denied = [item for item in case.attempted_operations if item.result == "denied"]
    if denied:
        risk_findings.append(DiagnosticFinding(
            finding_id="system-handled-operation", category="system_handled", severity="low", headline="系统已拒绝越权操作", plain_language_explanation="该操作没有生效，不需要维护者再次处理。", affected_files=(), affected_line_ranges=(), expected_state="操作必须由有权角色执行。", observed_state=f"已拒绝 {len(denied)} 次无权操作。", gap="", risk_rule_refs=(), obligation_refs=(), evidence_refs=(), responsibility="system", recommended_route="no_action", blocking=False, source_state_refs=tuple(item.id for item in denied)))
    current_attestations = [a for a in case.attestations if a.status == "confirmed" and a.contribution_fingerprint == case.contribution_fingerprint]
    self_review = current_attestations[-1] if current_attestations else None
    human = {"contributor_self_review": "已检查当前版本" if self_review else "贡献者尚未检查当前版本", "maintainer_review": "已完成必要检查" if case.maintainer_verifications else "尚未完成必要检查", "final_decision": "已记录 AGM 最终建议" if case.final_decision else "尚未作出最终决定"}
    if self_review: objects.append(_object("贡献者检查当前版本", "HumanConfirmationInspectionObject", "确认已绑定当前提交和检查范围。", commit=commit, content=self_review.statement, source=self_review.actor, metadata={"scope": self_review.reviewed_scope, "timestamp": self_review.timestamp}))
    if gaps:
        status, route = "需要贡献者先处理", "contributor"
    elif case.overall_risk_level in {"high", "critical"}:
        status, route = "可以开始重点审查", "maintainer"
    else:
        status, route = "可以按常规流程审查", "maintainer"
    boundaries = (ActionEffectBoundary("确认这项检查没有问题", "verify_evidence", ("记录该检查已完成。", "保留其他有效材料。"), ("不会修改代码。", "不会批准或合并 PR。", "不会作出最终接受决定。")), ActionEffectBoundary("请求贡献者补充", "request_repair", ("记录需要补充的范围。",), ("不会修改代码。", "不会执行 git merge。", "不会改变 GitHub/GitLab PR 状态。")))
    return PRDiagnosticView(case.id, case.contribution_fingerprint, case.policy_snapshot.policy_fingerprint, status, {"summary": context.get("summary", "当前没有额外变更说明。"), "files": tuple(case.changed_files), "line_ranges": {path: _lines(context, path) for path in case.changed_files}}, tuple(risk_findings), tuple(requirements), tuple(observed), tuple(gaps), agent_summary, human, {"status": status, "blocking_gaps": len([g for g in gaps if g.blocking])}, {"owner": route, "message": "请贡献者完成测试、检查当前 diff，并确认实际操作后重新提交。" if route == "contributor" else "请查看具体 diff、测试和影响说明。"}, tuple(objects), boundaries, {"derived_from": {"matched_rules": tuple(item.id for item in case.matched_rules), "compiled_obligations": tuple(item.id for item in case.obligations), "evidence_set_fingerprint": evidence_set_fingerprint(case.evidence), "case_state": case.state}, "host_platform": {"status": "未连接，未批准，未合并", "adapter": None}})
