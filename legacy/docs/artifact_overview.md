# Artifact Overview

The Agent Governance Manifest (AGM) prototype is a repository-level governance artifact for AI-mediated contribution. It demonstrates how a repository can declare risk zones, evidence requirements, contributor-side obligations, maintainer-side review expectations, and human responsibility gates.

## Two-Sided Governance Contract

AGM is modeled as a two-sided governance contract. Contributor-side coding agents read the manifest, classify changed files, and produce a contributor-side evidence package. Maintainer-side review agents read the same manifest, inspect changed files and evidence, and produce review-support artifacts.

## Contributor-Side Evidence Package

The evidence package records independently checkable facts: affected files, risk zones, risk level, tests run, test outcomes, known limitations, linked issues or explicit no-issue notes, AI assistance disclosure, and human confirmation status.

## Maintainer-Side Review Packet

The review packet summarizes risk, required evidence, submitted evidence, missing evidence, test evidence, provenance, linked issue context, issue-related hints, reviewer attention points, and the human final-decision reminder.

## Risk-Zoned Governance

The manifest maps paths such as documentation, tests, core logic, authentication, dependencies, configuration, and workflows to risk levels. Higher-risk changes require stronger evidence and human responsibility gates.

## Evidence Rather Than Reasoning

AGM uses evidence disclosure rather than reasoning disclosure. It does not require original prompts, chain-of-thought, detailed intermediate reasoning, private exploratory attempts, or persuasive narratives.

## Human Responsibility and Review Independence

AGM supports review, but human maintainers retain final authority. Maintainer-side review agents should preserve review independence and should not rely on contributor prompts or detailed reasoning as primary evidence.

## Boundaries

- AGM is not an AI detector.
- AGM is not a prompt or chain-of-thought disclosure mechanism.
- AGM is not an automatic merge or reject system.
- AGM is not a production deployment.

