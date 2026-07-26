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
| 检查项 | `CompiledObligation.evidence_type` and stable obligation ID |
| 项目要求 | compiled description, blocking flag, source rules |
| 当前情况 | bound evidence, attestations, verifications, findings, and repair records |
| 结果 | deterministic presentation state derived from those records |

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

Plain-language diagnostics are presentation translations, not a second
governance rule engine. Examples include:

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

It returns the source and predicted target states, affected obligations,
retained evidence, potentially invalidated attestations, effects, authority
reason, next actor roles, trace references, and a deterministic preview
fingerprint. `mutates_case` is always false.

The local panel uses two requests:

1. preview the operation without storage mutation;
2. confirm with the preview fingerprint.

Confirmation fails if the case or inputs changed after preview. The backend
then authorizes and performs the real operation. The preview does not promise
that an external actor identity is genuine.

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
both fingerprints, transitions, migration diagnostic, final decision, closure
receipt, and raw English text.

Routine review is possible without opening it, while every summary remains
traceable.

## Demonstrations

Run:

```bash
python scripts/generate_reviewer_guidance_demos.py
```

Outputs are written to `examples/reviewer_guidance/outputs/`. Eight scenarios
cover multi-risk missing material, partial invalidation, scoped repair,
unauthorized verification, lightweight review, governance self-modification,
policy migration, and human final closure.

Each JSON contains the guidance view, expected workflow and comparison
snapshots, available/unavailable actions, preview, and final verification
record. The HTML is rendered from the same view model.

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
