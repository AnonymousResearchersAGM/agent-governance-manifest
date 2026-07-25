# AGM vNext Curated Examples

Status: illustrative `v0.2-dev` fixtures and reproducible local demonstration

Run all ten scenarios without changing the repository:

```bash
python scripts/run_vnext_demo.py
```

The script creates a temporary project, copies canonical policy, and exercises:

1. ordinary documentation with no package and no authorship claim;
2. declared agent-mediated low-risk documentation;
3. authentication plus configuration multi-risk compilation;
4. governance policy plus runtime self-modification;
5. evidence bound to a stale contribution fingerprint;
6. pending then explicitly confirmed human attestation;
7. maintainer repair, resubmission, revalidation, and final decision;
8. authorized override followed by a separate final decision;
9. policy change while a case is open; and
10. contradictory rules that create a blocking policy-conflict finding.

The files in this directory are explanatory fixtures. They are not claims that
the vNext mechanisms were evaluated in the v0.1.0 studies.

## Ordinary path

```yaml
requested_mode: ordinary
changed_files: [docs/guide.md]
result:
  package_status: no_agm_package_submitted
  case_created: false
  authorship_claim: none
```

## Multi-risk path

```yaml
changed_files:
  - demo_app/auth.py
  - demo_app/config.py
overall_risk_level: critical
matched_rules:
  - authentication-critical
  - configuration-high
interaction_rules:
  - authentication-configuration
required_obligations:
  - O-AUTH-IMPACT
  - O-INDEPENDENT-REVIEW
```

## Stale evidence

```yaml
evidence:
  contribution_fingerprint: old-fingerprint
case:
  contribution_fingerprint: current-fingerprint
result:
  validity_state: stale
  repair: regenerate or rebind evidence after rerunning the required check
```

## Closure receipt

```yaml
schema_version: agm.closure_receipt/v0.2-dev
final_state: accepted
authority:
  role: maintainer
  human: true
records:
  - policy_fingerprint
  - contribution_fingerprint
  - obligation_statuses
  - evidence_ids
  - attestation_ids
  - verification_ids
  - repair_request_ids
  - transition_log_hash
note: "Ready and verified states occurred before, and separately from, acceptance."
```
