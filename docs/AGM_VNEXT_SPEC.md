# Agent Governance Manifest vNext Development Specification

Version: `v0.2-dev`

Status: new design development; not part of the reported AGM v0.1.0
evaluation and not a stable v0.2.0 release

## 1. Scope

AGM vNext instantiates project governance for a concrete contribution. It
resolves canonical policy, compiles contribution-specific obligations, binds
evidence and human accountability to the actual change, authorizes lifecycle
operations by role, supports scoped repair, and records a final human decision.

AGM is not an AI detector, authorship classifier, provenance log, automatic
approval system, or replacement for code review and maintainer judgment.

## 2. Compatibility boundary

`src/agm/governance.py` preserves the reported v0.1 behavior. It records all
matched zones but selects one evidence profile from the highest risk level.
vNext lives under `src/agm/vnext/` and compiles obligations from all applicable
sources.

The immutable v0.1 base and evidence boundary are recorded in
`docs/V0_1_RESEARCH_SNAPSHOT.md`.

## 3. Canonical and runtime locations

- `.agm/manifest.yml`: canonical entrypoint.
- `.agm/policies/`: risk, obligation, and interaction rules.
- `.agm/profiles/`: autonomy and assurance profiles.
- `.agm/roles/`: roles and permissions.
- `.agm/workflows/`: authority-typed state machine.
- `.agm/interfaces/`: report, panel, and message configuration.
- `.agm/agents/`: optional steward entrypoints and protocols.
- `.agm/schemas/`: development schemas.
- `.agm-work/cases/<case-id>/`: ignored local runtime state.

Policy documents use schema identifiers ending in `/v0.2-dev`. Runtime data
must not be written into canonical policy files.

## 4. Intake modes

| Mode | Meaning |
| --- | --- |
| `ordinary` | No AGM package was submitted and no matched rule requires one. This does not confirm human authorship. |
| `declared_agent_mediated` | Structured governance was voluntarily declared. |
| `policy_required` | Project policy requires a case because of the actual change or risk. |
| `maintainer_requested` | A maintainer requests structured preparation. |

A policy-required rule overrides requested ordinary intake. The decision is
based on the change, never inferred authorship.

## 5. Lifecycle

The lifecycle is:

`Resolve -> Compile -> Bind -> Attest -> Verify -> Repair -> Decide -> Record`

Every state mutation records actor, role, source, target, action, reason,
related objects, and timestamp in append-only `transitions.jsonl`.

Case states include:

- `case_opened`
- `policy_resolved`
- `obligations_compiled`
- `evidence_incomplete`
- `awaiting_human_attestation`
- `awaiting_maintainer_verification`
- `repair_requested`
- `resubmitted`
- `verification_complete`
- `ready_for_human_decision`
- `overridden`
- `accepted`
- `rejected`
- `closed`

`ordinary_unmanaged` is a diagnostic path result, not proof of human
authorship. `ready_for_human_decision` is not acceptance.

## 6. Domain records

The typed domain model includes:

1. `GovernanceCase`
2. `PolicySnapshot`
3. `MatchedRule`
4. `CompiledObligation`
5. `BoundEvidence`
6. `HumanAttestation`
7. `GovernanceFinding`
8. `RepairRequest`
9. `StateTransition`
10. `MaintainerVerification`
11. `FinalDecision`
12. `ClosureReceipt`

All records have stable IDs. Time-sensitive events have timezone-explicit
timestamps.

## 7. Rule resolution

Risk selectors support:

- repository-relative path/glob patterns;
- supplied change-type tags;
- supplied semantic target/symbol labels; and
- governance-entrypoint changes.

The prototype exposes AST/symbol integration through supplied semantic labels
without embedding a heavyweight parser.

Every rule match is retained with trigger reasons and affected paths. Files
without a path match receive the conservative fallback even when another file
matched a known rule.

Technical/organizational risk and agent autonomy are orthogonal. Autonomy may
add action-scope or human-accountability obligations without changing the
technical risk headline.

## 8. Obligation compilation

Sources are:

- every matched risk rule;
- the selected autonomy profile;
- the selected assurance profile; and
- every triggered interaction rule.

Compilation applies:

- union by stable obligation ID;
- source and affected-scope preservation;
- deduplication of identical obligations;
- blocking over warning;
- highest severity for compatible duplicates;
- union of verifier roles;
- conjunction across all blocking obligations; and
- explicit blocking `policy_conflict` findings for incompatible type or
  evidence semantics.

Overall risk is the maximum applicable severity for display and fallback. It
is never the sole source of obligations.

## 9. Evidence binding and validity

Each `BoundEvidence` records:

- evidence ID and obligation IDs;
- affected files or semantic scopes;
- contribution and policy fingerprints;
- evidence type and factual value;
- command and environment where applicable;
- artifact path and SHA-256 hash;
- observation time and optional expiry;
- source actor and tool; and
- current validity and rejection state.

Validation detects:

- missing and placeholder values;
- unknown or orphaned obligations;
- evidence-type mismatch;
- scope outside the contribution;
- stale contribution or policy binding;
- expired evidence;
- missing or changed artifacts;
- missing command environment or source tool; and
- conflicting values for the same obligation.

Local paths are resolved inside the repository root. Case IDs and runtime paths
reject traversal. State files use atomic replacement.

## 10. Human attestation

Human attestation is an explicit append-only event. Only the
`accountable_human` role may confirm it. The event binds:

- human actor and timestamp;
- reviewed scope;
- statement and reservations;
- policy fingerprint;
- contribution fingerprint; and
- evidence-set fingerprint.

An agent cannot confirm attestation. Material changes invalidate only
attestations whose reviewed scope or evidence binding is affected. Confirmation
does not mean acceptance.

## 11. Maintainer operations

Authorized operations include:

- verify or reject evidence;
- ask for clarification;
- request repair;
- invalidate an attestation;
- record or resolve a policy conflict;
- record an authorized override; and
- accept, reject, request changes, or close.

UI controls do not grant authority. The service validates role permission,
current state, transition definition, and operation-specific preconditions.
Independent review enforces separation from evidence and attestation actors.

Override and final decision are distinct. A terminal decision produces a
`ClosureReceipt` containing policy/change fingerprints, obligation states,
evidence, attestations, verifications, repair history, exceptions, and the
transition-log hash.

## 12. Repair and partial invalidation

A `GovernanceFinding` identifies the issue and affected obligations. A
`RepairRequest` identifies the responsible role, correction, revalidation
scope, and every attempt.

Resubmission recomputes the contribution fingerprint, revalidates evidence,
and invalidates affected attestations. Unaffected records remain available.
Previous attempts and transitions are retained.

## 13. Policy migration

Every case records its original policy fingerprint. `case migrate-check`
recompiles current obligations and reports:

- still-valid, changed, added, and removed obligations;
- evidence requiring revalidation;
- attestations invalidated if migrated; and
- whether the original snapshot remains permitted.

Migration is never performed by the diagnostic. A newly added critical
blocking obligation or explicit `must_follow_current` policy requires
migration; otherwise an authorized maintainer decides whether to remain on the
recorded snapshot.

## 14. Reports and local panels

Both panels show the exact contribution and policy fingerprints.

The contributor panel presents matched risk, obligations, evidence gaps, and
the precise scope offered for explicit human confirmation, correction, or
decline.

The maintainer report presents risk domains, reference-versus-observed
obligation state, anomalies, evidence binding, attestations, repair and
transition history, and authorized operations.

HTML escapes all user-controlled content. Mutation forms require a random
per-session action token. The standard-library server rejects non-loopback
binding and validates authorization server-side.

## 15. CLI

After an editable install (`python -m pip install -e .`), discover commands
with:

```bash
python -m agm.vnext.cli --help
python -m agm.vnext.cli project validate
python -m agm.vnext.cli project simulate --changed-file docs/example.md
python -m agm.vnext.cli contributor open-case --changed-file docs/example.md --actor contributor-agent
python -m agm.vnext.cli contributor prepare --case CASE --actor contributor-agent
python -m agm.vnext.cli contributor review --case CASE --serve
python -m agm.vnext.cli case status --case CASE
python -m agm.vnext.cli maintainer inspect --case CASE --serve
python -m agm.vnext.cli maintainer request-repair --case CASE --actor HUMAN --message REASON --obligation O-ID
python -m agm.vnext.cli maintainer verify --case CASE --actor HUMAN --reason REASON
python -m agm.vnext.cli maintainer decide --case CASE --actor HUMAN --decision accept --reason REASON
python -m agm.vnext.cli case migrate-check --case CASE
```

## 16. Security and trust boundary

The local prototype uses safe YAML loading, deterministic SHA-256 hashing,
atomic state writes, append-only transition logs, traversal-safe paths, escaped
HTML, loopback-only serving, action tokens, and server-side authorization.

It does not provide cryptographic identity, signatures, hosted storage,
platform branch protection, or proof that a claimed human identity is
truthful. Projects requiring those guarantees must integrate external identity
and attestation systems.

## 17. Reviewer Guidance Layer

The maintainer-facing Reviewer Guidance Layer shall be generated from a
`GovernanceCase`, canonical `VNextConfig`, transition history, actor context,
and optional migration diagnostic.

Its serializable domain records include:

1. `ActorContext`
2. `ReviewerGuidanceView`
3. `ContributionSummary`
4. `WorkflowStepView`
5. `RequirementComparison`
6. `DiagnosticFindingView`
7. `AvailableAction`
8. `UnavailableAction`
9. `ActionPreview`
10. `GuidanceExplanation`
11. `TraceReference`
12. `ResponsibilityView`
13. `ContextSelectorOption`
14. `GuidanceUtilityAction`
15. `MaterialityDeclarationView`
16. `GuidanceReasonPresentation`
17. `RejectedOperationView`
18. `ActionPreviewDisplayEffect`

The underlying case may also contain append-only `AttemptedOperation` audit
records for denied operations. These are not findings or state transitions.

The core API is:

```python
build_reviewer_guidance(
    case,
    policy,
    transitions,
    current_actor,
    migration_diagnostic=None,
)
```

The main view shall expose a contribution summary, five-step lifecycle,
reference-versus-observed comparison, available and unavailable actions,
action preview, and default-collapsed technical detail. Plain-language labels
shall not remove raw English states, stable IDs, fingerprints, or source
references.

The five workflow states use `completed`, `current`, `problem`, `pending`,
`return`, and `skipped`/`not_required`. Status must be conveyed by text or
symbol as well as color.

Requirement presentation states are `meets_requirement`, `needs_attention`,
`not_started`, `missing`, `needs_update`, `invalid`, `blocked`,
`not_applicable`, `verified`, `overridden`, and `closed`.

An ordinary no-case path shall render `no_agm_package_submitted` as
`not_applicable`, never as failure or evidence of human authorship. A
lightweight path may omit attestation or independent review while final
authority remains human.

## 18. Action planning

The pure action API is:

```python
preview_reviewer_action(
    case,
    policy,
    transitions,
    actor,
    action,
    parameters,
)
```

It shall not mutate the case, transition list, or storage. Its display layer
shall expose Chinese human-readable effects, affected and retained material
names, responsibility/workflow movement, next steps, and whether final
acceptance remains outstanding. Its default-collapsed `technical_details`
shall expose the operation, source/predicted target raw states, canonical IDs,
raw effects, internal workflow nodes, expected record types, next actors,
traceability, and deterministic preview fingerprint.

The local maintainer panel shall require preview before confirmation.
Confirmation shall be rejected when the preview fingerprint no longer matches
the current case and inputs. Preview authorization does not replace domain
service authorization.

Available actions shall agree with canonical permissions, current-state
transitions, and operation preconditions. Likely but unavailable actions shall
remain visible with a readable reason and possible authorized role.

No UI element may label one operation as the recommended or uniquely correct
answer.

## 19. Scoped binding retention

Resubmission accepts an explicit `unrelated`, `non_material`, or `material`
classification, a factual reason, and affected obligation IDs.

When the contribution fingerprint changes:

- evidence bound to affected material obligations becomes stale;
- unaffected evidence retains its original binding and records a
  `retained_for_contribution_fingerprint` plus reason;
- intersecting attestations are invalidated;
- unaffected attestations can be retained with an explicit reason; and
- the repair attempt records old/new fingerprints, stale and retained evidence,
  invalidated attestations, and required revalidation scope.

The engine shall not treat every diff as full invalidation. The prototype does
not independently establish semantic materiality; the declared classification
and scope remain subject to human maintainer inspection.

## 20. Guidance output and demonstrations

`maintainer inspect` writes:

- `guidance.json`;
- `report.md`; and
- `report.html`.

The served HTML defaults to the Reviewer Guidance Layer and offers simple and
technical views. The contributor panel retains its existing entry point and
authority boundary.

`scripts/generate_reviewer_guidance_demos.py` produces eight scenario
directories with `guidance.json`, `report.md`, and `report.html` under
`examples/reviewer_guidance/outputs/`. These
outputs are not a formal experimental package, human verification, or an
acceptance record.

The generator shall default to deterministic research-fixture execution.
Deterministic identity shall arise while constructing domain records, never by
post-processing rendered HTML/Markdown/JSON. A scenario execution context shall
cover case, transition, evidence, finding, repair, verification, attestation
and other generated IDs; timestamps; authenticated selector tokens; and
fingerprints dependent on those runtime values. Scenario namespaces shall
prevent cross-scenario collisions.

Normal runtime execution shall retain random IDs, the real clock, and
non-public selector signing material. A fixed research-demo selector key shall
never process an ordinary user session. Running the generator twice in a
checkout with frozen outputs shall yield identical per-file SHA-256 hashes and
an empty `git status --short`.

## 21. Guidance semantic hardening requirements

### 21.1 Presentation boundary

The guidance layer shall provide stable Chinese participant-facing names and
plain requirements for the twelve canonical obligation IDs. Presentation text
shall not modify canonical `.agm` policy. Every row shall retain canonical
English and raw observed state. An unknown obligation shall render a non-empty
conservative fallback.

### 21.2 Dual requirement state

`RequirementComparison` shall carry `material_status`, `workflow_status`,
`blocking_requirement`, and `currently_blocks_progression` in addition to
compatibility result fields. `blocking_requirement` states whether the
compiled policy defines a blocking requirement;
`currently_blocks_progression` states whether that row blocks the case now.
Material
states are `missing`, `invalid`, `stale`, `provided`, `retained`, `verified`,
`overridden`, and `not_applicable`. Workflow states are
`blocks_progression`, `awaiting_contributor`, `awaiting_attestation`,
`awaiting_revalidation`, `awaiting_final_decision`, and `completed`.

Provided or retained repaired material awaiting maintainer revalidation shall
not be presented as missing or invalid.

The former Python properties `blocking` and `blocks_progression` may remain
read-only aliases with `DeprecationWarning`. Default new JSON shall emit only
the new names. A compatibility serializer may emit old names only when
explicitly requested.

### 21.3 Responsibility

Current responsibility shall be derived from blocking comparisons, evidence
validity, attestation status, open repair ownership, resubmission completeness,
revalidation scope, policy conflict, and final-decision readiness. It shall not
be derived from `GovernanceCase.state` alone. `resubmitted` with unresolved
contributor-side material shall remain contributor-side; valid scoped
resubmission shall hand off to an authorized verifier.

### 21.4 Action relevance and unavailable detail

The default-expanded group shall contain at most four current-relevant legal
actions. Other legal actions and unavailable actions shall be collapsed by
default. An unavailable action shall retain readable reason, required roles,
required states, category, future availability and traceability. Presentation
grouping shall not replace permission or state-machine checks.

### 21.5 Context selectors

The web panel shall use case-bound selector tokens rather than free-text
evidence, finding, attestation, obligation or repair IDs. Valid options shall
be rebuilt from current case state for each preview and confirmation. Forged,
stale, wrong-case, wrong-action and wrong-scope tokens shall be rejected.
Domain services shall continue to validate role, state, case membership and
scope. Non-interactive CLI interfaces may accept explicit IDs.

### 21.6 Read-only utilities

The view shall expose missing-requirement, contributor-checklist,
reviewer-summary, change-scope and handoff-note utilities. These actions shall
carry trace references and `state_changing=false`, and shall neither write
case storage nor append transitions.

### 21.7 Workflow traces

Each transition shall have exactly one primary five-step workflow node.
Secondary cross-references, if introduced, shall be explicitly marked. Step
details shall not indiscriminately repeat the complete transition log.

### 21.8 Preview projection

Preview shall remain pure and expose processed objects, state effects,
retained/invalidated material, before/after responsibility and workflow,
expected finding/repair/transition/verification/closure records, remaining
attestation and verification, and whether final acceptance occurred. The
preview fingerprint shall cover current case identity and submitted inputs.
Real execution shall repeat canonical authorization and scope validation.

The main preview shall not expose long evidence, finding, repair, transition,
or other opaque IDs. Obligation IDs may appear only as secondary/technical
text. The technical layer shall retain every canonical ID and raw state needed
to compare preview with actual execution.

### 21.9 Materiality, delegation, and lightweight paths

Materiality shall be presented as a declaration with declarer and reason,
affected/unaffected requirements, and a flag that maintainer inspection
remains necessary. The interface shall not claim semantic proof.

Delegation help shall distinguish subagent file/command/adopted-output or
independent-tool action from ordinary tool calls, reading, search, non-agentic
model calls, and advice-only assistance.

Lightweight/no-package paths shall be non-failure outcomes. Reduced process
intensity shall never authorize an agent to attest, verify, override, or make
the final project decision.

### 21.10 Reason presentation

Finding, repair, materiality and scope reasons shall use a structured
`GuidanceReasonPresentation` with Chinese `display_plain`, complete
`source_english`, optional `source_code`, and typed `trace_refs`. Selection
shall prefer reason/finding code or structured type and shall not depend on
demo filenames or exact full-sentence English matching. Unknown codes shall use
“系统记录了一项需要维护者查看的说明。” while retaining the source.

### 21.11 Rejected attempted operations

A denied operation shall be recorded as `AttemptedOperation` with operation,
actor/role, time, result, raw reason, required roles, before/after state, and
`state_changed`. It shall not advance case state, append a successful
transition, close a finding, or fabricate a new finding. The main page shall
show only the latest relevant `RejectedOperationView`; historical attempts
remain in technical detail. Successful operations shall not enter the rejected
collection.

### 21.12 Audit events versus transitions

`StateTransition` proves that an authorized lifecycle mutation took effect.
`AttemptedOperation` proves only that a call was attempted and rejected. Audit
display and analysis shall preserve this distinction, including transition
counts and finding status.

### 21.13 File-level reproducibility

The eight research demos shall be byte-for-byte reproducible across consecutive
generation runs. Tests shall cover stable IDs, timestamps, fingerprints,
selector tokens, scenario isolation, unchanged semantics versus runtime-random
mode, and a clean Git worktree after the second generation. These outputs
remain development research artifacts pending human review, not a formal
participant experiment package.

### 21.14 Cross-platform canonical research bytes

Research-demo text fixtures shall be UTF-8 with LF line endings and an explicit
final-newline policy before contribution fingerprinting. CRLF and CR input
shall normalize to the same bytes. Temporary textual policy/skill fixtures may
be normalized, but the canonical tracked `.agm` policy shall not be rewritten.
Binary fixtures shall bypass text normalization.

Serialized repository-relative paths shall use POSIX `/` separators. Absolute
temporary roots, local timezone/locale, platform permission modes, and
implicit filesystem enumeration order shall not enter research output or its
fingerprints. JSON, Markdown, and HTML outputs shall use stable ordering and LF
output bytes.

One frozen manifest,
`examples/reviewer_guidance/expected_sha256.json`, shall contain the canonical
SHA-256 values for exactly 25 generated files. Normal validation shall fail on
a missing, extra, or mismatched file and shall not update the freeze.
`scripts/check_reviewer_guidance_demo_hashes.py --update` is reserved for an
explicit researcher-reviewed change. Windows and Linux CI jobs shall both
generate and compare against this same manifest before running the complete
tests and a clean-diff check.

### 21.15 Participant-facing canonical term presentation

Reviewer-facing actions, roles, obligations, workflow nodes, record types, and
states shall use a backend `PresentedTerm(display_plain, canonical)` registry.
Known values shall have stable Chinese labels. Unknown values shall use a
neutral participant-facing fallback while retaining the unchanged canonical
value in technical details.

The Action Preview and rejected-operation main layers shall not lead with raw
values such as `verify_evidence`, `contributor_agent`, `O-SUMMARY`,
`maintainer_check`, or `maintainer_verification`. They shall show the
participant label and affected/retained consequence. Folded technical details
shall preserve the raw action, current and required roles, obligation IDs,
workflow nodes, record types, state, and trace references. This presentation
split shall not alter authority enforcement, state transitions, scoped repair,
responsibility derivation, selector validation, or preview purity.

## 22. Review Briefing Layer — Phase 1 and Phase 1.1

### 22.1 Purpose and authority

The Review Briefing Layer shall compile existing governance conclusions into
ordinary maintainer work. It is a read-only presentation/compiler layer above
Reviewer Guidance and shall not replace, delete, or change Reviewer Guidance.

Phase 1 and Phase 1.1 shall not perform item-level verification, request repair, reject
evidence, resubmit, attest, override, decide, close, merge, or mutate the case.
Its server shall expose no state-changing route.

### 22.2 Core model and API

The serializable model shall include:

1. `ReviewBriefView`
2. `ContributionBrief`
3. `RiskBrief`
4. `RequirementBrief`
5. `RequirementItem`
6. `AutomaticCheckResult`
7. `ContributorAccountabilityBrief`
8. `HumanJudgmentItem`
9. `NextStepBrief`
10. `GovernanceTechnicalDetails`
11. `WorkItemSummary`
12. `WorkOwner`
13. `BriefSemanticState`

The core API shall be:

```python
compile_review_brief(
    *,
    governance_case,
    policy_snapshot,
    contribution,
    actor_context,
) -> ReviewBriefView
```

Compilation shall be deterministic and side-effect free. It shall consume
recorded case risk, matched rules, compiled obligations, stable Reviewer
Guidance requirement comparisons and responsibility, evidence bindings,
attestations, findings, repair scope, attempted operations, verification,
migration diagnostics, and final decision. It shall not independently match
risk selectors, union obligations, derive permissions, authorize an operation,
or predict a state transition.

### 22.3 Epistemic categories

Participant presentation shall distinguish:

- material availability;
- structural validity;
- current-version binding;
- system-completed formal checking;
- agent or contributor declarations;
- accountable-human confirmation; and
- legal maintainer verification;
- final-decision eligibility and final acceptance; and
- unverified path/declaration-based inference.

Agent self-report shall not be labelled system-observed fact. A test command
and passing result shall not be labelled code correctness. Verification or
readiness shall not be labelled acceptance.

### 22.4 Contribution and risk briefs

`ContributionBrief` shall include title, plain summary, changed files,
component grouping, behavioral-impact navigation, security-sensitive paths,
configuration paths, governance paths, and agent-involvement wording. A path-
based semantic summary shall identify itself as a system inference and state
its limitations.

`RiskBrief` shall read the case's recorded overall risk and matched rules. It
shall explain every triggered risk area, affected-path reason, interaction
effect, and independent-review requirement in participant language. Canonical
rule IDs shall remain in technical detail.

### 22.5 Requirements and automatic checks

Every compiled requirement shall map to one current participant status and may
also expose the compatible semantic states:

- `material_available`;
- `structure_valid`;
- `version_bound`;
- `system_checked`;
- `human_review_required`;
- `human_verified`;
- `missing`;
- `stale`;
- `invalid`;
- `awaiting_accountable_human`;
- `awaiting_independent_review`; or
- `not_applicable`.

The original Phase 1 `status` field and bucket names shall remain available for
compatibility. Phase 1.1 presentation shall use the additive
`semantic_status` and `semantic_states` fields.

The main organization shall use requirement meaning rather than obligation ID.

Automatic checks shall cover current-version material binding, test
command/result structure, test-version binding, expiry, attestation-version
binding, declared versus recorded changed-file scope, recorded agent
involvement, recorded delegation declaration, denied authority attempts, and
structural obligations. Results shall state their evidence and limitations.
The automatic layer shall not ask a maintainer to repeat a formal check AGM has
already completed.

Each `AutomaticCheckResult` shall expose `policy_required`, `blocking`, safe
`requirement_refs`, `informational_only`, `owner`, and `system_handled`.
Missing or blocking wording shall require a compiled obligation, active
matched rule, binding requirement, existing finding, valid transition
prerequisite, or canonical migration diagnostic. Agent involvement alone
shall not create an agent-action-scope requirement. A non-required missing
declaration may be shown only as non-blocking information.

### 22.6 Accountability

`ContributorAccountabilityBrief` shall expose agent use, configured or
declared capabilities, recorded actions, delegation declaration, declaration
source/status, accountable-human identity, attestation status/scope/version
binding, and separate system-observed, declared, human-confirmed, and
unverified-inference groups.

AGM shall not infer authorship from a `human_direct` profile or missing agent
declaration.

### 22.7 Human judgment queue

Only content AGM cannot decide automatically shall enter
`HumanJudgmentItem`. Each item shall contain a stable presentation key, plain
title, reason a human is needed, contribution claim, system observation,
evidence summary, review focus, possible outcomes, priority, blocking meaning,
and a safe public trace reference. It shall also identify a safe requirement
reference and explicit governance provenance.

Missing, stale, invalid, pre-attestation, already verified, terminal, and
unaffected scoped-repair items shall not enter the queue. Scoped repair shall
produce only the recorded revalidation scope. A low-risk path may produce an
empty queue.

A denied attempted operation shall not create a judgment item. It shall be
shown as a system-handled anomaly and retained in technical audit detail.

### 22.8 Next-step routing

`NextStepBrief` shall select one business-level route and state the current
responsible party, what the system will do, what the human should do, and
whether final acceptance has occurred.

Valid routes include contribution-side update, accountable-human confirmation,
policy-migration attention, maintainer judgment, normal code review, final
authorized human decision, and completed/closed. The brief shall not present a
generic operation menu.

### 22.9 Participant information architecture

The Phase 1.1 main page order shall be:

1. contribution identity;
2. prominent current status and next step;
3. current human judgment queue when non-empty;
4. contribution and risk summary;
5. contribution-side or accountable-human outstanding work;
6. blocking problems and system-handled anomalies;
7. requirement and automatic-check summaries;
8. default-collapsed complete requirements;
9. default-collapsed passed checks and accountability detail; and
10. default-collapsed governance process and technical detail.

The five-step workflow shall not be the primary Review Brief navigation. Raw
state names, transition names, obligation/finding/evidence/repair IDs,
fingerprints, and generic action lists shall not appear in the participant-
visible main layer. Technical detail shall retain the complete records and
Reviewer Guidance view.

### 22.10 CLI, output, and scenarios

The Phase 1 command shall be:

```bash
python -m agm.vnext.cli maintainer brief \
  --case CASE --actor HUMAN --role maintainer --serve
```

It shall write `brief.json`, `brief.md`, and `brief.html` beside the case.
Serving shall remain loopback-only and read-only.

`scripts/generate_review_briefing_demos.py` shall compile the existing eight
Reviewer Guidance governance cases into the same three output formats under
`examples/review_briefing/outputs/`. The output is a design-review fixture, not
a P92 experiment package, human verification, final decision, acceptance, or
merge approval.

### 22.11 Phase 1.1 determinism and review boundary

`scripts/check_review_briefing_demo_hashes.py` shall verify frozen SHA-256
values for all eight JSON/Markdown/HTML triples and `manifest.json`.
Windows and Ubuntu CI shall explicitly regenerate the Review Briefing demos,
check their hashes, and require a clean diff. Participant-visible demo prose
shall use natural contribution language. Fixture actor IDs, generator names,
raw states, IDs, traces, and fingerprints shall remain in folded technical
detail.

The artifact shall remain pending human review. Phase 1.1 shall not be
described as human-approved, shall not start Phase 2, and shall not produce a
P92 experiment package.
