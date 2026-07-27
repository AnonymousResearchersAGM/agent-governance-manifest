# AGM Review Briefing Layer — Phase 1 demos

This directory contains deterministic, read-only human-work briefs compiled
from the same eight governance cases used by the Reviewer Guidance Layer.

Each scenario contains:

- `brief.json`: the complete `ReviewBriefView`, including collapsed technical
  trace data;
- `brief.md`: the participant-readable Markdown brief;
- `brief.html`: the standalone, read-only HTML brief.

Regenerate the outputs from the repository root:

```bash
python scripts/generate_review_briefing_demos.py
```

These artifacts are design and review fixtures. They are not a P92 experiment
package, human attestation, maintainer verification, final decision, or merge
approval.
