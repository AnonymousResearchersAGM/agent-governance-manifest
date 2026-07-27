"""Small delivery-local checks; the full harness suite lives in the repository."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from common import no_forbidden_prompt_leak, verify_baseline_manifest


def test_formal_sample_is_false():
    config = json.loads((ROOT / "p92_session.json").read_text(encoding="utf-8"))
    assert config["formal_sample"] is False


def test_prompts_do_not_leak_expected_answer():
    config = json.loads((ROOT / "p92_session.json").read_text(encoding="utf-8"))
    assert no_forbidden_prompt_leak(config)


def test_baselines_are_frozen():
    verify_baseline_manifest(ROOT)


def test_delivery_has_no_agm_source_copy():
    assert not (ROOT / "src" / "agm").exists()
