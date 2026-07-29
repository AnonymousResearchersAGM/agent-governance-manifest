"""Detect conflicts only from verified, bound sidecar material."""
from __future__ import annotations
import json
from ..models import VNextError, fingerprint
from ..service import GovernanceService
from .sidecar import SidecarEvidenceStore

class TrustedSidecarConflictDetector:
    def __init__(self, service: GovernanceService): self.service=service; self.store=SidecarEvidenceStore(service.root)
    def detect(self, case_id: str, package_digest: str):
        self.store.append_conflict_audit("detection_started",case_id=case_id,package_digest=package_digest)
        try:
            case=self.service.storage.load_case(case_id); package=self.store.get_package_by_digest(package_digest)
            if (package.get("case_id"),package.get("contribution_fingerprint"),package.get("policy_fingerprint")) != (case.id,case.contribution_fingerprint,case.policy_snapshot.policy_fingerprint): raise VNextError("Conflict package binding does not match current case")
            items={item["artifact_type"]:item for item in package["artifacts"]}; declaration=items.get("contribution_declaration"); activity=items.get("agent_activity")
            if not declaration or not activity:self.store.append_conflict_audit("no_conflict",case_id=case_id,package_digest=package_digest);return None
            if declaration["artifact_type"]!="contribution_declaration" or activity["artifact_type"]!="agent_activity":raise VNextError("Conflict artifact types are invalid")
            for artifact in (declaration,activity):
                if artifact.get("contribution_fingerprint")!=case.contribution_fingerprint or artifact.get("head_commit_sha")!=package.get("head_commit_sha"):raise VNextError("Conflict artifact binding does not match package")
            _,declared=self.store.read_artifact(package_digest,declaration["artifact_id"]); _,active=self.store.read_artifact(package_digest,activity["artifact_id"])
            d=json.loads(declared);a=json.loads(active); conflict=d.get("other_agents_or_tools_used") is False and a.get("other_agents_or_tools_used") is True
            expected=["sidecar-"+fingerprint({"package":package_digest,"artifact":x["artifact_id"],"obligation":o})[:24] for x,o in ((declaration,"O-SUMMARY"),(activity,"O-AGENT-SCOPE"))]
            if not set(expected)<= {item.id for item in case.evidence}:raise VNextError("Conflict canonical evidence mapping is unavailable")
            if not conflict:self.store.append_conflict_audit("no_conflict",case_id=case_id,package_digest=package_digest);return None
            before=len(case.findings); result=self.service.record_sidecar_conflict(case.id,actor="sidecar-conflict-detector",role="maintainer",message="贡献者声明与编码助手活动记录不一致。",source_evidence_ids=expected,source_artifact_ids=[declaration["artifact_id"],activity["artifact_id"]],affected_obligation_ids=["O-AGENT-SCOPE"],package_digest=package_digest)
            self.store.append_conflict_audit("conflict_already_recorded" if len(self.service.storage.load_case(case.id).findings)==before else "conflict_detected",case_id=case_id,package_digest=package_digest);return result
        except (VNextError,json.JSONDecodeError):
            self.store.append_conflict_audit("source_validation_rejected",case_id=case_id,package_digest=package_digest);raise
