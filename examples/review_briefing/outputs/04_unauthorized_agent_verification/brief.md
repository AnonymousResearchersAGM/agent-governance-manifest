# AGM Maintainer Review Brief

## 认证模块使用说明更新

## 当前状态与下一步

### 无需额外 AGM 治理判断

本次无需额外 AGM 治理判断，可以进入正常代码审查。

当前责任方：普通代码审查者

- 按项目常规方式审查代码质量和功能影响。

> 检查完成不等于贡献已被接受；最终决定仍由有权人类维护者作出。

## 本次修改与风险

贡献者说明：本次贡献更新了认证模块的使用说明。

系统根据文件和声明归纳：

更新项目文档：docs/guide.md

影响范围：

- 文档与说明

综合风险：低

- docs/guide.md 触发了“文档与说明”风险范围。

- 未记录风险联动

> 归纳边界：系统归纳只依据文件路径、已匹配风险区域和明确声明，不代表系统已经证明代码的真实语义或行为。

## 当前问题与系统处理

### 系统已处理的异常

- 是否存在越权操作：系统拒绝了 1 次越权操作；治理状态没有变化。
  - 系统已拒绝该操作；该事件不产生新的维护者判断项。

## 项目要求与自动检查摘要

项目要求 2 项材料或确认。
- 2 项已完成当前阶段的形式核对或人工检查

自动检查：
- 4 项完成形式或版本核对
- 0 项发现问题
- 0 项需要人工判断
- 1 项异常已由系统处理

<details>
<summary>查看全部项目要求</summary>

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
  - 类别：附加信息；责任：系统已处理
  - 结论边界：AGM 只呈现治理记录和声明，不是智能体使用检测器。
- i 是否记录继续委派：本次贡献记录了智能体参与，但当前项目规则未要求单独提交智能体行动与委派说明。
  - 类别：附加信息；责任：系统已处理
  - 结论边界：这是一项附加信息，不构成缺失材料、finding 或流程阻断。
- ✓ 是否存在越权操作：系统拒绝了 1 次越权操作；治理状态没有变化。
  - 类别：系统完整性核对；责任：系统已处理
  - 结论边界：被拒绝事件不会替代对当前贡献材料的正常检查。
- ✓ 结构性项目要求是否满足：当前材料的结构、必填范围和前置确认已达到进入人类判断的条件。
  - 类别：项目规则要求；责任：系统已处理
  - 结论边界：结构满足不等于语义正确，也不等于贡献已被项目接受。

</details>

<details>
<summary>查看智能体与负责人材料</summary>

系统观察：

- 系统记录到贡献侧智能体尝试了维护者侧操作，该操作已被权限边界拒绝。
- 系统记录到智能体身份提交了 2 份治理材料。

贡献侧声明：

- 尚未提供智能体行动与委派声明。

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
  "case_id": "unauthorized-agent",
  "raw_state": "awaiting_maintainer_verification",
  "raw_readiness": "verification_in_progress",
  "contribution_fingerprint": "60746c94ba0cedc1010f84cd5b296629d37b67f940292df43aaeab4661462ede",
  "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
  "policy_snapshot": {
    "id": "policy-09b98729f0c95d56ae2d33d3e257dcb1",
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
      "id": "evidence-63a977ff7a335965a13a541abbb5b259",
      "obligation_ids": [
        "O-CHANGED-FILES"
      ],
      "affected_scope": [
        "docs/guide.md"
      ],
      "contribution_fingerprint": "60746c94ba0cedc1010f84cd5b296629d37b67f940292df43aaeab4661462ede",
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
      "id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
      "obligation_ids": [
        "O-SUMMARY"
      ],
      "affected_scope": [
        "docs/guide.md"
      ],
      "contribution_fingerprint": "60746c94ba0cedc1010f84cd5b296629d37b67f940292df43aaeab4661462ede",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "evidence_type": "contribution_summary",
      "value": "本次贡献更新了认证模块的使用说明。",
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
  "findings": [],
  "repair_requests": [],
  "attempted_operations": [
    {
      "id": "attempted-operation-141c5c1825f65706ad3787e49ff221ce",
      "case_id": "unauthorized-agent",
      "operation": "verify_evidence",
      "actor": "contributor-agent",
      "actor_role": "contributor_agent",
      "attempted_at": "2026-07-26T00:00:00Z",
      "result": "denied",
      "reason_raw": "Role contributor_agent is not authorized for action verify_evidence",
      "state_before": "awaiting_maintainer_verification",
      "state_after": "awaiting_maintainer_verification",
      "state_changed": false,
      "required_roles": [
        "maintainer",
        "maintainer_verifier",
        "policy_steward"
      ]
    }
  ],
  "verification_records": [],
  "transition_history": [
    {
      "id": "transition-c77ab972331f53338f79d0023aa05814",
      "case_id": "unauthorized-agent",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "case_opened",
      "target_state": "policy_resolved",
      "action": "resolve_policy",
      "reason": "Resolved canonical policy against the contribution.",
      "related_object_ids": [
        "policy-09b98729f0c95d56ae2d33d3e257dcb1"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-88c72d167b555327958927719ce12954",
      "case_id": "unauthorized-agent",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "policy_resolved",
      "target_state": "obligations_compiled",
      "action": "compile_obligations",
      "reason": "Compiled the union of matched, profile, and interaction obligations.",
      "related_object_ids": [
        "obl-o-changed-files",
        "obl-o-summary"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-3398fabaf05e5545add810d0fa006517",
      "case_id": "unauthorized-agent",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "obligations_compiled",
      "target_state": "evidence_incomplete",
      "action": "mark_evidence_state",
      "reason": "The new case has unsatisfied evidence obligations.",
      "related_object_ids": [
        "obl-o-changed-files",
        "obl-o-summary"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-3c7e885a30fc5b0b865fd5df1b530581",
      "case_id": "unauthorized-agent",
      "actor": "contributor-agent",
      "role": "contributor_agent",
      "source_state": "evidence_incomplete",
      "target_state": "awaiting_maintainer_verification",
      "action": "submit_for_verification",
      "reason": "Contributor submitted prepared evidence for maintainer verification.",
      "related_object_ids": [
        "evidence-63a977ff7a335965a13a541abbb5b259",
        "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    }
  ],
  "final_decision": null,
  "closure_receipt": null,
  "policy_migration_diagnostic": {
    "case_id": "unauthorized-agent",
    "policy_changed": false,
    "original_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
    "current_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
    "still_valid_obligations": [
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
    "generated_from_case_fingerprint": "60746c94ba0cedc1010f84cd5b296629d37b67f940292df43aaeab4661462ede",
    "actor": {
      "actor": "human-maintainer",
      "role": "maintainer",
      "human": true
    },
    "summary": {
      "case_id": "unauthorized-agent",
      "changed_files": [
        "docs/guide.md"
      ],
      "risk_level": "low",
      "risk_areas": [
        "文档（documentation）"
      ],
      "autonomy_profile": "human_direct",
      "path_kind": "lightweight",
      "path_label": "轻量审核",
      "current_stage": "等待维护者检查",
      "blocking_issue_count": 0,
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
      "raw_readiness": "verification_in_progress"
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
            "object_id": "transition-c77ab972331f53338f79d0023aa05814",
            "relationship": "primary:resolve_policy"
          },
          {
            "kind": "state_transition",
            "object_id": "transition-88c72d167b555327958927719ce12954",
            "relationship": "primary:compile_obligations"
          },
          {
            "kind": "matched_rule",
            "object_id": "match-documentation-low",
            "relationship": "risk_matching"
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
            "object_id": "transition-3398fabaf05e5545add810d0fa006517",
            "relationship": "primary:mark_evidence_state"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
            "relationship": "binding_or_retention"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
            "relationship": "binding_or_retention"
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
            "object_id": "transition-3c7e885a30fc5b0b865fd5df1b530581",
            "relationship": "primary:submit_for_verification"
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
        "traceability": []
      }
    ],
    "requirement_comparisons": [
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
          "evidence-63a977ff7a335965a13a541abbb5b259"
        ],
        "binding_fingerprints": [
          "60746c94ba0cedc1010f84cd5b296629d37b67f940292df43aaeab4661462ede"
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
            "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
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
          "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
        ],
        "binding_fingerprints": [
          "60746c94ba0cedc1010f84cd5b296629d37b67f940292df43aaeab4661462ede"
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
            "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
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
    "diagnostics": [],
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
          "O-CHANGED-FILES",
          "O-SUMMARY"
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
            "selector_token": "sel-05e2ed83b035677a3bbb8a8bf04ab683f1c574e757587f4be03471c89a96f948",
            "action": "verify_evidence",
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
                "evidence-63a977ff7a335965a13a541abbb5b259"
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
                "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-ad8a0478f7b8f97d7f43adeea0483a93d77f38fbbd813f2fee2df1435adc1aaf",
            "action": "verify_evidence",
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
                "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
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
                "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
                "relationship": "observed"
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
        "default_obligation_ids": [],
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
            "selector_token": "sel-301da2412a9809847ab6f316c9cc1880bb367cc482492234bcc4f7166d9ee7fc",
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
                "evidence-63a977ff7a335965a13a541abbb5b259"
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
                "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-73016056245d238a410c53c436950dfe44ae034faf23ddc9dba4f1af94e985ed",
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
                "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
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
                "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
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
            "selector_token": "sel-aa8a2cfebed39d031f0c7337d52ab0193b638030574b2fa6f5e5c56b4902250f",
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
              "evidence-63a977ff7a335965a13a541abbb5b259"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-63a977ff7a335965a13a541abbb5b259",
              "evidence_type": "changed_files"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-facfe421df4f1da7845fb3e27d591f0936970f547cc1611d5ef15b591257cd49",
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
              "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
              "evidence_type": "contribution_summary"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
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
        "default_obligation_ids": [],
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
            "selector_token": "sel-0532327c320a1b296a6f9c50a46f2f1fd8c87d6d78b53d3cadd8a81ad834eff0",
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
                "evidence-63a977ff7a335965a13a541abbb5b259"
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
                "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-6a60388bed5d4b03eab8f61725303866a181f324c0ed794daac4651140320f20",
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
                "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
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
                "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
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
        "default_obligation_ids": [],
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
            "selector_token": "sel-4fa031138877fe5a2835b589d20e0c36833657f889a045e0bf0bf9b77a7f5777",
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
                "evidence-63a977ff7a335965a13a541abbb5b259"
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
                "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-7ac60ee3a7cfb2ff98df510d8af06f7b0922df65a982b7edb3ae7fbcbb7cc48e",
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
                "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
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
                "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
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
      }
    ],
    "delegation_help": {
      "title": "是否把具有独立行动能力的工作交给了另一个智能体？",
      "technical_term": "agent action and delegation scope",
      "plain_language": "通常算作继续委派：子智能体修改文件、执行命令、自主生成被直接采用的代码或配置、拥有独立工具权限或行动范围，或其产出直接进入当前贡献。通常不算：普通函数或工具调用、文件读取、搜索、没有独立行动权的模型调用，或只提供建议且没有修改/提交产出的辅助模型。",
      "source_references": [
        {
          "kind": "autonomy_profile",
          "object_id": "human_direct",
          "relationship": "delegation_definition"
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
      "readiness": "verification_in_progress",
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
        "id": "human_direct",
        "description": "Direct human contribution; no claim about authorship is inferred from package absence.",
        "obligation_ids": [],
        "action_scope": "human-controlled",
        "persistence": "none",
        "permissions": "human account",
        "supervision": "direct",
        "submission_authority": "human",
        "delegation": "none"
      },
      "assurance_profile": {
        "id": "standard",
        "description": "Project-default assurance profile.",
        "obligation_ids": []
      },
      "interaction_rules": [],
      "compiled_obligations": [
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
          "id": "evidence-63a977ff7a335965a13a541abbb5b259",
          "obligation_ids": [
            "O-CHANGED-FILES"
          ],
          "affected_scope": [
            "docs/guide.md"
          ],
          "contribution_fingerprint": "60746c94ba0cedc1010f84cd5b296629d37b67f940292df43aaeab4661462ede",
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
          "id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
          "obligation_ids": [
            "O-SUMMARY"
          ],
          "affected_scope": [
            "docs/guide.md"
          ],
          "contribution_fingerprint": "60746c94ba0cedc1010f84cd5b296629d37b67f940292df43aaeab4661462ede",
          "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
          "evidence_type": "contribution_summary",
          "value": "本次贡献更新了认证模块的使用说明。",
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
      "verification_records": [],
      "findings": [],
      "repair_requests": [],
      "attempted_operations": [
        {
          "id": "attempted-operation-141c5c1825f65706ad3787e49ff221ce",
          "case_id": "unauthorized-agent",
          "operation": "verify_evidence",
          "actor": "contributor-agent",
          "actor_role": "contributor_agent",
          "attempted_at": "2026-07-26T00:00:00Z",
          "result": "denied",
          "reason_raw": "Role contributor_agent is not authorized for action verify_evidence",
          "state_before": "awaiting_maintainer_verification",
          "state_after": "awaiting_maintainer_verification",
          "state_changed": false,
          "required_roles": [
            "maintainer",
            "maintainer_verifier",
            "policy_steward"
          ]
        }
      ],
      "contribution_fingerprint": "60746c94ba0cedc1010f84cd5b296629d37b67f940292df43aaeab4661462ede",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "policy_snapshot": {
        "id": "policy-09b98729f0c95d56ae2d33d3e257dcb1",
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
          "id": "transition-c77ab972331f53338f79d0023aa05814",
          "case_id": "unauthorized-agent",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "case_opened",
          "target_state": "policy_resolved",
          "action": "resolve_policy",
          "reason": "Resolved canonical policy against the contribution.",
          "related_object_ids": [
            "policy-09b98729f0c95d56ae2d33d3e257dcb1"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-88c72d167b555327958927719ce12954",
          "case_id": "unauthorized-agent",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "policy_resolved",
          "target_state": "obligations_compiled",
          "action": "compile_obligations",
          "reason": "Compiled the union of matched, profile, and interaction obligations.",
          "related_object_ids": [
            "obl-o-changed-files",
            "obl-o-summary"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-3398fabaf05e5545add810d0fa006517",
          "case_id": "unauthorized-agent",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "obligations_compiled",
          "target_state": "evidence_incomplete",
          "action": "mark_evidence_state",
          "reason": "The new case has unsatisfied evidence obligations.",
          "related_object_ids": [
            "obl-o-changed-files",
            "obl-o-summary"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-3c7e885a30fc5b0b865fd5df1b530581",
          "case_id": "unauthorized-agent",
          "actor": "contributor-agent",
          "role": "contributor_agent",
          "source_state": "evidence_incomplete",
          "target_state": "awaiting_maintainer_verification",
          "action": "submit_for_verification",
          "reason": "Contributor submitted prepared evidence for maintainer verification.",
          "related_object_ids": [
            "evidence-63a977ff7a335965a13a541abbb5b259",
            "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        }
      ],
      "final_decision": null,
      "closure_receipt": null,
      "policy_migration_diagnostic": {
        "case_id": "unauthorized-agent",
        "policy_changed": false,
        "original_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
        "current_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
        "still_valid_obligations": [
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
      "reason": "贡献侧要求已经满足，当前轮到有权限的维护者检查；检查完成仍不等于接受。",
      "blocking_items": [],
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
          "O-CHANGED-FILES",
          "O-SUMMARY"
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
            "selector_token": "sel-05e2ed83b035677a3bbb8a8bf04ab683f1c574e757587f4be03471c89a96f948",
            "action": "verify_evidence",
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
                "evidence-63a977ff7a335965a13a541abbb5b259"
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
                "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-ad8a0478f7b8f97d7f43adeea0483a93d77f38fbbd813f2fee2df1435adc1aaf",
            "action": "verify_evidence",
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
                "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
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
                "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
                "relationship": "observed"
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
        "default_obligation_ids": [],
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
            "selector_token": "sel-301da2412a9809847ab6f316c9cc1880bb367cc482492234bcc4f7166d9ee7fc",
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
                "evidence-63a977ff7a335965a13a541abbb5b259"
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
                "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-73016056245d238a410c53c436950dfe44ae034faf23ddc9dba4f1af94e985ed",
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
                "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
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
                "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
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
            "selector_token": "sel-aa8a2cfebed39d031f0c7337d52ab0193b638030574b2fa6f5e5c56b4902250f",
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
              "evidence-63a977ff7a335965a13a541abbb5b259"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-63a977ff7a335965a13a541abbb5b259",
              "evidence_type": "changed_files"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-facfe421df4f1da7845fb3e27d591f0936970f547cc1611d5ef15b591257cd49",
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
              "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
              "evidence_type": "contribution_summary"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
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
        "default_obligation_ids": [],
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
            "selector_token": "sel-0532327c320a1b296a6f9c50a46f2f1fd8c87d6d78b53d3cadd8a81ad834eff0",
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
                "evidence-63a977ff7a335965a13a541abbb5b259"
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
                "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-6a60388bed5d4b03eab8f61725303866a181f324c0ed794daac4651140320f20",
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
                "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
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
                "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
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
        "default_obligation_ids": [],
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
            "selector_token": "sel-4fa031138877fe5a2835b589d20e0c36833657f889a045e0bf0bf9b77a7f5777",
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
                "evidence-63a977ff7a335965a13a541abbb5b259"
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
                "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-7ac60ee3a7cfb2ff98df510d8af06f7b0922df65a982b7edb3ae7fbcbb7cc48e",
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
                "evidence-e5d1ac324bcd53b2a28fc53cd521b65f"
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
                "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
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
        "output": "# 贡献者待办清单\n\n案例：unauthorized-agent\n当前责任方：维护者侧检查人员、项目规则负责人、人类维护者\n原因：贡献侧要求已经满足，当前轮到有权限的维护者检查；检查完成仍不等于接受。\n\n## 待处理项\n\n当前没有需要贡献侧补充或更新的材料。\n\n完成后请按当前 repair/提交范围交回；最终决定仍由人类维护者作出。",
        "trace_refs": [],
        "state_changing": false
      },
      {
        "action_id": "export_reviewer_summary",
        "label": "下载维护者摘要",
        "description": "导出当前风险、责任方和阻断项摘要，不作接受判断。",
        "output_type": "text/markdown",
        "output": "# 维护者审核摘要\n\n案例：unauthorized-agent\n当前状态：等待维护者检查\n风险：low\n当前责任方：维护者侧检查人员、项目规则负责人、人类维护者\n责任方依据：贡献侧要求已经满足，当前轮到有权限的维护者检查；检查完成仍不等于接受。\n\n## 阻断或待检查项\n\n- 当前没有阻断项。\n\n本摘要是治理状态说明，不是接受决定。",
        "trace_refs": [
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
            "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
            "relationship": "observed"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-summary",
            "relationship": "reference"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
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
        "output": "{\n  \"case_id\": \"unauthorized-agent\",\n  \"changed_files\": [\n    \"docs/guide.md\"\n  ],\n  \"matched_risk_rules\": [\n    {\n      \"rule_id\": \"documentation-low\",\n      \"zone\": \"documentation\",\n      \"affected_paths\": [\n        \"docs/guide.md\"\n      ]\n    }\n  ],\n  \"requirement_scopes\": {\n    \"O-CHANGED-FILES\": [\n      \"docs/guide.md\"\n    ],\n    \"O-SUMMARY\": [\n      \"docs/guide.md\"\n    ]\n  }\n}",
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
        "output": "案例 unauthorized-agent 当前交给：维护者侧检查人员、项目规则负责人、人类维护者。\n贡献侧要求已经满足，当前轮到有权限的维护者检查；检查完成仍不等于接受。\n完成后交给角色：人类维护者。",
        "trace_refs": [
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
            "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
            "relationship": "observed"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-summary",
            "relationship": "reference"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
            "relationship": "observed"
          }
        ],
        "state_changing": false
      }
    ],
    "materiality_declaration": null,
    "rejected_operation_notice": {
      "attempt_id": "attempted-operation-141c5c1825f65706ad3787e49ff221ce",
      "operation": "verify_evidence",
      "actor": "contributor-agent",
      "actor_role": "contributor_agent",
      "attempted_at": "2026-07-26T00:00:00Z",
      "result": "denied",
      "display_title": "最近一次操作未生效",
      "display_message": "贡献侧智能体尝试执行“检查提交材料”。",
      "reason_plain": "系统拒绝了该操作，因为这一操作必须由维护者侧角色执行。",
      "reason_raw": "Role contributor_agent is not authorized for action verify_evidence",
      "state_changed": false,
      "current_state": "awaiting_maintainer_verification",
      "current_state_label": "等待维护者检查",
      "required_roles": [
        "maintainer",
        "maintainer_verifier",
        "policy_steward"
      ],
      "trace_refs": [
        {
          "kind": "attempted_operation",
          "object_id": "attempted-operation-141c5c1825f65706ad3787e49ff221ce",
          "relationship": "denied_audit_event"
        }
      ]
    }
  },
  "trace_index": {
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
        "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
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
        "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
        "relationship": "observed"
      }
    ],
    "trace:automatic-check:material_version_binding": [
      {
        "kind": "evidence",
        "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
        "relationship": "material_version_binding"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
        "relationship": "material_version_binding"
      }
    ],
    "trace:automatic-check:test_command_and_result": [],
    "trace:automatic-check:test_version_binding": [],
    "trace:automatic-check:evidence_freshness": [
      {
        "kind": "evidence",
        "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
        "relationship": "evidence_freshness"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
        "relationship": "evidence_freshness"
      }
    ],
    "trace:automatic-check:attestation_version_binding": [],
    "trace:automatic-check:changed_file_scope_match": [],
    "trace:automatic-check:agent_involvement": [],
    "trace:automatic-check:recorded_delegation": [],
    "trace:automatic-check:authority_boundary": [
      {
        "kind": "attempted_operation",
        "object_id": "attempted-operation-141c5c1825f65706ad3787e49ff221ce",
        "relationship": "denied"
      }
    ],
    "trace:automatic-check:structural_obligations": [
      {
        "kind": "evidence",
        "object_id": "evidence-63a977ff7a335965a13a541abbb5b259",
        "relationship": "structural_obligations"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-e5d1ac324bcd53b2a28fc53cd521b65f",
        "relationship": "structural_obligations"
      }
    ]
  }
}
```

</details>
