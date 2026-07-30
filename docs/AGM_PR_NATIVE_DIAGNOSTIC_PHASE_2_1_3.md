# AGM PR-native Diagnostic Phase 2.1.3

Phase 2.1.2 established a trusted-source projection. Phase 2.1.3 couples a
verified sidecar artifact to the existing canonical evidence path: explicit
project-requirement references, registration, validation, binding, compiled
current state, responsibility, gate and participant route now share one
record. This prototype has no GitHub/GitLab adapter and is not authorised for
a new participant study.

`SidecarEvidenceBridge` verifies package, case, policy, contribution and
artifact bindings, validates the artifact-to-requirement mapping, then calls
the public evidence-registration service. It never appends case evidence or
changes a lifecycle state directly. D2 has no current test result; D3 is the
complete bridged positive path. D6A records a canonical conflict for
maintainer action and D6B records only a maintainer's legal repair request.

Risk locations are parsed from a digest-verified unified diff. Free-text PR
description cannot select files, lines or severity. The loopback artifact
endpoint is a controlled read-only viewer. Artifact status remains
`pending_human_review`.

## Participant-facing presentation patch

The Phase 2.1.3 participant view now separates three concepts that were
previously easy to conflate:

- **当前待办归属** identifies who must act first for review to continue;
- **下一步需要完成** states that concrete action; and
- **最终决定权** remains with the human maintainer.

The internal `current_responsibility` compiler model is unchanged. It is an
internal routing input, not the primary participant label. The page never
claims that AGM, an agent, the local viewer, or a pilot harness can approve or
merge a platform PR.

For D9, a read-only `VerificationSubmissionProjection` makes the missing
handoff observable. It reports that the PR exists, the current materials pass
the completeness check, this low-risk contribution does not require an extra
contributor confirmation, and no maintainer-verification submission record
has been generated. The projection is derived from the existing case,
current package, completeness result, and absent submission state. It is not
persisted and does not create evidence, a receipt, an attestation, an
obligation result, or a lifecycle transition.

Structured artifact pages use one source:

```text
canonical UTF-8 artifact bytes
  -> JSON or YAML safe parser
  -> deterministic Markdown projection
  -> restricted HTML renderer
```

The default readable tab and the raw-data tab retain the same artifact ID,
source digest, package binding, and contribution binding. JSON uses two-space
indentation; YAML uses block style and an indented safe dumper. The exact raw
copy comes from the original decoded source, while the formatted copy comes
from the pretty display. Digest calculation continues to cover the original
content. A malformed structured artifact keeps its inert raw view and gets no
apparently valid readable projection.

The Markdown is display-only: it is not registered as evidence and cannot
satisfy an obligation. Its restricted renderer escapes every source value,
does not accept raw HTML or links, and is served under a CSP that disallows
external images, network connections, frames, objects, and unapproved
scripts.

### Deterministic output hash audit

Fresh regeneration changes 33 presentation hashes and no `case.json` hash:

- all 11 `diagnosis.json` files add the compatible action-owner,
  next-action, and final-authority projection fields; D9 additionally adds
  the non-persisted verification-submission projection, and D10 exposes the
  existing final receipt through the controlled artifact route;
- all 11 `report.md` files replace the ambiguous owner line with the three
  participant-facing responsibility lines; and
- all 11 `report.html` files make the same responsibility separation and
  replace one-line structured previews with deterministic readable previews.

The 11 canonical scenario `case.json` files are byte-for-byte unchanged.
Accordingly, `expected_sha256.json` changes exactly those 33 presentation
entries and retains all 11 case hashes.
