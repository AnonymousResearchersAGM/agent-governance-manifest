# AGM Prototype Architecture

Agent Governance Manifest is modeled as a two-sided repository governance contract.

```text
contributor-side agent
-> reads manifest
-> classifies changed files by risk zone
-> generates contribution and evidence package
-> maintainer-side review agent reads manifest + diff + evidence + issue context
-> generates review support
-> human maintainer makes final decision
```

The prototype does not implement GitHub App behavior, webhooks, or API integration. Instead, it isolates the governance mechanism in a small repository where changed files, evidence packages, and review packets can be generated and compared across evaluation conditions.

## Main Components

- `agent_governance_manifest.yml`: repository-level risk and evidence policy.
- `app/`: small Python application with low, medium, high, and critical risk areas.
- `templates/`: contributor and maintainer artifacts.
- `scripts/`: local commands for classification, validation, and review packet generation.
- `evaluation_tasks/`: controlled tasks for later study phases.
- `sample_outputs/`: baseline and manifest-supported outputs for comparison.

