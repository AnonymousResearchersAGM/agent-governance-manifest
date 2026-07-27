# AGM Review Briefing Phase 1.1 Review Record

Status: implementation evidence prepared; `pending_human_review`

## 1. Why this hardening was required

P91 showed an adoption risk: an ordinary programmer could read an accurate
Reviewer Guidance view and still need to understand lifecycle stages, roles,
obligation codes, evidence states, findings, repairs, transitions, and
authority before identifying the work that belonged to them.

Phase 1 introduced the Human-Work Compiler, but an independent review found
that the first page still resembled a complete governance report. The current
route appeared late, formal binding checks used wording broad enough to imply
content correctness, and two presentation fallbacks could manufacture work
not justified by canonical policy.

This record describes Phase 1.1 corrections. It is not a human approval,
maintainer verification, final decision, or experiment result.

## 2. Independent-review findings addressed

### Information hierarchy

The current-next-step card moved directly below contribution identity. It
states whether the reader acts now, the owner, item count, and the distinction
between checking and acceptance. Human judgment appears next when present.

Complete requirements, passed automatic checks, accountability detail, and
governance technical records are closed by default.

### Semantic precision

The broad participant label “系统已确认” was replaced by explicit states for
material availability, structural validity, version binding, system checking,
human review, human verification, final-decision pending, and acceptance.

Test-record completeness remains explicitly bounded: it does not prove code
correctness or coverage sufficiency. Agent declaration remains separate from
system observation.

### Human-judgment provenance

The denied-attempt fallback that selected contribution summary when the queue
was otherwise empty was removed. Every judgment now has a safe requirement
reference and provenance from a compiled requirement plus an existing review
stage, independent-review requirement, finding, or scoped revalidation.

Denied attempts appear only as system-handled anomalies. They do not create
obligations, findings, repair requests, verification targets, or judgments.

### Policy boundary

Automatic checks now expose whether they are policy-required, blocking,
informational-only, and system-handled. A missing agent action/delegation
statement is a problem only when the case contains the compiled
`O-AGENT-SCOPE` obligation. Otherwise it is gray, non-blocking information and
does not affect routing or responsibility.

### Work ownership

Unresolved work is explicitly assigned to the system, contribution side,
accountable human, maintainer, or final-decision authority. The owner is data,
not template wording.

### Demonstration language and reproducibility

The eight Review Briefing fixtures now use natural contribution descriptions.
Fixture actor IDs and generator names remain only in technical detail. A
frozen 25-file SHA-256 manifest and explicit Windows/Ubuntu regeneration steps
cover JSON, Markdown, HTML, and `manifest.json`.

## 3. Human acceptance checklist

For each scenario, a reviewer should be able to answer without reading the
folded technical section:

1. Does the maintainer need to act now?
2. If not, who owns the current work?
3. What changed and why is it risky?
4. Which visible problems are actually blocking?
5. Which exact items require human content judgment?
6. Did the system check only form and binding, or did a legal maintainer
   verification occur?
7. Does verification completion remain distinct from final acceptance?

Scenario-specific checks:

- scenario 1 routes missing work to the contribution side;
- scenario 2 preserves unaffected material and names only modification
  summary as stale;
- scenario 3 contains one scoped agent-action judgment;
- scenario 4 separates the system-handled unauthorized attempt from normal
  review and creates no fallback judgment;
- scenario 5 returns directly to normal code review;
- scenario 6 identifies governance self-modification and independent review;
- scenario 7 reports policy change, unchanged requirements, revalidation
  count, and the canonical contribution-side owner without invalidating
  everything; and
- scenario 8 distinguishes verification, human acceptance, and archival
  closure.

## 4. Remaining limitations

- File-path classification is conservative and does not establish code
  semantics.
- AGM does not provide complete agent runtime provenance or AI detection.
- Recorded human identity and statement truth require external identity and
  attestation systems.
- Normal code review remains outside automatic AGM governance checks.
- The future item-level action binding has not been designed or implemented.
- Browser viewport usability still requires human visual acceptance on the
  committed HTML fixtures.
- The artifact remains `pending_human_review`.

## 5. Explicit phase boundary

Phase 2 has not started. No item-level mutation, verification, repair,
attestation, rejection, acceptance, closure, or merge control was added.
No P92 experiment package was generated.
