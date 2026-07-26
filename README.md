# Agent Governance Manifest (AGM)

AGM is project-side governance infrastructure that resolves project rules
against a concrete contribution, compiles contribution-specific obligations
and authority boundaries, binds evidence and human accountability to the
actual change, and supports authorized verification, repair, final human
decision, and auditable closure.

Status:

- AGM v0.1.0 remains the immutable reported research snapshot.
- AGM vNext is isolated `v0.2-dev` design development, not a stable release and
  not behavior validated by the existing v0.1.0 studies.

AGM is an open research artifact, not a commercial product, platform lock-in
mechanism, or vendor-specific agent workflow.

## Specification and Documentation

- [vNext Development Specification](docs/AGM_VNEXT_SPEC.md)
- [vNext Design](docs/AGM_VNEXT_DESIGN.md)
- [vNext Contributor Guide](docs/AGM_VNEXT_CONTRIBUTOR_GUIDE.md)
- [vNext Maintainer Guide](docs/AGM_VNEXT_MAINTAINER_GUIDE.md)
- [Reviewer Guidance Layer](docs/AGM_REVIEWER_GUIDANCE_LAYER.md)
- [Reviewer Guidance Maintainer Guide](docs/AGM_MAINTAINER_GUIDE.md)
- [vNext Adoption and Migration](docs/AGM_VNEXT_ADOPTION_AND_MIGRATION.md)
- [v0.1 Research Snapshot](docs/V0_1_RESEARCH_SNAPSHOT.md)
- [Documentation Home](docs/index.md)
- [Human Guide to `.agm/`](.agm/README.md)
- [AGM Specification v0.1 — Community Draft](docs/AGM_SPEC_v0.1.md)
- [Prototype Usage Guide](docs/PROTOTYPE_USAGE.md)
- [Agent Skill Profiles](docs/AGM_AGENT_SKILLS.md)
- [Human Review Declaration](docs/HUMAN_REVIEW_DECLARATION.md)
- [Dogfooding Report](docs/DOGFOODING_REPORT.md)

## vNext Quick Start

```bash
python -m pip install -e .
python -m agm.vnext.cli project validate
python -m agm.vnext.cli project simulate \
  --changed-file demo_app/auth.py \
  --changed-file requirements.txt \
  --mode declared_agent_mediated \
  --autonomy-profile supervised_agent
```

The vNext lifecycle is:

`Resolve -> Compile -> Bind -> Attest -> Verify -> Repair -> Decide -> Record`

Runtime cases live under ignored `.agm-work/`. Contributor and maintainer
commands are separated:

```bash
python -m agm.vnext.cli contributor --help
python -m agm.vnext.cli maintainer --help
python -m agm.vnext.cli case --help
```

Run the deterministic ten-scenario development demonstration:

```bash
python scripts/run_vnext_demo.py
```

## v0.1 Compatibility Quick Start

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

- complete matched-rule sets and multi-risk interaction rules;
- obligations compiled from risk, autonomy, and assurance profiles;
- evidence bound to policy, change fingerprint, scope, environment, and time;
- explicit accountable-human and maintainer operations;
- authority-typed state transitions, scoped repair, migration diagnostics, and
  closure receipts; and
- contributor and maintainer reference-versus-observed reports.

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
- `src/agm/vnext/`: isolated vNext models, policy compiler, evidence binding,
  state machine, repair/migration services, reports, local panels, storage, and
  CLI.
- `.agm-work/`: ignored local vNext case runtime.
- `scripts/`: small CLI wrappers around the core AGM engine.
- `tests/`: pytest coverage for AGM behavior.
- `docs/`: specification, usage guide, adoption guidance, and dogfooding report.
- `examples/`: compact adoption workflow examples.
- `legacy/`: historical experimental materials that are not part of AGM v0.1.0 core.

## Human Review Boundary

`eligible_for_human_decision` means the contribution has enough governance evidence to enter human decision-making. It does not mean the contribution is accepted. Approval, rejection, request-for-changes, or merge decisions remain with human maintainers.

## Citation and License

See [CITATION.cff](CITATION.cff) and [LICENSE](LICENSE). Repository URL, DOI, and final paper author order should be updated before archival release.
