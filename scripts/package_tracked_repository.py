"""Package exact Git blobs into a tracked-only, directly verifiable ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PARTS = {
    ".git",
    ".agm-work",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}


def _git(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout


def tracked_files(ref: str) -> tuple[str, ...]:
    completed = subprocess.run(
        ["git", "ls-tree", "-rz", "--name-only", ref],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
    )
    return tuple(
        name.decode("utf-8")
        for name in completed.stdout.split(b"\x00")
        if name
    )


def _validate_member(name: str) -> None:
    path = PurePosixPath(name)
    if (
        path.is_absolute()
        or ".." in path.parts
        or any(part in FORBIDDEN_PARTS for part in path.parts)
    ):
        raise ValueError(f"Unsafe or runtime-only ZIP member: {name}")


def verify_archive(path: Path, *, ref: str) -> tuple[str, ...]:
    expected = tracked_files(ref)
    with zipfile.ZipFile(path) as archive:
        actual = tuple(
            item.filename
            for item in archive.infolist()
            if not item.is_dir()
        )
    for name in actual:
        _validate_member(name)
    if set(actual) != set(expected) or len(actual) != len(expected):
        missing = sorted(set(expected) - set(actual))
        unexpected = sorted(set(actual) - set(expected))
        raise ValueError(
            "ZIP file list does not equal the Git tracked-file list: "
            f"missing={missing}, unexpected={unexpected}"
        )
    return actual


def package_repository(
    *,
    output: Path,
    ref: str = "HEAD",
) -> dict[str, object]:
    commit = _git("rev-parse", "--verify", f"{ref}^{{commit}}").strip()
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_name = handle.name
        subprocess.run(
            [
                "git",
                "archive",
                "--format=zip",
                f"--output={temporary_name}",
                commit,
            ],
            cwd=REPOSITORY_ROOT,
            check=True,
        )
        members = verify_archive(Path(temporary_name), ref=commit)
        os.replace(temporary_name, output)
        temporary_name = None
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return {
        "archive": str(output),
        "commit": commit,
        "tracked_file_count": len(members),
        "size_bytes": output.stat().st_size,
        "sha256": digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create a ZIP from exact Git blobs instead of platform-specific "
            "working-tree bytes."
        )
    )
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    commit = _git(
        "rev-parse", "--verify", f"{args.ref}^{{commit}}"
    ).strip()
    output = args.output or (
        REPOSITORY_ROOT
        / (
            "agent-governance-manifest-phase-2-0-1-"
            f"{commit[:7]}.zip"
        )
    )
    print(
        json.dumps(
            package_repository(output=output, ref=commit),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
