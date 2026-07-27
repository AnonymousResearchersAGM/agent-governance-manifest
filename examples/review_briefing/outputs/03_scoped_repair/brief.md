# AGM Maintainer Review Brief

## 补充智能体行动与委派说明

## 当前状态与下一步

### 现在需要你检查 1 项

形式化检查已经完成到当前阶段；下面只列出系统不能替代人类作出的判断。

当前责任方：维护者侧检查人员

- 检查：智能体行动与委派说明

> 检查完成不等于贡献已被接受；最终决定仍由有权人类维护者作出。

## 现在需要你判断的事项（1 项）

### 1. 智能体行动与委派说明

为什么需要人：系统能确认材料结构、范围和版本绑定，但不能自动判断声明是否准确描述代码行为和风险。

贡献者说明：编码智能体仅处理本次文档贡献并运行既有检查；没有继续委派，补充说明覆盖当前版本。

系统观察：治理案例记录为智能体参与路径，并存在相应行动范围材料。

材料摘要：系统记录有 1 份形式有效且对应当前版本的材料。

请重点检查：

- 声明范围是否覆盖实际变更和命令记录
- 是否存在未披露的子智能体行动或继续委派
- 负责人审阅范围是否覆盖当前版本和智能体行动说明

可能的处理结果：

- 说明与修改一致，可以记录本项检查完成
- 需要贡献侧补充或更正说明
- 发现不可接受风险，交由有权人类维护者处理

## 本次修改与风险

贡献者说明：贡献者补充了智能体行动与委派说明；本次补充未修改代码、测试结果或安全影响说明。

系统根据文件和声明归纳：

更新项目文档：docs/guide.md

影响范围：

- 文档与说明

综合风险：低

- docs/guide.md 触发了“文档与说明”风险范围。

- 未记录风险联动

> 归纳边界：系统归纳只依据文件路径、已匹配风险区域和明确声明，不代表系统已经证明代码的真实语义或行为。

## 项目要求与自动检查摘要

项目要求 3 项材料或确认。
- 1 项需要维护者判断
- 2 项已完成当前阶段的形式核对或人工检查

自动检查：
- 6 项完成形式或版本核对
- 0 项发现问题
- 1 项需要人工判断
- 0 项异常已由系统处理

<details>
<summary>查看全部项目要求</summary>

- ! 智能体行动与委派说明 — 材料齐备，内容待人工检查（材料已提供；形式要求已满足；已对应当前版本；内容待人工检查）
  - 材料已提供，形式要求有效且对应当前版本；内容是否与实际修改一致仍需维护者判断。
- ✓ 变更文件清单 — 材料与版本已核对（材料已提供；形式要求已满足；已对应当前版本；材料与版本已核对）
  - 材料已提供，形式要求有效且对应当前版本；这只表示系统完成了可自动执行的核对，不表示内容正确。
- ✓ 修改说明 — 材料与版本已核对（材料已提供；形式要求已满足；已对应当前版本；材料与版本已核对）
  - 材料已提供，形式要求有效且对应当前版本；这只表示系统完成了可自动执行的核对，不表示内容正确。

</details>

<details>
<summary>查看自动检查详情</summary>

- ✓ 材料与当前修改版本一致：所有已提供材料都绑定当前版本，或已记录为受影响范围外的保留材料。
  - 类别：项目规则要求；责任：系统已处理
- – 测试是否包含命令和结果：当前风险路径没有额外要求测试命令记录。
  - 类别：附加信息；责任：系统已处理
- – 测试材料是否对应当前版本：当前没有需要核对版本绑定的测试材料。
  - 类别：系统完整性核对；责任：系统已处理
- ✓ 材料是否仍在有效期内：现有材料记录没有过期状态。
  - 类别：项目规则要求；责任：系统已处理
- – 负责人确认是否绑定当前版本：当前风险路径不要求额外负责人确认。
  - 类别：附加信息；责任：系统已处理
- ✓ 声明范围与实际变更文件一致：材料中的变更文件清单与治理案例记录的实际范围一致。
  - 类别：项目规则要求；责任：系统已处理
- i 是否记录了智能体参与：治理案例明确记录为智能体参与路径。
  - 类别：项目规则要求；责任：系统已处理
  - 结论边界：AGM 只呈现治理记录和声明，不是智能体使用检测器。
- ✓ 是否记录继续委派：行动与委派声明材料已提供，并通过形式与版本核对。
  - 类别：项目规则要求；责任：系统已处理
  - 结论边界：声明不是系统观察到的完整智能体行动日志。
- ✓ 是否存在越权操作：当前案例审计记录中没有被拒绝的越权操作。
  - 类别：系统完整性核对；责任：系统已处理
  - 结论边界：结论范围仅限 AGM 已记录的操作。
- ✓ 结构性项目要求是否满足：当前材料的结构、必填范围和前置确认已达到进入人类判断的条件。
  - 类别：项目规则要求；责任：系统已处理
  - 结论边界：结构满足不等于语义正确，也不等于贡献已被项目接受。
- ! 声明内容是否与实际修改一致：系统已完成结构和绑定检查，但以下内容仍需人类语义判断：智能体行动与委派说明。
  - 类别：项目规则要求；责任：维护者判断
  - 结论边界：系统不会把文件路径推断、贡献者声明或智能体自述当作代码语义证明。

</details>

<details>
<summary>查看智能体与负责人材料</summary>

系统观察：

- 系统记录到智能体身份提交了 3 份治理材料。

贡献侧声明：

- 智能体或贡献者声明：编码智能体仅处理本次文档贡献并运行既有检查；没有继续委派，补充说明覆盖当前版本。

负责人确认：

- 当前风险路径不要求额外确认

边界：

- 能力范围来自治理配置或贡献者声明，不证明每项能力实际被使用。
- AGM 不把智能体自述当作系统观察事实，也不检测未披露的智能体使用。

</details>

<details>
<summary>治理过程与技术详情</summary>

以下内容用于追溯完整 workflow、内部状态、规则、义务、finding、transition、ID、trace 和 fingerprint。

```json
{
  "case_id": "scoped-repair",
  "raw_state": "awaiting_maintainer_verification",
  "raw_readiness": "repair_required",
  "contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
  "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
  "policy_snapshot": {
    "id": "policy-d4b430c206225c9f96fd01ce0f6199ec",
    "schema_version": "agm.policy_snapshot/v0.2-dev",
    "manifest_version": "agm.manifest/v0.2-dev",
    "base_commit": "demo-base",
    "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
    "resolved_at": "2026-07-26T00:00:00Z",
    "source_paths": [
      ".agm/manifest.yml",
      ".agm/agents/entrypoints.yml",
      ".agm/profiles/assurance_profiles.yml",
      ".agm/profiles/autonomy_profiles.yml",
      ".agm/interfaces/contributor_panel.yml",
      ".agm/policies/evidence_profiles.yml",
      ".agm/interfaces/governance_report.yml",
      ".agm/policies/interaction_rules.yml",
      ".agm/interfaces/maintainer_panel.yml",
      ".agm/interfaces/messages.yml",
      ".agm/roles/permissions.yml",
      ".agm/policies/risk_rules.yml",
      ".agm/roles/roles.yml",
      ".agm/workflows/state_machine.yml"
    ]
  },
  "matched_rules": [
    {
      "id": "match-documentation-low",
      "rule_id": "documentation-low",
      "zone": "documentation",
      "risk_level": "low",
      "affected_paths": [
        "docs/guide.md"
      ],
      "selector_reasons": [
        "path selectors matched: docs/guide.md"
      ],
      "obligation_ids": [
        "O-SUMMARY",
        "O-CHANGED-FILES"
      ],
      "case_required": false,
      "source": "risk_rule",
      "obligation_overrides": {}
    }
  ],
  "compiled_obligations": [
    {
      "id": "obl-o-agent-scope",
      "obligation_id": "O-AGENT-SCOPE",
      "source_rule_ids": [
        "autonomy:supervised_agent"
      ],
      "type": "evidence",
      "severity": "medium",
      "blocking": true,
      "verifier_roles": [
        "maintainer",
        "maintainer_verifier"
      ],
      "evidence_type": "agent_action_scope",
      "description": "Record the declared action, permissions, supervision, and delegation scope.",
      "affected_scope": [],
      "status": "satisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-changed-files",
      "obligation_id": "O-CHANGED-FILES",
      "source_rule_ids": [
        "documentation-low"
      ],
      "type": "evidence",
      "severity": "low",
      "blocking": true,
      "verifier_roles": [
        "maintainer",
        "maintainer_verifier"
      ],
      "evidence_type": "changed_files",
      "description": "Identify the files and scopes covered by the contribution.",
      "affected_scope": [
        "docs/guide.md"
      ],
      "status": "satisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-summary",
      "obligation_id": "O-SUMMARY",
      "source_rule_ids": [
        "documentation-low"
      ],
      "type": "evidence",
      "severity": "low",
      "blocking": true,
      "verifier_roles": [
        "maintainer",
        "maintainer_verifier"
      ],
      "evidence_type": "contribution_summary",
      "description": "Provide a concise factual contribution summary.",
      "affected_scope": [
        "docs/guide.md"
      ],
      "status": "satisfied",
      "interaction_ids": []
    }
  ],
  "evidence_records": [
    {
      "id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
      "obligation_ids": [
        "O-AGENT-SCOPE"
      ],
      "affected_scope": [
        "docs/guide.md"
      ],
      "contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "evidence_type": "agent_action_scope",
      "value": "编码智能体仅处理本次文档贡献并运行既有检查；没有继续委派，补充说明覆盖当前版本。",
      "command": null,
      "environment": null,
      "artifact_path": null,
      "artifact_hash": null,
      "observed_at": "2026-07-26T00:05:00Z",
      "expires_at": null,
      "source_actor": "contributor-agent",
      "source_tool": "scenario-generator",
      "retained_for_contribution_fingerprint": null,
      "retention_reason": null,
      "rejected_at": null,
      "rejected_by": null,
      "rejection_reason": null,
      "validity_state": "valid",
      "invalid_reasons": []
    },
    {
      "id": "evidence-0a51a227c9c15692a99d7e527b174492",
      "obligation_ids": [
        "O-CHANGED-FILES"
      ],
      "affected_scope": [
        "docs/guide.md"
      ],
      "contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "evidence_type": "changed_files",
      "value": [
        "docs/guide.md"
      ],
      "command": null,
      "environment": null,
      "artifact_path": null,
      "artifact_hash": null,
      "observed_at": "2026-07-26T00:05:00Z",
      "expires_at": null,
      "source_actor": "contributor-agent",
      "source_tool": "scenario-generator",
      "retained_for_contribution_fingerprint": null,
      "retention_reason": null,
      "rejected_at": null,
      "rejected_by": null,
      "rejection_reason": null,
      "validity_state": "valid",
      "invalid_reasons": []
    },
    {
      "id": "evidence-5c1362d33d7653c7ab21254f127c4317",
      "obligation_ids": [
        "O-SUMMARY"
      ],
      "affected_scope": [
        "docs/guide.md"
      ],
      "contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "evidence_type": "contribution_summary",
      "value": "贡献者补充了智能体行动与委派说明；本次补充未修改代码、测试结果或安全影响说明。",
      "command": null,
      "environment": null,
      "artifact_path": null,
      "artifact_hash": null,
      "observed_at": "2026-07-26T00:05:00Z",
      "expires_at": null,
      "source_actor": "contributor-agent",
      "source_tool": "scenario-generator",
      "retained_for_contribution_fingerprint": null,
      "retention_reason": null,
      "rejected_at": null,
      "rejected_by": null,
      "rejection_reason": null,
      "validity_state": "valid",
      "invalid_reasons": []
    }
  ],
  "attestation_records": [],
  "findings": [
    {
      "id": "finding-8c9865b11f9455de8729c497a127546b",
      "code": "agent_delegation_clarification",
      "severity": "high",
      "message": "Clarify agent action and delegation scope only.",
      "blocking": true,
      "related_object_ids": [],
      "affected_obligation_ids": [
        "O-AGENT-SCOPE"
      ],
      "status": "open",
      "created_at": "2026-07-26T00:00:00Z",
      "resolved_at": null,
      "resolution": null
    }
  ],
  "repair_requests": [
    {
      "id": "repair-36a01320d26c57d4a38a7c937e522e18",
      "finding_ids": [
        "finding-8c9865b11f9455de8729c497a127546b"
      ],
      "responsible_role": "contributor",
      "affected_obligation_ids": [
        "O-AGENT-SCOPE"
      ],
      "requested_correction": "Clarify agent action and delegation scope only.",
      "revalidation_required": [
        "O-AGENT-SCOPE"
      ],
      "requested_by": "verifier-1",
      "requested_at": "2026-07-26T00:00:00Z",
      "status": "resubmitted",
      "attempts": [
        {
          "id": "attempt-612807c028a75b3782f750a111c86bb9",
          "actor": "contributor-agent",
          "timestamp": "2026-07-26T00:00:00Z",
          "summary": "Clarified delegation wording without changing the contribution.",
          "affected_obligation_ids": [
            "O-AGENT-SCOPE"
          ],
          "evidence_ids": [],
          "change_assessment": {
            "change_classification": "no_material_change",
            "change_reason": "Wording clarification does not change contribution behavior.",
            "previous_contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
            "new_contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
            "stale_evidence_ids": [],
            "retained_evidence_ids": [
              "evidence-0a51a227c9c15692a99d7e527b174492",
              "evidence-5c1362d33d7653c7ab21254f127c4317"
            ],
            "invalidated_attestation_ids": [],
            "required_revalidation_scope": [
              "O-AGENT-SCOPE"
            ]
          },
          "change_classification": "no_material_change",
          "change_reason": "Wording clarification does not change contribution behavior.",
          "previous_contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
          "new_contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
          "stale_evidence_ids": [],
          "retained_evidence_ids": [
            "evidence-0a51a227c9c15692a99d7e527b174492",
            "evidence-5c1362d33d7653c7ab21254f127c4317"
          ],
          "invalidated_attestation_ids": [],
          "required_revalidation_scope": [
            "O-AGENT-SCOPE"
          ]
        }
      ]
    }
  ],
  "attempted_operations": [],
  "verification_records": [
    {
      "id": "verification-5b2e4e7a1c325583912ee759c2b334cf",
      "actor": "verifier-1",
      "role": "maintainer_verifier",
      "timestamp": "2026-07-26T00:00:00Z",
      "obligation_ids": [
        "O-AGENT-SCOPE",
        "O-CHANGED-FILES",
        "O-SUMMARY"
      ],
      "evidence_ids": [
        "evidence-0a51a227c9c15692a99d7e527b174492",
        "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
        "evidence-5c1362d33d7653c7ab21254f127c4317"
      ],
      "outcome": "verified",
      "reason": "Initial evidence checked.",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0"
    }
  ],
  "transition_history": [
    {
      "id": "transition-1881127c74f85c64a27983540b53aa8f",
      "case_id": "scoped-repair",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "case_opened",
      "target_state": "policy_resolved",
      "action": "resolve_policy",
      "reason": "Resolved canonical policy against the contribution.",
      "related_object_ids": [
        "policy-d4b430c206225c9f96fd01ce0f6199ec"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-177148c790b35961986ce8d6da0ef25d",
      "case_id": "scoped-repair",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "policy_resolved",
      "target_state": "obligations_compiled",
      "action": "compile_obligations",
      "reason": "Compiled the union of matched, profile, and interaction obligations.",
      "related_object_ids": [
        "obl-o-agent-scope",
        "obl-o-changed-files",
        "obl-o-summary"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-f3df06251a0c57f58f302d45ebf1f8c7",
      "case_id": "scoped-repair",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "obligations_compiled",
      "target_state": "evidence_incomplete",
      "action": "mark_evidence_state",
      "reason": "The new case has unsatisfied evidence obligations.",
      "related_object_ids": [
        "obl-o-agent-scope",
        "obl-o-changed-files",
        "obl-o-summary"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-6512e18aa3935087bbedb4777db22138",
      "case_id": "scoped-repair",
      "actor": "contributor-agent",
      "role": "contributor_agent",
      "source_state": "evidence_incomplete",
      "target_state": "awaiting_maintainer_verification",
      "action": "submit_for_verification",
      "reason": "Contributor submitted prepared evidence for maintainer verification.",
      "related_object_ids": [
        "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
        "evidence-0a51a227c9c15692a99d7e527b174492",
        "evidence-5c1362d33d7653c7ab21254f127c4317"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-e5af5ef503e7581eb3deaad43fb1baef",
      "case_id": "scoped-repair",
      "actor": "verifier-1",
      "role": "maintainer_verifier",
      "source_state": "awaiting_maintainer_verification",
      "target_state": "verification_complete",
      "action": "verify_evidence",
      "reason": "Initial evidence checked.",
      "related_object_ids": [
        "verification-5b2e4e7a1c325583912ee759c2b334cf"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-ea7b63934d9e50ddbf6208b6ee05da15",
      "case_id": "scoped-repair",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "verification_complete",
      "target_state": "ready_for_human_decision",
      "action": "mark_ready",
      "reason": "All blocking obligations are satisfied or verified; the case is ready for an authorized human decision, not accepted.",
      "related_object_ids": [
        "verification-5b2e4e7a1c325583912ee759c2b334cf"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-73f7594267755464b038a86d9eea8add",
      "case_id": "scoped-repair",
      "actor": "verifier-1",
      "role": "maintainer_verifier",
      "source_state": "ready_for_human_decision",
      "target_state": "repair_requested",
      "action": "request_repair",
      "reason": "Clarify agent action and delegation scope only.",
      "related_object_ids": [
        "finding-8c9865b11f9455de8729c497a127546b",
        "repair-36a01320d26c57d4a38a7c937e522e18"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-d852903b5565559abc3107e7e125f43a",
      "case_id": "scoped-repair",
      "actor": "contributor-agent",
      "role": "contributor_agent",
      "source_state": "repair_requested",
      "target_state": "resubmitted",
      "action": "resubmit",
      "reason": "Clarified delegation wording without changing the contribution.",
      "related_object_ids": [
        "attempt-612807c028a75b3782f750a111c86bb9"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-b2cf970564f25e54b8876e1685661bd3",
      "case_id": "scoped-repair",
      "actor": "contributor-agent",
      "role": "contributor_agent",
      "source_state": "resubmitted",
      "target_state": "awaiting_maintainer_verification",
      "action": "submit_for_verification",
      "reason": "Contributor submitted prepared evidence for maintainer verification.",
      "related_object_ids": [
        "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
        "evidence-0a51a227c9c15692a99d7e527b174492",
        "evidence-5c1362d33d7653c7ab21254f127c4317"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    }
  ],
  "final_decision": null,
  "closure_receipt": null,
  "policy_migration_diagnostic": {
    "case_id": "scoped-repair",
    "policy_changed": false,
    "original_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
    "current_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
    "still_valid_obligations": [
      "O-AGENT-SCOPE",
      "O-CHANGED-FILES",
      "O-SUMMARY"
    ],
    "changed_obligations": [],
    "added_obligations": [],
    "removed_obligations": [],
    "evidence_requiring_revalidation": [],
    "attestations_invalidated_if_migrated": [],
    "may_remain_on_original_snapshot": true,
    "must_migrate": false,
    "reason": "The canonical policy fingerprint is unchanged."
  },
  "reviewer_guidance": {
    "schema_version": "agm.reviewer_guidance/v0.2-dev",
    "generated_from_case_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
    "actor": {
      "actor": "human-maintainer",
      "role": "maintainer",
      "human": true
    },
    "summary": {
      "case_id": "scoped-repair",
      "changed_files": [
        "docs/guide.md"
      ],
      "risk_level": "low",
      "risk_areas": [
        "文档（documentation）"
      ],
      "autonomy_profile": "supervised_agent",
      "path_kind": "lightweight",
      "path_label": "轻量审核",
      "current_stage": "等待维护者重新检查指定范围",
      "blocking_issue_count": 1,
      "warning_count": 0,
      "current_responsible_parties": [
        "维护者侧检查人员",
        "项目规则负责人",
        "人类维护者"
      ],
      "next_authorized_actor_roles": [
        "maintainer_verifier",
        "policy_steward",
        "maintainer"
      ],
      "raw_state": "awaiting_maintainer_verification",
      "raw_readiness": "repair_required"
    },
    "workflow_steps": [
      {
        "number": 1,
        "step_id": "identify_requirements",
        "title": "系统识别要求",
        "status": "completed",
        "status_label": "已完成",
        "symbol": "✓",
        "explanation": "适用规则和本次要求已由 AGM 引擎生成。",
        "internal_stages": [
          "Resolve",
          "Compile"
        ],
        "traceability": [
          {
            "kind": "state_transition",
            "object_id": "transition-1881127c74f85c64a27983540b53aa8f",
            "relationship": "primary:resolve_policy"
          },
          {
            "kind": "state_transition",
            "object_id": "transition-177148c790b35961986ce8d6da0ef25d",
            "relationship": "primary:compile_obligations"
          },
          {
            "kind": "matched_rule",
            "object_id": "match-documentation-low",
            "relationship": "risk_matching"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-agent-scope",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-changed-files",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-summary",
            "relationship": "obligation_compilation"
          }
        ]
      },
      {
        "number": 2,
        "step_id": "prepare_materials",
        "title": "贡献者准备材料",
        "status": "completed",
        "status_label": "已完成",
        "symbol": "✓",
        "explanation": "本次所需材料已提交到后续流程。",
        "internal_stages": [
          "Bind",
          "Repair"
        ],
        "traceability": [
          {
            "kind": "state_transition",
            "object_id": "transition-f3df06251a0c57f58f302d45ebf1f8c7",
            "relationship": "primary:mark_evidence_state"
          },
          {
            "kind": "state_transition",
            "object_id": "transition-d852903b5565559abc3107e7e125f43a",
            "relationship": "primary:resubmit"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
            "relationship": "binding_or_retention"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
            "relationship": "binding_or_retention"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
            "relationship": "binding_or_retention"
          },
          {
            "kind": "repair_request",
            "object_id": "repair-36a01320d26c57d4a38a7c937e522e18",
            "relationship": "repair_scope"
          }
        ]
      },
      {
        "number": 3,
        "step_id": "accountable_confirmation",
        "title": "负责人确认",
        "status": "skipped",
        "status_label": "本次不要求",
        "symbol": "—",
        "explanation": "当前义务集合不要求负责人确认。",
        "internal_stages": [
          "Attest"
        ],
        "traceability": []
      },
      {
        "number": 4,
        "step_id": "maintainer_check",
        "title": "维护者检查",
        "status": "current",
        "status_label": "当前阶段",
        "symbol": "●",
        "explanation": "当前轮到有权限的维护者检查材料与绑定。",
        "internal_stages": [
          "Verify",
          "Repair"
        ],
        "traceability": [
          {
            "kind": "state_transition",
            "object_id": "transition-6512e18aa3935087bbedb4777db22138",
            "relationship": "primary:submit_for_verification"
          },
          {
            "kind": "state_transition",
            "object_id": "transition-e5af5ef503e7581eb3deaad43fb1baef",
            "relationship": "primary:verify_evidence"
          },
          {
            "kind": "state_transition",
            "object_id": "transition-73f7594267755464b038a86d9eea8add",
            "relationship": "primary:request_repair"
          },
          {
            "kind": "state_transition",
            "object_id": "transition-b2cf970564f25e54b8876e1685661bd3",
            "relationship": "primary:submit_for_verification"
          },
          {
            "kind": "maintainer_verification",
            "object_id": "verification-5b2e4e7a1c325583912ee759c2b334cf",
            "relationship": "verified"
          },
          {
            "kind": "finding",
            "object_id": "finding-8c9865b11f9455de8729c497a127546b",
            "relationship": "open"
          }
        ]
      },
      {
        "number": 5,
        "step_id": "human_final_decision",
        "title": "人类维护者最终决定",
        "status": "pending",
        "status_label": "尚未开始",
        "symbol": "○",
        "explanation": "前序治理要求完成后才进入最终决定。",
        "internal_stages": [
          "Decide",
          "Record"
        ],
        "traceability": [
          {
            "kind": "state_transition",
            "object_id": "transition-ea7b63934d9e50ddbf6208b6ee05da15",
            "relationship": "primary:mark_ready"
          }
        ]
      }
    ],
    "requirement_comparisons": [
      {
        "obligation_id": "O-AGENT-SCOPE",
        "check_item": "智能体行动与委派说明",
        "project_requirement": "说明智能体做了什么、用了哪些权限、是否有人监督，以及是否把具有独立行动能力的工作继续交给了另一个智能体。",
        "current_situation": "材料已补充或仍然有效；当前等待维护者重新检查这一项。",
        "result": "blocked",
        "result_label": "阻止继续",
        "raw_status": "satisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "autonomy:supervised_agent"
        ],
        "interaction_ids": [],
        "evidence_ids": [
          "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1"
        ],
        "binding_fingerprints": [
          "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0"
        ],
        "finding_ids": [
          "finding-8c9865b11f9455de8729c497a127546b"
        ],
        "reference_english": "Record the declared action, permissions, supervision, and delegation scope.",
        "observed_english": "valid material present; open repair awaits revalidation",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-agent-scope",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "autonomy:supervised_agent",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
            "relationship": "observed"
          },
          {
            "kind": "finding",
            "object_id": "finding-8c9865b11f9455de8729c497a127546b",
            "relationship": "diagnostic"
          }
        ],
        "display_name": "智能体行动与委派说明",
        "reference_plain": "说明智能体做了什么、用了哪些权限、是否有人监督，以及是否把具有独立行动能力的工作继续交给了另一个智能体。",
        "observed_plain": "材料已补充或仍然有效；当前等待维护者重新检查这一项。",
        "observed_raw": "valid material present; open repair awaits revalidation",
        "material_status": "provided",
        "material_status_label": "已提供",
        "workflow_status": "awaiting_revalidation",
        "workflow_status_label": "等待维护者重新检查",
        "currently_blocks_progression": true,
        "affected_scope": []
      },
      {
        "obligation_id": "O-CHANGED-FILES",
        "check_item": "变更文件清单",
        "project_requirement": "列出这次修改涉及的文件和范围。",
        "current_situation": "已提供与当前贡献和项目规则绑定的材料。",
        "result": "meets_requirement",
        "result_label": "符合要求",
        "raw_status": "satisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "documentation-low"
        ],
        "interaction_ids": [],
        "evidence_ids": [
          "evidence-0a51a227c9c15692a99d7e527b174492"
        ],
        "binding_fingerprints": [
          "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0"
        ],
        "finding_ids": [],
        "reference_english": "Identify the files and scopes covered by the contribution.",
        "observed_english": "valid bound evidence is present",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-changed-files",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "documentation-low",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
            "relationship": "observed"
          }
        ],
        "display_name": "变更文件清单",
        "reference_plain": "列出这次修改涉及的文件和范围。",
        "observed_plain": "已提供与当前贡献和项目规则绑定的材料。",
        "observed_raw": "valid bound evidence is present",
        "material_status": "provided",
        "material_status_label": "已提供",
        "workflow_status": "completed",
        "workflow_status_label": "已完成",
        "currently_blocks_progression": false,
        "affected_scope": [
          "docs/guide.md"
        ]
      },
      {
        "obligation_id": "O-SUMMARY",
        "check_item": "修改说明",
        "project_requirement": "简要说明这次修改做了什么。",
        "current_situation": "已提供与当前贡献和项目规则绑定的材料。",
        "result": "meets_requirement",
        "result_label": "符合要求",
        "raw_status": "satisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "documentation-low"
        ],
        "interaction_ids": [],
        "evidence_ids": [
          "evidence-5c1362d33d7653c7ab21254f127c4317"
        ],
        "binding_fingerprints": [
          "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0"
        ],
        "finding_ids": [],
        "reference_english": "Provide a concise factual contribution summary.",
        "observed_english": "valid bound evidence is present",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-summary",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "documentation-low",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
            "relationship": "observed"
          }
        ],
        "display_name": "修改说明",
        "reference_plain": "简要说明这次修改做了什么。",
        "observed_plain": "已提供与当前贡献和项目规则绑定的材料。",
        "observed_raw": "valid bound evidence is present",
        "material_status": "provided",
        "material_status_label": "已提供",
        "workflow_status": "completed",
        "workflow_status_label": "已完成",
        "currently_blocks_progression": false,
        "affected_scope": [
          "docs/guide.md"
        ]
      }
    ],
    "diagnostics": [
      {
        "finding_id": "finding-8c9865b11f9455de8729c497a127546b",
        "title": "阻断问题",
        "plain_language": "只需澄清智能体行动、权限和继续委派的范围。",
        "reason_presentation": {
          "reason_code": "agent_delegation_clarification",
          "display_plain": "只需澄清智能体行动、权限和继续委派的范围。",
          "source_english": "Clarify agent action and delegation scope only.",
          "source_code": "agent_delegation_clarification",
          "trace_refs": [
            {
              "kind": "finding",
              "object_id": "finding-8c9865b11f9455de8729c497a127546b",
              "relationship": "diagnostic"
            },
            {
              "kind": "repair_request",
              "object_id": "repair-36a01320d26c57d4a38a7c937e522e18",
              "relationship": "repair"
            }
          ]
        },
        "severity": "high",
        "blocking": true,
        "status": "open",
        "affected_obligation_ids": [
          "O-AGENT-SCOPE"
        ],
        "repair_request_ids": [
          "repair-36a01320d26c57d4a38a7c937e522e18"
        ],
        "traceability": [
          {
            "kind": "finding",
            "object_id": "finding-8c9865b11f9455de8729c497a127546b",
            "relationship": "diagnostic"
          },
          {
            "kind": "repair_request",
            "object_id": "repair-36a01320d26c57d4a38a7c937e522e18",
            "relationship": "repair"
          }
        ]
      }
    ],
    "available_actions": [
      {
        "action": "view_change_scope",
        "title": "查看变化范围",
        "description": "查看变更文件、风险规则、影响范围和绑定指纹。",
        "consequence": "只读操作，不改变案例状态。",
        "mutates_state": false,
        "actor_role": "maintainer",
        "default_obligation_ids": [],
        "required_parameters": [],
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:view_change_scope",
            "relationship": "authority"
          }
        ],
        "relevance": "secondary",
        "group": "other_available",
        "primary_reason": "后端允许此操作，但它不直接处理当前主要阻断项。",
        "selector_options": []
      },
      {
        "action": "verify_evidence",
        "title": "检查提交材料",
        "description": "记录维护者对指定项目要求及其绑定材料的检查结果。",
        "consequence": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
        "mutates_state": true,
        "actor_role": "maintainer",
        "default_obligation_ids": [
          "O-AGENT-SCOPE"
        ],
        "required_parameters": [
          "reason"
        ],
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:verify_evidence",
            "relationship": "authority"
          },
          {
            "kind": "state_machine_rule",
            "object_id": "awaiting_maintainer_verification:verify_evidence:verification_complete",
            "relationship": "transition"
          }
        ],
        "relevance": "current",
        "group": "current_relevant",
        "primary_reason": "该操作直接对应当前流程阶段或开放问题。",
        "selector_options": [
          {
            "selector_token": "sel-137fe07fbb014f30f02652c6e0c985e18db341759375069b63fcf8dc956f2cc4",
            "action": "verify_evidence",
            "label": "智能体行动与委派说明",
            "status_label": "已提供；等待维护者重新检查",
            "affected_scope": [],
            "obligation_ids": [
              "O-AGENT-SCOPE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-AGENT-SCOPE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "awaiting_revalidation",
            "technical_details": {
              "obligation_id": "O-AGENT-SCOPE",
              "evidence_ids": [
                "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1"
              ],
              "finding_ids": [
                "finding-8c9865b11f9455de8729c497a127546b"
              ]
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-agent-scope",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "autonomy:supervised_agent",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
                "relationship": "observed"
              },
              {
                "kind": "finding",
                "object_id": "finding-8c9865b11f9455de8729c497a127546b",
                "relationship": "diagnostic"
              }
            ]
          }
        ]
      },
      {
        "action": "request_repair",
        "title": "要求补充或修改",
        "description": "指出问题和受影响义务，返回贡献侧修复。",
        "consequence": "仅指定范围需要修复和重新检查，未受影响材料保留。",
        "mutates_state": true,
        "actor_role": "maintainer",
        "default_obligation_ids": [
          "O-AGENT-SCOPE"
        ],
        "required_parameters": [
          "obligation_ids",
          "reason"
        ],
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:request_repair",
            "relationship": "authority"
          },
          {
            "kind": "state_machine_rule",
            "object_id": "awaiting_maintainer_verification:request_repair:repair_requested",
            "relationship": "transition"
          }
        ],
        "relevance": "current",
        "group": "current_relevant",
        "primary_reason": "该操作直接对应当前流程阶段或开放问题。",
        "selector_options": [
          {
            "selector_token": "sel-80a9ed6e44d1378f574c328eaeaf7ba96cd07e4aad5c449608cae2681d73ddb5",
            "action": "request_repair",
            "label": "智能体行动与委派说明",
            "status_label": "已提供；等待维护者重新检查",
            "affected_scope": [],
            "obligation_ids": [
              "O-AGENT-SCOPE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-AGENT-SCOPE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "awaiting_revalidation",
            "technical_details": {
              "obligation_id": "O-AGENT-SCOPE",
              "evidence_ids": [
                "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1"
              ],
              "finding_ids": [
                "finding-8c9865b11f9455de8729c497a127546b"
              ]
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-agent-scope",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "autonomy:supervised_agent",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
                "relationship": "observed"
              },
              {
                "kind": "finding",
                "object_id": "finding-8c9865b11f9455de8729c497a127546b",
                "relationship": "diagnostic"
              }
            ]
          },
          {
            "selector_token": "sel-a0df379baa9cd51709208499e5bc735cdb78f956129ecc689d8f9ebafadcd430",
            "action": "request_repair",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-CHANGED-FILES"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-CHANGED-FILES"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-CHANGED-FILES",
              "evidence_ids": [
                "evidence-0a51a227c9c15692a99d7e527b174492"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-changed-files",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "documentation-low",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-f5497a7a3588ab4f15c015d60f2b1c53839a7ad9f4d009807ee059e2514ab182",
            "action": "request_repair",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-SUMMARY"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-SUMMARY"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-SUMMARY",
              "evidence_ids": [
                "evidence-5c1362d33d7653c7ab21254f127c4317"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-summary",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "documentation-low",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
                "relationship": "observed"
              }
            ]
          }
        ]
      },
      {
        "action": "reject_evidence",
        "title": "拒绝当前材料",
        "description": "拒绝一条不能支持当前修改的具体材料。",
        "consequence": "该材料将标记为已拒绝，并建立指定范围的补充或修改请求。",
        "mutates_state": true,
        "actor_role": "maintainer",
        "default_obligation_ids": [],
        "required_parameters": [
          "object_id",
          "reason"
        ],
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:reject_evidence",
            "relationship": "authority"
          },
          {
            "kind": "state_machine_rule",
            "object_id": "awaiting_maintainer_verification:reject_evidence:repair_requested",
            "relationship": "transition"
          }
        ],
        "relevance": "current",
        "group": "current_relevant",
        "primary_reason": "该操作直接对应当前流程阶段或开放问题。",
        "selector_options": [
          {
            "selector_token": "sel-f5ec08276b893da6c7a097c371ba920091d96d4ffd7706e8e8a21f371fca4183",
            "action": "reject_evidence",
            "label": "智能体行动与委派说明",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-AGENT-SCOPE"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
              "evidence_type": "agent_action_scope"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-a65b60ff9f372d533e72ca54467c1ef6132c344cf1208e96606bd783e18191da",
            "action": "reject_evidence",
            "label": "变更文件清单",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-CHANGED-FILES"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-0a51a227c9c15692a99d7e527b174492"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-0a51a227c9c15692a99d7e527b174492",
              "evidence_type": "changed_files"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-15e0e6c942e977a2f31a241b4ee3d865640d4e5e084878bb3ca47b4d4a3db7eb",
            "action": "reject_evidence",
            "label": "修改说明",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-SUMMARY"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-5c1362d33d7653c7ab21254f127c4317"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
              "evidence_type": "contribution_summary"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
                "relationship": "action_target"
              }
            ]
          }
        ]
      },
      {
        "action": "ask_clarification",
        "title": "请求补充说明",
        "description": "针对指定要求提出可审计的澄清问题。",
        "consequence": "案例返回贡献侧回答，所选范围需要重新检查。",
        "mutates_state": true,
        "actor_role": "maintainer",
        "default_obligation_ids": [
          "O-AGENT-SCOPE"
        ],
        "required_parameters": [
          "obligation_ids",
          "reason"
        ],
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:ask_clarification",
            "relationship": "authority"
          },
          {
            "kind": "state_machine_rule",
            "object_id": "awaiting_maintainer_verification:ask_clarification:repair_requested",
            "relationship": "transition"
          }
        ],
        "relevance": "current",
        "group": "current_relevant",
        "primary_reason": "该操作直接对应当前流程阶段或开放问题。",
        "selector_options": [
          {
            "selector_token": "sel-06aa442dd7376de0976c29253225cf3e2504ae05fbf85cd14c7740fe2e791e03",
            "action": "ask_clarification",
            "label": "智能体行动与委派说明",
            "status_label": "已提供；等待维护者重新检查",
            "affected_scope": [],
            "obligation_ids": [
              "O-AGENT-SCOPE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-AGENT-SCOPE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "awaiting_revalidation",
            "technical_details": {
              "obligation_id": "O-AGENT-SCOPE",
              "evidence_ids": [
                "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1"
              ],
              "finding_ids": [
                "finding-8c9865b11f9455de8729c497a127546b"
              ]
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-agent-scope",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "autonomy:supervised_agent",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
                "relationship": "observed"
              },
              {
                "kind": "finding",
                "object_id": "finding-8c9865b11f9455de8729c497a127546b",
                "relationship": "diagnostic"
              }
            ]
          },
          {
            "selector_token": "sel-e65658a4f5b72be80ac6a9461bfc3afbb6c1c162d5f3b28a74a428e9b121626d",
            "action": "ask_clarification",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-CHANGED-FILES"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-CHANGED-FILES"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-CHANGED-FILES",
              "evidence_ids": [
                "evidence-0a51a227c9c15692a99d7e527b174492"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-changed-files",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "documentation-low",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-b921eaf9964c762866f88b8d0cb3d6f95d549096559394246722e34f2fc026a5",
            "action": "ask_clarification",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-SUMMARY"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-SUMMARY"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-SUMMARY",
              "evidence_ids": [
                "evidence-5c1362d33d7653c7ab21254f127c4317"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-summary",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "documentation-low",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
                "relationship": "observed"
              }
            ]
          }
        ]
      },
      {
        "action": "record_policy_conflict",
        "title": "记录项目规则冲突",
        "description": "记录无法由普通材料修复的策略冲突。",
        "consequence": "案例转入补充处理，由项目规则负责人或维护者处理。",
        "mutates_state": true,
        "actor_role": "maintainer",
        "default_obligation_ids": [
          "O-AGENT-SCOPE"
        ],
        "required_parameters": [
          "obligation_ids",
          "reason"
        ],
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:record_policy_conflict",
            "relationship": "authority"
          },
          {
            "kind": "state_machine_rule",
            "object_id": "awaiting_maintainer_verification:record_policy_conflict:repair_requested",
            "relationship": "transition"
          }
        ],
        "relevance": "secondary",
        "group": "other_available",
        "primary_reason": "后端允许此操作，但它不直接处理当前主要阻断项。",
        "selector_options": [
          {
            "selector_token": "sel-13cc652c952536ab0042e22c9d6232b281083b0cbfb486e3e2b6ec20e9d7b7ec",
            "action": "record_policy_conflict",
            "label": "智能体行动与委派说明",
            "status_label": "已提供；等待维护者重新检查",
            "affected_scope": [],
            "obligation_ids": [
              "O-AGENT-SCOPE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-AGENT-SCOPE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "awaiting_revalidation",
            "technical_details": {
              "obligation_id": "O-AGENT-SCOPE",
              "evidence_ids": [
                "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1"
              ],
              "finding_ids": [
                "finding-8c9865b11f9455de8729c497a127546b"
              ]
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-agent-scope",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "autonomy:supervised_agent",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
                "relationship": "observed"
              },
              {
                "kind": "finding",
                "object_id": "finding-8c9865b11f9455de8729c497a127546b",
                "relationship": "diagnostic"
              }
            ]
          },
          {
            "selector_token": "sel-c92112faea315c07d46a7546b2fd819b64c12fcfabedda4820d3a2adfad73068",
            "action": "record_policy_conflict",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-CHANGED-FILES"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-CHANGED-FILES"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-CHANGED-FILES",
              "evidence_ids": [
                "evidence-0a51a227c9c15692a99d7e527b174492"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-changed-files",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "documentation-low",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-a2ec175bb781dce35c635dfcf64baf5e59300d15cb1d805d99582382ec03c64d",
            "action": "record_policy_conflict",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-SUMMARY"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-SUMMARY"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-SUMMARY",
              "evidence_ids": [
                "evidence-5c1362d33d7653c7ab21254f127c4317"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-summary",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "documentation-low",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
                "relationship": "observed"
              }
            ]
          }
        ]
      }
    ],
    "unavailable_actions": [
      {
        "action": "invalidate_attestation",
        "title": "将旧负责人确认标记为失效",
        "description": "使一条过时或不正确的负责人确认失效。",
        "reason": "当前没有仍然有效的负责人确认可供失效处理。",
        "next_actor_roles": [
          "maintainer",
          "maintainer_verifier"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:invalidate_attestation",
            "relationship": "authority"
          },
          {
            "kind": "state_machine_rule",
            "object_id": "awaiting_maintainer_verification:invalidate_attestation:repair_requested",
            "relationship": "transition"
          }
        ],
        "category": "authority",
        "required_role": [
          "maintainer",
          "maintainer_verifier"
        ],
        "required_state": [
          "awaiting_maintainer_verification",
          "ready_for_human_decision",
          "verification_complete"
        ],
        "future_availability": "到达所需状态且对象范围满足后可能可用。"
      },
      {
        "action": "resolve_policy_conflict",
        "title": "处理项目规则冲突",
        "description": "由有权限的角色记录策略冲突的解决依据。",
        "reason": "当前处于“等待维护者检查”，还不能执行“处理项目规则冲突”。",
        "next_actor_roles": [
          "maintainer_verifier",
          "policy_steward",
          "maintainer"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:resolve_policy_conflict",
            "relationship": "authority"
          }
        ],
        "category": "scope",
        "required_role": [
          "maintainer",
          "policy_steward"
        ],
        "required_state": [
          "repair_requested"
        ],
        "future_availability": "到达所需状态且对象范围满足后可能可用。"
      },
      {
        "action": "resubmit",
        "title": "重新提交修改后的材料",
        "description": "贡献侧提交补充或修改影响范围和新增材料。",
        "reason": "当前角色没有“重新提交修改后的材料”的权限。可以执行这一步的角色：人类贡献者或贡献侧智能体。",
        "next_actor_roles": [
          "contributor",
          "contributor_agent"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:resubmit",
            "relationship": "authority"
          }
        ],
        "category": "permission",
        "required_role": [
          "contributor",
          "contributor_agent"
        ],
        "required_state": [
          "repair_requested"
        ],
        "future_availability": "切换流程阶段不会改变角色权限；需要由列出的有权角色执行。"
      },
      {
        "action": "confirm_attestation",
        "title": "确认负责人声明",
        "description": "由负责人对明确范围作出事实确认。",
        "reason": "当前角色没有“确认负责人声明”的权限。可以执行这一步的角色：负责人。",
        "next_actor_roles": [
          "accountable_human"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:confirm_attestation",
            "relationship": "authority"
          }
        ],
        "category": "permission",
        "required_role": [
          "accountable_human"
        ],
        "required_state": [
          "awaiting_human_attestation",
          "evidence_incomplete"
        ],
        "future_availability": "切换流程阶段不会改变角色权限；需要由列出的有权角色执行。"
      },
      {
        "action": "authorized_override",
        "title": "由有权维护者执行覆盖处理",
        "description": "记录具备权限的维护者对明确项目要求或问题的例外处理。",
        "reason": "当前处于“等待维护者检查”，还不能执行“由有权维护者执行覆盖处理”。",
        "next_actor_roles": [
          "maintainer_verifier",
          "policy_steward",
          "maintainer"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:authorized_override",
            "relationship": "authority"
          }
        ],
        "category": "authority",
        "required_role": [
          "maintainer"
        ],
        "required_state": [
          "ready_for_human_decision",
          "repair_requested",
          "verification_complete"
        ],
        "future_availability": "到达所需状态且对象范围满足后可能可用。"
      },
      {
        "action": "decide_accept",
        "title": "最终接受",
        "description": "由人类维护者记录接受决定。",
        "reason": "当前处于“等待维护者检查”，还不能执行“最终接受”。",
        "next_actor_roles": [
          "maintainer_verifier",
          "policy_steward",
          "maintainer"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:decide_accept",
            "relationship": "authority"
          }
        ],
        "category": "authority",
        "required_role": [
          "maintainer"
        ],
        "required_state": [
          "overridden",
          "ready_for_human_decision"
        ],
        "future_availability": "前序阻断要求完成并进入人类最终决定阶段后可用。"
      },
      {
        "action": "decide_reject",
        "title": "最终拒绝",
        "description": "由人类维护者记录拒绝决定。",
        "reason": "当前处于“等待维护者检查”，还不能执行“最终拒绝”。",
        "next_actor_roles": [
          "maintainer_verifier",
          "policy_steward",
          "maintainer"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:decide_reject",
            "relationship": "authority"
          }
        ],
        "category": "authority",
        "required_role": [
          "maintainer"
        ],
        "required_state": [
          "overridden",
          "ready_for_human_decision",
          "repair_requested"
        ],
        "future_availability": "前序阻断要求完成并进入人类最终决定阶段后可用。"
      },
      {
        "action": "decide_request_changes",
        "title": "要求继续修改",
        "description": "由人类维护者要求贡献侧继续修改。",
        "reason": "当前处于“等待维护者检查”，还不能执行“要求继续修改”。",
        "next_actor_roles": [
          "maintainer_verifier",
          "policy_steward",
          "maintainer"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:decide_request_changes",
            "relationship": "authority"
          }
        ],
        "category": "authority",
        "required_role": [
          "maintainer"
        ],
        "required_state": [
          "overridden",
          "ready_for_human_decision"
        ],
        "future_availability": "前序阻断要求完成并进入人类最终决定阶段后可用。"
      },
      {
        "action": "decide_close",
        "title": "关闭本次审核记录",
        "description": "由人类维护者关闭案例而不表示接受或合并。",
        "reason": "当前处于“等待维护者检查”，还不能执行“关闭本次审核记录”。",
        "next_actor_roles": [
          "maintainer_verifier",
          "policy_steward",
          "maintainer"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:decide_close",
            "relationship": "authority"
          }
        ],
        "category": "authority",
        "required_role": [
          "maintainer"
        ],
        "required_state": [
          "overridden",
          "ready_for_human_decision",
          "repair_requested"
        ],
        "future_availability": "前序阻断要求完成并进入人类最终决定阶段后可用。"
      }
    ],
    "explanations": [
      {
        "title": "为什么本次采用轻量审核？",
        "technical_term": "lightweight path",
        "plain_language": "本次修改未触发高风险规则，也不要求负责人确认或独立维护者检查；所需材料较少，但最终项目决定仍由人类维护者作出。",
        "source_references": [
          {
            "kind": "matched_rule",
            "object_id": "match-documentation-low",
            "relationship": "path_intensity"
          }
        ],
        "reason_presentation": {
          "reason_code": "lightweight_path",
          "display_plain": "本次未触发完整治理流程，只需完成轻量审核要求。",
          "source_english": "Structured AGM preparation was explicitly declared or requested; no claim about contributor identity is inferred.",
          "source_code": "lightweight_path",
          "trace_refs": [
            {
              "kind": "matched_rule",
              "object_id": "match-documentation-low",
              "relationship": "path_intensity"
            }
          ]
        }
      },
      {
        "title": "本次只重新检查受影响部分",
        "technical_term": "scoped repair and revalidation",
        "plain_language": "需要重新检查：O-AGENT-SCOPE。 保留的材料：evidence-0a51a227c9c15692a99d7e527b174492, evidence-5c1362d33d7653c7ab21254f127c4317。",
        "source_references": [
          {
            "kind": "repair_request",
            "object_id": "repair-36a01320d26c57d4a38a7c937e522e18",
            "relationship": "scope"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
            "relationship": "retained"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
            "relationship": "retained"
          }
        ],
        "reason_presentation": {
          "reason_code": "retained_unaffected_evidence",
          "display_plain": "未受本次变化影响的材料继续有效，无需重复提交。",
          "source_english": "Unaffected evidence remains bound to the current contribution fingerprint.",
          "source_code": "retained_unaffected_evidence",
          "trace_refs": [
            {
              "kind": "repair_request",
              "object_id": "repair-36a01320d26c57d4a38a7c937e522e18",
              "relationship": "scope"
            },
            {
              "kind": "evidence",
              "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
              "relationship": "retained"
            },
            {
              "kind": "evidence",
              "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
              "relationship": "retained"
            }
          ]
        }
      }
    ],
    "delegation_help": {
      "title": "是否把具有独立行动能力的工作交给了另一个智能体？",
      "technical_term": "agent action and delegation scope",
      "plain_language": "通常算作继续委派：子智能体修改文件、执行命令、自主生成被直接采用的代码或配置、拥有独立工具权限或行动范围，或其产出直接进入当前贡献。通常不算：普通函数或工具调用、文件读取、搜索、没有独立行动权的模型调用，或只提供建议且没有修改/提交产出的辅助模型。",
      "source_references": [
        {
          "kind": "autonomy_profile",
          "object_id": "supervised_agent",
          "relationship": "delegation_definition"
        },
        {
          "kind": "compiled_obligation",
          "object_id": "obl-o-agent-scope",
          "relationship": "agent_scope_requirement"
        }
      ],
      "reason_presentation": null
    },
    "repair_loop": [
      "维护者发现问题",
      "返回修改指定部分",
      "重新检查受影响部分",
      "继续原流程"
    ],
    "technical_details": {
      "raw_state": "awaiting_maintainer_verification",
      "readiness": "repair_required",
      "risk_rules": [
        {
          "id": "match-documentation-low",
          "rule_id": "documentation-low",
          "zone": "documentation",
          "risk_level": "low",
          "affected_paths": [
            "docs/guide.md"
          ],
          "selector_reasons": [
            "path selectors matched: docs/guide.md"
          ],
          "obligation_ids": [
            "O-SUMMARY",
            "O-CHANGED-FILES"
          ],
          "case_required": false,
          "source": "risk_rule",
          "obligation_overrides": {}
        }
      ],
      "autonomy_profile": {
        "id": "supervised_agent",
        "description": "Agent acts within a task under active human supervision.",
        "obligation_ids": [
          "O-AGENT-SCOPE"
        ],
        "action_scope": "task-bounded",
        "persistence": "session",
        "permissions": "workspace",
        "supervision": "active",
        "submission_authority": "human",
        "delegation": "declared"
      },
      "assurance_profile": {
        "id": "standard",
        "description": "Project-default assurance profile.",
        "obligation_ids": []
      },
      "interaction_rules": [],
      "compiled_obligations": [
        {
          "id": "obl-o-agent-scope",
          "obligation_id": "O-AGENT-SCOPE",
          "source_rule_ids": [
            "autonomy:supervised_agent"
          ],
          "type": "evidence",
          "severity": "medium",
          "blocking": true,
          "verifier_roles": [
            "maintainer",
            "maintainer_verifier"
          ],
          "evidence_type": "agent_action_scope",
          "description": "Record the declared action, permissions, supervision, and delegation scope.",
          "affected_scope": [],
          "status": "satisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-changed-files",
          "obligation_id": "O-CHANGED-FILES",
          "source_rule_ids": [
            "documentation-low"
          ],
          "type": "evidence",
          "severity": "low",
          "blocking": true,
          "verifier_roles": [
            "maintainer",
            "maintainer_verifier"
          ],
          "evidence_type": "changed_files",
          "description": "Identify the files and scopes covered by the contribution.",
          "affected_scope": [
            "docs/guide.md"
          ],
          "status": "satisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-summary",
          "obligation_id": "O-SUMMARY",
          "source_rule_ids": [
            "documentation-low"
          ],
          "type": "evidence",
          "severity": "low",
          "blocking": true,
          "verifier_roles": [
            "maintainer",
            "maintainer_verifier"
          ],
          "evidence_type": "contribution_summary",
          "description": "Provide a concise factual contribution summary.",
          "affected_scope": [
            "docs/guide.md"
          ],
          "status": "satisfied",
          "interaction_ids": []
        }
      ],
      "evidence_records": [
        {
          "id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
          "obligation_ids": [
            "O-AGENT-SCOPE"
          ],
          "affected_scope": [
            "docs/guide.md"
          ],
          "contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
          "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
          "evidence_type": "agent_action_scope",
          "value": "编码智能体仅处理本次文档贡献并运行既有检查；没有继续委派，补充说明覆盖当前版本。",
          "command": null,
          "environment": null,
          "artifact_path": null,
          "artifact_hash": null,
          "observed_at": "2026-07-26T00:05:00Z",
          "expires_at": null,
          "source_actor": "contributor-agent",
          "source_tool": "scenario-generator",
          "retained_for_contribution_fingerprint": null,
          "retention_reason": null,
          "rejected_at": null,
          "rejected_by": null,
          "rejection_reason": null,
          "validity_state": "valid",
          "invalid_reasons": []
        },
        {
          "id": "evidence-0a51a227c9c15692a99d7e527b174492",
          "obligation_ids": [
            "O-CHANGED-FILES"
          ],
          "affected_scope": [
            "docs/guide.md"
          ],
          "contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
          "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
          "evidence_type": "changed_files",
          "value": [
            "docs/guide.md"
          ],
          "command": null,
          "environment": null,
          "artifact_path": null,
          "artifact_hash": null,
          "observed_at": "2026-07-26T00:05:00Z",
          "expires_at": null,
          "source_actor": "contributor-agent",
          "source_tool": "scenario-generator",
          "retained_for_contribution_fingerprint": null,
          "retention_reason": null,
          "rejected_at": null,
          "rejected_by": null,
          "rejection_reason": null,
          "validity_state": "valid",
          "invalid_reasons": []
        },
        {
          "id": "evidence-5c1362d33d7653c7ab21254f127c4317",
          "obligation_ids": [
            "O-SUMMARY"
          ],
          "affected_scope": [
            "docs/guide.md"
          ],
          "contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
          "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
          "evidence_type": "contribution_summary",
          "value": "贡献者补充了智能体行动与委派说明；本次补充未修改代码、测试结果或安全影响说明。",
          "command": null,
          "environment": null,
          "artifact_path": null,
          "artifact_hash": null,
          "observed_at": "2026-07-26T00:05:00Z",
          "expires_at": null,
          "source_actor": "contributor-agent",
          "source_tool": "scenario-generator",
          "retained_for_contribution_fingerprint": null,
          "retention_reason": null,
          "rejected_at": null,
          "rejected_by": null,
          "rejection_reason": null,
          "validity_state": "valid",
          "invalid_reasons": []
        }
      ],
      "attestation_records": [],
      "verification_records": [
        {
          "id": "verification-5b2e4e7a1c325583912ee759c2b334cf",
          "actor": "verifier-1",
          "role": "maintainer_verifier",
          "timestamp": "2026-07-26T00:00:00Z",
          "obligation_ids": [
            "O-AGENT-SCOPE",
            "O-CHANGED-FILES",
            "O-SUMMARY"
          ],
          "evidence_ids": [
            "evidence-0a51a227c9c15692a99d7e527b174492",
            "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
            "evidence-5c1362d33d7653c7ab21254f127c4317"
          ],
          "outcome": "verified",
          "reason": "Initial evidence checked.",
          "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
          "contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0"
        }
      ],
      "findings": [
        {
          "id": "finding-8c9865b11f9455de8729c497a127546b",
          "code": "agent_delegation_clarification",
          "severity": "high",
          "message": "Clarify agent action and delegation scope only.",
          "blocking": true,
          "related_object_ids": [],
          "affected_obligation_ids": [
            "O-AGENT-SCOPE"
          ],
          "status": "open",
          "created_at": "2026-07-26T00:00:00Z",
          "resolved_at": null,
          "resolution": null
        }
      ],
      "repair_requests": [
        {
          "id": "repair-36a01320d26c57d4a38a7c937e522e18",
          "finding_ids": [
            "finding-8c9865b11f9455de8729c497a127546b"
          ],
          "responsible_role": "contributor",
          "affected_obligation_ids": [
            "O-AGENT-SCOPE"
          ],
          "requested_correction": "Clarify agent action and delegation scope only.",
          "revalidation_required": [
            "O-AGENT-SCOPE"
          ],
          "requested_by": "verifier-1",
          "requested_at": "2026-07-26T00:00:00Z",
          "status": "resubmitted",
          "attempts": [
            {
              "id": "attempt-612807c028a75b3782f750a111c86bb9",
              "actor": "contributor-agent",
              "timestamp": "2026-07-26T00:00:00Z",
              "summary": "Clarified delegation wording without changing the contribution.",
              "affected_obligation_ids": [
                "O-AGENT-SCOPE"
              ],
              "evidence_ids": [],
              "change_assessment": {
                "change_classification": "no_material_change",
                "change_reason": "Wording clarification does not change contribution behavior.",
                "previous_contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
                "new_contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
                "stale_evidence_ids": [],
                "retained_evidence_ids": [
                  "evidence-0a51a227c9c15692a99d7e527b174492",
                  "evidence-5c1362d33d7653c7ab21254f127c4317"
                ],
                "invalidated_attestation_ids": [],
                "required_revalidation_scope": [
                  "O-AGENT-SCOPE"
                ]
              },
              "change_classification": "no_material_change",
              "change_reason": "Wording clarification does not change contribution behavior.",
              "previous_contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
              "new_contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
              "stale_evidence_ids": [],
              "retained_evidence_ids": [
                "evidence-0a51a227c9c15692a99d7e527b174492",
                "evidence-5c1362d33d7653c7ab21254f127c4317"
              ],
              "invalidated_attestation_ids": [],
              "required_revalidation_scope": [
                "O-AGENT-SCOPE"
              ]
            }
          ]
        }
      ],
      "attempted_operations": [],
      "contribution_fingerprint": "712fcd4dc43abd39cf07328603c2a14d9da29e20b1369a6d2b1b1b8eba6080a0",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "policy_snapshot": {
        "id": "policy-d4b430c206225c9f96fd01ce0f6199ec",
        "schema_version": "agm.policy_snapshot/v0.2-dev",
        "manifest_version": "agm.manifest/v0.2-dev",
        "base_commit": "demo-base",
        "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
        "resolved_at": "2026-07-26T00:00:00Z",
        "source_paths": [
          ".agm/manifest.yml",
          ".agm/agents/entrypoints.yml",
          ".agm/profiles/assurance_profiles.yml",
          ".agm/profiles/autonomy_profiles.yml",
          ".agm/interfaces/contributor_panel.yml",
          ".agm/policies/evidence_profiles.yml",
          ".agm/interfaces/governance_report.yml",
          ".agm/policies/interaction_rules.yml",
          ".agm/interfaces/maintainer_panel.yml",
          ".agm/interfaces/messages.yml",
          ".agm/roles/permissions.yml",
          ".agm/policies/risk_rules.yml",
          ".agm/roles/roles.yml",
          ".agm/workflows/state_machine.yml"
        ]
      },
      "transition_history": [
        {
          "id": "transition-1881127c74f85c64a27983540b53aa8f",
          "case_id": "scoped-repair",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "case_opened",
          "target_state": "policy_resolved",
          "action": "resolve_policy",
          "reason": "Resolved canonical policy against the contribution.",
          "related_object_ids": [
            "policy-d4b430c206225c9f96fd01ce0f6199ec"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-177148c790b35961986ce8d6da0ef25d",
          "case_id": "scoped-repair",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "policy_resolved",
          "target_state": "obligations_compiled",
          "action": "compile_obligations",
          "reason": "Compiled the union of matched, profile, and interaction obligations.",
          "related_object_ids": [
            "obl-o-agent-scope",
            "obl-o-changed-files",
            "obl-o-summary"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-f3df06251a0c57f58f302d45ebf1f8c7",
          "case_id": "scoped-repair",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "obligations_compiled",
          "target_state": "evidence_incomplete",
          "action": "mark_evidence_state",
          "reason": "The new case has unsatisfied evidence obligations.",
          "related_object_ids": [
            "obl-o-agent-scope",
            "obl-o-changed-files",
            "obl-o-summary"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-6512e18aa3935087bbedb4777db22138",
          "case_id": "scoped-repair",
          "actor": "contributor-agent",
          "role": "contributor_agent",
          "source_state": "evidence_incomplete",
          "target_state": "awaiting_maintainer_verification",
          "action": "submit_for_verification",
          "reason": "Contributor submitted prepared evidence for maintainer verification.",
          "related_object_ids": [
            "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
            "evidence-0a51a227c9c15692a99d7e527b174492",
            "evidence-5c1362d33d7653c7ab21254f127c4317"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-e5af5ef503e7581eb3deaad43fb1baef",
          "case_id": "scoped-repair",
          "actor": "verifier-1",
          "role": "maintainer_verifier",
          "source_state": "awaiting_maintainer_verification",
          "target_state": "verification_complete",
          "action": "verify_evidence",
          "reason": "Initial evidence checked.",
          "related_object_ids": [
            "verification-5b2e4e7a1c325583912ee759c2b334cf"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-ea7b63934d9e50ddbf6208b6ee05da15",
          "case_id": "scoped-repair",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "verification_complete",
          "target_state": "ready_for_human_decision",
          "action": "mark_ready",
          "reason": "All blocking obligations are satisfied or verified; the case is ready for an authorized human decision, not accepted.",
          "related_object_ids": [
            "verification-5b2e4e7a1c325583912ee759c2b334cf"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-73f7594267755464b038a86d9eea8add",
          "case_id": "scoped-repair",
          "actor": "verifier-1",
          "role": "maintainer_verifier",
          "source_state": "ready_for_human_decision",
          "target_state": "repair_requested",
          "action": "request_repair",
          "reason": "Clarify agent action and delegation scope only.",
          "related_object_ids": [
            "finding-8c9865b11f9455de8729c497a127546b",
            "repair-36a01320d26c57d4a38a7c937e522e18"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-d852903b5565559abc3107e7e125f43a",
          "case_id": "scoped-repair",
          "actor": "contributor-agent",
          "role": "contributor_agent",
          "source_state": "repair_requested",
          "target_state": "resubmitted",
          "action": "resubmit",
          "reason": "Clarified delegation wording without changing the contribution.",
          "related_object_ids": [
            "attempt-612807c028a75b3782f750a111c86bb9"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-b2cf970564f25e54b8876e1685661bd3",
          "case_id": "scoped-repair",
          "actor": "contributor-agent",
          "role": "contributor_agent",
          "source_state": "resubmitted",
          "target_state": "awaiting_maintainer_verification",
          "action": "submit_for_verification",
          "reason": "Contributor submitted prepared evidence for maintainer verification.",
          "related_object_ids": [
            "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
            "evidence-0a51a227c9c15692a99d7e527b174492",
            "evidence-5c1362d33d7653c7ab21254f127c4317"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        }
      ],
      "final_decision": null,
      "closure_receipt": null,
      "policy_migration_diagnostic": {
        "case_id": "scoped-repair",
        "policy_changed": false,
        "original_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
        "current_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
        "still_valid_obligations": [
          "O-AGENT-SCOPE",
          "O-CHANGED-FILES",
          "O-SUMMARY"
        ],
        "changed_obligations": [],
        "added_obligations": [],
        "removed_obligations": [],
        "evidence_requiring_revalidation": [],
        "attestations_invalidated_if_migrated": [],
        "may_remain_on_original_snapshot": true,
        "must_migrate": false,
        "reason": "The canonical policy fingerprint is unchanged."
      },
      "raw_english_specification_text": {
        "obligations": {
          "O-AGENT-SCOPE": "Record the declared action, permissions, supervision, and delegation scope.",
          "O-CHANGED-FILES": "Identify the files and scopes covered by the contribution.",
          "O-SUMMARY": "Provide a concise factual contribution summary."
        },
        "matched_rule_reasons": {
          "documentation-low": [
            "path selectors matched: docs/guide.md"
          ]
        },
        "interaction_rules": {},
        "authority_notice": "Verification or readiness is not acceptance. Final decisions remain with authorized human maintainers."
      }
    },
    "authority_notice": "本页面只把 AGM 的真实状态、依据和合法操作整理成人类可读形式。材料齐备、维护者检查完成，或者已经具备进入最终决定的条件，都不等于代码已经被项目接受。最终决定只属于获授权的人类维护者。",
    "responsibility": {
      "primary_roles": [
        "maintainer_verifier",
        "policy_steward",
        "maintainer"
      ],
      "display_label": "维护者侧检查人员、项目规则负责人、人类维护者",
      "reason": "受影响材料已补充或仍然有效；当前只需重新检查指定修复范围。",
      "blocking_items": [
        "智能体行动与委派说明"
      ],
      "next_handoff_roles": [
        "maintainer"
      ]
    },
    "current_relevant_actions": [
      {
        "action": "verify_evidence",
        "title": "检查提交材料",
        "description": "记录维护者对指定项目要求及其绑定材料的检查结果。",
        "consequence": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
        "mutates_state": true,
        "actor_role": "maintainer",
        "default_obligation_ids": [
          "O-AGENT-SCOPE"
        ],
        "required_parameters": [
          "reason"
        ],
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:verify_evidence",
            "relationship": "authority"
          },
          {
            "kind": "state_machine_rule",
            "object_id": "awaiting_maintainer_verification:verify_evidence:verification_complete",
            "relationship": "transition"
          }
        ],
        "relevance": "current",
        "group": "current_relevant",
        "primary_reason": "该操作直接对应当前流程阶段或开放问题。",
        "selector_options": [
          {
            "selector_token": "sel-137fe07fbb014f30f02652c6e0c985e18db341759375069b63fcf8dc956f2cc4",
            "action": "verify_evidence",
            "label": "智能体行动与委派说明",
            "status_label": "已提供；等待维护者重新检查",
            "affected_scope": [],
            "obligation_ids": [
              "O-AGENT-SCOPE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-AGENT-SCOPE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "awaiting_revalidation",
            "technical_details": {
              "obligation_id": "O-AGENT-SCOPE",
              "evidence_ids": [
                "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1"
              ],
              "finding_ids": [
                "finding-8c9865b11f9455de8729c497a127546b"
              ]
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-agent-scope",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "autonomy:supervised_agent",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
                "relationship": "observed"
              },
              {
                "kind": "finding",
                "object_id": "finding-8c9865b11f9455de8729c497a127546b",
                "relationship": "diagnostic"
              }
            ]
          }
        ]
      },
      {
        "action": "request_repair",
        "title": "要求补充或修改",
        "description": "指出问题和受影响义务，返回贡献侧修复。",
        "consequence": "仅指定范围需要修复和重新检查，未受影响材料保留。",
        "mutates_state": true,
        "actor_role": "maintainer",
        "default_obligation_ids": [
          "O-AGENT-SCOPE"
        ],
        "required_parameters": [
          "obligation_ids",
          "reason"
        ],
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:request_repair",
            "relationship": "authority"
          },
          {
            "kind": "state_machine_rule",
            "object_id": "awaiting_maintainer_verification:request_repair:repair_requested",
            "relationship": "transition"
          }
        ],
        "relevance": "current",
        "group": "current_relevant",
        "primary_reason": "该操作直接对应当前流程阶段或开放问题。",
        "selector_options": [
          {
            "selector_token": "sel-80a9ed6e44d1378f574c328eaeaf7ba96cd07e4aad5c449608cae2681d73ddb5",
            "action": "request_repair",
            "label": "智能体行动与委派说明",
            "status_label": "已提供；等待维护者重新检查",
            "affected_scope": [],
            "obligation_ids": [
              "O-AGENT-SCOPE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-AGENT-SCOPE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "awaiting_revalidation",
            "technical_details": {
              "obligation_id": "O-AGENT-SCOPE",
              "evidence_ids": [
                "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1"
              ],
              "finding_ids": [
                "finding-8c9865b11f9455de8729c497a127546b"
              ]
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-agent-scope",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "autonomy:supervised_agent",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
                "relationship": "observed"
              },
              {
                "kind": "finding",
                "object_id": "finding-8c9865b11f9455de8729c497a127546b",
                "relationship": "diagnostic"
              }
            ]
          },
          {
            "selector_token": "sel-a0df379baa9cd51709208499e5bc735cdb78f956129ecc689d8f9ebafadcd430",
            "action": "request_repair",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-CHANGED-FILES"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-CHANGED-FILES"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-CHANGED-FILES",
              "evidence_ids": [
                "evidence-0a51a227c9c15692a99d7e527b174492"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-changed-files",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "documentation-low",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-f5497a7a3588ab4f15c015d60f2b1c53839a7ad9f4d009807ee059e2514ab182",
            "action": "request_repair",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-SUMMARY"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-SUMMARY"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-SUMMARY",
              "evidence_ids": [
                "evidence-5c1362d33d7653c7ab21254f127c4317"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-summary",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "documentation-low",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
                "relationship": "observed"
              }
            ]
          }
        ]
      },
      {
        "action": "reject_evidence",
        "title": "拒绝当前材料",
        "description": "拒绝一条不能支持当前修改的具体材料。",
        "consequence": "该材料将标记为已拒绝，并建立指定范围的补充或修改请求。",
        "mutates_state": true,
        "actor_role": "maintainer",
        "default_obligation_ids": [],
        "required_parameters": [
          "object_id",
          "reason"
        ],
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:reject_evidence",
            "relationship": "authority"
          },
          {
            "kind": "state_machine_rule",
            "object_id": "awaiting_maintainer_verification:reject_evidence:repair_requested",
            "relationship": "transition"
          }
        ],
        "relevance": "current",
        "group": "current_relevant",
        "primary_reason": "该操作直接对应当前流程阶段或开放问题。",
        "selector_options": [
          {
            "selector_token": "sel-f5ec08276b893da6c7a097c371ba920091d96d4ffd7706e8e8a21f371fca4183",
            "action": "reject_evidence",
            "label": "智能体行动与委派说明",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-AGENT-SCOPE"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
              "evidence_type": "agent_action_scope"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-a65b60ff9f372d533e72ca54467c1ef6132c344cf1208e96606bd783e18191da",
            "action": "reject_evidence",
            "label": "变更文件清单",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-CHANGED-FILES"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-0a51a227c9c15692a99d7e527b174492"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-0a51a227c9c15692a99d7e527b174492",
              "evidence_type": "changed_files"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-15e0e6c942e977a2f31a241b4ee3d865640d4e5e084878bb3ca47b4d4a3db7eb",
            "action": "reject_evidence",
            "label": "修改说明",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-SUMMARY"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-5c1362d33d7653c7ab21254f127c4317"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
              "evidence_type": "contribution_summary"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
                "relationship": "action_target"
              }
            ]
          }
        ]
      },
      {
        "action": "ask_clarification",
        "title": "请求补充说明",
        "description": "针对指定要求提出可审计的澄清问题。",
        "consequence": "案例返回贡献侧回答，所选范围需要重新检查。",
        "mutates_state": true,
        "actor_role": "maintainer",
        "default_obligation_ids": [
          "O-AGENT-SCOPE"
        ],
        "required_parameters": [
          "obligation_ids",
          "reason"
        ],
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:ask_clarification",
            "relationship": "authority"
          },
          {
            "kind": "state_machine_rule",
            "object_id": "awaiting_maintainer_verification:ask_clarification:repair_requested",
            "relationship": "transition"
          }
        ],
        "relevance": "current",
        "group": "current_relevant",
        "primary_reason": "该操作直接对应当前流程阶段或开放问题。",
        "selector_options": [
          {
            "selector_token": "sel-06aa442dd7376de0976c29253225cf3e2504ae05fbf85cd14c7740fe2e791e03",
            "action": "ask_clarification",
            "label": "智能体行动与委派说明",
            "status_label": "已提供；等待维护者重新检查",
            "affected_scope": [],
            "obligation_ids": [
              "O-AGENT-SCOPE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-AGENT-SCOPE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "awaiting_revalidation",
            "technical_details": {
              "obligation_id": "O-AGENT-SCOPE",
              "evidence_ids": [
                "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1"
              ],
              "finding_ids": [
                "finding-8c9865b11f9455de8729c497a127546b"
              ]
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-agent-scope",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "autonomy:supervised_agent",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
                "relationship": "observed"
              },
              {
                "kind": "finding",
                "object_id": "finding-8c9865b11f9455de8729c497a127546b",
                "relationship": "diagnostic"
              }
            ]
          },
          {
            "selector_token": "sel-e65658a4f5b72be80ac6a9461bfc3afbb6c1c162d5f3b28a74a428e9b121626d",
            "action": "ask_clarification",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-CHANGED-FILES"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-CHANGED-FILES"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-CHANGED-FILES",
              "evidence_ids": [
                "evidence-0a51a227c9c15692a99d7e527b174492"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-changed-files",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "documentation-low",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-b921eaf9964c762866f88b8d0cb3d6f95d549096559394246722e34f2fc026a5",
            "action": "ask_clarification",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-SUMMARY"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-SUMMARY"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-SUMMARY",
              "evidence_ids": [
                "evidence-5c1362d33d7653c7ab21254f127c4317"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-summary",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "documentation-low",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
                "relationship": "observed"
              }
            ]
          }
        ]
      }
    ],
    "other_available_actions": [
      {
        "action": "view_change_scope",
        "title": "查看变化范围",
        "description": "查看变更文件、风险规则、影响范围和绑定指纹。",
        "consequence": "只读操作，不改变案例状态。",
        "mutates_state": false,
        "actor_role": "maintainer",
        "default_obligation_ids": [],
        "required_parameters": [],
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:view_change_scope",
            "relationship": "authority"
          }
        ],
        "relevance": "secondary",
        "group": "other_available",
        "primary_reason": "后端允许此操作，但它不直接处理当前主要阻断项。",
        "selector_options": []
      },
      {
        "action": "record_policy_conflict",
        "title": "记录项目规则冲突",
        "description": "记录无法由普通材料修复的策略冲突。",
        "consequence": "案例转入补充处理，由项目规则负责人或维护者处理。",
        "mutates_state": true,
        "actor_role": "maintainer",
        "default_obligation_ids": [
          "O-AGENT-SCOPE"
        ],
        "required_parameters": [
          "obligation_ids",
          "reason"
        ],
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:record_policy_conflict",
            "relationship": "authority"
          },
          {
            "kind": "state_machine_rule",
            "object_id": "awaiting_maintainer_verification:record_policy_conflict:repair_requested",
            "relationship": "transition"
          }
        ],
        "relevance": "secondary",
        "group": "other_available",
        "primary_reason": "后端允许此操作，但它不直接处理当前主要阻断项。",
        "selector_options": [
          {
            "selector_token": "sel-13cc652c952536ab0042e22c9d6232b281083b0cbfb486e3e2b6ec20e9d7b7ec",
            "action": "record_policy_conflict",
            "label": "智能体行动与委派说明",
            "status_label": "已提供；等待维护者重新检查",
            "affected_scope": [],
            "obligation_ids": [
              "O-AGENT-SCOPE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-AGENT-SCOPE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "awaiting_revalidation",
            "technical_details": {
              "obligation_id": "O-AGENT-SCOPE",
              "evidence_ids": [
                "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1"
              ],
              "finding_ids": [
                "finding-8c9865b11f9455de8729c497a127546b"
              ]
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-agent-scope",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "autonomy:supervised_agent",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
                "relationship": "observed"
              },
              {
                "kind": "finding",
                "object_id": "finding-8c9865b11f9455de8729c497a127546b",
                "relationship": "diagnostic"
              }
            ]
          },
          {
            "selector_token": "sel-c92112faea315c07d46a7546b2fd819b64c12fcfabedda4820d3a2adfad73068",
            "action": "record_policy_conflict",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-CHANGED-FILES"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-CHANGED-FILES"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-CHANGED-FILES",
              "evidence_ids": [
                "evidence-0a51a227c9c15692a99d7e527b174492"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-changed-files",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "documentation-low",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-a2ec175bb781dce35c635dfcf64baf5e59300d15cb1d805d99582382ec03c64d",
            "action": "record_policy_conflict",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              "docs/guide.md"
            ],
            "obligation_ids": [
              "O-SUMMARY"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-SUMMARY"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-SUMMARY",
              "evidence_ids": [
                "evidence-5c1362d33d7653c7ab21254f127c4317"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-summary",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "documentation-low",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
                "relationship": "observed"
              }
            ]
          }
        ]
      }
    ],
    "unavailable_action_summary": "还有 9 项操作因当前阶段、权限或对象范围暂不可用",
    "utility_actions": [
      {
        "action_id": "copy_missing_requirements",
        "label": "复制缺失项清单",
        "description": "生成可直接交给贡献侧的缺失、过时或无效材料清单。",
        "output_type": "text/plain",
        "output": "当前没有需要贡献侧补充或更新的材料。",
        "trace_refs": [],
        "state_changing": false
      },
      {
        "action_id": "export_contributor_checklist",
        "label": "导出贡献者待办清单",
        "description": "导出包含责任方、待处理项和范围的 Markdown 清单。",
        "output_type": "text/markdown",
        "output": "# 贡献者待办清单\n\n案例：scoped-repair\n当前责任方：维护者侧检查人员、项目规则负责人、人类维护者\n原因：受影响材料已补充或仍然有效；当前只需重新检查指定修复范围。\n\n## 待处理项\n\n当前没有需要贡献侧补充或更新的材料。\n\n完成后请按当前 repair/提交范围交回；最终决定仍由人类维护者作出。",
        "trace_refs": [],
        "state_changing": false
      },
      {
        "action_id": "export_reviewer_summary",
        "label": "下载维护者摘要",
        "description": "导出当前风险、责任方和阻断项摘要，不作接受判断。",
        "output_type": "text/markdown",
        "output": "# 维护者审核摘要\n\n案例：scoped-repair\n当前状态：等待维护者检查\n风险：low\n当前责任方：维护者侧检查人员、项目规则负责人、人类维护者\n责任方依据：受影响材料已补充或仍然有效；当前只需重新检查指定修复范围。\n\n## 阻断或待检查项\n\n- 智能体行动与委派说明：已提供；等待维护者重新检查；范围：当前贡献范围\n\n本摘要是治理状态说明，不是接受决定。",
        "trace_refs": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-agent-scope",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "autonomy:supervised_agent",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
            "relationship": "observed"
          },
          {
            "kind": "finding",
            "object_id": "finding-8c9865b11f9455de8729c497a127546b",
            "relationship": "diagnostic"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-changed-files",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "documentation-low",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
            "relationship": "observed"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-summary",
            "relationship": "reference"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
            "relationship": "observed"
          }
        ],
        "state_changing": false
      },
      {
        "action_id": "view_change_scope",
        "label": "查看变化范围",
        "description": "查看变更文件、匹配规则和各要求的影响范围。",
        "output_type": "application/json",
        "output": "{\n  \"case_id\": \"scoped-repair\",\n  \"changed_files\": [\n    \"docs/guide.md\"\n  ],\n  \"matched_risk_rules\": [\n    {\n      \"rule_id\": \"documentation-low\",\n      \"zone\": \"documentation\",\n      \"affected_paths\": [\n        \"docs/guide.md\"\n      ]\n    }\n  ],\n  \"requirement_scopes\": {\n    \"O-AGENT-SCOPE\": [],\n    \"O-CHANGED-FILES\": [\n      \"docs/guide.md\"\n    ],\n    \"O-SUMMARY\": [\n      \"docs/guide.md\"\n    ]\n  }\n}",
        "trace_refs": [
          {
            "kind": "matched_rule",
            "object_id": "match-documentation-low",
            "relationship": "change_scope"
          }
        ],
        "state_changing": false
      },
      {
        "action_id": "copy_handoff_note",
        "label": "复制当前责任方说明",
        "description": "生成不改变案例状态的 handoff note。",
        "output_type": "text/plain",
        "output": "案例 scoped-repair 当前交给：维护者侧检查人员、项目规则负责人、人类维护者。\n受影响材料已补充或仍然有效；当前只需重新检查指定修复范围。\n涉及：智能体行动与委派说明。\n完成后交给角色：人类维护者。",
        "trace_refs": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-agent-scope",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "autonomy:supervised_agent",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
            "relationship": "observed"
          },
          {
            "kind": "finding",
            "object_id": "finding-8c9865b11f9455de8729c497a127546b",
            "relationship": "diagnostic"
          }
        ],
        "state_changing": false
      }
    ],
    "materiality_declaration": {
      "classification": "no_material_change",
      "classification_label": "未检测到贡献指纹变化",
      "declared_by": "contributor-agent",
      "declared_by_role": "contributor_agent",
      "declared_by_display": "贡献侧智能体",
      "reason": "本次只澄清文字表述，不改变贡献行为。",
      "reason_presentation": {
        "reason_code": "wording_only_clarification",
        "display_plain": "本次只澄清文字表述，不改变贡献行为。",
        "source_english": "Wording clarification does not change contribution behavior.",
        "source_code": "wording_only_clarification",
        "trace_refs": [
          {
            "kind": "repair_request",
            "object_id": "repair-36a01320d26c57d4a38a7c937e522e18",
            "relationship": "source"
          },
          {
            "kind": "resubmission_attempt",
            "object_id": "attempt-612807c028a75b3782f750a111c86bb9",
            "relationship": "materiality_declaration"
          }
        ]
      },
      "affected_obligation_ids": [
        "O-AGENT-SCOPE"
      ],
      "affected_labels": [
        "智能体行动与委派说明"
      ],
      "unaffected_obligation_ids": [
        "O-CHANGED-FILES",
        "O-SUMMARY"
      ],
      "unaffected_labels": [
        "变更文件清单",
        "修改说明"
      ],
      "retained_evidence_ids": [
        "evidence-0a51a227c9c15692a99d7e527b174492",
        "evidence-5c1362d33d7653c7ab21254f127c4317"
      ],
      "stale_evidence_ids": [],
      "invalidated_attestation_ids": [],
      "requires_maintainer_verification": true,
      "traceability": [
        {
          "kind": "repair_request",
          "object_id": "repair-36a01320d26c57d4a38a7c937e522e18",
          "relationship": "source"
        },
        {
          "kind": "resubmission_attempt",
          "object_id": "attempt-612807c028a75b3782f750a111c86bb9",
          "relationship": "materiality_declaration"
        }
      ]
    },
    "rejected_operation_notice": null
  },
  "trace_index": {
    "trace:requirement:agent-actions-delegation": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-agent-scope",
        "relationship": "source"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-agent-scope",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "autonomy:supervised_agent",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
        "relationship": "observed"
      },
      {
        "kind": "finding",
        "object_id": "finding-8c9865b11f9455de8729c497a127546b",
        "relationship": "diagnostic"
      }
    ],
    "trace:requirement:changed-files": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-changed-files",
        "relationship": "source"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-changed-files",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "documentation-low",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
        "relationship": "observed"
      }
    ],
    "trace:requirement:change-summary": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-summary",
        "relationship": "source"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-summary",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "documentation-low",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
        "relationship": "observed"
      }
    ],
    "trace:automatic-check:material_version_binding": [
      {
        "kind": "evidence",
        "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
        "relationship": "material_version_binding"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
        "relationship": "material_version_binding"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
        "relationship": "material_version_binding"
      }
    ],
    "trace:automatic-check:test_command_and_result": [],
    "trace:automatic-check:test_version_binding": [],
    "trace:automatic-check:evidence_freshness": [
      {
        "kind": "evidence",
        "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
        "relationship": "evidence_freshness"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
        "relationship": "evidence_freshness"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
        "relationship": "evidence_freshness"
      }
    ],
    "trace:automatic-check:attestation_version_binding": [],
    "trace:automatic-check:changed_file_scope_match": [],
    "trace:automatic-check:agent_involvement": [],
    "trace:automatic-check:recorded_delegation": [],
    "trace:automatic-check:authority_boundary": [],
    "trace:automatic-check:structural_obligations": [
      {
        "kind": "evidence",
        "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
        "relationship": "structural_obligations"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-0a51a227c9c15692a99d7e527b174492",
        "relationship": "structural_obligations"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-5c1362d33d7653c7ab21254f127c4317",
        "relationship": "structural_obligations"
      }
    ],
    "trace:automatic-check:semantic_declaration_consistency": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-agent-scope",
        "relationship": "semantic_declaration_consistency"
      }
    ],
    "trace:judgment:agent-actions-delegation": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-agent-scope",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "autonomy:supervised_agent",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-1f877f9f9e5d5df1b4c3714ea5fec6a1",
        "relationship": "observed"
      },
      {
        "kind": "finding",
        "object_id": "finding-8c9865b11f9455de8729c497a127546b",
        "relationship": "diagnostic"
      }
    ]
  }
}
```

</details>
