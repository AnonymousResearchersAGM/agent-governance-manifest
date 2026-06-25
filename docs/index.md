# Agent Governance Manifest Documentation

**AGM Specification v0.1 — Community Draft**

Agent Governance Manifest (AGM) is a project-side, agent-readable governance manifest for making agent-mediated open-source contributions reviewable, evidence-oriented, and accountable.

Status: Community Draft v0.1.0  
Repository: https://github.com/agent-governance-manifest/agent-governance-manifest  
Website: https://agent-governance-manifest.github.io/agent-governance-manifest/

## Documentation

- [AGM Specification v0.1 — Community Draft](AGM_SPEC_v0.1.md)
- [Human Guide to `.agm/`](AGM_HUMAN_GUIDE.md)
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