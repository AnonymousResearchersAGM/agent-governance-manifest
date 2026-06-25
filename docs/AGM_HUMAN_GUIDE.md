# Agent Governance Manifest Human Guide

This directory is the canonical governance source for the AGM v0.1.0 Community Draft prototype.

The YAML files are machine-readable so that agents and lightweight scripts can validate contributions. They are also intended to be human-readable project governance documents. This guide explains the same rules in natural language.

## Canonical Files

| File | Purpose | Human Meaning |
| --- | --- | --- |
| `manifest.yml` | Project-level AGM entry point | Defines the governed project, scope, policy references, human review policy, non-goals, and final decision authority. |
| `risk_zones.yml` | Risk-zone rules | Maps repository paths to risk levels so contributors and reviewers know which files require extra evidence. |
| `evidence_requirements.yml` | Evidence requirements | Defines the minimum evidence package fields required for each risk level. |

Skills, `AGENTS.md`, and `CLAUDE.md` are optional adoption helpers. They point agents to this directory, but they do not replace these canonical files.

## Risk Levels

| Risk Level | Meaning in This Prototype | Example Paths | Review Implication |
| --- | --- | --- | --- |
| `low` | Documentation and explanatory text | `README.md`, `docs/**` | Contribution summary and changed files are enough. |
| `medium` | Ordinary business logic | `demo_app/tasks.py` | Requires rationale and tests run or explanation. |
| `high` | Configuration, dependency, tests, and governance entrypoints | `demo_app/config.py`, `requirements.txt`, `.agm/**`, `AGENTS.md`, `CLAUDE.md`, `skills/**`, `tests/**` | Requires concrete test command/artifact evidence and known limitations. Governance entrypoint changes need maintainer attention. |
| `critical` | Authentication or security-sensitive behavior | `demo_app/auth.py`, `**/auth.py` | Requires security/auth impact statement, test command/artifact, known limitations, and human review declaration. |

Unknown changed paths use the conservative default risk level: `high`.

## Evidence Requirements

| Risk Level | Required Evidence |
| --- | --- |
| `low` | Contribution summary; changed files list. |
| `medium` | Contribution summary; changed files list; rationale; tests run or explanation. |
| `high` | Contribution summary; changed files list; rationale; tests run with command; relevant artifact or test output; known limitations. |
| `critical` | Contribution summary; changed files list; rationale; security/auth impact statement; tests run with command; relevant artifact or test output; known limitations; human review declaration. |

Evidence must be factual and checkable. Placeholder text such as `TODO`, `TBD`, `N/A`, `placeholder`, or `lorem ipsum` is not valid required evidence.

## Human Review Declaration

| Status | Meaning |
| --- | --- |
| `not_required` | The detected risk level does not require human review declaration. |
| `pending_human_review` | Human review is required or requested, but no human has declared completion. |
| `human_reviewed` | A human contributor or reviewer declares that the scoped review was completed. This is not acceptance. |
| `maintainer_review_required` | Maintainer attention is required before the contribution can be considered ready. |

For critical risk, `pending_human_review` is not enough for final-acceptance readiness. `human_reviewed` can make the evidence package eligible for human decision, but it still does not mean accepted.

## Gate State Meaning

| Gate State | Meaning |
| --- | --- |
| `pass` | Evidence is complete enough to enter human decision-making. This is not acceptance. |
| `needs_evidence` | Some required evidence is missing or incomplete. |
| `blocked` | Policy blocks readiness, commonly because critical risk lacks `human_reviewed` or required evidence is placeholder. |

Final approval, rejection, request-for-changes, or merge decisions remain with human maintainers.

## What AGM Is Not

AGM is not AGENTS.md, a PR template, an AI detector, an agent trace or provenance log, an automatic merge/reject tool, or a replacement for human maintainers.
