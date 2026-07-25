# AGM Contributor Skill

Use this portable lifecycle protocol as a governance overlay. It does not
replace the coding objective or the primary coding agent.

## Executable lifecycle

1. **Discover** — read `.agm/manifest.yml` and every referenced policy needed
   for the contribution. Treat Skills and discovery files as adapters, not
   authority.
2. **Preflight** — identify the base commit, requested intake mode, changed
   files, change-type tags, semantic targets, autonomy profile, permissions,
   supervision, and delegation.
3. **Inspect the actual change** — compute or obtain the real diff/change
   fingerprint. Do not infer authorship from package presence or absence.
4. **Resolve all risk** — retain every matched rule and the conservative
   fallback for unknown paths. Overall risk is a summary only.
5. **Compile** — union and deduplicate rule, autonomy, assurance, and
   interaction obligations. Surface contradictions as policy conflicts.
6. **Gather** — bind factual evidence to obligation IDs, affected scope,
   contribution and policy fingerprints, command/environment, artifact hash,
   time, expiry, and source actor/tool.
7. **Validate** — detect missing, placeholder, stale, expired, mismatched,
   conflicting, orphaned, or unverifiable evidence. Never invent evidence or
   test outcomes.
8. **Pause for human attestation** — generate the contributor panel and
   explicitly tell the user what scope requires review. An agent must not
   submit `confirm_attestation`.
9. **Bind and revalidate** — after explicit human action, bind the attestation
   to the current contribution, policy, evidence set, scope, statement, and
   reservations.
10. **Prepare submission** — revalidate after every material change, invalidate
    only affected records, record repair attempts, and submit for independent
    maintainer verification.

Useful commands:

```bash
python -m agm.vnext.cli project simulate --changed-file PATH
python -m agm.vnext.cli contributor open-case --changed-file PATH --actor ACTOR
python -m agm.vnext.cli contributor prepare --case CASE --actor ACTOR
python -m agm.vnext.cli contributor review --case CASE --serve
```

## Authority boundary

Contributor agents may propose, prepare, and resubmit. They may not perform
human attestation, maintainer verification, policy override, acceptance,
rejection, closure, or merge. `ready` is never `accepted`.
