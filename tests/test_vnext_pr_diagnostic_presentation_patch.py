"""Participant-facing action ownership and structured artifact presentation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

from agm.vnext.models import fingerprint
from agm.vnext.pr_diagnostic import project_structured_artifact
from agm.vnext.pr_diagnostic.presenters import (
    render_pr_diagnostic_html,
    render_pr_diagnostic_markdown,
)
from agm.vnext.pr_diagnostic.server import _artifact_page
from agm.vnext.runtime import DemoExecutionContext, use_execution_context
from agm.vnext.service import GovernanceService
from generate_pr_diagnostic_demos import FIXED_TIME, SCENARIOS, build_scenario
from generate_reviewer_guidance_demos import make_project


def _scenario(tmp_path: Path, slug: str):
    args = next(item for item in SCENARIOS if item[0] == slug)
    with use_execution_context(DemoExecutionContext("patch-" + slug, FIXED_TIME, "key")):
        root = make_project(tmp_path, slug)
        service = GovernanceService(root)
        case_id, context = build_scenario(service, *args)
        return service, case_id, context


def _metadata(
    content: str,
    artifact_type: str,
    *,
    media_type: str = "application/json",
) -> dict[str, str]:
    return {
        "artifact_id": "artifact-1",
        "artifact_type": artifact_type,
        "title": "测试材料",
        "content_digest": fingerprint(content),
        "contribution_fingerprint": "contribution-1",
        "media_type": media_type,
    }


@pytest.mark.parametrize("slug", [item[0] for item in SCENARIOS])
def test_participant_pages_separate_action_owner_action_and_final_authority(
    tmp_path: Path, slug: str
):
    service, case_id, context = _scenario(tmp_path, slug)
    view = service.pr_diagnosis(case_id, contribution=context)
    html = render_pr_diagnostic_html(view)
    markdown = render_pr_diagnostic_markdown(view)
    assert "当前责任方" not in html + markdown
    assert "当前待办归属" in html
    assert "下一步需要完成" in html
    assert "最终决定权" in html
    assert "最终接受、拒绝或合并决定仍由人类维护者作出" in html
    assert view.recommended_route["owner"] == view.recommended_route["action_owner"]
    assert view.recommended_route["final_authority"] == "维护者"


def test_d9_handoff_projection_is_observable_without_canonical_mutation(tmp_path: Path):
    service, case_id, context = _scenario(tmp_path, "D9_contributor_waiting")
    before = service.storage.load_case(case_id).to_dict()
    view = service.pr_diagnosis(case_id, contribution=context)
    after = service.storage.load_case(case_id).to_dict()
    projection = view.verification_submission
    assert view.diagnostic_status == "材料已准备，尚未送交维护者核验"
    assert projection is not None
    assert projection.pr_status == "已创建，可供查看"
    assert projection.material_completeness == "已通过自动检查"
    assert projection.contributor_confirmation == "本类修改不要求额外的贡献者人工确认。"
    assert projection.submission_status == "尚未提交"
    assert projection.missing_handoff_record == "尚未生成本轮维护者核验提交记录"
    assert projection.action_owner == "贡献者"
    assert projection.final_authority == "维护者"
    assert projection.persisted is False
    assert before == after
    assert not list((service.root / ".agm-work" / "evidence_store" / "receipts").glob("*.json"))


def test_d9_page_does_not_imply_that_pr_is_missing(tmp_path: Path):
    service, case_id, context = _scenario(tmp_path, "D9_contributor_waiting")
    html = render_pr_diagnostic_html(service.pr_diagnosis(case_id, contribution=context))
    assert "PR 已创建，材料也已准备" in html
    assert "PR 状态</dt><dd>已创建，可供查看" in html
    assert "等待贡献者提交维护者检查" not in html


@pytest.mark.parametrize(
    "artifact_type,required_heading",
    [
        ("change_summary", "修改内容"),
        ("changed_files", "文件路径"),
        ("rationale", "修改理由"),
        ("known_limitations", "已知限制"),
        ("impact_statement", "影响说明"),
        ("test_result", "测试命令"),
        ("agent_activity", "活动覆盖范围"),
        ("contribution_declaration", "贡献者声明"),
        ("human_confirmation", "贡献者确认"),
        ("repair_record", "原问题"),
        ("final_receipt", "AGM 建议"),
    ],
)
def test_supported_artifact_types_have_deterministic_specialized_projections(
    artifact_type: str, required_heading: str
):
    value = {
        "artifact_type": artifact_type,
        "summary": "修改说明",
        "files": ["src/a.py"],
        "reason": "修复问题",
        "limitations": [],
        "security_impact": "无额外影响",
        "command": "python -m pytest",
        "activity_scope": ["src/a.py"],
        "statement": "已检查",
        "original_issue": "原问题",
        "agm_final_recommendation": "建议接受",
        "contribution_fingerprint": "c" * 64,
        "head_commit_sha": "a" * 40,
    }
    content = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    first = project_structured_artifact(
        metadata=_metadata(content, artifact_type),
        content=content,
        package_digest="package-1",
    )
    second = project_structured_artifact(
        metadata=_metadata(content, artifact_type),
        content=content,
        package_digest="package-1",
    )
    assert first == second
    assert first is not None and first.readable_available
    assert required_heading in first.markdown
    assert "Derived human-readable projection" in first.markdown
    assert first.source_digest == fingerprint(content)
    assert fingerprint(content) == _metadata(content, artifact_type)["content_digest"]


def test_one_line_json_and_yaml_are_pretty_printed_without_changing_raw():
    json_raw = '{"中文":"保留","nested":{"items":[1,2]}}'
    yaml_raw = "中文: 保留\nnested: {items: [1, 2]}\n"
    json_projection = project_structured_artifact(
        metadata=_metadata(json_raw, "unknown", media_type="application/json"),
        content=json_raw,
        package_digest="package",
    )
    yaml_projection = project_structured_artifact(
        metadata=_metadata(yaml_raw, "unknown", media_type="application/yaml"),
        content=yaml_raw,
        package_digest="package",
    )
    assert json_projection is not None and json_projection.raw_text == json_raw
    assert '\n  "nested": {' in json_projection.formatted_text
    assert "\\u4e2d" not in json_projection.formatted_text
    assert yaml_projection is not None and yaml_projection.raw_text == yaml_raw
    assert "items:\n    - 1\n    - 2" in yaml_projection.formatted_text


def test_unknown_structured_type_uses_hierarchical_safe_fallback():
    raw = '{"outer":{"items":["one","two"]}}'
    projection = project_structured_artifact(
        metadata=_metadata(raw, "future_type"),
        content=raw,
        package_digest="package",
    )
    assert projection is not None and projection.readable_available
    assert "## 材料内容" in projection.markdown
    assert "**outer:**" in projection.markdown
    assert "<table" not in projection.rendered_html


def test_malformed_structured_content_has_no_fake_readable_projection():
    raw = '{"broken":'
    projection = project_structured_artifact(
        metadata=_metadata(raw, "test_result"),
        content=raw,
        package_digest="package",
    )
    assert projection is not None
    assert not projection.readable_available
    assert projection.markdown is None
    assert projection.formatted_text == raw
    page = _artifact_page(_metadata(raw, "test_result"), raw, "package")
    assert "该材料无法生成结构化可读视图" in page
    assert html_escape(raw) in page


@pytest.mark.parametrize(
    "raw",
    [
        "value: !!python/object/apply:os.system ['echo unsafe']\n",
        "value: &loop [*loop]\n",
    ],
)
def test_yaml_constructors_and_recursive_aliases_are_not_projected(raw: str):
    projection = project_structured_artifact(
        metadata=_metadata(raw, "future_type", media_type="application/yaml"),
        content=raw,
        package_digest="package",
    )
    assert projection is not None
    assert not projection.readable_available
    assert projection.formatted_text == raw


def html_escape(value: str) -> str:
    import html

    return html.escape(value)


def test_script_html_javascript_and_external_resource_payloads_are_inert():
    raw = json.dumps(
        {
            "statement": "</script><script>alert(1)</script>",
            "url": "javascript:alert(2)",
            "image": "https://attacker.invalid/image.png",
            "html": "<img src=x onerror=alert(3)>",
        }
    )
    projection = project_structured_artifact(
        metadata=_metadata(raw, "contribution_declaration"),
        content=raw,
        package_digest="package",
    )
    assert projection is not None and projection.readable_available
    assert "<script>alert" not in projection.rendered_html
    assert "<img " not in projection.rendered_html
    assert "&lt;/script&gt;" in projection.rendered_html
    page = _artifact_page(_metadata(raw, "contribution_declaration"), raw, "package")
    assert '<img src="https://attacker.invalid' not in page
    assert 'href="javascript:' not in page


def test_artifact_page_defaults_to_readable_and_preserves_raw_pane_contract():
    raw = '{"path":"src/' + "long-" * 50 + 'file.py","digest":"' + "a" * 64 + '"}'
    page = _artifact_page(_metadata(raw, "changed_files"), raw, "package")
    assert 'role="tab" aria-selected="true"' in page
    assert 'id="panel-raw"' in page and " hidden" in page
    assert "white-space:pre;" in page
    assert "overflow-wrap:normal" in page
    assert 'id="wrap-raw"' in page
    assert "复制原始内容" in page and "复制格式化内容" in page
    assert "data-raw=" in page and "data-formatted=" in page
    assert "摘要基于原始 canonical bytes" in page


def test_projection_is_pure_and_does_not_register_evidence_or_satisfy_obligations(
    tmp_path: Path,
):
    service, case_id, _ = _scenario(tmp_path, "D9_contributor_waiting")
    before = service.storage.load_case(case_id).to_dict()
    artifact = next(
        item
        for item in service.pr_diagnosis(case_id).inspection_objects
        if item.technical_metadata.get("artifact_type") == "agent_activity"
    )
    projection = project_structured_artifact(
        metadata={
            **artifact.technical_metadata,
            "artifact_id": artifact.object_id,
            "title": artifact.title,
            "content_digest": artifact.content_digest,
            "contribution_fingerprint": artifact.contribution_fingerprint,
        },
        content=artifact.inline_content or "",
        package_digest=artifact.evidence_package_digest or "",
    )
    assert projection is not None and projection.readable_available
    assert service.storage.load_case(case_id).to_dict() == before
