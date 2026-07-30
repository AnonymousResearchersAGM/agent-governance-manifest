"""Deterministic D1--D10 fixtures, built only through public domain services."""
from __future__ import annotations
import hashlib,json,shutil,sys,tempfile
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

def _summary(path):
    if path=="README.md":return "更新 README 的安装命令，并保留现有链接说明。"
    if "auth" in path:return "在访问检查中拒绝已撤销令牌，再判断令牌是否仍然有效。"
    return "让任务列表按稳定顺序返回，避免调用方收到不确定顺序。"

def _typed(case,artifact_type,head,refs,**fields):
    payload={"schema_version":"agm.evidence_artifact/v1","artifact_type":artifact_type,
      "observed_at":FIXED_TIME,"head_commit_sha":head,
      "contribution_fingerprint":case.contribution_fingerprint,
      "obligation_refs":refs,**fields}
    return json.dumps(payload,ensure_ascii=False,sort_keys=True)

def _artifact(case,artifact_type,title,head,refs,*,source_tool="deterministic-scenario",**fields):
    return {"type":artifact_type,"title":title,
      "content":_typed(case,artifact_type,head,refs,source_tool=source_tool,**fields),
      "source_tool":source_tool,"observed_at":FIXED_TIME,
      "affected_scope":[case.changed_files[0]],"obligation_refs":refs}

def _artifacts(case,path,profile,head,*,include_test=True,conflict=False):
    result=[{"type":"unified_diff","title":"相关代码差异","content":_diff(path),
      "source_tool":"deterministic-diff","observed_at":FIXED_TIME,
      "affected_scope":[path],"obligation_refs":[]},
      _artifact(case,"change_summary","修改说明",head,["O-SUMMARY"],
        summary=_summary(path),affected_components=[path],
        behavioral_change="文档安装示例更明确。" if path=="README.md" else
          ("已撤销令牌现在会被明确拒绝。" if "auth" in path else "任务列表返回顺序稳定。")),
      _artifact(case,"changed_files","变更文件清单",head,["O-CHANGED-FILES"],files=[path])]
    if "auth" in path or path!="README.md":
      result.append(_artifact(case,"rationale","修改原因",head,["O-RATIONALE"],
        reason="避免已撤销令牌继续访问。" if "auth" in path else "避免任务顺序随运行环境变化。",
        intended_outcome="撤销后的访问稳定失败。" if "auth" in path else "调用方获得可预测的任务顺序。"))
    if "auth" in path:
      result.append(_artifact(case,"known_limitations","已知限制",head,["O-LIMITATIONS"],
        limitations=[],no_known_limitations=True,declared_by="demo contributor"))
      result.append(_artifact(case,"impact_statement","认证与权限影响说明",head,["O-AUTH-IMPACT"],
        security_impact="已撤销令牌在访问检查中被拒绝。",
        compatibility_impact={"status":"not_applicable","reason":"未改变令牌格式或调用接口。"},
        data_impact={"status":"not_applicable","reason":"不读取或迁移持久化数据。"},
        operational_impact="部署后现有已撤销会话会立即失去访问能力。"))
    if profile!="human_direct":
      task_summary=("修正 README 安装命令和链接说明。" if path=="README.md" else
        ("实现已撤销令牌拒绝逻辑。" if "auth" in path else "实现任务列表稳定排序。"))
      commands=[] if path=="README.md" else [
        "python -m pytest tests/test_auth.py -q" if "auth" in path else
        "python -m pytest tests/test_tasks.py -q"]
      result.append(_artifact(case,"agent_activity","编码助手活动记录",head,["O-AGENT-SCOPE"],
        source_tool="deterministic-agent-recorder",agent_type="编码助手",
        task_summary=task_summary,files_modified=[path],commands_executed=commands,
        tests_executed=[] if path=="README.md" else [
          "tests/test_auth.py" if "auth" in path else "tests/test_tasks.py"],
        other_agents_or_tools_used=conflict,tools_used=["secondary-code-tool"] if conflict else [],
        activity_scope=[path],network_access=False))
    if include_test and path!="README.md":
      command=("python -m pytest tests/test_auth.py -q" if "auth" in path else
        "python -m pytest tests/test_tasks.py -q")
      passed=18 if "auth" in path else 8
      refs=["O-TEST-COMMAND","O-ARTIFACT"] if "auth" in path else ["O-TEST-EXPLANATION"]
      content=_typed(case,"test_result",head,refs,command=command,
        environment="deterministic demo fixture",result_summary=f"{passed} passed, 0 failed",
        exit_code=0,tests_passed=passed,tests_failed=0,affected_scope=[path],
        source_tool="pytest")
      result.append({"type":"test_result","title":"测试记录","content":content,
        "source_tool":"pytest","command":command,"environment":"deterministic demo fixture",
        "result_summary":f"{passed} passed, 0 failed","exit_code":0,
        "tests_passed":passed,"tests_failed":0,"affected_scope":[path],
        "observed_at":FIXED_TIME,"obligation_refs":refs})
    if conflict:
      result.append(_artifact(case,"contribution_declaration","贡献者声明",head,["O-AGENT-SCOPE"],
        source_tool="contributor-declaration",other_agents_or_tools_used=False,
        declared_tools=[],declaration_scope=[path],declared_by="demo contributor",
        statement="没有使用其他助手或自动化工具。"))
    return result

def _open(service,slug,path,profile):
    case,_=service.open_case([path],requested_mode="declared_agent_mediated" if profile!="human_direct" else "maintainer_requested",actor="contributor",actor_role="contributor",case_id="case-"+slug,base_commit="d"*40,autonomy_profile=profile,timestamp=FIXED_TIME);assert case;return case
def _bridge(service,case,arts,*,submit=True,head_commit="c"*40):
    receipt=SidecarEvidenceStore(service.root).write_package(case_id=case.id,contribution_fingerprint=case.contribution_fingerprint,policy_fingerprint=case.policy_snapshot.policy_fingerprint,producer="deterministic-scenario",created_at=FIXED_TIME,base_commit_sha=case.base_commit,head_commit_sha=head_commit,artifacts=arts)
    SidecarEvidenceBridge(service).register_package(case.id,package_digest=receipt.package_digest)
    if submit: service.prepare_case(case.id,actor="contributor",actor_role="contributor")
    return receipt
def _attest(service,case):return service.attest(case.id,actor="contributor-human",role="accountable_human",reviewed_scope=case.changed_files,statement="已检查当前版本的代码差异和测试结果。",timestamp=FIXED_TIME)

def build_scenario(service,slug,path,profile,mode):
    case=_open(service,slug,path,profile); package=None
    package=_bridge(service,case,_artifacts(case,path,profile,"c"*40,include_test=mode!="missing",conflict=mode in {"conflict","repair"}),submit=mode!="waiting")
    if mode=="ready":
      if any(item.type=="human_attestation" for item in service.storage.load_case(case.id).obligations):_attest(service,case)
    elif mode in {"conflict","repair"}:
      if mode=="repair":service.request_repair(case.id,actor="maintainer-reviewer",role="maintainer",message="请核对并修正工具使用声明。",affected_obligation_ids=["O-AGENT-SCOPE"])
    elif mode=="stale":
      service.request_repair(case.id,actor="maintainer-reviewer",role="maintainer",message="请更新测试记录。",affected_obligation_ids=["O-TEST-EXPLANATION"])
      service.resubmit(case.id,actor="contributor",role="contributor",summary="提交新版本。",affected_obligation_ids=["O-TEST-EXPLANATION"],diff_material="new deterministic contribution",change_classification="material")
      current=service.storage.load_case(case.id)
      _bridge(service,current,_artifacts(current,path,profile,"e"*40,include_test=False),submit=False,head_commit="e"*40)
    elif mode=="denied":
      try:service.verify(case.id,actor="coding-agent",role="contributor_agent",reason="无权验证",timestamp=FIXED_TIME)
      except VNextError:pass
    elif mode=="final":
      service.verify(case.id,actor="maintainer-reviewer",role="maintainer",reason="已检查当前材料。",timestamp=FIXED_TIME);service.decide(case.id,actor="final-maintainer",role="maintainer",decision="accept",reason="AGM 审查建议可以接受。",timestamp=FIXED_TIME)
      final=service.storage.load_case(case.id).final_decision; store=SidecarEvidenceStore(service.root);store.write_final_receipt(FinalEvidenceReceipt(case.contribution_fingerprint,case.policy_snapshot.policy_fingerprint,package.package_digest,"低风险文档修改","未检测到可验证记录","不适用","已完成必要检查","建议接受",{"connected":False,"approval_state":"not_performed","merge_state":"not_performed","close_state":"not_performed","verified":True},FIXED_TIME,case.id,final.id))
    return case.id,{"summary":_summary(path)}

def generate(output):
 output.mkdir(parents=True,exist_ok=True)
 expected={item[0] for item in SCENARIOS}
 for directory in output.iterdir():
  if directory.is_dir() and directory.name not in expected:shutil.rmtree(directory)
 hashes={};results=[]
 with tempfile.TemporaryDirectory(prefix="agm-pr-diagnostic-") as raw:
  for slug,path,profile,mode in SCENARIOS:
   with use_execution_context(DemoExecutionContext("pr-"+slug,FIXED_TIME,"demo-key")):
    root=make_project(Path(raw),slug);service=GovernanceService(root);case_id,ctx=build_scenario(service,slug,path,profile,mode);view=service.pr_diagnosis(case_id,contribution=ctx);scenario=output/slug
    for name,text in {"diagnosis.json":render_pr_diagnostic_json(view),"report.md":render_pr_diagnostic_markdown(view),"report.html":render_pr_diagnostic_html(view),"case.json":json.dumps(service.storage.load_case(case_id).to_dict(),ensure_ascii=False,indent=2)+"\n"}.items():
      target=scenario/name;atomic_write_text(target,text);hashes[target.relative_to(output).as_posix()]=hashlib.sha256(text.encode()).hexdigest()
    results.append({"scenario":slug,"case_state":service.storage.load_case(case_id).state})
 atomic_write_text(output/"expected_sha256.json",json.dumps(hashes,ensure_ascii=False,indent=2,sort_keys=True)+"\n");return results
if __name__=="__main__":print(json.dumps({"generated":generate(ROOT/"examples"/"pr_native_diagnostic"/"outputs")},ensure_ascii=False,indent=2))
