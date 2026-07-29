"""Recoverable package-ingestion transaction coordinator."""
from __future__ import annotations

import json
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
        """Rollback every transaction that lacks a completed manifest."""
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
                if manifest.get("status") in {"case_replaced", "sidecar_finalized"}:
                    original = GovernanceCase.from_dict(manifest["case_before"])
                    self.service.storage.save_case(original)
                self._remove_finalized_sidecar(manifest)
                self.store.restore_audit_lengths(manifest.get("audit_lengths", {}))
                shutil.rmtree(directory, ignore_errors=True)

    def _remove_finalized_sidecar(self, manifest: dict[str, Any]) -> None:
        receipt = self.store.root / "bridge_receipts" / (
            str(manifest.get("receipt_digest", "")) + ".json"
        )
        if receipt.name != ".json":
            receipt.unlink(missing_ok=True)
        package_digest = manifest.get("package_digest")
        if package_digest:
            self.store.registration_path(package_digest).unlink(missing_ok=True)

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
            directory = self._directory(case_before.id, package_digest)
            if directory.exists():
                self.recover()
            directory.mkdir(parents=True, exist_ok=False)
            receipt_digest = fingerprint(receipt_payload)
            manifest = {
                "transaction_version": "agm.package_ingestion_tx/v1",
                "case_id": case_before.id,
                "package_digest": package_digest,
                "receipt_digest": receipt_digest,
                "status": "staged",
                "audit_lengths": self.store.audit_lengths(),
                "case_before": case_before.to_dict(),
            }
            try:
                self._fault("receipt_stage_failure")
                atomic_write_text(
                    directory / "staged_case.json",
                    canonical_json(case_after.to_dict()) + "\n",
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
                atomic_write_text(
                    directory / "manifest.json",
                    canonical_json(manifest) + "\n",
                )
                self._fault("process_interrupted_after_staging")
                self._fault("commit_marker_failure")
                atomic_write_text(directory / "commit.marker", "commit\n")
                self._fault("canonical_case_save_failure")
                self.service.storage.save_case(case_after)
                manifest["status"] = "case_replaced"
                atomic_write_text(
                    directory / "manifest.json",
                    canonical_json(manifest) + "\n",
                )
                self._fault("process_interrupted_after_case_replace")
                _, finalized_digest = self.store.finalize_bridge_receipt(
                    receipt_payload
                )
                if finalized_digest != receipt_digest:
                    raise VNextError("Staged receipt digest changed during commit")
                self._fault("receipt_finalization_failure")
                self.store.append_audit_event("bridge_audit", bridge_audit)
                self._fault("audit_append_failure")
                for event in conflict_audits:
                    self.store.append_audit_event("conflict_audit", event)
                self.store.finalize_registration(registration_payload)
                manifest["status"] = "sidecar_finalized"
                atomic_write_text(
                    directory / "manifest.json",
                    canonical_json(manifest) + "\n",
                )
                manifest["status"] = "complete"
                atomic_write_text(
                    directory / "manifest.json",
                    canonical_json(manifest) + "\n",
                )
                shutil.rmtree(directory)
                return receipt_digest
            except Exception:
                if manifest.get("status") in {"case_replaced", "sidecar_finalized"}:
                    self.service.storage.save_case(case_before)
                self._remove_finalized_sidecar(manifest)
                self.store.restore_audit_lengths(manifest["audit_lengths"])
                shutil.rmtree(directory, ignore_errors=True)
                raise
