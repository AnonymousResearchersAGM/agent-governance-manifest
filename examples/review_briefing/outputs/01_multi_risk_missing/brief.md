# AGM Maintainer Review Brief

## 1. 本次贡献与修改

### 本次贡献

贡献者说明：修改登录、认证或权限相关文件：demo_app/auth.py；调整配置、依赖或部署相关文件：demo_app/config.py

说明来源：系统根据已记录的变更路径归纳

系统根据文件和声明归纳：修改登录、认证或权限相关文件：demo_app/auth.py；调整配置、依赖或部署相关文件：demo_app/config.py

影响范围：

- 用户认证与权限控制
- 项目配置与依赖

可能的行为影响：

- 可能影响配置或部署兼容性
- 可能影响登录与身份认证路径

> 归纳边界：系统归纳只依据文件路径、已匹配风险区域和明确声明，不代表系统已经证明代码的真实语义或行为。

### 智能体与负责人

智能体使用：已记录智能体参与。

系统观察到的记录：

- 没有额外系统观察记录

智能体或贡献者声明：

- 尚未提供智能体行动与委派声明。

人类负责人确认：

- 尚未确认

尚未核验的推断边界：

- 能力范围来自治理配置或贡献者声明，不证明每项能力实际被使用。
- AGM 不把智能体自述当作系统观察事实，也不检测未披露的智能体使用。

## 2. 风险判断

综合风险：关键

为什么：

- demo_app/config.py 触发了“配置与依赖”风险范围。
- demo_app/auth.py 触发了“登录与身份认证”风险范围。

风险联动：

- 认证行为与配置同时变化，组合影响需要独立维护者检查。

因此需要独立维护者检查。

## 3. 项目要求和完成情况

项目要求 10 项治理材料或确认：

- ✕ 智能体行动与委派说明 — 缺少：当前没有可用于这项要求的材料。
- ✕ 可检查的测试输出或文件 — 缺少：当前没有可用于这项要求的材料。
- ✕ 登录、认证与权限影响说明 — 缺少：当前没有可用于这项要求的材料。
- ✕ 变更文件清单 — 缺少：当前没有可用于这项要求的材料。
- ○ 负责人确认 — 等待负责人确认：需要人类负责人确认自己已审阅当前版本和明确范围。
- ○ 独立维护者检查 — 等待独立维护者检查：需要与贡献侧分离的维护者完成独立检查；完成检查不等于接受。
- ✕ 已知限制 — 缺少：当前没有可用于这项要求的材料。
- ✕ 修改原因 — 缺少：当前没有可用于这项要求的材料。
- ✕ 修改说明 — 缺少：当前没有可用于这项要求的材料。
- ✕ 测试命令与结果 — 缺少：当前没有可用于这项要求的材料。

## 4. 系统已经确认

- ✓ 是否记录了智能体参与：治理案例明确记录为智能体参与路径。
  - 边界：AGM 只呈现治理记录和声明，不是智能体使用检测器。
- ✓ 是否存在越权操作：当前案例审计记录中没有被拒绝的越权操作。
  - 边界：结论范围仅限 AGM 已记录的操作。

## 5. 系统发现的问题

- ✕ 测试是否包含命令和结果：项目要求测试记录，但当前缺少完整的命令或结果。
- ✕ 负责人确认是否绑定当前版本：项目要求负责人确认，但当前没有绑定当前版本的有效确认。
- ✕ 声明范围与实际变更文件一致：尚未提供变更文件清单，系统无法完成一致性核对。
- ✕ 是否记录继续委派：智能体参与路径缺少行动与委派说明。
- ✕ 结构性项目要求是否满足：还有 9 项材料或负责人确认未达到当前要求。

### 系统无法判断，需要人检查

- ? 声明内容是否与实际修改一致：系统已完成结构和绑定检查，但以下内容仍需人类语义判断：独立维护者检查。
  - 边界：系统不会把文件路径推断、贡献者声明或智能体自述当作代码语义证明。

## 6. 现在需要你判断

当前没有额外 AGM 人类判断项。

请按“当前下一步”继续。

## 7. 当前下一步

### 当前不能进入维护者检查

缺少、过期或无效材料需要由贡献侧先处理。

当前责任方：贡献者或贡献侧智能体

系统会：

- 已把需要补充或更新的内容整理为贡献侧待办。
- 材料更新后重新核对版本绑定、有效期和结构要求。
- 保留未受影响且仍有效的材料。

人类现在应当：

- 维护者当前无需选择拒绝、退回或修复操作。
- 等待贡献侧补齐：智能体行动与委派说明、可检查的测试输出或文件、登录、认证与权限影响说明、变更文件清单、已知限制、修改原因、修改说明、测试命令与结果

> 系统确认、维护者检查完成或具备最终决定条件，都不等于贡献已被接受；最终接受、拒绝或合并决定仍由获授权的人类维护者作出。

<details>
<summary>8. 治理过程和技术详情</summary>

以下内容用于追溯治理状态、规则、义务、材料、问题、修复、状态变化和 fingerprint；普通审查工作不依赖先理解这些字段。

```json
{
  "case_id": "multi-risk-missing",
  "raw_state": "evidence_incomplete",
  "raw_readiness": "not_ready",
  "contribution_fingerprint": "e9bf2e6f68419187ca25503e78de5f29d0032fe013d4a59252b069d25e8bb261",
  "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
  "policy_snapshot": {
    "id": "policy-f5cedfe888295753a49e57b2eeae94c8",
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
      "id": "match-configuration-high",
      "rule_id": "configuration-high",
      "zone": "configuration",
      "risk_level": "high",
      "affected_paths": [
        "demo_app/config.py"
      ],
      "selector_reasons": [
        "path selectors matched: demo_app/config.py"
      ],
      "obligation_ids": [
        "O-SUMMARY",
        "O-CHANGED-FILES",
        "O-RATIONALE",
        "O-TEST-COMMAND",
        "O-ARTIFACT",
        "O-LIMITATIONS"
      ],
      "case_required": false,
      "source": "risk_rule",
      "obligation_overrides": {}
    },
    {
      "id": "match-authentication-critical",
      "rule_id": "authentication-critical",
      "zone": "authentication",
      "risk_level": "critical",
      "affected_paths": [
        "demo_app/auth.py"
      ],
      "selector_reasons": [
        "path selectors matched: demo_app/auth.py"
      ],
      "obligation_ids": [
        "O-SUMMARY",
        "O-CHANGED-FILES",
        "O-RATIONALE",
        "O-AUTH-IMPACT",
        "O-TEST-COMMAND",
        "O-ARTIFACT",
        "O-LIMITATIONS",
        "O-HUMAN-ATTEST"
      ],
      "case_required": true,
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
      "status": "unsatisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-artifact",
      "obligation_id": "O-ARTIFACT",
      "source_rule_ids": [
        "authentication-critical",
        "configuration-high"
      ],
      "type": "evidence",
      "severity": "high",
      "blocking": true,
      "verifier_roles": [
        "maintainer",
        "maintainer_verifier"
      ],
      "evidence_type": "artifact",
      "description": "Provide a locally checkable artifact or test output.",
      "affected_scope": [
        "demo_app/auth.py",
        "demo_app/config.py"
      ],
      "status": "unsatisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-auth-impact",
      "obligation_id": "O-AUTH-IMPACT",
      "source_rule_ids": [
        "authentication-critical"
      ],
      "type": "evidence",
      "severity": "critical",
      "blocking": true,
      "verifier_roles": [
        "maintainer",
        "maintainer_verifier"
      ],
      "evidence_type": "security_auth_impact",
      "description": "Describe security, authentication, and authorization impact.",
      "affected_scope": [
        "demo_app/auth.py"
      ],
      "status": "unsatisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-changed-files",
      "obligation_id": "O-CHANGED-FILES",
      "source_rule_ids": [
        "authentication-critical",
        "configuration-high"
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
        "demo_app/auth.py",
        "demo_app/config.py"
      ],
      "status": "unsatisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-human-attest",
      "obligation_id": "O-HUMAN-ATTEST",
      "source_rule_ids": [
        "authentication-critical"
      ],
      "type": "human_attestation",
      "severity": "critical",
      "blocking": true,
      "verifier_roles": [
        "accountable_human",
        "maintainer"
      ],
      "evidence_type": "human_attestation",
      "description": "Obtain explicit accountable-human attestation bound to the case.",
      "affected_scope": [
        "demo_app/auth.py"
      ],
      "status": "unsatisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-independent-review",
      "obligation_id": "O-INDEPENDENT-REVIEW",
      "source_rule_ids": [
        "authentication-configuration"
      ],
      "type": "maintainer_verification",
      "severity": "critical",
      "blocking": true,
      "verifier_roles": [
        "maintainer"
      ],
      "evidence_type": "independent_review",
      "description": "Require independent maintainer verification with separation of duty.",
      "affected_scope": [
        "demo_app/auth.py",
        "demo_app/config.py"
      ],
      "status": "unsatisfied",
      "interaction_ids": [
        "authentication-configuration"
      ]
    },
    {
      "id": "obl-o-limitations",
      "obligation_id": "O-LIMITATIONS",
      "source_rule_ids": [
        "authentication-critical",
        "configuration-high"
      ],
      "type": "evidence",
      "severity": "high",
      "blocking": true,
      "verifier_roles": [
        "maintainer",
        "maintainer_verifier"
      ],
      "evidence_type": "known_limitations",
      "description": "State known limitations or explicitly state none.",
      "affected_scope": [
        "demo_app/auth.py",
        "demo_app/config.py"
      ],
      "status": "unsatisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-rationale",
      "obligation_id": "O-RATIONALE",
      "source_rule_ids": [
        "authentication-critical",
        "configuration-high"
      ],
      "type": "evidence",
      "severity": "medium",
      "blocking": true,
      "verifier_roles": [
        "maintainer",
        "maintainer_verifier"
      ],
      "evidence_type": "rationale",
      "description": "Explain why the change is needed without disclosing private reasoning.",
      "affected_scope": [
        "demo_app/auth.py",
        "demo_app/config.py"
      ],
      "status": "unsatisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-summary",
      "obligation_id": "O-SUMMARY",
      "source_rule_ids": [
        "authentication-critical",
        "configuration-high"
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
        "demo_app/auth.py",
        "demo_app/config.py"
      ],
      "status": "unsatisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-test-command",
      "obligation_id": "O-TEST-COMMAND",
      "source_rule_ids": [
        "authentication-critical",
        "configuration-high"
      ],
      "type": "evidence",
      "severity": "high",
      "blocking": true,
      "verifier_roles": [
        "maintainer",
        "maintainer_verifier"
      ],
      "evidence_type": "test_command",
      "description": "Provide a concrete test command, environment, and outcome.",
      "affected_scope": [
        "demo_app/auth.py",
        "demo_app/config.py"
      ],
      "status": "unsatisfied",
      "interaction_ids": []
    }
  ],
  "evidence_records": [],
  "attestation_records": [],
  "findings": [],
  "repair_requests": [],
  "attempted_operations": [],
  "verification_records": [],
  "transition_history": [
    {
      "id": "transition-9ed5f98de82e5bfe85d3e06792eaae4d",
      "case_id": "multi-risk-missing",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "case_opened",
      "target_state": "policy_resolved",
      "action": "resolve_policy",
      "reason": "Resolved canonical policy against the contribution.",
      "related_object_ids": [
        "policy-f5cedfe888295753a49e57b2eeae94c8"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-ed268ca69bf85494a89aa2cc5301464a",
      "case_id": "multi-risk-missing",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "policy_resolved",
      "target_state": "obligations_compiled",
      "action": "compile_obligations",
      "reason": "Compiled the union of matched, profile, and interaction obligations.",
      "related_object_ids": [
        "obl-o-agent-scope",
        "obl-o-artifact",
        "obl-o-auth-impact",
        "obl-o-changed-files",
        "obl-o-human-attest",
        "obl-o-independent-review",
        "obl-o-limitations",
        "obl-o-rationale",
        "obl-o-summary",
        "obl-o-test-command"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-9080364f5b2058b3ac966e1467c54d2e",
      "case_id": "multi-risk-missing",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "obligations_compiled",
      "target_state": "evidence_incomplete",
      "action": "mark_evidence_state",
      "reason": "The new case has unsatisfied evidence obligations.",
      "related_object_ids": [
        "obl-o-agent-scope",
        "obl-o-artifact",
        "obl-o-auth-impact",
        "obl-o-changed-files",
        "obl-o-limitations",
        "obl-o-rationale",
        "obl-o-summary",
        "obl-o-test-command"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    }
  ],
  "final_decision": null,
  "closure_receipt": null,
  "policy_migration_diagnostic": {
    "case_id": "multi-risk-missing",
    "policy_changed": false,
    "original_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
    "current_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
    "still_valid_obligations": [
      "O-AGENT-SCOPE",
      "O-ARTIFACT",
      "O-AUTH-IMPACT",
      "O-CHANGED-FILES",
      "O-HUMAN-ATTEST",
      "O-INDEPENDENT-REVIEW",
      "O-LIMITATIONS",
      "O-RATIONALE",
      "O-SUMMARY",
      "O-TEST-COMMAND"
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
    "generated_from_case_fingerprint": "e9bf2e6f68419187ca25503e78de5f29d0032fe013d4a59252b069d25e8bb261",
    "actor": {
      "actor": "human-maintainer",
      "role": "maintainer",
      "human": true
    },
    "summary": {
      "case_id": "multi-risk-missing",
      "changed_files": [
        "demo_app/auth.py",
        "demo_app/config.py"
      ],
      "risk_level": "critical",
      "risk_areas": [
        "登录与认证（authentication）",
        "配置（configuration）"
      ],
      "autonomy_profile": "supervised_agent",
      "path_kind": "full",
      "path_label": "完整治理流程",
      "current_stage": "等待贡献侧补齐或更新材料",
      "blocking_issue_count": 8,
      "warning_count": 0,
      "current_responsible_parties": [
        "人类贡献者",
        "贡献侧智能体"
      ],
      "next_authorized_actor_roles": [
        "contributor",
        "contributor_agent"
      ],
      "raw_state": "evidence_incomplete",
      "raw_readiness": "not_ready"
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
            "object_id": "transition-9ed5f98de82e5bfe85d3e06792eaae4d",
            "relationship": "primary:resolve_policy"
          },
          {
            "kind": "state_transition",
            "object_id": "transition-ed268ca69bf85494a89aa2cc5301464a",
            "relationship": "primary:compile_obligations"
          },
          {
            "kind": "matched_rule",
            "object_id": "match-configuration-high",
            "relationship": "risk_matching"
          },
          {
            "kind": "matched_rule",
            "object_id": "match-authentication-critical",
            "relationship": "risk_matching"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-agent-scope",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-artifact",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-auth-impact",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-changed-files",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-human-attest",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-independent-review",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-limitations",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-rationale",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-summary",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-test-command",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "interaction_rule",
            "object_id": "authentication-configuration",
            "relationship": "interaction_matching"
          }
        ]
      },
      {
        "number": 2,
        "step_id": "prepare_materials",
        "title": "贡献者准备材料",
        "status": "current",
        "status_label": "当前阶段",
        "symbol": "●",
        "explanation": "贡献者正在准备或补齐本次所需材料。",
        "internal_stages": [
          "Bind",
          "Repair"
        ],
        "traceability": [
          {
            "kind": "state_transition",
            "object_id": "transition-9080364f5b2058b3ac966e1467c54d2e",
            "relationship": "primary:mark_evidence_state"
          }
        ]
      },
      {
        "number": 3,
        "step_id": "accountable_confirmation",
        "title": "负责人确认",
        "status": "pending",
        "status_label": "尚未开始",
        "symbol": "○",
        "explanation": "材料准备完成后才进入负责人确认。",
        "internal_stages": [
          "Attest"
        ],
        "traceability": []
      },
      {
        "number": 4,
        "step_id": "maintainer_check",
        "title": "维护者检查",
        "status": "pending",
        "status_label": "尚未开始",
        "symbol": "○",
        "explanation": "贡献侧要求完成后才进入维护者检查。",
        "internal_stages": [
          "Verify",
          "Repair"
        ],
        "traceability": []
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
        "obligation_id": "O-AGENT-SCOPE",
        "check_item": "智能体行动与委派说明",
        "project_requirement": "说明智能体做了什么、用了哪些权限、是否有人监督，以及是否把具有独立行动能力的工作继续交给了另一个智能体。",
        "current_situation": "尚未提供。",
        "result": "missing",
        "result_label": "缺少",
        "raw_status": "unsatisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "autonomy:supervised_agent"
        ],
        "interaction_ids": [],
        "evidence_ids": [],
        "binding_fingerprints": [],
        "finding_ids": [],
        "reference_english": "Record the declared action, permissions, supervision, and delegation scope.",
        "observed_english": "no bound evidence record",
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
          }
        ],
        "display_name": "智能体行动与委派说明",
        "reference_plain": "说明智能体做了什么、用了哪些权限、是否有人监督，以及是否把具有独立行动能力的工作继续交给了另一个智能体。",
        "observed_plain": "尚未提供。",
        "observed_raw": "no bound evidence record",
        "material_status": "missing",
        "material_status_label": "缺少",
        "workflow_status": "awaiting_contributor",
        "workflow_status_label": "等待贡献者处理",
        "currently_blocks_progression": true,
        "affected_scope": []
      },
      {
        "obligation_id": "O-ARTIFACT",
        "check_item": "可检查的测试输出或文件",
        "project_requirement": "提供可以实际检查的测试输出或文件。",
        "current_situation": "尚未提供。",
        "result": "missing",
        "result_label": "缺少",
        "raw_status": "unsatisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "authentication-critical",
          "configuration-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [],
        "binding_fingerprints": [],
        "finding_ids": [],
        "reference_english": "Provide a locally checkable artifact or test output.",
        "observed_english": "no bound evidence record",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-artifact",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-critical",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "configuration-high",
            "relationship": "source"
          }
        ],
        "display_name": "可检查的测试输出或文件",
        "reference_plain": "提供可以实际检查的测试输出或文件。",
        "observed_plain": "尚未提供。",
        "observed_raw": "no bound evidence record",
        "material_status": "missing",
        "material_status_label": "缺少",
        "workflow_status": "awaiting_contributor",
        "workflow_status_label": "等待贡献者处理",
        "currently_blocks_progression": true,
        "affected_scope": [
          "demo_app/auth.py",
          "demo_app/config.py"
        ]
      },
      {
        "obligation_id": "O-AUTH-IMPACT",
        "check_item": "登录、认证与权限影响说明",
        "project_requirement": "说明本次修改是否改变登录、认证或权限行为。",
        "current_situation": "尚未提供。",
        "result": "missing",
        "result_label": "缺少",
        "raw_status": "unsatisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "authentication-critical"
        ],
        "interaction_ids": [],
        "evidence_ids": [],
        "binding_fingerprints": [],
        "finding_ids": [],
        "reference_english": "Describe security, authentication, and authorization impact.",
        "observed_english": "no bound evidence record",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-auth-impact",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-critical",
            "relationship": "source"
          }
        ],
        "display_name": "登录、认证与权限影响说明",
        "reference_plain": "说明本次修改是否改变登录、认证或权限行为。",
        "observed_plain": "尚未提供。",
        "observed_raw": "no bound evidence record",
        "material_status": "missing",
        "material_status_label": "缺少",
        "workflow_status": "awaiting_contributor",
        "workflow_status_label": "等待贡献者处理",
        "currently_blocks_progression": true,
        "affected_scope": [
          "demo_app/auth.py"
        ]
      },
      {
        "obligation_id": "O-CHANGED-FILES",
        "check_item": "变更文件清单",
        "project_requirement": "列出这次修改涉及的文件和范围。",
        "current_situation": "尚未提供。",
        "result": "missing",
        "result_label": "缺少",
        "raw_status": "unsatisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "authentication-critical",
          "configuration-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [],
        "binding_fingerprints": [],
        "finding_ids": [],
        "reference_english": "Identify the files and scopes covered by the contribution.",
        "observed_english": "no bound evidence record",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-changed-files",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-critical",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "configuration-high",
            "relationship": "source"
          }
        ],
        "display_name": "变更文件清单",
        "reference_plain": "列出这次修改涉及的文件和范围。",
        "observed_plain": "尚未提供。",
        "observed_raw": "no bound evidence record",
        "material_status": "missing",
        "material_status_label": "缺少",
        "workflow_status": "awaiting_contributor",
        "workflow_status_label": "等待贡献者处理",
        "currently_blocks_progression": true,
        "affected_scope": [
          "demo_app/auth.py",
          "demo_app/config.py"
        ]
      },
      {
        "obligation_id": "O-HUMAN-ATTEST",
        "check_item": "负责人确认",
        "project_requirement": "由负责人确认自己审阅了当前代码版本、材料和明确范围。",
        "current_situation": "尚未到负责人确认阶段。",
        "result": "not_started",
        "result_label": "尚未进行",
        "raw_status": "unsatisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "authentication-critical"
        ],
        "interaction_ids": [],
        "evidence_ids": [],
        "binding_fingerprints": [],
        "finding_ids": [],
        "reference_english": "Obtain explicit accountable-human attestation bound to the case.",
        "observed_english": "attestation stage not reached",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-human-attest",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-critical",
            "relationship": "source"
          }
        ],
        "display_name": "负责人确认",
        "reference_plain": "由负责人确认自己审阅了当前代码版本、材料和明确范围。",
        "observed_plain": "尚未到负责人确认阶段。",
        "observed_raw": "attestation stage not reached",
        "material_status": "missing",
        "material_status_label": "缺少",
        "workflow_status": "awaiting_attestation",
        "workflow_status_label": "等待负责人确认",
        "currently_blocks_progression": false,
        "affected_scope": [
          "demo_app/auth.py"
        ]
      },
      {
        "obligation_id": "O-INDEPENDENT-REVIEW",
        "check_item": "独立维护者检查",
        "project_requirement": "由另一名具备权限且与贡献侧分离的维护者独立检查。",
        "current_situation": "尚未到独立维护者检查阶段。",
        "result": "not_started",
        "result_label": "尚未进行",
        "raw_status": "unsatisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "authentication-configuration"
        ],
        "interaction_ids": [
          "authentication-configuration"
        ],
        "evidence_ids": [],
        "binding_fingerprints": [],
        "finding_ids": [],
        "reference_english": "Require independent maintainer verification with separation of duty.",
        "observed_english": "independent maintainer verification not recorded",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-independent-review",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-configuration",
            "relationship": "source"
          },
          {
            "kind": "interaction_rule",
            "object_id": "authentication-configuration",
            "relationship": "source"
          }
        ],
        "display_name": "独立维护者检查",
        "reference_plain": "由另一名具备权限且与贡献侧分离的维护者独立检查。",
        "observed_plain": "尚未到独立维护者检查阶段。",
        "observed_raw": "independent maintainer verification not recorded",
        "material_status": "missing",
        "material_status_label": "缺少",
        "workflow_status": "blocks_progression",
        "workflow_status_label": "阻止继续",
        "currently_blocks_progression": false,
        "affected_scope": [
          "demo_app/auth.py",
          "demo_app/config.py"
        ]
      },
      {
        "obligation_id": "O-LIMITATIONS",
        "check_item": "已知限制",
        "project_requirement": "说明已知限制；没有已知限制也要明确说明。",
        "current_situation": "尚未提供。",
        "result": "missing",
        "result_label": "缺少",
        "raw_status": "unsatisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "authentication-critical",
          "configuration-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [],
        "binding_fingerprints": [],
        "finding_ids": [],
        "reference_english": "State known limitations or explicitly state none.",
        "observed_english": "no bound evidence record",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-limitations",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-critical",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "configuration-high",
            "relationship": "source"
          }
        ],
        "display_name": "已知限制",
        "reference_plain": "说明已知限制；没有已知限制也要明确说明。",
        "observed_plain": "尚未提供。",
        "observed_raw": "no bound evidence record",
        "material_status": "missing",
        "material_status_label": "缺少",
        "workflow_status": "awaiting_contributor",
        "workflow_status_label": "等待贡献者处理",
        "currently_blocks_progression": true,
        "affected_scope": [
          "demo_app/auth.py",
          "demo_app/config.py"
        ]
      },
      {
        "obligation_id": "O-RATIONALE",
        "check_item": "修改原因",
        "project_requirement": "说明为什么需要这次修改。",
        "current_situation": "尚未提供。",
        "result": "missing",
        "result_label": "缺少",
        "raw_status": "unsatisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "authentication-critical",
          "configuration-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [],
        "binding_fingerprints": [],
        "finding_ids": [],
        "reference_english": "Explain why the change is needed without disclosing private reasoning.",
        "observed_english": "no bound evidence record",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-rationale",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-critical",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "configuration-high",
            "relationship": "source"
          }
        ],
        "display_name": "修改原因",
        "reference_plain": "说明为什么需要这次修改。",
        "observed_plain": "尚未提供。",
        "observed_raw": "no bound evidence record",
        "material_status": "missing",
        "material_status_label": "缺少",
        "workflow_status": "awaiting_contributor",
        "workflow_status_label": "等待贡献者处理",
        "currently_blocks_progression": true,
        "affected_scope": [
          "demo_app/auth.py",
          "demo_app/config.py"
        ]
      },
      {
        "obligation_id": "O-SUMMARY",
        "check_item": "修改说明",
        "project_requirement": "简要说明这次修改做了什么。",
        "current_situation": "尚未提供。",
        "result": "missing",
        "result_label": "缺少",
        "raw_status": "unsatisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "authentication-critical",
          "configuration-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [],
        "binding_fingerprints": [],
        "finding_ids": [],
        "reference_english": "Provide a concise factual contribution summary.",
        "observed_english": "no bound evidence record",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-summary",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-critical",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "configuration-high",
            "relationship": "source"
          }
        ],
        "display_name": "修改说明",
        "reference_plain": "简要说明这次修改做了什么。",
        "observed_plain": "尚未提供。",
        "observed_raw": "no bound evidence record",
        "material_status": "missing",
        "material_status_label": "缺少",
        "workflow_status": "awaiting_contributor",
        "workflow_status_label": "等待贡献者处理",
        "currently_blocks_progression": true,
        "affected_scope": [
          "demo_app/auth.py",
          "demo_app/config.py"
        ]
      },
      {
        "obligation_id": "O-TEST-COMMAND",
        "check_item": "测试命令与结果",
        "project_requirement": "提供测试命令、运行环境和实际结果。",
        "current_situation": "尚未提供。",
        "result": "missing",
        "result_label": "缺少",
        "raw_status": "unsatisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "authentication-critical",
          "configuration-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [],
        "binding_fingerprints": [],
        "finding_ids": [],
        "reference_english": "Provide a concrete test command, environment, and outcome.",
        "observed_english": "no bound evidence record",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-test-command",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-critical",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "configuration-high",
            "relationship": "source"
          }
        ],
        "display_name": "测试命令与结果",
        "reference_plain": "提供测试命令、运行环境和实际结果。",
        "observed_plain": "尚未提供。",
        "observed_raw": "no bound evidence record",
        "material_status": "missing",
        "material_status_label": "缺少",
        "workflow_status": "awaiting_contributor",
        "workflow_status_label": "等待贡献者处理",
        "currently_blocks_progression": true,
        "affected_scope": [
          "demo_app/auth.py",
          "demo_app/config.py"
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
            "object_id": "evidence_incomplete:record_policy_conflict:repair_requested",
            "relationship": "transition"
          }
        ],
        "relevance": "secondary",
        "group": "other_available",
        "primary_reason": "后端允许此操作，但它不直接处理当前主要阻断项。",
        "selector_options": [
          {
            "selector_token": "sel-d72ffd4814be3b7a07b610082832f0657713870e73b66bbfe81913e713b4e91f",
            "action": "record_policy_conflict",
            "label": "智能体行动与委派说明",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [],
            "obligation_ids": [
              "O-AGENT-SCOPE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-AGENT-SCOPE"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-AGENT-SCOPE",
              "evidence_ids": [],
              "finding_ids": []
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
              }
            ]
          },
          {
            "selector_token": "sel-358daaa9b0c9e1483b94a970419c039c2db3d8223c1e93c339df1824d3d5b51e",
            "action": "record_policy_conflict",
            "label": "可检查的测试输出或文件",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-ARTIFACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-ARTIFACT"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-ARTIFACT",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-artifact",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-critical",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "configuration-high",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-1ba1d34d839f78c41f0b06828b4526e9c26631953ab147e6fb4d4448aaa03d15",
            "action": "record_policy_conflict",
            "label": "登录、认证与权限影响说明",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py"
            ],
            "obligation_ids": [
              "O-AUTH-IMPACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-AUTH-IMPACT"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-AUTH-IMPACT",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-auth-impact",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-critical",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-4dd8137617b48a4a08c73a6f1ac40fe6bf8a7979fb73e3a2fdf156841e28047f",
            "action": "record_policy_conflict",
            "label": "变更文件清单",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-CHANGED-FILES"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-CHANGED-FILES"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-CHANGED-FILES",
              "evidence_ids": [],
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
                "object_id": "authentication-critical",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "configuration-high",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-7a3164cc9fb350147a1bc270ebaa51e007b479d0d1be3a10d1b85c2d370d2710",
            "action": "record_policy_conflict",
            "label": "负责人确认",
            "status_label": "缺少；等待负责人确认",
            "affected_scope": [
              "demo_app/auth.py"
            ],
            "obligation_ids": [
              "O-HUMAN-ATTEST"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-HUMAN-ATTEST"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_attestation",
            "technical_details": {
              "obligation_id": "O-HUMAN-ATTEST",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-human-attest",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-critical",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-9a5770bf324a4329d37ec6d4c61b05a758bc65cf97dca3f3096afab23d4b0fb3",
            "action": "record_policy_conflict",
            "label": "独立维护者检查",
            "status_label": "缺少；阻止继续",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-INDEPENDENT-REVIEW"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-INDEPENDENT-REVIEW"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "blocks_progression",
            "technical_details": {
              "obligation_id": "O-INDEPENDENT-REVIEW",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-independent-review",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-configuration",
                "relationship": "source"
              },
              {
                "kind": "interaction_rule",
                "object_id": "authentication-configuration",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-0502b1424e2b74ff3de9799d5ea841aff57ab2cbf6d1f87f42ab2e25b6e9469d",
            "action": "record_policy_conflict",
            "label": "已知限制",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-LIMITATIONS"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-LIMITATIONS"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-LIMITATIONS",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-limitations",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-critical",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "configuration-high",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-1f1a03634afa3ef0c4f5b8b5ebbd18a03c94a4c154cfd44b33e64876dbdb7b52",
            "action": "record_policy_conflict",
            "label": "修改原因",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-RATIONALE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-RATIONALE"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-RATIONALE",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-rationale",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-critical",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "configuration-high",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-72fd0673de38d47762b249b5c39482b13c484e54124ecfd34e9dfd3b563e0b26",
            "action": "record_policy_conflict",
            "label": "修改说明",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-SUMMARY"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-SUMMARY"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-SUMMARY",
              "evidence_ids": [],
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
                "object_id": "authentication-critical",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "configuration-high",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-4a49e0e1ebbb02dab1fce7ce2d4340f202fa234b9b18e212265a605468b9095b",
            "action": "record_policy_conflict",
            "label": "测试命令与结果",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-TEST-COMMAND"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-TEST-COMMAND"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-TEST-COMMAND",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-test-command",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-critical",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "configuration-high",
                "relationship": "source"
              }
            ]
          }
        ]
      }
    ],
    "unavailable_actions": [
      {
        "action": "verify_evidence",
        "title": "检查提交材料",
        "description": "记录维护者对指定项目要求及其绑定材料的检查结果。",
        "reason": "当前处于“等待贡献者补齐材料”，还不能执行“检查提交材料”。",
        "next_actor_roles": [
          "contributor",
          "contributor_agent"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:verify_evidence",
            "relationship": "authority"
          }
        ],
        "category": "authority",
        "required_role": [
          "maintainer",
          "maintainer_verifier",
          "policy_steward"
        ],
        "required_state": [
          "awaiting_maintainer_verification",
          "resubmitted"
        ],
        "future_availability": "到达所需状态且对象范围满足后可能可用。"
      },
      {
        "action": "request_repair",
        "title": "要求补充或修改",
        "description": "指出问题和受影响义务，返回贡献侧修复。",
        "reason": "当前处于“等待贡献者补齐材料”，还不能执行“要求补充或修改”。",
        "next_actor_roles": [
          "contributor",
          "contributor_agent"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:request_repair",
            "relationship": "authority"
          }
        ],
        "category": "authority",
        "required_role": [
          "maintainer",
          "maintainer_verifier",
          "policy_steward"
        ],
        "required_state": [
          "awaiting_maintainer_verification",
          "ready_for_human_decision",
          "verification_complete"
        ],
        "future_availability": "到达所需状态且对象范围满足后可能可用。"
      },
      {
        "action": "reject_evidence",
        "title": "拒绝当前材料",
        "description": "拒绝一条不能支持当前修改的具体材料。",
        "reason": "当前处于“等待贡献者补齐材料”，还不能执行“拒绝当前材料”。",
        "next_actor_roles": [
          "contributor",
          "contributor_agent"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:reject_evidence",
            "relationship": "authority"
          }
        ],
        "category": "authority",
        "required_role": [
          "maintainer",
          "maintainer_verifier"
        ],
        "required_state": [
          "awaiting_maintainer_verification",
          "verification_complete"
        ],
        "future_availability": "到达所需状态且对象范围满足后可能可用。"
      },
      {
        "action": "ask_clarification",
        "title": "请求补充说明",
        "description": "针对指定要求提出可审计的澄清问题。",
        "reason": "当前处于“等待贡献者补齐材料”，还不能执行“请求补充说明”。",
        "next_actor_roles": [
          "contributor",
          "contributor_agent"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:ask_clarification",
            "relationship": "authority"
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
        "action": "invalidate_attestation",
        "title": "将旧负责人确认标记为失效",
        "description": "使一条过时或不正确的负责人确认失效。",
        "reason": "当前处于“等待贡献者补齐材料”，还不能执行“将旧负责人确认标记为失效”。",
        "next_actor_roles": [
          "contributor",
          "contributor_agent"
        ],
        "mutates_state": true,
        "traceability": [
          {
            "kind": "permission_rule",
            "object_id": "maintainer:invalidate_attestation",
            "relationship": "authority"
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
        "reason": "当前处于“等待贡献者补齐材料”，还不能执行“处理项目规则冲突”。",
        "next_actor_roles": [
          "contributor",
          "contributor_agent"
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
          },
          {
            "kind": "state_machine_rule",
            "object_id": "evidence_incomplete:confirm_attestation:awaiting_maintainer_verification",
            "relationship": "transition"
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
        "reason": "当前处于“等待贡献者补齐材料”，还不能执行“由有权维护者执行覆盖处理”。",
        "next_actor_roles": [
          "contributor",
          "contributor_agent"
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
        "reason": "当前处于“等待贡献者补齐材料”，还不能执行“最终接受”。",
        "next_actor_roles": [
          "contributor",
          "contributor_agent"
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
        "reason": "当前处于“等待贡献者补齐材料”，还不能执行“最终拒绝”。",
        "next_actor_roles": [
          "contributor",
          "contributor_agent"
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
        "reason": "当前处于“等待贡献者补齐材料”，还不能执行“要求继续修改”。",
        "next_actor_roles": [
          "contributor",
          "contributor_agent"
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
        "reason": "当前处于“等待贡献者补齐材料”，还不能执行“关闭本次审核记录”。",
        "next_actor_roles": [
          "contributor",
          "contributor_agent"
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
    "explanations": [],
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
      "raw_state": "evidence_incomplete",
      "readiness": "not_ready",
      "risk_rules": [
        {
          "id": "match-configuration-high",
          "rule_id": "configuration-high",
          "zone": "configuration",
          "risk_level": "high",
          "affected_paths": [
            "demo_app/config.py"
          ],
          "selector_reasons": [
            "path selectors matched: demo_app/config.py"
          ],
          "obligation_ids": [
            "O-SUMMARY",
            "O-CHANGED-FILES",
            "O-RATIONALE",
            "O-TEST-COMMAND",
            "O-ARTIFACT",
            "O-LIMITATIONS"
          ],
          "case_required": false,
          "source": "risk_rule",
          "obligation_overrides": {}
        },
        {
          "id": "match-authentication-critical",
          "rule_id": "authentication-critical",
          "zone": "authentication",
          "risk_level": "critical",
          "affected_paths": [
            "demo_app/auth.py"
          ],
          "selector_reasons": [
            "path selectors matched: demo_app/auth.py"
          ],
          "obligation_ids": [
            "O-SUMMARY",
            "O-CHANGED-FILES",
            "O-RATIONALE",
            "O-AUTH-IMPACT",
            "O-TEST-COMMAND",
            "O-ARTIFACT",
            "O-LIMITATIONS",
            "O-HUMAN-ATTEST"
          ],
          "case_required": true,
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
      "interaction_rules": [
        {
          "id": "authentication-configuration",
          "all_rule_ids": [
            "authentication-critical",
            "configuration-high"
          ],
          "risk_level": "critical",
          "obligation_ids": [
            "O-INDEPENDENT-REVIEW"
          ],
          "separation_of_duty": true,
          "description": "Authentication behavior and deployment/dependency configuration interact."
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
          "status": "unsatisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-artifact",
          "obligation_id": "O-ARTIFACT",
          "source_rule_ids": [
            "authentication-critical",
            "configuration-high"
          ],
          "type": "evidence",
          "severity": "high",
          "blocking": true,
          "verifier_roles": [
            "maintainer",
            "maintainer_verifier"
          ],
          "evidence_type": "artifact",
          "description": "Provide a locally checkable artifact or test output.",
          "affected_scope": [
            "demo_app/auth.py",
            "demo_app/config.py"
          ],
          "status": "unsatisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-auth-impact",
          "obligation_id": "O-AUTH-IMPACT",
          "source_rule_ids": [
            "authentication-critical"
          ],
          "type": "evidence",
          "severity": "critical",
          "blocking": true,
          "verifier_roles": [
            "maintainer",
            "maintainer_verifier"
          ],
          "evidence_type": "security_auth_impact",
          "description": "Describe security, authentication, and authorization impact.",
          "affected_scope": [
            "demo_app/auth.py"
          ],
          "status": "unsatisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-changed-files",
          "obligation_id": "O-CHANGED-FILES",
          "source_rule_ids": [
            "authentication-critical",
            "configuration-high"
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
            "demo_app/auth.py",
            "demo_app/config.py"
          ],
          "status": "unsatisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-human-attest",
          "obligation_id": "O-HUMAN-ATTEST",
          "source_rule_ids": [
            "authentication-critical"
          ],
          "type": "human_attestation",
          "severity": "critical",
          "blocking": true,
          "verifier_roles": [
            "accountable_human",
            "maintainer"
          ],
          "evidence_type": "human_attestation",
          "description": "Obtain explicit accountable-human attestation bound to the case.",
          "affected_scope": [
            "demo_app/auth.py"
          ],
          "status": "unsatisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-independent-review",
          "obligation_id": "O-INDEPENDENT-REVIEW",
          "source_rule_ids": [
            "authentication-configuration"
          ],
          "type": "maintainer_verification",
          "severity": "critical",
          "blocking": true,
          "verifier_roles": [
            "maintainer"
          ],
          "evidence_type": "independent_review",
          "description": "Require independent maintainer verification with separation of duty.",
          "affected_scope": [
            "demo_app/auth.py",
            "demo_app/config.py"
          ],
          "status": "unsatisfied",
          "interaction_ids": [
            "authentication-configuration"
          ]
        },
        {
          "id": "obl-o-limitations",
          "obligation_id": "O-LIMITATIONS",
          "source_rule_ids": [
            "authentication-critical",
            "configuration-high"
          ],
          "type": "evidence",
          "severity": "high",
          "blocking": true,
          "verifier_roles": [
            "maintainer",
            "maintainer_verifier"
          ],
          "evidence_type": "known_limitations",
          "description": "State known limitations or explicitly state none.",
          "affected_scope": [
            "demo_app/auth.py",
            "demo_app/config.py"
          ],
          "status": "unsatisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-rationale",
          "obligation_id": "O-RATIONALE",
          "source_rule_ids": [
            "authentication-critical",
            "configuration-high"
          ],
          "type": "evidence",
          "severity": "medium",
          "blocking": true,
          "verifier_roles": [
            "maintainer",
            "maintainer_verifier"
          ],
          "evidence_type": "rationale",
          "description": "Explain why the change is needed without disclosing private reasoning.",
          "affected_scope": [
            "demo_app/auth.py",
            "demo_app/config.py"
          ],
          "status": "unsatisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-summary",
          "obligation_id": "O-SUMMARY",
          "source_rule_ids": [
            "authentication-critical",
            "configuration-high"
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
            "demo_app/auth.py",
            "demo_app/config.py"
          ],
          "status": "unsatisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-test-command",
          "obligation_id": "O-TEST-COMMAND",
          "source_rule_ids": [
            "authentication-critical",
            "configuration-high"
          ],
          "type": "evidence",
          "severity": "high",
          "blocking": true,
          "verifier_roles": [
            "maintainer",
            "maintainer_verifier"
          ],
          "evidence_type": "test_command",
          "description": "Provide a concrete test command, environment, and outcome.",
          "affected_scope": [
            "demo_app/auth.py",
            "demo_app/config.py"
          ],
          "status": "unsatisfied",
          "interaction_ids": []
        }
      ],
      "evidence_records": [],
      "attestation_records": [],
      "verification_records": [],
      "findings": [],
      "repair_requests": [],
      "attempted_operations": [],
      "contribution_fingerprint": "e9bf2e6f68419187ca25503e78de5f29d0032fe013d4a59252b069d25e8bb261",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "policy_snapshot": {
        "id": "policy-f5cedfe888295753a49e57b2eeae94c8",
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
          "id": "transition-9ed5f98de82e5bfe85d3e06792eaae4d",
          "case_id": "multi-risk-missing",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "case_opened",
          "target_state": "policy_resolved",
          "action": "resolve_policy",
          "reason": "Resolved canonical policy against the contribution.",
          "related_object_ids": [
            "policy-f5cedfe888295753a49e57b2eeae94c8"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-ed268ca69bf85494a89aa2cc5301464a",
          "case_id": "multi-risk-missing",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "policy_resolved",
          "target_state": "obligations_compiled",
          "action": "compile_obligations",
          "reason": "Compiled the union of matched, profile, and interaction obligations.",
          "related_object_ids": [
            "obl-o-agent-scope",
            "obl-o-artifact",
            "obl-o-auth-impact",
            "obl-o-changed-files",
            "obl-o-human-attest",
            "obl-o-independent-review",
            "obl-o-limitations",
            "obl-o-rationale",
            "obl-o-summary",
            "obl-o-test-command"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-9080364f5b2058b3ac966e1467c54d2e",
          "case_id": "multi-risk-missing",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "obligations_compiled",
          "target_state": "evidence_incomplete",
          "action": "mark_evidence_state",
          "reason": "The new case has unsatisfied evidence obligations.",
          "related_object_ids": [
            "obl-o-agent-scope",
            "obl-o-artifact",
            "obl-o-auth-impact",
            "obl-o-changed-files",
            "obl-o-limitations",
            "obl-o-rationale",
            "obl-o-summary",
            "obl-o-test-command"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        }
      ],
      "final_decision": null,
      "closure_receipt": null,
      "policy_migration_diagnostic": {
        "case_id": "multi-risk-missing",
        "policy_changed": false,
        "original_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
        "current_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
        "still_valid_obligations": [
          "O-AGENT-SCOPE",
          "O-ARTIFACT",
          "O-AUTH-IMPACT",
          "O-CHANGED-FILES",
          "O-HUMAN-ATTEST",
          "O-INDEPENDENT-REVIEW",
          "O-LIMITATIONS",
          "O-RATIONALE",
          "O-SUMMARY",
          "O-TEST-COMMAND"
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
          "O-ARTIFACT": "Provide a locally checkable artifact or test output.",
          "O-AUTH-IMPACT": "Describe security, authentication, and authorization impact.",
          "O-CHANGED-FILES": "Identify the files and scopes covered by the contribution.",
          "O-HUMAN-ATTEST": "Obtain explicit accountable-human attestation bound to the case.",
          "O-INDEPENDENT-REVIEW": "Require independent maintainer verification with separation of duty.",
          "O-LIMITATIONS": "State known limitations or explicitly state none.",
          "O-RATIONALE": "Explain why the change is needed without disclosing private reasoning.",
          "O-SUMMARY": "Provide a concise factual contribution summary.",
          "O-TEST-COMMAND": "Provide a concrete test command, environment, and outcome."
        },
        "matched_rule_reasons": {
          "configuration-high": [
            "path selectors matched: demo_app/config.py"
          ],
          "authentication-critical": [
            "path selectors matched: demo_app/auth.py"
          ]
        },
        "interaction_rules": {
          "authentication-configuration": "Authentication behavior and deployment/dependency configuration interact."
        },
        "authority_notice": "Verification or readiness is not acceptance. Final decisions remain with authorized human maintainers."
      }
    },
    "authority_notice": "本页面只把 AGM 的真实状态、依据和合法操作整理成人类可读形式。材料齐备、维护者检查完成，或者已经具备进入最终决定的条件，都不等于代码已经被项目接受。最终决定只属于获授权的人类维护者。",
    "responsibility": {
      "primary_roles": [
        "contributor",
        "contributor_agent"
      ],
      "display_label": "人类贡献者、贡献侧智能体",
      "reason": "受影响材料尚未准备或更新完成，当前还不能进入维护者检查。",
      "blocking_items": [
        "智能体行动与委派说明",
        "可检查的测试输出或文件",
        "登录、认证与权限影响说明",
        "变更文件清单",
        "已知限制",
        "修改原因",
        "修改说明",
        "测试命令与结果"
      ],
      "next_handoff_roles": [
        "accountable_human",
        "maintainer_verifier",
        "maintainer"
      ]
    },
    "current_relevant_actions": [],
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
            "object_id": "evidence_incomplete:record_policy_conflict:repair_requested",
            "relationship": "transition"
          }
        ],
        "relevance": "secondary",
        "group": "other_available",
        "primary_reason": "后端允许此操作，但它不直接处理当前主要阻断项。",
        "selector_options": [
          {
            "selector_token": "sel-d72ffd4814be3b7a07b610082832f0657713870e73b66bbfe81913e713b4e91f",
            "action": "record_policy_conflict",
            "label": "智能体行动与委派说明",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [],
            "obligation_ids": [
              "O-AGENT-SCOPE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-AGENT-SCOPE"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-AGENT-SCOPE",
              "evidence_ids": [],
              "finding_ids": []
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
              }
            ]
          },
          {
            "selector_token": "sel-358daaa9b0c9e1483b94a970419c039c2db3d8223c1e93c339df1824d3d5b51e",
            "action": "record_policy_conflict",
            "label": "可检查的测试输出或文件",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-ARTIFACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-ARTIFACT"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-ARTIFACT",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-artifact",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-critical",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "configuration-high",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-1ba1d34d839f78c41f0b06828b4526e9c26631953ab147e6fb4d4448aaa03d15",
            "action": "record_policy_conflict",
            "label": "登录、认证与权限影响说明",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py"
            ],
            "obligation_ids": [
              "O-AUTH-IMPACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-AUTH-IMPACT"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-AUTH-IMPACT",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-auth-impact",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-critical",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-4dd8137617b48a4a08c73a6f1ac40fe6bf8a7979fb73e3a2fdf156841e28047f",
            "action": "record_policy_conflict",
            "label": "变更文件清单",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-CHANGED-FILES"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-CHANGED-FILES"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-CHANGED-FILES",
              "evidence_ids": [],
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
                "object_id": "authentication-critical",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "configuration-high",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-7a3164cc9fb350147a1bc270ebaa51e007b479d0d1be3a10d1b85c2d370d2710",
            "action": "record_policy_conflict",
            "label": "负责人确认",
            "status_label": "缺少；等待负责人确认",
            "affected_scope": [
              "demo_app/auth.py"
            ],
            "obligation_ids": [
              "O-HUMAN-ATTEST"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-HUMAN-ATTEST"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_attestation",
            "technical_details": {
              "obligation_id": "O-HUMAN-ATTEST",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-human-attest",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-critical",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-9a5770bf324a4329d37ec6d4c61b05a758bc65cf97dca3f3096afab23d4b0fb3",
            "action": "record_policy_conflict",
            "label": "独立维护者检查",
            "status_label": "缺少；阻止继续",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-INDEPENDENT-REVIEW"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-INDEPENDENT-REVIEW"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "blocks_progression",
            "technical_details": {
              "obligation_id": "O-INDEPENDENT-REVIEW",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-independent-review",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-configuration",
                "relationship": "source"
              },
              {
                "kind": "interaction_rule",
                "object_id": "authentication-configuration",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-0502b1424e2b74ff3de9799d5ea841aff57ab2cbf6d1f87f42ab2e25b6e9469d",
            "action": "record_policy_conflict",
            "label": "已知限制",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-LIMITATIONS"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-LIMITATIONS"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-LIMITATIONS",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-limitations",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-critical",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "configuration-high",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-1f1a03634afa3ef0c4f5b8b5ebbd18a03c94a4c154cfd44b33e64876dbdb7b52",
            "action": "record_policy_conflict",
            "label": "修改原因",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-RATIONALE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-RATIONALE"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-RATIONALE",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-rationale",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-critical",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "configuration-high",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-72fd0673de38d47762b249b5c39482b13c484e54124ecfd34e9dfd3b563e0b26",
            "action": "record_policy_conflict",
            "label": "修改说明",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-SUMMARY"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-SUMMARY"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-SUMMARY",
              "evidence_ids": [],
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
                "object_id": "authentication-critical",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "configuration-high",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-4a49e0e1ebbb02dab1fce7ce2d4340f202fa234b9b18e212265a605468b9095b",
            "action": "record_policy_conflict",
            "label": "测试命令与结果",
            "status_label": "缺少；等待贡献者处理",
            "affected_scope": [
              "demo_app/auth.py",
              "demo_app/config.py"
            ],
            "obligation_ids": [
              "O-TEST-COMMAND"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-TEST-COMMAND"
            ],
            "blocking": true,
            "material_status": "missing",
            "workflow_status": "awaiting_contributor",
            "technical_details": {
              "obligation_id": "O-TEST-COMMAND",
              "evidence_ids": [],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-test-command",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "authentication-critical",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "configuration-high",
                "relationship": "source"
              }
            ]
          }
        ]
      }
    ],
    "unavailable_action_summary": "还有 13 项操作因当前阶段、权限或对象范围暂不可用",
    "utility_actions": [
      {
        "action_id": "copy_missing_requirements",
        "label": "复制缺失项清单",
        "description": "生成可直接交给贡献侧的缺失、过时或无效材料清单。",
        "output_type": "text/plain",
        "output": "- 智能体行动与委派说明：缺少；等待贡献者处理；范围：当前贡献范围\n- 可检查的测试输出或文件：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 登录、认证与权限影响说明：缺少；等待贡献者处理；范围：demo_app/auth.py\n- 变更文件清单：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 负责人确认：缺少；等待负责人确认；范围：demo_app/auth.py\n- 已知限制：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 修改原因：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 修改说明：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 测试命令与结果：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py",
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
            "kind": "compiled_obligation",
            "object_id": "obl-o-artifact",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-critical",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "configuration-high",
            "relationship": "source"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-auth-impact",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-changed-files",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-human-attest",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-limitations",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-rationale",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-summary",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-test-command",
            "relationship": "reference"
          }
        ],
        "state_changing": false
      },
      {
        "action_id": "export_contributor_checklist",
        "label": "导出贡献者待办清单",
        "description": "导出包含责任方、待处理项和范围的 Markdown 清单。",
        "output_type": "text/markdown",
        "output": "# 贡献者待办清单\n\n案例：multi-risk-missing\n当前责任方：人类贡献者、贡献侧智能体\n原因：受影响材料尚未准备或更新完成，当前还不能进入维护者检查。\n\n## 待处理项\n\n- 智能体行动与委派说明：缺少；等待贡献者处理；范围：当前贡献范围\n- 可检查的测试输出或文件：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 登录、认证与权限影响说明：缺少；等待贡献者处理；范围：demo_app/auth.py\n- 变更文件清单：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 负责人确认：缺少；等待负责人确认；范围：demo_app/auth.py\n- 已知限制：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 修改原因：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 修改说明：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 测试命令与结果：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n\n完成后请按当前 repair/提交范围交回；最终决定仍由人类维护者作出。",
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
            "kind": "compiled_obligation",
            "object_id": "obl-o-artifact",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-critical",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "configuration-high",
            "relationship": "source"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-auth-impact",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-changed-files",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-human-attest",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-limitations",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-rationale",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-summary",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-test-command",
            "relationship": "reference"
          }
        ],
        "state_changing": false
      },
      {
        "action_id": "export_reviewer_summary",
        "label": "下载维护者摘要",
        "description": "导出当前风险、责任方和阻断项摘要，不作接受判断。",
        "output_type": "text/markdown",
        "output": "# 维护者审核摘要\n\n案例：multi-risk-missing\n当前状态：等待贡献者补齐材料\n风险：critical\n当前责任方：人类贡献者、贡献侧智能体\n责任方依据：受影响材料尚未准备或更新完成，当前还不能进入维护者检查。\n\n## 阻断或待检查项\n\n- 智能体行动与委派说明：缺少；等待贡献者处理；范围：当前贡献范围\n- 可检查的测试输出或文件：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 登录、认证与权限影响说明：缺少；等待贡献者处理；范围：demo_app/auth.py\n- 变更文件清单：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 已知限制：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 修改原因：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 修改说明：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n- 测试命令与结果：缺少；等待贡献者处理；范围：demo_app/auth.py、demo_app/config.py\n\n本摘要是治理状态说明，不是接受决定。",
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
            "kind": "compiled_obligation",
            "object_id": "obl-o-artifact",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-critical",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "configuration-high",
            "relationship": "source"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-auth-impact",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-changed-files",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-human-attest",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-independent-review",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-configuration",
            "relationship": "source"
          },
          {
            "kind": "interaction_rule",
            "object_id": "authentication-configuration",
            "relationship": "source"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-limitations",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-rationale",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-summary",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-test-command",
            "relationship": "reference"
          }
        ],
        "state_changing": false
      },
      {
        "action_id": "view_change_scope",
        "label": "查看变化范围",
        "description": "查看变更文件、匹配规则和各要求的影响范围。",
        "output_type": "application/json",
        "output": "{\n  \"case_id\": \"multi-risk-missing\",\n  \"changed_files\": [\n    \"demo_app/auth.py\",\n    \"demo_app/config.py\"\n  ],\n  \"matched_risk_rules\": [\n    {\n      \"rule_id\": \"configuration-high\",\n      \"zone\": \"configuration\",\n      \"affected_paths\": [\n        \"demo_app/config.py\"\n      ]\n    },\n    {\n      \"rule_id\": \"authentication-critical\",\n      \"zone\": \"authentication\",\n      \"affected_paths\": [\n        \"demo_app/auth.py\"\n      ]\n    }\n  ],\n  \"requirement_scopes\": {\n    \"O-AGENT-SCOPE\": [],\n    \"O-ARTIFACT\": [\n      \"demo_app/auth.py\",\n      \"demo_app/config.py\"\n    ],\n    \"O-AUTH-IMPACT\": [\n      \"demo_app/auth.py\"\n    ],\n    \"O-CHANGED-FILES\": [\n      \"demo_app/auth.py\",\n      \"demo_app/config.py\"\n    ],\n    \"O-HUMAN-ATTEST\": [\n      \"demo_app/auth.py\"\n    ],\n    \"O-INDEPENDENT-REVIEW\": [\n      \"demo_app/auth.py\",\n      \"demo_app/config.py\"\n    ],\n    \"O-LIMITATIONS\": [\n      \"demo_app/auth.py\",\n      \"demo_app/config.py\"\n    ],\n    \"O-RATIONALE\": [\n      \"demo_app/auth.py\",\n      \"demo_app/config.py\"\n    ],\n    \"O-SUMMARY\": [\n      \"demo_app/auth.py\",\n      \"demo_app/config.py\"\n    ],\n    \"O-TEST-COMMAND\": [\n      \"demo_app/auth.py\",\n      \"demo_app/config.py\"\n    ]\n  }\n}",
        "trace_refs": [
          {
            "kind": "matched_rule",
            "object_id": "match-configuration-high",
            "relationship": "change_scope"
          },
          {
            "kind": "matched_rule",
            "object_id": "match-authentication-critical",
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
        "output": "案例 multi-risk-missing 当前交给：人类贡献者、贡献侧智能体。\n受影响材料尚未准备或更新完成，当前还不能进入维护者检查。\n涉及：智能体行动与委派说明、可检查的测试输出或文件、登录、认证与权限影响说明、变更文件清单、已知限制、修改原因、修改说明、测试命令与结果。\n完成后交给角色：负责人、维护者侧检查人员或人类维护者。",
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
            "kind": "compiled_obligation",
            "object_id": "obl-o-artifact",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "authentication-critical",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "configuration-high",
            "relationship": "source"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-auth-impact",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-changed-files",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-limitations",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-rationale",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-summary",
            "relationship": "reference"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-test-command",
            "relationship": "reference"
          }
        ],
        "state_changing": false
      }
    ],
    "materiality_declaration": null,
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
      }
    ],
    "trace:requirement:reviewable-artifact": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-artifact",
        "relationship": "source"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-artifact",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "authentication-critical",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "configuration-high",
        "relationship": "source"
      }
    ],
    "trace:requirement:auth-impact": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-auth-impact",
        "relationship": "source"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-auth-impact",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "authentication-critical",
        "relationship": "source"
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
        "object_id": "authentication-critical",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "configuration-high",
        "relationship": "source"
      }
    ],
    "trace:requirement:accountable-human-confirmation": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-human-attest",
        "relationship": "source"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-human-attest",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "authentication-critical",
        "relationship": "source"
      }
    ],
    "trace:requirement:independent-review": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-independent-review",
        "relationship": "source"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-independent-review",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "authentication-configuration",
        "relationship": "source"
      },
      {
        "kind": "interaction_rule",
        "object_id": "authentication-configuration",
        "relationship": "source"
      }
    ],
    "trace:requirement:known-limitations": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-limitations",
        "relationship": "source"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-limitations",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "authentication-critical",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "configuration-high",
        "relationship": "source"
      }
    ],
    "trace:requirement:change-rationale": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-rationale",
        "relationship": "source"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-rationale",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "authentication-critical",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "configuration-high",
        "relationship": "source"
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
        "object_id": "authentication-critical",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "configuration-high",
        "relationship": "source"
      }
    ],
    "trace:requirement:test-command-result": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-test-command",
        "relationship": "source"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-test-command",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "authentication-critical",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "configuration-high",
        "relationship": "source"
      }
    ],
    "trace:automatic-check:material_version_binding": [],
    "trace:automatic-check:test_command_and_result": [],
    "trace:automatic-check:test_version_binding": [],
    "trace:automatic-check:evidence_freshness": [],
    "trace:automatic-check:attestation_version_binding": [],
    "trace:automatic-check:changed_file_scope_match": [],
    "trace:automatic-check:agent_involvement": [],
    "trace:automatic-check:recorded_delegation": [],
    "trace:automatic-check:authority_boundary": [],
    "trace:automatic-check:structural_obligations": [],
    "trace:automatic-check:semantic_declaration_consistency": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-agent-scope",
        "relationship": "semantic_declaration_consistency"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-auth-impact",
        "relationship": "semantic_declaration_consistency"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-independent-review",
        "relationship": "semantic_declaration_consistency"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-limitations",
        "relationship": "semantic_declaration_consistency"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-rationale",
        "relationship": "semantic_declaration_consistency"
      }
    ]
  }
}
```

</details>
