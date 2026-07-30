"""Recoverable package-ingestion transaction coordinator."""
from __future__ import annotations

import json
import os
import shutil
import threading
from pathlib import Path
from typing import Any, Callable

from ..models import GovernanceCase, VNextError, canonical_json, fingerprint
from ..storage import atomic_write_text
from .sidecar import SidecarEvidenceStore


class IngestionInterrupted(BaseException):
    """Fault-injection stand-in for abrupt process interruption."""


class PackageIngestionTransaction:
    _lock = threading.RLock()

    def __init__(
        self,
        service: Any,
        store: SidecarEvidenceStore,
        fault_injector: Callable[[str], None] | None = None,
    ):
        self.service = service
        self.store = store
        self.fault_injector = fault_injector
        self.transactions_root = self.store.root / "transactions"
        self.recovery_root = self.store.root / "transaction_recovery"
        self.last_failure_audited = False
        self.recover()

    def _fault(self, point: str) -> None:
        if self.fault_injector is not None:
            self.fault_injector(point)

    def _directory(self, case_id: str, package_digest: str) -> Path:
        transaction_id = fingerprint(
            {"case_id": case_id, "package_digest": package_digest}
        )
        return self.transactions_root / transaction_id

    def recover(self) -> None:
        """Recover every incomplete transaction from durable state."""
        with self._lock:
            if not self.transactions_root.exists():
                return
            for directory in sorted(self.transactions_root.iterdir()):
                manifest_path = directory / "manifest.json"
                if not manifest_path.is_file():
                    shutil.rmtree(directory, ignore_errors=True)
                    continue
                manifest = json.loads(manifest_path.read_text(encoding="utf8"))
                if manifest.get("status") == "complete":
                    shutil.rmtree(directory, ignore_errors=True)
                    continue
                self._validate_manifest(manifest)
                before = GovernanceCase.from_dict(manifest["case_before"])
                current = self.service.storage.load_case(manifest["case_id"])
                current_digest = fingerprint(current.to_dict())
                status = manifest.get("status")
                before_digest = manifest["case_before_digest"]
                after_digest = manifest["case_after_digest"]
                if status == "prepared":
                    if current_digest != before_digest:
                        self._recovery_error(
                            directory, manifest, "Prepared transaction changed canonical case"
                        )
                    self.store.restore_audit_lengths(
                        manifest.get("audit_lengths", {})
                    )
                    self.store.append_audit_event(
                        "bridge_audit",
                        {
                            "event": "registration_failed",
                            "case_id": manifest["case_id"],
                            "package_digest": manifest["package_digest"],
                            "transaction_id": manifest["transaction_id"],
                        },
                    )
                    self._write_recovery_record(
                        manifest,
                        status="recovered",
                        detail="Prepared transaction was discarded before case replacement",
                    )
                    shutil.rmtree(directory, ignore_errors=True)
                    continue
                if status not in {
                    "replacement_intent",
                    "case_replaced",
                    "sidecars_published",
                    "rolling_back",
                }:
                    self._recovery_error(
                        directory, manifest, "Unknown transaction recovery state"
                    )
                if current_digest not in {before_digest, after_digest}:
                    self._recovery_error(
                        directory,
                        manifest,
                        "Canonical case matches neither transaction snapshot",
                    )
                self._rollback(directory, manifest, before, recovered=True)

    def _remove_finalized_sidecar(self, manifest: dict[str, Any]) -> None:
        receipt = self.store.root / "bridge_receipts" / (
            str(manifest.get("receipt_digest", "")) + ".json"
        )
        if receipt.name != ".json":
            receipt.unlink(missing_ok=True)
        package_digest = manifest.get("package_digest")
        if package_digest:
            self.store.registration_path(package_digest).unlink(missing_ok=True)

    def _sync_directory(self, path: Path) -> None:
        if os.name == "nt":
            return
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def _write_manifest(self, directory: Path, manifest: dict[str, Any]) -> None:
        atomic_write_text(
            directory / "manifest.json", canonical_json(manifest) + "\n"
        )
        self._sync_directory(directory)

    def _validate_manifest(self, manifest: dict[str, Any]) -> None:
        before = manifest.get("case_before")
        if not isinstance(before, dict):
            raise VNextError("Transaction recovery snapshot is missing")
        if fingerprint(before) != manifest.get("case_before_digest"):
            raise VNextError("Transaction recovery snapshot digest is invalid")
        if (
            before.get("id") != manifest.get("case_id")
            or before.get("contribution_fingerprint")
            != manifest.get("contribution_fingerprint")
        ):
            raise VNextError("Transaction recovery snapshot binding is invalid")

    def _write_recovery_record(
        self, manifest: dict[str, Any], *, status: str, detail: str
    ) -> None:
        self.recovery_root.mkdir(parents=True, exist_ok=True)
        transaction_id = manifest["transaction_id"]
        atomic_write_text(
            self.recovery_root / f"{transaction_id}.json",
            canonical_json(
                {
                    "transaction_id": transaction_id,
                    "case_id": manifest["case_id"],
                    "package_digest": manifest["package_digest"],
                    "status": status,
                    "detail": detail,
                }
            )
            + "\n",
        )

    def _recovery_error(
        self, directory: Path, manifest: dict[str, Any], detail: str
    ) -> None:
        manifest["status"] = "recovery_error"
        manifest["recovery_error"] = detail
        self._write_manifest(directory, manifest)
        self._write_recovery_record(
            manifest, status="recovery_error", detail=detail
        )
        raise VNextError(detail)

    def _rollback(
        self,
        directory: Path,
        manifest: dict[str, Any],
        case_before: GovernanceCase,
        *,
        recovered: bool,
    ) -> None:
        manifest["status"] = "rolling_back"
        self._write_manifest(directory, manifest)
        current = self.service.storage.load_case(case_before.id)
        if fingerprint(current.to_dict()) != manifest["case_before_digest"]:
            self.service.storage.save_case(case_before)
            self._fault("recovery_after_case_restore")
        self._remove_finalized_sidecar(manifest)
        self.store.restore_audit_lengths(manifest.get("audit_lengths", {}))
        transaction_id = manifest["transaction_id"]
        events = []
        if manifest.get("prepared_persisted"):
            events.append("transaction_prepared")
        if manifest.get("replacement_intent_persisted"):
            events.append("replacement_intent_written")
        events.extend(
            ("registration_failed", "rollback_started", "rollback_completed")
        )
        for event in events:
            self.store.append_audit_event(
                "bridge_audit",
                {
                    "event": event,
                    "case_id": manifest["case_id"],
                    "package_digest": manifest["package_digest"],
                    "transaction_id": transaction_id,
                },
            )
        self.store.append_audit_event(
            "conflict_audit",
            {
                "event": "transaction_rolled_back",
                "case_id": manifest["case_id"],
                "package_digest": manifest["package_digest"],
                "transaction_id": transaction_id,
            },
        )
        self._write_recovery_record(
            manifest,
            status="recovered" if recovered else "rolled_back",
            detail="Canonical case and sidecars restored to pre-registration state",
        )
        self.last_failure_audited = True
        shutil.rmtree(directory, ignore_errors=True)

    def commit(
        self,
        *,
        case_before: GovernanceCase,
        case_after: GovernanceCase,
        package_digest: str,
        receipt_payload: dict[str, Any],
        bridge_audit: dict[str, Any],
        conflict_audits: list[dict[str, Any]],
        registration_payload: dict[str, Any],
    ) -> str:
        """Publish case, receipt, audits and index as one recoverable unit."""
        with self._lock:
            self.last_failure_audited = False
            directory = self._directory(case_before.id, package_digest)
            if directory.exists():
                self.recover()
            directory.mkdir(parents=True, exist_ok=False)
            receipt_digest = fingerprint(receipt_payload)
            transaction_id = directory.name
            case_before_payload = case_before.to_dict()
            case_after_payload = case_after.to_dict()
            manifest = {
                "transaction_version": "agm.package_ingestion_tx/v1",
                "transaction_id": transaction_id,
                "case_id": case_before.id,
                "contribution_fingerprint": case_before.contribution_fingerprint,
                "package_digest": package_digest,
                "receipt_digest": receipt_digest,
                "status": "prepared",
                "audit_lengths": self.store.audit_lengths(),
                "case_before": case_before_payload,
                "case_before_digest": fingerprint(case_before_payload),
                "case_after_digest": fingerprint(case_after_payload),
                "prepared_persisted": False,
                "replacement_intent_persisted": False,
            }
            try:
                self._fault("receipt_stage_failure")
                atomic_write_text(
                    directory / "staged_case.json",
                    canonical_json(case_after_payload) + "\n",
                )
                atomic_write_text(
                    directory / "staged_receipt.json",
                    canonical_json(receipt_payload) + "\n",
                )
                atomic_write_text(
                    directory / "staged_audits.json",
                    canonical_json(
                        {
                            "bridge": bridge_audit,
                            "conflict": conflict_audits,
                        }
                    )
                    + "\n",
                )
                self._write_manifest(directory, manifest)
                manifest["prepared_persisted"] = True
                self._write_manifest(directory, manifest)
                self.store.append_audit_event(
                    "bridge_audit",
                    {
                        "event": "transaction_prepared",
                        "case_id": case_before.id,
                        "package_digest": package_digest,
                        "transaction_id": transaction_id,
                    },
                )
                self._fault("process_interrupted_after_staging")
                self._fault("commit_marker_failure")
                atomic_write_text(directory / "commit.marker", "commit\n")
                manifest["status"] = "replacement_intent"
                manifest["replacement_intent_persisted"] = True
                self._write_manifest(directory, manifest)
                self.store.append_audit_event(
                    "bridge_audit",
                    {
                        "event": "replacement_intent_written",
                        "case_id": case_before.id,
                        "package_digest": package_digest,
                        "transaction_id": transaction_id,
                    },
                )
                self._fault("process_interrupted_after_replacement_intent")
                self._fault("canonical_case_save_failure")
                self.service.storage.save_case(case_after)
                self._fault("durable_case_write_then_failure")
                self._fault("process_interrupted_after_case_write")
                manifest["status"] = "case_replaced"
                self._write_manifest(directory, manifest)
                self._fault("process_interrupted_after_case_replace")
                _, finalized_digest = self.store.finalize_bridge_receipt(
                    receipt_payload
                )
                if finalized_digest != receipt_digest:
                    raise VNextError("Staged receipt digest changed during commit")
                self._fault("receipt_finalization_failure")
                self._fault("process_interrupted_after_receipt_publication")
                self.store.append_audit_event("bridge_audit", bridge_audit)
                self._fault("audit_append_failure")
                for event in conflict_audits:
                    self.store.append_audit_event("conflict_audit", event)
                self.store.finalize_registration(registration_payload)
                manifest["status"] = "sidecars_published"
                self._write_manifest(directory, manifest)
                manifest["status"] = "complete"
                self._write_manifest(directory, manifest)
                shutil.rmtree(directory)
                return receipt_digest
            except Exception:
                self._rollback(
                    directory, manifest, case_before, recovered=False
                )
                raise
