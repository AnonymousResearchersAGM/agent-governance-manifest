"""Reset P92 runtime from immutable baselines without deleting records."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from common import (
    TASK_IDS,
    package_root,
    reset_task_runtime,
    verify_baseline_manifest,
)
from stop_p92 import stop_marked_processes


def reset(
    *,
    task_id: str,
    root: Path,
    repo_root: Path | None,
    clear_records: bool = False,
    confirm_clear: str = "",
) -> dict[str, object]:
    root = root.resolve()
    stop_marked_processes(root)
    verify_baseline_manifest(root)
    session_path = root / "runtime" / "session.json"
    if repo_root is None and session_path.exists():
        session = json.loads(session_path.read_text(encoding="utf-8"))
        repo_root = Path(session["repo_root"])
    if repo_root is None:
        raise RuntimeError("RepoRoot is required when no P92 session exists.")
    if clear_records:
        if confirm_clear != "CLEAR RECORDS":
            raise RuntimeError(
                "Clearing P92 records requires exact confirmation: CLEAR RECORDS"
            )
        records = root / "records"
        if records.exists():
            shutil.rmtree(records)
        records.mkdir()
    destination = reset_task_runtime(
        task_id,
        repo_root=repo_root.resolve(),
        root=root,
    )
    verify_baseline_manifest(root)
    return {
        "task_id": task_id,
        "runtime": str(destination),
        "records_preserved": not clear_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, default=package_root())
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--task", choices=TASK_IDS, required=True)
    parser.add_argument("--clear-records", action="store_true")
    parser.add_argument("--confirm-clear", default="")
    args = parser.parse_args()
    print(
        json.dumps(
            reset(
                task_id=args.task,
                root=args.package_root,
                repo_root=args.repo_root,
                clear_records=args.clear_records,
                confirm_clear=args.confirm_clear,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
