# AGM Maintainer Review Packet

## Risk Summary

- highest_risk_level: critical
- matched_risk_zones:
  - file: workflows/ci.yml; zone: workflow; level: critical
- affected_files:
  - workflows/ci.yml

## Evidence Summary

- required_evidence:
  - contribution_report
  - test_report
  - trace_manifest
  - human_review_declaration
  - linked_issue_or_explicit_no_issue_note
- submitted_evidence:
  - contribution_report
  - human_review_declaration
  - linked_issue_or_explicit_no_issue_note
  - test_report
  - trace_manifest
- missing_evidence:
  - none

## Test-Evidence Summary

- tests_run: python -m pytest; python scripts/classify_risk_zone.py workflows/ci.yml; python scripts/validate_evidence_package.py workflows/ci.yml --evidence-dir sample_outputs/manifest_supported/critical_workflow_change
- test_outcomes: pass; pytest collected 7 tests and all passed, classifier reported workflow critical risk, and evidence validation returned valid true with no missing evidence.
- coverage_notes: Application tests cover existing auth and core behavior. Classification verifies the changed workflow file maps to the manifest critical workflow risk zone.

## Provenance Summary

- ai_assistance_disclosure: AI assistance was used to modify the workflow and prepare structured AGM evidence.
- submitted_files: contribution_report.md, human_review_declaration.md, test_report.md, trace_manifest.json
- human_confirmation_status: required pending
- reasoning_materials_excluded: true

## Linked Issue Context

- linked_issues: none
- issue_related_hints:
  - No linked issue supplied; reviewer may ask whether issue context exists.

## Suggested Reviewer Attention Points

- Check whether CI permissions or execution paths changed.
- Inspect security-sensitive behavior and confirm human review status before merge.
- Review tests for behavior coverage, not only command success.

## Human Maintainer Final-Decision Note

The review agent provides support artifacts only. Approval, rejection, or merge remains the responsibility of the human maintainer.

