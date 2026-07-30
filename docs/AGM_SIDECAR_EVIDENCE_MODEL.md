# Sidecar evidence model

Packages live in `.agm-work/evidence_store/`, never in tracked project source or a Git commit.

`SidecarEvidenceStore` writes canonical JSON to a SHA-256-named directory. A later write with the same digest must byte-match, making a package immutable by digest.

Each package binds case ID, contribution fingerprint, policy fingerprint, creation time, producer, and bounded artifact references. New commits create new packages. Old packages remain auditable but are not current evidence.

Caller-controlled paths are not accepted. Secret-like content, raw prompts, chain-of-thought, and unbounded terminal transcripts are rejected.

Final receipts are sidecar JSON and never amend a commit or call a platform API.

Phase 2.1.1 connects this model to D3 (current package), D7 (historical stale package after legal resubmission), and D10 (typed final receipt). A receipt rejects a claimed platform merge or approval without verified adapter evidence.

Phase 2.1.2 validates package and artifact digests before using sidecar content in a diagnostic projection.
# Phase 2.1.3 continuity

Satisfiable sidecar artifacts require explicit project-requirement references
and must enter canonical registration and validation.
