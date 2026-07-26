"""Human-operable contributor and maintainer reports."""

from __future__ import annotations

import html
from typing import TYPE_CHECKING, Any

from .models import GovernanceCase, StateTransition

if TYPE_CHECKING:
    from .config import VNextConfig
    from .guidance.models import ActionPreview, ActorContext


AUTHORITY_NOTICE = (
    "AGM reports governance readiness only. Verification or readiness is not "
    "acceptance. Final decisions remain with authorized human maintainers."
)


def readiness(case: GovernanceCase) -> str:
    from .guidance.diagnostics import derive_readiness

    return derive_readiness(case)


def obligation_observation(
    case: GovernanceCase, obligation_id: str
) -> str:
    obligation = case.obligation(obligation_id)
    evidence_ids = [
        item.id
        for item in case.evidence
        if obligation_id in item.obligation_ids
    ]
    attestation_ids = (
        [item.id for item in case.attestations]
        if obligation.type == "human_attestation"
        else []
    )
    verification_ids = [
        item.id
        for item in case.maintainer_verifications
        if obligation_id in item.obligation_ids
    ]
    observed = evidence_ids + attestation_ids + verification_ids
    return ", ".join(observed) if observed else "No bound record"


def markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(
    case: GovernanceCase,
    transitions: list[StateTransition],
    *,
    audience: str,
    config: VNextConfig | None = None,
    current_actor: ActorContext | None = None,
) -> str:
    if audience == "maintainer" and config is not None:
        from .guidance import ActorContext, build_reviewer_guidance
        from .guidance.presenters import render_guidance_markdown
        from .migration import check_migration

        actor = current_actor or ActorContext(
            actor="maintainer-reviewer",
            role="maintainer",
        )
        return render_guidance_markdown(
            build_reviewer_guidance(
                case,
                config,
                transitions,
                actor,
                migration_diagnostic=check_migration(case, config),
            )
        )
    title = (
        "AGM Contributor Governance Panel"
        if audience == "contributor"
        else "AGM Maintainer Governance Report"
    )
    zones: dict[str, dict[str, Any]] = {}
    for rule in case.matched_rules:
        item = zones.setdefault(
            rule.zone,
            {"risk_levels": set(), "paths": set(), "rules": set()},
        )
        item["risk_levels"].add(rule.risk_level)
        item["paths"].update(rule.affected_paths)
        item["rules"].add(rule.rule_id)

    lines = [
        f"# {title}",
        "",
        f"- Case ID: `{case.id}`",
        f"- Mode: `{case.mode}`",
        f"- State: `{case.state}`",
        f"- Overall readiness: `{readiness(case)}`",
        f"- Overall risk: `{case.overall_risk_level}`",
        f"- Base commit: `{case.base_commit}`",
        f"- Contribution fingerprint: `{case.contribution_fingerprint}`",
        f"- Policy fingerprint: `{case.policy_snapshot.policy_fingerprint}`",
        "",
        "## Matched Risk Areas",
        "",
        "| Risk area | Levels | Rules | Affected paths |",
        "| --- | --- | --- | --- |",
    ]
    for zone, values in sorted(zones.items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_cell(zone),
                    markdown_cell(", ".join(sorted(values["risk_levels"]))),
                    markdown_cell(", ".join(sorted(values["rules"]))),
                    markdown_cell(", ".join(sorted(values["paths"]))),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Compiled Obligations",
            "",
            "| Obligation | Source rules | Reference | Observed | Status | Blocking |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for obligation in case.obligations:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_cell(obligation.obligation_id),
                    markdown_cell(", ".join(obligation.source_rule_ids)),
                    markdown_cell(obligation.description),
                    markdown_cell(
                        obligation_observation(case, obligation.obligation_id)
                    ),
                    markdown_cell(obligation.status),
                    "yes" if obligation.blocking else "no",
                ]
            )
            + " |"
        )

    lines.extend(["", "## Findings and Repair", ""])
    if case.findings:
        for finding in case.findings:
            lines.append(
                f"- `{finding.status}` `{finding.code}`: {finding.message}"
            )
    else:
        lines.append("- No findings recorded.")
    if case.repair_requests:
        lines.extend(["", "Repair history:"])
        for request in case.repair_requests:
            lines.append(
                f"- `{request.id}` `{request.status}`: "
                f"{request.requested_correction}"
            )

    lines.extend(["", "## Human Attestations", ""])
    if case.attestations:
        for item in case.attestations:
            lines.append(
                f"- `{item.status}` by `{item.actor}` at `{item.timestamp}`; "
                f"scope: {', '.join(item.reviewed_scope)}"
            )
    else:
        lines.append("- No human attestation event recorded.")

    if audience == "maintainer":
        lines.extend(
            [
                "",
                "## Applicable Policy Snapshot",
                "",
                f"- Schema: `{case.policy_snapshot.schema_version}`",
                f"- Manifest: `{case.policy_snapshot.manifest_version}`",
                f"- Resolved at: `{case.policy_snapshot.resolved_at}`",
                "",
                "## Transition History",
                "",
            ]
        )
        for item in transitions:
            lines.append(
                f"- `{item.timestamp}` `{item.source_state}` → "
                f"`{item.target_state}` via `{item.action}` by "
                f"`{item.actor}` (`{item.role}`): {item.reason}"
            )

    lines.extend(["", "## Authority Boundary", "", AUTHORITY_NOTICE, ""])
    return "\n".join(lines)


def _html_list(items: list[str], empty: str) -> str:
    if not items:
        return f"<p>{html.escape(empty)}</p>"
    return "<ul>" + "".join(
        f"<li>{html.escape(item)}</li>" for item in items
    ) + "</ul>"


def render_html(
    case: GovernanceCase,
    transitions: list[StateTransition],
    *,
    audience: str,
    action_token: str | None = None,
    config: VNextConfig | None = None,
    current_actor: ActorContext | None = None,
    preview: ActionPreview | None = None,
    form_values: dict[str, list[str]] | None = None,
) -> str:
    if audience == "maintainer" and config is not None:
        from .guidance import ActorContext, build_reviewer_guidance
        from .guidance.presenters import render_guidance_html
        from .migration import check_migration

        actor = current_actor or ActorContext(
            actor="maintainer-reviewer",
            role="maintainer",
        )
        return render_guidance_html(
            build_reviewer_guidance(
                case,
                config,
                transitions,
                actor,
                migration_diagnostic=check_migration(case, config),
            ),
            action_token=action_token,
            preview=preview,
            form_values=form_values,
        )
    title = (
        "AGM Contributor Governance Panel"
        if audience == "contributor"
        else "AGM Maintainer Governance Report"
    )
    rows = []
    for obligation in case.obligations:
        rows.append(
            "<tr>"
            f"<td>{html.escape(obligation.obligation_id)}</td>"
            f"<td>{html.escape(', '.join(obligation.source_rule_ids))}</td>"
            f"<td>{html.escape(obligation.description)}</td>"
            f"<td>{html.escape(obligation_observation(case, obligation.obligation_id))}</td>"
            f"<td><span class=\"status\">{html.escape(obligation.status)}</span></td>"
            f"<td>{'yes' if obligation.blocking else 'no'}</td>"
            "</tr>"
        )
    findings = [
        f"{item.status} {item.code}: {item.message}" for item in case.findings
    ]
    attestations = [
        f"{item.status} by {item.actor} at {item.timestamp}; scope: "
        f"{', '.join(item.reviewed_scope)}"
        for item in case.attestations
    ]
    transitions_html = ""
    if audience == "maintainer":
        transitions_html = (
            "<section><h2>Transition history</h2>"
            + _html_list(
                [
                    f"{item.timestamp} {item.source_state} → {item.target_state} "
                    f"via {item.action} by {item.actor} ({item.role}): {item.reason}"
                    for item in transitions
                ],
                "No transitions recorded.",
            )
            + "</section>"
        )
    actions_html = render_action_forms(
        case, audience=audience, action_token=action_token
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — {html.escape(case.id)}</title>
<style>
:root {{ color-scheme: light; font-family: system-ui, sans-serif; }}
body {{ margin: 0; background: #f4f7fb; color: #172033; }}
main {{ max-width: 1180px; margin: 0 auto; padding: 2rem; }}
.hero, section {{ background: white; border: 1px solid #d8e0ea; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; }}
.hero {{ border-left: 6px solid #3157a4; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: .75rem; }}
.metric {{ background: #eef3fa; border-radius: 8px; padding: .75rem; overflow-wrap: anywhere; }}
table {{ width: 100%; border-collapse: collapse; font-size: .92rem; }}
th, td {{ border-bottom: 1px solid #d8e0ea; padding: .65rem; text-align: left; vertical-align: top; }}
th {{ background: #eef3fa; }}
.status {{ font-weight: 700; }}
.notice {{ border-left: 6px solid #9b6a00; }}
label {{ display: block; margin-top: .7rem; font-weight: 600; }}
input, textarea, select {{ box-sizing: border-box; width: 100%; padding: .55rem; }}
button {{ margin-top: .8rem; padding: .6rem .9rem; cursor: pointer; }}
code {{ overflow-wrap: anywhere; }}
</style>
</head>
<body><main>
<header class="hero">
<h1>{html.escape(title)}</h1>
<div class="grid">
<div class="metric"><strong>Case</strong><br>{html.escape(case.id)}</div>
<div class="metric"><strong>State</strong><br>{html.escape(case.state)}</div>
<div class="metric"><strong>Readiness</strong><br>{html.escape(readiness(case))}</div>
<div class="metric"><strong>Risk</strong><br>{html.escape(case.overall_risk_level)}</div>
</div>
<p><strong>Contribution fingerprint</strong><br><code>{html.escape(case.contribution_fingerprint)}</code></p>
<p><strong>Policy fingerprint</strong><br><code>{html.escape(case.policy_snapshot.policy_fingerprint)}</code></p>
</header>
<section><h2>Obligation reference vs observed</h2>
<table><thead><tr><th>Obligation</th><th>Sources</th><th>Reference</th><th>Observed</th><th>Status</th><th>Blocking</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></section>
<section><h2>Findings and repair</h2>{_html_list(findings, "No findings recorded.")}</section>
<section><h2>Human attestations</h2>{_html_list(attestations, "No human attestation event recorded.")}</section>
{transitions_html}
{actions_html}
<section class="notice"><h2>Authority boundary</h2><p>{html.escape(AUTHORITY_NOTICE)}</p></section>
</main></body></html>"""


def render_action_forms(
    case: GovernanceCase,
    *,
    audience: str,
    action_token: str | None,
) -> str:
    if not action_token:
        return ""
    token = html.escape(action_token, quote=True)
    if audience == "contributor":
        return f"""
<section><h2>Explicit human attestation operation</h2>
<p>An agent may prepare this form but cannot submit an accountable-human attestation.</p>
<form method="post">
<input type="hidden" name="action_token" value="{token}">
<label>Action<select name="action"><option value="confirm_attestation">Confirm reviewed scope</option><option value="request_correction">Request correction</option><option value="decline_attestation">Decline to attest</option></select></label>
<label>Human actor<input name="actor" required></label>
<label>Reviewed scope (one repository-relative item per line)<textarea name="scope" required>{html.escape(chr(10).join(case.changed_files))}</textarea></label>
<label>Statement or correction reason<textarea name="statement" required></textarea></label>
<label>Reservations<textarea name="reservations"></textarea></label>
<button type="submit">Record explicit operation</button>
</form></section>"""
    obligation_options = "".join(
        f'<option value="{html.escape(item.obligation_id, quote=True)}">'
        f"{html.escape(item.obligation_id)}</option>"
        for item in case.obligations
    )
    return f"""
<section><h2>Authorized maintainer operation</h2>
<form method="post">
<input type="hidden" name="action_token" value="{token}">
<label>Action<select name="action"><option value="verify_evidence">Verify evidence</option><option value="reject_evidence">Reject evidence</option><option value="request_repair">Request repair</option><option value="ask_clarification">Ask for clarification</option><option value="invalidate_attestation">Invalidate attestation</option><option value="record_policy_conflict">Record policy conflict</option><option value="resolve_policy_conflict">Resolve policy conflict</option><option value="authorized_override">Authorized override</option><option value="decide_accept">Final accept</option><option value="decide_reject">Final reject</option><option value="decide_request_changes">Final request changes</option><option value="decide_close">Close without merge</option></select></label>
<label>Maintainer actor<input name="actor" required></label>
<label>Role<select name="role"><option value="maintainer_verifier">maintainer_verifier</option><option value="policy_steward">policy_steward</option><option value="maintainer">maintainer</option></select></label>
<label>Affected obligation<select name="obligation">{obligation_options}</select></label>
<label>Evidence, attestation, or finding ID (when required)<input name="object_id"></label>
<label>Reason<textarea name="reason" required></textarea></label>
<button type="submit">Record authorized operation</button>
</form></section>"""
