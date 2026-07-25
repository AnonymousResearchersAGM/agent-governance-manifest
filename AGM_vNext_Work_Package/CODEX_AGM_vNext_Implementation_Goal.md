# Codex Goal: Implement AGM vNext on an Isolated Development Branch

## Mission

Upgrade the current Agent Governance Manifest prototype from a compact v0.1.0 research artifact into a vNext development prototype that implements contribution-level governance instantiation, multi-risk obligation compilation, human-operable contributor and maintainer workflows, authority-typed state transitions, repair loops, and workflow embedding.

The current repository is a valid, tested v0.1.0 research snapshot. Preserve its historical and evidentiary boundary. Do not silently rewrite the reported artifact as though the new features existed in the earlier evaluation.

Read these files before coding:

1. `AGM_vNext_Conceptual_Doctrine_CN.md` (provided with this goal; copy it into `docs/AGM_VNEXT_DESIGN.md` or create an English implementation-oriented companion document).
2. `AGM_v0.1.0_Artifact_Anatomy_and_Multi_Risk_Diagnosis.md`.
3. Existing `.agm/*`, `src/agm/governance.py`, scripts, tests, skills, `AGENTS.md`, `CLAUDE.md`, and current docs.

## Git and versioning rules

1. Confirm the working tree is clean.
2. Create and work only on a new branch named `v0.2-dev` (use a collision-safe suffix only if it already exists).
3. Never force-push and never rewrite `main` history.
4. Record the current base commit in `docs/V0_1_RESEARCH_SNAPSHOT.md`.
5. Preserve the existing v0.1.0 behavior through compatibility tests or an explicit compatibility module.
6. Use development schema identifiers such as `agm.* /v0.2-dev`; do not call this a stable v0.2.0 release.
7. Push only the new development branch after all acceptance criteria pass. Do not merge to `main`.

## Non-negotiable governance constraints

- AGM is not an AI detector.
- Absence of AGM materials must mean `no_agm_package_submitted`, not confirmed human authorship.
- Ordinary human contributions must remain possible without forced AGM form filling, unless project risk policy requires structured evidence for the change itself.
- Risk and agent autonomy are orthogonal dimensions.
- Multi-risk contributions must retain every matched rule. Overall highest risk is a summary, not the sole source of obligations.
- Required obligations are compiled from the union of matched rules, autonomy profile, and interaction rules.
- Evidence must bind to specific obligations and the actual contribution/diff.
- Agents may propose assessments and prepare evidence, but may not perform human attestation, maintainer verification, override, final acceptance, rejection, or merge decisions.
- `pass` or `ready` must never mean accepted.
- Human attestation and maintainer operations must be visible, explicit, and append-only/auditable.
- Final decisions remain with authorized human maintainers.
- New vNext behavior must not be represented as validated by the existing v0.1.0 studies.

## Target lifecycle

Implement the following lifecycle as explicit domain behavior:

`Resolve -> Compile -> Bind -> Attest -> Verify -> Repair -> Decide -> Record`

## Target domain objects

Implement typed models (dataclasses or similarly explicit validated structures) for at least:

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

Every record must have a stable ID and timestamps where appropriate. State transitions must record actor, role, source state, target state, action, reason, and related object IDs.

## Recommended repository architecture

Keep the old v0.1 module usable while adding a clean vNext package:

```text
src/agm/
  governance.py                 # v0.1 compatibility; avoid destructive redesign
  vnext/
    __init__.py
    models.py
    config.py
    policy.py
    risk.py
    obligations.py
    evidence.py
    attestations.py
    state_machine.py
    repair.py
    reporting.py
    storage.py
    ui.py
    cli.py
```

Add a project configuration structure similar to:

```text
.agm/
  manifest.yml
  policies/
    risk_rules.yml
    evidence_profiles.yml
    interaction_rules.yml
  profiles/
    autonomy_profiles.yml
    assurance_profiles.yml
  roles/
    roles.yml
    permissions.yml
  workflows/
    state_machine.yml
  interfaces/
    contributor_panel.yml
    maintainer_panel.yml
    governance_report.yml
    messages.yml
  agents/
    entrypoints.yml
    contributor_protocol.md
    maintainer_protocol.md
  schemas/
    *.schema.json
```

Preserve exact copies of the current v0.1 canonical files under a clearly marked snapshot directory, or document their immutable base commit. Do not mix runtime case state into canonical policy files.

Use `.agm-work/` for runtime cases:

```text
.agm-work/
  cases/<case-id>/
    case.yml
    policy_snapshot.yml
    matched_rules.yml
    obligations.yml
    evidence.yml
    attestations.yml
    transitions.jsonl
    findings.yml
    report.html
    report.md
    closure_receipt.yml
```

Add `.agm-work/` to `.gitignore` by default, except curated examples/fixtures stored elsewhere.

## Functional work packages

### WP1 — Preserve and characterize v0.1

- Keep all 23 current tests passing.
- Add a snapshot/compatibility test demonstrating current v0.1 highest-risk behavior, so the historical behavior is explicit.
- Document that v0.1 retained all detected zones for display but selected evidence requirements only from the highest risk level.

### WP2 — Configuration and schema validation

Create vNext schemas and loaders for:

- roles and permissions;
- risk rules with multiple selector types;
- evidence obligations;
- autonomy profiles;
- interaction rules;
- state machine transitions;
- interface configuration.

At minimum, selectors must support:

- path/glob selectors;
- change-type tags supplied by analysis or user;
- named semantic targets/symbol labels supplied by analysis;
- governance-entrypoint changes.

Design extension points for AST/symbol analyzers without requiring a heavy parser in this prototype.

Configuration errors must be explicit and fail safely. Detect duplicate IDs, unknown roles, unknown transitions, unknown obligation references, cyclic/invalid state definitions, and conflicting blocking semantics.

### WP3 — Ordinary and AGM-managed paths

Implement contribution intake modes:

- `ordinary`: no AGM package submitted; no claim of human authorship;
- `declared_agent_mediated`: contributor/agent starts AGM voluntarily;
- `policy_required`: project policy requires AGM for the actual change/risk;
- optional `maintainer_requested`: maintainer requests structured AGM preparation.

The system must explain why a case is or is not required. Do not infer AI use from absence or presence of files.

### WP4 — Multi-risk resolution and obligation compilation

Replace highest-risk-only obligation selection in vNext with:

- complete `MatchedRuleSet`;
- `overall_risk_level` retained only as summary;
- union and de-duplication of obligations;
- provenance from each obligation back to source rules;
- per-obligation severity, blocking mode, verifier role, evidence type, and affected scope;
- interaction rules that can add obligations, require independent review, or escalate assurance.

Implement deterministic conflict rules:

- highest risk wins only for the overall summary;
- obligations are unioned by stable obligation ID;
- blocking overrides warning for the same obligation;
- contradictory rules create an explicit policy conflict finding rather than silently choosing the last value;
- authorized policy exceptions must be explicit and recorded.

Add tests for at least:

1. low + critical paths;
2. two different high-risk zones with distinct obligations;
3. governance policy + governance runtime interaction requiring independent review;
4. duplicate obligation de-duplication;
5. contradictory rule conflict;
6. unknown path conservative fallback without discarding other matched rules.

### WP5 — Evidence binding and validity

Each evidence item must contain:

- stable ID;
- obligation IDs satisfied;
- affected files/scopes;
- contribution/diff fingerprint;
- command and environment where applicable;
- artifact path and optional hash;
- generated/observed timestamp;
- optional expiry;
- source actor/tool;
- current validity state.

Implement checks for:

- missing evidence;
- placeholders;
- referenced artifact missing;
- evidence-to-file mismatch;
- evidence bound to stale diff;
- expired evidence;
- unverifiable provenance fields;
- conflicting evidence;
- evidence satisfying no known obligation.

Use local deterministic hashing. Do not require external services.

### WP6 — Human attestation workflow and contributor panel

Human attestation must be a first-class event, not direct manual editing of a deeply nested YAML field.

Implement a contributor command such as:

```bash
python -m agm.vnext.cli contributor prepare ...
python -m agm.vnext.cli contributor review --case <id> --serve
```

Provide both:

- standalone friendly HTML served locally using the Python standard library or a minimal justified dependency;
- Markdown/CLI fallback.

The panel must prominently show:

- exact contribution/diff fingerprint;
- matched risk areas;
- compiled obligations;
- evidence and gaps;
- scope the human is being asked to review;
- explicit actions: confirm reviewed scope, request correction, decline to attest.

On confirmation, record actor, timestamp, reviewed scope, statement, reservations, policy version, case fingerprint, and evidence-set fingerprint.

If the diff/evidence changes materially, invalidate only affected attestations and explain why.

An agent must never be able to set `human_attested` without an explicit human operation.

### WP7 — Maintainer report and authorized operations

Implement a maintainer command such as:

```bash
python -m agm.vnext.cli maintainer inspect --case <id> --serve
```

The maintainer report should resemble a governance laboratory report, with:

- case identity;
- applicable policy snapshot;
- overall readiness;
- per-risk-area table;
- per-obligation reference vs observed status;
- anomalies/findings;
- human attestations;
- evidence binding validity;
- repair history;
- authority boundary notice.

Implement authorized operations:

- verify evidence;
- reject evidence;
- request repair;
- ask for clarification;
- invalidate an attestation with reason;
- record policy conflict;
- authorized override with reason and actor;
- final accept/reject/request changes/close decision.

Each operation must go through the state machine and append a transition record. The UI/CLI must reject unauthorized transitions.

### WP8 — State machine, repair loop, and closure

Define explicit states, at minimum covering:

- `ordinary_unmanaged`;
- `case_opened`;
- `policy_resolved`;
- `obligations_compiled`;
- `evidence_incomplete`;
- `awaiting_human_attestation`;
- `awaiting_maintainer_verification`;
- `repair_requested`;
- `resubmitted`;
- `verification_complete`;
- `ready_for_human_decision`;
- `overridden`;
- `accepted`;
- `rejected`;
- `closed`.

Use sub-status/per-obligation status rather than forcing every case into one coarse scalar state.

Repair requests must specify findings, responsible role, affected obligations, requested correction, and what will need revalidation. Preserve previous attempts and transition history.

Generate a `ClosureReceipt` for every terminal decision.

### WP9 — Discovery adapters, Skills, and dedicated-agent protocols

Update `AGENTS.md`, `CLAUDE.md`, and relevant docs so they remain short discovery pointers to canonical `.agm/` rules and lifecycle protocols.

Upgrade the two Skills from descriptive notes to executable lifecycle protocols:

- contributor Skill: discover -> preflight -> inspect diff -> resolve multi-risk -> compile -> gather -> validate -> pause for human attestation -> bind -> revalidate -> prepare submission;
- maintainer Skill: load base policy -> independently resolve -> verify binding -> produce report -> execute authorized operation -> repair/close.

Add dedicated, harness-neutral protocol documents for:

- AGM Contribution Steward;
- AGM Review Steward.

Do not make dedicated agents mandatory. Document three adoption levels:

1. discovery pointer only;
2. ordinary agent + portable AGM Skill;
3. dedicated AGM Steward agent.

### WP10 — Project governance console (minimum viable prototype)

Provide at least a read-only/configuration-preview command that:

- validates project policy;
- lists roles, risk rules, profiles, and transitions;
- simulates a changed-file set and displays matched rules/compiled obligations;
- detects policy conflicts;
- previews migration impact.

A full graphical editor is optional for this iteration. Do not sacrifice the contributor and maintainer panels for it.

### WP11 — Versioning and migration

Record in each case:

- base commit;
- manifest/schema version;
- policy fingerprint;
- when the case was opened;
- whether policy changed during review.

Implement a migration diagnostic that reports:

- still valid obligations;
- added/removed obligations;
- evidence requiring revalidation;
- attestations invalidated;
- whether the case may remain on its original snapshot or must migrate.

No silent migration.

### WP12 — Documentation and end-to-end examples

Create or update:

- `docs/AGM_VNEXT_DESIGN.md`;
- `docs/AGM_VNEXT_SPEC.md`;
- `docs/V0_1_RESEARCH_SNAPSHOT.md`;
- contributor and maintainer user guides;
- adoption/migration guide;
- authority and state model documentation;
- multi-risk example;
- ordinary human contribution example;
- stale evidence example;
- repair-loop example;
- governance self-modification example;
- closure receipt example.

Clearly label all vNext material as new design development, not part of the reported v0.1.0 evaluation.

## Required CLI user experience

Provide discoverable `--help` output and commands equivalent to:

```bash
python -m agm.vnext.cli project validate
python -m agm.vnext.cli project simulate --changed-file ...
python -m agm.vnext.cli contributor open-case ...
python -m agm.vnext.cli contributor prepare --case ...
python -m agm.vnext.cli contributor review --case ... [--serve]
python -m agm.vnext.cli case status --case ...
python -m agm.vnext.cli maintainer inspect --case ... [--serve]
python -m agm.vnext.cli maintainer request-repair --case ...
python -m agm.vnext.cli maintainer verify --case ...
python -m agm.vnext.cli maintainer decide --case ...
python -m agm.vnext.cli case migrate-check --case ...
```

Exact naming may vary, but separate contributor, maintainer, project, and case responsibilities.

## Security and correctness requirements

- Never use `eval` or unsafe YAML loading.
- Prevent path traversal for evidence artifacts and case storage.
- Escape all user-controlled content in HTML.
- Bind local UI actions to loopback only and use a per-session CSRF/action token if forms mutate files.
- Do not expose a network service beyond localhost.
- Use atomic writes for case state and append-only JSONL for transitions.
- Validate role and transition authorization server-side, not only in UI controls.
- Avoid adding large frameworks unless justified; prefer standard library + existing dependencies.

## Testing requirements

Keep all existing tests passing and add comprehensive vNext tests. Target at least 60 total tests, covering:

- schema/config errors;
- ordinary path semantics;
- policy-required cases;
- multi-risk union and interaction;
- autonomy profiles;
- evidence binding, expiry, mismatch, and conflict;
- attestation creation and invalidation;
- unauthorized state transitions;
- maintainer operations;
- repair/resubmission;
- version migration;
- HTML escaping and local action validation;
- closure receipt;
- end-to-end successful and failed cases.

Use temporary directories and deterministic timestamps/fingerprints where practical.

## Required end-to-end demonstration scenarios

1. Ordinary human documentation PR with no AGM package.
2. Agent-mediated low-risk documentation change.
3. Critical authentication + high configuration multi-risk contribution.
4. Governance rule + governance runtime self-modification requiring independent review.
5. Evidence bound to stale diff.
6. Pending human attestation, followed by explicit confirmation.
7. Maintainer repair request, contributor resubmission, partial revalidation, final decision.
8. Authorized override with recorded rationale.
9. Policy version changes while a case is open.
10. Conflicting rules that block readiness until policy resolution.

## Implementation cadence and commits

Use small, reviewable commits. Suggested sequence:

1. `docs: record v0.1 snapshot and vnext design`
2. `feat: add vnext domain models and config schemas`
3. `feat: add multi-risk resolver and obligation compiler`
4. `feat: add evidence binding and attestation records`
5. `feat: add authority-typed state machine and repair loop`
6. `feat: add contributor panel and workflow`
7. `feat: add maintainer report and operations`
8. `feat: add discovery adapters and executable skills`
9. `feat: add migration diagnostics and closure receipts`
10. `test: add vnext integration and failure scenarios`
11. `docs: complete vnext guides and examples`

Run after each meaningful stage:

```bash
pytest -q
```

Before push, also run a clean-clone or fresh temporary-directory smoke test of the documented commands.

## Definition of done

The work is complete only when:

- all existing and new tests pass;
- v0.1.0 research behavior is preserved/documented;
- multi-risk obligations are truly compiled rather than collapsed to highest risk;
- ordinary contributions are supported without false human-authorship claims;
- human attestation is a visible operation bound to the actual case state;
- maintainer verification, repair, override, and final decision are distinct authorized operations;
- contributor and maintainer HTML/Markdown panels are usable;
- transition history and closure receipt are produced;
- discovery adapters and Skills point to the canonical `.agm/` source;
- README/spec clearly separate v0.1.0 reported evidence from vNext development;
- branch `v0.2-dev` is committed and pushed without merging to `main`.

## Final Codex report

At completion, provide:

1. branch and final commit hash;
2. exact files added/changed;
3. architectural summary;
4. commands to run both panels and the demonstration;
5. test count and results;
6. known limitations;
7. any design decisions that differ from this goal and why;
8. confirmation that `main` and the v0.1.0 historical boundary were not overwritten.
