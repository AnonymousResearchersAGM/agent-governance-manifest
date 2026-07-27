"""Fail-closed verification for the frozen artifact and P92 package."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

from common import (
    ARTIFACT_COMMIT,
    POLICY_FINGERPRINT,
    load_config,
    no_forbidden_prompt_leak,
    package_root,
    sha256_file,
    stable_file_map,
    verify_baseline_manifest,
)


HASH_CHECKS = (
    "scripts/check_reviewer_guidance_demo_hashes.py",
    "scripts/check_review_briefing_demo_hashes.py",
    "scripts/check_review_interactive_demo_hashes.py",
)


def _run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(
            f"Verification command failed ({result.returncode}): "
            + " ".join(command)
            + "\n"
            + result.stdout
            + result.stderr
        )
    return result.stdout.strip()


def _git(repo: Path, *args: str) -> str:
    return _run(["git", *args], cwd=repo)


def verify_package_integrity(root: Path) -> dict[str, Any]:
    path = root / "package_integrity.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected = payload.get("immutable_files", {})
    excluded = {"package_integrity.json"}
    observed = stable_file_map(root, excluded=excluded)
    observed = {
        name: digest
        for name, digest in observed.items()
        if not name.startswith("runtime/")
        and not name.startswith("records/")
    }
    if expected != observed:
        missing = sorted(set(expected) - set(observed))
        extra = sorted(set(observed) - set(expected))
        changed = sorted(
            name
            for name in set(expected) & set(observed)
            if expected[name] != observed[name]
        )
        raise RuntimeError(
            "P92 package integrity mismatch: "
            f"missing={missing}, extra={extra}, changed={changed}"
        )
    return payload


def _ports_available() -> list[int]:
    sockets = []
    ports = []
    try:
        for _ in range(2):
            handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            handle.bind(("127.0.0.1", 0))
            sockets.append(handle)
            ports.append(int(handle.getsockname()[1]))
    finally:
        for handle in sockets:
            handle.close()
    if len(set(ports)) != 2:
        raise RuntimeError("Unable to reserve two distinct loopback ports.")
    return ports


def verify(repo_root: Path, root: Path | None = None) -> dict[str, Any]:
    root = (root or package_root()).resolve()
    repo_root = repo_root.resolve()
    if not repo_root.is_dir():
        raise RuntimeError(f"RepoRoot does not exist: {repo_root}")
    if not (repo_root / ".git").exists():
        raise RuntimeError("RepoRoot is not a Git checkout.")
    if repo_root == root or repo_root in root.parents or root in repo_root.parents:
        raise RuntimeError(
            "P92 package must be outside the frozen repository so runtime "
            "cannot write into the prototype checkout."
        )
    head = _git(repo_root, "rev-parse", "HEAD")
    if head != ARTIFACT_COMMIT:
        raise RuntimeError(
            f"Frozen artifact commit mismatch: expected {ARTIFACT_COMMIT}, got {head}"
        )
    status = _git(
        repo_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status:
        raise RuntimeError("Frozen artifact repository is dirty:\n" + status)

    source = str(repo_root / "src")
    if source not in sys.path:
        sys.path.insert(0, source)
    import agm.vnext  # noqa: F401
    from agm.vnext.config import load_vnext_config

    config = load_vnext_config(repo_root)
    if config.policy_fingerprint != POLICY_FINGERPRINT:
        raise RuntimeError(
            "Canonical policy fingerprint mismatch: "
            f"{config.policy_fingerprint}"
        )
    process_env = dict(os.environ)
    process_env["PYTHONPATH"] = (
        source
        + os.pathsep
        + process_env.get("PYTHONPATH", "")
    )
    validation = _run(
        [
            sys.executable,
            "-m",
            "agm.vnext.cli",
            "--root",
            str(repo_root),
            "project",
            "validate",
        ],
        cwd=repo_root,
        env=process_env,
    )
    parsed_validation = json.loads(validation)
    if not parsed_validation.get("valid"):
        raise RuntimeError("AGM project validate did not return valid=true.")
    for script in HASH_CHECKS:
        _run([sys.executable, script], cwd=repo_root, env=process_env)
    baseline = verify_baseline_manifest(root)
    immutable = verify_package_integrity(root)
    package_config = load_config(root)
    if package_config.get("formal_sample") is not False:
        raise RuntimeError("P92 must declare formal_sample=false.")
    if not no_forbidden_prompt_leak(package_config):
        raise RuntimeError("A P92 task prompt leaks an expected answer.")
    runtime = (root / "runtime").resolve()
    if repo_root == runtime or repo_root in runtime.parents:
        raise RuntimeError("P92 runtime resolves inside the frozen repository.")
    ports = _ports_available()
    status_after = _git(
        repo_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status_after:
        raise RuntimeError("Verification changed the frozen repository.")
    return {
        "verified": True,
        "repo_root": str(repo_root),
        "artifact_commit": head,
        "repo_clean": True,
        "policy_fingerprint": config.policy_fingerprint,
        "python_import": "agm.vnext",
        "project_validate": True,
        "hash_checks": list(HASH_CHECKS),
        "baseline_file_count": len(baseline["files"]),
        "package_file_count": len(immutable["immutable_files"]) + 1,
        "runtime_isolated": True,
        "loopback_ports_checked": ports,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--package-root", type=Path, default=package_root())
    args = parser.parse_args()
    print(
        json.dumps(
            verify(args.repo_root, args.package_root),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
