"""Render the read-only maintainer brief as JSON, Markdown, and HTML."""

from __future__ import annotations

import html
import json
from collections import Counter
from typing import Iterable

from .models import (
    AutomaticCheckResult,
    HumanJudgmentItem,
    RequirementItem,
    ReviewBriefView,
    WorkItemSummary,
    WorkOwner,
)


CHECK_SYMBOLS = {
    "system_checked": "✓",
    "problem": "✕",
    "human_review_required": "!",
    "system_handled": "✓",
    "informational": "i",
    "not_applicable": "–",
}

REQUIREMENT_SYMBOLS = {
    "material_available": "✓",
    "structure_valid": "✓",
    "version_bound": "✓",
    "system_checked": "✓",
    "human_review_required": "!",
    "human_verified": "✓",
    "missing": "✕",
    "stale": "!",
    "invalid": "✕",
    "awaiting_accountable_human": "○",
    "awaiting_independent_review": "○",
    "not_applicable": "–",
}

SEMANTIC_LABELS = {
    "material_available": "材料已提供",
    "structure_valid": "形式要求已满足",
    "version_bound": "已对应当前版本",
    "system_checked": "材料与版本已核对",
    "human_review_required": "内容待人工检查",
    "human_verified": "维护者已完成检查",
    "final_decision_pending": "等待最终人类决定",
    "accepted": "贡献已被最终接受",
}

OWNER_LABELS = {
    WorkOwner.SYSTEM: "系统已处理",
    WorkOwner.CONTRIBUTION_SIDE: "贡献侧处理",
    WorkOwner.ACCOUNTABLE_HUMAN: "负责人处理",
    WorkOwner.MAINTAINER: "维护者判断",
    WorkOwner.FINAL_DECISION_AUTHORITY: "最终决定人处理",
}


def render_review_brief_json(view: ReviewBriefView) -> str:
    return json.dumps(view.to_dict(), indent=2, ensure_ascii=False) + "\n"


def _markdown_lines(items: Iterable[str], empty: str) -> list[str]:
    values = list(items)
    return [f"- {item}" for item in values] if values else [empty]


def _markdown_requirement(item: RequirementItem) -> list[str]:
    states = "；".join(
        SEMANTIC_LABELS[state]
        for state in item.semantic_states
        if state in SEMANTIC_LABELS
    )
    suffix = f"（{states}）" if states else ""
    return [
        (
            f"- {REQUIREMENT_SYMBOLS[item.semantic_status]} {item.display_title}"
            f" — {item.status_label}{suffix}"
        ),
        f"  - {item.plain_status}",
    ]


def _markdown_check(item: AutomaticCheckResult) -> list[str]:
    owner = OWNER_LABELS[item.owner]
    policy = (
        "项目规则要求"
        if item.policy_required
        else (
            "附加信息"
            if item.informational_only
            else "系统完整性核对"
        )
    )
    lines = [
        (
            f"- {CHECK_SYMBOLS[item.semantic_status]} {item.display_title}："
            f"{item.plain_result}"
        ),
        f"  - 类别：{policy}；责任：{owner}",
    ]
    lines.extend(f"  - 结论边界：{value}" for value in item.limitations)
    return lines


def _markdown_judgment(
    index: int,
    item: HumanJudgmentItem,
) -> list[str]:
    return [
        f"### {index}. {item.display_title}",
        "",
        f"为什么需要人：{item.why_human_is_needed}",
        "",
        f"贡献者说明：{item.contribution_claim}",
        "",
        f"系统观察：{item.system_observation}",
        "",
        f"材料摘要：{item.evidence_summary}",
        "",
        "请重点检查：",
        "",
        *_markdown_lines(item.review_focus, "- 无额外检查点"),
        "",
        "可能的处理结果：",
        "",
        *_markdown_lines(item.possible_outcomes, "- 无"),
        "",
    ]


def _requirement_summary(view: ReviewBriefView) -> list[str]:
    counts = Counter(item.owner for item in view.requirements.items)
    ready = len(view.requirements.system_satisfied)
    lines = [f"项目要求 {view.requirements.total_required} 项材料或确认。"]
    if counts[WorkOwner.CONTRIBUTION_SIDE]:
        lines.append(
            f"- {counts[WorkOwner.CONTRIBUTION_SIDE]} 项尚待贡献侧处理"
        )
    if counts[WorkOwner.ACCOUNTABLE_HUMAN]:
        lines.append(
            f"- {counts[WorkOwner.ACCOUNTABLE_HUMAN]} 项等待负责人确认"
        )
    if counts[WorkOwner.MAINTAINER]:
        lines.append(
            f"- {counts[WorkOwner.MAINTAINER]} 项需要维护者判断"
        )
    if ready:
        lines.append(f"- {ready} 项已完成当前阶段的形式核对或人工检查")
    if len(lines) == 1:
        lines.append("- 项目要求已经齐备")
    return lines


def _check_summary(view: ReviewBriefView) -> list[str]:
    counts = Counter(
        item.semantic_status for item in view.automatic_checks
    )
    return [
        "自动检查：",
        f"- {counts['system_checked']} 项完成形式或版本核对",
        f"- {counts['problem']} 项发现问题",
        f"- {counts['human_review_required']} 项需要人工判断",
        f"- {counts['system_handled']} 项异常已由系统处理",
    ]


def render_review_brief_markdown(view: ReviewBriefView) -> str:
    """Put the current conclusion first and fold supporting detail."""

    contribution = view.contribution
    risk = view.risk
    accountability = view.contributor_accountability
    next_step = view.current_next_step
    outstanding = [
        item
        for item in view.work_items
        if item.owner
        in {WorkOwner.CONTRIBUTION_SIDE, WorkOwner.ACCOUNTABLE_HUMAN}
    ]
    anomalies = [item for item in view.work_items if item.system_handled]
    blockers = [
        item
        for item in view.automatic_checks
        if item.semantic_status == "problem" and item.blocking
    ]
    lines = [
        "# AGM Maintainer Review Brief",
        "",
        f"## {contribution.title}",
        "",
        "## 当前状态与下一步",
        "",
        f"### {next_step.display_title}",
        "",
        next_step.plain_explanation,
        "",
        f"当前责任方：{next_step.responsible_party}",
        "",
        *_markdown_lines(next_step.human_should_do, "- 当前无需操作"),
        "",
        (
            "> 贡献已被最终接受，最终决定和治理记录已经归档。"
            if next_step.final_acceptance_state == "accepted"
            else "> 检查完成不等于贡献已被接受；最终决定仍由有权人类维护者作出。"
        ),
        "",
    ]
    if view.human_judgments:
        lines.extend(
            [
                f"## 现在需要你判断的事项（{len(view.human_judgments)} 项）",
                "",
            ]
        )
        for index, item in enumerate(view.human_judgments, start=1):
            lines.extend(_markdown_judgment(index, item))

    lines.extend(
        [
            "## 本次修改与风险",
            "",
            f"贡献者说明：{contribution.plain_summary}",
            "",
            "系统根据文件和声明归纳：",
            "",
            contribution.system_inferred_summary,
            "",
            "影响范围：",
            "",
            *_markdown_lines(
                contribution.changed_components, "- 未归纳出组件范围"
            ),
            "",
            f"综合风险：{risk.display_level}",
            "",
            *_markdown_lines(risk.plain_reasons, "- 未记录风险理由"),
            "",
            *_markdown_lines(risk.interaction_effects, "- 未记录风险联动"),
            "",
            f"> 归纳边界：{contribution.inference_limitations}",
            "",
        ]
    )

    if outstanding:
        lines.extend(["## 贡献侧或负责人尚需完成", ""])
        for item in outstanding:
            lines.extend(
                [
                    f"### {OWNER_LABELS[item.owner]}：{item.display_title}",
                    "",
                    item.plain_explanation,
                    "",
                ]
            )

    if blockers or anomalies:
        lines.extend(["## 当前问题与系统处理", ""])
        if blockers:
            lines.extend(["### 阻断性问题", ""])
            for item in blockers:
                lines.extend(_markdown_check(item))
            lines.append("")
        if anomalies:
            lines.extend(["### 系统已处理的异常", ""])
            for item in anomalies:
                lines.extend(
                    [
                        f"- {item.display_title}：{item.plain_explanation}",
                        "  - 系统已拒绝该操作；该事件不产生新的维护者判断项。",
                    ]
                )
            lines.append("")

    lines.extend(
        [
            "## 项目要求与自动检查摘要",
            "",
            *_requirement_summary(view),
            "",
            *_check_summary(view),
            "",
            "<details>",
            "<summary>查看全部项目要求</summary>",
            "",
        ]
    )
    for item in view.requirements.items:
        lines.extend(_markdown_requirement(item))
    lines.extend(
        [
            "",
            "</details>",
            "",
            "<details>",
            "<summary>查看自动检查详情</summary>",
            "",
        ]
    )
    for item in view.automatic_checks:
        lines.extend(_markdown_check(item))
    lines.extend(
        [
            "",
            "</details>",
            "",
            "<details>",
            "<summary>查看智能体与负责人材料</summary>",
            "",
            "系统观察：",
            "",
            *_markdown_lines(
                accountability.system_observations, "- 没有额外系统观察"
            ),
            "",
            "贡献侧声明：",
            "",
            *_markdown_lines(
                accountability.declared_facts, "- 当前没有相关声明"
            ),
            "",
            "负责人确认：",
            "",
            *_markdown_lines(
                accountability.human_confirmed_facts,
                f"- {accountability.attestation_status}",
            ),
            "",
            "边界：",
            "",
            *_markdown_lines(
                accountability.unverified_inferences, "- 无额外推断"
            ),
            "",
            "</details>",
            "",
            "<details>",
            "<summary>治理过程与技术详情</summary>",
            "",
            "以下内容用于追溯完整 workflow、内部状态、规则、义务、"
            "finding、transition、ID、trace 和 fingerprint。",
            "",
            "```json",
            json.dumps(
                view.governance_details.to_dict(),
                indent=2,
                ensure_ascii=False,
            ),
            "```",
            "",
            "</details>",
        ]
    )
    return "\n".join(lines) + "\n"


def _html_list(items: Iterable[str], empty: str) -> str:
    values = list(items)
    if not values:
        return f'<p class="empty">{html.escape(empty)}</p>'
    return "<ul>" + "".join(
        f"<li>{html.escape(item)}</li>" for item in values
    ) + "</ul>"


def _html_requirement(item: RequirementItem) -> str:
    badges = "".join(
        f'<span class="semantic-badge">{html.escape(SEMANTIC_LABELS[state])}</span>'
        for state in item.semantic_states
        if state in SEMANTIC_LABELS
    )
    return (
        f'<li class="requirement {html.escape(item.semantic_status)}">'
        f'<span class="symbol" aria-hidden="true">'
        f"{REQUIREMENT_SYMBOLS[item.semantic_status]}</span>"
        f"<div><strong>{html.escape(item.display_title)}</strong>"
        f'<small class="status-label">{html.escape(item.status_label)}</small>'
        f'<div class="badges">{badges}</div>'
        f"<p>{html.escape(item.plain_status)}</p></div></li>"
    )


def _html_check(item: AutomaticCheckResult) -> str:
    policy = (
        "项目规则要求"
        if item.policy_required
        else (
            "附加信息"
            if item.informational_only
            else "系统完整性核对"
        )
    )
    limitations = (
        '<div class="limit"><strong>结论边界</strong>'
        + _html_list(item.limitations, "")
        + "</div>"
        if item.limitations
        else ""
    )
    return (
        f'<article class="check {html.escape(item.semantic_status)}">'
        f"<h3><span aria-hidden=\"true\">"
        f"{CHECK_SYMBOLS[item.semantic_status]}</span> "
        f"{html.escape(item.display_title)}</h3>"
        f"<p>{html.escape(item.plain_result)}</p>"
        f'<p class="meta">{html.escape(policy)} · '
        f"{html.escape(OWNER_LABELS[item.owner])}</p>"
        f"{limitations}</article>"
    )


def _html_judgment(index: int, item: HumanJudgmentItem) -> str:
    return f"""
<article class="judgment">
<div class="judgment-number">{index}</div>
<div>
<h3>{html.escape(item.display_title)}</h3>
<p class="owner-tag">{html.escape(OWNER_LABELS[item.owner])}</p>
<p class="why">{html.escape(item.why_human_is_needed)}</p>
<div class="two-col">
<div><h4>贡献者说明</h4><p>{html.escape(item.contribution_claim)}</p></div>
<div><h4>系统观察</h4><p>{html.escape(item.system_observation)}</p></div>
</div>
<h4>请重点检查</h4>{_html_list(item.review_focus, "无额外检查点")}
<h4>可能的处理结果</h4>{_html_list(item.possible_outcomes, "无")}
</div>
</article>"""


def _html_work_item(item: WorkItemSummary) -> str:
    return (
        '<article class="work-item">'
        f'<p class="owner-tag">{html.escape(OWNER_LABELS[item.owner])}</p>'
        f"<h3>{html.escape(item.display_title)}</h3>"
        f"<p>{html.escape(item.plain_explanation)}</p>"
        "</article>"
    )


def _html_requirement_summary(view: ReviewBriefView) -> str:
    return _html_list(_requirement_summary(view), "项目要求已经齐备")


def _html_check_summary(view: ReviewBriefView) -> str:
    return _html_list(_check_summary(view)[1:], "没有自动检查记录")


def render_review_brief_html(view: ReviewBriefView) -> str:
    """Render current-next-step-first information with folded detail."""

    contribution = view.contribution
    risk = view.risk
    accountability = view.contributor_accountability
    next_step = view.current_next_step
    status_class = {
        "awaiting_contributor": "waiting",
        "awaiting_accountable_human": "accountable",
        "maintainer_judgment": "judgment-needed",
        "normal_code_review": "ready",
        "awaiting_final_human_decision": "final",
        "completed": "complete",
        "policy_migration_attention": "judgment-needed",
    }.get(next_step.status, "judgment-needed")
    acceptance_boundary = (
        "贡献已被最终接受；最终决定和治理记录已经归档。"
        if next_step.final_acceptance_state == "accepted"
        else "检查完成不等于贡献已被接受；最终决定仍由有权人类维护者作出。"
    )
    judgments = "".join(
        _html_judgment(index, item)
        for index, item in enumerate(view.human_judgments, start=1)
    )
    outstanding = [
        item
        for item in view.work_items
        if item.owner
        in {WorkOwner.CONTRIBUTION_SIDE, WorkOwner.ACCOUNTABLE_HUMAN}
    ]
    anomalies = [item for item in view.work_items if item.system_handled]
    blockers = [
        item
        for item in view.automatic_checks
        if item.semantic_status == "problem" and item.blocking
    ]
    requirements = "".join(
        _html_requirement(item) for item in view.requirements.items
    )
    checks = "".join(_html_check(item) for item in view.automatic_checks)
    technical = html.escape(
        json.dumps(
            view.governance_details.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
    )
    outstanding_section = (
        '<section id="outstanding"><h2>贡献侧或负责人尚需完成</h2>'
        + "".join(_html_work_item(item) for item in outstanding)
        + "</section>"
        if outstanding
        else ""
    )
    issue_section = ""
    if blockers or anomalies:
        parts = ['<section id="issues"><h2>当前问题与系统处理</h2>']
        if blockers:
            parts.append("<h3>阻断性问题</h3>")
            parts.extend(_html_check(item) for item in blockers)
        if anomalies:
            parts.append("<h3>系统已处理的异常</h3>")
            for item in anomalies:
                parts.append(_html_work_item(item))
            parts.append(
                "<p class=\"system-note\">这些异常已被拒绝且未改变治理状态，"
                "不会生成新的维护者判断项。</p>"
            )
        parts.append("</section>")
        issue_section = "".join(parts)
    judgment_section = (
        '<section id="judgments"><h2>现在需要你判断的事项'
        f"（{len(view.human_judgments)} 项）</h2>{judgments}</section>"
        if view.human_judgments
        else ""
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AGM Maintainer Review Brief</title>
<style>
:root {{ color-scheme:light; --ink:#18212f; --muted:#5d6878; --line:#dbe2ea;
--paper:#fff; --bg:#f3f6f8; --blue:#176b9c; --green:#18754d; --amber:#986000;
--red:#ae2f2f; --purple:#6654a4; --navy:#153452; --gray:#66717e; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.55
system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif; overflow-wrap:anywhere; }}
main {{ width:min(1120px,calc(100% - 32px)); margin:20px auto 64px; }}
.hero {{ color:white; background:linear-gradient(135deg,#112f4b,#176a83);
padding:22px 28px; border-radius:18px 18px 8px 8px; }}
.hero h1 {{ margin:0; font-size:clamp(1.7rem,4vw,2.6rem); }}
.hero p {{ margin:.35rem 0 0; color:#e7f3fa; }}
section,details {{ background:var(--paper); margin:16px 0; padding:24px;
border:1px solid var(--line); border-radius:14px; }}
h2 {{ margin:0 0 16px; font-size:1.4rem; color:var(--navy); }}
h3 {{ margin:.2rem 0 .5rem; }} h4 {{ margin:1rem 0 .35rem; }}
.status-card {{ margin-top:0; border-width:2px; box-shadow:0 12px 28px #17324b18; }}
.status-card.waiting {{ border-color:var(--blue); background:#f3f9fd; }}
.status-card.accountable,.status-card.final {{ border-color:var(--purple); background:#f7f5ff; }}
.status-card.judgment-needed {{ border-color:var(--amber); background:#fff9ed; }}
.status-card.ready,.status-card.complete {{ border-color:var(--green); background:#f1faf5; }}
.status-title {{ font-size:clamp(1.5rem,4vw,2.2rem); line-height:1.25; margin:.1rem 0 .7rem; }}
.owner-line {{ font-size:1.05rem; }}
.acceptance-boundary {{ border-left:5px solid var(--amber); padding:10px 14px;
background:#fff; border-radius:5px; font-weight:700; }}
.grid,.two-col {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; }}
.summary-card {{ min-width:0; border:1px solid var(--line); border-radius:12px; padding:18px; }}
.risk-level {{ display:inline-block; font-size:1.35rem; font-weight:800; color:white;
background:var(--red); padding:5px 14px; border-radius:999px; }}
.inference {{ background:#edf5f9; border-radius:10px; padding:12px; }}
.judgment {{ display:grid; grid-template-columns:48px minmax(0,1fr); gap:14px;
padding:20px; margin:14px 0; border:2px solid #c8953b; border-radius:14px; }}
.judgment-number {{ display:grid; place-items:center; align-self:start; width:42px;
height:42px; border-radius:50%; color:white; background:var(--amber); font-weight:800; }}
.why,.meta,.limit,.empty {{ color:var(--muted); }}
.owner-tag {{ display:inline-block; margin:.2rem 0 .45rem; color:var(--navy);
background:#eaf1f6; border-radius:999px; padding:3px 10px; font-weight:750; }}
.work-item {{ border-left:5px solid var(--blue); padding:12px 16px;
margin:10px 0; background:#f8fbfd; border-radius:8px; }}
.work-item h3,.work-item p {{ margin:.25rem 0; }}
.check {{ border-left:5px solid var(--line); padding:12px 16px;
margin:10px 0; background:#fbfcfd; border-radius:8px; }}
.check.system_checked {{ border-color:var(--green); }}
.check.problem {{ border-color:var(--red); }}
.check.human_review_required {{ border-color:var(--amber); }}
.check.system_handled {{ border-color:var(--blue); }}
.check.informational,.check.not_applicable {{ border-color:var(--gray); background:#f5f6f7; }}
.check h3,.check p {{ margin:.3rem 0; }}
.system-note {{ color:var(--blue); font-weight:700; }}
summary {{ cursor:pointer; font-weight:800; color:var(--navy); }}
.requirements {{ list-style:none; padding:0; margin:16px 0 0; display:grid; gap:10px; }}
.requirement {{ display:grid; grid-template-columns:34px minmax(0,1fr); gap:8px;
border:1px solid var(--line); border-radius:12px; padding:12px; }}
.symbol {{ font-size:1.4rem; font-weight:800; }}
.status-label {{ display:block; color:var(--muted); }}
.badges {{ display:flex; flex-wrap:wrap; gap:6px; margin-top:7px; }}
.semantic-badge {{ color:#275066; background:#eaf3f7; border-radius:999px;
padding:2px 8px; font-size:.78rem; }}
.missing .symbol,.invalid .symbol,.problem h3 {{ color:var(--red); }}
.stale .symbol,.human_review_required .symbol,
.awaiting_accountable_human .symbol,.awaiting_independent_review .symbol {{ color:var(--amber); }}
.system_checked .symbol,.human_verified .symbol {{ color:var(--green); }}
pre {{ max-height:70vh; overflow:auto; padding:16px; background:#111b27;
color:#e8eef4; border-radius:10px; white-space:pre-wrap; overflow-wrap:anywhere; }}
@media (max-width:720px) {{
  .grid,.two-col {{ grid-template-columns:1fr; }}
  .judgment {{ grid-template-columns:1fr; }}
  section,details {{ padding:18px; }}
  main {{ width:min(100% - 16px,1120px); margin-top:8px; }}
  .hero {{ padding:20px; }}
}}
</style>
</head>
<body><main>
<header class="hero">
<h1>维护者审查简报</h1>
<p>{html.escape(contribution.title)} · 只读治理工作说明</p>
</header>
<section id="current-status" class="status-card {status_class}">
<p class="owner-tag">当前结论</p>
<h2 class="status-title">{html.escape(next_step.display_title)}</h2>
<p>{html.escape(next_step.plain_explanation)}</p>
<p class="owner-line"><strong>当前责任方：</strong>{html.escape(next_step.responsible_party)}</p>
{_html_list(next_step.human_should_do, "当前无需操作")}
<p class="acceptance-boundary">{html.escape(acceptance_boundary)}</p>
</section>
{judgment_section}
<section id="change-risk">
<h2>本次修改与风险</h2>
<div class="grid">
<article class="summary-card"><h3>这次改了什么</h3>
<p><strong>贡献者说明：</strong>{html.escape(contribution.plain_summary)}</p>
<div class="inference"><strong>系统根据文件和声明归纳</strong>
<p>{html.escape(contribution.system_inferred_summary)}</p></div>
<h4>影响范围</h4>{_html_list(contribution.changed_components, "未归纳出组件范围")}
</article>
<article class="summary-card"><h3>风险判断</h3>
<p class="risk-level">综合风险：{html.escape(risk.display_level)}</p>
<h4>为什么</h4>{_html_list(risk.plain_reasons, "未记录风险理由")}
<h4>风险联动</h4>{_html_list(risk.interaction_effects, "未记录风险联动")}
</article>
</div>
<p class="meta">归纳边界：{html.escape(contribution.inference_limitations)}</p>
</section>
{outstanding_section}
{issue_section}
<section id="summaries">
<h2>项目要求与自动检查摘要</h2>
<div class="grid">
<article class="summary-card"><h3>项目要求</h3>{_html_requirement_summary(view)}</article>
<article class="summary-card"><h3>自动检查</h3>{_html_check_summary(view)}</article>
</div>
</section>
<details id="requirements">
<summary>查看全部项目要求</summary>
<ul class="requirements">{requirements}</ul>
</details>
<details id="automatic-checks">
<summary>查看自动检查详情</summary>
{checks}
</details>
<details id="accountability">
<summary>查看智能体与负责人材料</summary>
<div class="two-col">
<div><h3>系统观察</h3>{_html_list(accountability.system_observations, "没有额外系统观察")}
<h3>贡献侧声明</h3>{_html_list(accountability.declared_facts, "当前没有相关声明")}</div>
<div><h3>负责人确认</h3>{_html_list(accountability.human_confirmed_facts, accountability.attestation_status)}
<h3>结论边界</h3>{_html_list(accountability.unverified_inferences, "无额外推断")}</div>
</div>
</details>
<details id="technical">
<summary>治理过程与技术详情</summary>
<p>这里保留完整 workflow、内部状态、规则、义务、材料、finding、transition、ID、trace 和 fingerprint，供追溯使用。</p>
<pre>{technical}</pre>
</details>
</main></body></html>"""
