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
