# AGM Maintainer Skill

Use this portable lifecycle protocol to perform independent governance
verification. A maintainer-side agent may prepare the diagnosis; only an
authorized human role may execute human-authority operations.

## Executable lifecycle

1. **Load base policy** — recover canonical `.agm/` from the contribution's
   recorded base branch/commit, not from contributor assertions alone.
2. **Independently resolve** — inspect the actual diff, recover every matched
   risk rule, autonomy/assurance profile, fallback, and interaction rule.
3. **Recompile** — independently compile the full obligation set and compare it
   with the submitted case. Record mismatches and policy conflicts.
4. **Verify bindings** — check obligation linkage, file/symbol scope,
   contribution and policy fingerprints, commands, environment, artifact
   existence/hash, freshness, expiry, provenance fields, and conflicting
   evidence.
5. **Verify attestations** — confirm actor role, scope, statement,
   reservations, and current contribution/evidence fingerprints. Never treat
   `pending` as confirmed.
6. **Produce the report** — show overall readiness, every risk domain,
   obligation reference vs observed state, findings, attestations, repair
   history, and authority boundary.
7. **Execute one authorized operation** — verify/reject evidence, request
   repair, ask clarification, invalidate an attestation, record/resolve a
   policy conflict, or record an authorized override. The domain service must
   recheck role and transition authority.
8. **Repair or close** — preserve attempts, revalidate only affected records,
   and produce a closure receipt for a terminal human decision.

Useful commands:

```bash
python -m agm.vnext.cli maintainer inspect --case CASE --serve
python -m agm.vnext.cli maintainer verify --case CASE --actor HUMAN --reason "Bindings checked."
python -m agm.vnext.cli maintainer request-repair --case CASE --actor HUMAN --message "Correction required." --obligation O-ID
python -m agm.vnext.cli maintainer decide --case CASE --actor HUMAN --decision accept --reason "Human decision rationale."
```

## Authority boundary

An agent may generate the report but may not impersonate a human verifier,
policy steward, accountable human, or final maintainer. Verification is not
acceptance. Final decisions remain with authorized human maintainers.
