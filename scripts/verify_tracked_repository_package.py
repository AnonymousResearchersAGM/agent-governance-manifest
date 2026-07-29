"""Verify a tracked ZIP before and after deterministic regeneration."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from package_tracked_repository import verify_archive


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    "scripts/check_reviewer_guidance_demo_hashes.py",
    "scripts/check_review_briefing_demo_hashes.py",
    "scripts/check_review_interactive_demo_hashes.py",
    "scripts/check_pr_diagnostic_demo_hashes.py",
)
GENERATORS = (
    "scripts/generate_reviewer_guidance_demos.py",
    "scripts/generate_review_briefing_demos.py",
    "scripts/generate_review_interactive_demos.py",
    "scripts/generate_pr_diagnostic_demos.py",
)


def _run(root: Path, script: str) -> None:
    subprocess.run(
        [sys.executable, script],
        cwd=root,
        check=True,
    )


def _snapshot(root: Path, members: tuple[str, ...]) -> dict[str, str]:
    return {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in members
    }


def verify_fresh_extract(
    archive_path: Path,
    *,
    ref: str = "HEAD",
) -> dict[str, object]:
    archive_path = archive_path.resolve()
    members = verify_archive(archive_path, ref=ref)
    with tempfile.TemporaryDirectory(
        prefix="agm-tracked-zip-verification-"
    ) as raw:
        extracted = Path(raw)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(extracted)
        before = _snapshot(extracted, members)
        for script in CHECKS:
            _run(extracted, script)
        for script in GENERATORS:
            _run(extracted, script)
        for script in CHECKS:
            _run(extracted, script)
        _run(extracted, "scripts/validate_pr_diagnostic_links.py")
        _run(extracted, "scripts/validate_pr_diagnostic_participant_terms.py")
        after = _snapshot(extracted, members)
        changed = sorted(
            name for name in members if before[name] != after[name]
        )
        generated_untracked = sorted(
            path.relative_to(extracted).as_posix()
            for path in extracted.rglob("*")
            if path.is_file()
            and path.relative_to(extracted).as_posix() not in set(members)
            and "__pycache__" not in path.parts
        )
        if changed or generated_untracked:
            raise ValueError(
                "Fresh ZIP regeneration was not content-stable: "
                f"changed={changed}, generated_untracked={generated_untracked}"
            )
    return {
        "archive": str(archive_path),
        "tracked_file_count": len(members),
        "hash_checks_before_generation": len(CHECKS),
        "hash_checks_after_generation": len(CHECKS),
        "fresh_demo_links_valid": True,
        "participant_term_scan_valid": True,
        "regeneration_content_stable": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--ref", default="HEAD")
    args = parser.parse_args()
    print(
        json.dumps(
            verify_fresh_extract(args.archive, ref=args.ref),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
