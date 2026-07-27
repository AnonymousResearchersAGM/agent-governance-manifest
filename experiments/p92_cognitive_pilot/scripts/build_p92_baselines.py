"""Build deterministic P92 baselines through the frozen AGM domain API."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from common import (
    ARTIFACT_COMMIT,
    POLICY_FINGERPRINT,
    TASK_IDS,
    atomic_write_json,
    build_baseline_manifest,
    load_config,
)


FIXED_TIME = "2026-07-27T00:00:00Z"
PUBLIC_FIXTURE_SECRET = b"agm-p92-public-baseline-fixtures-v1"
DOC_PATH = "docs/AGM_HUMAN_GUIDE.md"
AUTH_PATHS = ["demo_app/auth.py", "demo_app/config.py"]

EVIDENCE_VALUES: dict[str, Any] = {
    "contribution_summary": "更新当前贡献并补充对应说明。",
    "changed_files": [],
    "rationale": "该修改用于完成已说明的项目目标。",
    "test_explanation": "已检查本次文档变更。",
    "test_command": "python -m pytest -q；完整回归通过。",
    "artifact": "冻结仓库中的回归依赖清单可供复核。",
    "known_limitations": "这是本地研究原型，未发现其他已知限制。",
    "security_auth_impact": (
        "修改涉及认证路径；令牌撤销、会话终止和权限边界均已覆盖。"
    ),
    "policy_impact": "本次修改不改变治理规则。",
    "agent_action_scope": (
        "主智能体在当前任务范围内修改文件；没有未披露的继续委派。"
    ),
}


def _imports(repo_root: Path):
    source = str(repo_root / "src")
    if source not in sys.path:
        sys.path.insert(0, source)
    from agm.vnext.guidance import ActorContext
    from agm.vnext.models import VNextError
    from agm.vnext.runtime import DemoExecutionContext, use_execution_context
    from agm.vnext.service import GovernanceService

    return (
        ActorContext,
        VNextError,
        DemoExecutionContext,
        use_execution_context,
        GovernanceService,
    )


def _service(repo_root: Path, work_root: Path):
    *_, GovernanceService = _imports(repo_root)
    return GovernanceService(repo_root, work_root=work_root)


def _open_case(
    service,
    case_id: str,
    changed_files: list[str],
    *,
    autonomy_profile: str = "supervised_agent",
    semantic_targets: list[str] | None = None,
) -> None:
    case, _ = service.open_case(
        changed_files,
        requested_mode="declared_agent_mediated",
        actor="p92-contributor-agent",
        actor_role="contributor_agent",
        case_id=case_id,
        base_commit=ARTIFACT_COMMIT,
        semantic_targets=semantic_targets,
        autonomy_profile=autonomy_profile,
        diff_material=f"{case_id}:initial",
        timestamp=FIXED_TIME,
    )
    if case is None:
        raise RuntimeError(f"P92 baseline did not create case {case_id}")


def _add_all_evidence(
    service,
    case_id: str,
    *,
    overrides: dict[str, Any] | None = None,
) -> None:
    case = service.storage.load_case(case_id)
    overrides = overrides or {}
    for obligation in case.obligations:
        if obligation.type != "evidence":
            continue
        value = overrides.get(
            obligation.evidence_type,
            EVIDENCE_VALUES[obligation.evidence_type],
        )
        if obligation.evidence_type == "changed_files":
            value = list(case.changed_files)
        extra: dict[str, Any] = {}
        if obligation.evidence_type == "test_command":
            extra = {
                "command": "python -m pytest -q",
                "environment": "Python / frozen P92 artifact",
            }
        if obligation.evidence_type == "artifact":
            extra = {"artifact_path": "requirements.txt"}
        service.add_evidence(
            case_id,
            actor="p92-contributor-agent",
            actor_role="contributor_agent",
            obligation_ids=[obligation.obligation_id],
            evidence_type=obligation.evidence_type,
            value=value,
            source_tool="p92-baseline-builder",
            observed_at="2026-07-27T00:02:00Z",
            **extra,
        )


def _prepare(service, case_id: str) -> None:
    service.prepare_case(
        case_id,
        actor="p92-contributor-agent",
        actor_role="contributor_agent",
    )
    case = service.storage.load_case(case_id)
    if case.state == "awaiting_human_attestation":
        service.attest(
            case_id,
            actor="p92-accountable-human",
            role="accountable_human",
            reviewed_scope=list(case.changed_files),
            statement="已审阅当前版本、材料集合和明确列出的范围。",
            timestamp="2026-07-27T00:05:00Z",
        )


def _scoped_revalidation(
    service,
    *,
    case_id: str,
    changed_files: list[str],
    target_obligation: str,
    revised_evidence_type: str,
    revised_claim: str,
    semantic_targets: list[str] | None = None,
) -> None:
    _open_case(
        service,
        case_id,
        changed_files,
        semantic_targets=semantic_targets,
    )
    _add_all_evidence(
        service,
        case_id,
        overrides={revised_evidence_type: revised_claim},
    )
    _prepare(service, case_id)
    service.verify(
        case_id,
        actor="p92-maintainer",
        role="maintainer",
        reason="P92 基线前置材料已按当前冻结原型完成检查。",
        timestamp="2026-07-27T00:08:00Z",
    )
    service.request_repair(
        case_id,
        actor="p92-maintainer",
        role="maintainer",
        message="仅重新检查当前指定说明。",
        affected_obligation_ids=[target_obligation],
        finding_code="p92_scoped_revalidation",
    )
    service.resubmit(
        case_id,
        actor="p92-contributor-agent",
        role="contributor_agent",
        summary="贡献侧补交当前指定说明，其他材料未改变。",
        affected_obligation_ids=[target_obligation],
        diff_material=f"{case_id}:initial",
        change_classification="non_material",
        change_reason="补交记录不改变贡献版本；仅重新提交当前说明供复核。",
    )
    _prepare(service, case_id)


def _build_t0(service) -> None:
    _scoped_revalidation(
        service,
        case_id="p92-t0-training",
        changed_files=[DOC_PATH],
        target_obligation="O-AGENT-SCOPE",
        revised_evidence_type="agent_action_scope",
        revised_claim=(
            "主智能体仅在当前任务范围内更新文档，使用工作区文件权限；"
            "没有启动子智能体，也没有继续委派。负责人审阅覆盖当前版本。"
        ),
    )


def _build_t1(service) -> None:
    _open_case(
        service,
        "p92-t1-contribution-side",
        AUTH_PATHS,
        semantic_targets=["authentication", "authorization"],
    )


def _build_t2(service) -> None:
    _scoped_revalidation(
        service,
        case_id="p92-t2-supplement",
        changed_files=[DOC_PATH],
        target_obligation="O-AGENT-SCOPE",
        revised_evidence_type="agent_action_scope",
        revised_claim=(
            "补交说明只写明主智能体修改了文档，没有列出系统记录所涉及的"
            "子智能体行动、命令范围或继续委派边界；当前说明无法确认实际"
            "行动是否都在负责人审阅范围内。"
        ),
    )


def _build_t3(service) -> None:
    _, VNextError, *_ = _imports(service.root)
    _open_case(
        service,
        "p92-t3-system-handled",
        [DOC_PATH],
        autonomy_profile="human_direct",
    )
    _add_all_evidence(service, "p92-t3-system-handled")
    _prepare(service, "p92-t3-system-handled")
    try:
        service.verify(
            "p92-t3-system-handled",
            actor="p92-contributor-agent",
            role="contributor_agent",
            reason="贡献侧智能体尝试执行维护者检查。",
        )
    except VNextError:
        pass
    else:
        raise RuntimeError("Unauthorized P92 baseline operation was not rejected")


def _build_t4(service) -> None:
    _scoped_revalidation(
        service,
        case_id="p92-t4-material-risk",
        changed_files=AUTH_PATHS,
        target_obligation="O-AUTH-IMPACT",
        revised_evidence_type="security_auth_impact",
        revised_claim=(
            "贡献者声明此次令牌撤销改动不会影响权限边界。补交说明同时记录："
            "关键认证回归测试失败，权限撤销后旧令牌仍可访问受限接口；"
            "当前没有证据支持“权限边界不受影响”的声明。"
        ),
        semantic_targets=["authentication", "authorization"],
    )


BUILDERS = {
    "T0": _build_t0,
    "T1": _build_t1,
    "T2": _build_t2,
    "T3": _build_t3,
    "T4": _build_t4,
}


def build(repo_root: Path, package_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    package_root = package_root.resolve()
    config = load_config(package_root)
    baseline_root = package_root / "baseline"
    if baseline_root.exists():
        shutil.rmtree(baseline_root)
    baseline_root.mkdir(parents=True)
    _, _, DemoExecutionContext, use_execution_context, _ = _imports(repo_root)
    summaries = {}
    for task_id in TASK_IDS:
        task = config["tasks"][task_id]
        destination = baseline_root / task["baseline"]
        destination.mkdir(parents=True)
        with use_execution_context(
            DemoExecutionContext(
                scenario_namespace=f"p92-{task_id.lower()}",
                fixed_timestamp=FIXED_TIME,
                token_secret=PUBLIC_FIXTURE_SECRET,
            )
        ):
            service = _service(repo_root, destination)
            BUILDERS[task_id](service)
            case = service.storage.load_case(task["case_id"])
            summaries[task_id] = {
                "case_id": case.id,
                "state": case.state,
                "risk": case.overall_risk_level,
                "transition_count": len(
                    service.storage.read_transitions(case.id)
                ),
                "finding_count": len(case.findings),
                "evidence_count": len(case.evidence),
            }
    manifest = build_baseline_manifest(package_root)
    atomic_write_json(baseline_root / "baseline_sha256.json", manifest)
    if manifest["policy_fingerprint"] != POLICY_FINGERPRINT:
        raise RuntimeError("P92 baseline manifest policy fingerprint mismatch")
    return {"tasks": summaries, "file_count": len(manifest["files"])}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--package-root", type=Path, default=Path(__file__).parents[1])
    args = parser.parse_args()
    print(
        json.dumps(
            build(args.repo_root, args.package_root),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
