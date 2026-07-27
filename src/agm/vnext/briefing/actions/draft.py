"""Actor-bound review drafts stored outside canonical governance policy."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from ...models import GovernanceCase, VNextError, new_id, utc_now
from ...storage import CaseStorage, atomic_write_text
from .models import (
    DraftAssessment,
    JudgmentDecision,
    ReviewActionView,
    ReviewDecisionDraft,
)


MAX_REASON_LENGTH = 2000


def normalize_reason(
    value: object,
    *,
    required: bool,
) -> str | None:
    reason = str(value or "").strip()
    if required and not reason:
        raise VNextError("所选判断结果必须填写简短原因。")
    if len(reason) > MAX_REASON_LENGTH:
        raise VNextError(
            f"原因不得超过 {MAX_REASON_LENGTH} 个字符。"
        )
    return reason or None


def _draft_from_dict(payload: Mapping[str, Any]) -> ReviewDecisionDraft:
    decisions = tuple(
        JudgmentDecision(
            judgment_id=str(item["judgment_id"]),
            selected_option_id=str(item["selected_option_id"]),
            reason=(
                str(item["reason"]) if item.get("reason") is not None else None
            ),
            requirement_refs=tuple(item.get("requirement_refs", ())),
            provenance_refs=tuple(item.get("provenance_refs", ())),
        )
        for item in payload.get("judgment_decisions", ())
    )
    return ReviewDecisionDraft(
        draft_id=str(payload["draft_id"]),
        case_id=str(payload["case_id"]),
        actor_id=str(payload["actor_id"]),
        role=str(payload["role"]),
        contribution_fingerprint=str(
            payload["contribution_fingerprint"]
        ),
        policy_snapshot_fingerprint=str(
            payload["policy_snapshot_fingerprint"]
        ),
        judgment_decisions=decisions,
        created_at=str(payload["created_at"]),
        updated_at=str(payload["updated_at"]),
        status=str(payload.get("status", "draft")),
    )


class ReviewDraftStore:
    """Persist one active draft per actor/role/case in ``.agm-work``."""

    def __init__(self, storage: CaseStorage):
        self.storage = storage

    def _actor_key(self, actor_id: str, role: str) -> str:
        return hashlib.sha256(
            f"{actor_id}\0{role}".encode("utf-8")
        ).hexdigest()

    def _draft_root(self, case_id: str) -> Path:
        root = self.storage.case_dir(case_id) / "review_drafts"
        root.mkdir(parents=True, exist_ok=True)
        return root

    def _active_path(
        self,
        case_id: str,
        actor_id: str,
        role: str,
    ) -> Path:
        return (
            self._draft_root(case_id)
            / f"{self._actor_key(actor_id, role)}.json"
        )

    def save(
        self,
        *,
        action_view: ReviewActionView,
        selections: Mapping[str, Mapping[str, object]],
    ) -> ReviewDecisionDraft:
        if not action_view.can_save_draft:
            raise VNextError(
                action_view.unavailable_reason
                or "当前交互视图不允许保存 review draft。"
            )
        item_map = {item.judgment_id: item for item in action_view.items}
        unknown = sorted(set(selections) - set(item_map))
        if unknown:
            raise VNextError("草稿包含当前页面不存在的判断项。")
        decisions = []
        for judgment_id, supplied in selections.items():
            item = item_map[judgment_id]
            option_id = str(supplied.get("option_id", ""))
            option = next(
                (
                    candidate
                    for candidate in item.options
                    if candidate.option_id == option_id
                ),
                None,
            )
            if option is None:
                raise VNextError("草稿包含未知的判断结果。")
            if not option.authorized:
                raise VNextError(
                    option.unavailable_reason or "当前结果不可用。"
                )
            reason = normalize_reason(
                supplied.get("reason"),
                required=option.requires_reason,
            )
            decisions.append(
                JudgmentDecision(
                    judgment_id=judgment_id,
                    selected_option_id=option.option_id,
                    reason=reason,
                    requirement_refs=item.requirement_refs,
                    provenance_refs=item.provenance_refs,
                )
            )
        existing = self.restore(
            case_id=action_view.case_id,
            actor_id=action_view.actor_id,
            role=action_view.role,
        )
        now = utc_now()
        draft = ReviewDecisionDraft(
            draft_id=(
                existing.draft_id if existing else new_id("review-draft")
            ),
            case_id=action_view.case_id,
            actor_id=action_view.actor_id,
            role=action_view.role,
            contribution_fingerprint=(
                action_view.contribution_fingerprint
            ),
            policy_snapshot_fingerprint=(
                action_view.policy_snapshot_fingerprint
            ),
            judgment_decisions=tuple(
                sorted(decisions, key=lambda item: item.judgment_id)
            ),
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        path = self._active_path(
            draft.case_id,
            draft.actor_id,
            draft.role,
        )
        atomic_write_text(
            path,
            json.dumps(
                draft.to_dict(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        return draft

    def restore(
        self,
        *,
        case_id: str,
        actor_id: str,
        role: str,
    ) -> ReviewDecisionDraft | None:
        path = self._active_path(case_id, actor_id, role)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise VNextError("无法读取当前 review draft。") from exc
        if not isinstance(payload, dict):
            raise VNextError("Review draft 必须是 JSON object。")
        draft = _draft_from_dict(payload)
        if (
            draft.case_id != case_id
            or draft.actor_id != actor_id
            or draft.role != role
        ):
            raise VNextError("Review draft 的 actor/case/role 绑定不匹配。")
        return draft

    def assess(
        self,
        *,
        draft: ReviewDecisionDraft,
        case: GovernanceCase,
        action_view: ReviewActionView,
    ) -> DraftAssessment:
        reasons = []
        if draft.case_id != case.id:
            reasons.append("案例绑定已变化。")
        if draft.actor_id != action_view.actor_id:
            reasons.append("参与者绑定已变化。")
        if draft.role != action_view.role:
            reasons.append("角色绑定已变化。")
        if (
            draft.contribution_fingerprint
            != case.contribution_fingerprint
        ):
            reasons.append("贡献版本已经变化。")
        if (
            draft.policy_snapshot_fingerprint
            != case.policy_snapshot.policy_fingerprint
        ):
            reasons.append("策略快照已经变化。")
        current = {item.judgment_id: item for item in action_view.items}
        decision_map = {
            item.judgment_id: item for item in draft.judgment_decisions
        }
        changed = []
        for judgment_id, decision in decision_map.items():
            item = current.get(judgment_id)
            if item is None:
                changed.append(judgment_id)
                continue
            if (
                decision.requirement_refs != item.requirement_refs
                or decision.provenance_refs != item.provenance_refs
                or not any(
                    option.option_id == decision.selected_option_id
                    and option.authorized
                    for option in item.options
                )
            ):
                changed.append(judgment_id)
        if changed:
            reasons.append("一项或多项人类判断已消失或发生变化。")
        missing = sorted(set(current) - set(decision_map))
        return DraftAssessment(
            stale=bool(reasons),
            complete=not reasons and not missing and bool(current),
            reasons=tuple(reasons),
            missing_judgment_ids=tuple(missing),
            changed_judgment_ids=tuple(sorted(changed)),
        )

    def abandon(
        self,
        *,
        case_id: str,
        actor_id: str,
        role: str,
    ) -> bool:
        draft = self.restore(
            case_id=case_id,
            actor_id=actor_id,
            role=role,
        )
        if draft is None:
            return False
        self._archive(draft, status="abandoned")
        self._active_path(case_id, actor_id, role).unlink(missing_ok=True)
        return True

    def archive_submitted(
        self,
        draft: ReviewDecisionDraft,
        *,
        submission: Mapping[str, Any],
    ) -> None:
        self._archive(draft, status="submitted", extra=submission)
        self._active_path(
            draft.case_id,
            draft.actor_id,
            draft.role,
        ).unlink(missing_ok=True)
        self._append_jsonl(
            self.storage.case_dir(draft.case_id)
            / "review_submissions.jsonl",
            {
                "schema_version": (
                    "agm.review_submission_audit/v0.2-dev"
                ),
                "append_only": True,
                "draft": draft.to_dict(),
                "submission": dict(submission),
            },
        )

    def record_rejected_attempt(
        self,
        *,
        case_id: str,
        actor_id: str,
        role: str,
        reason: str,
        operation: str,
    ) -> None:
        self._append_jsonl(
            self.storage.case_dir(case_id)
            / "review_action_attempts.jsonl",
            {
                "schema_version": (
                    "agm.review_action_attempt/v0.2-dev"
                ),
                "append_only": True,
                "case_id": case_id,
                "actor_id": actor_id,
                "role": role,
                "operation": operation,
                "result": "denied",
                "state_changed": False,
                "reason": reason,
                "attempted_at": utc_now(),
            },
        )

    def _archive(
        self,
        draft: ReviewDecisionDraft,
        *,
        status: str,
        extra: Mapping[str, Any] | None = None,
    ) -> None:
        archive = self._draft_root(draft.case_id) / "archive"
        archive.mkdir(parents=True, exist_ok=True)
        payload = {
            **draft.to_dict(),
            "status": status,
            "archived_at": utc_now(),
        }
        if extra:
            payload["submission"] = dict(extra)
        archive_name = hashlib.sha256(
            draft.draft_id.encode("utf-8")
        ).hexdigest()
        atomic_write_text(
            archive / f"{archive_name}.json",
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

    @staticmethod
    def _append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(
            dict(payload),
            ensure_ascii=False,
            sort_keys=True,
        ) + "\n"
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
