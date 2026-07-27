from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_reviewer_guidance_demo_hashes import (  # noqa: E402
    DEFAULT_EXPECTED,
    check_hashes,
    load_expected,
    output_hashes,
)
from generate_reviewer_guidance_demos import (  # noqa: E402
    copy_demo_text_tree,
    demo_relative_path,
    generate,
    normalize_demo_text,
    write_demo_text,
)
from agm.vnext.config import normalize_path  # noqa: E402
from agm.vnext.guidance import (  # noqa: E402
    present_action,
    present_obligation,
    present_record_type,
    present_role,
    present_state,
    present_workflow_node,
)


GUIDE_FIXTURE_SHA256 = (
    "2519bd19006edce575d942a991bf020737650250157d421ae41a6b6c6d6b09da"
)
SCENARIO_2_CONTRIBUTION_FINGERPRINT = (
    "8e2f8be0859837b0e34208e1e7f77f5b6e877d3d958d5337bd60c16409348f93"
)
SCENARIO_3_CASE_FINGERPRINT = (
    "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0"
)
OUTPUT_MANIFEST_SHA256 = (
    "9f4f102640f6da1e3460a4f143b1a262d4a4908e28ca4dcfe6730f9bd646a5d5"
)


@pytest.fixture(scope="module")
def canonical_outputs(tmp_path_factory):
    output = tmp_path_factory.mktemp("cross-platform-canonical") / "outputs"
    generate(output)
    return output


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("first\nsecond\n", b"first\nsecond\n"),
        ("first\r\nsecond\r\n", b"first\nsecond\n"),
        ("first\rsecond\r", b"first\nsecond\n"),
        ("trailing\n\n", b"trailing\n"),
        ("no trailing newline", b"no trailing newline\n"),
        ("", b"\n"),
        ("中文内容\r\n第二行", "中文内容\n第二行\n".encode("utf-8")),
        ("def run():\r\n    return True\r\n", b"def run():\n    return True\n"),
        ("# 标题\r\n\r\n正文", "# 标题\n\n正文\n".encode("utf-8")),
        ("key: value\r\nitems:\r\n  - one", b"key: value\nitems:\n  - one\n"),
        ('{"key": "值"}\r\n', '{"key": "值"}\n'.encode("utf-8")),
    ],
    ids=[
        "lf",
        "crlf",
        "cr-only",
        "single-final-newline",
        "add-final-newline",
        "empty",
        "unicode-chinese",
        "python",
        "markdown",
        "yaml",
        "json",
    ],
)
def test_demo_fixture_text_has_cross_platform_canonical_bytes(
    content,
    expected,
):
    assert normalize_demo_text(content) == expected


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("value\n", b"value"),
        ("value\r\n\r\n", b"value"),
        ("", b""),
    ],
)
def test_demo_fixture_writer_can_explicitly_omit_final_newline(
    content,
    expected,
):
    assert normalize_demo_text(content, final_newline=False) == expected


def test_demo_fixture_writer_writes_utf8_lf_bytes(tmp_path):
    target = tmp_path / "nested" / "fixture.md"
    write_demo_text(target, "第一行\r\n第二行")
    assert target.read_bytes() == "第一行\n第二行\n".encode("utf-8")


def test_demo_fixture_tree_normalizes_text_and_preserves_binary(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "fixture.md").write_bytes(b"line one\r\nline two\r\n")
    binary = b"\x00\xff\r\n\x10"
    (source / "fixture.bin").write_bytes(binary)
    destination = tmp_path / "destination"

    copy_demo_text_tree(source, destination)

    assert (destination / "fixture.md").read_bytes() == (
        b"line one\nline two\n"
    )
    assert (destination / "fixture.bin").read_bytes() == binary


def test_simple_fixture_sha256_matches_frozen_cross_platform_value():
    digest = hashlib.sha256(normalize_demo_text("reviewer guidance")).hexdigest()
    assert digest == GUIDE_FIXTURE_SHA256


@pytest.mark.parametrize(
    "value",
    [
        r".\demo_app\auth.py",
        "demo_app/auth.py",
    ],
    ids=["windows-style", "posix-style"],
)
def test_repository_relative_paths_normalize_to_posix(value):
    assert normalize_path(value) == "demo_app/auth.py"


def test_serialized_demo_relative_path_uses_forward_slashes(tmp_path):
    output = tmp_path / "outputs"
    target = output / "scenario" / "guidance.json"
    assert demo_relative_path(target, output) == "scenario/guidance.json"


def test_generated_paths_are_posix_sorted_and_do_not_leak_temp_root(
    canonical_outputs,
):
    manifest = json.loads(
        (canonical_outputs / "manifest.json").read_text(encoding="utf-8")
    )
    serialized_paths = [
        scenario[key]
        for scenario in manifest["scenarios"]
        for key in ("json", "markdown", "html")
    ]
    assert all("\\" not in path for path in serialized_paths)
    assert [item["scenario"] for item in manifest["scenarios"]] == sorted(
        item["scenario"] for item in manifest["scenarios"]
    )
    combined = b"\n".join(
        path.read_bytes()
        for path in sorted(canonical_outputs.rglob("*"))
        if path.is_file()
    )
    assert str(canonical_outputs).encode("utf-8") not in combined
    assert b"/tmp/" not in combined
    assert b"C:\\Users\\" not in combined


def test_generated_scenario_fingerprints_match_frozen_canonical_values(
    canonical_outputs,
):
    scenario_2 = json.loads(
        (
            canonical_outputs
            / "02_material_partial_invalidation"
            / "guidance.json"
        ).read_text(encoding="utf-8")
    )
    scenario_3 = json.loads(
        (
            canonical_outputs / "03_scoped_repair" / "guidance.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        scenario_2["guidance_view"]["generated_from_case_fingerprint"]
        == SCENARIO_2_CONTRIBUTION_FINGERPRINT
    )
    assert (
        scenario_3["guidance_view"]["generated_from_case_fingerprint"]
        == SCENARIO_3_CASE_FINGERPRINT
    )


def test_generated_manifest_matches_frozen_cross_platform_sha256(
    canonical_outputs,
):
    digest = hashlib.sha256(
        (canonical_outputs / "manifest.json").read_bytes()
    ).hexdigest()
    assert digest == OUTPUT_MANIFEST_SHA256


def test_all_generated_outputs_match_shared_expected_sha256_manifest(
    canonical_outputs,
):
    expected = load_expected(DEFAULT_EXPECTED)
    assert len(expected) == 25
    assert output_hashes(canonical_outputs) == expected
    assert check_hashes(canonical_outputs, DEFAULT_EXPECTED) == []


def test_hash_check_reports_missing_file(canonical_outputs, tmp_path):
    copied = tmp_path / "missing"
    shutil.copytree(canonical_outputs, copied)
    (copied / "01_multi_risk_missing" / "guidance.json").unlink()
    problems = check_hashes(copied, DEFAULT_EXPECTED)
    assert "missing: 01_multi_risk_missing/guidance.json" in problems


def test_hash_check_reports_unexpected_file(canonical_outputs, tmp_path):
    copied = tmp_path / "extra"
    shutil.copytree(canonical_outputs, copied)
    (copied / "unexpected.txt").write_bytes(b"not a research output\n")
    problems = check_hashes(copied, DEFAULT_EXPECTED)
    assert "unexpected: unexpected.txt" in problems


def test_hash_check_reports_specific_sha256_mismatch(
    canonical_outputs,
    tmp_path,
):
    copied = tmp_path / "mismatch"
    shutil.copytree(canonical_outputs, copied)
    changed = copied / "manifest.json"
    changed.write_bytes(changed.read_bytes() + b"\n")
    problems = check_hashes(copied, DEFAULT_EXPECTED)
    assert any(
        problem.startswith("sha256 mismatch: manifest.json")
        for problem in problems
    )


@pytest.mark.parametrize(
    ("presenter", "canonical", "expected"),
    [
        (present_action, "verify_evidence", "检查提交材料"),
        (present_role, "maintainer_verifier", "维护者侧检查人员"),
        (present_obligation, "O-SUMMARY", "修改说明"),
        (present_workflow_node, "maintainer_check", "维护者检查"),
        (present_record_type, "maintainer_verification", "维护者检查记录"),
        (present_state, "awaiting_maintainer_verification", "等待维护者检查"),
    ],
)
def test_known_canonical_terms_have_one_chinese_presentation(
    presenter,
    canonical,
    expected,
):
    presented = presenter(canonical)
    assert presented.display_plain == expected
    assert presented.canonical == canonical


@pytest.mark.parametrize(
    ("presenter", "expected"),
    [
        (present_action, "某项维护者操作"),
        (present_role, "某个有权角色"),
        (present_obligation, "某项项目要求"),
        (present_workflow_node, "某个审核步骤"),
        (present_record_type, "某类治理记录"),
        (present_state, "当前审核阶段"),
    ],
)
def test_unknown_canonical_terms_use_safe_display_fallback(
    presenter,
    expected,
):
    presented = presenter("future_internal_term")
    assert presented.display_plain == expected
    assert presented.canonical == "future_internal_term"
