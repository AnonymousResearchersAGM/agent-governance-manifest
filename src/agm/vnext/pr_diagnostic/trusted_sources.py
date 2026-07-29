"""Trusted inputs for the PR diagnostic projection.

Presentation context is intentionally absent from this module.  It resolves
only canonical case records, legal attestations, and digest-verified sidecar
artifacts that bind to the current contribution and policy snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..models import GovernanceCase, VNextError, fingerprint
from .sidecar import SidecarEvidenceStore


@dataclass(frozen=True)
class TrustedArtifact:
    artifact_id: str
    artifact_type: str
    title: str
    content: str
    content_digest: str
    package_digest: str
    contribution_fingerprint: str
    head_commit_sha: str | None
    media_type: str
    obligation_refs: tuple[str, ...]
    producer_assurance: str


@dataclass(frozen=True)
class TrustedDiagnosticEvidenceSet:
    current_package: dict[str, Any] | None
    historical_packages: tuple[dict[str, Any], ...]
    artifacts: tuple[TrustedArtifact, ...]
    agent_activity: TrustedArtifact | None
    contribution_declaration: TrustedArtifact | None
    tests: tuple[TrustedArtifact, ...]
    diffs: tuple[TrustedArtifact, ...]
    human_confirmations: tuple[Any, ...]
    final_receipt: dict[str, Any] | None
    host_platform_status: dict[str, Any]


class TrustedDiagnosticEvidenceResolver:
    def __init__(self, store: SidecarEvidenceStore): self.store = store

    def resolve(self, case: GovernanceCase) -> TrustedDiagnosticEvidenceSet:
        current = self.store.find_current_package(case.id, case.contribution_fingerprint)
        historical = tuple(self.store.list_historical_packages(case.id, case.contribution_fingerprint))
        artifacts: list[TrustedArtifact] = []
        if current:
            if current.get("policy_fingerprint") != case.policy_snapshot.policy_fingerprint:
                raise VNextError("Current evidence package policy binding does not match case")
            for metadata in current["artifacts"]:
                artifact, content = self.store.read_artifact(current["package_digest"], metadata["artifact_id"])
                if artifact["contribution_fingerprint"] != case.contribution_fingerprint:
                    raise VNextError("Current evidence artifact contribution binding does not match case")
                artifacts.append(TrustedArtifact(artifact["artifact_id"], artifact["artifact_type"], artifact["title"], content, artifact["content_digest"], current["package_digest"], artifact["contribution_fingerprint"], artifact.get("head_commit_sha"), artifact["media_type"], tuple(artifact.get("obligation_refs", ())), "producer_declared"))
        by_type: dict[str, list[TrustedArtifact]] = {}
        for item in artifacts: by_type.setdefault(item.artifact_type, []).append(item)
        receipt = None
        # Receipts are trusted only when their digest and all bindings validate.
        for candidate in self.store.root.joinpath("receipts").glob("*.json") if self.store.root.joinpath("receipts").is_dir() else ():
            try: value = self.store.verify_receipt(candidate.stem)
            except VNextError: continue
            try:
                receipt_package = self.store.get_package_by_digest(value["evidence_package_digest"])
            except VNextError:
                continue
            if (receipt_package.get("case_id") == case.id
                and value["contribution_fingerprint"] == case.contribution_fingerprint
                and value["policy_fingerprint"] == case.policy_snapshot.policy_fingerprint):
                receipt = value
        confirmations = tuple(item for item in case.attestations if item.status == "confirmed" and item.policy_fingerprint == case.policy_snapshot.policy_fingerprint)
        return TrustedDiagnosticEvidenceSet(current, historical, tuple(artifacts),
            next(iter(by_type.get("agent_activity", ())), None),
            next(iter(by_type.get("contribution_declaration", ())), None),
            tuple(by_type.get("test_result", ())), tuple(by_type.get("diff", ())),
            confirmations, receipt,
            {"connected": False, "approval_state": "not_performed", "merge_state": "not_performed", "close_state": "not_performed", "verified": True})


def select_obligation_evidence(case: GovernanceCase, obligation_id: str) -> tuple[str, tuple[Any, ...]]:
    """Choose the strongest canonical evidence state without stale pollution."""
    records = [item for item in case.evidence if obligation_id in item.obligation_ids]
    if not records: return "missing", ()
    def state(item: Any) -> str:
        if item.contribution_fingerprint == case.contribution_fingerprint or item.retained_for_contribution_fingerprint == case.contribution_fingerprint:
            if item.validity_state in {"valid", "verified"}: return "current"
        if item.validity_state == "conflicting": return "invalid"
        if item.validity_state in {"rejected", "expired", "stale", "invalid"}: return item.validity_state
        return "unbound"
    priority = {"current": 0, "rejected": 1, "expired": 2, "stale": 3, "invalid": 4, "unbound": 5}
    grouped = sorted(((state(item), item) for item in records), key=lambda pair: (priority[pair[0]], pair[1].id))
    selected_state = grouped[0][0]
    return selected_state, tuple(item for status, item in grouped if status == selected_state)
