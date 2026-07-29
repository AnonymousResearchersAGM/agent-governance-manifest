from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "tests")]

from agm.vnext.models import VNextError  # noqa: E402
from agm.vnext.pr_diagnostic import SidecarEvidenceBridge, SidecarEvidenceStore  # noqa: E402
from agm.vnext.pr_diagnostic.artifact_schemas import compare_scopes  # noqa: E402
from agm.vnext.pr_diagnostic.conflicts import TrustedSidecarConflictDetector  # noqa: E402
from agm.vnext.pr_diagnostic.transaction import IngestionInterrupted  # noqa: E402
from agm.vnext.service import GovernanceService  # noqa: E402
from generate_reviewer_guidance_demos import FIXED_TIME, make_project  # noqa: E402
from test_vnext_pr_diagnostic_semantic_hardening import (  # noqa: E402
    _agent,
    _artifact,
    _changed,
    _declaration,
    _package,
    _summary,
)


def _multi_case(tmp_path: Path):
    root = make_project(tmp_path, "scope-recovery")
    service = GovernanceService(root)
    case, _ = service.open_case(
        ["README.md", "demo_app/auth.py"],
        requested_mode="declared_agent_mediated",
        actor="contributor",
        actor_role="contributor",
        case_id="scope-recovery",
        base_commit="d" * 40,
        autonomy_profile="supervised_agent",
        timestamp=FIXED_TIME,
    )
    assert case is not None
    return root, service, case


def _audit_events(store: SidecarEvidenceStore, name: str) -> list[str]:
    path = store.root / f"{name}.jsonl"
    if not path.exists():
        return []
    return [
        json.loads(line)["event"]
        for line in path.read_text(encoding="utf8").splitlines()
    ]


@pytest.mark.parametrize(
    ("declared", "canonical", "relation"),
    [
        (("README.md",), ("README.md",), "exact_match"),
        (("README.md",), ("README.md", "demo_app/auth.py"), "declared_subset"),
        (("README.md", "demo_app/auth.py"), ("README.md",), "declared_superset"),
        (("README.md",), ("demo_app/auth.py",), "disjoint"),
        (
            ("README.md", "demo_app/tasks.py"),
            ("README.md", "demo_app/auth.py"),
            "overlap_but_inconsistent",
        ),
    ],
)
def test_scope_comparison_relations(declared, canonical, relation):
    assert compare_scopes(declared, canonical) == relation


def test_summary_scope_disjoint_from_contribution_is_rejected_atomically(tmp_path):
    root, service, case = _multi_case(tmp_path)
    case.changed_files = ["demo_app/auth.py"]
    service.storage.save_case(case)
    summary = _summary(case)
    value = json.loads(summary["content"])
    value["affected_components"] = ["README.md"]
    summary["content"] = json.dumps(value, sort_keys=True)
    summary["affected_scope"] = ["README.md"]
    diff = _artifact(
        case,
        "unified_diff",
        [],
        content=(
            "diff --git a/demo_app/auth.py b/demo_app/auth.py\n"
            "--- a/demo_app/auth.py\n+++ b/demo_app/auth.py\n"
            "@@ -1 +1 @@\n-old\n+new\n"
        ),
    )
    package = _package(root, case, [diff, summary, _changed(case)])

    with pytest.raises(VNextError, match="Change summary affected files"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )

    store = SidecarEvidenceStore(root)
    loaded = service.storage.load_case(case.id)
    assert not loaded.evidence
    assert loaded.obligation("O-SUMMARY").status == "unsatisfied"
    assert store.read_registration(package.package_digest) is None
    assert not list((store.root / "bridge_receipts").glob("*.json"))
    assert "registration_completed" not in _audit_events(store, "bridge_audit")


def test_summary_changed_files_and_metadata_must_exactly_match(tmp_path):
    root, service, case = _multi_case(tmp_path)
    summary = _summary(case)
    summary["affected_scope"] = ["README.md"]
    package = _package(root, case, [summary, _changed(case)])
    with pytest.raises(VNextError, match="metadata scope"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )


def test_activity_typed_scope_must_match_metadata_scope(tmp_path):
    root, service, case = _multi_case(tmp_path)
    activity = _agent(case, activity_scope=["README.md"])
    activity["affected_scope"] = ["demo_app/auth.py"]
    package = _package(root, case, [_summary(case), _changed(case), activity])
    with pytest.raises(VNextError, match="typed scope"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )
    assert not service.storage.load_case(case.id).evidence


def test_declaration_typed_scope_must_match_metadata_scope(tmp_path):
    root, service, case = _multi_case(tmp_path)
    declaration = _declaration(case, declaration_scope=["README.md"])
    declaration["affected_scope"] = ["demo_app/auth.py"]
    package = _package(
        root, case, [_summary(case), _changed(case), declaration]
    )
    with pytest.raises(VNextError, match="typed scope"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )


def test_partial_declaration_does_not_imply_full_contribution_coverage(tmp_path):
    root, service, case = _multi_case(tmp_path)
    declaration = _declaration(case, declaration_scope=["README.md"])
    declaration["affected_scope"] = ["README.md"]
    package = _package(
        root, case, [_summary(case), _changed(case), declaration]
    )
    SidecarEvidenceBridge(service).register_package(
        case.id, package_digest=package.package_digest
    )
    loaded = service.storage.load_case(case.id)
    assert loaded.obligation("O-AGENT-SCOPE").status == "unsatisfied"
    record = next(
        item for item in loaded.evidence if item.evidence_type == "agent_action_scope"
    )
    assert record.value["coverage_relation"] == "declared_subset"


def test_full_declaration_is_valid_contribution_wide_coverage(tmp_path):
    root, service, case = _multi_case(tmp_path)
    package = _package(
        root, case, [_summary(case), _changed(case), _declaration(case)]
    )
    SidecarEvidenceBridge(service).register_package(
        case.id, package_digest=package.package_digest
    )
    assert (
        service.storage.load_case(case.id).obligation("O-AGENT-SCOPE").status
        == "satisfied"
    )


def test_partial_activity_does_not_satisfy_but_union_coverage_does(tmp_path):
    root, service, case = _multi_case(tmp_path)
    first = _agent(case, activity_scope=["README.md"])
    first["affected_scope"] = ["README.md"]
    first_package = _package(
        root, case, [_summary(case), _changed(case), first]
    )
    SidecarEvidenceBridge(service).register_package(
        case.id, package_digest=first_package.package_digest
    )
    loaded = service.storage.load_case(case.id)
    assert loaded.obligation("O-AGENT-SCOPE").status == "unsatisfied"
    record = next(
        item for item in loaded.evidence if item.evidence_type == "agent_action_scope"
    )
    assert record.value["validated_typed_scope"] == ["README.md"]
    assert record.value["canonical_contribution_scope"] == [
        "README.md",
        "demo_app/auth.py",
    ]
    assert record.value["coverage_relation"] == "declared_subset"
    view = service.pr_diagnosis(case.id)
    assert view.agent_involvement["state"] == "coverage_incomplete"
    assert "只覆盖部分修改" in view.agent_involvement["message"]
    assert "demo_app/auth.py" in view.agent_involvement["message"]

    second = _agent(case, activity_scope=["demo_app/auth.py"])
    second["affected_scope"] = ["demo_app/auth.py"]
    second_package = _package(root, case, [second])
    SidecarEvidenceBridge(service).register_package(
        case.id, package_digest=second_package.package_digest
    )
    assert (
        service.storage.load_case(case.id).obligation("O-AGENT-SCOPE").status
        == "satisfied"
    )


def test_disjoint_scoped_sources_do_not_create_trusted_conflict(tmp_path):
    root, service, case = _multi_case(tmp_path)
    declaration = _declaration(case, declaration_scope=["README.md"])
    declaration["affected_scope"] = ["README.md"]
    activity = _agent(
        case, used=True, activity_scope=["demo_app/auth.py"]
    )
    activity["affected_scope"] = ["demo_app/auth.py"]
    package = _package(
        root,
        case,
        [_summary(case), _changed(case), declaration, activity],
    )
    SidecarEvidenceBridge(service).register_package(
        case.id, package_digest=package.package_digest
    )
    loaded = service.storage.load_case(case.id)
    assert not [
        item for item in loaded.findings if item.code == "trusted_sidecar_conflict"
    ]
    assert (
        TrustedSidecarConflictDetector(service).detect(
            case.id, package.package_digest
        )
        is None
    )


def test_overlapping_scoped_sources_create_one_idempotent_conflict(tmp_path):
    root, service, case = _multi_case(tmp_path)
    declaration = _declaration(case, declaration_scope=["README.md"])
    declaration["affected_scope"] = ["README.md"]
    activity = _agent(case, used=True, activity_scope=["README.md"])
    activity["affected_scope"] = ["README.md"]
    package = _package(
        root,
        case,
        [_summary(case), _changed(case), declaration, activity],
    )
    SidecarEvidenceBridge(service).register_package(
        case.id, package_digest=package.package_digest
    )
    TrustedSidecarConflictDetector(service).detect(
        case.id, package.package_digest
    )
    assert len(
        [
            item
            for item in service.storage.load_case(case.id).findings
            if item.code == "trusted_sidecar_conflict"
        ]
    ) == 1


def test_replacement_intent_is_durable_before_case_save(tmp_path):
    root, service, case = _multi_case(tmp_path)
    package = _package(root, case, [_summary(case), _changed(case)])

    def inject(point):
        if point == "canonical_case_save_failure":
            manifests = list(
                (SidecarEvidenceStore(root).root / "transactions").glob(
                    "*/manifest.json"
                )
            )
            assert len(manifests) == 1
            assert json.loads(manifests[0].read_text(encoding="utf8"))[
                "status"
            ] == "replacement_intent"
            raise VNextError("inspected replacement intent")

    with pytest.raises(VNextError, match="inspected replacement intent"):
        SidecarEvidenceBridge(service, fault_injector=inject).register_package(
            case.id, package_digest=package.package_digest
        )


def test_durable_case_write_then_exception_rolls_back_and_retry_succeeds(
    tmp_path, monkeypatch
):
    root, service, case = _multi_case(tmp_path)
    package = _package(root, case, [_summary(case), _changed(case)])
    real_save = service.storage.save_case
    calls = 0

    def durable_then_fail(value):
        nonlocal calls
        calls += 1
        result = real_save(value)
        if calls == 1:
            raise VNextError("durable write completed before failure")
        return result

    monkeypatch.setattr(service.storage, "save_case", durable_then_fail)
    with pytest.raises(VNextError, match="durable write completed"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )
    store = SidecarEvidenceStore(root)
    restored = GovernanceService(root).storage.load_case(case.id)
    assert restored.to_dict() == case.to_dict()
    assert store.read_registration(package.package_digest) is None
    assert not list((store.root / "bridge_receipts").glob("*.json"))
    assert "registration_completed" not in _audit_events(store, "bridge_audit")
    assert _audit_events(store, "bridge_audit")[-5:] == [
        "transaction_prepared",
        "replacement_intent_written",
        "registration_failed",
        "rollback_started",
        "rollback_completed",
    ]
    fresh = GovernanceService(root)
    receipt = SidecarEvidenceBridge(fresh).register_package(
        case.id, package_digest=package.package_digest
    )
    assert receipt.registration_status == "completed"


def test_restart_recovers_durable_case_with_intent_manifest_idempotently(tmp_path):
    root, service, case = _multi_case(tmp_path)
    package = _package(root, case, [_summary(case), _changed(case)])

    def inject(point):
        if point == "process_interrupted_after_case_write":
            raise IngestionInterrupted(point)

    with pytest.raises(IngestionInterrupted):
        SidecarEvidenceBridge(service, fault_injector=inject).register_package(
            case.id, package_digest=package.package_digest
        )
    assert GovernanceService(root).storage.load_case(case.id).evidence

    restarted = GovernanceService(root)
    SidecarEvidenceBridge(restarted)
    assert restarted.storage.load_case(case.id).to_dict() == case.to_dict()
    SidecarEvidenceBridge(GovernanceService(root))
    assert GovernanceService(root).storage.load_case(case.id).to_dict() == case.to_dict()
    store = SidecarEvidenceStore(root)
    assert store.read_registration(package.package_digest) is None
    assert not list((store.root / "bridge_receipts").glob("*.json"))
    records = list((store.root / "transaction_recovery").glob("*.json"))
    assert len(records) == 1
    assert json.loads(records[0].read_text(encoding="utf8"))["status"] == "recovered"


def test_restart_after_receipt_publication_rolls_back_all_sidecars(tmp_path):
    root, service, case = _multi_case(tmp_path)
    package = _package(root, case, [_summary(case), _changed(case)])

    def inject(point):
        if point == "process_interrupted_after_receipt_publication":
            raise IngestionInterrupted(point)

    with pytest.raises(IngestionInterrupted):
        SidecarEvidenceBridge(service, fault_injector=inject).register_package(
            case.id, package_digest=package.package_digest
        )
    store = SidecarEvidenceStore(root)
    assert list((store.root / "bridge_receipts").glob("*.json"))
    restarted = GovernanceService(root)
    SidecarEvidenceBridge(restarted)
    assert restarted.storage.load_case(case.id).to_dict() == case.to_dict()
    assert not list((store.root / "bridge_receipts").glob("*.json"))
    assert store.read_registration(package.package_digest) is None
    assert "registration_completed" not in _audit_events(store, "bridge_audit")


def test_snapshot_digest_mismatch_blocks_recovery(tmp_path):
    root, service, case = _multi_case(tmp_path)
    package = _package(root, case, [_summary(case), _changed(case)])

    def inject(point):
        if point == "process_interrupted_after_replacement_intent":
            raise IngestionInterrupted(point)

    with pytest.raises(IngestionInterrupted):
        SidecarEvidenceBridge(service, fault_injector=inject).register_package(
            case.id, package_digest=package.package_digest
        )
    manifest_path = next(
        (SidecarEvidenceStore(root).root / "transactions").glob("*/manifest.json")
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf8"))
    manifest["case_before"]["state"] = "tampered"
    manifest_path.write_text(json.dumps(manifest), encoding="utf8")
    with pytest.raises(VNextError, match="snapshot digest"):
        SidecarEvidenceBridge(GovernanceService(root))
