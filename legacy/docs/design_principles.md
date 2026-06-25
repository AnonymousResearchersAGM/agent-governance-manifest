# AGM Design Principles

## Evidence-Based Governance

AGM asks for concrete evidence: affected files, risk zone, risk level, tests run, test outcomes, linked issues, known limitations, AI assistance disclosure, and human confirmation status.

## Risk-Zoned Governance

Repository files are mapped to risk zones. The highest matched risk level determines the evidence expected from the contributor side and the review attention expected from the maintainer side.

## Two-Sided Governance Contract

Contributor-side agents generate structured evidence. Maintainer-side review agents use the same manifest to independently check risk and evidence completeness.

## Human Responsibility Gates

High and critical changes require explicit human confirmation. Review agents provide support artifacts; they do not make final merge decisions.

## Machine-Readable and Human-Readable Evidence

Markdown templates are structured for human review. JSON trace manifests and schema files support machine processing.

## Maintainer-Side Review Support

AGM shifts review agents toward risk summaries, missing-evidence reports, test evidence summaries, provenance summaries, review checklists, and issue-related hints.

## Review Independence

Maintainer-side review should not rely on contributor prompts, detailed reasoning, or chain-of-thought as primary evidence. It should evaluate the diff, tests, manifest classification, evidence package, and issue context.

