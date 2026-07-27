# AGM Review Briefing Phase 2

Status: implementation evidence prepared; `pending_human_review`

## Purpose

Phase 2 turns the read-only Human-Work Compiler into a contextual,
permission-controlled, item-by-item maintainer interface. AGM still owns the
workflow. The participant chooses a business outcome for one concrete human
judgment; they never choose a transition, finding type, obligation ID, repair
mechanism, or lifecycle state.

The read-only command remains unchanged:

```bash
python -m agm.vnext.cli maintainer brief \
  --case CASE --actor HUMAN --role maintainer --serve
```

The interactive command is separate:

```bash
python -m agm.vnext.cli maintainer review \
  --case CASE --actor HUMAN --role maintainer --serve
```

## Compiler relationship

```text
Canonical Governance Objects
        ↓
Review Briefing Compiler
        ↓
ReviewBriefView
        ↓
Contextual Action Compiler
        ↓
Interactive Maintainer Review
```

The action compiler reuses `ReviewBriefView`, `HumanJudgmentItem`,
`NextStepBrief`, and `WorkItemSummary`. It filters out any judgment without a
current compiled-requirement mapping and accepted provenance. Denied attempts,
informational observations, missing contribution material, policy migration,
terminal cases, and low-risk normal review do not manufacture buttons.

## Item-bound options

Each `InteractiveJudgmentItem` preserves the plain title, why a human is
needed, contribution claim, system observation, evidence summary, review
focus, blocking meaning, safe requirement references, and provenance.

At most three business outcomes appear inside that card:

1. **确认材料充分** — eligible only when material, binding, current stage,
   verifier role, human role, and authority permit existing
   `verify_evidence`.
2. **要求补充或修正** — requires a reason and maps to existing scoped
   `request_repair` when the current state supports it.
3. **标记重大风险** — requires a reason and uses the same legal blocking
   repair/finding mechanism; it never means final rejection.

`existing_operation_ref` is retained for technical trace and preview only.
The participant layer never shows obligation, finding, evidence, transition,
or fixture actor IDs.

## Draft and stale handling

`ReviewDecisionDraft` is stored below the case's ignored `.agm-work` runtime
directory. It binds:

- case, actor, and canonical role;
- contribution fingerprint;
- policy snapshot fingerprint;
- selected judgment and business option;
- safe requirement references and provenance; and
- created/updated timestamps.

A draft is not canonical governance state, verification, or final audit.
Saving and abandoning a draft do not write case state or transitions. A
changed binding, disappeared/changed judgment, or newly unauthorized option
makes it stale and unsubmitable. A submitted or abandoned draft is archived
outside `.agm`.

## Preview-before-execute

Preview reloads the current case and recompiles the Review Brief and contextual
options. It rechecks completeness, actor/role/case, state, contribution and
policy fingerprints, judgment provenance, authority, and existing-operation
legality. The plain preview describes:

- sufficient, supplement, and material-risk item counts;
- affected repair scope;
- retained valid evidence;
- the fact that no current accept/reject occurs; and
- whether later recheck is scoped.

A live preview receives a random, short-lived, server-session-only token bound
to the case, actor, role, draft fingerprint, current state, current policy and
contribution, and compiled plan. Static outputs contain no token. A missing,
expired, used, wrong-actor, wrong-role, wrong-case, or stale token is rejected.

## Existing-operation adapters and automatic routing

An all-sufficient batch calls existing `verify_evidence`. The domain service
may then perform its existing `mark_ready` transition. The result page says
that maintainer checking is complete and final acceptance is still a separate
human decision.

A batch containing supplement or material-risk choices calls existing scoped
`request_repair` for the affected obligations. Unaffected valid evidence is
preserved by the existing repair model. If the case requires independent
review, a material-risk repair routes to the maintainer side. No such batch
calls `decide_reject`.

For a mixed sufficient/repair batch, executing verification first would make
the existing engine transiently mark the case ready before creating repair.
Executing repair first would make verification illegal. Phase 2 therefore
performs only the legal scoped repair and records every submitted selection
in the append-only interaction submission audit; it does not invent a
verification.

The canonical state machine currently has no repair-request transition from
`resubmitted`. In that state, supplement and material-risk options are shown
unavailable with the stage limitation. Phase 2 does not add a transition,
temporarily rewrite state, or verify material the human judged insufficient.

## Final-decision separation

The review page never contains final accept, reject, or close controls. When
the canonical state is `ready_for_human_decision` or `overridden`, an
authorized maintainer sees only **进入最终决定**.

The separate **最终人类决定** page recompiles contribution, risk,
requirements, verification, unresolved findings, final authority, and the
acceptance boundary. It exposes only existing `decide_accept`,
`decide_reject`, `decide_request_changes`, and `decide_close` operations that
are currently legal. Every decision requires its own reason, preview, token,
and authority recheck. Review completion never auto-navigates into or executes
a final decision.

## Security

The interactive server:

- binds loopback only, defaulting to `127.0.0.1`;
- uses POST only for mutation paths;
- validates host and origin against the current loopback port;
- requires a session CSRF token;
- accepts only bounded UTF-8 form input;
- fixes case, actor, and role in the server session;
- maps business option IDs server-side and ignores arbitrary operation or
  transition fields;
- requires preview before execute;
- expires and consumes tokens once;
- rejects replay, stale binding, malformed input, and path traversal;
- escapes participant reasons in HTML and safely serializes JSON; and
- records rejected interaction attempts separately with
  `state_changed=false`.

The local actor assertion is not externally authenticated. Canonical role,
permission, stage, verifier role, and recorded separation-of-duty are
enforced, but real-world identity proof requires an external identity
provider.

## Deterministic outputs and CI

`scripts/generate_review_interactive_demos.py` writes
`review_action_model.json` and `review_interactive.html` for the existing
eight scenarios plus `09_pre_final_decision`. Static models set
`live_actions_enabled=false`; they contain no CSRF/session/preview secret or
current time.

`scripts/check_review_interactive_demo_hashes.py` checks the committed
19-file output set. Windows and Ubuntu CI regenerate Reviewer Guidance,
read-only Review Briefing, and interactive Review Briefing outputs, compare
all frozen hashes, run the two briefing test files independently, run the
complete suite, and require a clean Git diff.

## Governance boundary

Phase 2 does not modify canonical `.agm` policy, risk matching, obligation
compilation, authority, state-machine transitions or preconditions, evidence
and attestation binding, responsibility derivation, scoped invalidation or
repair, override, final-decision, closure, legacy, or v0.1 semantics.

The artifact remains `pending_human_review`. No P92 package is generated and
Phase 3 is not started.
