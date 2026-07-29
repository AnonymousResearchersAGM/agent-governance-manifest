"""Compile the participant diagnostic from canonical state and verified artifacts."""
from __future__ import annotations

import json
from typing import Any

from ..config import VNextConfig
from ..guidance.diagnostics import obligation_presentation
from ..guidance.responsibility import derive_current_responsibility
from ..models import GovernanceCase, VNextError, fingerprint
from ..state_machine import allowed_actions
from .diff_parser import compact_ranges, parse_verified_diff
from .models import ActionEffectBoundary, DiagnosticFinding, HostPlatformStatus, InspectionObject, PRDiagnosticView
from .sidecar import SidecarEvidenceStore
from .trusted_sources import TrustedArtifact, TrustedDiagnosticEvidenceResolver, select_obligation_evidence

RISK_TEXT={"authentication":"该位置决定认证或权限何时生效；需要重点检查。","documentation":"该位置是项目说明；需要检查文字准确性和链接。","task_logic":"该位置影响应用的业务行为。","test_strategy":"该位置影响测试和验证覆盖。"}
STATE_WORDS={"missing":"未提供","invalid":"材料验证未通过","stale":"对应旧版本","expired":"已过有效期","rejected":"验证未通过","unbound":"尚未关联当前版本","current":"对应当前版本"}
DISPLAY_TITLE={"O-AGENT-SCOPE":"编码助手活动记录","O-HUMAN-ATTEST":"贡献者人工检查","O-TEST-COMMAND":"测试记录","O-ARTIFACT":"可复查的测试输出","O-AUTH-IMPACT":"认证与权限影响说明","O-SUMMARY":"修改说明","O-CHANGED-FILES":"变更文件清单","O-RATIONALE":"修改原因","O-LIMITATIONS":"已知限制"}
ROUTE_TEXT={"contributor_action_required":("贡献者","请补充或更新下列材料后，再提交维护者检查。"),"waiting_for_contributor_submission":("贡献者","当前无需你操作；下一步由贡献者提交维护者检查。"),"maintainer_focused_review":("维护者","材料已齐备，但涉及风险区域；请重点检查指定差异和关键测试。"),"maintainer_action_required":("维护者","发现需要先处理的材料矛盾；请决定是否要求贡献者补充或修正。"),"waiting_for_accountable_human":("有权限的负责人","等待确认已经检查当前版本和范围。"),"final_recommendation_recorded":("无需额外处理","AGM 最终审查建议已经记录；本页没有批准或合并平台 PR。"),"normal_pr_review":("维护者","检查文字准确性、命令示例和链接即可，可以返回常规审查。"),"blocked_pending_repair":("贡献者","维护者已要求修正；下一步由贡献者处理。")}

def _json(content:str)->dict[str,Any]:
    try:
        value=json.loads(content); return value if isinstance(value,dict) else {}
    except json.JSONDecodeError:return {}

def _object(*,object_id:str,title:str,kind:str,summary:str,case:GovernanceCase,content:str|None=None,head_commit:str|None=None,package_digest:str|None=None,artifact_route:str|None=None,source:str="当前材料",freshness:str="current",metadata:dict[str,Any]|None=None)->InspectionObject:
    return InspectionObject(object_id,title,kind,summary,source,case.base_commit,head_commit,case.contribution_fingerprint,fingerprint(content) if content is not None else None,package_digest,"available" if content is not None or artifact_route else "unavailable",freshness,artifact_route,content,metadata or {})

def _trusted_object(case:GovernanceCase,item:TrustedArtifact,kind:str,summary:str,evidence_ids:tuple[str,...])->InspectionObject:
    return _object(object_id=item.artifact_id,title=item.title,kind=kind,summary=summary,case=case,content=item.content,head_commit=item.head_commit_sha,package_digest=item.package_digest,artifact_route=f"/artifacts/{case.id}/{item.package_digest}/{item.artifact_id}",source="已验证并绑定当前版本的材料",metadata={"artifact_type":item.artifact_type,"media_type":item.media_type,"obligation_refs":item.obligation_refs,"canonical_evidence_ids":evidence_ids,"producer_assurance":item.producer_assurance})

def _artifact_evidence_ids(case:GovernanceCase,item:TrustedArtifact)->tuple[str,...]:
    return tuple("sidecar-"+fingerprint({"package":item.package_digest,"artifact":item.artifact_id,"obligation":ref})[:24] for ref in item.obligation_refs if any(e.id=="sidecar-"+fingerprint({"package":item.package_digest,"artifact":item.artifact_id,"obligation":ref})[:24] for e in case.evidence))

def _route(case:GovernanceCase,config:VNextConfig,responsibility:Any,gaps:list[DiagnosticFinding],actor_role:str)->tuple[str,list[str]]:
    legal=allowed_actions(config,state=case.state,role=actor_role)
    conflict=next((item for item in case.open_blocking_findings() if item.code=="trusted_sidecar_conflict"),None)
    if case.final_decision:return "final_recommendation_recorded",[]
    if conflict and case.state!="repair_requested": return "maintainer_action_required", [item for item in legal if item=="request_repair"]
    if case.state=="repair_requested":return "blocked_pending_repair",[]
    roles=set(responsibility.primary_roles)
    if case.state=="awaiting_human_attestation" or roles=={"accountable_human"}:return "waiting_for_accountable_human",[]
    if roles & {"contributor","contributor_agent"}:
        if not gaps and case.state=="evidence_incomplete":return "waiting_for_contributor_submission",[]
        return "contributor_action_required",[]
    if case.state=="awaiting_maintainer_verification":return ("maintainer_focused_review" if case.overall_risk_level in {"high","critical"} else "normal_pr_review"),legal
    if gaps:return "contributor_action_required",[]
    return "normal_pr_review",[]

def _actions(legal:list[str],route:str)->tuple[ActionEffectBoundary,...]:
    if route not in {"maintainer_focused_review","maintainer_action_required"}:return ()
    labels={"verify_evidence":"确认这项检查没有问题","request_repair":"请求贡献者补充或修正"}
    return tuple(ActionEffectBoundary(labels[action],action,("记录 AGM 中这项检查的结果。",),("不会修改代码。","不会执行 git merge。","不会批准或合并 GitHub/GitLab PR。")) for action in legal if action in labels)

def compile_pr_diagnostic(*,governance_case:GovernanceCase,contribution:Any=None,policy_config:VNextConfig,evidence_store:SidecarEvidenceStore|None=None,actor_role:str="maintainer")->PRDiagnosticView:
    # contribution only supplies an untrusted free-text description. It never controls risks or lines.
    summary=(contribution or {}).get("summary","当前没有额外变更说明。") if isinstance(contribution,dict) else "当前没有额外变更说明。"
    case=governance_case; trusted=TrustedDiagnosticEvidenceResolver(evidence_store).resolve(case) if evidence_store else None
    requirements=[]; observed=[]; gaps=[]; objects=[]
    for obligation in case.obligations:
        title,plain=obligation_presentation(obligation); title=DISPLAY_TITLE.get(obligation.obligation_id,title)
        if obligation.type=="human_attestation":
            confirmed=[item for item in case.attestations if item.status=="confirmed"]
            state="current" if any(item.contribution_fingerprint==case.contribution_fingerprint for item in confirmed) else ("stale" if confirmed else "missing"); selected=()
        elif obligation.type=="maintainer_verification": state,selected=("current",()) if obligation.status=="verified" else ("missing",())
        else: state,selected=select_obligation_evidence(case,obligation.obligation_id)
        requirements.append({"title":title,"plain_requirement":plain,"obligation_ref":obligation.obligation_id,"state":state,"blocking":obligation.blocking,"evidence_ids":tuple(item.id for item in selected)})
        for item in selected:
            observed.append({"title":title,"state":state,"evidence_type":item.evidence_type,"contribution_fingerprint":item.contribution_fingerprint,"source":item.source_actor,"evidence_id":item.id})
        if state!="current":gaps.append(DiagnosticFinding(f"gap:{obligation.id}","evidence_gap",obligation.severity,STATE_WORDS[state],plain,tuple(obligation.affected_scope),(),"对应当前版本",STATE_WORDS[state],"请贡献者补充或更新。",tuple(obligation.source_rule_ids),(obligation.obligation_id,),tuple(item.id for item in selected),"contributor","contributor_action_required",obligation.blocking,(obligation.id,*[item.id for item in selected])))
    locations=[]
    if trusted:
        for diff in trusted.diffs:
            try: locations.extend((diff,location) for location in parse_verified_diff(diff.content))
            except VNextError: pass  # legacy inspection-only material is never a source of locations
    risks=[]
    for rule in case.matched_rules:
        matched=[(item,location) for item,location in locations if location.path in rule.affected_paths]
        lines=tuple(value for _,location in matched for value in compact_ranges(location.added or location.removed))
        refs=tuple(f"{item.artifact_id}:{location.hunk}" for item,location in matched)
        risks.append(DiagnosticFinding(f"risk:{rule.id}","risk_area",rule.risk_level,f"{ {'low':'低风险','medium':'中等风险','high':'较高风险','critical':'严重风险'}.get(rule.risk_level,'风险区域')}：{', '.join(rule.affected_paths)}",RISK_TEXT.get(rule.zone,"该位置被项目规则识别为需要额外检查的区域。"),tuple(location.path for _,location in matched) or tuple(rule.affected_paths),lines,"按项目要求检查","已识别该风险区域","",(rule.rule_id,),tuple(rule.obligation_ids),refs,"maintainer","inspect_risk",False,(rule.id,*refs)))
    if trusted:
        kinds={"diff":("DiffInspectionObject","绑定当前贡献的代码差异。"),"test_result":("TestInspectionObject","可复查的测试命令和结果。"),"agent_activity":("AgentActivityInspectionObject","对应当前版本的编码助手活动记录。"),"contribution_declaration":("ContributionDeclarationInspectionObject","贡献者对工具使用的声明。"),"impact_statement":("ImpactStatementInspectionObject","对应当前版本的影响说明。")}
        for item in trusted.artifacts:
            if item.artifact_type in kinds: objects.append(_trusted_object(case,item,*kinds[item.artifact_type],_artifact_evidence_ids(case,item)))
        for confirmation in trusted.human_confirmations:
            if confirmation.contribution_fingerprint==case.contribution_fingerprint:objects.append(_object(object_id=confirmation.id,title="贡献者人工检查",kind="HumanConfirmationInspectionObject",summary="贡献者已确认检查当前版本和范围。",case=case,content=confirmation.statement,source=confirmation.actor,metadata={"attestation_id":confirmation.id}))
        if trusted.final_receipt:objects.append(_object(object_id=fingerprint(trusted.final_receipt),title="最终审查建议回执",kind="FinalReceiptInspectionObject",summary="已验证的 AGM 最终审查建议回执。",case=case,content=json.dumps(trusted.final_receipt,ensure_ascii=False,indent=2),metadata={"receipt_digest":fingerprint(trusted.final_receipt)}))
    if not any(item.object_type=="DiffInspectionObject" for item in objects):
        for path in case.changed_files:objects.append(_object(object_id=f"diff:{path}",title=f"相关修改：{path}",kind="DiffInspectionObject",summary="当前未提供可查看的代码差异。",case=case,metadata={"path":path}))
    activity=next((item for item in (trusted.artifacts if trusted else ()) if item.artifact_type=="agent_activity"),None); activity_data=_json(activity.content) if activity else {}
    agent={"state":"verifiable","status":"verifiable","message":"检测到一份内容完整、并绑定当前版本的编码助手活动记录。","type":activity_data.get("agent_type","未记录"),"modified_file_count":len(activity_data.get("files_modified",[])),"commands":tuple(activity_data.get("commands_executed",[])),"tests":tuple(activity_data.get("tests_executed",[])),"used_other_tools":activity_data.get("other_agents_or_tools_used"),"network":activity_data.get("network_access"),"current_version":True,"producer_assurance":"记录声明由某编码助手生成；当前原型已验证内容完整性和版本绑定，尚未通过代码托管平台或密码学签名确认生产者身份。"} if activity else {"state":"not_detected","status":"none","message":"未检测到可验证的编码助手活动记录。该贡献可能主要由人工完成，也可能存在未被记录的辅助工具使用。","type":None,"modified_file_count":0,"commands":(),"tests":(),"used_other_tools":None,"network":None,"current_version":False}
    attestation_required=any(item.type=="human_attestation" for item in case.obligations); confirmed=any(item.status=="confirmed" and item.contribution_fingerprint==case.contribution_fingerprint for item in case.attestations); human_state="required_current" if confirmed else ("required_missing" if attestation_required else "not_required")
    human={"contributor_self_review":{"required_current":"已完成","required_missing":"项目要求贡献者检查当前版本，但尚未确认。","not_required":"本类修改不要求额外的贡献者人工确认。"}[human_state],"contributor_state":human_state,"maintainer_review":"已完成必要检查" if case.maintainer_verifications else "尚未完成必要检查","final_recommendation":"已记录" if case.final_decision else "尚未记录"}
    responsibility=derive_current_responsibility(case,[]); route,legal=_route(case,policy_config,responsibility,gaps,actor_role); owner,message=ROUTE_TEXT[route]
    status={"normal_pr_review":"可以按常规流程审查","maintainer_focused_review":"需要重点检查","maintainer_action_required":"发现需要先处理的材料矛盾","contributor_action_required":"需要贡献者先处理","waiting_for_contributor_submission":"等待贡献者提交维护者检查","blocked_pending_repair":"等待贡献者修正","waiting_for_accountable_human":"等待人类确认","final_recommendation_recorded":"AGM 最终审查建议已记录"}[route]
    host=HostPlatformStatus(False,None,None,None,"not_performed","not_performed","not_performed","local absence of host-platform adapter",True)
    final={"status":"建议接受" if case.final_decision and case.final_decision.decision=="accept" else "尚未记录","decision":case.final_decision.decision if case.final_decision else None}
    return PRDiagnosticView(case.id,case.contribution_fingerprint,case.policy_snapshot.policy_fingerprint,status,{"summary":summary,"files":tuple(case.changed_files),"line_ranges":{path:tuple(value for _,location in locations if location.path==path for value in compact_ranges(location.added or location.removed)) for path in case.changed_files}},tuple(risks),tuple(requirements),tuple(observed),tuple(gaps),agent,human,final,host,{"status":status,"blocking_gaps":len([item for item in gaps if item.blocking])},{"route":route,"owner":owner,"message":message},tuple(objects),_actions(legal,route),{"case_state":case.state,"responsible_side":("maintainer",) if route=="maintainer_action_required" else tuple(responsibility.primary_roles),"gate_state":case.state,"legal_operations":tuple(legal),"risk_rule_refs":tuple(item.rule_id for item in case.matched_rules),"compiled_obligation_refs":tuple(item.obligation_id for item in case.obligations),"evidence_state_summary":{item["obligation_ref"]:item["state"] for item in requirements},"human_confirmation_state":human_state,"agent_trace_state":agent["state"],"route_derivation":{"route":route,"reason":responsibility.reason},"sidecar":{"current_package":trusted.current_package["package_digest"] if trusted and trusted.current_package else None,"historical_packages":tuple(item["package_digest"] for item in trusted.historical_packages) if trusted else ()},"host_platform":host.to_dict()})
