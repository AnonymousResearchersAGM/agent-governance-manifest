# AGM Maintainer Review Packet

## Risk Summary

- highest_risk_level: critical
- matched_risk_zones:
  - file: app/auth.py; zone: authentication; level: critical
  - file: tests/test_auth.py; zone: tests; level: medium
- affected_files:
  - app/auth.py
  - tests/test_auth.py

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
  - test_report
  - trace_manifest
- missing_evidence:
  - contribution_report.md field: ai_assistance_disclosure
  - contribution_report.md field: contribution_summary
  - contribution_report.md field: known_limitations
  - contribution_report.md field: linked_issues
  - contribution_report.md field: missing_evidence
  - contribution_report.md field: test_outcomes
  - contribution_report.md field: tests_run
  - human_review_declaration.md field: notes
  - human_review_declaration.md field: reviewed_evidence_files
  - human_review_declaration.md field: reviewer_name_or_role
  - linked_issue_or_explicit_no_issue_note
  - test_report.md field: commands
  - test_report.md field: coverage_notes
  - test_report.md field: environment
  - test_report.md field: failures
  - test_report.md field: outcomes
  - trace_manifest.json field: linked_issues

## Test-Evidence Summary

- tests_run: TBD: list test commands or not run.
- test_outcomes: TBD: pass, fail, or not run with concise result.
- coverage_notes: TBD: behavior covered by tests

## Provenance Summary

- ai_assistance_disclosure: TBD: disclose AI assistance at a high level; do not include prompts or private reasoning.
- submitted_files: contribution_report.md, human_review_declaration.md, test_report.md, trace_manifest.json
- human_confirmation_status: required pending
- reasoning_materials_excluded: true

## Linked Issue Context

- linked_issues: TBD: issue id/url or explicit none.
- issue_related_hints:
  - Check whether the implementation and tests address linked issue context: TBD: issue id/url or explicit none.

## Suggested Reviewer Attention Points

- Check password verification, authorization boundaries, and regression coverage.
- Inspect security-sensitive behavior and confirm human review status before merge.
- Resolve missing evidence before treating the packet as complete.
- Review tests for behavior coverage, not only command success.

## Human Maintainer Final-Decision Note

The review agent provides support artifacts only. Approval, rejection, or merge remains the responsibility of the human maintainer.
