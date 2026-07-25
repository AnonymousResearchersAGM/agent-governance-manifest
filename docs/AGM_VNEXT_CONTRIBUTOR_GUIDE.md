# AGM vNext Contributor Guide

Status: `v0.2-dev`

Install the local package and validate project policy:

```bash
python -m pip install -e .
python -m agm.vnext.cli project validate
```

## Ordinary contributions

Preview a documentation change:

```bash
python -m agm.vnext.cli project simulate \
  --changed-file docs/example.md \
  --mode ordinary
```

If no rule requires a case, the result is
`no_agm_package_submitted`. This does not claim the contributor is human; the
project's ordinary review workflow continues.

## Open a managed case

```bash
python -m agm.vnext.cli contributor open-case \
  --changed-file docs/example.md \
  --mode declared_agent_mediated \
  --actor contributor-agent \
  --role contributor_agent \
  --autonomy-profile supervised_agent
```

Record the returned case ID. Inspect required obligation IDs:

```bash
python -m agm.vnext.cli case status --case CASE
```

## Bind evidence

Add one factual item per evidence semantic:

```bash
python -m agm.vnext.cli contributor add-evidence \
  --case CASE \
  --actor contributor-agent \
  --obligation O-SUMMARY \
  --evidence-type contribution_summary \
  --value "Updated the vNext contributor guide." \
  --scope docs/example.md \
  --source-tool codex
```

For command evidence, include `--command`, `--environment`, and
`--source-tool`. For artifact evidence, include a repository-contained
`--artifact-path`; AGM records its SHA-256 hash.

Do not use placeholders or invent tests. Missing evidence should remain
visible.

## Prepare and attest

```bash
python -m agm.vnext.cli contributor prepare \
  --case CASE \
  --actor contributor-agent

python -m agm.vnext.cli contributor review --case CASE --serve
```

When state is `awaiting_human_attestation`, the agent must pause. A human uses
the local panel or an explicit command:

```bash
python -m agm.vnext.cli contributor attest \
  --case CASE \
  --actor accountable-human \
  --role accountable_human \
  --scope docs/example.md \
  --statement "I reviewed this exact change and the bound evidence."
```

Attestation is scoped responsibility, not approval.

## Repair and resubmit

After a repair request, correct the change/evidence and record the attempt:

```bash
python -m agm.vnext.cli case resubmit \
  --case CASE \
  --actor contributor-agent \
  --role contributor_agent \
  --summary "Corrected the requested evidence." \
  --obligation O-SUMMARY
```

AGM recomputes bindings and invalidates only affected evidence or attestations.
The maintainer must reverify.
