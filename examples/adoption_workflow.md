# AGM Adoption Workflow Example

1. A contributor-side coding agent receives the original coding task.
2. The AGM contributor skill does not take over coding. It only reminds the agent to read `.agm/manifest.yml`.
3. The agent reads the manifest, the referenced risk zones, and the evidence requirements.
4. The agent changes `demo_app/auth.py`, which is classified as critical risk.
5. The agent prepares an evidence package with `human_review_declaration.status: pending_human_review`.
6. A human contributor reviews the auth-sensitive logic, test output, and limitations, then updates the declaration to `human_reviewed`.
7. The maintainer-side agent uses the base AGM plus the submitted evidence package to generate a reference-vs-observed diagnostic report.
8. The report highlights risk-zone classification, required evidence, human review declaration, governance entrypoint changes, and final decision authority.
9. The human maintainer makes the final decision.

AGM skills and discovery files are optional adoption helpers. Canonical governance rules remain in `.agm/`.
