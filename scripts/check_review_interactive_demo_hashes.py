"""Check deterministic Phase 2 interaction output SHA-256 values."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    REPOSITORY_ROOT
    / "examples"
    / "review_briefing"
    / "interactive_outputs"
)
DEFAULT_EXPECTED = (
    REPOSITORY_ROOT
    / "examples"
    / "review_briefing"
    / "interactive_expected_sha256.json"
)
GENERATOR_VERSION = "review-briefing-phase-2-contextual-actions"
COMMIT_BASIS = "785c8d5a0381299d62d52858f707194c49958f5d"
EXPECTED_FILE_COUNT = 19


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_hashes(output_root: Path) -> dict[str, str]:
    return {
        path.relative_to(output_root).as_posix(): sha256_file(path)
        for path in sorted(
            (item for item in output_root.rglob("*") if item.is_file()),
            key=lambda item: item.relative_to(output_root).as_posix(),
        )
    }


def expected_document(files: dict[str, str]) -> dict[str, Any]:
    return {
        "schema_version": (
            "agm.review_interaction_expected_sha256/v1"
        ),
        "generator_version": GENERATOR_VERSION,
        "commit_basis": COMMIT_BASIS,
        "file_count": len(files),
        "files": files,
    }


def write_expected(path: Path, files: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            expected_document(files),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def load_expected(path: Path) -> dict[str, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"Cannot read expected hash manifest: {path}"
        ) from exc
    files = payload.get("files")
    if (
        payload.get("schema_version")
        != "agm.review_interaction_expected_sha256/v1"
        or payload.get("generator_version") != GENERATOR_VERSION
        or not isinstance(files, dict)
        or payload.get("file_count") != len(files)
        or len(files) != EXPECTED_FILE_COUNT
    ):
        raise ValueError(f"Malformed expected hash manifest: {path}")
    return {str(key): str(value) for key, value in files.items()}


def check_hashes(
    output_root: Path,
    expected_path: Path,
) -> list[str]:
    expected = load_expected(expected_path)
    actual = output_hashes(output_root)
    problems = []
    for name in sorted(set(expected) - set(actual)):
        problems.append(f"missing: {name}")
    for name in sorted(set(actual) - set(expected)):
        problems.append(f"unexpected: {name}")
    for name in sorted(set(expected) & set(actual)):
        if expected[name] != actual[name]:
            problems.append(
                f"sha256 mismatch: {name}\n"
                f"  expected {expected[name]}\n"
                f"  actual   {actual[name]}"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--expected", type=Path, default=DEFAULT_EXPECTED)
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    expected = args.expected.resolve()
    actual = output_hashes(output)
    if args.update:
        if len(actual) != EXPECTED_FILE_COUNT:
            print(
                "Refusing to update: expected "
                f"{EXPECTED_FILE_COUNT} files, found {len(actual)}."
            )
            return 2
        write_expected(expected, actual)
        print(f"Updated {expected} with {len(actual)} SHA-256 values.")
        return 0
    try:
        problems = check_hashes(output, expected)
    except ValueError as exc:
        print(exc)
        return 2
    if problems:
        print("Interactive demo hash verification failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print(
        f"Verified {len(actual)} interactive outputs against {expected}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
