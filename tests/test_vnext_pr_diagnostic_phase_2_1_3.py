"""Semantic coverage for Phase 2.1.3's canonical evidence bridge."""
from __future__ import annotations
import json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/"src"),str(ROOT/"scripts")]
from agm.vnext.models import VNextError
from agm.vnext.pr_diagnostic import SidecarEvidenceBridge,SidecarEvidenceStore
from agm.vnext.pr_diagnostic.diff_parser import parse_verified_diff
from agm.vnext.pr_diagnostic.server import _safe_segment
from agm.vnext.runtime import DemoExecutionContext,use_execution_context
from agm.vnext.service import GovernanceService
from generate_reviewer_guidance_demos import FIXED_TIME,make_project
from generate_pr_diagnostic_demos import SCENARIOS,build_scenario

def _case(tmp_path,path="demo_app/auth.py",profile="supervised_agent"):
 root=make_project(tmp_path,"p213");service=GovernanceService(root);case,_=service.open_case([path],requested_mode="declared_agent_mediated",actor="contributor",actor_role="contributor",case_id="p213",base_commit="a"*40,autonomy_profile=profile,timestamp=FIXED_TIME);return root,service,case
def _package(root,case,artifacts):return SidecarEvidenceStore(root).write_package(case_id=case.id,contribution_fingerprint=case.contribution_fingerprint,policy_fingerprint=case.policy_snapshot.policy_fingerprint,producer="fixture",created_at=FIXED_TIME,artifacts=artifacts)
def _diff():return "diff --git a/demo_app/auth.py b/demo_app/auth.py\n--- a/demo_app/auth.py\n+++ b/demo_app/auth.py\n@@ -84,1 +84,2 @@\n+    return False\n"

def test_bridge_registers_test_as_canonical_evidence(tmp_path):
 root,service,case=_case(tmp_path);p=_package(root,case,[{"type":"test_result","content":"python -m pytest tests/test_auth.py -q\n18 passed, 0 failed","source_tool":"pytest","command":"python -m pytest tests/test_auth.py -q","environment":"fixture","result_summary":"18 passed, 0 failed","affected_scope":["demo_app/auth.py"],"observed_at":FIXED_TIME,"obligation_refs":["O-TEST-COMMAND","O-ARTIFACT"]}]);receipt=SidecarEvidenceBridge(service).register_package(case.id,package_digest=p.package_digest)
 assert len(receipt.evidence_ids)==2 and all(item.validity_state=="valid" for item in service.storage.load_case(case.id).evidence)

@pytest.mark.parametrize("artifact,needle",[
 ({"type":"test_result","content":"x","obligation_refs":["O-NOPE"]},"compiled"),
 ({"type":"diff","content":_diff(),"obligation_refs":["O-TEST-COMMAND"]},"incompatible"),
 ({"type":"agent_activity","content":"{}","obligation_refs":["O-HUMAN-ATTEST"]},"incompatible"),
 ({"type":"impact_statement","content":"impact","obligation_refs":["O-TEST-COMMAND"]},"incompatible"),
 ({"type":"final_receipt","content":"receipt","obligation_refs":["O-TEST-COMMAND"]},"incompatible"),
])
def test_bridge_rejects_unknown_or_incompatible_refs(tmp_path,artifact,needle):
 root,service,case=_case(tmp_path);p=_package(root,case,[artifact])
 with pytest.raises(VNextError,match=needle):SidecarEvidenceBridge(service).register_package(case.id,package_digest=p.package_digest)

@pytest.mark.parametrize("field,value",[("case_id","other"),("contribution_fingerprint","old"),("policy_fingerprint","old")])
def test_bridge_rejects_package_bindings(tmp_path,field,value):
 root,service,case=_case(tmp_path);kwargs={"case_id":case.id,"contribution_fingerprint":case.contribution_fingerprint,"policy_fingerprint":case.policy_snapshot.policy_fingerprint};kwargs[field]=value
 p=SidecarEvidenceStore(root).write_package(producer="fixture",created_at=FIXED_TIME,artifacts=[],**kwargs)
 with pytest.raises(VNextError):SidecarEvidenceBridge(service).register_package(case.id,package_digest=p.package_digest)

@pytest.mark.parametrize("diff,expected",[
 (_diff(),("84",)),
 ("diff --git a/a.py b/b.py\nsimilarity index 90%\nrename from a.py\nrename to b.py\n--- a/a.py\n+++ b/b.py\n@@ -1 +1 @@\n-x\n+y\n",("1",)),
 ("diff --git a/x.py b/x.py\nnew file mode 100644\n--- /dev/null\n+++ b/x.py\n@@ -0,0 +1,1 @@\n+x\n",("1",)),
 ("diff --git a/x.py b/x.py\ndeleted file mode 100644\n--- a/x.py\n+++ /dev/null\n@@ -1,1 +0,0 @@\n-x\n",("1",)),
])
def test_verified_diff_locations_are_hunk_derived(diff,expected):
 assert parse_verified_diff(diff)[0].added or parse_verified_diff(diff)[0].removed
 assert (parse_verified_diff(diff)[0].added or parse_verified_diff(diff)[0].removed)==expected

@pytest.mark.parametrize("bad",["not a diff","diff --git a/../../x b/x\n--- a/x\n+++ b/x\n@@ -1 +1 @@\n-x\n+y\n","diff --git a/a b/a\n--- a/a\n+++ b/a\n"])
def test_malformed_diff_is_rejected(bad):
 with pytest.raises(VNextError):parse_verified_diff(bad)

@pytest.mark.parametrize("slug,route",[("D1_low_risk_readme","normal_pr_review"),("D2_high_risk_missing","contributor_action_required"),("D3_high_risk_ready","maintainer_focused_review"),("D6A_declaration_conflict","maintainer_action_required"),("D6B_repair_requested","contributor_action_required"),("D8_system_handled","normal_pr_review")])
def test_scenario_routes_are_canonical(tmp_path,slug,route):
 args=next(item for item in SCENARIOS if item[0]==slug)
 with use_execution_context(DemoExecutionContext("p213-"+slug,FIXED_TIME,"key")):
  root=make_project(tmp_path,slug);service=GovernanceService(root);case_id,ctx=build_scenario(service,*args);view=service.pr_diagnosis(case_id,contribution={"summary":"untrusted","changed_line_ranges":{"README.md":["999"]}})
 assert view.recommended_route["route"]==route
 if slug=="D3_high_risk_ready":assert all(item["state"]=="current" for item in view.expected_requirements)
 if slug=="D2_high_risk_missing":assert next(item for item in view.expected_requirements if item["obligation_ref"]=="O-TEST-COMMAND")["state"]=="missing"
 if slug=="D6A_declaration_conflict":assert view.technical_derivation["responsible_side"]==("maintainer",)

def test_producer_wording_does_not_claim_identity(tmp_path):
 args=next(item for item in SCENARIOS if item[0]=="D3_high_risk_ready")
 root=make_project(tmp_path,"wording");service=GovernanceService(root);case_id,ctx=build_scenario(service,*args);view=service.pr_diagnosis(case_id,contribution=ctx)
 assert "尚未通过" in view.agent_involvement["producer_assurance"] and "真实完成" not in view.agent_involvement["message"]

def test_final_receipt_never_crosses_case_boundary(tmp_path):
 root,service,case=_case(tmp_path,path="README.md")
 other,_=service.open_case(["README.md"],requested_mode="declared_agent_mediated",actor="contributor",actor_role="contributor",case_id="other",base_commit="a"*40,autonomy_profile="supervised_agent",timestamp=FIXED_TIME)
 assert other is not None
 from agm.vnext.pr_diagnostic.sidecar import FinalEvidenceReceipt
 store=SidecarEvidenceStore(root);package=_package(root,other,[])
 store.write_final_receipt(FinalEvidenceReceipt(other.contribution_fingerprint,other.policy_snapshot.policy_fingerprint,package.package_digest,"low","none","none","none","accept",{"connected":False,"approval_state":"not_performed","merge_state":"not_performed","close_state":"not_performed","verified":True},FIXED_TIME))
 assert not any(item.object_type=="FinalReceiptInspectionObject" for item in service.pr_diagnosis(case.id).inspection_objects)

@pytest.mark.parametrize("value",["..","%2e%2e","C:\\secret","/absolute","a/b"])
def test_artifact_route_rejects_pathlike_segments(value):
 assert not _safe_segment(value)

def test_bridge_is_idempotent_and_does_not_prepare_case(tmp_path):
 root,service,case=_case(tmp_path);p=_package(root,case,[{"type":"supporting_statement","content":"summary","affected_scope":["demo_app/auth.py"],"source_tool":"fixture","observed_at":FIXED_TIME,"obligation_refs":["O-SUMMARY"]}])
 first=SidecarEvidenceBridge(service).register_package(case.id,package_digest=p.package_digest)
 second=SidecarEvidenceBridge(service).register_package(case.id,package_digest=p.package_digest)
 loaded=service.storage.load_case(case.id)
 assert first.evidence_ids==second.evidence_ids and len(loaded.evidence)==1 and loaded.state=="evidence_incomplete"

def test_bridge_batch_failure_is_atomic(tmp_path):
 root,service,case=_case(tmp_path);p=_package(root,case,[{"type":"supporting_statement","content":"summary","affected_scope":["demo_app/auth.py"],"source_tool":"fixture","observed_at":FIXED_TIME,"obligation_refs":["O-SUMMARY"]},{"type":"diff","content":_diff(),"obligation_refs":["O-TEST-COMMAND"]}])
 with pytest.raises(VNextError):SidecarEvidenceBridge(service).register_package(case.id,package_digest=p.package_digest)
 assert not service.storage.load_case(case.id).evidence

def test_d7_historical_test_is_stale_and_current_diff_is_available(tmp_path):
 args=next(item for item in SCENARIOS if item[0]=="D7_stale_test")
 root=make_project(tmp_path,"d7");service=GovernanceService(root);case_id,_=build_scenario(service,*args);case=service.storage.load_case(case_id);view=service.pr_diagnosis(case_id)
 assert any(item.evidence_type=="test_explanation" and item.validity_state=="stale" for item in case.evidence)
 assert view.recommended_route["route"]=="contributor_action_required" and view.recommended_route["owner"]=="贡献者"
 assert any(item.object_type=="DiffInspectionObject" and item.availability=="available" for item in view.inspection_objects)
 assert any(item.title=="旧版本测试结果" and item.availability=="available" for item in view.inspection_objects)
