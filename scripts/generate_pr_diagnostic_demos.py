"""Legal, deterministic D1--D10 lifecycle fixtures and frozen projections."""
from __future__ import annotations
import hashlib, json, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/"src"),str(ROOT/"scripts")]
from agm.vnext.models import VNextError  # noqa:E402
from agm.vnext.pr_diagnostic import SidecarEvidenceStore, render_pr_diagnostic_html, render_pr_diagnostic_json, render_pr_diagnostic_markdown  # noqa:E402
from agm.vnext.pr_diagnostic.sidecar import FinalEvidenceReceipt  # noqa:E402
from agm.vnext.runtime import DemoExecutionContext,use_execution_context  # noqa:E402
from agm.vnext.service import GovernanceService  # noqa:E402
from agm.vnext.storage import atomic_write_text  # noqa:E402
from generate_reviewer_guidance_demos import FIXED_TIME,make_project  # noqa:E402

class ScenarioLifecycleDriver:
    """A fixture driver deliberately limited to public GovernanceService calls."""
    def __init__(self, service: GovernanceService, case_id: str): self.service,self.case_id=service,case_id
    def add_required_evidence(self):
        for obligation in self.service.storage.load_case(self.case_id).obligations:
            if obligation.type=="human_attestation": continue
            concrete={
                "summary":"修复令牌撤销后的访问拒绝行为，并保留现有登录流程。",
                "changed_files":"本次修改仅涉及列出的贡献文件。",
                "rationale":"撤销令牌后必须拒绝继续访问，避免旧会话绕过权限变更。",
                "test_command":"python -m pytest tests/test_auth.py -q\n18 passed, 0 failed\n覆盖：test_revoked_token_is_rejected；test_expired_session_cannot_refresh；test_permission_change_invalidates_session",
                "artifact":"认证回归测试输出：18 passed, 0 failed。",
                "known_limitations":"未改变密码重置、注册或多因素认证流程。",
                "security_auth_impact":"影响撤销令牌、会话刷新和权限变更后的会话失效路径；未改变身份验证回退策略。",
                "agent_action_scope":"编码助手修改认证逻辑并运行定向测试。",
            }
            kwargs={"actor":"contributor","actor_role":"contributor","obligation_ids":[obligation.obligation_id],"evidence_type":obligation.evidence_type,"value":concrete.get(obligation.evidence_type,"已提供可复查的当前版本材料。"),"observed_at":FIXED_TIME}
            if obligation.evidence_type=="test_command": kwargs.update(command="python -m pytest -q",environment="Python 3.11 / local deterministic fixture",source_tool="pytest")
            self.service.add_evidence(self.case_id,**kwargs)
    def prepare(self): return self.service.prepare_case(self.case_id,actor="contributor",actor_role="contributor")
    def attest(self):
        case=self.service.storage.load_case(self.case_id)
        return self.service.attest(self.case_id,actor="contributor-human",role="accountable_human",reviewed_scope=case.changed_files,statement="已检查当前版本的代码差异和测试结果。",timestamp=FIXED_TIME)
    def verify(self): return self.service.verify(self.case_id,actor="maintainer-reviewer",role="maintainer",reason="已检查当前材料。",timestamp=FIXED_TIME)
    def repair(self, obligation_id: str): return self.service.request_repair(self.case_id,actor="maintainer-reviewer",role="maintainer",message="请更新指定测试记录。",affected_obligation_ids=[obligation_id])
    def resubmit(self, obligation_id: str): return self.service.resubmit(self.case_id,actor="contributor",role="contributor",summary="提交新版本代码差异。",affected_obligation_ids=[obligation_id],diff_material="new deterministic contribution",change_classification="material")
    def decide_accept(self): return self.service.decide(self.case_id,actor="final-maintainer",role="maintainer",decision="accept",reason="AGM 审查建议可以接受。",timestamp=FIXED_TIME)
    def denied_verify(self):
        try: self.service.verify(self.case_id,actor="coding-agent",role="contributor_agent",reason="无权验证",timestamp=FIXED_TIME)
        except VNextError: return
        raise AssertionError("fixture expected an unauthorized operation rejection")
    def sidecar_package(self, artifacts):
        case=self.service.storage.load_case(self.case_id); store=SidecarEvidenceStore(self.service.root)
        return store.write_package(case_id=case.id,contribution_fingerprint=case.contribution_fingerprint,policy_fingerprint=case.policy_snapshot.policy_fingerprint,producer="deterministic-scenario",created_at=FIXED_TIME,base_commit_sha=case.base_commit,head_commit_sha="c"*40,artifacts=artifacts)

def _context(slug: str, path: str, *, agent=True, diff=True):
    return {"summary":slug,"changed_line_ranges":{path:["84–117"] if "auth" in path else ["5–8"]}}

def _materials(path: str, *, agent: bool, declaration: bool=False, conflict: bool=False):
    diff = """@@ demo_app/auth.py:84-117 @@\n-    return token in active_tokens\n+    if token in revoked_tokens:\n+        return False\n+    return token in active_tokens\n\n撤销后的令牌不能继续访问受保护资源。""" if "auth" in path else """@@ README.md:5-8 @@\n- pip install agm-demo\n+ python -m pip install agm-demo\n\n修正安装命令，链接仍指向同一份项目文档。"""
    materials=[{"type":"diff","title":"相关代码差异","content":diff}]
    if "auth" in path:
        materials.extend([{"type":"test_result","title":"测试记录","content":"测试命令：python -m pytest tests/test_auth.py -q\n结果：18 passed, 0 failed\n关键测试：test_revoked_token_is_rejected；test_expired_session_cannot_refresh；test_permission_change_invalidates_session"},{"type":"impact_statement","title":"认证与权限影响说明","content":"本次修改在撤销令牌、会话刷新和权限变更后拒绝旧会话。未改变注册、密码重置或多因素认证。维护者应重点确认撤销列表查询发生在访问允许之前。"}])
    if agent: materials.append({"type":"agent_activity","title":"编码助手行动摘要","content":json.dumps({"agent_type":"编码助手","tool_name":"deterministic-fixture","task_summary":"修复令牌撤销检查","files_modified":[path],"commands_executed":["python -m pytest tests/test_auth.py -q"],"tests_executed":["tests/test_auth.py"],"other_agents_or_tools_used":conflict,"network_access":False,"risk_sensitive_files_touched":"auth" in path},ensure_ascii=False)})
    if declaration: materials.append({"type":"contribution_declaration","title":"贡献者声明","content":json.dumps({"used_other_agents_or_tools":False,"statement":"本次工作没有使用其他编码助手或自动化子任务。"},ensure_ascii=False)})
    return materials

SCENARIOS=(
 ("D1_low_risk_readme","README.md","supervised_agent","ready"),("D2_high_risk_missing","demo_app/auth.py","supervised_agent","missing"),("D3_high_risk_ready","demo_app/auth.py","supervised_agent","ready"),("D4_no_agent_trace","demo_app/tasks.py","human_direct","ready"),("D5_no_agent_high_missing_test","demo_app/auth.py","human_direct","missing"),("D6_declaration_conflict","README.md","supervised_agent","conflict"),("D7_stale_test","tests/test_auth.py","supervised_agent","stale"),("D8_system_handled","README.md","human_direct","denied"),("D9_contributor_waiting","README.md","supervised_agent","waiting"),("D10_final_recommendation","README.md","human_direct","final"))

def build_scenario(service: GovernanceService, slug: str, path: str, profile: str, mode: str):
    case,_=service.open_case([path],requested_mode="declared_agent_mediated" if profile!="human_direct" else "maintainer_requested",actor="contributor",actor_role="contributor",case_id="case-"+slug,base_commit="d"*40,autonomy_profile=profile,timestamp=FIXED_TIME); assert case
    driver=ScenarioLifecycleDriver(service,case.id); ctx=_context(slug,path,agent=profile!="human_direct",diff=mode != "waiting")
    if mode in {"ready","denied","waiting","conflict","stale","final"}: driver.add_required_evidence()
    package=None
    if mode in {"ready","missing","conflict","stale","waiting"} and profile!="human_direct":
        package=driver.sidecar_package(_materials(path,agent=True,declaration=mode=="conflict",conflict=mode=="conflict"))
    if mode=="ready":
        driver.prepare()
        if any(o.type=="human_attestation" for o in service.storage.load_case(case.id).obligations): driver.attest()
    elif mode=="conflict":
        driver.prepare(); agent_scope=next(o.obligation_id for o in service.storage.load_case(case.id).obligations if o.evidence_type=="agent_action_scope"); driver.repair(agent_scope)
    elif mode=="stale":
        driver.prepare(); test_id=next(o.obligation_id for o in service.storage.load_case(case.id).obligations if o.evidence_type=="test_command"); driver.repair(test_id); driver.resubmit(test_id)
    elif mode=="denied": driver.prepare(); driver.denied_verify()
    elif mode=="final": driver.prepare(); driver.verify(); driver.decide_accept()
    if mode=="ready" and slug=="D3_high_risk_ready" and package is None: package=driver.sidecar_package(_materials(path,agent=True))
    if mode=="final":
        package=driver.sidecar_package(_materials(path,agent=False)); store=SidecarEvidenceStore(service.root); final=service.storage.load_case(case.id).final_decision
        receipt=FinalEvidenceReceipt(service.storage.load_case(case.id).contribution_fingerprint,service.storage.load_case(case.id).policy_snapshot.policy_fingerprint,package.package_digest,"低风险文档修改","未检测到可验证记录","不适用","已完成必要检查","建议接受",{"connected":False,"approval_state":"not_performed","merge_state":"not_performed","close_state":"not_performed","verified":True},FIXED_TIME)
        store.write_final_receipt(receipt)
    return case.id,ctx

def generate(output: Path)->list[dict[str,str]]:
    output.mkdir(parents=True,exist_ok=True); hashes={}; results=[]
    with tempfile.TemporaryDirectory(prefix="agm-pr-diagnostic-") as raw:
      for slug,path,profile,mode in SCENARIOS:
       with use_execution_context(DemoExecutionContext("pr-"+slug,FIXED_TIME,"demo-key")):
        root=make_project(Path(raw),slug); service=GovernanceService(root); case_id,ctx=build_scenario(service,slug,path,profile,mode); view=service.pr_diagnosis(case_id,contribution=ctx); scenario=output/slug
        for name,text in {"diagnosis.json":render_pr_diagnostic_json(view),"report.md":render_pr_diagnostic_markdown(view),"report.html":render_pr_diagnostic_html(view),"case.json":json.dumps(service.storage.load_case(case_id).to_dict(),ensure_ascii=False,indent=2)+"\n"}.items():
            target=scenario/name; atomic_write_text(target,text); hashes[target.relative_to(output).as_posix()]=hashlib.sha256(text.encode()).hexdigest()
        results.append({"scenario":slug,"case_state":service.storage.load_case(case_id).state})
    atomic_write_text(output/"expected_sha256.json",json.dumps(hashes,ensure_ascii=False,indent=2,sort_keys=True)+"\n"); return results
if __name__=="__main__": print(json.dumps({"generated":generate(ROOT/"examples"/"pr_native_diagnostic"/"outputs")},ensure_ascii=False,indent=2))
