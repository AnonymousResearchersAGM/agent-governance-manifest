"""Build a clean, deterministic P92 delivery directory and ZIP."""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from pathlib import Path
from typing import Any

from common import (
    ARTIFACT_COMMIT,
    POLICY_FINGERPRINT,
    atomic_write_json,
    sha256_file,
    stable_file_map,
)


EXCLUDED_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".venv",
}
EXCLUDED_FILES = {
    "README.md",
    "package_integrity.json",
}
FIXED_ZIP_TIME = (2026, 7, 27, 0, 0, 0)


def _copy_source(source: Path, output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for path in sorted(
        source.rglob("*"),
        key=lambda item: item.relative_to(source).as_posix(),
    ):
        relative = path.relative_to(source)
        if any(part in EXCLUDED_NAMES for part in relative.parts):
            continue
        if relative.as_posix() in EXCLUDED_FILES:
            continue
        if relative.parts and relative.parts[0] in {"runtime", "records"}:
            continue
        if path.is_dir():
            (output / relative).mkdir(parents=True, exist_ok=True)
        elif path.suffix not in {".pyc", ".pyo"}:
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    (output / "runtime").mkdir(exist_ok=True)
    (output / "records").mkdir(exist_ok=True)


def _write_integrity(output: Path) -> dict[str, Any]:
    immutable = stable_file_map(
        output,
        excluded={"package_integrity.json"},
    )
    immutable = {
        name: digest
        for name, digest in immutable.items()
        if not name.startswith("runtime/")
        and not name.startswith("records/")
    }
    payload = {
        "schema_version": "agm.p92_package_integrity/v1",
        "artifact_commit": ARTIFACT_COMMIT,
        "policy_fingerprint": POLICY_FINGERPRINT,
        "formal_sample": False,
        "self_excluded": True,
        "mutable_directories": ["runtime", "records"],
        "immutable_files": immutable,
    }
    atomic_write_json(output / "package_integrity.json", payload)
    return payload


def _zip(output: Path, archive: Path) -> None:
    if archive.exists():
        archive.unlink()
    files = sorted(
        (path for path in output.rglob("*") if path.is_file()),
        key=lambda item: item.relative_to(output).as_posix(),
    )
    directories = sorted(
        (
            path
            for path in output.rglob("*")
            if path.is_dir() and not any(path.iterdir())
        ),
        key=lambda item: item.relative_to(output).as_posix(),
    )
    with zipfile.ZipFile(
        archive,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as handle:
        for directory in directories:
            name = directory.relative_to(output).as_posix().rstrip("/") + "/"
            info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
            info.external_attr = 0o40755 << 16
            handle.writestr(info, b"")
        for path in files:
            name = path.relative_to(output).as_posix()
            info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            handle.writestr(info, path.read_bytes(), compresslevel=9)


def build(source: Path, output: Path, archive: Path | None = None) -> dict[str, Any]:
    source = source.resolve()
    output = output.resolve()
    archive = (
        archive.resolve()
        if archive
        else output.with_name(output.name + ".zip")
    )
    _copy_source(source, output)
    integrity = _write_integrity(output)
    _zip(output, archive)
    return {
        "output": str(output),
        "archive": str(archive),
        "package_file_count": len(integrity["immutable_files"]) + 1,
        "zip_sha256": sha256_file(archive),
        "formal_sample": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            build(args.source, args.output, args.archive),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
