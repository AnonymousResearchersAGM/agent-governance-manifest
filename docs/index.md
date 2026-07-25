# Agent Governance Manifest Documentation

**AGM v0.1 Research Snapshot and vNext Development**

Agent Governance Manifest (AGM) is a project-side, agent-readable governance manifest for making agent-mediated open-source contributions reviewable, evidence-oriented, and accountable.

Status: Community Draft v0.1.0  
Repository: https://github.com/agent-governance-manifest/agent-governance-manifest  
Website: https://agent-governance-manifest.github.io/agent-governance-manifest/

## Documentation

- [AGM vNext Design](AGM_VNEXT_DESIGN.md)
- [AGM vNext Development Specification](AGM_VNEXT_SPEC.md)
- [vNext Contributor Guide](AGM_VNEXT_CONTRIBUTOR_GUIDE.md)
- [vNext Maintainer Guide](AGM_VNEXT_MAINTAINER_GUIDE.md)
- [vNext Adoption and Migration](AGM_VNEXT_ADOPTION_AND_MIGRATION.md)
- [vNext Authority and State Model](AGM_VNEXT_AUTHORITY_AND_STATE.md)
- [v0.1 Research Snapshot](V0_1_RESEARCH_SNAPSHOT.md)
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
