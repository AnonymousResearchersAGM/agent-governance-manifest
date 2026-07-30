"""Trusted conflicts derived only from fully validated typed artifacts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..models import GovernanceCase, VNextError, fingerprint
from ..service import GovernanceService
from .artifact_schemas import TypedArtifactValidator, ValidatedArtifact
from .sidecar import SidecarEvidenceStore


@dataclass(frozen=True)
class ValidatedConflictDerivation:
    case_id: str
    policy_fingerprint: str
    contribution_fingerprint: str
    package_digest: str
    declaration_artifact_id: str
    declaration_artifact_digest: str
    agent_activity_artifact_id: str
    agent_activity_artifact_digest: str
    canonical_evidence_ids: tuple[str, ...]
    typed_relation: tuple[tuple[str, bool], ...]
    overlap_scope: tuple[str, ...]
    validation_result: str = "validated"


def _evidence_id(package: str, artifact: str, obligation: str) -> str:
    return "sidecar-" + fingerprint(
        {"package": package, "artifact": artifact, "obligation": obligation}
    )[:24]


def validate_conflict_derivation(
    case: GovernanceCase,
    store: SidecarEvidenceStore,
    derivation: ValidatedConflictDerivation,
) -> None:
    """Revalidate every source and the typed relation at the canonical boundary."""
    if not isinstance(derivation, ValidatedConflictDerivation):
        raise VNextError("Trusted conflict requires a validated derivation object")
    if (
        derivation.case_id,
        derivation.policy_fingerprint,
        derivation.contribution_fingerprint,
    ) != (
        case.id,
        case.policy_snapshot.policy_fingerprint,
        case.contribution_fingerprint,
    ):
        raise VNextError("Conflict derivation does not bind to the current case")
    package = store.get_package_by_digest(derivation.package_digest)
    validated = TypedArtifactValidator().validate_package(
        case, package, store.read_artifact
    )
    by_id = {item.artifact_id: item for item in validated}
    declaration = by_id.get(derivation.declaration_artifact_id)
    activity = by_id.get(derivation.agent_activity_artifact_id)
    if (
        declaration is None
        or declaration.artifact_type != "contribution_declaration"
        or activity is None
        or activity.artifact_type != "agent_activity"
    ):
        raise VNextError("Conflict derivation source artifacts are unavailable")
    if (
        declaration.metadata["content_digest"]
        != derivation.declaration_artifact_digest
        or activity.metadata["content_digest"]
        != derivation.agent_activity_artifact_digest
    ):
        raise VNextError("Conflict derivation source digest does not match")
    expected_relation = (
        ("declared_other_agents_or_tools_used", False),
        ("observed_other_agents_or_tools_used", True),
    )
    if (
        declaration.typed_value is None
        or activity.typed_value is None
        or declaration.typed_value["other_agents_or_tools_used"] is not False
        or activity.typed_value["other_agents_or_tools_used"] is not True
        or derivation.typed_relation != expected_relation
    ):
        raise VNextError("Typed artifacts do not form a trusted conflict")
    overlap = tuple(
        sorted(set(declaration.validated_scope) & set(activity.validated_scope))
    )
    if not overlap or derivation.overlap_scope != overlap:
        raise VNextError("Trusted conflict sources do not share a validated scope")
    expected_ids = (
        _evidence_id(
            package["package_digest"], declaration.artifact_id, "O-AGENT-SCOPE"
        ),
        _evidence_id(
            package["package_digest"], activity.artifact_id, "O-AGENT-SCOPE"
        ),
    )
    if derivation.canonical_evidence_ids != expected_ids:
        raise VNextError("Conflict derivation canonical evidence mapping is invalid")
    evidence = {item.id: item for item in case.evidence}
    if not set(expected_ids) <= set(evidence):
        raise VNextError("Conflict canonical evidence mapping is unavailable")
    for evidence_id, artifact in zip(expected_ids, (declaration, activity)):
        item = evidence[evidence_id]
        if (
            item.contribution_fingerprint != case.contribution_fingerprint
            or item.policy_fingerprint != case.policy_snapshot.policy_fingerprint
            or item.value != {
                "artifact_type": artifact.artifact_type,
                "validated_typed_scope": sorted(artifact.validated_scope),
                "canonical_contribution_scope": list(artifact.canonical_scope),
                "coverage_relation": artifact.coverage_relation,
                "scope_source": artifact.scope_source,
                "typed_source_validated": True,
            }
        ):
            raise VNextError("Conflict canonical evidence source mapping is invalid")


class TrustedSidecarConflictDetector:
    def __init__(
        self,
        service: GovernanceService,
        store: SidecarEvidenceStore | None = None,
    ):
        self.service = service
        self.store = store or SidecarEvidenceStore(service.root)

    def derive(
        self,
        case: GovernanceCase,
        package_digest: str,
        artifacts: tuple[ValidatedArtifact, ...],
    ) -> ValidatedConflictDerivation | None:
        package = self.store.get_package_by_digest(package_digest)
        if (
            package.get("case_id"),
            package.get("contribution_fingerprint"),
            package.get("policy_fingerprint"),
        ) != (
            case.id,
            case.contribution_fingerprint,
            case.policy_snapshot.policy_fingerprint,
        ):
            raise VNextError("Conflict package binding does not match current case")
        declarations = [
            item
            for item in artifacts
            if item.artifact_type == "contribution_declaration"
        ]
        activities = [
            item for item in artifacts if item.artifact_type == "agent_activity"
        ]
        pair = next(
            (
                (declaration, activity)
                for declaration in declarations
                for activity in activities
                if declaration.typed_value is not None
                and activity.typed_value is not None
                and declaration.typed_value["other_agents_or_tools_used"] is False
                and activity.typed_value["other_agents_or_tools_used"] is True
                and set(declaration.validated_scope)
                & set(activity.validated_scope)
            ),
            None,
        )
        if pair is None:
            return None
        declaration, activity = pair
        overlap = tuple(
            sorted(set(declaration.validated_scope) & set(activity.validated_scope))
        )
        return ValidatedConflictDerivation(
            case_id=case.id,
            policy_fingerprint=case.policy_snapshot.policy_fingerprint,
            contribution_fingerprint=case.contribution_fingerprint,
            package_digest=package_digest,
            declaration_artifact_id=declaration.artifact_id,
            declaration_artifact_digest=declaration.metadata["content_digest"],
            agent_activity_artifact_id=activity.artifact_id,
            agent_activity_artifact_digest=activity.metadata["content_digest"],
            canonical_evidence_ids=(
                _evidence_id(
                    package_digest,
                    declaration.artifact_id,
                    "O-AGENT-SCOPE",
                ),
                _evidence_id(
                    package_digest, activity.artifact_id, "O-AGENT-SCOPE"
                ),
            ),
            typed_relation=(
                ("declared_other_agents_or_tools_used", False),
                ("observed_other_agents_or_tools_used", True),
            ),
            overlap_scope=overlap,
        )

    def detect(self, case_id: str, package_digest: str) -> Any:
        """Idempotently re-run detection for an already registered package."""
        self.store.append_conflict_audit(
            "detection_started", case_id=case_id, package_digest=package_digest
        )
        try:
            case = self.service.storage.load_case(case_id)
            package = self.store.get_package_by_digest(package_digest)
            artifacts = TypedArtifactValidator().validate_package(
                case, package, self.store.read_artifact
            )
            derivation = self.derive(case, package_digest, artifacts)
            if derivation is None:
                self.store.append_conflict_audit(
                    "no_conflict", case_id=case_id, package_digest=package_digest
                )
                return None
            before = len(case.findings)
            result = self.service._record_validated_sidecar_conflict(
                case, derivation
            )
            self.service.storage.save_case(case)
            self.store.append_conflict_audit(
                "conflict_already_recorded"
                if len(case.findings) == before
                else "conflict_detected",
                case_id=case_id,
                package_digest=package_digest,
            )
            return result
        except VNextError:
            self.store.append_conflict_audit(
                "source_validation_rejected",
                case_id=case_id,
                package_digest=package_digest,
            )
            raise
