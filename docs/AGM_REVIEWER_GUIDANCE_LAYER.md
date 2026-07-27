# AGM Reviewer Guidance Layer

Status: `v0.2-dev`; maintainer-facing development interface, pending
independent human review

## Purpose

The Reviewer Guidance Layer turns an existing `GovernanceCase` into a
maintainer-operable view:

```text
canonical AGM state
-> reference requirement versus observed record
-> current workflow position
-> problems and blocking reasons
-> legal and illegal operations with consequences
-> expandable source evidence and policy detail
```

It does not make a review decision, select a recommended answer, infer human
authorship, or grant authority. The view is generated from domain records and
the canonical configuration loaded by the existing governance engine.

The implementation is isolated under:

```text
src/agm/vnext/guidance/
    __init__.py
    models.py
    diagnostics.py
    responsibility.py
    selectors.py
    utilities.py
    workflow.py
    action_planner.py
    presenters.py
```

The frozen v0.1 compatibility module is not imported or changed.

## Boundary with the governance engine

The layer consumes:

- `GovernanceCase`;
- canonical `VNextConfig` and its policy fingerprint;
- `StateTransition` history;
- current `ActorContext`; and
- optional read-only `MigrationDiagnostic`.

It never recompiles risks or obligations in HTML. Risk and interaction matches,
compiled obligations, bindings, findings, repairs, permissions, and transitions
remain outputs of the existing engine.

The public pure-data entry point is:

```python
build_reviewer_guidance(
    case,
    policy,
    transitions,
    current_actor,
    migration_diagnostic=None,
) -> ReviewerGuidanceView
```

The service convenience method loads the same records from local storage:

```python
service.reviewer_guidance(case_id, actor="...", role="...")
```

Every view object is a dataclass with `to_dict()` and can be serialized to JSON.

## Five-step user workflow

The internal lifecycle remains:

`Resolve -> Compile -> Bind -> Attest -> Verify -> Repair -> Decide -> Record`

The maintainer interface groups it as follows:

| User step | Internal stages | Meaning |
| --- | --- | --- |
| 1. 系统识别要求 | Resolve, Compile | Match every applicable rule and compile the obligation union. |
| 2. 贡献者准备材料 | Bind, Repair | Prepare, bind, correct, and resubmit affected material. |
| 3. 负责人确认 | Attest | Obtain accountable-human confirmation only when compiled policy requires it. |
| 4. 维护者检查 | Verify, Repair | Check bindings and loop through scoped repair when necessary. |
| 5. 人类维护者最终决定 | Decide, Record | Record a human decision and closure receipt. |

Displayed step states are text-and-symbol values, not colors alone:

| State | Symbol | User text |
| --- | --- | --- |
| `completed` | `✓` | 已完成 |
| `current` | `●` | 当前阶段 |
| `problem` | `!` | 有问题 |
| `pending` | `○` | 尚未开始 |
| `return` | `↺` | 返回修改 |
| `skipped` / `not_required` | `—` | 本次不要求 |

Repair is rendered as a loop:

```text
维护者发现问题
-> 返回修改指定部分
-> 重新检查受影响部分
-> 继续原流程
```

The step calculation uses the case state, obligation types and status,
attestation status, repair requests, and transition history.

## Requirement comparison

Every compiled obligation becomes one row:

| Column | Source |
| --- | --- |
| 检查项 | Stable Chinese participant-facing name; the ID remains in detail |
| 项目要求 | Chinese plain-language presentation metadata |
| 当前情况 | Chinese observation derived from bound domain records |
| 材料状态 | Whether the material is absent, usable, stale, retained, verified, etc. |
| 流程状态 | Who/what the row is waiting for and whether progression is blocked |

The twelve canonical obligation IDs have stable Chinese presentation metadata
in `guidance/diagnostics.py`. This metadata is deliberately outside `.agm`;
the canonical English `CompiledObligation.description` is preserved as
`reference_english`. Every row carries `display_name`, `reference_plain`,
`reference_english`, `observed_plain`, and `observed_raw`. Unknown future
obligations use a non-empty conservative fallback and expose the English
canonical text in detail.

Material and workflow state are deliberately separate:

| Material state | Meaning |
| --- | --- |
| `missing` | No usable material exists. |
| `invalid` | A record exists but cannot support the contribution. |
| `stale` | A record is bound to an old version or has expired. |
| `provided` | Current bound material exists. |
| `retained` | A prior binding was explicitly retained for the current contribution. |
| `verified` | Maintainer-side checking covers the material. |
| `overridden` | An authorized exception covers the requirement. |
| `not_applicable` | This path does not require the material. |

Two boolean fields make the policy property and current consequence explicit:

| Field | Meaning |
| --- | --- |
| `blocking_requirement` | The compiled requirement is blocking by policy design. |
| `currently_blocks_progression` | The requirement is unresolved in a way that blocks the case now. |

A satisfied blocking requirement therefore serializes as
`blocking_requirement=true` and `currently_blocks_progression=false`. The
former Python properties `blocking` and `blocks_progression` remain
deprecated read-only aliases for source compatibility; default JSON contains
only the new names.

Workflow states are `blocks_progression`, `awaiting_contributor`,
`awaiting_attestation`, `awaiting_revalidation`, `awaiting_final_decision`,
and `completed`. Thus a repaired item can be `provided` or `retained` while
its workflow state is `awaiting_revalidation`; it is not mislabelled missing
or invalid.

Presentation states are:

| State | Meaning |
| --- | --- |
| `meets_requirement` | Valid bound material exists for the current case. |
| `needs_attention` | A non-blocking issue is open. |
| `not_started` | The lifecycle has not reached this requirement. |
| `missing` | A record should now exist but does not. |
| `needs_update` | Material exists but is stale or expired. |
| `invalid` | Material is invalid, rejected, conflicting, or an attestation was invalidated. |
| `blocked` | An open blocking finding or policy conflict prevents progress. |
| `not_applicable` | The compiled/intake path does not require the item. |
| `verified` | A maintainer verification record covers the item. |
| `overridden` | An authorized override covers the item. |
| `closed` | The relevant case path is terminal. |

The result label does not replace the raw English state. Each row expands to
show:

- obligation ID and raw status;
- source rule and interaction IDs;
- evidence IDs;
- binding fingerprints;
- finding IDs;
- English reference text;
- English observed state; and
- typed trace references.

## Diagnostics

Plain-language diagnostics are presentation translations keyed by structured
finding/reason codes, not a second governance rule engine and not a lookup by
demo filename or complete English sentence. `GuidanceReasonPresentation`
carries `reason_code`, `display_plain`, `source_english`, `source_code`, and
typed `trace_refs`. Unknown codes use the conservative Chinese fallback
“系统记录了一项需要维护者查看的说明。” while preserving the complete source.

This presentation is used for finding messages, repair reasons, materiality and
scope reasons, retained evidence, invalidated attestations, authorization
denials, migration warnings, and lightweight/no-package explanations. Examples
include:

```text
这份材料已经过时
stale evidence

现有材料对应旧的代码、策略或有效期，不能直接支持当前修改。
```

The explanation carries references to the actual evidence record. Similar
translations cover invalidated attestations, scoped repair, retained evidence,
and policy migration warnings.

## Lightweight and ordinary paths

Risk intensity and role authority are independent.

A declared low/medium case without attestation or independent-review
obligations is shown as `lightweight`. It can require only a small material set,
while its final decision still belongs to a human maintainer.

When ordinary intake does not create a case,
`build_no_package_guidance(...)` reports:

```text
本次修改不要求完整 AGM 材料
No AGM package required
```

The result is `not_applicable`, not failure. `no_agm_package_submitted` never
proves human authorship.

## Material change and partial invalidation

`GovernanceService.resubmit(...)` accepts a factual classification:

- `unrelated`;
- `non_material`; or
- `material`.

It also accepts a reason and exact affected obligation IDs. A material
fingerprint change makes evidence for affected obligations stale. Unaffected
records keep their original contribution fingerprint and receive an audited
`retained_for_contribution_fingerprint` plus `retention_reason`; the original
binding is not rewritten.

The resubmission attempt records:

- effective change classification;
- reason;
- previous and new contribution fingerprints;
- stale evidence IDs;
- retained evidence IDs;
- invalidated attestation IDs; and
- required revalidation scope.

Attestations whose reviewed scope intersects a material affected scope are
invalidated. Confirmed attestations outside that scope can be retained with an
explicit reason. An unrelated or non-material change can retain all unaffected
bindings. This avoids an unconditional “any diff means redo everything” rule.

The prototype does not independently infer semantic materiality from an AST or
code-review model. The declared classification and affected obligation scope
remain facts that a maintainer must independently inspect.

## Scoped repair

A repair view combines:

- `GovernanceFinding`;
- `RepairRequest`;
- `affected_obligation_ids`;
- each recorded resubmission scope;
- retained evidence IDs; and
- `revalidation_required`.

The default verification action uses the open repair's revalidation scope.
Unaffected evidence stays visible and is not silently discarded.

## Action authority and unavailable actions

`action_views(...)` checks canonical role permissions, the state-machine
transition, and operation-specific preconditions. It shows both legal and
likely-but-illegal operations. Unavailable operations include a readable
reason and the possible authorized roles.

The presentation layer is not an authorization boundary. Every confirmed
operation still calls the existing `GovernanceService`, which checks role,
state, scope, separation of duty, and object existence again.

A contributor agent can prepare evidence and resubmit but cannot claim:

- accountable-human attestation;
- maintainer verification;
- authorized override; or
- final decision.

Lower governance intensity never expands agent authority.

### Responsibility derivation

`derive_current_responsibility(...)` uses the comparison rows plus findings,
repair requests, attestations, policy conflicts and readiness. Precedence is:

1. terminal closure;
2. open policy conflict;
3. contributor-side missing/stale/invalid blocking material;
4. open repair responsibility;
5. pending or invalidated accountable-human attestation;
6. valid resubmitted material awaiting scoped revalidation;
7. human final-decision readiness; and
8. ordinary lifecycle fallback.

Consequently `state=resubmitted` does not automatically mean “maintainer
verifier”. If affected material remains stale or missing, the contribution
side remains responsible.

### Relevance groups and selectors

Legal actions are partitioned into at most four current-relevant actions and a
default-collapsed other-available group. Unavailable actions are also
collapsed and carry category, required roles, required states and future
availability. This grouping does not remove or weaken domain authorization.

The web panel uses action-specific `ContextSelectorOption` records instead of
free-text evidence, finding, attestation, repair or obligation IDs. Selector
tokens are opaque and bound to case ID, contribution fingerprint, action,
object type and scope. Tokens are authenticated with HMAC. Normal execution
uses runtime secret material; deterministic demo secret material exists only
inside the research-fixture execution context. On every POST the server
rebuilds current valid options and rejects forged, stale, wrong-case,
wrong-action or wrong-scope tokens.
Non-interactive CLI operations may continue to accept explicit canonical IDs.

### Read-only handoff utilities

When no state-changing action is relevant, the view still exposes:

- `copy_missing_requirements`;
- `export_contributor_checklist`;
- `export_reviewer_summary`;
- `view_change_scope`; and
- `copy_handoff_note`.

Each `GuidanceUtilityAction` carries output and trace references with
`state_changing=false`. Opening an output neither writes the case nor appends a
transition.

## Action preview

The pure API is:

```python
preview_reviewer_action(
    case,
    policy,
    transitions,
    actor,
    action,
    parameters,
) -> ActionPreview
```

`ActionPreview` has two explicit layers. `display_effects`, `affected_items`,
`retained_items`, `invalidated_items`, responsibility/workflow labels, and
`next_steps` form the Chinese-first main layer. It contains material names and
human consequences, including which unaffected materials remain valid and
whether final acceptance is still outstanding.

`technical_details` contains the operation name, source/target raw states,
canonical obligation/evidence/finding/repair IDs, raw before/after effects,
internal workflow nodes, created record types, trace references, and the
preview fingerprint. HTML and Markdown fold this layer by default. The
deprecated object-level accessors used by early Python callers resolve into the
technical layer but are not duplicated in default JSON.

The hardened preview also projects responsibility and workflow position,
lists processed objects, retained and invalidated evidence, invalidated
attestations, record types that would be created, remaining attestation and
verification needs, and whether final acceptance actually occurred. Projection
uses a deep copy; storage and transition history remain unchanged.

The local panel uses two requests:

1. preview the operation without storage mutation;
2. confirm with the preview fingerprint.

Confirmation fails if the case or inputs changed after preview. The backend
then authorizes and performs the real operation. The preview does not promise
that an external actor identity is genuine.

## Rejected attempted operations

An authorization or operation-scope failure is an audit fact, not a governance
finding and not a successful state transition. `AttemptedOperation` records the
operation, actor/role, time, denial reason, required roles, state before/after,
and `state_changed=false`. It is appended to the case audit collection without
closing findings or advancing workflow state.

`RejectedOperationView` presents only the most recent relevant denial in the
main page as “最近一次操作未生效”. It states that the case did not move, shows
the current workflow position, and identifies the next authorized roles.
Historical denials and raw operation/role/reason fields stay in default-folded
technical detail. Successful operations never enter this audit collection.

## Delegation help

The expandable help defines delegation operationally.

Usually delegation:

- a subagent changes files;
- a subagent executes commands;
- a subagent autonomously produces and submits an adopted output; or
- another agent has an independent action scope or tool permission.

Usually not delegation:

- an ordinary tool-function call;
- file reading or search;
- a model call with no independent action right; or
- an assistant that only returns advice and does not autonomously modify the
  contribution.

The source trace points to the autonomy profile and `O-AGENT-SCOPE` when
compiled.

## Technical detail

The default-collapsed technical section includes raw state and readiness,
risk rules, autonomy and assurance profiles, interaction rules, compiled
obligations, evidence, attestations, verifications, findings, repair requests,
rejected attempted operations, both fingerprints, transitions, migration
diagnostic, final decision, closure receipt, and raw English text.

Routine review is possible without opening it, while every summary remains
traceable.

## Workflow trace allocation

Each `StateTransition` has one primary five-step destination:

| User step | Primary transition actions |
| --- | --- |
| 系统识别要求 | open/resolve policy, compile obligations |
| 贡献者准备材料 | evidence-state preparation, resubmit |
| 负责人确认 | await/confirm/decline/invalidate attestation, request correction |
| 维护者检查 | submit/verify/reject, repair, clarification, policy-conflict operations |
| 人类维护者最终决定 | mark ready, override, all decisions and closure |

Rule/obligation compilation, evidence, attestation, verification, finding,
decision and receipt references are attached only to the relevant expandable
step. The implementation no longer copies the entire transition log onto all
five nodes.

## Demonstrations

Run:

```bash
PYTHONPATH=src python scripts/generate_reviewer_guidance_demos.py
```

The demo generator defaults to deterministic research-fixture mode. Each
scenario installs a `DemoExecutionContext` with a fixed UTC clock, UUID5 IDs
derived from `scenario namespace + object type + stable ordinal`, and a
scenario-derived demo-only selector secret. Case/transition/evidence/finding/
repair/verification/attestation IDs, timestamps, selector tokens, and
fingerprints that depend on those records are therefore stable at file level.
Normal service execution remains random; `--runtime-random` is available only
for debugging the generator's ordinary runtime path.

Verify a frozen checkout with:

```bash
PYTHONPATH=src python scripts/generate_reviewer_guidance_demos.py
sha256sum examples/reviewer_guidance/outputs/**/*
PYTHONPATH=src python scripts/generate_reviewer_guidance_demos.py
sha256sum examples/reviewer_guidance/outputs/**/*
git status --short
```

The two hash sets must match and `git status --short` must be empty. This is
source-generation reproducibility; no generated page is post-processed to
replace IDs, and the fixed demo selector secret is never used for real
sessions.

Cross-platform reproducibility additionally fixes the input bytes and path
spelling. `write_demo_text()` converts CRLF and CR to LF, writes UTF-8 bytes
directly, and enforces the declared final-newline policy. The copied `.agm`
and skill files inside each temporary scenario are normalized in the same
fixture-only path; tracked canonical policy files are not edited. Serialized
repository-relative paths use `/`, file lists are explicitly ordered, and no
temporary absolute root or platform permission bit participates in a demo
contribution fingerprint. Narrow `.gitattributes` rules keep only the public
demo outputs and expected hash manifest on LF in every checkout, including
Windows repositories with `core.autocrlf=true`.

The shared Windows/Linux freeze lives at
`examples/reviewer_guidance/expected_sha256.json`. Verify all 25 outputs with:

```bash
PYTHONPATH=src python scripts/generate_reviewer_guidance_demos.py
python scripts/check_reviewer_guidance_demo_hashes.py
git diff --exit-code
```

The checker reports missing, unexpected, and mismatched files. It never
updates the freeze during ordinary validation. A researcher may deliberately
replace it only after reviewing the generated changes:

```bash
python scripts/check_reviewer_guidance_demo_hashes.py --update
```

The CI matrix runs the same generator, checker, complete test suite, and Git
diff check on `windows-latest` and `ubuntu-latest`.

Participant-facing canonical terms use one backend presentation registry.
Actions, roles, obligations, workflow nodes, record types, and states are
represented as a Chinese `display_plain` label paired with the unchanged
canonical value. Preview and rejected-operation main layers use the display
label; raw values such as `verify_evidence`, `contributor_agent`,
`O-SUMMARY`, `maintainer_check`, and `maintainer_verification` remain in
default-collapsed technical detail. Unknown values receive a neutral display
fallback while preserving the original canonical value for traceability.

Outputs are written to `examples/reviewer_guidance/outputs/`. Eight scenarios
cover multi-risk missing material, partial invalidation, scoped repair,
unauthorized verification, lightweight review, governance self-modification,
policy migration, and human final closure.

Each scenario has its own directory containing `guidance.json`, `report.md`
and `report.html`. JSON includes workflow and comparison snapshots,
responsibility, current actions, unavailable summary, selector data, preview,
trace mapping and final verification record. Markdown and HTML are rendered
from the same view model.

## Known limitations

- Local actor names and claimed roles have no cryptographic identity proof.
- The standard-library panel has no hosted authentication or multi-user
  session model.
- Materiality and affected obligation scope are explicitly declared and then
  reviewed; semantic change classification is not automatic.
- The preview predicts AGM state transitions, not external merge, deployment,
  or CI effects.
- No action is automatically recommended.
- The layer is `v0.2-dev` and remains pending independent human review.
