from __future__ import annotations
import json, sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from agm.vnext.pr_diagnostic.sidecar import FinalEvidenceReceipt, SidecarEvidenceStore  # noqa:E402
from agm.vnext.models import VNextError  # noqa:E402
from agm.vnext.runtime import DemoExecutionContext,use_execution_context  # noqa:E402
from agm.vnext.service import GovernanceService  # noqa:E402
from generate_pr_diagnostic_demos import SCENARIOS,build_scenario  # noqa:E402
from generate_reviewer_guidance_demos import FIXED_TIME,make_project  # noqa:E402

EXPECTED={"D1_low_risk_readme":("awaiting_maintainer_verification","normal_pr_review",0),"D2_high_risk_missing":("evidence_incomplete","contributor_action_required",0),"D3_high_risk_ready":("awaiting_maintainer_verification","maintainer_focused_review",2),"D4_no_agent_trace":("awaiting_maintainer_verification","normal_pr_review",0),"D5_no_agent_high_missing_test":("evidence_incomplete","contributor_action_required",0),"D6_declaration_conflict":("repair_requested","blocked_pending_repair",0),"D7_stale_test":("resubmitted","contributor_action_required",0),"D8_system_handled":("awaiting_maintainer_verification","normal_pr_review",0),"D9_contributor_waiting":("evidence_incomplete","waiting_for_contributor_submission",0),"D10_final_recommendation":("accepted","final_recommendation_recorded",0)}

@pytest.mark.parametrize("slug,path,profile,mode",SCENARIOS)
def test_each_scenario_is_a_legal_state_projection(tmp_path,slug,path,profile,mode):
    with use_execution_context(DemoExecutionContext('semantic-'+slug,FIXED_TIME,'key')):
        root=make_project(tmp_path,slug); service=GovernanceService(root); case_id,context=build_scenario(service,slug,path,profile,mode); case=service.storage.load_case(case_id); view=service.pr_diagnosis(case_id,contribution=context)
    expected_state,route,action_count=EXPECTED[slug]
    assert case.state==expected_state and view.recommended_route['route']==route and len(view.action_effect_boundaries)==action_count
    assert view.technical_derivation['case_state']==case.state
    assert all(item.source_state_refs for item in (*view.risk_findings,*view.evidence_gaps))
    if slug in {'D2_high_risk_missing','D3_high_risk_ready'}: assert any(o.object_type=='DiffInspectionObject' and o.availability=='available' for o in view.inspection_objects)
    if slug=='D3_high_risk_ready': assert {item['state'] for item in view.expected_requirements}=={'current'} and view.human_review_status['contributor_state']=='required_current'
    if slug=='D7_stale_test': assert [item['state'] for item in view.expected_requirements].count('stale')==1
    if slug=='D8_system_handled': assert case.attempted_operations and not view.action_effect_boundaries
    if slug=='D10_final_recommendation': assert case.final_decision and case.final_decision.decision=='accept'

def test_scenario_builders_do_not_mutate_domain_fields_directly():
    source=(ROOT/'scripts'/'generate_pr_diagnostic_demos.py').read_text(encoding='utf8')
    forbidden=('case.state =','case.final_decision =','case.attestations.append','case.evidence.append','contribution_fingerprint =')
    assert not any(token in source for token in forbidden)

def test_sidecar_receipt_is_typed_immutable_and_rejects_forged_merge(tmp_path):
    store=SidecarEvidenceStore(tmp_path); package=store.write_package(case_id='c',contribution_fingerprint='f',policy_fingerprint='p',producer='test',created_at=FIXED_TIME,artifacts=[{'type':'test','summary':'pytest result'}])
    assert store.read_package(package.package_digest)['contribution_fingerprint']=='f' and len(store.packages_for_contribution('f'))==1
    receipt=FinalEvidenceReceipt('f','p',package.package_digest,'low','not detected','current','verified','accept',{'connected':False,'approval_state':'not_performed','merge_state':'not_performed','close_state':'not_performed','verified':True},FIXED_TIME)
    assert store.write_final_receipt(receipt)==store.write_final_receipt(receipt)
    with pytest.raises(VNextError): store.write_final_receipt(FinalEvidenceReceipt('f','p',package.package_digest,'low','none','none','none','accept',{'connected':True,'approval_state':'approved','merge_state':'merged','close_state':'not_performed','verified':False},FIXED_TIME))

def test_participant_layer_uses_no_python_dict_or_english_requirement(tmp_path):
    with use_execution_context(DemoExecutionContext('terms',FIXED_TIME,'key')):
        root=make_project(tmp_path,'terms'); service=GovernanceService(root); case_id,context=build_scenario(service,*SCENARIOS[2]); page=service.pr_diagnosis(case_id,contribution=context)
    from agm.vnext.pr_diagnostic.presenters import render_pr_diagnostic_html
    visible=render_pr_diagnostic_html(page).split('<details>',1)[0]
    assert "{'verified'" not in visible
    assert 'Record the declared action' not in visible
