# Reviewer Guidance Layer demonstrations

These eight generated scenarios exercise the guidance view without encoding a
preferred maintainer answer:

1. multi-risk contribution with missing requirements;
2. material change with partial evidence invalidation;
3. scoped repair preserving unaffected evidence;
4. unauthorized contributor-agent verification;
5. lightweight low-risk contribution;
6. governance self-modification;
7. policy migration warning; and
8. human final decision and closure.

Regenerate the JSON, Markdown, and HTML outputs from a clean clone:

```bash
PYTHONPATH=src python scripts/generate_reviewer_guidance_demos.py
git status --short
```

Deterministic research-fixture mode is the default, so a frozen clean checkout
remains clean and per-file SHA-256 hashes remain identical after regeneration.
Use `--runtime-random` only to exercise ordinary random IDs and runtime selector
signing during development; the fixed demo context is never a production
session context.

Every scenario directory contains `guidance.json`, `report.md`, and
`report.html`. JSON contains the complete guidance view, workflow and
requirement snapshots, current responsibility, action groups, unavailable
summary, context selector data, trace mapping, dry-run preview, and the final
verification record when one exists. Markdown and HTML are rendered from that
same view model.

These are development demonstrations, not a formal experiment package or a
human acceptance record.
