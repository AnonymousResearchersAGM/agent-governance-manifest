from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from package_tracked_repository import (  # noqa: E402
    package_repository,
    tracked_files,
    verify_archive,
)
from verify_tracked_repository_package import (  # noqa: E402
    verify_fresh_extract,
)


INTERACTIVE_ROOT = (
    ROOT / "examples" / "review_briefing" / "interactive_outputs"
)
INTERACTIVE_EXPECTED = (
    ROOT
    / "examples"
    / "review_briefing"
    / "interactive_expected_sha256.json"
)


def test_interactive_artifacts_and_manifests_are_lf_bytes():
    paths = [
        path
        for path in INTERACTIVE_ROOT.rglob("*")
        if path.is_file()
    ]
    paths.append(INTERACTIVE_EXPECTED)
    assert len(paths) == 20
    for path in paths:
        raw = path.read_bytes()
        assert b"\r\n" not in raw, path


def test_gitattributes_freezes_interactive_artifacts_as_lf():
    samples = (
        "examples/review_briefing/interactive_outputs/manifest.json",
        (
            "examples/review_briefing/interactive_outputs/"
            "03_scoped_repair/review_interactive.html"
        ),
        "examples/review_briefing/interactive_expected_sha256.json",
    )
    completed = subprocess.run(
        ["git", "check-attr", "text", "eol", "--", *samples],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    for sample in samples:
        assert f"{sample}: text: set" in completed.stdout
        assert f"{sample}: eol: lf" in completed.stdout


def test_tracked_zip_uses_git_blobs_and_matches_tracked_file_list(
    tmp_path,
):
    output = tmp_path / "tracked.zip"
    result = package_repository(output=output)
    expected = tracked_files(result["commit"])
    actual = verify_archive(output, ref=result["commit"])

    assert set(actual) == set(expected)
    assert len(actual) == len(expected)
    assert result["tracked_file_count"] == len(expected)
    assert not any(
        forbidden in Path(name).parts
        for name in actual
        for forbidden in (
            ".git",
            ".agm-work",
            ".venv",
            "__pycache__",
            ".pytest_cache",
        )
    )
    with zipfile.ZipFile(output) as archive:
        archived = archive.read(
            "examples/review_briefing/interactive_outputs/"
            "03_scoped_repair/review_interactive.html"
        )
    assert b"\r\n" not in archived


def test_fresh_tracked_zip_passes_hashes_before_regeneration(
    tmp_path,
):
    output = tmp_path / "tracked.zip"
    packaged = package_repository(output=output)
    result = verify_fresh_extract(
        output,
        ref=str(packaged["commit"]),
    )
    assert result["hash_checks_before_generation"] == 4
    assert result["hash_checks_after_generation"] == 4
    assert result["fresh_demo_links_valid"] is True
    assert result["participant_term_scan_valid"] is True
    assert result["regeneration_content_stable"] is True
