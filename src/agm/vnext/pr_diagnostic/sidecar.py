"""Immutable, traversal-safe sidecar evidence packages outside tracked source."""
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
    case_id: str; contribution_fingerprint: str; policy_fingerprint: str; package_digest: str; created_at: str; producer: str; artifact_list: tuple[EvidenceArtifactRef, ...]

def _safe(value: Any) -> None:
    text = canonical_json(value).lower()
    prohibited = ("chain of thought", "chain-of-thought", "raw prompt", "authorization: bearer", "api_key", "password=")
    if any(token in text for token in prohibited): raise VNextError("Evidence package contains prohibited private or secret-like content")

class SidecarEvidenceStore:
    def __init__(self, root: Path):
        self.root = (root / ".agm-work" / "evidence_store").resolve()

    def write_package(self, *, case_id: str, contribution_fingerprint: str, policy_fingerprint: str, producer: str, artifacts: list[dict[str, Any]], created_at: str | None = None) -> EvidencePackageReceipt:
        _safe(artifacts)
        payload = {"case_id": case_id, "contribution_fingerprint": contribution_fingerprint, "policy_fingerprint": policy_fingerprint, "created_at": created_at or utc_now(), "producer": producer, "artifacts": artifacts}
        digest = fingerprint(payload); path = self.root / digest / "package.json"
        if path.exists():
            if path.read_text(encoding="utf-8") != canonical_json(payload) + "\n": raise VNextError("Evidence package digest collision")
        else: atomic_write_text(path, canonical_json(payload) + "\n")
        refs = tuple(EvidenceArtifactRef(str(a.get("type", "artifact")), fingerprint(a), str(a.get("summary", ""))) for a in artifacts)
        return EvidencePackageReceipt(case_id, contribution_fingerprint, policy_fingerprint, digest, payload["created_at"], producer, refs)

    def write_final_receipt(self, receipt: dict[str, Any]) -> Path:
        _safe(receipt); digest = fingerprint(receipt); path = self.root / "receipts" / f"{digest}.json"; atomic_write_text(path, canonical_json(receipt) + "\n"); return path
