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
            kwargs={"actor":"contributor","actor_role":"contributor","obligation_ids":[obligation.obligation_id],"evidence_type":obligation.evidence_type,"value":f"{obligation.obligation_id} 的当前版本材料","observed_at":FIXED_TIME}
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
    def sidecar_package(self):
        case=self.service.storage.load_case(self.case_id); store=SidecarEvidenceStore(self.service.root)
        return store.write_package(case_id=case.id,contribution_fingerprint=case.contribution_fingerprint,policy_fingerprint=case.policy_snapshot.policy_fingerprint,producer="deterministic-scenario",created_at=FIXED_TIME,artifacts=[{"type":"evidence","summary":item.evidence_type,"digest":item.id} for item in case.evidence])

def _context(slug: str, path: str, *, agent=True, diff=True):
    base={"summary":slug,"changed_line_ranges":{path:["84–117"] if "auth" in path else ["5–8"]},"diff_hunks":{path:"@@ -1 +1 @@\n-old\n+new"} if diff else {}}
    if agent: base["agent_activity"]={"verified":True,"type":"编码 Agent","modified_files":[path],"commands":["python -m pytest -q"],"test_runs":["pytest"],"used_other_tools":False,"network":False,"summary":"修改当前贡献并运行测试。"}
    return base

SCENARIOS=(
 ("D1_low_risk_readme","README.md","supervised_agent","ready"),("D2_high_risk_missing","demo_app/auth.py","supervised_agent","missing"),("D3_high_risk_ready","demo_app/auth.py","supervised_agent","ready"),("D4_no_agent_trace","demo_app/tasks.py","human_direct","ready"),("D5_no_agent_high_missing_test","demo_app/auth.py","human_direct","missing"),("D6_declaration_conflict","README.md","supervised_agent","conflict"),("D7_stale_test","tests/test_auth.py","supervised_agent","stale"),("D8_system_handled","README.md","human_direct","denied"),("D9_contributor_waiting","README.md","supervised_agent","waiting"),("D10_final_recommendation","README.md","human_direct","final"))

def build_scenario(service: GovernanceService, slug: str, path: str, profile: str, mode: str):
    case,_=service.open_case([path],requested_mode="declared_agent_mediated" if profile!="human_direct" else "maintainer_requested",actor="contributor",actor_role="contributor",case_id="case-"+slug,base_commit="d"*40,autonomy_profile=profile,timestamp=FIXED_TIME); assert case
    driver=ScenarioLifecycleDriver(service,case.id); ctx=_context(slug,path,agent=profile!="human_direct",diff=mode != "waiting")
    if mode in {"ready","denied","waiting","conflict","stale","final"}: driver.add_required_evidence()
    package=None
    if mode=="ready":
        driver.prepare()
        if any(o.type=="human_attestation" for o in service.storage.load_case(case.id).obligations): driver.attest()
    elif mode=="conflict":
        driver.prepare(); ctx["contribution_declaration"]={"summary":"未使用其他助手。","used_other_tools":False}; ctx["agent_activity"]["used_other_tools"]=True; agent_scope=next(o.obligation_id for o in service.storage.load_case(case.id).obligations if o.evidence_type=="agent_action_scope"); driver.repair(agent_scope)
    elif mode=="stale":
        driver.prepare(); package=driver.sidecar_package(); test_id=next(o.obligation_id for o in service.storage.load_case(case.id).obligations if o.evidence_type=="test_command"); driver.repair(test_id); driver.resubmit(test_id)
    elif mode=="denied": driver.prepare(); driver.denied_verify()
    elif mode=="final": driver.prepare(); driver.verify(); driver.decide_accept()
    if mode=="ready" and slug=="D3_high_risk_ready": package=driver.sidecar_package()
    if package: ctx["sidecar_package"]={"digest":package.package_digest,"contribution_fingerprint":package.contribution_fingerprint,"freshness":"current" if package.contribution_fingerprint==service.storage.load_case(case.id).contribution_fingerprint else "stale"}
    if mode=="final":
        package=driver.sidecar_package(); store=SidecarEvidenceStore(service.root); final=service.storage.load_case(case.id).final_decision
        receipt=FinalEvidenceReceipt(service.storage.load_case(case.id).contribution_fingerprint,service.storage.load_case(case.id).policy_snapshot.policy_fingerprint,package.package_digest,"低风险文档修改","未检测到可验证记录","不适用","已完成必要检查","建议接受",{"connected":False,"approval_state":"not_performed","merge_state":"not_performed","close_state":"not_performed","verified":True},FIXED_TIME)
        path=store.write_final_receipt(receipt); ctx["final_receipt"]={"digest":path.stem,"href":".agm-work/evidence_store/receipts/"+path.name}
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
