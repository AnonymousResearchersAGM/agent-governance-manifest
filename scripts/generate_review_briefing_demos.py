"""Generate deterministic Phase 1 Review Briefing artifacts."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))
if str(REPOSITORY_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

from agm.vnext.briefing import (  # noqa: E402
    render_review_brief_html,
    render_review_brief_json,
    render_review_brief_markdown,
)
from agm.vnext.runtime import (  # noqa: E402
    DemoExecutionContext,
    use_execution_context,
)
from agm.vnext.service import GovernanceService  # noqa: E402
from agm.vnext.storage import atomic_write_text  # noqa: E402
from generate_reviewer_guidance_demos import (  # noqa: E402
    DEMO_TOKEN_SECRET,
    EVIDENCE_VALUES,
    FIXED_TIME,
    SCENARIOS,
    demo_relative_path,
    make_project,
)


DEMO_CONTRIBUTIONS: dict[str, dict[str, object]] = {
    "01_multi_risk_missing": {
        "title": "认证令牌刷新与配置调整",
        "summary": (
            "本次贡献修改认证模块中的令牌刷新逻辑，并同步调整认证配置，"
            "用于修复令牌即将过期时偶发退出登录的问题。"
        ),
        "agent_actions": (
            "编码智能体修改了认证代码和配置文件；可修改工作区文件并运行"
            "测试；没有继续委派。"
        ),
    },
    "02_material_partial_invalidation": {
        "title": "令牌失效说明的后续修订",
        "summary": (
            "贡献者在原提交基础上进一步修改了令牌失效时间的说明；"
            "原修改说明没有覆盖这次新增内容。"
        ),
        "agent_actions": (
            "编码智能体更新了当前文档；没有修改已保留材料所覆盖的其他范围，"
            "也没有继续委派。"
        ),
    },
    "03_scoped_repair": {
        "title": "补充智能体行动与委派说明",
        "summary": (
            "贡献者补充了智能体行动与委派说明；本次补充未修改代码、"
            "测试结果或安全影响说明。"
        ),
        "agent_actions": (
            "编码智能体仅处理本次文档贡献并运行既有检查；没有继续委派，"
            "补充说明覆盖当前版本。"
        ),
    },
    "04_unauthorized_agent_verification": {
        "title": "认证模块使用说明更新",
        "summary": "本次贡献更新了认证模块的使用说明。",
    },
    "05_lightweight_low_risk": {
        "title": "文档命令与链接修正",
        "summary": (
            "本次贡献修正文档中的命令拼写，并更新一个失效链接；"
            "未修改代码、配置、依赖或执行逻辑。"
        ),
    },
    "06_governance_self_modification": {
        "title": "AGM 风险规则与执行逻辑调整",
        "summary": (
            "本次贡献修改项目的 AGM 风险规则和治理执行逻辑，"
            "需要职责分离的独立检查。"
        ),
    },
    "07_policy_migration_warning": {
        "title": "贡献准备期间的规则变化",
        "summary": (
            "项目在该贡献准备期间更新了治理规则；原有要求不会被系统"
            "笼统判为失效，需要先查看规则比较再决定是否迁移。"
        ),
    },
    "08_human_final_decision_closure": {
        "title": "已完成最终决定的文档贡献",
        "summary": (
            "本次贡献的材料准备、负责人确认和维护者检查均已完成；"
            "具有最终决定权的人类维护者已经作出接受决定。"
        ),
    },
}


def _brief_evidence_values(slug: str) -> dict[str, object]:
    contribution = DEMO_CONTRIBUTIONS[slug]
    return {
        "contribution_summary": contribution["summary"],
        "rationale": "这次修改用于解决贡献说明中列出的具体维护问题。",
        "test_explanation": "已人工检查本次文档修改的命令、链接和表述。",
        "test_command": "完整本地回归测试已通过。",
        "artifact": "已附上可在本地检查的测试输出。",
        "known_limitations": "当前结论仅覆盖本次明确列出的修改范围。",
        "security_auth_impact": (
            "修改涉及认证行为；令牌刷新、会话失效和权限边界需要单独检查。"
        ),
        "policy_impact": (
            "修改涉及治理规则与执行逻辑的一致性、兼容性和迁移影响。"
        ),
        "agent_action_scope": contribution.get(
            "agent_actions",
            "编码智能体在本次任务范围内修改文件并提供检查记录；没有继续委派。",
        ),
    }


def _contribution_context(slug: str) -> dict[str, object]:
    contribution = DEMO_CONTRIBUTIONS[slug]
    declaration = {
        "summary": contribution["summary"],
        "source": "贡献者提供的演示说明",
    }
    if "agent_actions" in contribution:
        declaration.update(
            {
                "agent_used": True,
                "agent_actions": [contribution["agent_actions"]],
                "delegation_detected": False,
            }
        )
    return {
        "title": contribution["title"],
        "contributor_declaration": declaration,
    }


def generate(output_root: Path) -> list[dict[str, str]]:
    """Compile the same eight cases into the higher-level brief."""

    output_root.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(
        prefix="agm-review-briefing-demos-"
    ) as raw:
        temporary = Path(raw)
        for slug, builder in SCENARIOS:
            with use_execution_context(
                DemoExecutionContext(
                    scenario_namespace=f"brief-{slug}",
                    fixed_timestamp=FIXED_TIME,
                    token_secret=DEMO_TOKEN_SECRET,
                )
            ):
                root = make_project(temporary, slug)
                service = GovernanceService(root)
                original_values = dict(EVIDENCE_VALUES)
                try:
                    EVIDENCE_VALUES.update(_brief_evidence_values(slug))
                    scenario = builder(service)
                    view = service.review_brief(
                        scenario["case_id"],
                        actor="human-maintainer",
                        role="maintainer",
                        contribution=_contribution_context(slug),
                    )
                finally:
                    EVIDENCE_VALUES.clear()
                    EVIDENCE_VALUES.update(original_values)
                scenario_root = output_root / slug
                paths = {
                    "json": scenario_root / "brief.json",
                    "markdown": scenario_root / "brief.md",
                    "html": scenario_root / "brief.html",
                }
                atomic_write_text(
                    paths["json"], render_review_brief_json(view)
                )
                atomic_write_text(
                    paths["markdown"],
                    render_review_brief_markdown(view),
                )
                atomic_write_text(
                    paths["html"], render_review_brief_html(view)
                )
                results.append(
                    {
                        "scenario": slug,
                        **{
                            key: demo_relative_path(path, output_root)
                            for key, path in paths.items()
                        },
                    }
                )
    atomic_write_text(
        output_root / "manifest.json",
        json.dumps(
            {
                "schema_version": (
                    "agm.review_brief_demo_manifest/v0.2-dev"
                ),
                "scenario_count": len(results),
                "scenarios": results,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
    )
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            REPOSITORY_ROOT
            / "examples"
            / "review_briefing"
            / "outputs"
        ),
    )
    args = parser.parse_args()
    results = generate(args.output.resolve())
    print(
        json.dumps(
            {"generated": len(results), "outputs": results},
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
