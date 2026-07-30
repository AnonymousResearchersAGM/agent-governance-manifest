# Review artifact serving boundary

Phase 2.1.3 adds a loopback-only read-only route at
`/artifacts/{case_id}/{package_digest}/{artifact_id}`. It verifies ownership,
rejects traversal and absolute paths, limits response size and renders active
content inert as escaped text with `nosniff` and a restrictive CSP. Storage
paths are never sent to the browser.

Runtime evidence is stored under ignored `.agm-work/evidence_store`. Package
and artifact identifiers reject traversal and absolute-path shaped input;
content digests are verified before projection. Frozen demos include safe
inline, deterministic material so an unavailable runtime package is never
presented as a working storage path. A future host route must validate case,
package and artifact ownership before serving content and must not expose the
store path, secrets, prompts or private conversations.
