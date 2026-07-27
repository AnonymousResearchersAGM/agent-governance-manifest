# AGM Review Briefing Layer

Status: Phase 1 development prototype (`agm.review_brief/v0.2-dev`)

The Review Briefing Layer is AGM's human-work compiler. It turns an already
resolved governance case into the smallest useful set of facts, problems,
human judgments, and next responsibility that an ordinary maintainer needs to
understand.

Phase 1 is read-only. It does not add an action menu, perform item-level
verification, request repair, alter responsibility, advance the state machine,
attest, decide, accept, reject, close, or merge.

## 1. Two compiler levels

AGM now distinguishes two compilation problems:

1. the **governance-state compiler** resolves policy, matches every applicable
   risk rule, compiles obligations, binds evidence, validates freshness and
   scope, derives responsibility, and records authority-checked lifecycle
   state; and
2. the **human-work compiler** consumes those conclusions and explains the
   concrete review work to a maintainer who should not have to learn the AGM
   lifecycle first.

The data flow is:

```text
Governance Case
+ Policy Snapshot
+ Matched Rules
+ Compiled Obligations
+ Bound Evidence
+ Agent Declaration
+ Human Attestation
+ Findings / Repair
+ Verification / Decision
        |
        v
Reviewer Guidance View
  governance state, workflow, trace, legal operation surface
        |
        v
Review Brief View
  change, risk, system facts, human judgment queue, next responsibility
```

The implementation may compile the brief directly from stable domain records,
but it reuses Reviewer Guidance requirement comparisons and responsibility
derivation. It never resolves selectors, unions obligations, validates
authority, or predicts transitions again.

## 2. Layer relationship

The two presentation layers serve different readers:

| Layer | Primary purpose | Main concepts |
| --- | --- | --- |
| Reviewer Guidance | Governance-state and operation traceability | workflow, state, requirement comparison, finding, repair, legal action, preview |
| Review Brief | Ordinary maintainer work understanding | what changed, why risky, what the system confirmed, what is wrong, what only a human can judge, who acts next |

The Review Brief's folded technical details contain the complete Reviewer
Guidance view and canonical records. Both layers therefore point back to the
same case conclusion. If a brief and guidance view ever disagree about
material validity, responsibility, verification, or final acceptance, that is
a compiler defect; the brief has no authority to choose a different answer.

## 3. Public API and modules

The implementation lives in `src/agm/vnext/briefing/`:

- `models.py`: immutable serializable briefing records;
- `compiler.py`: top-level pure compiler and technical trace index;
- `change_summary.py`: path- and declaration-aware contribution summary;
- `risk_summary.py`: plain explanation of recorded matched rules and
  interaction conclusions;
- `evidence_summary.py`: requirement buckets and automatic checks;
- `accountability.py`: agent declaration and accountable-human separation;
- `judgment_queue.py`: human-only review work;
- `next_step.py`: one responsibility-aligned next step;
- `presenters.py`: JSON, Markdown, and standalone HTML;
- `server.py`: loopback-only GET server with no mutation route.

The core API is:

```python
compile_review_brief(
    *,
    governance_case,
    policy_snapshot,
    contribution,
    actor_context,
) -> ReviewBriefView
```

`GovernanceService.review_brief()` supplies the stored case, current loaded
policy context, transition history, migration diagnostic, and actor context.
The compiler is deterministic and performs no storage writes. The CLI writer
persists only `brief.json`, `brief.md`, and `brief.html`.

## 4. Provenance model

Participant wording must keep four epistemic categories separate:

1. **system-confirmed** — facts AGM can verify from its own records, such as
   current version binding, expiry, artifact presence/hash, changed-file list
   equality, command/result field presence, attestation binding, structural
   requirements, denied authority attempts, and unchanged state after denial;
2. **declared** — contribution summary, rationale, impact statement, known
   limitations, agent action scope, capability, supervision, and delegation
   supplied by an agent or contributor;
3. **human-confirmed** — an accountable human's explicit reviewed scope,
   statement, reservations, and current version/material binding; and
4. **unverified inference** — path-based component or risk-oriented summaries
   that help navigation but do not prove source-code semantics.

Agent self-report is never promoted to system observation. A recorded command
and result is not proof that the code is correct or that the test coverage is
sufficient. A valid attestation binding is not proof that the human statement
is truthful. AGM is not an AI detector and does not infer human authorship
from the absence of an agent declaration.

## 5. Contribution summary

`ContributionBrief` answers “what changed?” using two parallel descriptions:

- the latest usable contribution summary, clearly labelled as contributor
  material and naming its recorded source; and
- a conservative system inference based only on changed paths, matched risk
  areas, supplied semantic targets, and explicit structured declarations.

Paths are grouped into components such as authentication/authorization,
configuration/dependencies, tests, governance/runtime, documentation, and
application code. Security, configuration, governance, and test paths remain
separately addressable. The compiler does not claim to understand a function's
behavior merely because a filename contains `auth` or `config`.

## 6. Risk explanation

`RiskBrief` does not calculate risk. It reads:

- `GovernanceCase.overall_risk_level`;
- every recorded `MatchedRule`;
- the affected paths and selector reasons already retained by the engine;
- interaction IDs already attached to compiled obligations; and
- the presence of the already-compiled independent-review obligation.

The participant sees the union of risk areas, a path-to-area explanation, the
business meaning of interaction escalation, and whether independent review is
required. Raw rule IDs and obligation IDs stay in technical details.

## 7. Requirements and automatic checks

`RequirementBrief` organizes work by maintainer language rather than
obligation code. Every required item has exactly one briefing status:

- `system_satisfied`;
- `provided_requires_human_judgment`;
- `missing`;
- `stale`;
- `invalid`;
- `awaiting_accountable_human`;
- `awaiting_independent_review`; or
- `not_applicable`.

The mapping consumes `RequirementComparison.material_status`,
`workflow_status`, requirement type, and recorded verification. It does not
revalidate evidence or compile policy.

`AutomaticCheckResult` covers:

- material/current-version binding;
- test command and result structure;
- test material's current-version binding;
- evidence expiry;
- accountable-human attestation binding;
- declared versus recorded changed-file scope;
- recorded agent-involvement profile;
- presence of an action/delegation declaration;
- denied authority attempts and whether state changed; and
- structural requirement completion.

Automatic results use `confirmed`, `problem`, `needs_human_judgment`, or
`not_applicable`. A “confirmed test record” means only that the command,
environment, result, and binding are structurally checkable.

## 8. Contributor accountability

`ContributorAccountabilityBrief` presents:

- whether the case is on an agent-mediated path;
- capability and action-scope values from the recorded autonomy profile;
- system-observed governance events, such as which actor identity submitted
  evidence or supplied command records;
- agent/contributor declarations about actions and delegation;
- declaration source and presence;
- accountable-human identity, reviewed scope, status, and current binding; and
- explicit inference limitations.

`delegation_detected` describes what the declaration says, not a behavioral
fact discovered independently by AGM.

## 9. Human judgment queue

`HumanJudgmentItem` is the central Phase 1 output. Each item has a stable
presentation key suitable for a future item-level action, but no Phase 1
action is attached.

An item contains:

- why automation must stop;
- the contributor claim;
- the system observation that motivates review;
- a concise evidence summary;
- concrete review focus questions;
- possible human outcomes;
- priority and blocking meaning; and
- a safe public trace reference whose raw objects live only in technical
  detail.

Queue rules are:

- missing materials do not become maintainer judgment;
- stale or invalid materials remain contribution-side work;
- pending accountable-human confirmation is not maintainer judgment;
- verified or terminal work does not re-enter the queue;
- scoped repair contributes only the recorded revalidation scope;
- a low-risk contribution may have an empty AGM judgment queue; and
- independent review remains a human item only after its prerequisites are
  ready.

The queue does not ask a maintainer to repeat current-version, expiry, hash,
field-presence, changed-file equality, or authority checks that AGM has already
completed.

## 10. Automatic routing and next step

`NextStepBrief` emits one current business-level route:

- contribution-side material update;
- accountable-human confirmation;
- policy-migration attention;
- maintainer judgment;
- normal code review with no extra AGM judgment;
- final authorized human decision; or
- completed/closed.

The route names the responsible party, what AGM will continue to check or
preserve, and what the human should do now. It never exposes a generic
reject/repair/return/resubmit menu.

Routing text can describe a contribution-side todo derived from current gaps,
but the Phase 1 compiler does not create a new domain record. Existing engine
responsibility and lifecycle services remain authoritative.

## 11. Information architecture

The participant-visible page order is:

1. contribution and changed scope;
2. risk conclusion and reason;
3. project requirements and completion;
4. system-confirmed facts;
5. system-detected problems and declared facts the system cannot judge;
6. the human judgment queue;
7. the one current next step; and
8. collapsed governance process and technical detail.

The five-step Reviewer Guidance workflow is not the main navigation. Raw
states, transitions, obligation/finding/evidence/repair IDs, fingerprints, and
generic action lists appear only inside the folded technical section.

## 12. CLI and outputs

```bash
python -m agm.vnext.cli maintainer brief \
  --case CASE \
  --actor HUMAN \
  --role maintainer \
  --serve
```

The command writes beside the case:

- `brief.json`;
- `brief.md`; and
- `brief.html`.

The server binds only to loopback, supports GET only, and returns method-not-
allowed for POST. There are no action tokens because Phase 1 has no action
endpoint.

The deterministic scenario generator is:

```bash
python scripts/generate_review_briefing_demos.py
```

It compiles the existing eight governance scenarios under
`examples/review_briefing/outputs/`. These are design-review fixtures, not a
formal experiment package, human verification, final decision, or accepted
artifact.

## 13. Phase 1 limitations

- Path classification is conservative and does not parse code semantics.
- Agent capabilities and delegation are recorded configuration/declaration,
  not complete runtime provenance.
- The queue offers review focus and possible outcomes but no item-level
  mutation.
- Normal code review remains outside AGM's automatic checks.
- External identity, signature, hosted storage, platform review, branch
  protection, and merge authority are not implemented.
- Human review of the information architecture is still required before
  Phase 2 state-changing actions are designed.
