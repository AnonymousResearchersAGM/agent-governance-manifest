# AGM Maintainer Guide

Status: Reviewer Guidance Layer, `v0.2-dev`, pending independent human review

## Open the guidance view

Generate the JSON, Markdown, and HTML report:

```bash
python -m agm.vnext.cli maintainer inspect \
  --case CASE \
  --actor human-maintainer \
  --role maintainer
```

Serve the loopback-only panel:

```bash
python -m agm.vnext.cli maintainer inspect \
  --case CASE \
  --actor human-maintainer \
  --role maintainer \
  --serve
```

The existing command remains the default entry point. Output files are:

```text
.agm-work/cases/CASE/guidance.json
.agm-work/cases/CASE/report.md
.agm-work/cases/CASE/report.html
```

Use the two page links:

- 简明审核视图 for routine work;
- 技术详情视图 for raw records, IDs, fingerprints, and policy text.

## Read the top summary

Confirm:

- the case and changed files are the intended contribution;
- all risk areas are present, not only the highest risk headline;
- the autonomy profile matches the declared working arrangement;
- the current stage is plausible;
- blocking and warning counts agree with the comparison rows; and
- the current responsible party is the role expected by project policy.

`轻量审核` reduces required process. It does not let an agent act as a human
maintainer.

## Follow the five-step navigator

The interface maps the internal eight-stage lifecycle to:

1. 系统识别要求;
2. 贡献者准备材料;
3. 负责人确认;
4. 维护者检查; and
5. 人类维护者最终决定.

`↺ 返回修改` is a loop, not a terminal failure. Inspect the repair request,
affected obligations, latest attempt, retained evidence, and required
revalidation scope before deciding what to check again.

## Use the requirement comparison

Treat the four columns like a reference-versus-observed report:

- 检查项: what is being checked;
- 项目要求: compiled canonical requirement;
- 当前情况: actual bound records;
- 结果: a presentation state, with raw English status retained.

Expand 查看原始依据 to see source rules, obligation ID, interaction IDs,
evidence IDs, binding fingerprints, findings, and English text.

Important distinctions:

- `missing`: required now but absent;
- `not_started`: the lifecycle has not reached the item;
- `needs_update`: evidence exists but is stale or expired;
- `invalid`: evidence or attestation cannot be used;
- `blocked`: an open blocking finding or policy conflict prevents progress;
- `needs_attention`: warning only;
- `verified`: maintainer-side checking is recorded, not acceptance;
- `overridden`: an authorized exception is recorded, not acceptance.

## Inspect multi-risk contributions

For changes such as:

```text
demo_app/auth.py
demo_app/config.py
```

verify that the view includes both authentication and configuration rules, the
union of their obligations, the `authentication-configuration` interaction,
the independent-review requirement, and every missing item.

Do not rely only on the overall `critical` headline.

## Inspect material change

For a resubmission, inspect:

- declared classification: unrelated, non-material, or material;
- materiality reason;
- affected obligation IDs and file/symbol scope;
- previous and new contribution fingerprints;
- stale evidence;
- retained evidence;
- invalidated/retained attestations; and
- revalidation scope.

Challenge an unsupported classification. The prototype records and applies a
scope; it does not prove that the declaration is semantically correct.

## Inspect delegation

Expand “怎样判断是否发生了智能体委派？”.

Subagent file changes, command execution, autonomous adopted output, and
independent tool/action permissions normally count as delegation. Read/search
tools and advisory-only model calls normally do not.

The view points to the autonomy profile and `O-AGENT-SCOPE` record. Verify that
the evidence describes actual action, permissions, supervision, and
delegation.

## Preview, then confirm

Every state-changing panel operation first displays:

- action and actor role;
- source and predicted target state;
- affected obligations;
- records expected to change;
- retained evidence;
- attestation invalidation;
- next actor role; and
- traceable permission/transition rules.

The preview is read-only. Confirm only after checking the scope. If the case
changes before confirmation, the panel rejects the stale preview.

Available operations are choices, not recommendations. Unavailable operations
remain visible with a reason. Frontend state never bypasses backend authority.

## Authority reminders

- Contributor agents cannot attest, verify, override, or decide.
- `accountable_human` confirmation is not maintainer verification.
- `maintainer_verifier` checking is not final acceptance.
- Independent review may require the `maintainer` role and separation of duty.
- Override and final decision are separate events.
- Automated tests passing is evidence, not human acceptance.
- Only an authorized human maintainer records accept, reject, request changes,
  or close.

The local prototype does not cryptographically verify that a typed actor name
is a human. Use repository/platform identity controls where that guarantee is
required.

## Reproduce the demonstrations

```bash
python scripts/generate_reviewer_guidance_demos.py
python -m pytest -q tests/test_vnext_reviewer_guidance.py
python -m pytest -q tests/test_vnext_guidance_e2e.py
```

Generated examples live in `examples/reviewer_guidance/outputs/`. They are
development demonstrations, not human review or formal experimental results.
