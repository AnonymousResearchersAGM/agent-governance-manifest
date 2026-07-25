# AGM vNext Authority and State Model

Status: `v0.2-dev`

Canonical roles and permissions live under `.agm/roles/`. Canonical
transitions live in `.agm/workflows/state_machine.yml`.

| Role | Human | Representative authority |
| --- | --- | --- |
| `system` | no | Deterministic resolution, compilation, readiness calculation, and closure recording |
| `contributor_agent` | no | Open, prepare, submit, and resubmit |
| `contributor` | yes | Prepare, request correction, submit, and resubmit |
| `accountable_human` | yes | Confirm/decline scoped attestation or request correction |
| `maintainer_verifier` | yes | Verify/reject evidence, clarify, invalidate, request repair |
| `policy_steward` | yes | Diagnose and resolve policy conflicts |
| `maintainer` | yes | Verification plus override and final decisions |

The `system` role has no human authority. It cannot attest, verify as a
maintainer, override, or decide.

## Transition invariants

- An action must be present in both role permissions and a transition allowed
  from the current state.
- Terminal states cannot transition.
- Actor, role, action, source, target, reason, related records, and timestamp
  are appended to JSONL.
- Agents cannot acquire human authority by choosing a CLI flag; authorization
  is checked by the service.
- Independent review requires separation from evidence/attestation actors.
- All unresolved blocking obligations complete conjunctively.
- Open blocking findings prevent readiness.
- Override is recorded before and separately from final decision.
- Closure receipt follows, rather than precedes, a terminal human decision.
