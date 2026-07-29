# Trusted diagnostic evidence projection

`TrustedDiagnosticEvidenceResolver` resolves the current package by case ID,
contribution fingerprint and policy fingerprint, verifies its digest, then
reads artifact content through the sidecar store. It also lists historical
packages without allowing them to satisfy a current obligation. Agent activity
and contributor declarations are trusted only when they are artifacts in that
verified current package. Human confirmations remain legal case attestations.

This is a projection boundary, not a change to AGM evidence binding,
attestation, responsibility or lifecycle semantics.
# Phase 2.1.3 continuity

Trusted projection is now downstream of the SidecarEvidenceBridge: current
and missing project requirements come from canonical evidence compilation.
