"""Immutable local sidecar packages, isolated from tracked project source."""
from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from ..models import VNextError, canonical_json, fingerprint, utc_now
from ..storage import atomic_write_text

@dataclass(frozen=True)
class EvidenceArtifactRef:
    artifact_type: str; content_digest: str; summary: str
@dataclass(frozen=True)
class EvidencePackageReceipt:
    case_id: str; contribution_fingerprint: str; policy_fingerprint: str; package_digest: str; created_at: str; producer: str; artifact_list: tuple[EvidenceArtifactRef,...]
@dataclass(frozen=True)
class FinalEvidenceReceipt:
    contribution_fingerprint: str; policy_fingerprint: str; evidence_package_digest: str; risk_summary: str; agent_involvement: str; contributor_self_review_status: str; maintainer_review_status: str; agm_final_recommendation: str; host_platform_status: dict[str,Any]; created_at: str
def _safe(value: Any)->None:
    text=canonical_json(value).lower()
    if any(token in text for token in ("chain of thought","chain-of-thought","raw prompt","authorization: bearer","api_key","password=")): raise VNextError("Evidence package contains prohibited private or secret-like content")
def _validate_host(status: dict[str,Any])->None:
    permitted={"connected":False,"approval_state":"not_performed","merge_state":"not_performed","close_state":"not_performed","verified":True}
    if any(status.get(key)!=value for key,value in permitted.items()): raise VNextError("Host-platform status requires verified adapter evidence; no local adapter exists")
class SidecarEvidenceStore:
    def __init__(self,root:Path): self.project_root=root.resolve(); self.root=(self.project_root/".agm-work"/"evidence_store").resolve()
    def write_package(self,*,case_id:str,contribution_fingerprint:str,policy_fingerprint:str,producer:str,artifacts:list[dict[str,Any]],created_at:str|None=None)->EvidencePackageReceipt:
        _safe(artifacts); payload={"case_id":case_id,"contribution_fingerprint":contribution_fingerprint,"policy_fingerprint":policy_fingerprint,"created_at":created_at or utc_now(),"producer":producer,"artifacts":artifacts}; digest=fingerprint(payload); path=self.root/digest/"package.json"; encoded=canonical_json(payload)+"\n"
        if path.exists() and path.read_text(encoding="utf8")!=encoded: raise VNextError("Evidence package digest collision")
        if not path.exists(): atomic_write_text(path,encoded)
        refs=tuple(EvidenceArtifactRef(str(a.get("type","artifact")),fingerprint(a),str(a.get("summary",""))) for a in artifacts)
        return EvidencePackageReceipt(case_id,contribution_fingerprint,policy_fingerprint,digest,payload["created_at"],producer,refs)
    def read_package(self,digest:str)->dict[str,Any]:
        if not digest or "/" in digest or "\\" in digest: raise VNextError("Invalid evidence package digest")
        path=(self.root/digest/"package.json").resolve()
        if self.root not in path.parents or not path.is_file(): raise VNextError("Evidence package is unavailable")
        return json.loads(path.read_text(encoding="utf8"))
    def packages_for_contribution(self,fingerprint_value:str)->list[dict[str,Any]]:
        return [self.read_package(path.parent.name) for path in sorted(self.root.glob("*/package.json")) if self.read_package(path.parent.name)["contribution_fingerprint"]==fingerprint_value]
    def write_final_receipt(self,receipt:FinalEvidenceReceipt)->Path:
        _safe(asdict(receipt)); _validate_host(receipt.host_platform_status); digest=fingerprint(asdict(receipt)); path=self.root/"receipts"/f"{digest}.json"; encoded=canonical_json(asdict(receipt))+"\n"
        if path.exists() and path.read_text(encoding="utf8")!=encoded: raise VNextError("Final receipt digest collision")
        if not path.exists(): atomic_write_text(path,encoded)
        return path
