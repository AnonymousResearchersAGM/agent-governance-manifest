"""Initialize an AGM contributor evidence package skeleton."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from classify_risk_zone import classify_files, load_manifest


ROOT = Path(__file__).resolve().parents[1]


def normalize(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_task_title(task_path: Path) -> str:
    if not task_path.exists():
        return task_path.stem
    for line in task_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
        if stripped.startswith("- task_title:"):
            return stripped.split(":", 1)[1].strip().strip('"')
    return task_path.stem


def evidence_files_for(required: list[str]) -> list[str]:
    file_map = {
        "contribution_report": "contribution_report.md",
        "test_report": "test_report.md",
        "trace_manifest": "trace_manifest.json",
        "human_review_declaration": "human_review_declaration.md",
    }
    return [file_map[item] for item in required if item in file_map]


def write_if_allowed(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def contribution_report(task: str, changed_files: list[str], classification: dict) -> str:
    zones = sorted({match["zone"] for match in classification["matched_risk_zones"]})
    required = classification["required_evidence"]
    human_status = "required pending" if classification["highest_risk_level"] in {"high", "critical"} else "not required"
    return "\n".join(
        [
            "# AGM Contribution Report",
            "",
            "## Structured Fields",
            "",
            f'- task_file: "{task}"',
            '- contribution_summary: "TBD: summarize the completed change factually."',
            f'- affected_files: "{"; ".join(changed_files)}"',
            f'- declared_risk_zone: "{"; ".join(zones)}"',
            f'- declared_risk_level: "{classification["highest_risk_level"]}"',
            f'- required_evidence: "{"; ".join(required)}"',
            '- ai_assistance_disclosure: "TBD: disclose AI assistance at a high level; do not include prompts or private reasoning."',
            '- tests_run: "TBD: list test commands or not run."',
            '- test_outcomes: "TBD: pass, fail, or not run with concise result."',
            '- known_limitations: "TBD: list known limitations or none."',
            '- linked_issues: "TBD: issue id/url or explicit none."',
            f'- human_confirmation_status: "{human_status}"',
            '- missing_evidence: "TBD: list missing evidence or none."',
            "",
            "## Boundary",
            "",
            "This evidence package intentionally excludes original prompts, chain-of-thought, detailed intermediate reasoning, private exploratory attempts, and persuasive narratives.",
            "",
        ]
    )


def test_report() -> str:
    return "\n".join(
        [
            "# AGM Test Report",
            "",
            "## Structured Fields",
            "",
            '- commands: "TBD: test command or not run"',
            '- environment: "TBD: local or CI environment and Python version if known"',
            '- outcomes: "TBD: command => pass/fail/not run with short summary"',
            '- coverage_notes: "TBD: behavior covered by tests"',
            '- failures: "TBD: failures or none"',
            "",
        ]
    )


def trace_manifest(task: str, changed_files: list[str], classification: dict, output_dir: Path) -> str:
    zones = sorted({match["zone"] for match in classification["matched_risk_zones"]})
    required = classification["required_evidence"]
    data = {
        "manifest_version": "0.1",
        "task_id": Path(task).stem,
        "task_file": task,
        "linked_issues": ["TBD: issue id/url or none"],
        "affected_files": changed_files,
        "risk_zones": zones,
        "risk_level": classification["highest_risk_level"],
        "required_evidence": required,
        "evidence_files": evidence_files_for(required),
        "evidence_package_dir": normalize(output_dir),
        "human_confirmation_required": classification["highest_risk_level"] in {"high", "critical"},
        "human_confirmation_status": "required pending"
        if classification["highest_risk_level"] in {"high", "critical"}
        else "not required",
        "reasoning_materials_excluded": True,
        "excluded_materials_note": "Original prompts, chain-of-thought, detailed intermediate reasoning, private exploratory attempts, and persuasive narratives are not part of the required evidence package.",
    }
    return json.dumps(data, indent=2) + "\n"


def human_review_declaration(classification: dict) -> str:
    zones = sorted({match["zone"] for match in classification["matched_risk_zones"]})
    return "\n".join(
        [
            "# AGM Human Review Declaration",
            "",
            "## Structured Fields",
            "",
            '- human_confirmation_required: "true"',
            '- human_confirmation_status: "required pending"',
            '- reviewer_name_or_role: "TBD: human maintainer role or handle"',
            f'- reviewed_risk_zones: "{"; ".join(zones)}"',
            '- reviewed_evidence_files: "TBD: evidence files reviewed"',
            '- decision_scope: "Human review confirmation only; final merge decision remains separate."',
            '- notes: "TBD: short factual notes or none"',
            "",
            "## Boundary",
            "",
            "This declaration confirms human review status without requiring contributor prompts or private reasoning.",
            "",
        ]
    )


def init_package(task: Path, changed_files: list[str], output_dir: Path, force: bool = False) -> dict:
    manifest = load_manifest(ROOT / "agent_governance_manifest.yml")
    classification = classify_files(changed_files, manifest)
    output_dir.mkdir(parents=True, exist_ok=True)
    normalized_files = classification["changed_files"]
    task_name = normalize(task)

    written = []
    skipped = []
    files = {
        "contribution_report.md": contribution_report(task_name, normalized_files, classification),
        "test_report.md": test_report(),
        "trace_manifest.json": trace_manifest(task_name, normalized_files, classification, output_dir),
    }
    if classification["highest_risk_level"] in {"high", "critical"}:
        files["human_review_declaration.md"] = human_review_declaration(classification)

    for file_name, content in files.items():
        path = output_dir / file_name
        if write_if_allowed(path, content, force):
            written.append(file_name)
        else:
            skipped.append(file_name)

    return {
        "task_title": read_task_title(task),
        "task_file": task_name,
        "changed_files": normalized_files,
        "highest_risk_level": classification["highest_risk_level"],
        "matched_risk_zones": classification["matched_risk_zones"],
        "required_evidence": classification["required_evidence"],
        "evidence_package_dir": normalize(output_dir),
        "written_files": written,
        "skipped_existing_files": skipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize an AGM evidence package skeleton.")
    parser.add_argument("--task", required=True, help="Task file path, usually under evaluation_tasks/.")
    parser.add_argument("--changed-files", nargs="+", required=True, help="Changed files relative to the repository root.")
    parser.add_argument("--output-dir", required=True, help="Evidence package output directory.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing evidence files.")
    args = parser.parse_args()

    result = init_package(Path(args.task), args.changed_files, Path(args.output_dir), force=args.force)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

