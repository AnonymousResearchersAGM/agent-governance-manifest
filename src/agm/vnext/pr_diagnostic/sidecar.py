"""Immutable, validated runtime evidence packages for PR diagnosis.

The store deliberately lives below ``.agm-work``.  A package digest covers its
metadata and artifact digests; callers never get to assert that a package is
current or trusted through a presentation dictionary.
"""
from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ..models import VNextError, canonical_json, fingerprint, utc_now
from ..storage import atomic_write_text


@dataclass(frozen=True)
class EvidenceArtifactRef:
    artifact_id: str
    artifact_type: str
    title: str
    content_digest: str
    media_type: str
    size: int
    source_tool: str | None
    created_at: str
    contribution_fingerprint: str
    head_commit_sha: str | None
    relative_storage_path: str
    obligation_refs: tuple[str, ...] = ()
    case_id: str | None = None
    policy_fingerprint: str | None = None
    base_commit_sha: str | None = None
    producer: str | None = None
    command: str | None = None
    environment: str | None = None
    result_summary: str | None = None
    exit_code: int | None = None
    tests_passed: int | None = None
    tests_failed: int | None = None
    affected_scope: list[str] | None = None
    observed_at: str | None = None


@dataclass(frozen=True)
class EvidencePackageReceipt:
    case_id: str
    contribution_fingerprint: str
    policy_fingerprint: str
    package_digest: str
    created_at: str
    producer: str
    artifact_list: tuple[EvidenceArtifactRef, ...]


@dataclass(frozen=True)
class FinalEvidenceReceipt:
    contribution_fingerprint: str
    policy_fingerprint: str
    evidence_package_digest: str
    risk_summary: str
    agent_involvement: str
    contributor_self_review_status: str
    maintainer_review_status: str
    agm_final_recommendation: str
    host_platform_status: dict[str, Any]
    created_at: str
    case_id: str | None = None
    final_decision_id: str | None = None


def _safe(value: Any) -> None:
    text = canonical_json(value).lower()
    banned = ("chain of thought", "chain-of-thought", "raw prompt", "authorization: bearer", "api_key", "password=", "token=")
    if any(token in text for token in banned):
        raise VNextError("Evidence package contains prohibited private or secret-like content")


def _validate_host(status: dict[str, Any]) -> None:
    permitted = {"connected": False, "approval_state": "not_performed", "merge_state": "not_performed", "close_state": "not_performed", "verified": True}
    if any(status.get(key) != value for key, value in permitted.items()):
        raise VNextError("Host-platform status requires verified adapter evidence; no local adapter exists")


class SidecarEvidenceStore:
    _audit_lock = threading.Lock()
    def __init__(self, root: Path):
        self.project_root = root.resolve()
        self.root = (self.project_root / ".agm-work" / "evidence_store").resolve()

    def _package_path(self, digest: str) -> Path:
        if not digest or "/" in digest or "\\" in digest or ".." in digest:
            raise VNextError("Invalid evidence package digest")
        path = (self.root / digest / "package.json").resolve()
        if self.root not in path.parents:
            raise VNextError("Evidence package path escapes the sidecar store")
        return path

    def write_package(self, *, case_id: str, contribution_fingerprint: str,
                      policy_fingerprint: str, producer: str,
                      artifacts: list[dict[str, Any]], created_at: str | None = None,
                      base_commit_sha: str | None = None,
                      head_commit_sha: str | None = None) -> EvidencePackageReceipt:
        _safe(artifacts)
        when = created_at or utc_now()
        normalized: list[dict[str, Any]] = []
        contents: dict[str, str] = {}
        for position, raw in enumerate(artifacts):
            content = str(raw.get("content", raw.get("summary", "")))
            _safe(content)
            artifact_id = str(raw.get("artifact_id") or fingerprint({"case": case_id, "position": position, "type": raw.get("type", "artifact"), "content": content})[:24])
            if "/" in artifact_id or "\\" in artifact_id or ".." in artifact_id:
                raise VNextError("Invalid evidence artifact id")
            digest = fingerprint(content)
            obligation_refs = tuple(str(item) for item in raw.get("obligation_refs", ()))
            if len(set(obligation_refs)) != len(obligation_refs):
                raise VNextError("Evidence artifact obligation references must be unique")
            normalized.append({
                "artifact_id": artifact_id, "artifact_type": str(raw.get("type", "artifact")),
                "title": str(raw.get("title", raw.get("summary", "材料"))), "content_digest": digest,
                "media_type": str(raw.get("media_type", "text/plain")), "size": len(content.encode("utf8")),
                "source_tool": raw.get("source_tool"), "created_at": str(raw.get("created_at", when)),
                "contribution_fingerprint": contribution_fingerprint,
                "head_commit_sha": raw.get("head_commit_sha", head_commit_sha),
                "base_commit_sha": raw.get("base_commit_sha", base_commit_sha),
                "case_id": case_id, "policy_fingerprint": policy_fingerprint,
                "producer": raw.get("producer", producer), "obligation_refs": list(obligation_refs),
                "relative_storage_path": f"artifacts/{artifact_id}.txt",
                "command": raw.get("command"), "environment": raw.get("environment"),
                "result_summary": raw.get("result_summary"), "exit_code": raw.get("exit_code"),
                "tests_passed": raw.get("tests_passed"), "tests_failed": raw.get("tests_failed"),
                "affected_scope": list(raw.get("affected_scope", [])), "observed_at": raw.get("observed_at", raw.get("created_at", when)),
            })
            contents[artifact_id] = content
        payload = {"package_version": "agm.sidecar_evidence/v1", "case_id": case_id,
                   "contribution_fingerprint": contribution_fingerprint,
                   "base_commit_sha": base_commit_sha, "head_commit_sha": head_commit_sha,
                   "policy_fingerprint": policy_fingerprint, "producer": producer,
                   "created_at": when, "artifacts": normalized}
        digest = fingerprint(payload)
        payload["package_digest"] = digest
        path = self._package_path(digest)
        encoded = canonical_json(payload) + "\n"
        if path.exists() and path.read_text(encoding="utf8") != encoded:
            raise VNextError("Evidence package digest collision")
        if not path.exists():
            atomic_write_text(path, encoded)
            for artifact in normalized:
                artifact_path = (path.parent / artifact["relative_storage_path"]).resolve()
                if path.parent not in artifact_path.parents:
                    raise VNextError("Evidence artifact path escapes package")
                atomic_write_text(artifact_path, contents[artifact["artifact_id"]])
        refs = tuple(EvidenceArtifactRef(**item) for item in normalized)
        return EvidencePackageReceipt(case_id, contribution_fingerprint, policy_fingerprint, digest, when, producer, refs)

    def get_package_by_digest(self, digest: str) -> dict[str, Any]:
        path = self._package_path(digest)
        if not path.is_file():
            raise VNextError("Evidence package is unavailable")
        package = json.loads(path.read_text(encoding="utf8"))
        if package.get("package_digest") != digest or fingerprint({key: value for key, value in package.items() if key != "package_digest"}) != digest:
            raise VNextError("Evidence package digest verification failed")
        return package

    read_package = get_package_by_digest

    def verify_package_digest(self, digest: str) -> bool:
        self.get_package_by_digest(digest)
        return True

    def find_packages_for_case(self, case_id: str) -> list[dict[str, Any]]:
        return [self.get_package_by_digest(path.parent.name) for path in sorted(self.root.glob("*/package.json")) if self.get_package_by_digest(path.parent.name).get("case_id") == case_id]

    def find_packages_for_contribution(self, contribution_fingerprint: str) -> list[dict[str, Any]]:
        return [item for item in self._all_packages() if item.get("contribution_fingerprint") == contribution_fingerprint]

    packages_for_contribution = find_packages_for_contribution

    def _all_packages(self) -> list[dict[str, Any]]:
        return [self.get_package_by_digest(path.parent.name) for path in sorted(self.root.glob("*/package.json"))]

    def find_current_package(self, case_id: str, contribution_fingerprint: str) -> dict[str, Any] | None:
        items = [item for item in self.find_packages_for_case(case_id) if item.get("contribution_fingerprint") == contribution_fingerprint]
        return sorted(items, key=lambda item: (item.get("created_at", ""), item["package_digest"]), reverse=True)[0] if items else None

    def list_historical_packages(self, case_id: str, current_contribution_fingerprint: str | None = None) -> list[dict[str, Any]]:
        return [item for item in self.find_packages_for_case(case_id) if item.get("contribution_fingerprint") != current_contribution_fingerprint]

    def read_artifact(self, package_digest: str, artifact_id: str) -> tuple[dict[str, Any], str]:
        package = self.get_package_by_digest(package_digest)
        artifact = next((item for item in package["artifacts"] if item["artifact_id"] == artifact_id), None)
        if artifact is None or "/" in artifact_id or "\\" in artifact_id or ".." in artifact_id:
            raise VNextError("Evidence artifact is unavailable")
        path = (self._package_path(package_digest).parent / artifact["relative_storage_path"]).resolve()
        if self._package_path(package_digest).parent not in path.parents or not path.is_file():
            raise VNextError("Evidence artifact is unavailable")
        content = path.read_text(encoding="utf8")
        if fingerprint(content) != artifact["content_digest"]:
            raise VNextError("Evidence artifact digest verification failed")
        return artifact, content

    def record_read_access(self, *, case_id: str, package_digest: str, artifact_id: str) -> None:
        """Append a minimal local audit fact without exposing storage details."""
        path = self.root / "read_audit.jsonl"; path.parent.mkdir(parents=True, exist_ok=True)
        line = canonical_json({"case_id":case_id,"package_digest":package_digest,"artifact_id":artifact_id,"access":"read"}) + "\n"
        for attempt in range(3):
            try:
                with self._audit_lock, path.open("a", encoding="utf8") as handle:
                    handle.write(line); handle.flush(); os.fsync(handle.fileno())
                return
            except PermissionError:
                if attempt == 2: raise
                time.sleep(0.02 * (attempt + 1))

    def write_final_receipt(self, receipt: FinalEvidenceReceipt) -> Path:
        _safe(asdict(receipt)); _validate_host(receipt.host_platform_status)
        self.get_package_by_digest(receipt.evidence_package_digest)
        digest = fingerprint(asdict(receipt)); path = self.root / "receipts" / f"{digest}.json"; encoded = canonical_json(asdict(receipt)) + "\n"
        if path.exists() and path.read_text(encoding="utf8") != encoded: raise VNextError("Final receipt digest collision")
        if not path.exists(): atomic_write_text(path, encoded)
        return path

    def write_bridge_receipt(self, payload: dict[str, Any]) -> Path:
        payload = dict(payload); digest = fingerprint(payload)
        path = self.root / "bridge_receipts" / f"{digest}.json"; encoded = canonical_json(payload) + "\n"
        if path.exists() and path.read_text(encoding="utf8") != encoded: raise VNextError("Bridge receipt digest collision")
        if not path.exists(): atomic_write_text(path, encoded)
        audit = self.root / "bridge_audit.jsonl"; audit.parent.mkdir(parents=True, exist_ok=True)
        with self._audit_lock, audit.open("a", encoding="utf8") as handle:
            handle.write(canonical_json({"event":payload["registration_status"],"receipt_digest":digest,"case_id":payload["case_id"],"package_digest":payload["package_digest"]})+"\n"); handle.flush(); os.fsync(handle.fileno())
        return path

    def append_conflict_audit(self, event: str, *, case_id: str, package_digest: str) -> None:
        path=self.root/"conflict_audit.jsonl"; path.parent.mkdir(parents=True,exist_ok=True)
        line=canonical_json({"event":event,"case_id":case_id,"package_digest":package_digest})+"\n"
        for attempt in range(3):
            try:
                with self._audit_lock,path.open("a",encoding="utf8") as handle:
                    handle.write(line);handle.flush();os.fsync(handle.fileno())
                return
            except PermissionError:
                if attempt==2:raise
                time.sleep(.02*(attempt+1))

    def verify_receipt(self, receipt_digest: str) -> dict[str, Any]:
        if not receipt_digest or "/" in receipt_digest or "\\" in receipt_digest or ".." in receipt_digest: raise VNextError("Invalid receipt digest")
        path = (self.root / "receipts" / f"{receipt_digest}.json").resolve()
        if self.root not in path.parents or not path.is_file(): raise VNextError("Final receipt is unavailable")
        payload = json.loads(path.read_text(encoding="utf8"))
        if fingerprint(payload) != receipt_digest: raise VNextError("Final receipt digest verification failed")
        _validate_host(payload["host_platform_status"])
        return payload
