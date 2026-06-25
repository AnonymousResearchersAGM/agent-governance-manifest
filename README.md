# Agent Governance Manifest (AGM)

AGM is a project-side, agent-readable governance manifest for making agent-mediated open-source contributions reviewable, evidence-oriented, and accountable.

Status: Community Draft v0.1.0. AGM is an open research artifact, not a commercial product, platform lock-in mechanism, or vendor-specific agent workflow.

## Specification and Documentation

- [Documentation Home](docs/index.md)
- [Human Guide to `.agm/`](.agm/README.md)
- [AGM Specification v0.1 — Community Draft](docs/AGM_SPEC_v0.1.md)
- [Prototype Usage Guide](docs/PROTOTYPE_USAGE.md)
- [Agent Skill Profiles](docs/AGM_AGENT_SKILLS.md)
- [Human Review Declaration](docs/HUMAN_REVIEW_DECLARATION.md)
- [Dogfooding Report](docs/DOGFOODING_REPORT.md)

## Quick Start

AGM v0.1.0 uses `.agm/` as the canonical governance source:

1. A repository defines canonical rules in `.agm/`.
2. A contributor-side agent reads `.agm/manifest.yml` and the referenced risk-zone and evidence-requirement files.
3. The agent prepares an evidence package for the contribution.
4. A maintainer-side agent or human reviewer compares base AGM reference values with contribution evidence.
5. The review packet produces a reference-vs-observed governance report.
6. Final decisions remain with human maintainers.

Install the lightweight prototype dependencies and run tests:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

Validate example evidence packages:

```bash
python scripts/validate_evidence_package.py evidence_packages/valid_critical_auth.yml
python scripts/validate_evidence_package.py evidence_packages/placeholder_evidence.yml
```

Generate a maintainer-facing review packet:

```bash
python scripts/generate_review_packet.py evidence_packages/valid_critical_auth.yml --output-dir review_packets
```

Run the demo app:

```bash
python -m demo_app.app
```

## What AGM Does

AGM helps projects define:

- risk zones for files and paths;
- evidence requirements by risk level;
- contribution-side evidence package expectations;
- human review declaration requirements;
- maintainer-facing diagnostic review packets;
- reference-vs-observed governance reports.

## What AGM Is Not

AGM is not:

- AGENTS.md;
- a PR template;
- an AI detector;
- an agent trace or provenance log;
- an automatic merge/reject tool;
- a replacement for human maintainers.

## Adoption Options

AGM can be used in several ways:

- Directly: humans or agents read `.agm/` materials.
- With agent skills: use the contributor-side and maintainer-side AGM skill profiles in `skills/`.
- With discovery pointers: use `AGENTS.md` or `CLAUDE.md` to tell Codex, Claude Code, or other coding agents to read `.agm/manifest.yml`.
- With reference tooling: use the included lightweight validator and report generator for reproducible checks.

The canonical governance source remains `.agm/`. Skills, `AGENTS.md`, and `CLAUDE.md` are adoption-layer helpers.

## Repository Structure

- `.agm/`: canonical manifest, risk zones, and evidence requirements.
- `demo_app/`: minimal Python task tracker used as the governed project.
- `evidence_packages/`: YAML evidence packages for valid, missing, placeholder, and dogfooding cases.
- `review_packets/`: generated maintainer-facing review packet examples and small test artifacts.
- `skills/`: optional contributor-side and maintainer-side AGM adoption profiles.
- `src/agm/`: manifest loading, risk classification, evidence validation, gate-state calculation, and review packet generation.
- `scripts/`: small CLI wrappers around the core AGM engine.
- `tests/`: pytest coverage for AGM behavior.
- `docs/`: specification, usage guide, adoption guidance, and dogfooding report.
- `examples/`: compact adoption workflow examples.
- `legacy/`: historical experimental materials that are not part of AGM v0.1.0 core.

## Human Review Boundary

`eligible_for_human_decision` means the contribution has enough governance evidence to enter human decision-making. It does not mean the contribution is accepted. Approval, rejection, request-for-changes, or merge decisions remain with human maintainers.

## Citation and License

See [CITATION.cff](CITATION.cff) and [LICENSE](LICENSE). Repository URL, DOI, and final paper author order should be updated before archival release.
