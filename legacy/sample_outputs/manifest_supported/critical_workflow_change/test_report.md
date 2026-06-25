# AGM Test Report

## Structured Fields

- commands:
  - "python -m pytest"
  - "python scripts/classify_risk_zone.py workflows/ci.yml"
  - "python scripts/validate_evidence_package.py workflows/ci.yml --evidence-dir sample_outputs/manifest_supported/critical_workflow_change"
- environment: "Local Windows environment; Python 3.14.5 reported by pytest."
- outcomes:
  - command: "python -m pytest"
    result: "pass"
    summary: "Collected 7 tests from tests\\test_auth.py and tests\\test_core.py; 7 passed in 0.22s."
  - command: "python scripts/classify_risk_zone.py workflows/ci.yml"
    result: "pass"
    summary: "Classified workflows/ci.yml in risk zone workflow with highest risk level critical and required critical evidence."
  - command: "python scripts/validate_evidence_package.py workflows/ci.yml --evidence-dir sample_outputs/manifest_supported/critical_workflow_change"
    result: "pass"
    summary: "Validated the evidence package as complete with submitted critical evidence and no missing evidence."
- coverage_notes: "Application tests cover existing auth and core behavior. Classification verifies the changed workflow file maps to the manifest critical workflow risk zone."
- failures:
  - "none"

## Notes

The CI workflow itself was changed locally but was not executed by GitHub Actions in this environment.

