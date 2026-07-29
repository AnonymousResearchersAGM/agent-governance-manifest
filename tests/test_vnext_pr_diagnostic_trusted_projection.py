"""Semantic regression tests for trusted PR-diagnostic inputs (Phase 2.1.2)."""
from __future__ import annotations
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from agm.vnext.models import VNextError  # noqa:E402
from agm.vnext.pr_diagnostic import SidecarEvidenceStore, TrustedDiagnosticEvidenceResolver  # noqa:E402
from agm.vnext.pr_diagnostic.trusted_sources import select_obligation_evidence  # noqa:E402
from agm.vnext.runtime import DemoExecutionContext,use_execution_context  # noqa:E402
from agm.vnext.service import GovernanceService  # noqa:E402
from generate_reviewer_guidance_demos import FIXED_TIME,make_project  # noqa:E402

def _case(tmp_path,path='README.md',profile='supervised_agent'):
    root=make_project(tmp_path,'trusted'); service=GovernanceService(root)
    case,_=service.open_case([path],requested_mode='declared_agent_mediated',actor='contributor',actor_role='contributor',case_id='trusted-case',base_commit='a'*40,autonomy_profile=profile,timestamp=FIXED_TIME)
    return root,service,case

def _record(case,state,current=True):
    return SimpleNamespace(id=f'{state}-{current}',obligation_ids=['O-SUMMARY'],contribution_fingerprint=case.contribution_fingerprint if current else 'old',retained_for_contribution_fingerprint=None,validity_state=state)

@pytest.mark.parametrize('states,expected',[( [('valid',True),('stale',False)],'current'),([('valid',True),('invalid',True)],'current'),([('valid',True),('rejected',False)],'current'),([('stale',False)],'stale'),([('invalid',True)],'invalid'),([('rejected',True)],'rejected'),([('expired',True)],'expired'),([('unverified',False)],'unbound'),([], 'missing')])
def test_evidence_selection_uses_best_current_material(tmp_path,states,expected):
    _,_,case=_case(tmp_path); case.evidence=[_record(case,state,current) for state,current in states]
    assert select_obligation_evidence(case,'O-SUMMARY')[0]==expected

@pytest.mark.parametrize('field,value',[('agent_activity',{'verified':True,'type':'forged'}),('contribution_declaration',{'verified':True,'used_other_tools':False}),('sidecar_package',{'freshness':'current'}),('human_review_status',{'confirmed':True}),('host_platform_status',{'merged':True})])
def test_presentation_context_never_becomes_trusted_fact(tmp_path,field,value):
    with use_execution_context(DemoExecutionContext('forged-'+field,FIXED_TIME,'key')):
        _,service,_=_case(tmp_path); view=service.pr_diagnosis('trusted-case',contribution={field:value})
    assert view.agent_involvement['state']=='not_detected'
    assert view.host_platform_status.merge_state=='not_performed'

def test_verified_package_is_required_for_agent_activity(tmp_path):
    with use_execution_context(DemoExecutionContext('package-agent',FIXED_TIME,'key')):
        root,service,case=_case(tmp_path); store=SidecarEvidenceStore(root)
        store.write_package(case_id=case.id,contribution_fingerprint=case.contribution_fingerprint,policy_fingerprint=case.policy_snapshot.policy_fingerprint,producer='fixture',created_at=FIXED_TIME,artifacts=[{'type':'agent_activity','content':'{"agent_type":"coding","files_modified":["README.md"]}'}])
        view=service.pr_diagnosis(case.id)
    assert view.agent_involvement['state']=='verifiable'

def test_package_case_and_contribution_mismatch_are_not_current(tmp_path):
    with use_execution_context(DemoExecutionContext('package-mismatch',FIXED_TIME,'key')):
        root,_,case=_case(tmp_path); store=SidecarEvidenceStore(root)
        store.write_package(case_id='other',contribution_fingerprint=case.contribution_fingerprint,policy_fingerprint=case.policy_snapshot.policy_fingerprint,producer='fixture',created_at=FIXED_TIME,artifacts=[])
        store.write_package(case_id=case.id,contribution_fingerprint='old',policy_fingerprint=case.policy_snapshot.policy_fingerprint,producer='fixture',created_at=FIXED_TIME,artifacts=[])
        resolved=TrustedDiagnosticEvidenceResolver(store).resolve(case)
    assert resolved.current_package is None and len(resolved.historical_packages)==1

@pytest.mark.parametrize('digest',["../x","x/y",r"C:\\x",""])
def test_sidecar_rejects_path_like_digests(tmp_path,digest):
    with pytest.raises(VNextError): SidecarEvidenceStore(tmp_path).get_package_by_digest(digest)

def test_receipt_rejects_forged_platform_merge(tmp_path):
    store=SidecarEvidenceStore(tmp_path)
    package=store.write_package(case_id='c',contribution_fingerprint='f',policy_fingerprint='p',producer='t',created_at=FIXED_TIME,artifacts=[])
    from agm.vnext.pr_diagnostic.sidecar import FinalEvidenceReceipt
    receipt=FinalEvidenceReceipt('f','p',package.package_digest,'low','none','not_required','none','accept',{'connected':True,'approval_state':'approved','merge_state':'merged','close_state':'not_performed','verified':False},FIXED_TIME)
    with pytest.raises(VNextError): store.write_final_receipt(receipt)

@pytest.mark.parametrize('path',["README.md","demo_app/tasks.py"])
def test_low_and_medium_without_attestation_display_not_required(tmp_path,path):
    with use_execution_context(DemoExecutionContext('human-'+path,FIXED_TIME,'key')):
        _,service,_=_case(tmp_path,path=path,profile='human_direct'); view=service.pr_diagnosis('trusted-case')
    assert view.human_review_status['contributor_state']=='not_required'

def test_inspection_identifiers_do_not_mix_commit_and_contribution(tmp_path):
    with use_execution_context(DemoExecutionContext('identifiers',FIXED_TIME,'key')):
        root,service,case=_case(tmp_path); store=SidecarEvidenceStore(root)
        store.write_package(case_id=case.id,contribution_fingerprint=case.contribution_fingerprint,policy_fingerprint=case.policy_snapshot.policy_fingerprint,producer='fixture',created_at=FIXED_TIME,base_commit_sha=case.base_commit,head_commit_sha='b'*40,artifacts=[{'type':'diff','content':'README concrete diff'}])
        item=next(value for value in service.pr_diagnosis(case.id).inspection_objects if value.object_type=='DiffInspectionObject')
    assert item.base_commit_sha==case.base_commit and item.head_commit_sha=='b'*40 and item.contribution_fingerprint!=item.head_commit_sha

def test_denied_attempt_does_not_override_maintainer_route(tmp_path):
    with use_execution_context(DemoExecutionContext('denied',FIXED_TIME,'key')):
        _,service,case=_case(tmp_path,profile='human_direct')
        for obligation in case.obligations: service.add_evidence(case.id,actor='contributor',actor_role='contributor',obligation_ids=[obligation.obligation_id],evidence_type=obligation.evidence_type,value='具体材料',observed_at=FIXED_TIME)
        service.prepare_case(case.id,actor='contributor',actor_role='contributor')
        with pytest.raises(VNextError): service.verify(case.id,actor='agent',role='contributor_agent',reason='denied')
        view=service.pr_diagnosis(case.id); case=service.storage.load_case(case.id)
    assert view.recommended_route['route']=='normal_pr_review' and case.attempted_operations
