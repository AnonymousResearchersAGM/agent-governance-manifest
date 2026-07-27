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
    FIXED_TIME,
    SCENARIOS,
    demo_relative_path,
    make_project,
)


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
                scenario = builder(service)
                view = service.review_brief(
                    scenario["case_id"],
                    actor="human-maintainer",
                    role="maintainer",
                )
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
