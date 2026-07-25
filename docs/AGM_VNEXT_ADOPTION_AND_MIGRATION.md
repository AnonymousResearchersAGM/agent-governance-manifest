# AGM vNext Adoption and Migration

Status: `v0.2-dev`

## Adoption levels

1. **Discovery pointer only** — keep AGENTS.md or another adapter short and
   point it to `.agm/manifest.yml`.
2. **Ordinary agent plus portable Skill** — use the contributor or maintainer
   Skill to execute the lifecycle.
3. **Dedicated AGM Steward** — use the harness-neutral protocols under
   `.agm/agents/`.

Dedicated agents are optional. No adoption level grants human authority.

## Project setup

1. Customize `.agm/policies/risk_rules.yml`.
2. Define stable obligations in `evidence_profiles.yml`.
3. Add project-specific interaction rules.
4. Configure autonomy and assurance profiles.
5. Map human and non-human roles to minimum permissions.
6. Validate state transitions and interface configuration.
7. Run `project simulate` for representative and adversarial diffs.
8. Keep `.agm-work/` ignored; curate examples under `examples/`.

## Integration points

AGM may read or complement CONTRIBUTING, CODEOWNERS, CI, PR templates,
provenance tools, and branch protection. These resources do not become AGM's
theoretical core. The canonical policy must identify how they contribute to a
concrete obligation or authority boundary.

## Open-case policy changes

Run:

```bash
python -m agm.vnext.cli case migrate-check --case CASE
```

The diagnostic reports unchanged, changed, added, and removed obligations,
evidence needing revalidation, and affected attestations. It performs no
migration.

A new critical blocking obligation requires migration. Otherwise, the case may
remain on its recorded snapshot unless project policy explicitly requires
`must_follow_current`. The authorized maintainer records the decision; silent
migration is prohibited.

## v0.1 projects

Do not rewrite historical v0.1 evidence. Preserve the reported module or a
compatibility layer, record the immutable base commit, introduce `/v0.2-dev`
schema identifiers, and label every new mechanism as unvalidated design
development until new evaluation exists.
