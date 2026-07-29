# AGM vNext Design Development

Status: `v0.2-dev`; new design development, not part of the reported v0.1.0
evaluation

The complete conceptual working baseline is retained in
`AGM_vNext_Work_Package/AGM_vNext_Conceptual_Doctrine_CN.md`. This document is
its implementation-oriented companion.

## Definition

AGM is project-side governance infrastructure that resolves project rules
against a concrete contribution, compiles contribution-specific obligations
and authority boundaries, binds evidence and human accountability to the
actual change, and supports authorized verification, repair, final human
decision, and auditable closure.

Phase 2.1 adds `pr_diagnostic` as a second, PR-native projection of the same compiled case. The projection has no independent rule matching. Its evidence packages are runtime-only, digest-immutable sidecars.

Phase 2.1.1 derives routes from existing responsibility, lifecycle stage, gate, and legal operations; it does not change canonical policy or lifecycle semantics.

The four v0.1 observable domains—risk, evidence, accountability, and review
gate—remain useful diagnostics. They are not the complete AGM ontology.

## Lifecycle

The normative lifecycle is:

`Resolve -> Compile -> Bind -> Attest -> Verify -> Repair -> Decide -> Record`

| Stage | Implementation result |
| --- | --- |
| Resolve | Applicable policy snapshot and complete matched-rule set |
| Compile | Deduplicated contribution-specific obligation set |
| Bind | Evidence linked to obligations, scope, contribution fingerprint, environment, and time |
| Attest | Explicit append-only accountable-human event |
| Verify | Independent, role-authorized maintainer verification |
| Repair | Findings, scoped repair request, resubmission, and partial revalidation |
| Decide | Authorized human-maintainer decision or override |
| Record | Transition history and terminal closure receipt |

## Non-negotiable semantics

- AGM is not an AI detector.
- No package means `no_agm_package_submitted`, not confirmed human authorship.
- A project may require structured governance because of the change itself,
  regardless of contributor identity.
- Risk and agent autonomy are orthogonal inputs.
- Overall risk is a summary. Obligations come from the complete matched-rule
  set, autonomy and assurance profiles, and interaction rules.
- Blocking obligations complete conjunctively.
- Evidence, attestations, and verifications are invalidated only where their
  bindings become stale.
- Agents may prepare and propose; they may not attest as humans, verify as
  maintainers, override policy, or make final decisions.
- Ready or verified never means accepted or merged.
- Final authority remains with authorized human maintainers.

## Runtime and policy boundaries

- `.agm/` stores versioned canonical policy, roles, workflows, interfaces, and
  agent protocol entrypoints.
- `.agm-work/` stores local runtime governance cases and is ignored by default.
- `src/agm/governance.py` preserves v0.1 behavior.
- `src/agm/vnext/` implements development schema identifiers ending in
  `/v0.2-dev`.

Every case records the base commit, policy fingerprint, contribution
fingerprint, applicable schema versions, and opening time. Policy changes are
diagnosed; migration is never silent.

## Multi-risk compilation

All matching rules are facts. Compilation uses:

- union for distinct obligations;
- stable-ID deduplication for identical obligations;
- blocking over warning and highest severity for compatible duplicates;
- explicit findings for incompatible obligation definitions;
- interaction rules for combination-specific escalation; and
- conjunction across all unresolved blocking obligations.

Every compiled obligation retains its triggering rule IDs and affected scope.

## Authority boundary

Roles are mapped to operations in canonical policy. State transitions record
actor, role, source, target, action, reason, related objects, and timestamp.
State history is append-only. UI controls are advisory; authorization is
rechecked by the domain service before any mutation.

Human attestation, maintainer verification, repair, override, and final
decision are distinct events. A terminal decision produces a closure receipt
that preserves unresolved but explicitly accepted exceptions.

## Reviewer Guidance Layer

`src/agm/vnext/guidance/` is a pure presentation layer over the lifecycle
records. It does not resolve risks or compile obligations a second time.

The layer produces:

- a plain-language contribution summary;
- a five-step workflow view over the internal eight-stage lifecycle;
- one reference-versus-observed row per compiled obligation;
- findings and scoped repair explanations;
- authority-aligned available and unavailable actions;
- deterministic, non-mutating transition previews; and
- default-collapsed raw technical detail.

The five user steps are:

| User step | Internal stages |
| --- | --- |
| 系统识别要求 | Resolve, Compile |
| 贡献者准备材料 | Bind, Repair |
| 负责人确认 | Attest |
| 维护者检查 | Verify, Repair |
| 人类维护者最终决定 | Decide, Record |

All presentation rows carry typed references back to rules, obligations,
evidence, attestations, findings, repairs, permissions, or transitions. The
HTML contains localization and layout only; backend domain services remain the
authorization and mutation boundary.

The local maintainer panel is two-stage. The first POST generates a pure
`ActionPreview`; the second supplies the preview fingerprint and requests the
real operation. If case state or inputs changed, confirmation fails and a new
preview is required.

Material resubmission retains unaffected bindings explicitly rather than
rewriting their original contribution fingerprint. The retained record names
the new contribution fingerprint and a reason. Repair attempts record stale,
retained, invalidated, and revalidation scopes for guidance traceability.

See `docs/AGM_REVIEWER_GUIDANCE_LAYER.md` for state definitions and
`docs/AGM_MAINTAINER_GUIDE.md` for operation guidance.

## Review Briefing Layer and human-work compilation

`src/agm/vnext/briefing/` adds a higher presentation/compiler layer without
replacing Reviewer Guidance. Reviewer Guidance explains governance state,
traceability, and legal operations to a governance-aware reviewer. Review
Briefing explains the work itself to an ordinary maintainer:

- what changed and which component paths are involved;
- the engine-recorded risk level and its matched-rule/interaction reasons;
- what the project requires and which items are complete, missing, stale,
  invalid, awaiting an accountable human, or awaiting independent review;
- formal facts the system has already checked;
- declared content whose truth or semantic fit still needs a human;
- contributor-agent and accountable-human provenance categories;
- the smallest queue of concrete human judgments; and
- one responsibility-aligned next step.

This is a second compiler boundary:

```text
governance-state compiler -> Reviewer Guidance -> human-work compiler
```

The human-work compiler consumes the same `RequirementComparison`,
responsibility derivation, matched rules, compiled obligations, bindings,
findings, repair scope, attestation, verification, and final-decision records.
It does not resolve policy or authority again. Its technical detail embeds the
Reviewer Guidance view and complete canonical records, so disagreement between
the two views is a defect rather than a permissible presentation choice.

The epistemic boundary is explicit. Phase 1.1 no longer uses a broad
“system-confirmed” category. Material availability, structural validity,
current-version binding, system checking, human content review, maintainer
verification, final-decision eligibility, and acceptance are separate states.
Test-record completeness is never described as code correctness. Agent self-
report is never described as system-observed behavior.

The human judgment queue excludes missing, stale, invalid, or pre-attestation
work. Every item carries compiled-requirement, maintainer-stage, finding,
independent-review, or scoped-revalidation provenance. A denied operation is a
system-handled audit anomaly and cannot supply provenance for a new judgment.
Scoped repair yields only its revalidation scope; a low-risk path can yield no
extra AGM judgment.

`AutomaticCheckResult` identifies whether a check is canonical-policy
required, blocking, informational-only, and system-handled. Missing
agent-action scope is blocking only when `O-AGENT-SCOPE` was compiled. The
brief cannot turn agent involvement into an implicit policy requirement.

`WorkOwner` makes each unresolved item system-, contribution-side-,
accountable-human-, maintainer-, or final-decision-authority-owned.
`NextStepBrief` then routes to one of those owners without exposing a generic
action menu.

Phase 1.1 is entirely read-only. The page puts the current route first, then
human judgments, change/risk, current-owner work, and blocking problems.
Complete requirements, passed checks, accountability details, and technical
records are closed by default. `maintainer brief` writes `brief.json`,
`brief.md`, and `brief.html`; its loopback server accepts GET only. Raw
workflow, state, obligation/finding/evidence/repair IDs, transition names, and
fingerprints remain default-collapsed.

See `docs/AGM_REVIEW_BRIEFING_LAYER.md` for the complete model, routing rules,
information architecture, and Phase 1.1 limitations.

## Reviewer guidance semantic hardening

Participant-facing Chinese is presentation metadata keyed by canonical
obligation ID. It is not written into `.agm`, and raw canonical English remains
in every comparison row and technical detail. Unknown future obligations use a
safe non-empty fallback.

Reviewer-facing finding, repair, materiality and scope reasons follow the same
boundary through `GuidanceReasonPresentation`. Structured codes select concise
Chinese presentation; complete source English and typed trace references remain
available. Unknown reason codes use a neutral fallback rather than sentence
matching or scenario-specific presentation.

`RequirementComparison` models two orthogonal axes:

- material: missing, invalid, stale, provided, retained, verified, overridden,
  or not applicable; and
- workflow: blocked, awaiting contribution, attestation, revalidation, final
  decision, or completed.

This prevents valid repaired material from being labelled invalid merely
because a finding remains open until scoped revalidation.

The boolean names follow the same separation:
`blocking_requirement` is the compiled policy property, while
`currently_blocks_progression` is the current workflow consequence. Deprecated
Python aliases preserve early source consumers; default serialization emits
only the clear names.

`ResponsibilityView` is derived from unresolved material, findings, repairs,
attestations, policy conflicts, revalidation scope and readiness. Case state is
one input, not the only input. A resubmitted case with stale contributor-side
material therefore stays with the contributor side.

The action surface has three layers:

1. no more than four current-relevant legal actions;
2. default-collapsed other legal actions; and
3. default-collapsed unavailable actions with role/state/future explanations.

This relevance model is presentation-only. Canonical permissions, transitions
and service validation remain authoritative.

Web mutation forms use current-case `ContextSelectorOption` objects. Opaque
tokens bind case, contribution fingerprint, action, object kind and scope. The
server rebuilds and resolves selectors on preview and confirmation, rejecting
unknown, stale, wrong-case, wrong-action and wrong-scope selections. Domain
services still validate IDs and repair/override/conflict scope.

`GuidanceUtilityAction` provides read-only checklists, summaries, change scope
and handoff notes. Utility generation consumes comparison rows and trace
references and never writes case storage or transition history.

Workflow trace mapping assigns each transition to one primary user step.
Compiled rules/obligations, evidence, attestations, verification/findings and
decision/closure records are attached only to their relevant step.

Action previews project onto a deep-copied case. Besides target state, they
expose processed objects, retained/invalidated records, before/after
responsibility and workflow, expected record types, remaining attestation and
verification, and the fact that final acceptance remains outstanding unless a
human accept action is actually being previewed.

The preview model separates Chinese `display_effects` and named
affected/retained items from `technical_details`. Canonical IDs, raw states,
operation names, internal workflow nodes, created record types and trace
references remain complete but default-collapsed. Preview execution and
fingerprinting continue to use the technical values; the split is
presentation-only and the projection remains side-effect free.

Materiality remains an actor declaration, not an objective semantic proof.
The view identifies classification, declarer, reason, affected/unaffected
requirements, stale/retained records and the continuing need for maintainer
inspection. Lightweight and ordinary paths reduce governance intensity only;
they never transfer final authority to an agent.

## Final presentation and reproducibility design

Denied state-changing calls to verification, final decision, and override are
recorded as append-only `AttemptedOperation` audit facts. A rejected audit event
records before/after state and required roles but is neither
`GovernanceFinding` nor `StateTransition`. `RejectedOperationView` surfaces the
latest denial without changing responsibility, readiness, or case state;
successful actions do not enter the rejected collection.

The eight public research demonstrations install a scenario-scoped
`DemoExecutionContext`. Its clock is fixed, its UUID5 identifier factory uses
`scenario namespace + record type + ordinal`, and its selector secret is
derived from a demo-only key plus scenario namespace. This makes source domain
records, HMAC selector tokens, timestamps, transition-log hashes, preview
fingerprints, and rendered files deterministic without HTML rewriting.

The default `RuntimeExecutionContext` continues to use UUID4 identifiers, the
real UTC clock, and process-random selector secret material. The deterministic
context is installed only around demo generation and is restored afterward.
Consequently a fixed demo key cannot leak into ordinary sessions and
`--runtime-random` exercises the normal path for semantic comparison.

Cross-platform byte identity is established before fingerprinting rather than
by rewriting rendered output. A single deterministic fixture writer
normalizes CRLF/CR to LF, encodes UTF-8 directly, and controls the final
newline. Temporary copies of textual policy and skill fixtures use that
writer, which makes the governance self-modification scenario independent of
Git checkout newline settings without changing tracked `.agm` files.
Repository-relative paths are POSIX-serialized and output enumeration is
ordered. Fingerprints intentionally ignore filesystem permission mode unless a
future policy explicitly makes mode a governance input.

The 25 generated files are frozen in
`examples/reviewer_guidance/expected_sha256.json` and checked by
`scripts/check_reviewer_guidance_demo_hashes.py`. The freeze is shared by the
Windows/Ubuntu CI matrix; same-process equality alone is insufficient.
Updating the freeze is an explicit researcher action.

Participant-facing canonical vocabulary is centralized in a presentation
registry. `PresentedTerm` carries `display_plain` and `canonical`, with
registries for actions, roles, obligations, workflow nodes, record types, and
states. Builders and error formatters consume the registry, so HTML templates
do not become an independent translation authority. Main-layer preview and
audit text uses display labels; canonical values remain available in folded
technical details and continue to drive authority checks, selectors,
projection, execution, and trace mapping.

## Phase 2 contextual human-judgment actions

Phase 2 extends the Human-Work Compiler without changing the governance-state
compiler:

```text
Canonical Governance Objects
        -> Review Briefing Compiler
        -> ReviewBriefView
        -> Contextual Action Compiler
        -> Interactive Maintainer Review
```

`JudgmentOption` belongs to one canonical `HumanJudgmentItem`. The default
business outcomes are material sufficient, supplement/correct, and material
risk. Availability is server/domain data derived from current state,
canonical human role, permissions, obligation verifier roles, and recorded
separation-of-duty facts. Templates only render that result.

Selections first enter a `ReviewDecisionDraft` under `.agm-work`. A draft
binds actor, role, case, contribution fingerprint, policy snapshot,
requirement references, and judgment provenance. It is not verification or
governance state. Any binding or judgment change makes it stale.

Preview reloads the case, recompiles `ReviewBriefView`, rechecks authority and
all bindings, and returns a short-lived one-time session token. Execution
accepts only that token and maps the plan to existing domain operations:

- an all-sufficient batch uses `verify_evidence` and the existing system
  `mark_ready` route;
- supplement and material-risk results use the existing blocking
  `request_repair`/finding mechanism with obligation-scoped revalidation; and
- no review action calls `decide_*`.

If the state machine has no semantically correct operation, the option is
disabled. In particular, raw `resubmitted` supports contribution-side
preparation but no maintainer repair request. It therefore exposes no
maintainer judgment actions. After complete, bound material passes existing
`prepare_case()`, the contribution-side `submit_for_verification` operation
enters `awaiting_maintainer_verification`, where all three contextual outcomes
have legal existing mappings. Phase 2.0.1 adds no transition and does not
route through false verification.

The final decision is a different compiler and page. It appears only in
`ready_for_human_decision` or `overridden`, rechecks final authority, exposes
only supported `decide_*` operations, and requires a separate preview. Review
completion never performs, redirects into, or implies final acceptance.

The local service remains loopback-only. Mutations are POST-only and require
a session CSRF token, loopback host/origin, fixed case/actor context, safe
content type and size, current fingerprints/provenance, and an unused,
unexpired preview token. Submitted interaction records and rejected attempts
are append-only runtime audit facts; they are not canonical `.agm` policy.

Participant-facing draft banners are conditional: no-task and no-authority
views show no unfinished-work warning; actionable items distinguish
unselected, selected, previewed, stale, and submitted states. The separate
final-decision main layer uses ordinary project language. Internal actor,
operation, transition, obligation, fingerprint, and token data remains in a
default-folded technical section.

Frozen interactive outputs use LF on every platform. Repository delivery ZIPs
are built from Git blob content rather than the Windows working tree and are
verified in a clean extraction before any generator runs.
