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
