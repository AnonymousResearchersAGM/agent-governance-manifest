"""Export P92 records without runtime state or live tokens."""

from __future__ import annotations

import argparse
import json
import platform
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from common import (
    ARTIFACT_COMMIT,
    POLICY_FINGERPRINT,
    package_root,
    sha256_file,
    validate_participant_id,
)


def export_results(
    *,
    participant_id: str,
    root: Path,
    output_dir: Path | None = None,
) -> dict[str, object]:
    participant_id = validate_participant_id(participant_id)
    root = root.resolve()
    records = root / "records"
    if not (records / "P92_session_log.jsonl").exists():
        raise RuntimeError("No P92 task records exist for export.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = (output_dir or root).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"P92_results_{participant_id}_{stamp}.zip"
    if archive.exists():
        raise RuntimeError(f"Refusing to overwrite existing export: {archive}")
    metadata = {
        "schema_version": "agm.p92_results_export/v1",
        "formal_sample": False,
        "participant_id": participant_id,
        "artifact_commit": ARTIFACT_COMMIT,
        "policy_fingerprint": POLICY_FINGERPRINT,
        "software_versions": {
            "python": sys.version,
            "platform": platform.platform(),
        },
    }
    members: list[str] = []
    with zipfile.ZipFile(
        archive,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as handle:
        for path in sorted(
            (item for item in records.rglob("*") if item.is_file()),
            key=lambda item: item.relative_to(root).as_posix(),
        ):
            name = path.relative_to(root).as_posix()
            handle.write(path, name)
            members.append(name)
        static = (
            "p92_session.json",
            "package_integrity.json",
            "baseline/baseline_sha256.json",
        )
        for name in static:
            handle.write(root / name, name)
            members.append(name)
        handle.writestr(
            "P92_export_metadata.json",
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        )
        members.append("P92_export_metadata.json")
    forbidden = (
        "runtime/",
        "preview_token",
        "csrf_token",
        "session_secret",
    )
    if any(
        name.startswith("runtime/") or any(term in name.lower() for term in forbidden[1:])
        for name in members
    ):
        archive.unlink(missing_ok=True)
        raise RuntimeError("P92 export contains a forbidden runtime or token member.")
    return {
        "archive": str(archive),
        "sha256": sha256_file(archive),
        "members": members,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, default=package_root())
    parser.add_argument("--participant-id", required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            export_results(
                participant_id=args.participant_id,
                root=args.package_root,
                output_dir=args.output_dir,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
