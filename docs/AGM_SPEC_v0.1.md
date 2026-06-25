# Agent Governance Manifest Specification v0.1 — Community Draft

Version: v0.1.0

Status: Community Draft

## 1. Purpose

Agent Governance Manifest (AGM) is project-side governance infrastructure for agent-mediated contributions. It makes project risk zones, minimum evidence requirements, human review declarations, and review gates explicit before a contribution enters human maintainer review.

AGM operates at the project-side governability layer of AI-mediated open-source software (OSS) governance. It complements agent-readability entrypoints such as `AGENTS.md` and `CLAUDE.md`, and it can coexist with traceability formats such as Agent Trace, but it does not replace or depend on either.

AGM turns an agent-mediated contribution into a reviewable project object. By structuring risk classification and evidence preparation upfront, AGM reduces maintainer verification burden, improves review readiness, and preserves human decision authority. It does not decide whether the contribution should be accepted.

## 2. Non-goals

AGM is not:

- `AGENTS.md` or `CLAUDE.md`;
- a pull request (PR) template;
- an AI detector;
- an agent trace or provenance log system;
- an automatic merge or reject tool;
- a replacement for independent code review;
- a replacement for human maintainer judgment.

AGM defines a project-side governance interface. It does not require contributors to disclose private prompts, chain-of-thought, full agent traces, or exploratory reasoning.

## 3. Trust Model and Enforcement Boundaries

AGM is a governance coordination mechanism, not a cryptographic enforcement mechanism. It cannot prevent contributors from ignoring AGM rules, omitting evidence, or fabricating declarations. It also cannot prove that a human review declaration is truthful without additional identity, signing, audit, or platform-level mechanisms.

The purpose of AGM v0.1 is more limited: it lowers the cost of compliant behavior, makes project governance expectations explicit, and helps maintainers detect missing, inconsistent, placeholder, or incomplete evidence before human review.

Projects that require stronger guarantees may combine AGM with additional mechanisms such as signed commits, CI enforcement, maintainer approval rules, artifact attestation, provenance records, or platform-level policy gates. These mechanisms are complementary to AGM and are outside the scope of this v0.1 specification.

## 4. Core Design Principles

AGM v0.1 follows five design principles.

1. **Evidence-based governance.** Governance readiness should be assessed through explicit, reviewable evidence rather than trust in contributor identity alone.
2. **Risk-zoned proportionality.** Evidence requirements should scale with the risk of affected files, functions, interfaces, or governance areas.
3. **Two-sided governance contract.** Contributor-side agents prepare evidence according to project rules, while maintainer-side agents or human reviewers diagnose readiness against the same rules.
4. **Evidence disclosure without reasoning disclosure.** AGM requires reviewable evidence, not private prompts, chain-of-thought, full agent traces, or internal exploratory process records.
5. **Review independence and human authority.** AGM supports review preparation and governance diagnosis but does not replace independent code review or final human maintainer decisions.

## 5. Core Concepts

- **Manifest:** project-level governance metadata and references to AGM policy files.
- **Risk zone:** a repository path pattern or governance area mapped to a risk level.
- **Evidence requirement:** a minimum evidence expectation associated with a risk level, path pattern, or governance rule.
- **Evidence package:** contribution-side structured evidence describing changed files, risk-zone assessment, tests, artifacts, limitations, rationale, and human review declaration when required.
- **Governance gate state:** review-readiness state calculated from risk classification, evidence completeness, placeholder detection, and human review declaration.
- **Review packet:** maintainer-facing diagnostic summary that compares AGM reference requirements with observed contribution evidence.
- **Adoption layer:** optional helper materials, such as agent skills, `AGENTS.md`, or `CLAUDE.md`, that help agents discover and apply AGM rules. These helpers are not the canonical AGM rules.

## 6. Manifest Schema

The prototype manifest lives at `.agm/manifest.yml`. It is the canonical entrypoint for AGM rules in a repository.

A manifest contains:

- `schema_version`
- `project`
- `governance_scope`
- `risk_zone_reference`
- `evidence_requirement_reference`
- `human_review_policy`
- `final_decision_authority`
- `non_goals`

The manifest is project-level infrastructure. It is not a PR-level template. Pull requests are one common enactment context, but AGM is defined for contributions more generally.

A manifest should be short enough for humans to inspect and structured enough for agents or reference tooling to parse.

## 7. Risk-zone Schema

Risk zones live at `.agm/risk_zones.yml`. Each zone has:

- `id`
- `level`: `low`, `medium`, `high`, or `critical`
- `patterns`: repository-relative path patterns
- `description`
- optional `rationale`
- optional `required_evidence`

The default risk levels in this prototype are illustrative only. Each project should customize its own risk zones according to its technical architecture, security sensitivity, maintainer capacity, downstream dependency structure, and community review norms.

The prototype uses a conservative `high` default for unknown paths. Explicit authentication, authorization, or security-sensitive paths are treated as `critical` in the demo application. These defaults are reference examples, not universal policy.

## 8. Evidence Package Schema

An evidence package is a structured YAML file, typically placed under `evidence_packages/`, with:

- `schema_version`
- `contribution_id`
- `changed_files`
- `summary`
- `rationale`
- `risk_zone_assessment`
- `evidence_index`
- `tests_run`
- `artifacts`
- `known_limitations`
- `human_review_declaration`
- `generated_at`

Required fields depend on the detected risk level and the repository's evidence requirements. Critical-risk contributions require stronger evidence, such as a security or authentication impact statement, test commands, test artifacts, known limitations, and a human review declaration.

The `rationale` field describes the technical, functional, business, or governance justification for the change. It must not require contributors to disclose internal prompts, chain-of-thought, exploratory reasoning, or private agent interactions.

The `evidence_index` may reference tests, logs, screenshots, review notes, traceability artifacts, or other supporting materials. If a project uses external traceability or provenance formats, such as Agent Trace, references to those artifacts may be included in `evidence_index` as optional supporting evidence. AGM does not require, define, or validate any specific trace format.

Contributor-side generation may record fields such as `risk_zone_assessment.agent_read_agm_files` to show which AGM files an agent consulted. This is a compact simulation of contribution-side governance behavior, not an agent trace log or provenance system.

## 9. Governance Gate-state Model

Validation or review diagnosis returns:

- `risk_level`
- `evidence_status`: `complete`, `incomplete`, `missing`, or `placeholder`
- `human_review_status`: `not_required`, `pending_human_review`, `human_reviewed`, or `maintainer_review_required`
- `governance_gate_status`: `pass`, `needs_evidence`, or `blocked`
- `technical_review_readiness`: `ready`, `limited`, or `not_ready`
- `final_acceptance_readiness`: `eligible_for_human_decision`, `not_eligible_missing_evidence`, or `blocked_by_policy`

`eligible_for_human_decision` never means accepted. It only means that the contribution appears sufficiently prepared for human maintainer consideration under the project's AGM rules.

AGM gate states are diagnostic. They support review preparation and reviewer attention, but they do not perform final acceptance, rejection, merge, or deployment decisions.

## 10. Review Packet Format

Review packets are generated as machine-readable and human-readable outputs, for example:

- `review_packets/review_packet.json`
- `review_packets/review_packet.md`

The Markdown packet contains a reference-vs-observed governance table:

| Governance Indicator | Reference / Required Value | Observed / Provided Value | Status |
| --- | --- | --- | --- |
| Risk-zone classification | Must identify affected risk zone | `critical_auth` | Pass |
| Required evidence | Auth test command and artifact required | Test command present, artifact missing | Needs evidence |
| Human review declaration | Required for critical risk | `pending_human_review` | Blocked |
| Final decision authority | Human maintainer | Human decision required | Pass |

The packet also includes changed files, detected risk zones, required evidence, provided evidence, missing evidence, placeholder warnings, gate state, reviewer attention points, and final decision authority.

The review packet is a diagnostic aid. It does not replace code review and does not approve or reject the contribution.

## 11. Human Review Declaration

Critical-risk contributions must include `human_review_declaration` with:

- `required`
- `status`: `not_required`, `pending_human_review`, `human_reviewed`, or `maintainer_review_required`
- `reviewer`
- `reviewed_at`
- `review_scope`
- `statement`

For critical risk, `pending_human_review` is not enough for final-acceptance readiness. It indicates that a human review is still required.

`human_reviewed` records a human declaration that scoped review was completed. It does not approve the contribution, does not replace maintainer review, and does not imply that the contribution should be merged.

Agents must not fabricate human review declarations. If no human has reviewed the change, the declaration should remain `pending_human_review` or `maintainer_review_required`, depending on the project's policy.

## 12. Compliance Levels

The following compliance levels are illustrative rather than prescriptive.

- **AGM-L0:** Human-readable governance guidance only. Useful for small projects or early governance exploration.
- **AGM-L1:** Machine-readable risk zones and evidence requirements. Useful for projects that want basic agent-readable governance rules.
- **AGM-L2:** Contribution-side evidence package preparation. Useful for projects where contributor-side agents or contributors prepare structured governance evidence.
- **AGM-L3:** Automated validation and maintainer-facing review packet generation. Useful for projects with standardized review workflows and diagnostic review packets.
- **AGM-L4:** Integration-ready governance infrastructure for CI or platform workflows. Useful for large-scale production projects seeking CI, platform, or ecosystem-level integration.

This prototype mainly covers AGM-L2 and AGM-L3. It does not implement production CI, platform integration, network services, external APIs, LLM calls, or GitHub App behavior.

## 13. Optional Adoption Layer

Agent skills, `AGENTS.md`, and `CLAUDE.md` are optional adoption helpers. They are not required for AGM compliance.

- Contributor skill profiles should act as non-invasive governance overlays. They should not replace the contributor's primary coding agent or coding instructions.
- Maintainer skill profiles should act as diagnostic assistants. They should compare repository AGM requirements with contributor-submitted evidence and produce review suggestions.
- Discovery pointers should direct agents to `.agm/manifest.yml` without copying the full rules.
- In PR-based workflows, maintainer-side diagnosis should use the base branch AGM rules as the reference standard. If a contribution modifies `.agm/`, `AGENTS.md`, or `CLAUDE.md`, that change should be flagged as a governance-rule or governance-entrypoint change requiring maintainer attention.

Canonical AGM rules remain in `.agm/manifest.yml` and the referenced risk-zone and evidence-requirement files. Final authority remains with human maintainers.

## 14. Minimal Adoption Path

A project can adopt AGM incrementally.

1. Add `.agm/manifest.yml` as the canonical governance entrypoint.
2. Define project-specific risk zones in `.agm/risk_zones.yml`.
3. Define evidence requirements in `.agm/evidence_requirements.yml`.
4. Optionally add `AGENTS.md`, `CLAUDE.md`, or skill profiles as discovery pointers.
5. Ask contributor-side agents or contributors to prepare evidence packages for contributions.
6. Ask maintainer-side agents or human reviewers to compare base AGM requirements with submitted evidence packages.
7. Use review packets to surface missing evidence, placeholder evidence, human review status, and final decision readiness.

Projects may stop at any compliance level that fits their scale and governance needs.
