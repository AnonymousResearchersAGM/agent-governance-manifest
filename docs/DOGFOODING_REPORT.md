# AGM Dogfooding Report

Date: 2026-06-24

Version: v0.1.0

Status: Community Draft

## Contributor-side Agent Pass

The contributor-side agent first read the AGM discovery pointer:

- `AGENTS.md`

It then read the canonical AGM files:

- `.agm/manifest.yml`
- `.agm/risk_zones.yml`
- `.agm/evidence_requirements.yml`

## Demo Change

The selected demo change was a small critical-risk authentication update:

- `demo_app/auth.py`: normalize token whitespace before lookup.
- `demo_app/tests/test_auth.py`: add a regression test for accidental leading/trailing whitespace.

The changed auth file is classified as critical. The test file is classified as high/configuration.

## Tests Actually Run

Command:

```bash
python -m pytest demo_app/tests/test_auth.py
```

Observed result:

```text
4 passed in 0.27s
```

The test artifact was recorded at:

- `review_packets/artifacts/dogfood_auth_pytest.txt`

## Evidence Package

The contributor-side simulation generated:

- `evidence_packages/dogfood_auth_pending.yml`

The evidence package records:

- changed files;
- detected critical/high risk zones;
- required evidence from AGM;
- test command and artifact;
- known limitations;
- `human_review_declaration.status: pending_human_review`.

The declaration remains pending because no real human review was performed during this agent-run dogfooding pass. The agent did not fabricate `human_reviewed`.

## Maintainer-side Agent Pass

The maintainer-side agent used the current repository `.agm/` files as reference values:

- base/current `.agm/manifest.yml`;
- referenced risk zones;
- referenced evidence requirements.

It read the submitted evidence package:

- `evidence_packages/dogfood_auth_pending.yml`

It generated the diagnostic report at:

- `review_packets/dogfood/review_packet.md`
- `review_packets/dogfood/review_packet.json`

## Reference-vs-observed Findings

The diagnostic report included these governance indicators:

- AGM reference source: Pass.
- Governance entrypoint change: Pass, none detected.
- Risk-zone classification: Pass, authentication and configuration detected.
- Required tests: Pass, command and artifact provided.
- Human review declaration: Blocked, observed `pending_human_review` for critical risk.
- Placeholder evidence: Pass, absent.
- Final decision authority: Pass, human decision required.

Gate state:

- `governance_gate_status: blocked`
- `technical_review_readiness: not_ready`
- `final_acceptance_readiness: blocked_by_policy`

This is the expected result for critical risk with pending human review.

## Usability Gaps Found

The initial reviewer attention point for incomplete evidence was too artifact/test-specific. In this dogfooding case, the incomplete condition was pending human review. The message was revised to say that human review remains pending and the contribution must not be treated as final-acceptance ready.

## Small Corrections Made

- Updated reviewer attention point generation for pending human review.
- Regenerated the dogfooding review packet after the correction.

Final decision remains with human maintainers. This dogfooding pass did not approve, reject, or merge the demo change.
