# Prompt Minimization in Round 2

Round 2 reduces the amount of AGM process knowledge that users must repeat in prompts.

## Rationale

User prompts should focus on the task itself. A contributor should be able to write:

```text
请按照 AGM 流程执行 evaluation_tasks/critical_auth_change.md。
```

The repository should carry the procedural burden through files and scripts.

## Repository Responsibilities

- `AGENTS.md` is the generic coding-agent entry point.
- `agent_governance_manifest.yml` is the authoritative governance rule source.
- `prompts/contributor_agent_instruction.md` packages the contributor-side workflow.
- `prompts/maintainer_review_agent_instruction.md` packages the maintainer-side workflow.
- `templates/` define evidence and review artifact structure.
- `scripts/` provide repeatable classification, evidence initialization, validation, and review packet generation.

`init_evidence_package.py` creates a skeleton only. It is a starting point with placeholders, not completed evidence. Users must fill real review-relevant facts before validation can pass.

## User Responsibilities

Users do not need to repeat every AGM step in each prompt. They should identify the task, the changed files when known, and the desired side of the workflow.

Users must not leave placeholder values such as `TBD`, `TODO`, `placeholder`, `not provided`, `not run`, `unknown`, `n/a`, `<...>`, or `[...]` in submitted evidence. For high and critical changes, a human review declaration is required. If no issue is linked, the evidence should explicitly say `No linked issue` or an equivalent clear statement.

## Governance Boundary

Prompt minimization does not weaken the evidence boundary. Contributor-side agents still provide evidence packages rather than original prompts, chain-of-thought, detailed intermediate reasoning, private exploratory attempts, or persuasive narratives.

Maintainer-side review agents still review independently using the manifest, changed files or diff, structured evidence package, tests, trace manifest, human declaration, and issue context.

## Intended Outcome

The workflow becomes easier to run, easier to teach, and easier to evaluate. The controlled prototype remains small while moving process knowledge out of ad hoc user prompts and into repository-native artifacts.
