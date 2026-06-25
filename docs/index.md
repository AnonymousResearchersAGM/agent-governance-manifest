# Agent Governance Manifest Documentation

AGM Specification v0.1 — Community Draft

Agent Governance Manifest (AGM) is a project-side, agent-readable governance manifest for making agent-mediated open-source contributions reviewable, evidence-oriented, and accountable.

## Documentation

- [AGM Specification v0.1 — Community Draft](AGM_SPEC_v0.1.md)
- [Human Guide to `.agm/`](../.agm/README.md)
- [Prototype Usage Guide](PROTOTYPE_USAGE.md)
- [Agent Skill Profiles](AGM_AGENT_SKILLS.md)
- [Human Review Declaration](HUMAN_REVIEW_DECLARATION.md)
- [Dogfooding Report](DOGFOODING_REPORT.md)
- [Repository README](../README.md)

## Canonical Rules

The canonical AGM governance rules live in `.agm/`:

- `.agm/manifest.yml`
- the risk-zone file referenced by the manifest
- the evidence-requirement file referenced by the manifest

Skills, `AGENTS.md`, and `CLAUDE.md` are optional adoption-layer helpers.

Final approval, rejection, request-for-changes, or merge decisions remain with human maintainers.
