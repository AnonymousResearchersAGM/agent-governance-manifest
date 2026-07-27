# AGM Review Briefing Phase 2.0.1

## Scope

Phase 2.0.1 aligns repaired contributions with the existing maintainer-review
lifecycle and hardens participant-facing and packaged artifacts. It does not
change canonical `.agm` policy, risk matching, obligation compilation,
authority, state-machine definitions or preconditions, evidence binding,
responsibility derivation, scoped repair, final decisions, closure, legacy, or
v0.1.

The artifact remains `pending_human_review`. P92 and Phase 3 have not started.

## Resubmission and maintainer stage

`resubmitted` means the contribution side has recorded a scoped repair. It
does not itself hand the case to a maintainer. The state has no legal
`request_repair` transition, so presenting maintainer actions there would
offer an incomplete and misleading choice.

After the repaired material is complete, structurally valid, and bound to the
current contribution and policy snapshot, the contribution-side workflow
calls existing `GovernanceService.prepare_case()` as
`contributor-agent / contributor_agent`. The method revalidates evidence and
uses existing `submit_for_verification`:

```text
repair_requested
  → resubmit
resubmitted
  → prepare_case()
  → submit_for_verification
awaiting_maintainer_verification
```

Existing transition and audit records preserve actor, role, source and target
state, contribution and policy bindings, timestamp, and related provenance.
No transition or precondition is added.

A raw `resubmitted` interactive page has no judgment cards or draft banner. It
states that responsibility remains with the contribution side while AGM
revalidates and submits the material for maintainer review.

## Three contextual outcomes

Only `awaiting_maintainer_verification` compiles enabled item actions:

- **确认材料充分** maps to existing `verify_evidence`. If all blockers are
  resolved, existing `mark_ready` moves the case to
  `ready_for_human_decision`; it does not accept or close the contribution.
- **要求补充或修正** maps to existing scoped `request_repair`, routes
  responsibility to the contribution side, and preserves unaffected evidence.
- **标记重大风险** uses the same existing blocking repair mechanism but keeps
  the selected business outcome and mandatory reason in the bound draft and
  append-only submission audit. It blocks final decision and never calls
  final rejection.

The two repair outcomes may share a transition because the canonical state
machine models both as blocking scoped repair. Their business difference is
preserved by selected option, reason, preview consequence, routing metadata,
and audit rather than by inventing a new state.

## Draft and participant language

The draft banner appears only for actionable work or a saved unsubmitted
draft:

- no selection: **尚未选择处理结果**;
- selected: **你的选择尚未提交**;
- previewed: **预览完成，尚未正式提交**;
- stale: **贡献或规则已经变化，之前的选择已失效**;
- submitted or no task: no draft banner.

The separate Final Decision page now describes completed materials, version
confirmation, maintainer checks, blocking issues, contribution changes,
risks, and business consequences in ordinary project language. Actor,
operation, transition, obligation, fingerprint, compiler, and token details
remain in **治理过程与技术详情**, collapsed by default. Review, final decision,
acceptance, and closure remain separate.

## LF artifacts and tracked ZIP

`.gitattributes` fixes interactive JSON, HTML, output manifests, and the
expected-hash manifest to LF. Raw-byte hash checks perform no EOL
normalization.

`scripts/package_tracked_repository.py` uses `git archive`, so delivery bytes
come from Git blobs rather than a Windows checkout. The ZIP contains exactly
tracked files and excludes `.git`, `.agm-work`, virtual environments, caches,
runtime tokens, screenshots, and untracked files.

`scripts/verify_tracked_repository_package.py` verifies a fresh extraction:

1. compare its member list with the Git tracked-file list;
2. run all three hash checks before generation;
3. regenerate Reviewer Guidance, Review Briefing, and interactive outputs;
4. rerun all three checks; and
5. confirm every tracked byte is unchanged.

Windows and Ubuntu CI execute these checks independently.

## Known limitation

The local loopback service binds an asserted actor and enforces canonical
role, permission, stage, provenance, and separation-of-duty rules. It cannot
prove the real-world identity behind that local assertion without an external
identity provider.
