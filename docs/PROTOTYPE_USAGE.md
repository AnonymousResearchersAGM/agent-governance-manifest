# AGM Prototype Usage

Version: v0.1.0

Status: Community Draft

Run commands from the repository root:

```bash
cd agm_prototype
python -m pip install -r requirements.txt
```

## Adoption Options

Option A: Directly read `.agm/`.

- Read `.agm/manifest.yml`.
- Follow the referenced risk-zone and evidence-requirement files.
- Generate or validate evidence packages with the local scripts.

Option B: Use AGM contributor / maintainer skills.

- `skills/agm-contributor/skill.md` is a non-invasive governance overlay for contribution-side agents.
- `skills/agm-maintainer/skill.md` is a diagnostic assistant for maintainer-side review.
- Skills are optional adoption helpers, not canonical rules.

Option C: Use discovery pointers.

- `AGENTS.md` and `CLAUDE.md` tell agents where to find AGM.
- They should remain thin pointers to `.agm/manifest.yml`.

Canonical AGM rules remain in `.agm/`.

## End-to-end Governance Workflow

1. Contributor agent reads `AGENTS.md` or `CLAUDE.md`, then reads `.agm/manifest.yml`.
2. Contributor agent completes the requested code change without letting AGM replace the coding task.
3. Contributor agent generates an evidence package. If no human has reviewed the change, the human review declaration remains `pending_human_review`.
4. A human contributor may update the declaration to `human_reviewed`.
5. Maintainer agent reads the base AGM plus the submitted evidence package and changed files.
6. Maintainer agent generates a diagnostic report with reference-vs-observed governance indicators.
7. Human maintainer decides.

## Simulate Contribution-side Agent Evidence Generation

The prototype includes a deterministic local simulation of a contribution-side agent. It reads:

- `.agm/manifest.yml`
- `.agm/risk_zones.yml`
- `.agm/evidence_requirements.yml`

Then it classifies the changed files, records the required evidence for the detected risk level, and writes one evidence package YAML file. This simulation does not call an LLM, network service, GitHub API, or CI platform.

```bash
python scripts/simulate_contribution_agent.py \
  --contribution-id simulated-critical-auth \
  --changed-files demo_app/auth.py demo_app/tests/test_auth.py \
  --summary "Simulated auth-token contribution with regression evidence." \
  --rationale "Auth behavior is security-sensitive and requires explicit test evidence." \
  --security-auth-impact "Token authentication and role checks are affected." \
  --test-command "python -m pytest demo_app/tests/test_auth.py" \
  --test-outcome "passed" \
  --artifact "review_packets/artifacts/critical_auth_pytest.txt::Auth pytest output" \
  --known-limitations "No persistent session store or network boundary is implemented in this prototype." \
  --human-review-status pending_human_review \
  --output evidence_packages/agent_generated_critical_auth.yml
```

The generated package can be validated immediately:

```bash
python scripts/validate_evidence_package.py evidence_packages/agent_generated_critical_auth.yml
```

If required facts are omitted, the simulated agent writes explicit `TODO` placeholders; validation then blocks or requests evidence.

To mark a package as human-reviewed after real human review:

```bash
python scripts/mark_human_review.py evidence_packages/agent_generated_critical_auth.yml \
  --reviewer "human contributor" \
  --scope "Reviewed auth-sensitive logic" \
  --scope "Checked test output" \
  --statement "I reviewed this change and confirm it is ready for maintainer review."
```

This declaration is not approval and does not replace maintainer review.

## Validate Evidence Packages

Low-risk documentation evidence:

```bash
python scripts/validate_evidence_package.py evidence_packages/valid_low_risk.yml
```

Critical auth evidence with human declaration:

```bash
python scripts/validate_evidence_package.py evidence_packages/valid_critical_auth.yml
```

Missing evidence package:

```bash
python scripts/validate_evidence_package.py evidence_packages/missing_evidence.yml
```

Placeholder evidence package:

```bash
python scripts/validate_evidence_package.py evidence_packages/placeholder_evidence.yml
```

Missing artifact package:

```bash
python scripts/validate_evidence_package.py evidence_packages/missing_artifact.yml
```

## Generate Review Packet

```bash
python scripts/generate_review_packet.py evidence_packages/valid_critical_auth.yml --output-dir review_packets
```

This writes:

- `review_packets/review_packet.json`
- `review_packets/review_packet.md`

The Markdown packet includes the `Governance Indicator / Reference / Observed / Status` table.

## Classify Changed Files

```bash
python scripts/classify_risk_zone.py docs/PROTOTYPE_USAGE.md
python scripts/classify_risk_zone.py demo_app/tasks.py
python scripts/classify_risk_zone.py demo_app/config.py
python scripts/classify_risk_zone.py demo_app/auth.py
```

## Run Demo App

```bash
python -m demo_app.app
```

Expected output:

```text
1:Prepare AGM evidence package:alice
```

## Run Tests

```bash
python -m pytest -q
```

The tests cover demo app behavior, risk classification, evidence validation, placeholder detection, missing artifact detection, gate states, malformed inputs, and review packet generation.
