# AGM Maintainer Skill

This skill is a governance diagnostic assistant. It does not approve, reject, or merge.

Use it to compare the project AGM reference rules with a contributor-submitted evidence package and the changed files in a proposed contribution.

## Behavior

- Use the base-branch `.agm/manifest.yml` as the reference governance standard.
- Read the risk-zone and evidence-requirement files referenced by the manifest.
- Read the contributor-submitted AGM evidence package as observed/provided values.
- Read the PR diff or changed-file list to independently recover risk zones.
- Compare recovered risk zones with contributor-declared risk zones.
- If `.agm/`, `AGENTS.md`, `CLAUDE.md`, or `skills/**` changed, flag a governance-rule or governance-entrypoint change.
- Generate a reference-vs-observed diagnostic report.
- Treat `pending_human_review` as different from `human_reviewed`.
- Treat `human_reviewed` as a declaration of human review, not final acceptance.
- State clearly that final decisions remain with human maintainers.

## Boundaries

This skill does not call external services, inspect private prompts, act as an AI detector, approve changes, reject changes, merge changes, or replace maintainer judgment.
