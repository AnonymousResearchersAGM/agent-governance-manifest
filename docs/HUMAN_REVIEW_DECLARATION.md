# Human Review Declaration

Human review declaration is a governance statement in an AGM evidence package. It is not approval, rejection, or merge authorization.

## Status Values

- `not_required`: Human review declaration is not required for the detected risk level.
- `pending_human_review`: Human review is required or requested, but no human has declared completion.
- `human_reviewed`: A human contributor or reviewer declares that the scoped review was completed.
- `maintainer_review_required`: Maintainer attention is required before the contribution can be considered ready.

For low and medium risk, `not_required` is normally acceptable unless the project AGM says otherwise.

For high risk, `pending_human_review` is allowed but lowers readiness when the package declares human review as required.

For critical risk, `pending_human_review` is not enough for final-acceptance readiness. Critical evidence must include a complete `human_reviewed` declaration to become `eligible_for_human_decision`.

`human_reviewed` does not mean accepted. Final decisions remain with human maintainers.

## Pending Form

```yaml
human_review_declaration:
  required: true
  status: pending_human_review
  reviewer: null
  reviewed_at: null
  review_scope: null
  statement: "Human review is required before final acceptance."
```

## Reviewed Form

```yaml
human_review_declaration:
  required: true
  status: human_reviewed
  reviewer: "human contributor"
  reviewed_at: "2026-06-24T00:00:00Z"
  review_scope:
    - "Reviewed auth-sensitive logic"
    - "Checked test output"
    - "Confirmed known limitations"
  statement: "I reviewed the security-sensitive change and confirm that it is ready for maintainer review."
```

## Updating a Declaration

Use the lightweight helper:

```bash
python scripts/mark_human_review.py evidence_packages/example.yml \
  --reviewer "human contributor" \
  --scope "Reviewed auth-sensitive logic" \
  --scope "Checked test output" \
  --statement "I reviewed this change and confirm it is ready for maintainer review."
```

Agents must not fabricate human review. If no human has reviewed the change, keep `status: pending_human_review`.
