# Agent Instructions

This repository uses Agent Governance Manifest (AGM).

Before making or submitting changes, coding agents should read:

- `.agm/manifest.yml`
- the risk-zone and evidence-requirement files referenced by the manifest

AGM is the canonical governance source. This file is only a discovery pointer.

Contributor-side agents should prepare an AGM-compliant evidence package for their changes. Do not invent evidence. If required evidence is missing, state that it is missing.

If human review is required and no human has reviewed the change, keep the human review declaration as `pending_human_review`.

Final review and acceptance remain with human maintainers.
