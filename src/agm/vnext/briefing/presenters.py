"""Render the read-only maintainer brief as JSON, Markdown, and HTML."""

from __future__ import annotations

import html
import json
from typing import Iterable

from .models import (
    AutomaticCheckResult,
    HumanJudgmentItem,
    ReviewBriefView,
)


CHECK_SYMBOLS = {
    "confirmed": "✓",
    "problem": "✕",
    "needs_human_judgment": "?",
    "not_applicable": "–",
}

REQUIREMENT_SYMBOLS = {
    "system_satisfied": "✓",
    "provided_requires_human_judgment": "!",
    "missing": "✕",
    "stale": "!",
    "invalid": "✕",
    "awaiting_accountable_human": "○",
    "awaiting_independent_review": "○",
    "not_applicable": "–",
}


def render_review_brief_json(view: ReviewBriefView) -> str:
    return json.dumps(view.to_dict(), indent=2, ensure_ascii=False) + "\n"


def _markdown_lines(items: Iterable[str], empty: str) -> list[str]:
    values = list(items)
    return [f"- {item}" for item in values] if values else [empty]


def _markdown_checks(
    checks: tuple[AutomaticCheckResult, ...],
    status: str,
    empty: str,
) -> list[str]:
    selected = [item for item in checks if item.status == status]
    if not selected:
        return [empty]
    lines = []
    for item in selected:
        lines.append(
            f"- {CHECK_SYMBOLS[item.status]} {item.display_title}："
            f"{item.plain_result}"
        )
        for limitation in item.limitations:
            lines.append(f"  - 边界：{limitation}")
    return lines


def _markdown_judgment(
    index: int,
    item: HumanJudgmentItem,
) -> list[str]:
    lines = [
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
    return lines


def render_review_brief_markdown(view: ReviewBriefView) -> str:
    """Keep workflow internals out of the participant-visible main layer."""

    contribution = view.contribution
    risk = view.risk
    accountability = view.contributor_accountability
    next_step = view.current_next_step
    lines = [
        "# AGM Maintainer Review Brief",
        "",
        "## 1. 本次贡献与修改",
        "",
        f"### {contribution.title}",
        "",
        f"贡献者说明：{contribution.plain_summary}",
        "",
        f"说明来源：{contribution.summary_source}",
        "",
        f"系统根据文件和声明归纳：{contribution.system_inferred_summary}",
        "",
        "影响范围：",
        "",
        *_markdown_lines(
            contribution.changed_components, "- 未归纳出组件范围"
        ),
        "",
        "可能的行为影响：",
        "",
        *_markdown_lines(
            contribution.behavioral_impacts, "- 未归纳出行为影响"
        ),
        "",
        f"> 归纳边界：{contribution.inference_limitations}",
        "",
        "### 智能体与负责人",
        "",
        (
            "智能体使用：已记录智能体参与。"
            if accountability.agent_used
            else "智能体使用：当前治理案例未声明智能体参与。"
        ),
        "",
        "系统观察到的记录：",
        "",
        *_markdown_lines(
            accountability.system_observations, "- 没有额外系统观察记录"
        ),
        "",
        "智能体或贡献者声明：",
        "",
        *_markdown_lines(
            accountability.declared_facts, "- 当前没有智能体行动声明"
        ),
        "",
        "人类负责人确认：",
        "",
        *_markdown_lines(
            accountability.human_confirmed_facts,
            f"- {accountability.attestation_status}",
        ),
        "",
        "尚未核验的推断边界：",
        "",
        *_markdown_lines(
            accountability.unverified_inferences, "- 无额外推断"
        ),
        "",
        "## 2. 风险判断",
        "",
        f"综合风险：{risk.display_level}",
        "",
        "为什么：",
        "",
        *_markdown_lines(risk.plain_reasons, "- 未记录风险理由"),
        "",
        "风险联动：",
        "",
        *_markdown_lines(risk.interaction_effects, "- 未记录风险联动"),
        "",
        (
            "因此需要独立维护者检查。"
            if risk.requires_independent_review
            else "当前治理结论不要求额外独立维护者检查。"
        ),
        "",
        "## 3. 项目要求和完成情况",
        "",
        f"项目要求 {view.requirements.total_required} 项治理材料或确认：",
        "",
    ]
    for item in view.requirements.items:
        lines.append(
            f"- {REQUIREMENT_SYMBOLS[item.status]} {item.display_title}"
            f" — {item.status_label}：{item.plain_status}"
        )
    lines.extend(
        [
            "",
            "## 4. 系统已经确认",
            "",
            *_markdown_checks(
                view.automatic_checks,
                "confirmed",
                "- 当前没有新增的系统确认项。",
            ),
            "",
            "## 5. 系统发现的问题",
            "",
            *_markdown_checks(
                view.automatic_checks,
                "problem",
                "- 系统当前没有发现形式化问题。",
            ),
            "",
            "### 系统无法判断，需要人检查",
            "",
            *_markdown_checks(
                view.automatic_checks,
                "needs_human_judgment",
                "- 当前没有额外的声明真实性检查项。",
            ),
            "",
            "## 6. 现在需要你判断",
            "",
        ]
    )
    if view.human_judgments:
        lines.append(f"现在需要你检查 {len(view.human_judgments)} 项。")
        lines.append("")
        for index, item in enumerate(view.human_judgments, start=1):
            lines.extend(_markdown_judgment(index, item))
    else:
        lines.extend(
            [
                "当前没有额外 AGM 人类判断项。",
                "",
                (
                    "本次无需额外治理检查，可以进入正常代码审查。"
                    if next_step.status == "normal_code_review"
                    else "请按“当前下一步”继续。"
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## 7. 当前下一步",
            "",
            f"### {next_step.display_title}",
            "",
            next_step.plain_explanation,
            "",
            f"当前责任方：{next_step.responsible_party}",
            "",
            "系统会：",
            "",
            *_markdown_lines(next_step.system_will_do, "- 保持只读"),
            "",
            "人类现在应当：",
            "",
            *_markdown_lines(next_step.human_should_do, "- 无需操作"),
            "",
            f"> {view.authority_notice}",
            "",
            "<details>",
            "<summary>8. 治理过程和技术详情</summary>",
            "",
            "以下内容用于追溯治理状态、规则、义务、材料、问题、修复、"
            "状态变化和 fingerprint；普通审查工作不依赖先理解这些字段。",
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
        return f"<p class=\"empty\">{html.escape(empty)}</p>"
    return "<ul>" + "".join(
        f"<li>{html.escape(item)}</li>" for item in values
    ) + "</ul>"


def _html_checks(
    checks: tuple[AutomaticCheckResult, ...],
    status: str,
    empty: str,
) -> str:
    selected = [item for item in checks if item.status == status]
    if not selected:
        return f'<p class="empty">{html.escape(empty)}</p>'
    cards = []
    for item in selected:
        limitations = _html_list(item.limitations, "")
        cards.append(
            f'<article class="check {html.escape(status)}">'
            f'<h3><span aria-hidden="true">{CHECK_SYMBOLS[status]}</span> '
            f"{html.escape(item.display_title)}</h3>"
            f"<p>{html.escape(item.plain_result)}</p>"
            + (
                f'<div class="limit"><strong>结论边界</strong>{limitations}</div>'
                if item.limitations
                else ""
            )
            + "</article>"
        )
    return "".join(cards)


def _html_judgment(index: int, item: HumanJudgmentItem) -> str:
    return f"""
<article class="judgment">
<div class="judgment-number">{index}</div>
<div>
<h3>{html.escape(item.display_title)}</h3>
<p class="why">{html.escape(item.why_human_is_needed)}</p>
<div class="two-col">
<div><h4>贡献者说明</h4><p>{html.escape(item.contribution_claim)}</p></div>
<div><h4>系统观察</h4><p>{html.escape(item.system_observation)}</p></div>
</div>
<h4>请重点检查</h4>{_html_list(item.review_focus, "无额外检查点")}
<h4>可能的处理结果</h4>{_html_list(item.possible_outcomes, "无")}
</div>
</article>"""


def render_review_brief_html(view: ReviewBriefView) -> str:
    """Render a no-action, scannable page with collapsed technical detail."""

    contribution = view.contribution
    risk = view.risk
    accountability = view.contributor_accountability
    next_step = view.current_next_step
    requirements = "".join(
        (
            f'<li class="requirement {html.escape(item.status)}">'
            f'<span aria-hidden="true">{REQUIREMENT_SYMBOLS[item.status]}</span>'
            f"<div><strong>{html.escape(item.display_title)}</strong>"
            f"<small>{html.escape(item.status_label)}</small>"
            f"<p>{html.escape(item.plain_status)}</p></div></li>"
        )
        for item in view.requirements.items
    )
    judgments = (
        "".join(
            _html_judgment(index, item)
            for index, item in enumerate(view.human_judgments, start=1)
        )
        if view.human_judgments
        else (
            '<div class="no-work"><strong>当前没有额外 AGM 人类判断项。</strong>'
            + (
                "<p>本次无需额外治理检查，可以进入正常代码审查。</p>"
                if next_step.status == "normal_code_review"
                else "<p>请按页面中的“当前下一步”继续。</p>"
            )
            + "</div>"
        )
    )
    technical = html.escape(
        json.dumps(
            view.governance_details.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AGM Maintainer Review Brief</title>
<style>
:root {{ color-scheme: light; --ink:#18212f; --muted:#5d6878; --line:#dbe2ea;
--paper:#fff; --bg:#f3f6f8; --blue:#125da8; --green:#18754d; --amber:#9a5b00;
--red:#ae2f2f; --navy:#153452; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.6
system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif; }}
main {{ width:min(1120px,calc(100% - 32px)); margin:32px auto 64px; }}
.hero {{ color:white; background:linear-gradient(135deg,#112f4b,#176a83);
padding:32px; border-radius:20px; box-shadow:0 14px 34px #17324b24; }}
.hero h1 {{ margin:0 0 8px; font-size:clamp(1.8rem,4vw,3rem); }}
.hero p {{ max-width:760px; margin:.4rem 0; color:#e7f3fa; }}
section {{ background:var(--paper); margin:18px 0; padding:28px;
border:1px solid var(--line); border-radius:16px; }}
h2 {{ margin:0 0 18px; font-size:1.5rem; color:var(--navy); }}
h3 {{ margin:.2rem 0 .5rem; }}
h4 {{ margin:1rem 0 .35rem; }}
.eyebrow {{ color:var(--blue); font-weight:750; letter-spacing:.06em; }}
.grid,.two-col {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; }}
.fact {{ border-left:4px solid #76a6bf; padding:4px 0 4px 14px; }}
.fact small,.requirement small {{ display:block; color:var(--muted); }}
.inference {{ background:#edf5f9; border-radius:12px; padding:14px; }}
.risk-level {{ display:inline-block; font-size:1.6rem; font-weight:800; color:white;
background:var(--red); padding:6px 16px; border-radius:999px; }}
.requirements {{ list-style:none; padding:0; margin:0; display:grid; gap:10px; }}
.requirement {{ display:grid; grid-template-columns:34px 1fr; gap:8px;
border:1px solid var(--line); border-radius:12px; padding:12px; }}
.requirement>span {{ font-size:1.4rem; font-weight:800; }}
.requirement p {{ margin:.25rem 0 0; }}
.system_satisfied>span,.confirmed h3 {{ color:var(--green); }}
.missing>span,.invalid>span,.problem h3 {{ color:var(--red); }}
.stale>span,.provided_requires_human_judgment>span,
.awaiting_accountable_human>span,.awaiting_independent_review>span,
.needs_human_judgment h3 {{ color:var(--amber); }}
.check {{ border-left:5px solid var(--line); padding:12px 16px;
margin:10px 0; background:#fbfcfd; border-radius:8px; }}
.check.confirmed {{ border-color:var(--green); }}
.check.problem {{ border-color:var(--red); }}
.check.needs_human_judgment {{ border-color:var(--amber); }}
.check p {{ margin:.3rem 0; }}
.limit {{ color:var(--muted); font-size:.92rem; }}
.judgment {{ display:grid; grid-template-columns:48px 1fr; gap:14px;
padding:20px; margin:14px 0; border:2px solid #c8953b; border-radius:14px; }}
.judgment-number {{ display:grid; place-items:center; align-self:start; width:42px;
height:42px; border-radius:50%; color:white; background:var(--amber); font-weight:800; }}
.why {{ color:var(--muted); }}
.next {{ border-color:#8ab0c9; background:#f4faff; }}
.authority {{ border-left:6px solid var(--amber); padding-left:14px; }}
.empty {{ color:var(--muted); }}
.no-work {{ text-align:center; padding:24px; background:#eef8f3; border-radius:12px; }}
details {{ background:var(--paper); border:1px solid var(--line); border-radius:14px;
padding:18px; }}
summary {{ cursor:pointer; font-weight:750; color:var(--navy); }}
pre {{ max-height:70vh; overflow:auto; padding:16px; background:#111b27;
color:#e8eef4; border-radius:10px; white-space:pre-wrap; overflow-wrap:anywhere; }}
@media (max-width:720px) {{ .grid,.two-col {{ grid-template-columns:1fr; }}
section {{ padding:20px; }} main {{ width:min(100% - 18px,1120px); margin-top:10px; }} }}
</style>
</head>
<body><main>
<header class="hero">
<div class="eyebrow">AGM REVIEW BRIEF</div>
<h1>维护者审查简报</h1>
<p>先看修改、风险、系统确认和你现在真正需要判断的事项。治理流程与技术字段收在页面末尾。</p>
</header>
<section id="contribution">
<h2>1. 本次贡献与修改</h2>
<div class="grid">
<div class="fact"><small>贡献者说明</small><strong>{html.escape(contribution.plain_summary)}</strong>
<p>{html.escape(contribution.summary_source)}</p></div>
<div class="fact"><small>系统归纳的影响范围</small>
{_html_list(contribution.changed_components, "未归纳出组件范围")}</div>
</div>
<div class="inference"><strong>系统根据文件和声明归纳</strong>
<p>{html.escape(contribution.system_inferred_summary)}</p>
<small>{html.escape(contribution.inference_limitations)}</small></div>
<h3>智能体与负责人</h3>
<div class="two-col">
<div><h4>系统观察</h4>{_html_list(accountability.system_observations, "没有额外系统观察记录")}
<h4>智能体或贡献者声明</h4>{_html_list(accountability.declared_facts, "当前没有智能体行动声明")}</div>
<div><h4>人类负责人确认</h4>{_html_list(accountability.human_confirmed_facts, accountability.attestation_status)}
<h4>未核验推断边界</h4>{_html_list(accountability.unverified_inferences, "无")}</div>
</div>
</section>
<section id="risk">
<h2>2. 风险判断</h2>
<p class="risk-level">综合风险：{html.escape(risk.display_level)}</p>
<h3>为什么</h3>{_html_list(risk.plain_reasons, "未记录风险理由")}
<h3>风险联动</h3>{_html_list(risk.interaction_effects, "未记录风险联动")}
<p><strong>{"需要独立维护者检查" if risk.requires_independent_review else "不要求额外独立维护者检查"}</strong></p>
</section>
<section id="requirements">
<h2>3. 项目要求和完成情况</h2>
<p>项目要求 {view.requirements.total_required} 项治理材料或确认。</p>
<ul class="requirements">{requirements}</ul>
</section>
<section id="confirmed">
<h2>4. 系统已经确认</h2>
{_html_checks(view.automatic_checks, "confirmed", "当前没有新增的系统确认项。")}
</section>
<section id="problems">
<h2>5. 系统发现的问题</h2>
{_html_checks(view.automatic_checks, "problem", "系统当前没有发现形式化问题。")}
<h3>系统无法判断，需要人检查</h3>
{_html_checks(view.automatic_checks, "needs_human_judgment", "当前没有额外的声明真实性检查项。")}
</section>
<section id="judgments">
<h2>6. 现在需要你判断</h2>
{judgments}
</section>
<section id="next" class="next">
<h2>7. 当前下一步</h2>
<h3>{html.escape(next_step.display_title)}</h3>
<p>{html.escape(next_step.plain_explanation)}</p>
<p><strong>当前责任方：</strong>{html.escape(next_step.responsible_party)}</p>
<div class="two-col"><div><h4>系统会</h4>{_html_list(next_step.system_will_do, "保持只读")}</div>
<div><h4>人类现在应当</h4>{_html_list(next_step.human_should_do, "无需操作")}</div></div>
<p class="authority">{html.escape(view.authority_notice)}</p>
</section>
<details id="technical">
<summary>8. 治理过程和技术详情</summary>
<p>这里保留完整 workflow、state、规则、义务、材料、问题、修复、状态变化、ID 和 fingerprint，供追溯使用。</p>
<pre>{technical}</pre>
</details>
</main></body></html>"""
