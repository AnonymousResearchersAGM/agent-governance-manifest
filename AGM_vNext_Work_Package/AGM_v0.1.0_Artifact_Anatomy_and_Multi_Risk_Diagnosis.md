# AGM v0.1.0 Artifact Anatomy and Multi-Risk Diagnosis

**Working date:** 2026-07-25
**Source snapshot:** user-provided `agent-governance-manifest-main.zip`
**Status:** diagnostic working note; does not modify the reported AGM v0.1.0 research snapshot.

## 1. Verified repository state

- The active prototype is local, file-based, deterministic, and centered on `.agm/`, `src/agm/governance.py`, evidence packages, review packets, and lightweight CLI wrappers.
- The full current test suite passes: **23 passed**.
- Canonical project rules are stored in:
  - `.agm/manifest.yml`
  - `.agm/risk_zones.yml`
  - `.agm/evidence_requirements.yml`
- The core executable engine is `src/agm/governance.py`.

## 2. Current executable pipeline

The actual v0.1.0 pipeline is:

```text
changed_files
  -> path-pattern matching
  -> detected risk-zone records
  -> highest risk level
  -> one risk-level evidence profile
  -> evidence completeness / placeholder / artifact-existence checks
  -> human-review declaration normalization
  -> pass | needs_evidence | blocked
  -> JSON/Markdown review packet
```

The prototype therefore implements a useful contribution-level governance-state externalization mechanism, but not yet a complete governance lifecycle.

## 3. Current risk-classification semantics

`classify_changed_files()` in `src/agm/governance.py`:

1. evaluates every changed file against every configured path pattern;
2. preserves every matched `(file, zone, risk_level)` record;
3. applies the default `high` level to unmatched paths;
4. computes one scalar `highest` risk level;
5. selects exactly one evidence requirement profile from that highest level.

Key implementation locations:

- `src/agm/governance.py:131-187`
- `.agm/risk_zones.yml:1-59`
- `.agm/evidence_requirements.yml:1-126`

The current design therefore preserves multi-zone observations but collapses obligation generation to one global severity profile.

## 4. Current multi-risk behavior verified by execution

### Case A: documentation + authentication

Changed files:

- `docs/guide.md` -> documentation / low
- `demo_app/auth.py` -> authentication / critical

Current result:

- overall risk: `critical`
- required evidence: critical profile only
- both zones remain visible in `detected_risk_zones`

### Case B: task logic + dependency/configuration

Changed files:

- `demo_app/tasks.py` -> task_logic / medium
- `requirements.txt` -> configuration / high

Current result:

- overall risk: `high`
- required evidence: high profile only

### Case C: governance rule + authentication + unclassified path

Changed files:

- `.agm/manifest.yml` -> configuration / high
- `demo_app/auth.py` -> authentication / critical
- `new/plugin.py` -> unclassified_path / high

Current result:

- overall risk: `critical`
- required evidence: critical profile only
- governance-entrypoint change is separately flagged

## 5. Why highest-risk-only is insufficient for vNext

Taking the maximum risk level is useful as a conservative summary, but it is not a sufficient governance-composition rule.

### 5.1 Specialized lower-level obligations can disappear

A higher generic profile does not necessarily contain every zone-specific obligation. For example, a critical authentication change and a high privacy/configuration change may require different evidence, reviewers, and validation operations. Selecting only the critical profile can silently lose the second obligation family.

### 5.2 One contribution can require several independent authorities

A contribution may require security, data governance, release, documentation, or project-governance review. Overall severity does not identify who holds each verification right.

### 5.3 Cross-zone interaction may create additional risk

Two individually bounded changes can interact. Examples include:

- authentication + deployment configuration;
- schema migration + data export;
- model behavior + production routing;
- governance-rule change + executable validator change.

The combined governance requirement may be stronger than either zone considered independently.

### 5.4 Repair and evidence invalidation should be scoped

If only one risk-zone obligation fails, the system should identify the affected obligation and repair path. A single undifferentiated package-level failure does not show what remains valid.

## 6. Proposed vNext multi-risk model

A contribution should remain one **Governance Case**, but contain multiple matched **Policy Obligations**.

### 6.1 Keep two distinct risk representations

1. **Overall risk summary**
   - normally the maximum effective severity;
   - used for headline display and conservative fallback;
   - never the sole source of obligations.

2. **Risk vector / matched policy set**
   - all matched zones and selectors;
   - all associated evidence obligations;
   - all required verification operations;
   - all required roles and gates.

### 6.2 Obligation compilation rule

```text
changed contribution
+ all matched risk rules
+ autonomy profile
+ project assurance profile
+ interaction/escalation rules
        -> compiled obligation set
```

The compiled obligation set should use:

- **union** for evidence and reviewer obligations;
- **deduplication** for identical obligations;
- **strongest constraint wins** for severity, expiry, and blocking behavior;
- **conjunctive completion** for mandatory gates: every required blocking gate must pass;
- **explicit conflict state** when obligations or authorities are incompatible;
- **interaction escalation** where project-defined combinations trigger additional controls.

### 6.3 Per-obligation evidence mapping

Evidence should not merely exist at package level. Each item should identify:

- obligation ID;
- triggering policy rule;
- affected files/symbols/change slice;
- artifact or test result;
- validity period and environment;
- attesting human, where required;
- maintainer verification status.

### 6.4 Suggested illustrative structure

```yaml
risk_assessment:
  overall_level: critical
  matched_rules:
    - rule_id: auth-change
      zone: authentication
      level: critical
      affected_paths:
        - demo_app/auth.py
    - rule_id: governance-entrypoint-change
      zone: project_governance
      level: high
      affected_paths:
        - .agm/manifest.yml
  interaction_rules:
    - rule_id: governance-engine-self-modification
      triggered: true
      effect: additional_independent_maintainer_verification

compiled_obligations:
  - id: O-AUTH-TEST
    source_rule: auth-change
    type: evidence
    blocking: true
  - id: O-AUTH-ATTEST
    source_rule: auth-change
    type: human_attestation
    blocking: true
  - id: O-GOV-INDEPENDENT-REVIEW
    source_rule: governance-entrypoint-change
    type: maintainer_verification
    blocking: true
```

## 7. Recommended report presentation

The maintainer-facing report should show:

1. overall risk headline;
2. all matched risk domains;
3. one panel per obligation family;
4. evidence coverage for each obligation;
5. required human attestations and maintainers;
6. unresolved conflicts and interaction escalations;
7. overall governance readiness derived from all blocking gates.

A useful report summary would be:

```text
Overall status: Repair required
Overall risk: Critical
Matched domains: Authentication, Project governance, Unclassified surface
Blocking findings:
- Authentication evidence complete
- Human attestation complete
- Independent governance-rule review missing
- Unclassified plugin path requires project classification
```

## 8. Other confirmed v0.1.0 limitations relevant to vNext

- Human review is recorded as a mutable YAML field and is not bound to a package/diff hash.
- `mark_human_review()` overwrites the declaration but does not preserve an event history.
- Maintainer-side behavior is diagnostic packet generation, not a formal set of authorized verification, challenge, repair, override, and closure operations.
- Artifact validation checks existence, but not content identity, provenance, freshness, diff coverage, or conflicts.
- Gate state is a derived three-value result, not an authority-typed state machine.
- Ordinary contributions without an AGM package have no explicit workflow semantics.
- Manifest applicability and migration are not modeled.

## 9. Immediate next design task

Before modifying code, freeze a vNext normative kernel containing:

1. Governance Case;
2. Policy Snapshot;
3. Matched Rule Set;
4. Compiled Obligation Set;
5. Bound Evidence;
6. Human Attestation Event;
7. Maintainer Verification Event;
8. Authorized State Transition;
9. Repair Request;
10. Closure / Override Record.

The first implementation slice should then cover:

- ordinary vs AGM-managed paths;
- multi-risk obligation compilation;
- visible human attestation interface;
- maintainer verification operations;
- report generation from per-obligation states.
