"""Generate deterministic static Phase 2 interaction models."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
SCRIPTS_ROOT = REPOSITORY_ROOT / "scripts"
for candidate in (SOURCE_ROOT, SCRIPTS_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from agm.vnext.briefing.actions import (  # noqa: E402
    compile_contextual_actions,
    compile_final_decision_view,
    render_final_decision_html,
    render_interactive_review_html,
)
from agm.vnext.guidance import ActorContext  # noqa: E402
from agm.vnext.runtime import (  # noqa: E402
    DemoExecutionContext,
    use_execution_context,
)
from agm.vnext.service import GovernanceService  # noqa: E402
from agm.vnext.storage import atomic_write_text  # noqa: E402
from generate_review_briefing_demos import (  # noqa: E402
    _brief_evidence_values,
    _contribution_context,
)
from generate_reviewer_guidance_demos import (  # noqa: E402
    DEMO_TOKEN_SECRET,
    EVIDENCE_VALUES,
    FIXED_TIME,
    SCENARIOS,
    demo_relative_path,
    make_project,
)


ACTOR = ActorContext(
    actor="human-maintainer",
    role="maintainer",
    human=True,
)
PRE_FINAL_SLUG = "09_pre_final_decision"


def _compile(
    service: GovernanceService,
    case_id: str,
    slug: str,
):
    case = service.storage.load_case(case_id)
    brief = service.review_brief(
        case_id,
        actor=ACTOR.actor,
        role=ACTOR.role,
        contribution=_contribution_context(
            slug if slug in dict(SCENARIOS) else "03_scoped_repair"
        ),
    )
    actions = compile_contextual_actions(
        review_brief=brief,
        governance_case=case,
        actor_context=ACTOR,
        policy_config=service.config,
        live_actions_enabled=False,
    )
    return case, brief, actions


def generate(output_root: Path) -> list[dict[str, str]]:
    output_root.mkdir(parents=True, exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(
        prefix="agm-review-interactive-demos-"
    ) as raw:
        temporary = Path(raw)
        for slug, builder in SCENARIOS:
            with use_execution_context(
                DemoExecutionContext(
                    scenario_namespace=f"interactive-{slug}",
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
                    _, _, actions = _compile(
                        service,
                        scenario["case_id"],
                        slug,
                    )
                finally:
                    EVIDENCE_VALUES.clear()
                    EVIDENCE_VALUES.update(original_values)
                scenario_root = output_root / slug
                model_path = scenario_root / "review_action_model.json"
                html_path = scenario_root / "review_interactive.html"
                atomic_write_text(
                    model_path,
                    json.dumps(
                        actions.to_dict(),
                        ensure_ascii=False,
                        indent=2,
                    )
                    + "\n",
                )
                atomic_write_text(
                    html_path,
                    render_interactive_review_html(actions),
                )
                results.append(
                    {
                        "scenario": slug,
                        "model": demo_relative_path(
                            model_path,
                            output_root,
                        ),
                        "html": demo_relative_path(
                            html_path,
                            output_root,
                        ),
                    }
                )

        with use_execution_context(
            DemoExecutionContext(
                scenario_namespace="interactive-pre-final",
                fixed_timestamp=FIXED_TIME,
                token_secret=DEMO_TOKEN_SECRET,
            )
        ):
            root = make_project(temporary, PRE_FINAL_SLUG)
            service = GovernanceService(root)
            original_values = dict(EVIDENCE_VALUES)
            try:
                EVIDENCE_VALUES.update(
                    _brief_evidence_values("03_scoped_repair")
                )
                scenario = dict(SCENARIOS)["03_scoped_repair"](service)
                service.verify(
                    scenario["case_id"],
                    actor=ACTOR.actor,
                    role=ACTOR.role,
                    reason=(
                        "Deterministic pre-final fixture verification; "
                        "not acceptance."
                    ),
                    obligation_ids=["O-AGENT-SCOPE"],
                    timestamp=FIXED_TIME,
                )
                case, brief, actions = _compile(
                    service,
                    scenario["case_id"],
                    PRE_FINAL_SLUG,
                )
                final_view = compile_final_decision_view(
                    review_brief=brief,
                    governance_case=case,
                    actor_context=ACTOR,
                    policy_config=service.config,
                )
            finally:
                EVIDENCE_VALUES.clear()
                EVIDENCE_VALUES.update(original_values)
            scenario_root = output_root / PRE_FINAL_SLUG
            model_path = scenario_root / "review_action_model.json"
            html_path = scenario_root / "review_interactive.html"
            atomic_write_text(
                model_path,
                json.dumps(
                    {
                        "schema_version": (
                            "agm.review_interaction_demo/v0.2-dev"
                        ),
                        "live_actions_enabled": False,
                        "review_actions": actions.to_dict(),
                        "final_decision": final_view.to_dict(),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
            )
            atomic_write_text(
                html_path,
                render_final_decision_html(final_view),
            )
            results.append(
                {
                    "scenario": PRE_FINAL_SLUG,
                    "model": demo_relative_path(
                        model_path,
                        output_root,
                    ),
                    "html": demo_relative_path(
                        html_path,
                        output_root,
                    ),
                }
            )
    atomic_write_text(
        output_root / "manifest.json",
        json.dumps(
            {
                "schema_version": (
                    "agm.review_interaction_demo_manifest/v0.2-dev"
                ),
                "scenario_count": len(results),
                "scenarios": results,
            },
            ensure_ascii=False,
            indent=2,
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
            / "interactive_outputs"
        ),
    )
    args = parser.parse_args()
    results = generate(args.output.resolve())
    print(
        json.dumps(
            {"generated": len(results), "outputs": results},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
