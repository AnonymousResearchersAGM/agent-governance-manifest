# AGM End-to-End Tutorial

This tutorial shows how to run the AGM prototype as a controlled local workflow. It does not require GitHub Apps, webhooks, a Web UI, or real GitHub API access.

AGM is not an automatic merge system, not an AI detector, and not a requirement to disclose a contributor's complete thinking process. Its goal is evidence-based governance and maintainer-side review support.

## A. Contributor-Side Workflow

The contributor-side workflow starts with a short task-focused prompt. The repository provides the AGM process details through `AGENTS.md`, `agent_governance_manifest.yml`, `prompts/contributor_agent_instruction.md`, scripts, and templates.

Minimal user prompt:

```text
请按照 AGM 流程执行 evaluation_tasks/critical_auth_change.md。
```

Expected contributor-side behavior:

1. Read the short task prompt.
2. Automatically read `AGENTS.md`, `agent_governance_manifest.yml`, and `prompts/contributor_agent_instruction.md`.
3. Read the task file under `evaluation_tasks/`.
4. Execute the requested code, test, documentation, configuration, dependency, or workflow change.
5. Identify expected affected files and actual changed files.
6. Classify the changed files into risk zones and determine the highest risk level.
7. Generate an evidence package from the relevant templates.
8. Run risk classification.
9. Run evidence validation.
10. Submit a PR description plus the evidence package.
11. Do not submit original prompts, chain-of-thought, detailed intermediate reasoning, private exploratory attempts, or persuasive narratives.

`init_evidence_package.py` creates an evidence skeleton, not completed evidence. The generated files contain `TBD` placeholders. Validation must fail until the contributor replaces placeholders with real, independently checkable evidence.

For the critical auth example, the expected evidence package location is:

```text
sample_outputs/manifest_supported/critical_auth_change/
  contribution_report.md
  test_report.md
  trace_manifest.json
  human_review_declaration.md
```

Useful commands:

```bash
python scripts/run_contributor_flow.py --task evaluation_tasks/critical_auth_change.md --changed-files app/auth.py tests/test_auth.py --evidence-dir sample_outputs/manifest_supported/critical_auth_change
python scripts/classify_risk_zone.py app/auth.py tests/test_auth.py
python scripts/validate_evidence_package.py app/auth.py tests/test_auth.py --evidence-dir sample_outputs/manifest_supported/critical_auth_change
```

The one-command contributor flow does not replace the coding agent's implementation work. It reduces friction around AGM classification, evidence skeleton creation, and validation.

Validation rejects placeholder evidence such as `TBD`, `TODO`, `placeholder`, `not provided`, `not run`, `unknown`, `n/a`, `<...>`, and `[...]`. For high and critical changes, `human_review_declaration.md` is required. If there is no linked issue, write a clear statement such as `No linked issue` rather than leaving template text like `TBD: issue id/url or explicit none`.

## B. Maintainer-Side Workflow

The maintainer-side workflow starts from a changed-file list or diff summary plus the contributor evidence package.

Minimal reviewer prompt:

```text
请按照 AGM 维护端流程审查 sample_outputs/manifest_supported/critical_auth_change/。
```

Expected maintainer-side behavior:

1. Read `agent_governance_manifest.yml`.
2. Read the changed files or diff summary.
3. Read the contributor evidence package.
4. Validate evidence completeness against the manifest.
5. Generate a review packet.
6. Check missing evidence.
7. Combine linked issue context with issue-related hints when available.
8. Generate reviewer attention points.
9. Preserve review independence.
10. Leave the final decision to the human maintainer.

Maintainer-side validation should treat skeleton packages as incomplete. Placeholder fields should appear in the missing-evidence report and review packet evidence summary.

Useful command:

```bash
python scripts/run_maintainer_review_flow.py --changed-files app/auth.py tests/test_auth.py --evidence-dir sample_outputs/manifest_supported/critical_auth_change --output sample_outputs/review_packets/critical_auth_change_review_packet.md
```

The review packet should summarize risk, affected files, required evidence, submitted evidence, missing evidence, test evidence, provenance, linked issue context, reviewer attention points, and the human final-decision reminder.

## What AGM Is Not

- AGM is not a GitHub App.
- AGM is not an automatic merge system.
- AGM is not an AI detector.
- AGM does not require contributors to disclose original prompts or detailed reasoning.

AGM is a lightweight research prototype for evidence-based governance and review support.

## Optional Content Inspection

Path-based risk classification is the default. To inspect readable file content for manifest `critical_if_contains` keywords, run:

```bash
python scripts/classify_risk_zone.py app/config.py --inspect-content
```

This can escalate a matched file to critical when keywords such as `SECRET`, `TOKEN`, `AUTH`, or `SESSION` are present.
