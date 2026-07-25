# AGM Review Steward Protocol

Status: optional, harness-neutral vNext development protocol

The Review Steward independently restores governance state for a maintainer. It
may prepare diagnostics but cannot impersonate an authorized human role.

1. Load canonical policy from the recorded base snapshot.
2. Independently inspect the actual diff and re-resolve all rules,
   interactions, profiles, and obligations.
3. Compare compiled reference state with the submitted Governance Case.
4. Verify evidence identity, scope, freshness, provenance, artifact hashes,
   conflicts, and contribution/policy binding.
5. Verify accountable-human events and separation-of-duty requirements.
6. Produce a reference-vs-observed governance laboratory report.
7. Present authorized operations to the human maintainer: verify/reject,
   clarify, request repair, invalidate, resolve policy conflict, override, or
   decide.
8. Apply no mutation without server-side role and state authorization.
9. Preserve repair history and produce a closure receipt after a terminal
   human decision.

`eligible_for_human_decision` is not acceptance. The Review Steward cannot
approve, reject, close, merge, or override.
