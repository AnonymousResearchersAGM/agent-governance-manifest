"""Render an already-derived diagnostic without adding participant conclusions."""
from __future__ import annotations
import html, json
from .artifact_projection import project_structured_artifact
from .models import PRDiagnosticView

def render_pr_diagnostic_json(view: PRDiagnosticView) -> str: return json.dumps(view.to_dict(),ensure_ascii=False,indent=2)+"\n"
def render_pr_diagnostic_markdown(view: PRDiagnosticView) -> str:
    route=view.recommended_route
    return "\n".join(["# PR 审查诊断","",f"## {view.diagnostic_status}",route["message"],"",f"当前待办归属：{route['action_owner']}",f"下一步需要完成：{route['next_action']}","最终决定权：维护者","最终接受、拒绝或合并决定仍由人类维护者作出。","", "## 修改概览",str(view.change_summary["summary"])])+"\n"
def _agent(data: dict) -> str:
    if data["state"]=="not_detected": return "<p>未检测到可验证的 Agent 参与记录。该贡献可能主要由人工完成，也可能存在未被记录的辅助工具使用。</p>"
    rows=[data["message"], f"工具类型：{data.get('type') or '未记录'}",f"修改文件：{data.get('modified_file_count',0)} 个",f"运行命令：{len(data.get('commands',()))} 条",f"测试：{'；'.join(data.get('tests',())) or '未记录'}",f"使用其他助手或自动化工具：{'是' if data.get('used_other_tools') else '未记录或否'}",f"网络访问：{'是' if data.get('network') else '未记录或否'}",f"记录版本：{'对应当前版本' if data.get('current_version') else '尚未关联当前版本'}"]
    return "<ul>"+"".join(f"<li>{html.escape(str(row))}</li>" for row in rows)+"</ul>"
def _object(item) -> str:
    projection = project_structured_artifact(
        metadata={
            **item.technical_metadata,
            "artifact_id": item.object_id,
            "artifact_type": item.technical_metadata.get("artifact_type"),
            "title": item.title,
            "content_digest": item.content_digest,
            "contribution_fingerprint": item.contribution_fingerprint,
        },
        content=item.inline_content,
        package_digest=item.evidence_package_digest or "",
    ) if item.inline_content else None
    if projection and projection.readable_available:
        content = f"<details><summary>预览可读视图</summary>{projection.rendered_html}</details>"
    elif item.inline_content:
        content = f"<details><summary>展开材料</summary><pre>{html.escape(item.inline_content)}</pre></details>"
    else:
        content = ""
    link = f'<p><a href="{html.escape(item.artifact_route,quote=True)}">查看完整材料</a></p>' if item.artifact_route else ""
    unavailable = "<p>该材料当前不可查看。</p>" if not item.inline_content and not item.artifact_route else ""
    return f"<article><h3>{html.escape(item.title)}</h3><p>{html.escape(item.plain_language_summary)}</p><p>{html.escape({'current':'对应当前版本','stale':'对应旧版本','expired':'已过有效期','invalid':'材料不完整','rejected':'验证未通过','unbound':'尚未关联当前版本'}.get(item.freshness,item.freshness))}</p>{content}{link}{unavailable}</article>"
def render_pr_diagnostic_html(view: PRDiagnosticView) -> str:
    esc=html.escape
    requirements="".join(f"<li>{esc(item['title'])}：{esc({'current':'对应当前版本','missing':'未提供','stale':'对应旧版本','expired':'已过有效期','invalid':'材料不完整','rejected':'验证未通过','unbound':'尚未关联当前版本'}[item['state']])}</li>" for item in view.expected_requirements)
    risks="".join(f"<article><h3>{esc(item.headline)}</h3><p>{esc('；'.join(item.affected_files))} {esc('；'.join(item.affected_line_ranges))}</p><p>{esc(item.plain_language_explanation)}</p></article>" for item in view.risk_findings)
    gaps="".join(f"<article class=gap><h3>{esc(item.headline)}</h3><p>{esc(item.plain_language_explanation)}</p><p>{esc(item.gap)}</p></article>" for item in view.evidence_gaps) or "<p>当前无需额外处理。</p>"
    actions="".join(f"<article><h3>{esc(a.label)}</h3><p><strong>会：</strong>{esc('；'.join(a.will_do))}</p><p><strong>不会：</strong>{esc('；'.join(a.will_not_do))}</p></article>" for a in view.action_effect_boundaries)
    host=view.host_platform_status
    route=view.recommended_route
    submission=""
    if view.verification_submission:
        item=view.verification_submission
        submission=f'''<section class="handoff"><h2>核验交接状态</h2><p>PR 已创建，材料也已准备，但贡献者尚未明确提交本轮治理材料供维护者核验。</p><dl><div><dt>PR 状态</dt><dd>{esc(item.pr_status)}</dd></div><div><dt>材料完整性</dt><dd>{esc(item.material_completeness)}</dd></div><div><dt>贡献者人工确认</dt><dd>{esc(item.contributor_confirmation)}</dd></div><div><dt>核验提交状态</dt><dd>{esc(item.submission_status)}</dd></div><div><dt>缺失的交接记录</dt><dd>{esc(item.missing_handoff_record)}</dd></div></dl></section>'''
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PR 审查诊断</title><style>body{{margin:0;background:#f3f6f8;font:16px/1.55 system-ui;color:#18212f;overflow-wrap:anywhere}}main{{max-width:1040px;margin:auto;padding:16px;min-width:0}}header{{background:#153452;color:#fff;padding:20px;border-radius:12px}}section,article,details{{background:#fff;border:1px solid #dbe2ea;border-radius:12px;padding:16px;margin:14px 0;min-width:0}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}.gap{{border-left:6px solid #a64b17}}.handoff{{border-left:6px solid #3578a8}}dl div{{display:grid;grid-template-columns:minmax(9rem,14rem) 1fr;gap:12px;padding:8px 0;border-bottom:1px solid #e5e9ee}}dt{{font-weight:700}}dd{{margin:0}}pre{{white-space:pre-wrap;overflow:auto}}li[class^=depth-]{{margin-left:calc(var(--depth, 0) * 1rem)}}.depth-1{{margin-left:1rem}}.depth-2{{margin-left:2rem}}@media(max-width:720px){{main{{padding:8px}}.grid{{grid-template-columns:1fr}}dl div{{grid-template-columns:1fr;gap:2px}}}}</style><main><header><h1>PR 审查诊断</h1><p>这是本地审查工作台：不会修改代码，不会执行 git merge，也不会批准或合并代码托管平台 PR。</p></header><section class=gap><h2>{esc(view.diagnostic_status)}</h2><p><strong>当前待办归属：</strong>{esc(route['action_owner'])}</p><p><strong>下一步需要完成：</strong>{esc(route['next_action'])}</p><p><strong>最终决定权：</strong>维护者</p><p>最终接受、拒绝或合并决定仍由人类维护者作出。</p></section>{submission}<section><h2>这次 PR 改了什么</h2><p>{esc(str(view.change_summary['summary']))}</p><p>{esc('；'.join(view.change_summary['files']))}</p></section><section><h2>风险位置与原因</h2>{risks}</section><section><h2>项目要求与当前情况</h2><ul>{requirements}</ul></section><section><h2>缺失和异常</h2>{gaps}</section><section><h2>编码助手参与情况</h2>{_agent(view.agent_involvement)}</section><section><h2>人工检查状态</h2><ul><li>贡献者是否已经检查当前版本：{esc(view.human_review_status['contributor_self_review'])}</li><li>维护者是否完成必要检查：{esc(view.human_review_status['maintainer_review'])}</li><li>是否已由有权限的人类维护者记录最终建议：{esc(view.human_review_status['final_recommendation'])}</li></ul></section><section><h2>AGM 最终审查建议</h2><p>{esc(view.final_recommendation['status'])}</p><h2>代码托管平台</h2><p>{'未连接代码托管平台' if not host.connected else esc(host.provider or '')}；未通过本页批准 PR；未通过本页合并 PR。</p></section><section><h2>具体检查对象</h2>{''.join(_object(o) for o in view.inspection_objects)}</section>{('<section><h2>当前可执行操作</h2>'+actions+'</section>') if actions else ''}<details><summary>技术详情（内部路由字段）</summary><pre>{esc(json.dumps(view.technical_derivation,ensure_ascii=False,indent=2))}</pre></details></main></html>'''
