from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

from agm.vnext.models import VNextError  # noqa: E402
from agm.vnext.pr_diagnostic import SidecarEvidenceBridge, SidecarEvidenceStore  # noqa: E402
from agm.vnext.pr_diagnostic.artifact_schemas import (  # noqa: E402
    TypedArtifactValidator,
)
from agm.vnext.pr_diagnostic.conflicts import (  # noqa: E402
    TrustedSidecarConflictDetector,
)
from agm.vnext.pr_diagnostic.transaction import IngestionInterrupted  # noqa: E402
from agm.vnext.runtime import DemoExecutionContext, use_execution_context  # noqa: E402
from agm.vnext.service import GovernanceService  # noqa: E402
from generate_pr_diagnostic_demos import (  # noqa: E402
    SCENARIOS,
    _artifacts,
    build_scenario,
)
from generate_reviewer_guidance_demos import FIXED_TIME, make_project  # noqa: E402
from run_pr_diagnostic_browser_review import (  # noqa: E402
    INLINE_ASSERTION_DETAILS,
    _empty_report,
)

HEAD = "c" * 40


def _case(tmp_path: Path, path: str = "README.md"):
    root = make_project(tmp_path, "hardening")
    service = GovernanceService(root)
    case, _ = service.open_case(
        [path],
        requested_mode="declared_agent_mediated",
        actor="contributor",
        actor_role="contributor",
        case_id="hardening",
        base_commit="d" * 40,
        autonomy_profile="supervised_agent",
        timestamp=FIXED_TIME,
    )
    assert case is not None
    return root, service, case


def _content(case, artifact_type: str, refs: list[str], **fields):
    return json.dumps(
        {
            "schema_version": "agm.evidence_artifact/v1",
            "artifact_type": artifact_type,
            "observed_at": FIXED_TIME,
            "head_commit_sha": HEAD,
            "contribution_fingerprint": case.contribution_fingerprint,
            "obligation_refs": refs,
            "source_tool": "fixture",
            **fields,
        },
        sort_keys=True,
    )


def _artifact(case, artifact_type: str, refs: list[str], **fields):
    content = fields.pop("content", None) or _content(
        case, artifact_type, refs, **fields.pop("content_fields", {})
    )
    return {
        "type": artifact_type,
        "content": content,
        "source_tool": fields.pop("source_tool", "fixture"),
        "observed_at": fields.pop("observed_at", FIXED_TIME),
        "affected_scope": fields.pop("affected_scope", list(case.changed_files)),
        "obligation_refs": refs,
        **fields,
    }


def _summary(case, summary: str = "更新 README 安装命令并保留链接说明。"):
    return _artifact(
        case,
        "change_summary",
        ["O-SUMMARY"],
        content_fields={
            "summary": summary,
            "affected_components": list(case.changed_files),
            "behavioral_change": "安装命令示例更明确。",
        },
    )


def _changed(case, files=None):
    return _artifact(
        case,
        "changed_files",
        ["O-CHANGED-FILES"],
        content_fields={"files": files or list(case.changed_files)},
    )


def _agent(case, *, used=False, tools=None, content=None, **overrides):
    fields = {
        "other_agents_or_tools_used": used,
        "tools_used": tools if tools is not None else ([] if not used else ["tool"]),
        "activity_scope": list(case.changed_files),
    }
    fields.update(overrides)
    if content is not None:
        return _artifact(
            case, "agent_activity", ["O-AGENT-SCOPE"], content=content
        )
    return _artifact(
        case, "agent_activity", ["O-AGENT-SCOPE"], content_fields=fields
    )


def _declaration(case, *, used=False, tools=None, content=None, **overrides):
    fields = {
        "other_agents_or_tools_used": used,
        "declared_tools": tools if tools is not None else ([] if not used else ["tool"]),
        "declaration_scope": list(case.changed_files),
        "declared_by": "contributor",
    }
    fields.update(overrides)
    if content is not None:
        return _artifact(
            case,
            "contribution_declaration",
            ["O-AGENT-SCOPE"],
            content=content,
        )
    return _artifact(
        case,
        "contribution_declaration",
        ["O-AGENT-SCOPE"],
        content_fields=fields,
    )


def _package(root, case, artifacts):
    return SidecarEvidenceStore(root).write_package(
        case_id=case.id,
        contribution_fingerprint=case.contribution_fingerprint,
        policy_fingerprint=case.policy_snapshot.policy_fingerprint,
        producer="fixture",
        created_at=FIXED_TIME,
        base_commit_sha=case.base_commit,
        head_commit_sha=HEAD,
        artifacts=artifacts,
    )


@pytest.mark.parametrize("missing_tools", [False, True])
def test_malformed_or_missing_agent_activity_is_rejected(tmp_path, missing_tools):
    root, service, case = _case(tmp_path)
    if missing_tools:
        value = json.loads(_agent(case)["content"])
        value.pop("tools_used")
        artifact = _agent(case, content=json.dumps(value))
        match = "tools_used"
    else:
        artifact = _agent(case, content="not json")
        match = "valid JSON"
    package = _package(root, case, [_summary(case), _changed(case), artifact])
    with pytest.raises(VNextError, match=match):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )
    assert not service.storage.load_case(case.id).evidence
    assert SidecarEvidenceStore(root).read_registration(package.package_digest) is None


@pytest.mark.parametrize(
    "artifact,match",
    [
        (lambda case: _agent(case, other_agents_or_tools_used="true"), "boolean"),
        (lambda case: _agent(case, used=True, tools=[]), "must name"),
        (lambda case: _agent(case, used=False, tools=["tool"]), "non-empty"),
        (
            lambda case: _agent(
                case, contribution_fingerprint="0" * 64
            ),
            "contribution binding",
        ),
        (lambda case: _agent(case, head_commit_sha="a" * 40), "head commit"),
        (lambda case: _declaration(case, content="not json"), "valid JSON"),
        (
            lambda case: _artifact(
                case, "unknown_type", ["O-SUMMARY"], content="{}"
            ),
            "not supported",
        ),
    ],
)
def test_typed_schema_rejects_invalid_artifacts(tmp_path, artifact, match):
    root, service, case = _case(tmp_path)
    package = _package(root, case, [artifact(case)])
    with pytest.raises(VNextError, match=match):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )
    assert not service.storage.load_case(case.id).evidence


@pytest.mark.parametrize(
    "obligation",
    ["O-SUMMARY", "O-CHANGED-FILES", "O-RATIONALE", "O-LIMITATIONS", "O-AUTH-IMPACT"],
)
def test_generic_statement_cannot_satisfy_specific_obligation(
    tmp_path, obligation
):
    root, service, case = _case(tmp_path, "demo_app/auth.py")
    package = _package(
        root,
        case,
        [
            _artifact(
                case,
                "supporting_statement",
                [obligation],
                content="generic material",
            )
        ],
    )
    with pytest.raises(VNextError, match="incompatible"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )


def test_one_artifact_cannot_satisfy_incompatible_obligations(tmp_path):
    root, service, case = _case(tmp_path, "demo_app/auth.py")
    artifact = _summary(case)
    value = json.loads(artifact["content"])
    value["obligation_refs"].append("O-RATIONALE")
    artifact["content"] = json.dumps(value)
    artifact["obligation_refs"] = ["O-SUMMARY", "O-RATIONALE"]
    package = _package(root, case, [artifact])
    with pytest.raises(VNextError, match="incompatible"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )


def test_changed_files_must_match_verified_diff(tmp_path):
    root, service, case = _case(tmp_path, "demo_app/auth.py")
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
    package = _package(root, case, [diff, _changed(case, ["demo_app/tasks.py"])])
    with pytest.raises(VNextError, match="does not match|exceeds"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )


def test_scenario_slug_cannot_satisfy_summary(tmp_path):
    root, service, case = _case(tmp_path)
    package = _package(root, case, [_summary(case, "D3_high_risk_ready")])
    with pytest.raises(VNextError, match="identifier or placeholder"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )


def test_empty_limitations_require_explicit_none(tmp_path):
    root, service, case = _case(tmp_path, "demo_app/auth.py")
    artifact = _artifact(
        case,
        "known_limitations",
        ["O-LIMITATIONS"],
        content_fields={"limitations": [], "declared_by": "contributor"},
    )
    package = _package(root, case, [artifact])
    with pytest.raises(VNextError, match="no_known_limitations"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )


def test_test_result_requires_typed_command_environment_and_scope(tmp_path):
    root, service, case = _case(tmp_path, "demo_app/auth.py")
    artifact = _artifact(
        case,
        "test_result",
        ["O-TEST-COMMAND"],
        command="pytest",
        environment="fixture",
        result_summary="1 passed",
        exit_code=0,
        tests_passed=1,
        tests_failed=0,
        source_tool="pytest",
        content_fields={
            "command": "pytest",
            "result_summary": "1 passed",
            "exit_code": 0,
            "tests_passed": 1,
            "tests_failed": 0,
            "affected_scope": ["demo_app/auth.py"],
            "source_tool": "pytest",
        },
    )
    package = _package(root, case, [artifact])
    with pytest.raises(VNextError, match="environment"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )


def test_human_confirmation_cannot_be_plain_evidence(tmp_path):
    root, service, case = _case(tmp_path, "demo_app/auth.py")
    artifact = _artifact(
        case,
        "human_confirmation",
        ["O-HUMAN-ATTEST"],
        content_fields={
            "confirmed_by": "human",
            "confirmed_at": FIXED_TIME,
            "confirmation_scope": ["demo_app/auth.py"],
            "statement": "reviewed",
        },
    )
    package = _package(root, case, [artifact])
    with pytest.raises(VNextError, match="incompatible"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )


def _valid_readme_package(root, case):
    return _package(root, case, [_summary(case), _changed(case), _agent(case)])


@pytest.mark.parametrize(
    "point",
    [
        "conflict_detector_failure",
        "canonical_case_save_failure",
        "receipt_stage_failure",
        "receipt_finalization_failure",
        "audit_append_failure",
        "commit_marker_failure",
    ],
)
def test_transaction_failures_leave_no_partial_registration(tmp_path, point):
    root, service, case = _case(tmp_path)
    package = _valid_readme_package(root, case)

    def inject(current):
        if current == point:
            raise VNextError(f"injected {point}")

    with pytest.raises(VNextError, match="injected"):
        SidecarEvidenceBridge(service, fault_injector=inject).register_package(
            case.id, package_digest=package.package_digest
        )
    store = SidecarEvidenceStore(root)
    loaded = service.storage.load_case(case.id)
    assert loaded.evidence == case.evidence
    assert loaded.findings == case.findings
    assert store.read_registration(package.package_digest) is None
    assert not list((store.root / "bridge_receipts").glob("*.json"))
    audit = (
        (store.root / "bridge_audit.jsonl").read_text(encoding="utf8")
        if (store.root / "bridge_audit.jsonl").exists()
        else ""
    )
    assert "registration_completed" not in audit


@pytest.mark.parametrize(
    "point",
    ["process_interrupted_after_staging", "process_interrupted_after_case_replace"],
)
def test_interrupted_transaction_recovers_and_retry_is_idempotent(tmp_path, point):
    root, service, case = _case(tmp_path)
    package = _valid_readme_package(root, case)

    def inject(current):
        if current == point:
            raise IngestionInterrupted(point)

    with pytest.raises(IngestionInterrupted):
        SidecarEvidenceBridge(service, fault_injector=inject).register_package(
            case.id, package_digest=package.package_digest
        )
    bridge = SidecarEvidenceBridge(service)
    assert not service.storage.load_case(case.id).evidence
    first = bridge.register_package(case.id, package_digest=package.package_digest)
    second = bridge.register_package(case.id, package_digest=package.package_digest)
    assert first.registration_status == "completed"
    assert second.registration_status == "already_registered"
    assert len(service.storage.load_case(case.id).evidence) == len(first.evidence_ids)


def test_successful_conflict_transaction_publishes_all_surfaces(tmp_path):
    root, service, case = _case(tmp_path)
    package = _package(
        root,
        case,
        [_summary(case), _changed(case), _agent(case, used=True), _declaration(case)],
    )
    receipt = SidecarEvidenceBridge(service).register_package(
        case.id, package_digest=package.package_digest
    )
    store = SidecarEvidenceStore(root)
    loaded = service.storage.load_case(case.id)
    assert len(loaded.evidence) == len(receipt.evidence_ids)
    assert len([item for item in loaded.findings if item.code == "trusted_sidecar_conflict"]) == 1
    assert store.read_registration(package.package_digest)
    assert list((store.root / "bridge_receipts").glob("*.json"))
    assert "registration_completed" in (store.root / "bridge_audit.jsonl").read_text(encoding="utf8")
    assert "conflict_detected" in (store.root / "conflict_audit.jsonl").read_text(encoding="utf8")


def test_public_caller_cannot_forge_trusted_conflict(tmp_path):
    root, service, case = _case(tmp_path)
    package = _package(
        root,
        case,
        [_summary(case), _changed(case), _agent(case), _declaration(case)],
    )
    SidecarEvidenceBridge(service).register_package(
        case.id, package_digest=package.package_digest
    )
    assert not hasattr(service, "record_sidecar_conflict")
    assert not [
        item
        for item in service.storage.load_case(case.id).findings
        if item.code == "trusted_sidecar_conflict"
    ]
    assert TrustedSidecarConflictDetector(service).detect(
        case.id, package.package_digest
    ) is None


def test_d6_conflict_remains_valid_and_idempotent(tmp_path):
    args = next(item for item in SCENARIOS if item[0] == "D6A_declaration_conflict")
    with use_execution_context(DemoExecutionContext("d6-hardening", FIXED_TIME, "key")):
        root = make_project(tmp_path, "d6")
        service = GovernanceService(root)
        case_id, _ = build_scenario(service, *args)
        case = service.storage.load_case(case_id)
        before = len(case.findings)
        package = SidecarEvidenceStore(root).find_current_package(
            case.id, case.contribution_fingerprint
        )
        assert package is not None
        TrustedSidecarConflictDetector(service).detect(
            case.id, package["package_digest"]
        )
        after = service.storage.load_case(case.id)
    assert before == 1
    assert len(after.findings) == 1


def test_private_conflict_boundary_rejects_caller_payload(tmp_path):
    _, service, case = _case(tmp_path)
    with pytest.raises(VNextError, match="validated derivation"):
        service._record_validated_sidecar_conflict(
            case,
            {
                "message": "caller supplied",
                "severity": "critical",
                "blocking": True,
                "source_evidence_ids": ["forged"],
            },
        )


def test_concurrent_bridge_audit_writes_are_complete_json(tmp_path):
    store = SidecarEvidenceStore(tmp_path)
    count = 64

    def append(position: int) -> None:
        store.append_audit_event(
            "bridge_audit",
            {"event": "concurrent_test", "position": position},
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(append, range(count)))
    lines = (store.root / "bridge_audit.jsonl").read_text(
        encoding="utf8"
    ).splitlines()
    records = [json.loads(line) for line in lines]
    assert len(records) == count
    assert {item["position"] for item in records} == set(range(count))


def test_browser_report_separates_links_from_inline_objects():
    report = _empty_report()
    assert report["artifact_link_clicks"] == 0
    assert report["inline_object_assertions"] == 0
    assert INLINE_ASSERTION_DETAILS == (
        "D8 denied operation",
        "D10 final receipt",
        "D10 host-platform boundary",
    )


def test_artifact_digest_failure_is_rejected_before_canonical_write(tmp_path):
    root, service, case = _case(tmp_path)
    package = _valid_readme_package(root, case)
    store = SidecarEvidenceStore(root)
    metadata = store.get_package_by_digest(package.package_digest)["artifacts"][0]
    artifact_path = (
        store.root
        / package.package_digest
        / metadata["relative_storage_path"]
    )
    artifact_path.write_text("tampered", encoding="utf8")
    with pytest.raises(VNextError, match="digest"):
        SidecarEvidenceBridge(service).register_package(
            case.id, package_digest=package.package_digest
        )
    assert not service.storage.load_case(case.id).evidence
    assert store.read_registration(package.package_digest) is None


def test_bridge_receipt_content_collision_is_rejected(tmp_path):
    store = SidecarEvidenceStore(tmp_path)
    payload = {
        "case_id": "case",
        "package_digest": "a" * 64,
        "registration_status": "completed",
    }
    path, _ = store.finalize_bridge_receipt(payload)
    path.write_text("{}\n", encoding="utf8")
    with pytest.raises(VNextError, match="collision"):
        store.finalize_bridge_receipt(payload)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda item: replace(item, declaration_artifact_digest="0" * 64),
        lambda item: replace(item, canonical_evidence_ids=("forged", "ids")),
        lambda item: replace(
            item,
            typed_relation=(
                ("declared_other_agents_or_tools_used", True),
                ("observed_other_agents_or_tools_used", True),
            ),
        ),
    ],
)
def test_validated_conflict_derivation_is_rechecked_at_service_boundary(
    tmp_path, mutation
):
    root, service, case = _case(tmp_path)
    package = _package(
        root,
        case,
        [
            _summary(case),
            _changed(case),
            _agent(case, used=True),
            _declaration(case),
        ],
    )
    SidecarEvidenceBridge(service).register_package(
        case.id, package_digest=package.package_digest
    )
    loaded = service.storage.load_case(case.id)
    artifacts = TypedArtifactValidator().validate_package(
        loaded,
        SidecarEvidenceStore(root).get_package_by_digest(
            package.package_digest
        ),
        SidecarEvidenceStore(root).read_artifact,
    )
    derivation = TrustedSidecarConflictDetector(service).derive(
        loaded, package.package_digest, artifacts
    )
    assert derivation is not None
    with pytest.raises(VNextError):
        service._record_validated_sidecar_conflict(
            loaded, mutation(derivation)
        )
