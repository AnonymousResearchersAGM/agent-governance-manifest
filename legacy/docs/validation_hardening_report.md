# Validation Hardening Report

This report documents v0.2.1 validation hardening for the AGM prototype.

## Hardened Behaviors

- Fresh skeleton evidence fails validation.
- Completed `critical_auth_change` evidence passes validation.
- Critical changes without `human_review_declaration.md` fail validation.
- Placeholder linked issue notes fail validation.
- Explicit `No linked issue` passes validation.
- Content-aware inspection can escalate risk to critical.
- Final pytest result before Round 3 preparation: `14 passed`.

## Placeholder Rejection

The validator treats empty fields and obvious placeholders as incomplete evidence, including `TBD`, `TODO`, `placeholder`, `not provided`, `fill me`, `to be filled`, `not run`, `unknown`, `n/a`, `<...>`, and `[...]`.

## Reproduction Commands

Completed critical evidence package:

```bash
python scripts/validate_evidence_package.py app/auth.py tests/test_auth.py --evidence-dir sample_outputs/manifest_supported/critical_auth_change
```

Skeleton evidence package:

```bash
python scripts/validate_evidence_package.py app/auth.py tests/test_auth.py --evidence-dir sample_outputs/manifest_supported/critical_auth_change_skeleton
```

Contributor flow with skeleton evidence:

```bash
python scripts/run_contributor_flow.py --task evaluation_tasks/critical_auth_change.md --changed-files app/auth.py tests/test_auth.py --evidence-dir sample_outputs/manifest_supported/critical_auth_change_skeleton
```

Content-aware risk escalation:

```bash
python scripts/classify_risk_zone.py app/config.py --inspect-content
```

Automated tests:

```bash
python -m pytest
```

## Interpretation

Evidence skeletons are useful starting points, not completed evidence. Validation only passes after contributors replace placeholders with independently checkable evidence. High and critical changes must include human review declarations.

