# AGM Phase 2.1.2: Trusted Evidence Projection

Phase 2.1.1 repaired lifecycle semantics. Phase 2.1.2 makes the diagnostic
projection trust only canonical case records, legal human confirmations and
digest-verified sidecar packages. Presentation context can supply a friendly
title or line label, but cannot assert Agent participation, freshness, a
confirmation, a conflict, a receipt or a host-platform outcome.

The runtime keeps Git commit SHA, contribution fingerprint, policy
fingerprint, package digest, artifact digest and receipt digest separate.
Current valid material wins over historical stale, invalid or rejected
material. A denied operation is an informational record and no longer replaces
the contribution's actual lifecycle route. Low-risk work that does not compile
a human-confirmation requirement is shown as not required.

The project has no GitHub/GitLab adapter. AGM final recommendations therefore
remain separate from platform approval, merge and close state. P92 remains
paused; no participant experiment or Phase 3 work has begun.
# Phase 2.1.3 continuity

Phase 2.1.2 established trusted-source projection. Phase 2.1.3 registers
accepted sidecar material through canonical evidence rather than retaining a
parallel diagnostic evidence state.
