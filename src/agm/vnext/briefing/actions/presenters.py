"""HTML presenters for contextual review and separate final decisions."""

from __future__ import annotations

import html
import json

from .models import (
    DraftAssessment,
    FinalDecisionPreview,
    FinalDecisionResult,
    FinalDecisionView,
    ReviewActionView,
    ReviewDecisionDraft,
    ReviewSubmissionPreview,
    ReviewSubmissionResult,
)


BASE_CSS = """
:root{color-scheme:light;--ink:#18212f;--muted:#5d6878;--line:#dbe2ea;
--paper:#fff;--bg:#f3f6f8;--blue:#176b9c;--green:#18754d;
--amber:#8a5700;--red:#982525;--purple:#6654a4;--navy:#153452}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.55 system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;
overflow-wrap:anywhere}main{width:min(1040px,calc(100% - 32px));margin:20px auto 64px}
header{color:#fff;background:linear-gradient(135deg,#112f4b,#176a83);
padding:22px 28px;border-radius:18px 18px 8px 8px}header.final{
background:linear-gradient(135deg,#33245d,#6654a4)}h1{margin:0;
font-size:clamp(1.7rem,4vw,2.5rem)}header p{margin:.35rem 0 0}
section,details{background:var(--paper);margin:16px 0;padding:24px;
border:1px solid var(--line);border-radius:14px}h2{margin:0 0 14px;color:var(--navy)}
.status{border:2px solid var(--blue);box-shadow:0 12px 28px #17324b18}
.boundary{border-left:5px solid var(--amber);padding:10px 14px;
background:#fff8e8;font-weight:750}.draft-banner{position:sticky;top:0;z-index:3;
border:2px solid var(--amber);background:#fff5d9}.stale{border-color:var(--red);
background:#fff0f0}.anomaly{border-left:5px solid var(--blue);
background:#edf7fb}.judgment{border:2px solid #c8953b}.judgment h2{
display:flex;gap:10px;align-items:center}.number{display:inline-grid;place-items:center;
width:36px;height:36px;border-radius:50%;color:#fff;background:var(--amber);
font-size:1rem}.context{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.context article{padding:12px;border:1px solid var(--line);border-radius:10px;
min-width:0}.options{display:grid;gap:10px;margin-top:16px}.option{display:block;
padding:14px;border:1px solid #b7c4cf;border-radius:10px;background:#fbfcfd}
.option:has(input:checked){border:2px solid var(--blue);background:#eef7fc}
.option strong{display:block}.option p{margin:.3rem 0;color:var(--muted)}
textarea{display:block;width:100%;min-height:70px;margin-top:8px;padding:10px;
font:inherit;border:1px solid #aab6c1;border-radius:8px;resize:vertical}
.actions{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
button,.button{display:inline-block;border:0;border-radius:9px;padding:10px 16px;
font:inherit;font-weight:750;color:#fff;background:var(--blue);cursor:pointer;
text-decoration:none}.secondary{background:#66717e}.danger{background:var(--red)}
button:disabled{cursor:not-allowed;opacity:.55}.meta,.unavailable{color:var(--muted)}
.unavailable{padding:10px;background:#f0f2f4;border-radius:8px}.preview-list{
font-size:1.05rem}.success{border-color:var(--green);background:#effaf4}
summary{cursor:pointer;font-weight:800;color:var(--navy)}pre{max-height:65vh;
overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;padding:15px;
color:#e8eef4;background:#111b27;border-radius:10px}
@media(max-width:720px){main{width:min(100% - 16px,1040px);margin-top:8px}
header,section,details{padding:18px}.context{grid-template-columns:1fr}
.actions{align-items:stretch;flex-direction:column}.actions>*{width:100%}
pre{font-size:.78rem}}
"""


def _page(
    *,
    title: str,
    header_title: str,
    header_subtitle: str,
    body: str,
    final: bool = False,
) -> str:
    header_class = ' class="final"' if final else ""
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{BASE_CSS}</style></head>
<body><main><header{header_class}>
<h1>{html.escape(header_title)}</h1>
<p>{html.escape(header_subtitle)}</p></header>{body}</main></body></html>"""


def _draft_map(
    draft: ReviewDecisionDraft | None,
) -> dict[str, object]:
    if not draft:
        return {}
    return {item.judgment_id: item for item in draft.judgment_decisions}


def render_interactive_review_html(
    view: ReviewActionView,
    *,
    draft: ReviewDecisionDraft | None = None,
    assessment: DraftAssessment | None = None,
    draft_status: str | None = None,
    csrf_token: str | None = None,
    notice: str | None = None,
) -> str:
    """Render item-bound actions; operation refs stay in folded details."""

    draft_by_id = _draft_map(draft)
    next_step = view.current_next_step
    anomaly = ""
    if view.system_handled_anomalies:
        anomaly = (
            '<aside class="anomaly"><strong>'
            f"系统已自动拒绝 {len(view.system_handled_anomalies)} 次越权操作。"
            "</strong><p>该操作未生效，你无需额外处理。</p></aside>"
        )
    draft_class = (
        "draft-banner stale"
        if assessment and assessment.stale
        else "draft-banner"
    )
    if assessment and assessment.stale:
        draft_text = "贡献或规则已经变化，之前的选择已失效。"
    elif draft_status == "previewed":
        draft_text = "预览完成，尚未正式提交。"
    elif draft_status == "submitted":
        draft_text = ""
    elif draft and draft.judgment_decisions:
        draft_text = (
            f"你的选择尚未提交（已选择 {len(draft.judgment_decisions)} 项）。"
        )
    else:
        draft_text = "尚未选择处理结果。"
    actionable_items = any(
        any(option.authorized for option in item.options)
        for item in view.items
    )
    show_draft_banner = bool(
        draft_text
        and (
            actionable_items
            or (draft and draft.judgment_decisions)
        )
    )
    cards = []
    for index, item in enumerate(view.items, start=1):
        selected = draft_by_id.get(item.judgment_id)
        selected_option = (
            getattr(selected, "selected_option_id", "") if selected else ""
        )
        selected_reason = getattr(selected, "reason", "") if selected else ""
        options = []
        for option in item.options:
            checked = (
                " checked" if selected_option == option.option_id else ""
            )
            disabled = (
                " disabled"
                if not option.authorized or not view.live_actions_enabled
                else ""
            )
            unavailable = (
                f'<p class="unavailable">{html.escape(option.unavailable_reason or "")}</p>'
                if not option.authorized
                else ""
            )
            reason_box = (
                f'<textarea name="reason:{index}:{html.escape(option.option_id)}" maxlength="2000" '
                f'placeholder="请填写简短原因">{html.escape(str(selected_reason or ""))}</textarea>'
                if option.requires_reason
                else ""
            )
            options.append(
                '<label class="option">'
                f'<input type="radio" name="decision:{index}" '
                f'value="{html.escape(option.option_id)}"{checked}{disabled}>'
                f"<strong>{html.escape(option.display_label)}</strong>"
                f"<p>{html.escape(option.plain_consequence)}</p>"
                f"{reason_box}{unavailable}</label>"
            )
        cards.append(
            f'<section class="judgment" data-item="{index}">'
            f'<h2><span class="number">{index}</span>'
            f"{html.escape(item.display_title)}</h2>"
            f'<p class="meta">{html.escape(item.why_human_is_needed)}</p>'
            '<div class="context"><article><h3>贡献者声明</h3>'
            f"<p>{html.escape(item.contribution_claim)}</p></article>"
            '<article><h3>系统观察</h3>'
            f"<p>{html.escape(item.system_observation)}</p></article>"
            '<article><h3>证据摘要</h3>'
            f"<p>{html.escape(item.evidence_summary)}</p></article>"
            '<article><h3>重点检查事项</h3><ul>'
            + "".join(
                f"<li>{html.escape(focus)}</li>"
                for focus in item.review_focus
            )
            + '</ul></article></div><div class="options">'
            + "".join(options)
            + "</div></section>"
        )
    if view.items:
        if view.live_actions_enabled and view.can_save_draft:
            controls = (
                '<section><div class="actions">'
                '<button type="submit" formaction="/draft">保存未提交选择</button>'
                '<button type="submit" formaction="/preview">预览本次处理</button>'
                '<button type="submit" formaction="/draft/abandon" '
                'class="secondary">放弃本次未提交选择</button>'
                "</div></section>"
            )
        elif not view.live_actions_enabled:
            controls = (
                '<section class="unavailable">静态演示页面仅用于视觉复核，'
                "不能在此提交选择。</section>"
            )
        else:
            controls = (
                f'<section class="unavailable">{html.escape(view.unavailable_reason or "当前无权处理")}</section>'
            )
        csrf = (
            f'<input type="hidden" name="csrf_token" value="{html.escape(csrf_token)}">'
            if csrf_token
            else ""
        )
        form = f'<form method="post">{csrf}{"".join(cards)}{controls}</form>'
    else:
        empty = (
            "无需额外 AGM 治理判断，可以进入正常代码审查。"
            if next_step.get("status") == "normal_code_review"
            else next_step.get("plain_explanation", "当前无需你操作")
        )
        form = (
            '<section class="unavailable"><h2>当前无需你操作</h2>'
            f"<p>{html.escape(str(empty))}</p></section>"
        )
    final_href = (
        "/final" if view.live_actions_enabled else "final_decision.html"
    )
    final_link = (
        f'<section><a class="button" href="{final_href}">进入最终决定</a>'
        '<p class="meta">这是独立页面；不会自动执行任何最终决定。</p></section>'
        if view.final_decision_entry_available
        else ""
    )
    technical = html.escape(
        json.dumps(view.to_dict(), ensure_ascii=False, indent=2)
    )
    notice_html = (
        f'<section class="success"><strong>{html.escape(notice)}</strong></section>'
        if notice
        else ""
    )
    draft_banner = (
        f'<section class="{draft_class}"><strong>'
        f"{html.escape(draft_text)}</strong></section>"
        if show_draft_banner
        else ""
    )
    body = (
        '<section class="boundary"><strong>当前为 AGM 本地审查工作台。</strong> 这里的操作只记录 AGM 审查结果；不会修改代码，不会执行 git merge，也不会批准或合并 GitHub/GitLab 上的 PR。</section>'
        f'<section class="status"><h2>{html.escape(str(next_step.get("display_title", "当前状态")))}</h2>'
        f'<p>{html.escape(str(next_step.get("plain_explanation", "")))}</p>'
        f'<p><strong>当前责任方：</strong>{html.escape(str(next_step.get("responsible_party", "")))}</p>'
        '<p class="boundary">检查不等于最终接受；最终决定必须在独立页面完成。</p>'
        f"{anomaly}</section>{notice_html}"
        f"{draft_banner}{form}{final_link}"
        "<details><summary>治理过程与技术详情</summary>"
        f"<pre>{technical}</pre></details>"
    )
    return _page(
        title="AGM Interactive Maintainer Review",
        header_title="维护者逐项检查",
        header_subtitle="上下文绑定的人类判断；选择不会立即改变治理状态",
        body=body,
    )


def render_review_preview_html(
    preview: ReviewSubmissionPreview,
    *,
    csrf_token: str,
) -> str:
    token = html.escape(preview.preview_token or "")
    lines = "".join(
        f"<li>{html.escape(item)}</li>" for item in preview.summary_lines
    )
    body = (
        '<section class="draft-banner"><strong>'
        "预览完成，尚未正式提交。</strong></section>"
        '<section class="status"><h2>预览本次处理</h2>'
        '<p class="boundary">这是无副作用预览；提交检查不等于接受贡献。</p>'
        f'<ul class="preview-list">{lines}</ul></section>'
        '<form method="post" action="/execute"><section class="actions">'
        f'<input type="hidden" name="csrf_token" value="{html.escape(csrf_token)}">'
        f'<input type="hidden" name="preview_token" value="{token}">'
        '<button type="submit">提交维护者检查</button>'
        '<a class="button secondary" href="/">返回修改选择</a>'
        "</section></form><details><summary>Preview trace 技术详情</summary><pre>"
        + html.escape(
            json.dumps(preview.to_dict(), ensure_ascii=False, indent=2)
        )
        + "</pre></details>"
    )
    return _page(
        title="AGM Review Submission Preview",
        header_title="维护者检查提交预览",
        header_subtitle="统一确认后才会调用既有治理操作",
        body=body,
    )


def render_review_result_html(result: ReviewSubmissionResult) -> str:
    next_step = result.next_review_brief.current_next_step
    body = (
        '<section class="status success"><h2>你的维护者检查已提交</h2>'
        f"<p>{html.escape(next_step.display_title)}</p>"
        f"<p>{html.escape(next_step.plain_explanation)}</p>"
        '<p class="boundary">维护者检查已经提交，但不等于贡献已经被接受。</p>'
        '<a class="button" href="/">查看新的逐项检查状态</a></section>'
    )
    return _page(
        title="AGM Review Submitted",
        header_title="维护者检查结果",
        header_subtitle="AGM 已根据既有操作自动路由下一责任方",
        body=body,
    )


def render_final_decision_html(
    view: FinalDecisionView,
    *,
    csrf_token: str | None = None,
) -> str:
    completed = (
        view.requirement_summary,
        view.verification_summary,
        view.unresolved_finding_summary,
    )
    completed_html = "".join(
        f"<li>✓ {html.escape(item)}</li>" for item in completed
    )
    options = "".join(
            '<label class="option">'
            f'<input type="radio" name="decision_id" value="{html.escape(option.decision_id)}"'
            f'{" disabled" if not option.authorized or not csrf_token else ""}>'
            f"<strong>{html.escape(option.display_label)}</strong>"
            f"<p>{html.escape(option.plain_consequence)}</p></label>"
            for option in view.options
            if option.authorized
    )
    if view.available and csrf_token:
        action = (
            '<form method="post" action="/final/preview">'
            f'<input type="hidden" name="csrf_token" value="{html.escape(csrf_token)}">'
            f'<div class="options">{options}</div>'
            '<label><strong>最终决定原因</strong>'
            '<textarea name="reason" maxlength="2000" required></textarea></label>'
            '<section class="actions"><button type="submit">预览最终决定</button>'
            '<a class="button secondary" href="/">返回维护者检查</a>'
            "</section></form>"
        )
    elif view.available:
        action = (
            f'<div class="options">{options}</div>'
            '<section class="unavailable">静态演示页面仅用于视觉复核，'
            "不能在此提交最终选择。</section>"
        )
    else:
        action = (
            f'<section class="unavailable">{html.escape(view.unavailable_reason or "当前没有可执行的最终决定。")}</section>'
        )
    technical = html.escape(
        json.dumps(view.to_dict(), ensure_ascii=False, indent=2)
    )
    body = (
        '<section class="boundary"><strong>当前为 AGM 本地审查工作台。</strong> 这里的操作只记录 AGM 审查结果；不会修改代码，不会执行 git merge，也不会批准或合并 GitHub/GitLab 上的 PR。</section>'
        '<section class="status"><h2>记录 AGM 最终审查建议</h2>'
        '<p>治理材料和维护者检查已经完成。</p>'
        f"<p>{html.escape(view.final_authority_summary)}</p>"
        f'<p class="boundary">{html.escape(view.acceptance_boundary)}</p>'
        '</section><section><h2>AGM 审查结论</h2><p>该结论只记录 AGM 审查建议。</p><h2>代码托管平台 PR 状态</h2><p>未连接，未批准，未合并</p></section><section><h2>已完成</h2>'
        f"<ul>{completed_html}</ul></section>"
        '<section><h2>本次贡献</h2>'
        f"<p>{html.escape(view.contribution_summary)}</p>"
        f"<p>{html.escape(view.risk_summary)}</p></section>"
        f"{action}<details><summary>治理过程与技术详情</summary>"
        f"<pre>{technical}</pre></details>"
    )
    return _page(
        title="AGM Final Human Decision",
        header_title="记录 AGM 最终审查建议",
        header_subtitle="不会批准或合并代码托管平台 PR",
        body=body,
        final=True,
    )


def render_final_preview_html(
    preview: FinalDecisionPreview,
    *,
    csrf_token: str,
) -> str:
    lines = "".join(
        f"<li>{html.escape(item)}</li>" for item in preview.summary_lines
    )
    body = (
        '<section class="draft-banner"><strong>'
        "预览完成，尚未正式提交。</strong></section>"
        '<section class="status"><h2>预览最终决定</h2>'
        f"<ul>{lines}</ul><p><strong>原因：</strong>{html.escape(preview.reason)}</p>"
        '<p class="boundary">这是正式提交前的预览；返回不会修改治理案例。</p>'
        '</section><form method="post" action="/final/execute">'
        f'<input type="hidden" name="csrf_token" value="{html.escape(csrf_token)}">'
        f'<input type="hidden" name="preview_token" value="{html.escape(preview.preview_token or "")}">'
        '<section class="actions"><button type="submit">提交最终人类决定</button>'
        '<a class="button secondary" href="/final">返回</a></section></form>'
    )
    return _page(
        title="AGM Final Decision Preview",
        header_title="最终人类决定预览",
        header_subtitle="请确认本次项目决定及其业务后果",
        body=body,
        final=True,
    )


def render_final_result_html(result: FinalDecisionResult) -> str:
    body = (
        '<section class="status success"><h2>最终人类决定已提交</h2>'
        f"<p>{html.escape(result.message)}</p>"
        f"<p>当前状态：{html.escape(result.next_review_brief.governance_details.raw_state)}</p>"
        '<p class="boundary">最终决定记录与前一阶段的维护者检查分别保存。</p>'
        '<a class="button" href="/">返回治理状态</a></section>'
    )
    return _page(
        title="AGM Final Decision Result",
        header_title="最终人类决定结果",
        header_subtitle="项目决定已经记录",
        body=body,
        final=True,
    )
