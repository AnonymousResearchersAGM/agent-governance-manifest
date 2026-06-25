# Contributor-Side Agent Instruction

This file packages the AGM contributor-side workflow so that user prompts can remain task-focused.

You are a contributor-side coding agent operating in a repository governed by an Agent Governance Manifest. Treat this file as repository-internal operating guidance.

## Default Workflow

1. Read `agent_governance_manifest.yml`.
2. Read the user-specified task file, usually under `evaluation_tasks/`, when one is provided.
3. Identify expected affected files from the task file and actual changed files from your work.
4. Classify the actual changed files into manifest-defined risk zones and determine the highest risk level.
5. Complete the requested code, test, documentation, configuration, dependency, or workflow change.
6. Run tests appropriate to the changed files and risk level.
7. Generate the evidence package required by the detected risk level.
8. For high and critical changes, generate `human_review_declaration.md` and mark human confirmation as required.
9. Explicitly report missing evidence, if any.
10. Do not submit original prompts, chain-of-thought, detailed intermediate reasoning, private exploratory attempts, or persuasive explanations.
11. Submit only independently checkable evidence.

## Evidence Package

Use `templates/` and `scripts/init_evidence_package.py` when helpful. A typical evidence package contains:

- `contribution_report.md`
- `test_report.md` when required
- `trace_manifest.json` when required
- `human_review_declaration.md` for high and critical changes

The package should include affected files, declared risk zones, declared risk level, AI assistance disclosure, tests run, test outcomes, known limitations, linked issues or an explicit no-issue note, human confirmation status, and missing evidence.

## Validation

After generating evidence, run the repository scripts when possible:

```bash
python scripts/classify_risk_zone.py <changed files>
python scripts/validate_evidence_package.py <changed files> --evidence-dir <evidence package directory>
```

For guided setup, use:

```bash
python scripts/run_contributor_flow.py --task <task file> --changed-files <changed files> --evidence-dir <evidence package directory>
```

## Boundary

AGM requires evidence disclosure rather than reasoning disclosure. Do not include original prompts, chain-of-thought, detailed intermediate reasoning, private exploratory attempts, or persuasive narratives in the submitted evidence package.

## Short User Prompt Examples

```text
请按照 AGM 流程执行 evaluation_tasks/critical_auth_change.md。
请完成 medium_risk_test_addition 任务，并按 AGM 要求生成 evidence package。
请根据仓库 AGM 流程处理这个任务：<task description>。
```

