# AGM vNext Maintainer Guide

Status: `v0.2-dev`

Maintainer verification must independently use canonical policy and the actual
change. Contributor assertions are observed values, not authority.

## Inspect

```bash
python -m agm.vnext.cli maintainer inspect --case CASE
python -m agm.vnext.cli maintainer inspect --case CASE --serve
```

Review:

- base and policy fingerprints;
- complete matched rules and interaction escalation;
- obligation reference versus observed state;
- evidence scope, hashes, freshness, and provenance fields;
- accountable-human event bindings;
- findings, repair attempts, and transition history; and
- separation-of-duty requirements.

## Authorized operations

Verify:

```bash
python -m agm.vnext.cli maintainer verify \
  --case CASE \
  --actor human-verifier \
  --role maintainer_verifier \
  --reason "Bindings and artifacts independently checked."
```

Request repair:

```bash
python -m agm.vnext.cli maintainer request-repair \
  --case CASE \
  --actor human-verifier \
  --role maintainer_verifier \
  --message "Test artifact does not cover the changed scope." \
  --obligation O-ARTIFACT
```

Other commands expose reject-evidence, ask-clarification,
invalidate-attestation, record-policy-conflict, resolve-policy-conflict, and
override operations. Every operation is role/state checked and appended to the
transition history.

Independent review obligations require a `maintainer` actor different from
evidence and attestation actors.

## Final decision

Only the authorized human `maintainer` role can decide:

```bash
python -m agm.vnext.cli maintainer decide \
  --case CASE \
  --actor human-maintainer \
  --role maintainer \
  --decision accept \
  --reason "Accepted after independent technical and governance review."
```

`verify` and `ready_for_human_decision` are not acceptance. Override is also a
separate operation and must be followed by an explicit final decision.
Terminal decisions produce `closure_receipt.yml`.
