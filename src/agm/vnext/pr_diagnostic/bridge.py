"""Transactional bridge from verified typed sidecar material to canonical state."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ..models import VNextError, fingerprint
from ..service import GovernanceService
from .artifact_schemas import (
    CANONICAL_TYPES,
    TypedArtifactValidator,
    ValidatedArtifact,
)
from .conflicts import TrustedSidecarConflictDetector
from .sidecar import SidecarEvidenceStore
from .transaction import PackageIngestionTransaction


@dataclass(frozen=True)
class BridgeReceipt:
    package_digest: str
    case_id: str
    contribution_fingerprint: str
    evidence_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]
    audit_record: dict[str, Any]
    registration_status: str = "completed"


class SidecarEvidenceBridge:
    def __init__(
        self,
        service: GovernanceService,
        store: SidecarEvidenceStore | None = None,
        *,
        fault_injector: Callable[[str], None] | None = None,
    ):
        self.service = service
        self.store = store or SidecarEvidenceStore(service.root)
        self.transaction = PackageIngestionTransaction(
            service, self.store, fault_injector
        )

    def _evidence_id(
        self, package_digest: str, artifact_id: str, obligation_id: str
    ) -> str:
        return "sidecar-" + fingerprint(
            {
                "package": package_digest,
                "artifact": artifact_id,
                "obligation": obligation_id,
            }
        )[:24]

    def _entry(
        self,
        item: ValidatedArtifact,
        package_digest: str,
        obligation_id: str,
    ) -> dict[str, Any]:
        value: Any = item.typed_value
        scope = list(item.validated_scope)
        if obligation_id == "O-AGENT-SCOPE":
            value = {
                "artifact_type": item.artifact_type,
                "validated_typed_scope": sorted(scope),
                "canonical_contribution_scope": list(item.canonical_scope),
                "coverage_relation": item.coverage_relation,
                "scope_source": item.scope_source,
                "typed_source_validated": True,
            }
        if item.artifact_type == "unified_diff":
            value = {
                "files": list(item.derived_files),
                "derived_from_artifact_id": item.artifact_id,
                "derivation_method": "verified_unified_diff_paths/v1",
                "source_digest": item.metadata["content_digest"],
            }
            scope = list(item.derived_files)
        return {
            "obligation_ids": [obligation_id],
            "evidence_type": CANONICAL_TYPES[
                item.metadata["artifact_type"]
            ][obligation_id],
            "value": value,
            "affected_scope": scope,
            "command": item.metadata.get("command"),
            "environment": item.metadata.get("environment"),
            "source_tool": item.metadata.get("source_tool"),
            "observed_at": item.metadata["observed_at"],
            "evidence_id": self._evidence_id(
                package_digest, item.artifact_id, obligation_id
            ),
        }

    def register_package(
        self,
        case_id: str,
        *,
        package_digest: str,
        actor: str = "sidecar-bridge",
        role: str = "contributor_agent",
    ) -> BridgeReceipt:
        with self.transaction._lock:
            case = self.service.storage.load_case(case_id)
            package = self.store.get_package_by_digest(package_digest)
            self._validate_package_binding(case, package)
            existing = self.store.read_registration(package_digest)
            if existing is not None:
                if (
                    existing.get("case_id"),
                    existing.get("contribution_fingerprint"),
                    existing.get("policy_fingerprint"),
                ) != (
                    case.id,
                    case.contribution_fingerprint,
                    case.policy_snapshot.policy_fingerprint,
                ):
                    raise VNextError("Registered package binding no longer matches case")
                audit = {
                    "event": "already_registered",
                    "case_id": case.id,
                    "package_digest": package_digest,
                }
                self.store.append_audit_event("bridge_audit", audit)
                return BridgeReceipt(
                    package_digest,
                    case.id,
                    case.contribution_fingerprint,
                    tuple(existing["canonical_evidence_ids"]),
                    tuple(existing["artifact_ids"]),
                    audit,
                    "already_registered",
                )
            self.store.append_audit_event(
                "bridge_audit",
                {
                    "event": "registration_started",
                    "case_id": case.id,
                    "package_digest": package_digest,
                },
            )
            try:
                validated_package = TypedArtifactValidator().validate_package_with_scope(
                    case, package, self.store.read_artifact
                )
                validated = validated_package.artifacts
                entries = [
                    self._entry(item, package_digest, obligation_id)
                    for item in validated
                    for obligation_id in item.obligation_refs
                ]
                staged_case, _ = self.service._prepare_evidence_batch(
                    case, actor=actor, actor_role=role, entries=entries
                )
                self.transaction._fault("conflict_detector_failure")
                detector = TrustedSidecarConflictDetector(
                    self.service, self.store
                )
                derivation = detector.derive(
                    staged_case, package_digest, validated
                )
                if derivation is not None:
                    self.service._record_validated_sidecar_conflict(
                        staged_case, derivation
                    )
                evidence_ids = tuple(entry["evidence_id"] for entry in entries)
                artifact_ids = tuple(item.artifact_id for item in validated)
                receipt_payload = {
                    "bridge_version": "v2",
                    "case_id": case.id,
                    "package_digest": package_digest,
                    "contribution_fingerprint": case.contribution_fingerprint,
                    "policy_fingerprint": case.policy_snapshot.policy_fingerprint,
                    "artifact_ids": list(artifact_ids),
                    "canonical_evidence_ids": list(evidence_ids),
                    "registration_status": "completed",
                    "registered_at": package["created_at"],
                }
                receipt_digest = fingerprint(receipt_payload)
                bridge_audit = {
                    "event": "registration_completed",
                    "case_id": case.id,
                    "package_digest": package_digest,
                    "receipt_digest": receipt_digest,
                }
                conflict_audits = [
                    {
                        "event": "detection_started",
                        "case_id": case.id,
                        "package_digest": package_digest,
                    },
                    {
                        "event": "conflict_detected"
                        if derivation is not None
                        else "no_conflict",
                        "case_id": case.id,
                        "package_digest": package_digest,
                    },
                ]
                registration = {
                    "registration_version": "agm.sidecar_registration/v1",
                    "case_id": case.id,
                    "package_digest": package_digest,
                    "contribution_fingerprint": case.contribution_fingerprint,
                    "policy_fingerprint": case.policy_snapshot.policy_fingerprint,
                    "artifact_ids": list(artifact_ids),
                    "canonical_evidence_ids": list(evidence_ids),
                    "receipt_digest": receipt_digest,
                }
                self.transaction.commit(
                    case_before=case,
                    case_after=staged_case,
                    package_digest=package_digest,
                    receipt_payload=receipt_payload,
                    bridge_audit=bridge_audit,
                    conflict_audits=conflict_audits,
                    registration_payload=registration,
                )
                return BridgeReceipt(
                    package_digest,
                    case.id,
                    case.contribution_fingerprint,
                    evidence_ids,
                    artifact_ids,
                    bridge_audit,
                    "completed",
                )
            except Exception:
                if not self.transaction.last_failure_audited:
                    try:
                        self.store.append_audit_event(
                            "bridge_audit",
                            {
                                "event": "registration_rejected",
                                "case_id": case.id,
                                "package_digest": package_digest,
                            },
                        )
                    except Exception:
                        pass
                raise

    def _validate_package_binding(self, case: Any, package: dict[str, Any]) -> None:
        if package.get("case_id") != case.id:
            raise VNextError("Evidence package case binding does not match")
        if package.get("policy_fingerprint") != case.policy_snapshot.policy_fingerprint:
            raise VNextError("Evidence package policy binding does not match")
        if package.get("contribution_fingerprint") != case.contribution_fingerprint:
            raise VNextError("Evidence package contribution binding does not match")
