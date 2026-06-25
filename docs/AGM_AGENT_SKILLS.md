# AGM Agent Skills and Adoption Layer

AGM core lives in `.agm/`. The canonical governance rules are:

- `.agm/manifest.yml`
- the risk-zone file referenced by the manifest
- the evidence-requirement file referenced by the manifest

Skills, `AGENTS.md`, and `CLAUDE.md` are optional adoption helpers. They make AGM easier for different coding and review agents to discover, but they are not the source of truth and are not required for AGM compliance.

## Contributor Skill

`skills/agm-contributor/skill.md` is a non-invasive governance overlay. It does not replace the user's coding task or the primary coding agent. It helps the agent:

- discover `.agm/manifest.yml`;
- classify risk zones;
- identify evidence requirements;
- prepare or update an evidence package;
- mark missing evidence honestly;
- keep human review as `pending_human_review` unless a human explicitly confirms review.

It must not invent evidence or claim tests were run unless they were actually run or reliable test output is provided.

## Maintainer Skill

`skills/agm-maintainer/skill.md` is a diagnostic assistant. It compares:

- reference values from the base-branch AGM;
- observed values from the submitted evidence package;
- independently recovered risk zones from changed files or PR diff.

It flags governance-rule or governance-entrypoint changes such as `.agm/**`, `AGENTS.md`, `CLAUDE.md`, or `skills/**`. It does not approve, reject, or merge.

## Discovery Pointers

`AGENTS.md` and `CLAUDE.md` are thin discovery pointers. They should direct agents to `.agm/manifest.yml` without copying the full governance rules.

## Direct Use Without Skills

Agents and humans can ignore skills entirely and read `.agm/manifest.yml` directly. The `.agm/` files remain the canonical governance source.

Final authority remains with human maintainers.
