"""Compiled-state PR diagnostic projection; presentation cannot create routes."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..config import VNextConfig
from ..guidance.diagnostics import build_requirement_comparisons, obligation_presentation
from ..guidance.responsibility import derive_current_responsibility
from ..models import GovernanceCase, fingerprint
from ..state_machine import allowed_actions
from .models import ActionEffectBoundary, DiagnosticFinding, HostPlatformStatus, InspectionObject, PRDiagnosticView

RISK_TEXT = {"authentication": "该位置决定认证或权限何时生效；错误修改可能让已撤销的权限继续有效。", "documentation": "该位置是项目说明；需要检查文字准确性和链接。", "task_logic": "该位置影响应用的业务行为。", "test_strategy": "该位置影响测试和验证覆盖。"}
STATE_WORDS = {"missing": "未提供", "invalid": "材料格式或验证信息不完整", "stale": "对应旧版本", "expired": "已过有效期", "rejected": "验证未通过", "unbound": "尚未关联当前版本", "current": "对应当前版本"}
DISPLAY_TITLE = {"O-AGENT-SCOPE":"编码助手操作摘要", "O-HUMAN-ATTEST":"贡献者人工检查", "O-TEST-COMMAND":"测试记录", "O-ARTIFACT":"可复查的测试输出", "O-AUTH-IMPACT":"认证与权限影响说明", "O-SUMMARY":"修改说明", "O-CHANGED-FILES":"变更文件清单", "O-RATIONALE":"修改原因", "O-LIMITATIONS":"已知限制"}
ROUTE_TEXT = {"contributor_action_required": ("贡献者", "请补充或更新下列材料后，再提交维护者检查。"), "waiting_for_contributor_submission": ("贡献者", "当前无需你操作；下一步由贡献者提交维护者检查。"), "maintainer_focused_review": ("维护者", "材料已齐备，但涉及风险区域；请重点检查代码差异、测试和影响说明。"), "maintainer_review_available": ("维护者", "材料已齐备，可以开始维护者检查。"), "waiting_for_accountable_human": ("有权限的人类维护者", "等待确认已经检查当前版本和范围。"), "system_handled_no_action": ("系统已处理", "系统已经拒绝该越权操作；该操作未生效，你无需再次处理。"), "final_recommendation_recorded": ("无需额外处理", "AGM 最终审查建议已经记录；本页没有批准或合并平台 PR。"), "normal_pr_review": ("维护者", "检查文字准确性和链接即可，可以返回正常 PR 审查。"), "blocked_pending_repair": ("贡献者", "当前修复范围仍未完成，请按已记录的范围补充材料。")}

def _context(value: Any) -> dict[str, Any]: return dict(value) if isinstance(value, Mapping) else {}
def _lines(ctx: dict[str, Any], path: str) -> tuple[str, ...]:
    values = ctx.get("changed_line_ranges", {}).get(path, ()) if isinstance(ctx.get("changed_line_ranges"), Mapping) else ()
    return (str(values),) if isinstance(values, str) else tuple(str(v) for v in values)
def _evidence_state(items: list[Any], case: GovernanceCase) -> str:
    if not items: return "missing"
    states = {item.validity_state for item in items}
    for state in ("rejected", "expired", "stale", "invalid", "conflicting"):
        if state in states: return "invalid" if state in {"invalid", "conflicting"} else state
    if any(item.contribution_fingerprint != case.contribution_fingerprint and item.retained_for_contribution_fingerprint != case.contribution_fingerprint for item in items): return "unbound"
    return "current"
def _object(title: str, kind: str, summary: str, *, commit: str, content: str | None = None, href: str | None = None, source: str = "当前材料", freshness: str = "current", metadata: dict[str, Any] | None = None) -> InspectionObject:
    return InspectionObject(title, kind, summary, source, commit, fingerprint(content) if content else None, "available" if content or href else "unavailable", freshness, href, content, metadata or {})
def _route(case: GovernanceCase, config: VNextConfig, responsibility: Any, gaps: list[DiagnosticFinding]) -> tuple[str, list[str]]:
    legal = allowed_actions(config, state=case.state, role="maintainer")
    if any(item.result == "denied" for item in case.attempted_operations): return "system_handled_no_action", []
    if case.final_decision: return "final_recommendation_recorded", []
    roles = set(responsibility.primary_roles)
    if case.state == "awaiting_human_attestation" or roles == {"accountable_human"}: return "waiting_for_accountable_human", []
    if roles & {"contributor", "contributor_agent"}:
        if not gaps and case.state == "evidence_incomplete": return "waiting_for_contributor_submission", []
        return ("blocked_pending_repair" if case.state == "repair_requested" else "contributor_action_required"), []
    if case.state == "awaiting_maintainer_verification":
        return ("maintainer_focused_review" if case.overall_risk_level in {"high", "critical"} else "normal_pr_review"), legal
    if gaps: return "contributor_action_required", []
    return "normal_pr_review", []
def _actions(legal: list[str], route: str) -> tuple[ActionEffectBoundary, ...]:
    if route in {"normal_pr_review", "system_handled_no_action", "final_recommendation_recorded", "contributor_action_required", "blocked_pending_repair", "waiting_for_contributor_submission"}: return ()
    labels = {"verify_evidence": "确认这项检查没有问题", "request_repair": "请求贡献者补充"}
    return tuple(ActionEffectBoundary(labels[action], action, ("记录 AGM 中这项检查的结果。",), ("不会修改代码。", "不会执行 git merge。", "不会批准或合并 GitHub/GitLab PR。")) for action in legal if action in labels)

def compile_pr_diagnostic(*, governance_case: GovernanceCase, contribution: Any = None, policy_config: VNextConfig) -> PRDiagnosticView:
    case, ctx, commit = governance_case, _context(contribution), str(_context(contribution).get("commit_sha") or governance_case.base_commit)
    comparisons = build_requirement_comparisons(case); responsibility = derive_current_responsibility(case, comparisons)
    records: dict[str, list[Any]] = {item.obligation_id: [e for e in case.evidence if item.obligation_id in e.obligation_ids] for item in case.obligations}
    requirements: list[dict[str, Any]]=[]; observed: list[dict[str, Any]]=[]; gaps: list[DiagnosticFinding]=[]; objects: list[InspectionObject]=[]
    for obligation in case.obligations:
        title, plain = obligation_presentation(obligation); title=DISPLAY_TITLE.get(obligation.obligation_id,title); items=records[obligation.obligation_id]
        attested = obligation.type == "human_attestation" and any(a.status == "confirmed" and a.contribution_fingerprint == case.contribution_fingerprint for a in case.attestations)
        state = "current" if attested else _evidence_state(items, case)
        requirements.append({"title": title, "plain_requirement": plain, "obligation_ref": obligation.obligation_id, "state": state, "blocking": obligation.blocking})
        for item in items:
            observed.append({"title": title, "state": _evidence_state([item], case), "evidence_type": item.evidence_type, "bound_commit": item.contribution_fingerprint, "source": item.source_actor})
            objects.append(_object(title, "EvidenceArtifactInspectionObject", "可复查的项目材料。", commit=commit, content=str(item.value) if item.validity_state in {"valid", "verified"} else None, href=item.artifact_path, source=item.source_actor, freshness=_evidence_state([item], case), metadata={"evidence_id": item.id}))
        if state != "current": gaps.append(DiagnosticFinding(f"gap:{obligation.id}", "evidence_gap", obligation.severity, STATE_WORDS[state], plain, tuple(obligation.affected_scope), (), "对应当前版本", STATE_WORDS[state], "请贡献者补充或更新。", tuple(obligation.source_rule_ids), (obligation.obligation_id,), tuple(i.id for i in items), "contributor", "contributor_action_required", obligation.blocking, (obligation.id, *[i.id for i in items])))
    risks=[]
    for rule in case.matched_rules:
        risks.append(DiagnosticFinding(f"risk:{rule.id}", "risk_area", rule.risk_level, f"{ {'low':'低风险','medium':'中等风险','high':'高风险','critical':'严重风险'}.get(rule.risk_level,'风险区域')}：{', '.join(rule.affected_paths)}", RISK_TEXT.get(rule.zone,"该位置被项目规则识别为需要额外检查的区域。"), tuple(rule.affected_paths), tuple(line for p in rule.affected_paths for line in _lines(ctx,p)), "按项目要求检查", "已识别该风险区域", "", (rule.rule_id,), tuple(rule.obligation_ids), (), "maintainer", "inspect_risk", False, (rule.id,)))
    for path in case.changed_files:
        content = ctx.get("diff_hunks",{}).get(path) if isinstance(ctx.get("diff_hunks"),Mapping) else None
        objects.append(_object(f"相关修改：{path}", "DiffInspectionObject", "绑定当前版本的代码差异。" if content else "当前未提供可查看的代码差异。", commit=commit, content=content, freshness="current", metadata={"path":path,"line_ranges":_lines(ctx,path)}))
    for evidence in case.evidence:
        if evidence.evidence_type in {"test_command","test_explanation"}: objects.append(_object("测试记录", "TestInspectionObject", "可复查的测试命令和结果。", commit=evidence.contribution_fingerprint, content=str(evidence.value), href=evidence.artifact_path, source=evidence.source_actor, freshness=_evidence_state([evidence],case), metadata={"command":evidence.command,"environment":evidence.environment}))
    sidecar = ctx.get("sidecar_package") if isinstance(ctx.get("sidecar_package"), Mapping) else None
    if sidecar:
        digest = str(sidecar.get("digest", ""))
        objects.append(_object("证据包", "EvidenceArtifactInspectionObject", "本地 sidecar 证据包，绑定本次贡献。", commit=str(sidecar.get("contribution_fingerprint", commit)), href=f".agm-work/evidence_store/{digest}/package.json" if digest else None, freshness=str(sidecar.get("freshness", "current")), metadata={"package_digest":digest}))
    receipt = ctx.get("final_receipt") if isinstance(ctx.get("final_receipt"), Mapping) else None
    if receipt:
        objects.append(_object("最终审查建议回执", "EvidenceArtifactInspectionObject", "记录 AGM 最终审查建议及本地平台边界。", commit=commit, href=str(receipt.get("href")) or None, freshness="current", metadata={"receipt_digest":receipt.get("digest")}))
    activity = ctx.get("agent_activity") if isinstance(ctx.get("agent_activity"),Mapping) else {}; agent_state="verifiable" if activity.get("verified") else ("indirect" if activity else "not_detected")
    agent_message = "检测到可验证的编码 Agent 活动。" if agent_state=="verifiable" else ("发现可能与 Agent 有关的公开信号，但没有完整、可验证的 AGM 行动记录。" if agent_state=="indirect" else "未检测到可验证的 Agent 参与记录。该贡献可能主要由人工完成，也可能存在未被记录的辅助工具使用。")
    agent = {"state":agent_state,"status":"none" if agent_state=="not_detected" else agent_state,"message":agent_message,"type":activity.get("type"),"modified_file_count":len(activity.get("modified_files",[])),"commands":tuple(activity.get("commands",[])),"tests":tuple(activity.get("test_runs",[])),"used_other_tools":activity.get("used_other_tools"),"network":activity.get("network"),"current_version":bool(activity.get("verified"))}
    if activity: objects.append(_object("编码助手行动摘要", "AgentActivityInspectionObject", agent_message, commit=commit, content=activity.get("summary") or None, source="可验证 Agent 记录", freshness="current" if activity.get("verified") else "unbound", metadata={"type":activity.get("type"),"commands":activity.get("commands",[])}))
    declaration=ctx.get("contribution_declaration") if isinstance(ctx.get("contribution_declaration"),Mapping) else {}
    if declaration: objects.append(_object("贡献者声明", "ContributionDeclarationInspectionObject", "贡献者对工具使用和修改范围的声明。", commit=commit, content=str(declaration.get("summary","")) or None, source="贡献者", freshness="current"))
    if declaration.get("used_other_tools") is False and activity.get("used_other_tools") is True:
        gaps.append(DiagnosticFinding("agent-conflict","agent_record_conflict","high","编码助手记录与贡献者声明不一致","声明未使用其他助手，但可验证记录显示使用了其他助手或自动化工具。",tuple(case.changed_files),(),"两份记录一致","发现冲突","请贡献者核对并更正。",tuple(r.rule_id for r in case.matched_rules),tuple(o.obligation_id for o in case.obligations if o.evidence_type=="agent_action_scope"),(),"contributor","contributor_action_required",True,("contribution_declaration","agent_activity")))
    confirmed=[a for a in case.attestations if a.status=="confirmed"]; current_confirmation=next((a for a in confirmed if a.contribution_fingerprint==case.contribution_fingerprint),None)
    if current_confirmation: objects.append(_object("贡献者人工检查", "HumanConfirmationInspectionObject", "贡献者已确认检查当前版本和范围。", commit=commit, content=current_confirmation.statement, source=current_confirmation.actor, freshness="current"))
    human={"contributor_self_review":"对应当前版本" if current_confirmation else ("对应旧版本" if confirmed else "尚未确认"),"maintainer_review":"已完成必要检查" if case.maintainer_verifications else "尚未完成必要检查","final_recommendation":"已记录" if case.final_decision else "尚未记录"}
    route, legal = _route(case,policy_config,responsibility,gaps); owner,message=ROUTE_TEXT[route]
    status={"normal_pr_review":"可以按常规流程审查","maintainer_focused_review":"需要重点检查","maintainer_review_available":"可以开始维护者审查","contributor_action_required":"需要贡献者先处理","waiting_for_contributor_submission":"等待贡献者提交维护者检查","blocked_pending_repair":"存在阻断问题","waiting_for_accountable_human":"等待人类确认","system_handled_no_action":"系统已处理，无需额外操作","final_recommendation_recorded":"AGM 最终审查建议已记录"}[route]
    host=HostPlatformStatus(False,None,None,None,"not_performed","not_performed","not_performed","local absence of host-platform adapter",True)
    final={"status":"建议接受" if case.final_decision and case.final_decision.decision=="accept" else "尚未记录","decision":case.final_decision.decision if case.final_decision else None}
    return PRDiagnosticView(case.id,case.contribution_fingerprint,case.policy_snapshot.policy_fingerprint,status,{"summary":ctx.get("summary","当前没有额外变更说明。"),"files":tuple(case.changed_files),"line_ranges":{p:_lines(ctx,p) for p in case.changed_files}},tuple(risks),tuple(requirements),tuple(observed),tuple(gaps),agent,human,final,host,{"status":status,"blocking_gaps":len([g for g in gaps if g.blocking])},{"route":route,"owner":owner,"message":message},tuple(objects),_actions(legal,route),{"case_state":case.state,"responsible_side":tuple(responsibility.primary_roles),"gate_state":case.state,"legal_operations":tuple(legal),"risk_rule_refs":tuple(r.rule_id for r in case.matched_rules),"compiled_obligation_refs":tuple(o.obligation_id for o in case.obligations),"evidence_state_summary":{r["obligation_ref"]:r["state"] for r in requirements},"human_confirmation_state":human["contributor_self_review"],"agent_trace_state":agent_state,"route_derivation":{"route":route,"reason":responsibility.reason},"host_platform":host.to_dict()})
