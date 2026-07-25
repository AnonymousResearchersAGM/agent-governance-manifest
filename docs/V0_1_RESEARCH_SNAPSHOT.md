# AGM v0.1.0 Research Snapshot

Status: immutable reported research boundary

AGM v0.1.0 is the research artifact reported by the existing evaluation. AGM
vNext is new design development and must not be described as behavior already
implemented or validated by that evaluation.

## Recorded base

- Base branch: `main`
- Base commit: `c781a2f40d823ca8b5cc53fb43ccf2c4f88dfa1b`
- Recorded on: `2026-07-25`
- Baseline test command: `.venv\Scripts\python.exe -m pytest -q`
- Baseline result observed on the recorded source: `23 passed in 1.47s`

The source tree supplied without Git metadata was compared against every Git
blob in the recorded upstream commit. All 139 tracked files matched after Git
line-ending normalization.

## Preserved behavior

The v0.1 compatibility module remains `src/agm/governance.py`. Its risk
classifier:

1. records every matched `(file, risk zone, risk level)` observation;
2. applies the conservative default to unclassified paths;
3. calculates the highest detected risk level; and
4. selects one evidence-requirement profile from that highest level.

This highest-risk-only evidence selection is intentional historical behavior.
vNext uses a separate package and compiles the union of obligations from every
matched rule, applicable profile, and interaction rule.

## Evidence boundary

The v0.1 evidence supports claims about the reported v0.1 artifact only. It
does not validate:

- vNext multi-risk obligation compilation;
- autonomy-sensitive obligations;
- authority-typed state transitions;
- contributor or maintainer panels;
- repair, migration, override, or closure workflows; or
- usability, adoption, or organizational outcomes of those new mechanisms.

Compatibility tests protect v0.1 behavior, but maintenance of the compatibility
module is not permission to rewrite the historical claims.
