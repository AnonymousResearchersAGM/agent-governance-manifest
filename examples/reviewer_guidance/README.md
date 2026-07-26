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

Regenerate the JSON and HTML outputs from a clean clone:

```bash
python scripts/generate_reviewer_guidance_demos.py
```

Every JSON file contains the complete guidance view, derived workflow and
requirement snapshots, available and unavailable actions, a dry-run action
preview, and the final verification record when one exists. The HTML file is
rendered from that same view model.

These are development demonstrations, not a formal experiment package or a
human acceptance record.
