# AGM Review Briefing Layer

Status: Phase 2 contextual-action prototype (`agm.review_action_view/v0.2-dev`)

The Review Briefing Layer is AGM's human-work compiler. It translates an
already-resolved governance case into the current conclusion, owner, blocking
work, irreducibly human judgment, and supporting explanation that an ordinary
maintainer can use without first learning the AGM lifecycle.

## Phase 2.1 PR-native diagnostic projection

`src/agm/vnext/pr_diagnostic/` is an additional read-only projection of the same compiled case. It does not perform independent matching or create cues. It presents a concrete PR, diffs when supplied, tests, materials, and clear local-operation boundaries; see `AGM_PR_NATIVE_DIAGNOSTIC_PHASE_2_1.md`.

The Phase 1.1 `brief` command remains read-only. Phase 2 adds a separate
interactive `review` command. It compiles each existing
`HumanJudgmentItem` into item-bound business outcomes, actor/case/version-bound
drafts, side-effect-free previews, and adapters to existing legal domain
operations. It does not add canonical obligations, authority, transitions, or
final-decision semantics.

## 1. Two compiler boundaries

The **governance-state compiler** resolves policy, matches rules, compiles the
union of obligations, binds evidence, enforces authority, derives
responsibility, and owns lifecycle state.

The **human-work compiler** reads those conclusions and explains:

- whether the current reader needs to act;
- who owns the current work if the reader does not;
- which exact items require human content judgment;
- what formal checks the system completed;
- what blocking problems remain; and
- what happens next.

```text
Governance Case + Policy Snapshot + canonical lifecycle records
        |
        v
Reviewer Guidance View
governance state, traceability, legal operation surface
        |
        v
Review Brief View
current conclusion, owner, human work, explanation
        |
        v
Contextual Action Compiler
item-bound outcomes, authorization, draft/preview binding
        |
        v
Interactive Maintainer Review
```

The brief may compile directly from stable domain records, but it reuses
Reviewer Guidance requirement comparisons and the same canonical lifecycle
facts. It never resolves risk selectors, compiles obligations, derives
authority, creates a finding, or predicts a transition. If Reviewer Guidance
and Review Brief disagree about material state, responsibility, verification,
or final acceptance, the disagreement is a compiler defect.

## 2. Current-next-step-first hierarchy

HTML and Markdown use this order:

1. contribution identity;
2. a prominent current-status and next-step card;
3. human judgment items, only when present;
4. contribution and risk summary;
5. contribution-side or accountable-human outstanding work;
6. blocking problems and system-handled anomalies;
7. requirement and automatic-check summaries;
8. default-collapsed complete requirements;
9. default-collapsed automatic-check and accountability detail; and
10. default-collapsed governance process and technical records.

The first status card states whether the maintainer acts now, the responsible
party, the item count, and the acceptance boundary. A user does not need to
scroll to discover the current route.

The five-step Reviewer Guidance workflow is not Review Brief navigation.
Workflow, internal state names, rule and obligation IDs, finding and repair
IDs, transitions, traces, and fingerprints remain in technical details.

## 3. Semantic vocabulary

One broad “system confirmed” label is not sufficient. Brief records use
non-overlapping semantic claims:

| State | Participant wording | Meaning |
| --- | --- | --- |
| `material_available` | 材料已提供 | A material record exists. |
| `structure_valid` | 形式要求已满足 | Required fields or command/result structure are present. |
| `version_bound` | 已对应当前版本 | The record binds the current contribution or has canonical retained-scope metadata. |
| `system_checked` | 材料与版本已核对 | The system completed available formal and binding checks. |
| `human_review_required` | 材料齐备，内容待人工检查 | Formal prerequisites are ready but content validity needs a human. |
| `human_verified` | 维护者已完成检查 | A legal maintainer-side verification record exists. |
| `final_decision_pending` | 等待最终人类决定 | Verification is complete but acceptance has not occurred. |
| `accepted` | 贡献已被最终接受 | An authorized final accept decision exists. |

A supplied, structurally valid, current-version statement can therefore show
`material_available`, `structure_valid`, `version_bound`, and
`human_review_required` together without contradiction. It is not presented
as content correctness.

For Phase 1 API compatibility, the original coarse `status` values remain in
serialized requirement and automatic-check records. Phase 1.1 adds
`semantic_status` and `semantic_states`; presenters use those precise fields.
Existing consumers can migrate without losing their original field.

A recorded passing test result proves only that a checkable command/result
record exists and is bound; it does not prove correct code or sufficient
coverage. An agent declaration remains a declaration. Attestation binding is
not proof that the statement is truthful. Maintainer verification is not
final acceptance.

## 4. Domain records and API

The read-only implementation lives in `src/agm/vnext/briefing/`:

- `models.py`: immutable records, `BriefSemanticState`, and `WorkOwner`;
- `compiler.py`: pure top-level compiler and technical trace index;
- `change_summary.py`: conservative path- and declaration-based summary;
- `risk_summary.py`: explanation of engine-recorded risk conclusions;
- `evidence_summary.py`: requirement semantics and policy-gated checks;
- `accountability.py`: observed, declared, attested, and inferred separation;
- `judgment_queue.py`: provenance-constrained human review work;
- `next_step.py`: one business-level current route;
- `work_items.py`: owner-labelled summaries derived from existing facts;
- `presenters.py`: JSON, Markdown, and standalone HTML; and
- `server.py`: loopback-only GET server with no mutation route.

Phase 2 lives in `src/agm/vnext/briefing/actions/`:

- `models.py`: contextual option, draft, preview, result, and separate
  final-decision records;
- `compiler.py`: item-bound options and final-decision view compilation;
- `authorization.py` and `binding.py`: canonical authority and stale binding;
- `draft.py`: non-canonical `.agm-work` persistence and interaction audit;
- `preview.py`: current-state recompilation and one-time tokens;
- `executor.py`: adapters to existing domain operations;
- `presenters.py`: review, preview, result, and final-decision HTML; and
- `server.py`: loopback POST service with CSRF, origin, host, content-type,
  expiry, and replay checks.

The core API remains:

```python
compile_review_brief(
    *,
    governance_case,
    policy_snapshot,
    contribution,
    actor_context,
) -> ReviewBriefView
```

The returned view includes `WorkItemSummary` records. Each record names one of:

- `system`;
- `contribution_side`;
- `accountable_human`;
- `maintainer`; or
- `final_decision_authority`.

It also states whether the item is blocking, whether the system already
handled it, and which safe public requirement/trace references link to folded
technical records.

## 5. Contribution and risk summaries

`ContributionBrief` keeps two sources separate:

- a contribution-side claim, labelled as a claim; and
- a conservative inference from changed paths, matched risk areas, semantic
  targets, and explicit structured declarations.

Path categories include authentication/authorization, configuration,
testing, governance/runtime, documentation, application, and other project
content. This supports navigation but does not claim function-level semantic
understanding.

`RiskBrief` reads the case's recorded overall risk, all matched rules,
affected paths, interaction IDs already attached to compiled obligations, and
the already-compiled independent-review obligation. It does not perform risk
matching in the presentation layer.

## 6. Requirement semantics

`RequirementBrief` remains organized by maintainer language. Its compatibility
buckets still separate:

- material that has completed its current formal or human-verification stage;
- material whose content requires human judgment;
- missing, stale, and invalid material;
- accountable-human confirmation;
- independent maintainer review; and
- non-applicable requirements.

Each `RequirementItem` additionally exposes precise semantic states and a
`WorkOwner`. Missing, stale, and invalid required material belongs to the
contribution side. Attestation belongs to the accountable human. Content or
independent review belongs to the maintainer. Completed formal checks belong
to the system only in the sense that no participant action is currently
assigned; they are not content approval.

## 7. Canonical gating for automatic checks

`AutomaticCheckResult` explicitly records:

- `policy_required`;
- `blocking`;
- safe `requirement_refs`;
- `informational_only`;
- `owner`; and
- `system_handled`.

Missing, blocking, required-to-continue, or contributor-todo wording is
permitted only when backed by a compiled obligation, active matched rule,
binding requirement, existing finding, transition prerequisite, or canonical
migration diagnostic.

Agent involvement alone does not create `O-AGENT-SCOPE`. If that obligation is
absent, a missing action/delegation statement is shown only as a gray
informational observation. It does not enter missing requirements, the human
queue, responsibility, progression, or findings.

Automatic checks distinguish system integrity checks from policy-required
checks and informational observations. Passed checks are folded by default;
real blocking problems remain visible.

## 8. Human judgment provenance

Every `HumanJudgmentItem` contains a safe requirement reference and explicit
provenance. Legal sources are:

- a compiled requirement whose material is ready for content review;
- an existing maintainer-review stage;
- an independent-review requirement;
- an existing finding; or
- the exact obligation scope of recorded scoped revalidation.

Missing or stale material never becomes maintainer judgment. Verified or
terminal work does not re-enter the queue. Scoped repair includes only the
recorded affected scope.

A denied attempted operation is never provenance for new human work. The
Phase 1 fallback that selected contribution summary after a denied attempt was
removed in Phase 1.1.

## 9. System-handled anomalies

Denied authority attempts are shown as **系统已处理的异常**:

- the attempted operation was rejected;
- no valid maintainer verification was produced;
- state did not change when the audit record says it did not; and
- the participant does not need to reject it again.

The event remains in folded technical audit records. It may provide security
visibility, but it cannot create an obligation, judgment target, repair, or
finding in the briefing layer.

Phase 1.1.1 also places a neutral summary in the first status card: the system
rejected the attempt, the operation did not take effect, and no participant
action is required. Full actor, operation, and transition data remain folded.

## 10. Accountability boundary

`ContributorAccountabilityBrief` separates:

- system-observed governance events;
- agent or contributor declarations;
- accountable-human confirmation;
- current version and material-set binding; and
- unverified inference limitations.

Participant labels avoid fixture actor IDs and tool names. Complete actor IDs,
source tools, evidence IDs, and attestation statements remain available in
technical records.

## 11. Routing and acceptance

`NextStepBrief` emits one current route:

- contribution-side material update;
- accountable-human confirmation;
- policy-migration assessment;
- maintainer content judgment;
- normal code review with no additional AGM judgment;
- final authorized human decision; or
- completed/closed.

Policy migration is surfaced in the top status card because an old-snapshot
requirement list must not be mistaken for a silent migration result. It does
not override the owner derived from current canonical work: if required
materials are still missing, the contribution side remains responsible while
the card also reports unchanged and revalidation counts.

No generic action menu is shown. A route does not execute the underlying
action. Verification completion and final acceptance remain separate.

## 12. CLI, deterministic demos, and CI

```bash
python -m agm.vnext.cli maintainer brief \
  --case CASE \
  --actor HUMAN \
  --role maintainer \
  --serve
```

The command writes `brief.json`, `brief.md`, and `brief.html`. Serving is
loopback-only and GET-only.

The separate Phase 2 command is:

```bash
python -m agm.vnext.cli maintainer review \
  --case CASE \
  --actor HUMAN \
  --role maintainer \
  --serve
```

Without `--serve`, it writes a deterministic action model and static HTML
without secrets. With `--serve`, draft saving is non-canonical; a governance
mutation requires a new preview and one-time actor/case-bound token. The
review page never exposes final accept, reject, or close controls. A ready
case shows only an entry to a separate **最终人类决定** page.

The eight design scenarios are regenerated and verified with:

```bash
python scripts/generate_review_briefing_demos.py
python scripts/check_review_briefing_demo_hashes.py
python scripts/generate_review_interactive_demos.py
python scripts/check_review_interactive_demo_hashes.py
git diff --exit-code
```

The frozen hash manifest covers all 24 JSON/Markdown/HTML outputs plus
`manifest.json`. The repository CI runs these commands explicitly on Windows
and Ubuntu. Fixture prose is natural participant language; generator names,
actor IDs, internal states, and other research identifiers remain only in
technical details.

Phase 2.0.1 additionally freezes interactive JSON, HTML, manifests, and the
interactive hash manifest as LF through `.gitattributes`. The tracked
repository ZIP is created from Git blobs with
`scripts/package_tracked_repository.py`, never from platform-converted
working-tree bytes. A fresh extraction must pass all three raw-byte hash
checks before regeneration and remain content-identical after regeneration.

## 13. Remaining limitations

- Path classification does not parse code semantics.
- Agent capabilities and delegation are configuration or declaration, not a
  complete runtime provenance system.
- Identity and truthfulness require external systems.
- Normal code review remains outside automatic AGM checks.
- The canonical state machine has no `request_repair` transition from
  `resubmitted`. A raw resubmission therefore remains contribution-side and
  exposes no maintainer actions. After complete bound material is validated,
  the contribution-side workflow calls existing `prepare_case()`, whose
  existing `submit_for_verification` transition enters
  `awaiting_maintainer_verification`. Only then are all legal review outcomes
  compiled.
- In a mixed sufficient/repair batch, the adapter executes only scoped repair.
  Sufficient selections remain in append-only interaction audit; it does not
  fabricate a maintainer verification transition.
- The loopback CLI binds an asserted actor and canonical role but cannot prove
  the real-world identity behind that local assertion.
- The artifact remains `pending_human_review`; review is not approval.
- No P92 experiment package has been generated.
