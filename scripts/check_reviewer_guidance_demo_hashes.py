"""Check Reviewer Guidance research outputs against frozen SHA-256 values."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    REPOSITORY_ROOT / "examples" / "reviewer_guidance" / "outputs"
)
DEFAULT_EXPECTED = (
    REPOSITORY_ROOT
    / "examples"
    / "reviewer_guidance"
    / "expected_sha256.json"
)
GENERATOR_VERSION = "reviewer-guidance-demo-v2-cross-platform"
COMMIT_BASIS = "b96a81cbc4da6d662286a7c549b867cb3490ade0"
EXPECTED_FILE_COUNT = 25


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
        "schema_version": "agm.reviewer_guidance_expected_sha256/v1",
        "generator_version": GENERATOR_VERSION,
        "commit_basis": COMMIT_BASIS,
        "file_count": len(files),
        "files": files,
    }


def write_expected(path: Path, files: dict[str, str]) -> None:
    payload = json.dumps(
        expected_document(files),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((payload + "\n").encode("utf-8"))


def load_expected(path: Path) -> dict[str, str]:
    try:
        payload = json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read expected hash manifest: {path}") from exc
    files = payload.get("files")
    if (
        payload.get("schema_version")
        != "agm.reviewer_guidance_expected_sha256/v1"
        or payload.get("generator_version") != GENERATOR_VERSION
        or not isinstance(files, dict)
        or payload.get("file_count") != len(files)
        or len(files) != EXPECTED_FILE_COUNT
        or not all(
            isinstance(name, str) and isinstance(digest, str)
            for name, digest in files.items()
        )
    ):
        raise ValueError(f"Malformed expected hash manifest: {path}")
    return dict(files)


def check_hashes(
    output_root: Path,
    expected_path: Path,
) -> list[str]:
    expected = load_expected(expected_path)
    actual = output_hashes(output_root)
    problems: list[str] = []
    for name in sorted(set(expected) - set(actual)):
        problems.append(f"missing: {name}")
    for name in sorted(set(actual) - set(expected)):
        problems.append(f"unexpected: {name}")
    for name in sorted(set(expected) & set(actual)):
        if actual[name] != expected[name]:
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
    parser.add_argument(
        "--update",
        action="store_true",
        help=(
            "Explicitly replace the frozen values from existing outputs. "
            "Use only after researcher review."
        ),
    )
    args = parser.parse_args()
    output_root = args.output.resolve()
    expected_path = args.expected.resolve()
    actual = output_hashes(output_root)
    if args.update:
        if len(actual) != EXPECTED_FILE_COUNT:
            print(
                "Refusing to update: expected "
                f"{EXPECTED_FILE_COUNT} output files, found {len(actual)}."
            )
            return 2
        write_expected(expected_path, actual)
        print(
            f"Updated {expected_path} with {len(actual)} frozen SHA-256 values."
        )
        return 0
    try:
        problems = check_hashes(output_root, expected_path)
    except ValueError as exc:
        print(exc)
        return 2
    if problems:
        print("Reviewer Guidance demo hash verification failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print(
        f"Verified {len(actual)} Reviewer Guidance outputs against "
        f"{expected_path}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
