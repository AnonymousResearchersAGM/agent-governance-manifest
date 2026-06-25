# Public Release Checklist

- [ ] Remove `__pycache__` directories and `*.pyc` files.
- [ ] Remove `.pytest_cache`.
- [ ] Check for local absolute paths.
- [ ] Check for personal access tokens, API keys, credentials, or secrets.
- [ ] Check that no raw private data is included.
- [ ] Check README commands work from a fresh environment.
- [ ] Run `python -m pytest`.
- [ ] Run the core reproduction commands in `README.md`.
- [ ] Finalize `LICENSE`.
- [ ] Update `CITATION.cff` with final repository URL and paper metadata.
- [ ] Create a git tag for the artifact release.
- [ ] Create a GitHub release.
- [ ] Optionally archive the release on Zenodo.
- [ ] Update the manuscript Data and Code Availability statement.

