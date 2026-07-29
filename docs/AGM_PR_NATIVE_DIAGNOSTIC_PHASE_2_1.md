# AGM Phase 2.1: PR-native diagnostic projection

Phase 2.1 projects an already compiled contribution case into **PR 审查诊断**.

Phase 2.1 was an architecture scaffold. Phase 2.1.1 adds legal lifecycle fixtures, precise material-state projection, responsibility/gate/operation-derived routes, and sidecar end-to-end fixtures.
It is not a set of presenter-created cues: each risk location, expected
requirement, material gap, route, and action boundary is derived from matched
risk rules, compiled obligations, bound materials, confirmations, and the
current lifecycle record. The full internal record remains available only in
the collapsed technical section.

The main screen is deliberately about a concrete contribution: changed paths
and recorded line ranges, a viewable diff where supplied, test materials,
Agent activity records, and human confirmations. A missing diff is reported as
unavailable; the presenter never invents a hunk or a test result.

The three human facts are separate: contributor inspection of the current
commit, maintainer checking, and an authorized final AGM recommendation. An
unobserved Agent is not evidence of purely human authorship. Agent use alone
does not create testing or confirmation requirements; requirements remain the
ones compiled by the project policy.

The local workbench is not a hosting-platform adapter. Its actions record AGM
operations only. They never alter source files, run `git merge`, approve a PR,
merge a PR, post a review, or change GitHub/GitLab state. The final page must
say “记录 AGM 最终审查建议” and separately show platform state as unconnected,
unapproved, and unmerged unless adapter evidence exists.

`artifact_status` remains `pending_human_review`. Phase 3 has not started.

Phase 2.1.2 replaces presentation-context self-certification with verified sidecar and canonical-case sources.
