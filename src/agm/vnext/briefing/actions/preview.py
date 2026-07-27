"""Side-effect-free plans plus short-lived, one-time preview tokens."""

from __future__ import annotations

import secrets
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from ...guidance import ActorContext
from ...models import VNextError, fingerprint
from ...service import GovernanceService
from .binding import actor_from_context, draft_fingerprint
from .compiler import (
    compile_contextual_actions,
    compile_final_decision_view,
)
from .draft import ReviewDraftStore, normalize_reason
from .models import (
    ExistingOperationPlan,
    FinalDecisionPreview,
    ReviewDecisionDraft,
    ReviewSubmissionPreview,
    StoredPreviewToken,
)


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class PreviewTokenRegistry:
    """In-memory server-session registry; tokens never enter static outputs."""

    def __init__(
        self,
        *,
        ttl_seconds: int = 300,
        clock: Callable[[], datetime] | None = None,
        token_factory: Callable[[], str] | None = None,
    ):
        if ttl_seconds <= 0:
            raise ValueError("Preview token TTL must be positive")
        self.ttl_seconds = ttl_seconds
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.token_factory = token_factory or (
            lambda: secrets.token_urlsafe(32)
        )
        self._tokens: dict[str, StoredPreviewToken] = {}

    def issue(
        self,
        *,
        kind: str,
        case_id: str,
        actor_id: str,
        role: str,
        preview_fingerprint: str,
        payload: dict[str, Any],
    ) -> StoredPreviewToken:
        now = self.clock().astimezone(timezone.utc)
        token = self.token_factory()
        if token in self._tokens:
            raise VNextError("Preview token collision")
        item = StoredPreviewToken(
            token=token,
            kind=kind,
            case_id=case_id,
            actor_id=actor_id,
            role=role,
            preview_fingerprint=preview_fingerprint,
            payload=payload,
            issued_at=_format_timestamp(now),
            expires_at=_format_timestamp(
                now + timedelta(seconds=self.ttl_seconds)
            ),
        )
        self._tokens[token] = item
        return item

    def consume(
        self,
        token: str | None,
        *,
        kind: str,
        case_id: str,
        actor_id: str,
        role: str,
    ) -> StoredPreviewToken:
        if not token or token not in self._tokens:
            raise VNextError("缺少有效的 preview token。")
        item = self._tokens[token]
        if item.used:
            raise VNextError("Preview token 已使用，重放请求被拒绝。")
        if (
            item.kind != kind
            or item.case_id != case_id
            or item.actor_id != actor_id
            or item.role != role
        ):
            item.used = True
            raise VNextError("Preview token 的 actor、role 或 case 绑定不匹配。")
        if self.clock().astimezone(timezone.utc) >= _parse_timestamp(
            item.expires_at
        ):
            item.used = True
            raise VNextError("Preview token 已过期。")
        item.used = True
        return item


def _decision_reason(
    title: str,
    option_label: str,
    reason: str | None,
) -> str:
    suffix = f"原因：{reason}" if reason else "未附加备注。"
    return f"{title}：{option_label}。{suffix}"


def _build_review_preview(
    *,
    service: GovernanceService,
    actor: ActorContext,
    draft: ReviewDecisionDraft,
    token_registry: PreviewTokenRegistry | None,
    issue_token: bool,
) -> ReviewSubmissionPreview:
    case = service.storage.load_case(draft.case_id)
    brief = service.review_brief(
        draft.case_id,
        actor=actor.actor,
        role=actor.role,
    )
    action_view = compile_contextual_actions(
        review_brief=brief,
        governance_case=case,
        actor_context=actor,
        policy_config=service.config,
        live_actions_enabled=True,
    )
    store = ReviewDraftStore(service.storage)
    assessment = store.assess(
        draft=draft,
        case=case,
        action_view=action_view,
    )
    if assessment.stale:
        raise VNextError(
            "Review draft 已失效：" + "；".join(assessment.reasons)
        )
    if not assessment.complete:
        raise VNextError(
            "请先完成所有必需判断，再预览本次处理。"
        )
    if (
        case.policy_snapshot.policy_fingerprint
        != draft.policy_snapshot_fingerprint
    ):
        raise VNextError("Policy snapshot binding 已变化。")
    item_map = {item.judgment_id: item for item in action_view.items}
    sufficient = []
    supplement = []
    material_risk = []
    reason_lines = []
    for decision in draft.judgment_decisions:
        item = item_map[decision.judgment_id]
        option = next(
            option
            for option in item.options
            if option.option_id == decision.selected_option_id
        )
        if not option.authorized:
            raise VNextError(
                option.unavailable_reason or "判断结果已不可执行。"
            )
        target = {
            "sufficient": sufficient,
            "supplement": supplement,
            "material-risk": material_risk,
        }[option.option_id]
        target.append((decision, item, option))
        reason_lines.append(
            _decision_reason(
                item.display_title,
                option.display_label,
                decision.reason,
            )
        )
    plans = []
    affected = tuple(
        sorted(
            {
                requirement
                for decision, _, _ in supplement + material_risk
                for requirement in decision.requirement_refs
            }
        )
    )
    requirement_to_obligation = {
        requirement.requirement_key: obligation.obligation_id
        for requirement, obligation in zip(
            brief.requirements.items,
            case.obligations,
            strict=True,
        )
    }
    affected_obligations = tuple(
        sorted(requirement_to_obligation[item] for item in affected)
    )
    if supplement or material_risk:
        independent_risk = bool(material_risk) and any(
            item.obligation_id == "O-INDEPENDENT-REVIEW"
            for item in case.obligations
        )
        plans.append(
            ExistingOperationPlan(
                operation="request_repair",
                consequence_type=(
                    "material_risk"
                    if material_risk
                    else "supplement"
                ),
                obligation_ids=affected_obligations,
                judgment_ids=tuple(
                    item.judgment_id
                    for _, item, _ in supplement + material_risk
                ),
                reason=" ".join(reason_lines),
                responsible_role=(
                    "maintainer" if independent_risk else "contributor"
                ),
            )
        )
    else:
        verified_obligations = tuple(
            sorted(
                {
                    requirement_to_obligation[ref]
                    for decision, _, _ in sufficient
                    for ref in decision.requirement_refs
                }
            )
        )
        plans.append(
            ExistingOperationPlan(
                operation="verify_evidence",
                consequence_type="sufficient",
                obligation_ids=verified_obligations,
                judgment_ids=tuple(
                    item.judgment_id for _, item, _ in sufficient
                ),
                reason=(
                    "逐项维护者检查已完成；检查不代表接受贡献。 "
                    + " ".join(reason_lines)
                ),
            )
        )
    affected_set = set(affected_obligations)
    retained_evidence = [
        evidence
        for evidence in case.evidence
        if evidence.validity_state in {"valid", "verified"}
        and not (set(evidence.obligation_ids) & affected_set)
    ]
    summaries = []
    if sufficient:
        if supplement or material_risk:
            summaries.append(
                f"记录 {len(sufficient)} 项“材料充分”选择；"
                "因本批仍包含阻断处理，本次不伪造 verification transition。"
            )
        else:
            summaries.append(
                f"确认 {len(sufficient)} 项材料已完成维护者检查。"
            )
    if supplement:
        summaries.append(
            f"针对 {len(supplement)} 项判断生成贡献侧 scoped 补充请求。"
        )
    if material_risk:
        summaries.append(
            f"针对 {len(material_risk)} 项判断创建既有 blocking repair/finding 机制；"
            "不会自动拒绝贡献。"
        )
    summaries.extend(
        [
            f"保留其他 {len(retained_evidence)} 份未受影响且有效的材料。",
            "当前不会接受或拒绝该贡献。",
        ]
    )
    if affected:
        summaries.append("补充完成后，仅重新检查受影响项目。")
    binding_payload = {
        "case_id": case.id,
        "draft_id": draft.draft_id,
        "actor": asdict(actor),
        "case_state": case.state,
        "contribution_fingerprint": case.contribution_fingerprint,
        "policy_snapshot_fingerprint": (
            case.policy_snapshot.policy_fingerprint
        ),
        "draft_fingerprint": draft_fingerprint(draft),
        "plans": [item.to_dict() for item in plans],
    }
    preview_fingerprint = fingerprint(binding_payload)
    issued = None
    if issue_token:
        if token_registry is None:
            raise VNextError("Live preview requires a token registry.")
        issued = token_registry.issue(
            kind="review",
            case_id=case.id,
            actor_id=actor.actor,
            role=actor.role,
            preview_fingerprint=preview_fingerprint,
            payload=binding_payload,
        )
    return ReviewSubmissionPreview(
        case_id=case.id,
        actor_id=actor.actor,
        role=actor.role,
        draft_id=draft.draft_id,
        authorized=True,
        unavailable_reason=None,
        summary_lines=tuple(summaries),
        operation_plans=tuple(plans),
        retained_evidence_count=len(retained_evidence),
        affected_requirement_refs=affected,
        contribution_fingerprint=case.contribution_fingerprint,
        policy_snapshot_fingerprint=(
            case.policy_snapshot.policy_fingerprint
        ),
        case_state=case.state,
        preview_fingerprint=preview_fingerprint,
        preview_token=issued.token if issued else None,
        expires_at=issued.expires_at if issued else None,
    )


def preview_review_submission(
    *,
    service: GovernanceService,
    actor_context: object,
    review_draft: ReviewDecisionDraft,
    token_registry: PreviewTokenRegistry | None = None,
    issue_token: bool = True,
) -> ReviewSubmissionPreview:
    """Recompile current work and produce a case/actor-bound preview."""

    actor = actor_from_context(actor_context)
    return _build_review_preview(
        service=service,
        actor=actor,
        draft=review_draft,
        token_registry=token_registry,
        issue_token=issue_token,
    )


def preview_final_decision(
    *,
    service: GovernanceService,
    actor_context: object,
    case_id: str,
    decision_id: str,
    reason: str,
    token_registry: PreviewTokenRegistry | None = None,
    issue_token: bool = True,
) -> FinalDecisionPreview:
    """Preview one final decision independently from maintainer review."""

    actor = actor_from_context(actor_context)
    case = service.storage.load_case(case_id)
    brief = service.review_brief(
        case_id,
        actor=actor.actor,
        role=actor.role,
    )
    view = compile_final_decision_view(
        review_brief=brief,
        governance_case=case,
        actor_context=actor,
        policy_config=service.config,
    )
    option = next(
        (
            item
            for item in view.options
            if item.decision_id == decision_id
        ),
        None,
    )
    if option is None:
        raise VNextError("未知的最终决定结果。")
    if not option.authorized:
        raise VNextError(
            option.unavailable_reason or "当前最终决定不可用。"
        )
    normalized_reason = normalize_reason(reason, required=True)
    assert normalized_reason is not None
    payload = {
        "case_id": case.id,
        "actor": asdict(actor),
        "decision_id": decision_id,
        "operation": option.existing_operation_ref,
        "reason": normalized_reason,
        "case_state": case.state,
        "contribution_fingerprint": case.contribution_fingerprint,
        "policy_snapshot_fingerprint": (
            case.policy_snapshot.policy_fingerprint
        ),
    }
    preview_fingerprint = fingerprint(payload)
    issued = None
    if issue_token:
        if token_registry is None:
            raise VNextError("Live preview requires a token registry.")
        issued = token_registry.issue(
            kind="final",
            case_id=case.id,
            actor_id=actor.actor,
            role=actor.role,
            preview_fingerprint=preview_fingerprint,
            payload=payload,
        )
    return FinalDecisionPreview(
        case_id=case.id,
        actor_id=actor.actor,
        role=actor.role,
        decision_id=decision_id,
        display_label=option.display_label,
        reason=normalized_reason,
        summary_lines=(
            f"将执行独立的“{option.display_label}”最终决定。",
            option.plain_consequence,
            "该操作与维护者 verification 分开记录。",
        ),
        contribution_fingerprint=case.contribution_fingerprint,
        policy_snapshot_fingerprint=(
            case.policy_snapshot.policy_fingerprint
        ),
        case_state=case.state,
        preview_fingerprint=preview_fingerprint,
        preview_token=issued.token if issued else None,
        expires_at=issued.expires_at if issued else None,
        authorized=True,
        unavailable_reason=None,
    )


__all__ = [
    "PreviewTokenRegistry",
    "preview_final_decision",
    "preview_review_submission",
    "_build_review_preview",
]
