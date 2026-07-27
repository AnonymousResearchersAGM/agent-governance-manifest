from __future__ import annotations

import http.client
import json
import re
import sys
import threading
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from pathlib import Path
from urllib.parse import urlencode

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from agm.vnext.briefing.actions import (  # noqa: E402
    DraftAssessment,
    PreviewTokenRegistry,
    ReviewDraftStore,
    compile_contextual_actions,
    compile_final_decision_view,
    execute_final_decision,
    execute_review_submission,
    preview_final_decision,
    preview_review_submission,
    render_final_decision_html,
    render_interactive_review_html,
    render_review_preview_html,
)
from agm.vnext.briefing.actions.server import (  # noqa: E402
    _handler_class,
)
from agm.vnext.briefing.models import HumanJudgmentItem  # noqa: E402
from agm.vnext.cli import main  # noqa: E402
from agm.vnext.guidance import ActorContext  # noqa: E402
from agm.vnext.models import VNextError  # noqa: E402
from agm.vnext.runtime import (  # noqa: E402
    DemoExecutionContext,
    use_execution_context,
)
from agm.vnext.service import GovernanceService  # noqa: E402
from generate_reviewer_guidance_demos import (  # noqa: E402
    DEMO_TOKEN_SECRET,
    FIXED_TIME,
    SCENARIOS,
    make_project,
)


BUILDERS = dict(SCENARIOS)
HUMAN = ActorContext(
    actor="independent-human-maintainer",
    role="maintainer",
    human=True,
)


@contextmanager
def demo_service(
    tmp_path: Path,
    scenario: str,
    **builder_kwargs,
):
    with use_execution_context(
        DemoExecutionContext(
            scenario_namespace=f"phase-2-{scenario}",
            fixed_timestamp=FIXED_TIME,
            token_secret=DEMO_TOKEN_SECRET,
        )
    ):
        root = make_project(tmp_path, scenario)
        service = GovernanceService(root)
        built = BUILDERS[scenario](service, **builder_kwargs)
        yield service, built["case_id"]


def action_view(
    service: GovernanceService,
    case_id: str,
    actor: ActorContext = HUMAN,
):
    case = service.storage.load_case(case_id)
    brief = service.review_brief(
        case_id,
        actor=actor.actor,
        role=actor.role,
    )
    return compile_contextual_actions(
        review_brief=brief,
        governance_case=case,
        actor_context=actor,
        policy_config=service.config,
    )


def all_sufficient(view):
    return {
        item.judgment_id: {
            "option_id": "sufficient",
            "reason": "",
        }
        for item in view.items
    }


def make_ready(service, case_id):
    view = action_view(service, case_id)
    store = ReviewDraftStore(service.storage)
    draft = store.save(
        action_view=view,
        selections=all_sufficient(view),
    )
    registry = PreviewTokenRegistry(token_factory=lambda: "ready-token")
    preview = preview_review_submission(
        service=service,
        actor_context=HUMAN,
        review_draft=draft,
        token_registry=registry,
    )
    execute_review_submission(
        service=service,
        actor_context=HUMAN,
        case_id=case_id,
        preview_token=preview.preview_token,
        token_registry=registry,
        draft_store=store,
    )


def test_contextual_actions_exist_only_for_human_judgments(tmp_path):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        view = action_view(service, case_id)
        brief = service.review_brief(
            case_id,
            actor=HUMAN.actor,
            role=HUMAN.role,
        )
        assert len(view.items) == len(brief.human_judgments) == 4
        assert all(len(item.options) == 3 for item in view.items)
        assert all(
            option.plain_consequence
            for item in view.items
            for option in item.options
        )

    with demo_service(
        tmp_path, "05_lightweight_low_risk"
    ) as (service, case_id):
        assert action_view(service, case_id).items == ()


def test_interactive_cli_writes_static_secret_free_artifacts(
    tmp_path,
    capsys,
):
    with demo_service(
        tmp_path, "03_scoped_repair"
    ) as (service, case_id):
        assert (
            main(
                [
                    "--root",
                    str(service.root),
                    "maintainer",
                    "review",
                    "--case",
                    case_id,
                    "--actor",
                    HUMAN.actor,
                    "--role",
                    HUMAN.role,
                ]
            )
            == 0
        )
        output = json.loads(capsys.readouterr().out)
        model = Path(output["review_action_model"]).read_text(
            encoding="utf-8"
        )
        rendered = Path(output["review_interactive_html"]).read_text(
            encoding="utf-8"
        )
        assert '"live_actions_enabled": false' in model
        assert "csrf_token" not in rendered
        assert "preview_token" not in rendered


def test_denied_attempt_and_information_do_not_compile_options(tmp_path):
    with demo_service(
        tmp_path, "04_unauthorized_agent_verification"
    ) as (service, case_id):
        view = action_view(service, case_id)
        assert view.items == ()
        assert len(view.system_handled_anomalies) == 1


def test_noncanonical_judgment_is_filtered(tmp_path):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        case = service.storage.load_case(case_id)
        brief = service.review_brief(
            case_id,
            actor=HUMAN.actor,
            role=HUMAN.role,
        )
        invented = HumanJudgmentItem(
            judgment_id="invented",
            display_title="Invented",
            why_human_is_needed="No canonical source",
            contribution_claim="",
            system_observation="",
            evidence_summary="",
            review_focus=(),
            possible_outcomes=(),
            priority="high",
            blocking=True,
            requirement_refs=("not-canonical",),
            provenance=("compiled_requirement",),
        )
        changed = replace(
            brief,
            human_judgments=brief.human_judgments + (invented,),
        )
        view = compile_contextual_actions(
            review_brief=changed,
            governance_case=case,
            actor_context=HUMAN,
            policy_config=service.config,
        )
        assert all(item.judgment_id != "invented" for item in view.items)


def test_operation_refs_are_technical_not_participant_visible(tmp_path):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        view = action_view(service, case_id)
        assert {
            option.existing_operation_ref
            for option in view.items[0].options
        } == {"verify_evidence", "request_repair"}
        rendered = render_interactive_review_html(
            replace(view, live_actions_enabled=False)
        )
        main = rendered.split("<details>", 1)[0]
        assert "verify_evidence" not in main
        assert "request_repair" not in main
        assert "obligation" not in main.lower()
        assert "transition" not in main.lower()


@pytest.mark.parametrize(
    "actor",
    [
        ActorContext("agent", "contributor_agent", False),
        ActorContext("reviewer-agent", "maintainer", False),
        ActorContext("human-verifier", "maintainer_verifier", True),
    ],
)
def test_independent_judgment_authority_is_server_compiled(
    tmp_path,
    actor,
):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        view = action_view(service, case_id, actor)
        independent = next(
            item
            for item in view.items
            if item.display_title == "独立维护者检查"
        )
        assert not any(option.authorized for option in independent.options)
        assert not view.can_save_draft


def test_scoped_repair_resubmission_enters_maintainer_stage_legally(
    tmp_path,
):
    with demo_service(
        tmp_path, "03_scoped_repair"
    ) as (service, case_id):
        case = service.storage.load_case(case_id)
        transitions = service.storage.read_transitions(case_id)
        view = action_view(service, case_id)

        assert case.state == "awaiting_maintainer_verification"
        assert transitions[-2].action == "resubmit"
        assert transitions[-2].target_state == "resubmitted"
        assert transitions[-1].action == "submit_for_verification"
        assert transitions[-1].source_state == "resubmitted"
        assert transitions[-1].target_state == (
            "awaiting_maintainer_verification"
        )
        assert transitions[-1].actor == "contributor-agent"
        assert transitions[-1].role == "contributor_agent"
        assert view.maintainer_stage_ready
        assert view.current_stage == "awaiting_maintainer_verification"
        assert len(view.items) == 1
        options = {item.option_id: item for item in view.items[0].options}
        assert all(option.authorized for option in options.values())


def test_raw_resubmitted_remains_contribution_side_and_has_no_actions(
    tmp_path,
):
    with demo_service(
        tmp_path,
        "03_scoped_repair",
        submit_for_verification=False,
    ) as (service, case_id):
        before = service.storage.read_transitions(case_id)
        case = service.storage.load_case(case_id)
        view = action_view(service, case_id)

        assert case.state == "resubmitted"
        assert not view.maintainer_stage_ready
        assert view.current_stage == "resubmitted"
        assert view.items == ()
        assert view.current_next_step["display_title"] == (
            "当前无需你操作"
        )
        assert view.current_next_step["responsible_party"] == "贡献侧"
        assert "正在重新编译要求并提交维护者检查" in (
            view.current_next_step["plain_explanation"]
        )
        assert not view.can_save_draft
        assert not view.can_preview

        with pytest.raises(VNextError):
            service.request_repair(
                case_id,
                actor=HUMAN.actor,
                role=HUMAN.role,
                message="Forged maintainer repair request.",
                affected_obligation_ids=["O-AGENT-SCOPE"],
            )
        assert service.storage.load_case(case_id).state == "resubmitted"
        assert service.storage.read_transitions(case_id) == before


def test_draft_roundtrip_binding_and_no_governance_mutation(tmp_path):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        view = action_view(service, case_id)
        before_case = (
            service.storage.case_dir(case_id) / "case.yml"
        ).read_bytes()
        before_transitions = service.storage.read_transitions(case_id)
        store = ReviewDraftStore(service.storage)
        first = view.items[0]
        draft = store.save(
            action_view=view,
            selections={
                first.judgment_id: {
                    "option_id": "supplement",
                    "reason": "需要补充范围说明。",
                }
            },
        )
        restored = store.restore(
            case_id=case_id,
            actor_id=HUMAN.actor,
            role=HUMAN.role,
        )
        assert restored == draft
        assert restored.case_id == case_id
        assert restored.actor_id == HUMAN.actor
        assert restored.role == HUMAN.role
        assert (
            service.storage.case_dir(case_id) / "case.yml"
        ).read_bytes() == before_case
        assert service.storage.read_transitions(case_id) == before_transitions
        assert (
            store.restore(
                case_id=case_id,
                actor_id="other",
                role=HUMAN.role,
            )
            is None
        )


def test_stale_draft_detection_and_abandon(tmp_path):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        view = action_view(service, case_id)
        store = ReviewDraftStore(service.storage)
        draft = store.save(
            action_view=view,
            selections=all_sufficient(view),
        )
        changed_case = service.storage.load_case(case_id)
        changed_case.contribution_fingerprint = "changed"
        assessment = store.assess(
            draft=draft,
            case=changed_case,
            action_view=view,
        )
        assert assessment.stale
        assert "贡献版本已经变化。" in assessment.reasons
        assert store.abandon(
            case_id=case_id,
            actor_id=HUMAN.actor,
            role=HUMAN.role,
        )
        assert (
            store.restore(
                case_id=case_id,
                actor_id=HUMAN.actor,
                role=HUMAN.role,
            )
            is None
        )
        assert service.storage.load_case(case_id).state == (
            "awaiting_maintainer_verification"
        )


def test_reason_validation_is_trimmed_required_and_bounded(tmp_path):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        view = action_view(service, case_id)
        store = ReviewDraftStore(service.storage)
        item = view.items[0]
        with pytest.raises(VNextError, match="必须填写"):
            store.save(
                action_view=view,
                selections={
                    item.judgment_id: {
                        "option_id": "supplement",
                        "reason": "   ",
                    }
                },
            )
        with pytest.raises(VNextError, match="不得超过"):
            store.save(
                action_view=view,
                selections={
                    item.judgment_id: {
                        "option_id": "material-risk",
                        "reason": "x" * 2001,
                    }
                },
            )
        draft = store.save(
            action_view=view,
            selections={
                item.judgment_id: {
                    "option_id": "supplement",
                    "reason": "  concise  ",
                }
            },
        )
        assert draft.judgment_decisions[0].reason == "concise"


def test_preview_is_side_effect_free_and_token_is_bound(tmp_path):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        view = action_view(service, case_id)
        store = ReviewDraftStore(service.storage)
        draft = store.save(
            action_view=view,
            selections=all_sufficient(view),
        )
        case_path = service.storage.case_dir(case_id) / "case.yml"
        before_case = case_path.read_bytes()
        before_transitions = service.storage.read_transitions(case_id)
        registry = PreviewTokenRegistry(token_factory=lambda: "bound-token")
        preview = preview_review_submission(
            service=service,
            actor_context=HUMAN,
            review_draft=draft,
            token_registry=registry,
        )
        assert preview.preview_token == "bound-token"
        assert case_path.read_bytes() == before_case
        assert service.storage.read_transitions(case_id) == before_transitions
        with pytest.raises(VNextError, match="绑定不匹配"):
            registry.consume(
                preview.preview_token,
                kind="review",
                case_id="wrong-case",
                actor_id=HUMAN.actor,
                role=HUMAN.role,
            )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("contribution_fingerprint", "changed", "贡献版本"),
        ("policy_snapshot_fingerprint", "changed", "策略快照"),
    ],
)
def test_preview_rejects_stale_draft_fingerprints(
    tmp_path,
    field,
    value,
    message,
):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        view = action_view(service, case_id)
        draft = ReviewDraftStore(service.storage).save(
            action_view=view,
            selections=all_sufficient(view),
        )
        stale = replace(draft, **{field: value})
        with pytest.raises(VNextError, match=message):
            preview_review_submission(
                service=service,
                actor_context=HUMAN,
                review_draft=stale,
                token_registry=PreviewTokenRegistry(),
            )


def test_preview_rejects_changed_judgment_provenance(tmp_path):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        view = action_view(service, case_id)
        draft = ReviewDraftStore(service.storage).save(
            action_view=view,
            selections=all_sufficient(view),
        )
        decision = replace(
            draft.judgment_decisions[0],
            provenance_refs=("changed",),
        )
        changed = replace(
            draft,
            judgment_decisions=(
                decision,
                *draft.judgment_decisions[1:],
            ),
        )
        with pytest.raises(VNextError, match="判断已消失或发生变化"):
            preview_review_submission(
                service=service,
                actor_context=HUMAN,
                review_draft=changed,
                token_registry=PreviewTokenRegistry(),
            )


def test_expired_and_replayed_preview_tokens_are_rejected():
    now = [datetime(2026, 1, 1, tzinfo=timezone.utc)]
    registry = PreviewTokenRegistry(
        ttl_seconds=2,
        clock=lambda: now[0],
        token_factory=lambda: "expiring-token",
    )
    item = registry.issue(
        kind="review",
        case_id="case",
        actor_id="actor",
        role="maintainer",
        preview_fingerprint="fingerprint",
        payload={},
    )
    now[0] += timedelta(seconds=3)
    with pytest.raises(VNextError, match="已过期"):
        registry.consume(
            item.token,
            kind="review",
            case_id="case",
            actor_id="actor",
            role="maintainer",
        )
    with pytest.raises(VNextError, match="已使用"):
        registry.consume(
            item.token,
            kind="review",
            case_id="case",
            actor_id="actor",
            role="maintainer",
        )


def test_execute_without_preview_is_rejected_and_audited(tmp_path):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        before = service.storage.read_transitions(case_id)
        store = ReviewDraftStore(service.storage)
        with pytest.raises(VNextError, match="没有 preview token"):
            execute_review_submission(
                service=service,
                actor_context=HUMAN,
                case_id=case_id,
                preview_token=None,
                token_registry=PreviewTokenRegistry(),
                draft_store=store,
            )
        assert service.storage.read_transitions(case_id) == before
        audit = (
            service.storage.case_dir(case_id)
            / "review_action_attempts.jsonl"
        ).read_text(encoding="utf-8")
        assert '"result": "denied"' in audit
        assert '"state_changed": false' in audit


def test_execute_sufficient_uses_existing_verification_and_is_replay_safe(
    tmp_path,
):
    with demo_service(
        tmp_path, "03_scoped_repair"
    ) as (service, case_id):
        view = action_view(service, case_id)
        store = ReviewDraftStore(service.storage)
        draft = store.save(
            action_view=view,
            selections=all_sufficient(view),
        )
        registry = PreviewTokenRegistry(token_factory=lambda: "execute-token")
        preview = preview_review_submission(
            service=service,
            actor_context=HUMAN,
            review_draft=draft,
            token_registry=registry,
        )
        before = service.storage.read_transitions(case_id)
        verification_count = len(
            service.storage.load_case(case_id).maintainer_verifications
        )
        result = execute_review_submission(
            service=service,
            actor_context=HUMAN,
            case_id=case_id,
            preview_token=preview.preview_token,
            token_registry=registry,
            draft_store=store,
        )
        case = service.storage.load_case(case_id)
        after = service.storage.read_transitions(case_id)
        assert result.message == "你的维护者检查已提交"
        assert case.state == "ready_for_human_decision"
        assert len(case.maintainer_verifications) == (
            verification_count + 1
        )
        assert [item.action for item in after[len(before):]] == [
            "verify_evidence",
            "mark_ready",
        ]
        count = len(after)
        with pytest.raises(VNextError, match="已使用"):
            execute_review_submission(
                service=service,
                actor_context=HUMAN,
                case_id=case_id,
                preview_token=preview.preview_token,
                token_registry=registry,
                draft_store=store,
            )
        assert len(service.storage.read_transitions(case_id)) == count
        rejected = (
            service.storage.case_dir(case_id)
            / "review_action_attempts.jsonl"
        ).read_text(encoding="utf-8")
        assert "重放请求被拒绝" in rejected


@pytest.mark.parametrize(
    (
        "option_id",
        "reason",
        "expected_operation",
        "expected_state",
        "preview_phrases",
    ),
    [
        (
            "sufficient",
            "",
            "verify_evidence",
            "ready_for_human_decision",
            (
                "完成“智能体行动与委派说明”的维护者检查",
                "将案例推进到等待最终人类决定",
                "不会自动接受贡献",
            ),
        ),
        (
            "supplement",
            "需要补充具体的委派边界。",
            "request_repair",
            "repair_requested",
            (
                "生成补充请求",
                "将处理责任交回贡献侧",
                "修复完成后仅重新检查这一项",
                "不会拒绝整个贡献",
            ),
        ),
        (
            "material-risk",
            "发现未受约束的委派路径，需要阻断处理。",
            "request_repair",
            "repair_requested",
            (
                "标记为阻断性风险",
                "阻止案例进入最终决定",
                "不会自动作出最终拒绝决定",
            ),
        ),
    ],
)
def test_scoped_repair_three_options_preview_and_execute(
    tmp_path,
    option_id,
    reason,
    expected_operation,
    expected_state,
    preview_phrases,
):
    with demo_service(
        tmp_path, "03_scoped_repair"
    ) as (service, case_id):
        view = action_view(service, case_id)
        target = view.items[0]
        before_case = service.storage.load_case(case_id)
        unaffected = {
            evidence.id
            for evidence in before_case.evidence
            if "O-AGENT-SCOPE" not in evidence.obligation_ids
            and evidence.validity_state in {"valid", "verified"}
        }
        before_transitions = service.storage.read_transitions(case_id)
        case_path = service.storage.case_dir(case_id) / "case.yml"
        before_bytes = case_path.read_bytes()
        store = ReviewDraftStore(service.storage)
        draft = store.save(
            action_view=view,
            selections={
                target.judgment_id: {
                    "option_id": option_id,
                    "reason": reason,
                }
            },
        )
        registry = PreviewTokenRegistry(
            token_factory=lambda: f"scenario-3-{option_id}"
        )
        preview = preview_review_submission(
            service=service,
            actor_context=HUMAN,
            review_draft=draft,
            token_registry=registry,
        )

        assert case_path.read_bytes() == before_bytes
        assert service.storage.read_transitions(case_id) == (
            before_transitions
        )
        assert preview.operation_plans[0].operation == expected_operation
        summary = " ".join(preview.summary_lines)
        for phrase in preview_phrases:
            assert phrase in summary

        execute_review_submission(
            service=service,
            actor_context=HUMAN,
            case_id=case_id,
            preview_token=preview.preview_token,
            token_registry=registry,
            draft_store=store,
        )
        case = service.storage.load_case(case_id)
        appended = service.storage.read_transitions(case_id)[
            len(before_transitions):
        ]
        assert case.state == expected_state
        assert case.final_decision is None
        assert case.state not in {"accepted", "closed", "rejected"}
        assert appended[0].action == expected_operation
        assert {
            evidence.id
            for evidence in case.evidence
            if evidence.validity_state in {"valid", "verified"}
        } >= unaffected

        if option_id == "sufficient":
            assert [item.action for item in appended] == [
                "verify_evidence",
                "mark_ready",
            ]
        else:
            repair = case.repair_requests[-1]
            finding = case.findings[-1]
            assert repair.affected_obligation_ids == ["O-AGENT-SCOPE"]
            assert finding.affected_obligation_ids == ["O-AGENT-SCOPE"]
            assert finding.blocking
            assert finding.severity == "high"
            assert reason in finding.message
            audit = (
                service.storage.case_dir(case_id)
                / "review_submissions.jsonl"
            ).read_text(encoding="utf-8")
            assert f'"selected_option_id": "{option_id}"' in audit


def test_supplement_routes_scoped_repair_and_preserves_other_evidence(
    tmp_path,
):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        view = action_view(service, case_id)
        target = view.items[0]
        selections = all_sufficient(view)
        selections[target.judgment_id] = {
            "option_id": "supplement",
            "reason": "独立检查范围说明不足。",
        }
        before = service.storage.load_case(case_id)
        unaffected = {
            evidence.id
            for evidence in before.evidence
            if not (
                set(evidence.obligation_ids)
                & {
                    before.obligation(
                        "O-INDEPENDENT-REVIEW"
                    ).obligation_id
                }
            )
        }
        store = ReviewDraftStore(service.storage)
        draft = store.save(action_view=view, selections=selections)
        registry = PreviewTokenRegistry(token_factory=lambda: "repair-token")
        preview = preview_review_submission(
            service=service,
            actor_context=HUMAN,
            review_draft=draft,
            token_registry=registry,
        )
        assert [plan.operation for plan in preview.operation_plans] == [
            "request_repair"
        ]
        assert "本次不会完成这些检查" in " ".join(
            preview.summary_lines
        )
        execute_review_submission(
            service=service,
            actor_context=HUMAN,
            case_id=case_id,
            preview_token=preview.preview_token,
            token_registry=registry,
            draft_store=store,
        )
        case = service.storage.load_case(case_id)
        assert case.state == "repair_requested"
        assert case.maintainer_verifications == []
        assert case.repair_requests[-1].affected_obligation_ids == [
            "O-INDEPENDENT-REVIEW"
        ]
        assert {
            evidence.id
            for evidence in case.evidence
            if evidence.validity_state in {"valid", "verified"}
        } >= unaffected
        audit = (
            service.storage.case_dir(case_id)
            / "review_submissions.jsonl"
        ).read_text(encoding="utf-8")
        assert "supplement" in audit
        assert "sufficient" in audit


def test_material_risk_uses_blocking_repair_not_final_rejection(tmp_path):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        view = action_view(service, case_id)
        target = view.items[-1]
        selections = all_sufficient(view)
        selections[target.judgment_id] = {
            "option_id": "material-risk",
            "reason": "发现需要阻断并独立复核的实质风险。",
        }
        store = ReviewDraftStore(service.storage)
        draft = store.save(action_view=view, selections=selections)
        registry = PreviewTokenRegistry(token_factory=lambda: "risk-token")
        preview = preview_review_submission(
            service=service,
            actor_context=HUMAN,
            review_draft=draft,
            token_registry=registry,
        )
        assert preview.operation_plans[0].responsible_role == "maintainer"
        execute_review_submission(
            service=service,
            actor_context=HUMAN,
            case_id=case_id,
            preview_token=preview.preview_token,
            token_registry=registry,
            draft_store=store,
        )
        case = service.storage.load_case(case_id)
        assert case.state == "repair_requested"
        assert case.final_decision is None
        assert case.findings[-1].blocking
        assert case.findings[-1].status == "open"


def test_review_and_final_decision_are_separate(tmp_path):
    with demo_service(
        tmp_path, "03_scoped_repair"
    ) as (service, case_id):
        make_ready(service, case_id)
        case = service.storage.load_case(case_id)
        brief = service.review_brief(
            case_id,
            actor=HUMAN.actor,
            role=HUMAN.role,
        )
        review = action_view(service, case_id)
        review_html = render_interactive_review_html(review)
        main = review_html.split("<details>", 1)[0]
        assert review.items == ()
        assert "进入最终决定" in main
        assert ">接受贡献<" not in main
        assert ">拒绝贡献<" not in main
        assert ">关闭案例<" not in main
        final = compile_final_decision_view(
            review_brief=brief,
            governance_case=case,
            actor_context=HUMAN,
            policy_config=service.config,
        )
        assert final.available
        assert {item.decision_id for item in final.options} == {
            "accept",
            "reject",
            "request_changes",
            "close",
        }
        final_html = render_final_decision_html(
            final,
            csrf_token="csrf",
        )
        assert "最终人类决定" in final_html
        assert "接受本次贡献" in final_html


def test_draft_banner_matches_real_interaction_state(tmp_path):
    with demo_service(
        tmp_path, "03_scoped_repair"
    ) as (service, case_id):
        view = action_view(service, case_id)
        empty = render_interactive_review_html(view)
        assert "尚未选择处理结果" in empty
        assert "你的选择尚未提交" not in empty

        store = ReviewDraftStore(service.storage)
        draft = store.save(
            action_view=view,
            selections=all_sufficient(view),
        )
        selected = render_interactive_review_html(view, draft=draft)
        assert "你的选择尚未提交" in selected

        preview = preview_review_submission(
            service=service,
            actor_context=HUMAN,
            review_draft=draft,
            token_registry=PreviewTokenRegistry(
                token_factory=lambda: "banner-preview"
            ),
        )
        previewed = render_review_preview_html(
            preview,
            csrf_token="csrf",
        )
        assert "预览完成，尚未正式提交" in previewed

        stale = render_interactive_review_html(
            view,
            draft=draft,
            assessment=DraftAssessment(
                stale=True,
                complete=False,
                reasons=("贡献版本已经变化。",),
                missing_judgment_ids=(),
                changed_judgment_ids=(),
            ),
        )
        assert "贡献或规则已经变化，之前的选择已失效" in stale

        submitted = render_interactive_review_html(
            view,
            draft=draft,
            draft_status="submitted",
        )
        assert '<section class="draft-banner' not in submitted
        participant = submitted.split("<details>", 1)[0]
        assert "尚未选择处理结果" not in participant
        assert "你的选择尚未提交" not in participant
        assert "预览完成，尚未正式提交" not in participant


def test_no_task_or_no_authority_pages_have_no_draft_banner(tmp_path):
    for scenario in (
        "01_multi_risk_missing",
        "04_unauthorized_agent_verification",
        "05_lightweight_low_risk",
        "07_policy_migration_warning",
        "08_human_final_decision_closure",
    ):
        with demo_service(tmp_path, scenario) as (service, case_id):
            rendered = render_interactive_review_html(
                action_view(service, case_id)
            ).split("<details>", 1)[0]
            assert "尚未选择处理结果" not in rendered
            assert "你的选择尚未提交" not in rendered

    with demo_service(
        tmp_path, "03_scoped_repair"
    ) as (service, case_id):
        unauthorized = action_view(
            service,
            case_id,
            ActorContext("reviewer-agent", "maintainer", False),
        )
        rendered = render_interactive_review_html(
            unauthorized
        ).split("<details>", 1)[0]
        assert "尚未选择处理结果" not in rendered
        assert "你的选择尚未提交" not in rendered


def test_final_decision_participant_surface_uses_plain_language(tmp_path):
    with demo_service(
        tmp_path, "03_scoped_repair"
    ) as (service, case_id):
        make_ready(service, case_id)
        case = service.storage.load_case(case_id)
        brief = service.review_brief(
            case_id,
            actor=HUMAN.actor,
            role=HUMAN.role,
        )
        view = compile_final_decision_view(
            review_brief=brief,
            governance_case=case,
            actor_context=HUMAN,
            policy_config=service.config,
        )
        rendered = render_final_decision_html(view)
        participant = rendered.split("<details>", 1)[0]
        required = (
            "最终人类决定",
            "治理材料和维护者检查已经完成",
            "接受本次贡献",
            "拒绝本次贡献",
            "要求修改后重新决定",
        )
        for text in required:
            assert text in participant
        forbidden = (
            "actor",
            "canonical maintainer",
            "authority-controlled",
            "finding",
            "verification operation",
            "final-decision operation",
            "closure operation",
            "transition",
            "obligation",
            "compiler",
            "CSRF",
            "preview token",
            "live_actions_enabled",
        )
        lowered = participant.lower()
        for text in forbidden:
            assert text.lower() not in lowered
        assert "<details>" in rendered
        assert "<details open" not in rendered


def test_final_decision_has_independent_preview_and_authority(tmp_path):
    with demo_service(
        tmp_path, "03_scoped_repair"
    ) as (service, case_id):
        make_ready(service, case_id)
        registry = PreviewTokenRegistry(token_factory=lambda: "final-token")
        preview = preview_final_decision(
            service=service,
            actor_context=HUMAN,
            case_id=case_id,
            decision_id="accept",
            reason="完成独立最终判断。",
            token_registry=registry,
        )
        assert preview.preview_token == "final-token"
        result = execute_final_decision(
            service=service,
            actor_context=HUMAN,
            case_id=case_id,
            preview_token=preview.preview_token,
            token_registry=registry,
        )
        case = service.storage.load_case(case_id)
        assert result.decision == "accept"
        assert case.state == "accepted"
        assert case.final_decision.decision == "accept"
        assert case.closure_receipt is not None
        assert all(
            item.action != "decide_close"
            for item in service.storage.read_transitions(case_id)
        )


def test_unauthorized_and_stale_final_decisions_are_rejected(tmp_path):
    with demo_service(
        tmp_path, "03_scoped_repair"
    ) as (service, case_id):
        make_ready(service, case_id)
        verifier = ActorContext(
            "human-verifier",
            "maintainer_verifier",
            True,
        )
        with pytest.raises(VNextError, match="最终决定"):
            preview_final_decision(
                service=service,
                actor_context=verifier,
                case_id=case_id,
                decision_id="accept",
                reason="unauthorized",
                token_registry=PreviewTokenRegistry(),
            )
        registry = PreviewTokenRegistry(token_factory=lambda: "stale-final")
        preview = preview_final_decision(
            service=service,
            actor_context=HUMAN,
            case_id=case_id,
            decision_id="accept",
            reason="preview first",
            token_registry=registry,
        )
        service.decide(
            case_id,
            actor="other-human-maintainer",
            role="maintainer",
            decision="request_changes",
            reason="case changed after preview",
        )
        with pytest.raises(VNextError, match="尚未进入|失效"):
            execute_final_decision(
                service=service,
                actor_context=HUMAN,
                case_id=case_id,
                preview_token=preview.preview_token,
                token_registry=registry,
            )


@contextmanager
def live_server(service, case_id):
    actor = HUMAN
    registry = PreviewTokenRegistry()
    store = ReviewDraftStore(service.storage)
    csrf = "csrf-test-token"
    from http.server import ThreadingHTTPServer

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        _handler_class(
            service,
            case_id=case_id,
            actor=actor,
            csrf_token=csrf,
            token_registry=registry,
            draft_store=store,
        ),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port, csrf
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def request(
    port,
    method,
    path,
    *,
    body="",
    content_type="application/x-www-form-urlencoded",
    origin=None,
):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    headers = {"Content-Type": content_type}
    if origin is not None:
        headers["Origin"] = origin
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    payload = response.read().decode("utf-8")
    status = response.status
    connection.close()
    return status, payload


def test_server_rejects_get_mutation_csrf_origin_json_and_traversal(
    tmp_path,
):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        with live_server(service, case_id) as (port, csrf):
            status, _ = request(port, "GET", "/execute")
            assert status == HTTPStatus.METHOD_NOT_ALLOWED
            good_origin = f"http://127.0.0.1:{port}"
            status, _ = request(
                port,
                "POST",
                "/draft",
                body=urlencode({"csrf_token": ""}),
                origin=good_origin,
            )
            assert status == HTTPStatus.BAD_REQUEST
            status, _ = request(
                port,
                "POST",
                "/draft",
                body=urlencode({"csrf_token": csrf}),
                origin="http://evil.example",
            )
            assert status == HTTPStatus.BAD_REQUEST
            status, _ = request(
                port,
                "POST",
                "/draft",
                body="{malformed",
                content_type="application/json",
                origin=good_origin,
            )
            assert status == HTTPStatus.BAD_REQUEST
            status, _ = request(port, "GET", "/../../case.yml")
            assert status == HTTPStatus.NOT_FOUND
            status, _ = request(port, "GET", "/?role=maintainer")
            assert status == HTTPStatus.NOT_FOUND


def test_server_escapes_xss_reason_and_ignores_operation_injection(
    tmp_path,
):
    with demo_service(
        tmp_path, "06_governance_self_modification"
    ) as (service, case_id):
        view = action_view(service, case_id)
        with live_server(service, case_id) as (port, csrf):
            origin = f"http://127.0.0.1:{port}"
            values = {
                "csrf_token": csrf,
                "operation": "decide_accept",
                "transition": "accepted",
            }
            for index, _ in enumerate(view.items, start=1):
                values[f"decision:{index}"] = "sufficient"
            values["decision:1"] = "supplement"
            values["reason:1:supplement"] = "<script>alert(1)</script>"
            status, payload = request(
                port,
                "POST",
                "/preview",
                body=urlencode(values),
                origin=origin,
            )
            assert status == HTTPStatus.OK
            assert "<script>alert(1)</script>" not in payload
            assert "&lt;script&gt;alert(1)&lt;/script&gt;" in payload
            assert "decide_accept" not in payload.split("<details>", 1)[0]
            token = re.search(
                r'name="preview_token" value="([^"]+)"',
                payload,
            ).group(1)
            status, result = request(
                port,
                "POST",
                "/execute",
                body=urlencode(
                    {
                        "csrf_token": csrf,
                        "preview_token": token,
                        "operation": "decide_accept",
                    }
                ),
                origin=origin,
            )
            assert status == HTTPStatus.OK
            assert "你的维护者检查已提交" in result
            assert service.storage.load_case(case_id).state == (
                "repair_requested"
            )
