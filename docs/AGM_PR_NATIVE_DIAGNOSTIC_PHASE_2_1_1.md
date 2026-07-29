# AGM Phase 2.1.1: semantic and lifecycle integrity

Phase 2.1 provided an architecture scaffold. Phase 2.1.1 rebuilds D1--D10 through public `GovernanceService` operations: evidence preparation, preparation/submission, human confirmation, verification, repair, resubmission, denied-operation auditing, and final decision recording.

The PR diagnosis is a compiled-state projection. Its route derives from the existing responsibility derivation, lifecycle stage, state-machine legal operations, blocking materials, and the current gate. Evidence presentation distinguishes absent, invalid, expired, rejected, old-version, unbound, and current material without creating new governance states.

D3 uses a current sidecar evidence package. D7 creates a package for the old contribution, then uses legal resubmission to make its test material stale. D10 records a typed sidecar final receipt. No GitHub/GitLab adapter exists; local platform status is unconnected, unapproved, and unmerged.

P92 remains paused, no new P92 material is created, and no usability experiment or Phase 3 work has begun. Artifact status remains `pending_human_review`.
