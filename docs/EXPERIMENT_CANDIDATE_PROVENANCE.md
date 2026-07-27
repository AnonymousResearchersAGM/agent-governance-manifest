# Reviewer Guidance experiment candidate provenance

This file records non-governance provenance for the Reviewer Guidance
experiment candidate. It does not record a maintainer verification, human
evaluation, final decision, or acceptance.

- Experiment-candidate commit: the Git commit containing this file (resolve
  with `git rev-parse HEAD`; the hash is not embedded because a commit cannot
  contain its own content-derived identifier).
- Parent commit:
  `a529a5c82a1c53f7eb49592f7f9e36e38d84fa46`.
- Canonical policy fingerprint:
  `e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564`.
- Frozen output manifest:
  `examples/reviewer_guidance/expected_sha256.json`.
- Complete test suite: 221 tests.
- Windows validation: 25 frozen outputs verified and 221 tests passed.
- Linux validation: WSL2 Ubuntu verified the same 25 frozen outputs and all
  221 tests.
- Windows/Ubuntu CI matrix: the existing
  `.github/workflows/reviewer-guidance-reproducibility.yml` workflow is the
  authoritative check for the pushed candidate commit.
- P91 cognitive testing has not been performed.
- The implementation artifact remains `pending_human_review`.

