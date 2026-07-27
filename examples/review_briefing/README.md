# AGM Review Briefing Layer — Phase 1.1 and Phase 2 demos

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
python scripts/check_review_briefing_demo_hashes.py
git diff --exit-code
```

The frozen SHA-256 manifest covers all eight JSON/Markdown/HTML triples plus
`manifest.json`. CI executes the same check explicitly on Windows and Ubuntu.

These artifacts are design and review fixtures. They are not a P92 experiment
package, human attestation, maintainer verification, final decision, or merge
approval.

Phase 2 adds `interactive_outputs/` with one deterministic
`review_action_model.json` and `review_interactive.html` for the same eight
cases plus `09_pre_final_decision`. Static interaction models set
`live_actions_enabled=false` and contain no runtime CSRF, session, or preview
token.

```bash
python scripts/generate_review_interactive_demos.py
python scripts/check_review_interactive_demo_hashes.py
git diff --exit-code
```

`interactive_expected_sha256.json` freezes exactly 19 files. The
pre-final fixture exists only to review the visual and authority separation
between maintainer checking and final human decision.
