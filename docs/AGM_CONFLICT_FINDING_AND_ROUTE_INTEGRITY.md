# Conflict finding and route integrity

Trusted, same-version contribution declarations and coding-assistant activity
may produce a canonical `trusted_sidecar_conflict` finding. The presenter does
not create a blocking result. Before a legal repair request, D6A remains in
maintainer verification and asks a maintainer whether to request correction.
After the existing `request_repair` operation, D6B is `repair_requested` and
asks the contributor to act.

Denied-operation audit facts remain informational: D8 retains ordinary review
for its normal diff while showing that the unauthorised action did not take
effect. The implementation adds no transition, authority or final decision.
