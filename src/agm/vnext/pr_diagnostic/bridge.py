"""One-way bridge from a verified sidecar package to canonical evidence.

The bridge intentionally does not mutate a case.  Every evidence record goes
through :meth:`GovernanceService.add_evidence`, so validation, binding,
obligation recompilation and audit behaviour remain canonical.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..models import GovernanceCase, VNextError, fingerprint
from ..service import GovernanceService
from .sidecar import SidecarEvidenceStore
from .diff_parser import parse_verified_diff

# A sidecar object is a transport type; it is not an alternative obligation
# schema.  This mapping deliberately permits only canonical evidence types.
ARTIFACT_COMPATIBILITY: dict[str, set[str]] = {
    "test_result": {"O-TEST-COMMAND", "O-ARTIFACT", "O-TEST-EXPLANATION"},
    "agent_activity": {"O-AGENT-SCOPE"},
    "impact_statement": {"O-AUTH-IMPACT", "O-POLICY-IMPACT"},
    "contribution_declaration": {"O-SUMMARY", "O-RATIONALE"},
    "supporting_statement": {"O-SUMMARY", "O-CHANGED-FILES", "O-RATIONALE", "O-LIMITATIONS", "O-TEST-EXPLANATION"},
    "diff": set(),
    "final_receipt": set(),
    "human_confirmation": set(),
}

CANONICAL_TYPES = {
    "test_result": {"O-TEST-COMMAND": "test_command", "O-ARTIFACT": "artifact", "O-TEST-EXPLANATION": "test_explanation"},
    "agent_activity": {"O-AGENT-SCOPE": "agent_action_scope"},
    "impact_statement": {"O-AUTH-IMPACT": "security_auth_impact", "O-POLICY-IMPACT": "policy_impact"},
    "contribution_declaration": {"O-SUMMARY": "contribution_summary", "O-RATIONALE": "rationale"},
    "supporting_statement": {"O-SUMMARY": "contribution_summary", "O-CHANGED-FILES": "changed_files", "O-RATIONALE": "rationale", "O-LIMITATIONS": "known_limitations", "O-TEST-EXPLANATION": "test_explanation"},
}

@dataclass(frozen=True)
class BridgeReceipt:
    package_digest: str
    case_id: str
    contribution_fingerprint: str
    evidence_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]
    audit_record: dict[str, Any]


class SidecarEvidenceBridge:
    def __init__(self, service: GovernanceService, store: SidecarEvidenceStore | None = None):
        self.service = service
        self.store = store or SidecarEvidenceStore(service.root)

    def register_package(self, case_id: str, *, package_digest: str, actor: str = "sidecar-bridge", role: str = "contributor_agent") -> BridgeReceipt:
        case = self.service.storage.load_case(case_id)
        package = self.store.get_package_by_digest(package_digest)  # digest validation
        if package.get("case_id") != case.id:
            raise VNextError("Evidence package case binding does not match")
        if package.get("policy_fingerprint") != case.policy_snapshot.policy_fingerprint:
            raise VNextError("Evidence package policy binding does not match")
        if package.get("contribution_fingerprint") != case.contribution_fingerprint:
            raise VNextError("Evidence package contribution binding does not match")
        evidence_ids: list[str] = []
        artifact_ids: list[str] = []
        for metadata in package["artifacts"]:
            artifact, content = self.store.read_artifact(package_digest, metadata["artifact_id"])
            self._validate_artifact(case, package, artifact, content)
            refs = list(artifact.get("obligation_refs", []))
            if not refs:
                continue  # inspection-only material is explicitly not evidence
            for obligation_id in refs:
                evidence_type = CANONICAL_TYPES[artifact["artifact_type"]][obligation_id]
                evidence_id = "sidecar-" + fingerprint({"package": package_digest, "artifact": artifact["artifact_id"], "obligation": obligation_id})[:24]
                item = self.service.add_evidence(
                    case.id, actor=actor, actor_role=role, obligation_ids=[obligation_id],
                    evidence_type=evidence_type, value=content,
                    affected_scope=case.obligation(obligation_id).affected_scope,
                    command=(content.splitlines()[0].replace("测试命令：", "") if evidence_type == "test_command" else None),
                    environment=("sidecar deterministic fixture" if evidence_type == "test_command" else None),
                    source_tool=artifact.get("source_tool") or "sidecar-evidence-bridge",
                    observed_at=artifact["created_at"], evidence_id=evidence_id,
                )
                evidence_ids.append(item.id)
            artifact_ids.append(artifact["artifact_id"])
        # Re-run the canonical compiler after registration before a caller may project it.
        self.service.prepare_case(case.id, actor=actor, actor_role=role)
        return BridgeReceipt(package_digest, case.id, case.contribution_fingerprint, tuple(evidence_ids), tuple(artifact_ids), {
            "event": "sidecar_evidence_bridge_registered", "case_id": case.id,
            "package_digest": package_digest, "evidence_ids": tuple(evidence_ids),
        })

    def _validate_artifact(self, case: GovernanceCase, package: dict[str, Any], artifact: dict[str, Any], content: str) -> None:
        if fingerprint(content) != artifact.get("content_digest"):
            raise VNextError("Evidence artifact digest verification failed")
        for field, expected in (("case_id", case.id), ("contribution_fingerprint", case.contribution_fingerprint), ("policy_fingerprint", case.policy_snapshot.policy_fingerprint)):
            if artifact.get(field) != expected:
                raise VNextError(f"Evidence artifact {field} binding does not match")
        artifact_type = artifact.get("artifact_type")
        if artifact_type not in ARTIFACT_COMPATIBILITY:
            raise VNextError("Evidence artifact type is not supported by the canonical bridge")
        refs = artifact.get("obligation_refs", [])
        unknown = set(refs) - {item.obligation_id for item in case.obligations}
        if unknown:
            raise VNextError("Evidence artifact references obligations not compiled for this case")
        incompatible = set(refs) - ARTIFACT_COMPATIBILITY[artifact_type]
        if incompatible:
            raise VNextError("Evidence artifact type is incompatible with referenced obligation")
        if artifact_type == "diff":
            parse_verified_diff(content)
