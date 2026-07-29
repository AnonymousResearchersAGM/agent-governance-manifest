"""Compile a PR diagnostic only from canonical and digest-verified sources."""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ..config import VNextConfig
from ..guidance.diagnostics import build_requirement_comparisons, obligation_presentation
from ..guidance.responsibility import derive_current_responsibility
from ..models import GovernanceCase, fingerprint
from ..state_machine import allowed_actions
from .models import ActionEffectBoundary, DiagnosticFinding, HostPlatformStatus, InspectionObject, PRDiagnosticView
from .sidecar import SidecarEvidenceStore
from .trusted_sources import TrustedDiagnosticEvidenceResolver, TrustedArtifact, select_obligation_evidence

RISK_TEXT={"authentication":"该位置决定认证或权限何时生效；错误修改可能让已撤销的权限继续有效。","documentation":"该位置是项目说明；需要检查文字准确性和链接。","task_logic":"该位置影响应用的业务行为。","test_strategy":"该位置影响测试和验证覆盖。"}
STATE_WORDS={"missing":"未提供","invalid":"材料格式或验证信息不完整","stale":"对应旧版本","expired":"已过有效期","rejected":"验证未通过","unbound":"尚未关联当前版本","current":"对应当前版本"}
DISPLAY_TITLE={"O-AGENT-SCOPE":"编码助手操作摘要","O-HUMAN-ATTEST":"贡献者人工检查","O-TEST-COMMAND":"测试记录","O-ARTIFACT":"可复查的测试输出","O-AUTH-IMPACT":"认证与权限影响说明","O-SUMMARY":"修改说明","O-CHANGED-FILES":"变更文件清单","O-RATIONALE":"修改原因","O-LIMITATIONS":"已知限制"}
ROUTE_TEXT={"contributor_action_required":("贡献者","请补充或更新下列材料后，再提交维护者检查。"),"waiting_for_contributor_submission":("贡献者","当前无需你操作；下一步由贡献者提交维护者检查。"),"maintainer_focused_review":("维护者","材料已齐备，但涉及风险区域；请重点检查代码差异、测试和影响说明。"),"maintainer_review_available":("维护者","材料已齐备，可以开始维护者检查。"),"waiting_for_accountable_human":("有权限的人类维护者","等待确认已经检查当前版本和范围。"),"system_handled_no_action":("系统已处理","系统已经拒绝该越权操作；该操作未生效，你无需再次处理。"),"final_recommendation_recorded":("无需额外处理","AGM 最终审查建议已经记录；本页没有批准或合并平台 PR。"),"normal_pr_review":("维护者","检查文字准确性和链接即可，可以返回正常 PR 审查。"),"blocked_pending_repair":("贡献者","当前修复范围仍未完成，请按已记录的范围补充材料。")}

def _ctx(value:Any)->dict[str,Any]: return dict(value) if isinstance(value,Mapping) else {}
def _lines(ctx:dict[str,Any], path:str)->tuple[str,...]:
    value=ctx.get("changed_line_ranges",{}).get(path,()) if isinstance(ctx.get("changed_line_ranges"),Mapping) else ()
    return (str(value),) if isinstance(value,str) else tuple(str(item) for item in value)
def _json(content:str)->dict[str,Any]:
    try: value=json.loads(content); return value if isinstance(value,dict) else {}
    except json.JSONDecodeError: return {}

def _object(*, object_id:str,title:str,kind:str,summary:str,case:GovernanceCase,content:str|None=None,head_commit:str|None=None,package_digest:str|None=None,artifact_route:str|None=None,source:str="当前材料",freshness:str="current",metadata:dict[str,Any]|None=None)->InspectionObject:
    return InspectionObject(object_id=object_id,title=title,object_type=kind,plain_language_summary=summary,source=source,base_commit_sha=case.base_commit,head_commit_sha=head_commit,contribution_fingerprint=case.contribution_fingerprint,content_digest=fingerprint(content) if content is not None else None,evidence_package_digest=package_digest,availability="available" if content is not None or artifact_route else "unavailable",freshness=freshness,artifact_route=artifact_route,inline_content=content,technical_metadata=metadata or {})

def _trusted_object(case:GovernanceCase,item:TrustedArtifact,kind:str,summary:str)->InspectionObject:
    return _object(object_id=item.artifact_id,title=item.title,kind=kind,summary=summary,case=case,content=item.content,head_commit=item.head_commit_sha,package_digest=item.package_digest,source="已验证 sidecar 材料",metadata={"artifact_type":item.artifact_type,"media_type":item.media_type})

def _route(case:GovernanceCase,config:VNextConfig,responsibility:Any,gaps:list[DiagnosticFinding])->tuple[str,list[str]]:
    legal=allowed_actions(config,state=case.state,role="maintainer")
    if case.final_decision:return "final_recommendation_recorded",[]
    roles=set(responsibility.primary_roles)
    if case.state=="awaiting_human_attestation" or roles=={"accountable_human"}:return "waiting_for_accountable_human",[]
    if roles & {"contributor","contributor_agent"}:
        if not gaps and case.state=="evidence_incomplete":return "waiting_for_contributor_submission",[]
        return ("blocked_pending_repair" if case.state=="repair_requested" else "contributor_action_required"),[]
    if case.state=="awaiting_maintainer_verification":return ("maintainer_focused_review" if case.overall_risk_level in {"high","critical"} else "normal_pr_review"),legal
    if gaps:return "contributor_action_required",[]
    if any(item.result=="denied" for item in case.attempted_operations) and not legal:return "system_handled_no_action",[]
    return "normal_pr_review",[]
def _actions(legal:list[str],route:str)->tuple[ActionEffectBoundary,...]:
    if route not in {"maintainer_focused_review","maintainer_review_available"}:return ()
    labels={"verify_evidence":"确认这项检查没有问题","request_repair":"请求贡献者补充"}
    return tuple(ActionEffectBoundary(labels[action],action,("记录 AGM 中这项检查的结果。",),("不会修改代码。","不会执行 git merge。","不会批准或合并 GitHub/GitLab PR。")) for action in legal if action in labels)

def compile_pr_diagnostic(*,governance_case:GovernanceCase,contribution:Any=None,policy_config:VNextConfig,evidence_store:SidecarEvidenceStore|None=None)->PRDiagnosticView:
    case,ctx=governance_case,_ctx(contribution)
    trusted=TrustedDiagnosticEvidenceResolver(evidence_store).resolve(case) if evidence_store else None
    comparisons=build_requirement_comparisons(case); responsibility=derive_current_responsibility(case,comparisons)
    requirements:list[dict[str,Any]]=[]; observed:list[dict[str,Any]]=[]; gaps:list[DiagnosticFinding]=[]; objects:list[InspectionObject]=[]
    for obligation in case.obligations:
        title,plain=obligation_presentation(obligation);title=DISPLAY_TITLE.get(obligation.obligation_id,title)
        if obligation.type=="human_attestation":
            current=any(item.contribution_fingerprint==case.contribution_fingerprint and item.status=="confirmed" for item in (trusted.human_confirmations if trusted else case.attestations))
            old=any(item.status=="confirmed" for item in (trusted.human_confirmations if trusted else case.attestations))
            state="current" if current else ("stale" if old else "missing")
            selected=()
        else: state,selected=select_obligation_evidence(case,obligation.obligation_id)
        requirements.append({"title":title,"plain_requirement":plain,"obligation_ref":obligation.obligation_id,"state":state,"blocking":obligation.blocking})
        for item in selected:
            observed.append({"title":title,"state":state,"evidence_type":item.evidence_type,"contribution_fingerprint":item.contribution_fingerprint,"source":item.source_actor})
            objects.append(_object(object_id=item.id,title=title,kind="EvidenceArtifactInspectionObject",summary="来自当前案例的可复查材料。",case=case,content=str(item.value) if state=="current" else None,source=item.source_actor,freshness=state,metadata={"evidence_id":item.id}))
        if state!="current":gaps.append(DiagnosticFinding(f"gap:{obligation.id}","evidence_gap",obligation.severity,STATE_WORDS[state],plain,tuple(obligation.affected_scope),(),"对应当前版本",STATE_WORDS[state],"请贡献者补充或更新。",tuple(obligation.source_rule_ids),(obligation.obligation_id,),tuple(item.id for item in selected),"contributor","contributor_action_required",obligation.blocking,(obligation.id,*[item.id for item in selected])))
    risks=[]
    for rule in case.matched_rules:risks.append(DiagnosticFinding(f"risk:{rule.id}","risk_area",rule.risk_level,f"{ {'low':'低风险','medium':'中等风险','high':'较高风险','critical':'严重风险'}.get(rule.risk_level,'风险区域')}：{', '.join(rule.affected_paths)}",RISK_TEXT.get(rule.zone,"该位置被项目规则识别为需要额外检查的区域。"),tuple(rule.affected_paths),tuple(line for path in rule.affected_paths for line in _lines(ctx,path)),"按项目要求检查","已识别该风险区域","",(rule.rule_id,),tuple(rule.obligation_ids),(),"maintainer","inspect_risk",False,(rule.id,)))
    if trusted:
        for item in trusted.diffs: objects.append(_trusted_object(case,item,"DiffInspectionObject","绑定当前贡献的代码差异。"))
        for item in trusted.tests: objects.append(_trusted_object(case,item,"TestInspectionObject","可复查的测试命令和结果。"))
        if trusted.agent_activity: objects.append(_trusted_object(case,trusted.agent_activity,"AgentActivityInspectionObject","编码助手的可验证行动记录。"))
        if trusted.contribution_declaration: objects.append(_trusted_object(case,trusted.contribution_declaration,"ContributionDeclarationInspectionObject","贡献者对工具使用的声明。"))
        for confirmation in trusted.human_confirmations:
            if confirmation.contribution_fingerprint==case.contribution_fingerprint: objects.append(_object(object_id=confirmation.id,title="贡献者人工检查",kind="HumanConfirmationInspectionObject",summary="贡献者已确认检查当前版本和范围。",case=case,content=confirmation.statement,source=confirmation.actor,metadata={"attestation_id":confirmation.id}))
        if trusted.current_package: objects.append(_object(object_id=trusted.current_package["package_digest"],title="证据包",kind="EvidenceArtifactInspectionObject",summary="已验证并绑定当前贡献的证据包。",case=case,package_digest=trusted.current_package["package_digest"],content="此证据包已通过摘要和贡献绑定校验。",metadata={"historical_package_count":len(trusted.historical_packages)}))
        if trusted.final_receipt:
            objects.append(_object(object_id=fingerprint(trusted.final_receipt),title="最终审查建议回执",kind="EvidenceArtifactInspectionObject",summary="已验证的 AGM 最终审查建议回执。",case=case,content=json.dumps(trusted.final_receipt,ensure_ascii=False,indent=2),metadata={"receipt_digest":fingerprint(trusted.final_receipt)}))
        if not trusted.diffs:
            for path in case.changed_files: objects.append(_object(object_id=f"diff:{path}",title=f"相关修改：{path}",kind="DiffInspectionObject",summary="当前未提供可查看的代码差异。",case=case,metadata={"path":path,"line_ranges":_lines(ctx,path)}))
    else:
        for path in case.changed_files: objects.append(_object(object_id=f"diff:{path}",title=f"相关修改：{path}",kind="DiffInspectionObject",summary="当前未提供可查看的代码差异。",case=case,metadata={"path":path,"line_ranges":_lines(ctx,path)}))
    activity_data=_json(trusted.agent_activity.content) if trusted and trusted.agent_activity else {}
    if activity_data:
        agent={"state":"verifiable","status":"verifiable","message":"检测到可验证的编码 Agent 活动。","type":activity_data.get("agent_type","未记录"),"modified_file_count":len(activity_data.get("files_modified",[])),"commands":tuple(activity_data.get("commands_executed",[])),"tests":tuple(activity_data.get("tests_executed",[])),"used_other_tools":activity_data.get("other_agents_or_tools_used"),"network":activity_data.get("network_access"),"current_version":True}
    else: agent={"state":"not_detected","status":"none","message":"未检测到可验证的 Agent 参与记录。该贡献可能主要由人工完成，也可能存在未被记录的辅助工具使用。","type":None,"modified_file_count":0,"commands":(),"tests":(),"used_other_tools":None,"network":None,"current_version":False}
    declaration=_json(trusted.contribution_declaration.content) if trusted and trusted.contribution_declaration else {}
    if declaration.get("used_other_agents_or_tools") is False and activity_data.get("other_agents_or_tools_used") is True:
        gaps.append(DiagnosticFinding("agent-conflict","agent_record_conflict","high","贡献者说明与编码助手活动记录不一致","贡献者声明未使用其他助手，但可验证记录显示使用了其他助手或自动化工具。",tuple(case.changed_files),(),"两份记录一致","发现冲突","请贡献者核对并补充说明。",tuple(rule.rule_id for rule in case.matched_rules),tuple(item.obligation_id for item in case.obligations if item.evidence_type=="agent_action_scope"),(),"contributor","contributor_action_required",True,(trusted.contribution_declaration.artifact_id,trusted.agent_activity.artifact_id)))
    attestation_required=any(item.type=="human_attestation" for item in case.obligations)
    confirmations=trusted.human_confirmations if trusted else tuple(case.attestations)
    current_confirmation=next((item for item in confirmations if item.status=="confirmed" and item.contribution_fingerprint==case.contribution_fingerprint),None)
    human_state="required_current" if current_confirmation else ("required_stale" if attestation_required and confirmations else ("required_missing" if attestation_required else "not_required"))
    human={"contributor_self_review":{"required_current":"贡献者已确认检查当前版本。","required_stale":"贡献者的确认对应旧版本，需要重新确认。","required_missing":"项目要求贡献者检查当前版本，但尚未确认。","not_required":"本类修改不要求额外的贡献者人工确认。"}[human_state],"contributor_state":human_state,"maintainer_review":"已完成必要检查" if case.maintainer_verifications else "尚未完成必要检查","final_recommendation":"已记录" if case.final_decision else "尚未记录"}
    route,legal=_route(case,policy_config,responsibility,gaps);owner,message=ROUTE_TEXT[route]
    status={"normal_pr_review":"可以按常规流程审查","maintainer_focused_review":"需要重点检查","maintainer_review_available":"可以开始维护者审查","contributor_action_required":"需要贡献者先处理","waiting_for_contributor_submission":"等待贡献者提交维护者检查","blocked_pending_repair":"存在阻断问题","waiting_for_accountable_human":"等待人类确认","system_handled_no_action":"系统已处理，无需额外操作","final_recommendation_recorded":"AGM 最终审查建议已记录"}[route]
    host=HostPlatformStatus(False,None,None,None,"not_performed","not_performed","not_performed","local absence of host-platform adapter",True)
    final={"status":"建议接受" if case.final_decision and case.final_decision.decision=="accept" else "尚未记录","decision":case.final_decision.decision if case.final_decision else None}
    return PRDiagnosticView(case.id,case.contribution_fingerprint,case.policy_snapshot.policy_fingerprint,status,{"summary":ctx.get("summary","当前没有额外变更说明。"),"files":tuple(case.changed_files),"line_ranges":{path:_lines(ctx,path) for path in case.changed_files}},tuple(risks),tuple(requirements),tuple(observed),tuple(gaps),agent,human,final,host,{"status":status,"blocking_gaps":len([item for item in gaps if item.blocking])},{"route":route,"owner":owner,"message":message},tuple(objects),_actions(legal,route),{"case_state":case.state,"responsible_side":tuple(responsibility.primary_roles),"gate_state":case.state,"legal_operations":tuple(legal),"risk_rule_refs":tuple(item.rule_id for item in case.matched_rules),"compiled_obligation_refs":tuple(item.obligation_id for item in case.obligations),"evidence_state_summary":{item["obligation_ref"]:item["state"] for item in requirements},"human_confirmation_state":human_state,"agent_trace_state":agent["state"],"route_derivation":{"route":route,"reason":responsibility.reason},"sidecar":{"current_package":trusted.current_package["package_digest"] if trusted and trusted.current_package else None,"historical_packages":tuple(item["package_digest"] for item in trusted.historical_packages) if trusted else ()},"host_platform":host.to_dict()})
