from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agm.vnext.cli import main  # noqa: E402
from agm.vnext.models import VNextError  # noqa: E402
from agm.vnext.reporting import (  # noqa: E402
    AUTHORITY_NOTICE,
    readiness,
    render_html,
    render_markdown,
)
from agm.vnext.repair import create_finding  # noqa: E402
from agm.vnext.service import GovernanceService  # noqa: E402
from agm.vnext.ui import (  # noqa: E402
    execute_panel_action,
    new_action_token,
    validate_action_token,
    validate_loopback_host,
)


def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    shutil.copytree(ROOT / ".agm", root / ".agm")
    (root / "docs").mkdir()
    (root / "docs" / "guide.md").write_text("guide", encoding="utf-8")
    return root


def case_and_service(tmp_path: Path):
    root = project(tmp_path)
    service = GovernanceService(root)
    case, _ = service.open_case(
        ["docs/guide.md"],
        requested_mode="declared_agent_mediated",
        actor="agent-1",
        actor_role="contributor_agent",
        case_id="panel-case",
        base_commit="base",
        autonomy_profile="human_direct",
    )
    assert case is not None
    return root, service, case


def test_html_escapes_user_controlled_finding_content(tmp_path):
    _, service, case = case_and_service(tmp_path)
    create_finding(
        case,
        code="unsafe",
        severity="high",
        message="<script>alert('x')</script>",
        blocking=True,
    )

    rendered = render_html(
        case,
        service.storage.read_transitions(case.id),
        audience="maintainer",
    )

    assert "<script>alert" not in rendered
    assert "&lt;script&gt;" in rendered


def test_markdown_escapes_table_pipe_content(tmp_path):
    _, service, case = case_and_service(tmp_path)
    case.obligations[0].description = "left | right"

    rendered = render_markdown(
        case,
        service.storage.read_transitions(case.id),
        audience="maintainer",
    )

    assert "left \\| right" in rendered
    assert AUTHORITY_NOTICE in rendered


def test_contributor_html_prominently_shows_fingerprint_and_actions(tmp_path):
    _, service, case = case_and_service(tmp_path)
    rendered = render_html(
        case,
        service.storage.read_transitions(case.id),
        audience="contributor",
        action_token="secret-token",
    )

    assert case.contribution_fingerprint in rendered
    assert "Confirm reviewed scope" in rendered
    assert 'value="secret-token"' in rendered
    assert "cannot submit" in rendered.lower()


def test_non_loopback_ui_bind_is_rejected():
    with pytest.raises(VNextError, match="loopback"):
        validate_loopback_host("0.0.0.0")


def test_loopback_ui_bind_is_allowed():
    assert validate_loopback_host("127.0.0.1") == "127.0.0.1"
    assert validate_loopback_host("::1") == "::1"
    assert validate_loopback_host("localhost") == "localhost"


def test_action_token_is_unpredictable_and_checked():
    first = new_action_token()
    second = new_action_token()

    assert first != second
    validate_action_token(first, first)
    with pytest.raises(VNextError, match="action token"):
        validate_action_token(first, second)


def test_panel_action_rejects_missing_token_before_mutation(tmp_path):
    _, service, case = case_and_service(tmp_path)

    with pytest.raises(VNextError, match="action token"):
        execute_panel_action(
            service,
            case_id=case.id,
            audience="contributor",
            form={
                "action": ["confirm_attestation"],
                "actor": ["human-1"],
                "scope": ["docs/guide.md"],
                "statement": ["Reviewed."],
            },
            action_token="expected",
        )

    assert service.storage.load_case(case.id).attestations == []


def test_readiness_never_calls_ready_case_accepted(tmp_path):
    _, _, case = case_and_service(tmp_path)
    case.state = "ready_for_human_decision"
    for obligation in case.obligations:
        obligation.status = "verified"

    assert readiness(case) == "eligible_for_human_decision"
    assert readiness(case) != "accepted"


def test_cli_project_validate_is_discoverable(tmp_path, capsys):
    root = project(tmp_path)

    result = main(["--root", str(root), "project", "validate"])
    output = capsys.readouterr().out

    assert result == 0
    assert '"valid": true' in output
    assert '"status": "development"' in output


def test_cli_project_simulate_shows_no_package_semantics(tmp_path, capsys):
    root = project(tmp_path)

    result = main(
        [
            "--root",
            str(root),
            "project",
            "simulate",
            "--changed-file",
            "docs/guide.md",
            "--mode",
            "ordinary",
        ]
    )
    output = capsys.readouterr().out

    assert result == 0
    assert "no_agm_package_submitted" in output
    assert "documentation-low" in output


def test_cli_ordinary_open_case_does_not_create_runtime_case(tmp_path, capsys):
    root = project(tmp_path)

    result = main(
        [
            "--root",
            str(root),
            "contributor",
            "open-case",
            "--changed-file",
            "docs/guide.md",
            "--mode",
            "ordinary",
            "--actor",
            "human-1",
            "--role",
            "contributor",
            "--base-commit",
            "base",
        ]
    )
    output = capsys.readouterr().out

    assert result == 0
    assert '"case_created": false' in output
    assert not (root / ".agm-work").exists()


def test_cli_rejects_unauthorized_human_attestation_role(tmp_path, capsys):
    root, service, case = case_and_service(tmp_path)

    result = main(
        [
            "--root",
            str(root),
            "contributor",
            "attest",
            "--case",
            case.id,
            "--actor",
            "agent-1",
            "--role",
            "contributor_agent",
            "--scope",
            "docs/guide.md",
            "--statement",
            "Agent attempted attestation.",
        ]
    )
    output = capsys.readouterr().out

    assert result == 2
    assert "agents cannot attest" in output
    assert service.storage.load_case(case.id).attestations == []
