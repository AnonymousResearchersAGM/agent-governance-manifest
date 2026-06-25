# Medium Test Addition

This public-facing alias mirrors `medium_risk_test_addition.md`.

- task_title: "Add tests for discount validation"
- task_description: "Add tests that cover invalid discount percentages in core business logic."
- expected_affected_files:
  - `tests/test_core.py`
- expected_risk_level: "medium"
- required_evidence_under_manifest:
  - contribution_report
  - test_report
  - trace_manifest
- baseline_condition_note: "A baseline agent may say tests were added but omit structured evidence."
- manifest_supported_condition_note: "An AGM-supported agent should report tests run, outcomes, and trace manifest metadata."
- expected_reviewer_concerns:
  - "Confirm tests cover invalid lower and upper bounds."
  - "Confirm no application behavior changed."

