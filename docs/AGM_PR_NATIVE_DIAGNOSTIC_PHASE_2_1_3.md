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
