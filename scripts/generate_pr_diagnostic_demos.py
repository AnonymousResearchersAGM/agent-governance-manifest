"""Deterministic D1--D10 fixtures, built only through public domain services."""
from __future__ import annotations
import hashlib,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/"src"),str(ROOT/"scripts")]
from agm.vnext.models import VNextError
from agm.vnext.pr_diagnostic import SidecarEvidenceBridge,SidecarEvidenceStore,render_pr_diagnostic_html,render_pr_diagnostic_json,render_pr_diagnostic_markdown
from agm.vnext.pr_diagnostic.sidecar import FinalEvidenceReceipt
from agm.vnext.runtime import DemoExecutionContext,use_execution_context
from agm.vnext.service import GovernanceService
from agm.vnext.storage import atomic_write_text
from generate_reviewer_guidance_demos import FIXED_TIME,make_project

SCENARIOS=(
 ("D1_low_risk_readme","README.md","supervised_agent","ready"),("D2_high_risk_missing","demo_app/auth.py","supervised_agent","missing"),("D3_high_risk_ready","demo_app/auth.py","supervised_agent","ready"),("D4_no_agent_trace","demo_app/tasks.py","human_direct","ready"),("D5_no_agent_high_missing_test","demo_app/auth.py","human_direct","missing"),("D6A_declaration_conflict","README.md","supervised_agent","conflict"),("D6B_repair_requested","README.md","supervised_agent","repair"),("D7_stale_test","demo_app/tasks.py","supervised_agent","stale"),("D8_system_handled","README.md","human_direct","denied"),("D9_contributor_waiting","README.md","supervised_agent","waiting"),("D10_final_recommendation","README.md","human_direct","final"))

def _diff(path):
    if path=="README.md": return """diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -5,2 +5,2 @@
-pip install agm-demo
+python -m pip install agm-demo
 link remains valid
"""
    if "auth" in path:return """diff --git a/demo_app/auth.py b/demo_app/auth.py
--- a/demo_app/auth.py
+++ b/demo_app/auth.py
@@ -84,3 +84,6 @@ def can_access(token):
-    return token in active_tokens
+    if token in revoked_tokens:
+        return False
+    return token in active_tokens
"""
    return """diff --git a/demo_app/tasks.py b/demo_app/tasks.py
--- a/demo_app/tasks.py
+++ b/demo_app/tasks.py
@@ -20,1 +20,2 @@ def list_tasks():
+    return sorted(tasks)
"""

def _artifacts(path,profile,*,include_test=True,conflict=False):
    refs=["O-SUMMARY","O-CHANGED-FILES"]
    if conflict: refs.remove("O-SUMMARY")
    if "auth" in path:refs += ["O-RATIONALE","O-LIMITATIONS"]
    elif path != "README.md":refs += ["O-RATIONALE"]
    result=[{"type":"diff","title":"相关代码差异","content":_diff(path),"obligation_refs":[]},{"type":"supporting_statement","title":"贡献材料说明","content":"这是一份绑定当前版本的具体贡献材料。","obligation_refs":refs}]
    if profile!="human_direct":result.append({"type":"agent_activity","title":"编码助手活动记录","content":json.dumps({"agent_type":"编码助手","task_summary":"修正 README 安装命令和失效链接" if path=="README.md" else "修复令牌撤销检查","files_modified":[path],"commands_executed":[] if path=="README.md" else ["python -m pytest tests/test_auth.py -q"],"tests_executed":[] if path=="README.md" else ["tests/test_auth.py"],"other_agents_or_tools_used":conflict,"tools_used":["sub-agent"] if conflict else [],"activity_scope":[path],"network_access":False},ensure_ascii=False),"source_tool":"deterministic-scenario","observed_at":FIXED_TIME,"affected_scope":[path],"obligation_refs":["O-AGENT-SCOPE"]})
    if "auth" in path:
      if include_test:result.append({"type":"test_result","title":"测试记录","content":"python -m pytest tests/test_auth.py -q\n18 passed, 0 failed","source_tool":"pytest","command":"python -m pytest tests/test_auth.py -q","environment":"deterministic demo fixture","result_summary":"18 passed, 0 failed","exit_code":0,"tests_passed":18,"tests_failed":0,"affected_scope":[path],"observed_at":FIXED_TIME,"obligation_refs":["O-TEST-COMMAND","O-ARTIFACT"]})
      result.append({"type":"impact_statement","title":"认证与权限影响说明","content":"撤销令牌、会话刷新和权限变更后拒绝旧会话；未改变注册或密码重置。","obligation_refs":["O-AUTH-IMPACT"]})
    elif path != "README.md" and include_test:
      result.append({"type":"test_result","title":"测试记录","content":"python -m pytest tests/test_tasks.py -q\n8 passed, 0 failed","source_tool":"pytest","command":"python -m pytest tests/test_tasks.py -q","environment":"deterministic demo fixture","result_summary":"8 passed, 0 failed","exit_code":0,"tests_passed":8,"tests_failed":0,"affected_scope":[path],"observed_at":FIXED_TIME,"obligation_refs":["O-TEST-EXPLANATION"]})
    if conflict:result.append({"type":"contribution_declaration","title":"贡献者声明","content":json.dumps({"other_agents_or_tools_used":False,"declared_tools":[],"declaration_scope":[path],"declared_by":"contributor","observed_at":FIXED_TIME,"statement":"没有使用其他自动化工具。"},ensure_ascii=False),"source_tool":"contributor","observed_at":FIXED_TIME,"affected_scope":[path],"obligation_refs":["O-SUMMARY"]})
    return result

def _open(service,slug,path,profile):
    case,_=service.open_case([path],requested_mode="declared_agent_mediated" if profile!="human_direct" else "maintainer_requested",actor="contributor",actor_role="contributor",case_id="case-"+slug,base_commit="d"*40,autonomy_profile=profile,timestamp=FIXED_TIME);assert case;return case
def _bridge(service,case,arts,*,submit=True):
    receipt=SidecarEvidenceStore(service.root).write_package(case_id=case.id,contribution_fingerprint=case.contribution_fingerprint,policy_fingerprint=case.policy_snapshot.policy_fingerprint,producer="deterministic-scenario",created_at=FIXED_TIME,base_commit_sha=case.base_commit,head_commit_sha="c"*40,artifacts=arts)
    SidecarEvidenceBridge(service).register_package(case.id,package_digest=receipt.package_digest)
    if submit: service.prepare_case(case.id,actor="contributor",actor_role="contributor")
    return receipt
def _attest(service,case):return service.attest(case.id,actor="contributor-human",role="accountable_human",reviewed_scope=case.changed_files,statement="已检查当前版本的代码差异和测试结果。",timestamp=FIXED_TIME)

def build_scenario(service,slug,path,profile,mode):
    case=_open(service,slug,path,profile); package=None
    package=_bridge(service,case,_artifacts(path,profile,include_test=mode!="missing",conflict=mode in {"conflict","repair"}),submit=mode!="waiting")
    if mode=="ready":
      if any(item.type=="human_attestation" for item in service.storage.load_case(case.id).obligations):_attest(service,case)
    elif mode in {"conflict","repair"}:
      if mode=="repair":service.request_repair(case.id,actor="maintainer-reviewer",role="maintainer",message="请核对并修正工具使用声明。",affected_obligation_ids=["O-AGENT-SCOPE"])
    elif mode=="stale":
      service.request_repair(case.id,actor="maintainer-reviewer",role="maintainer",message="请更新测试记录。",affected_obligation_ids=["O-TEST-EXPLANATION"])
      service.resubmit(case.id,actor="contributor",role="contributor",summary="提交新版本。",affected_obligation_ids=["O-TEST-EXPLANATION"],diff_material="new deterministic contribution",change_classification="material")
      _bridge(service,service.storage.load_case(case.id),_artifacts(path,profile,include_test=False),submit=False)
    elif mode=="denied":
      try:service.verify(case.id,actor="coding-agent",role="contributor_agent",reason="无权验证",timestamp=FIXED_TIME)
      except VNextError:pass
    elif mode=="final":
      service.verify(case.id,actor="maintainer-reviewer",role="maintainer",reason="已检查当前材料。",timestamp=FIXED_TIME);service.decide(case.id,actor="final-maintainer",role="maintainer",decision="accept",reason="AGM 审查建议可以接受。",timestamp=FIXED_TIME)
      final=service.storage.load_case(case.id).final_decision; store=SidecarEvidenceStore(service.root);store.write_final_receipt(FinalEvidenceReceipt(case.contribution_fingerprint,case.policy_snapshot.policy_fingerprint,package.package_digest,"低风险文档修改","未检测到可验证记录","不适用","已完成必要检查","建议接受",{"connected":False,"approval_state":"not_performed","merge_state":"not_performed","close_state":"not_performed","verified":True},FIXED_TIME,case.id,final.id))
    return case.id,{"summary":slug}

def generate(output):
 output.mkdir(parents=True,exist_ok=True);hashes={};results=[]
 with tempfile.TemporaryDirectory(prefix="agm-pr-diagnostic-") as raw:
  for slug,path,profile,mode in SCENARIOS:
   with use_execution_context(DemoExecutionContext("pr-"+slug,FIXED_TIME,"demo-key")):
    root=make_project(Path(raw),slug);service=GovernanceService(root);case_id,ctx=build_scenario(service,slug,path,profile,mode);view=service.pr_diagnosis(case_id,contribution=ctx);scenario=output/slug
    for name,text in {"diagnosis.json":render_pr_diagnostic_json(view),"report.md":render_pr_diagnostic_markdown(view),"report.html":render_pr_diagnostic_html(view),"case.json":json.dumps(service.storage.load_case(case_id).to_dict(),ensure_ascii=False,indent=2)+"\n"}.items():
      target=scenario/name;atomic_write_text(target,text);hashes[target.relative_to(output).as_posix()]=hashlib.sha256(text.encode()).hexdigest()
    results.append({"scenario":slug,"case_state":service.storage.load_case(case_id).state})
 atomic_write_text(output/"expected_sha256.json",json.dumps(hashes,ensure_ascii=False,indent=2,sort_keys=True)+"\n");return results
if __name__=="__main__":print(json.dumps({"generated":generate(ROOT/"examples"/"pr_native_diagnostic"/"outputs")},ensure_ascii=False,indent=2))
