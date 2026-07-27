# AGM Maintainer Review Brief

## AGM 风险规则与执行逻辑调整

## 当前状态与下一步

### 现在需要你检查 4 项

形式化检查已经完成到当前阶段；下面只列出系统不能替代人类作出的判断。

当前责任方：维护者侧检查人员

- 检查：独立维护者检查
- 检查：已知限制
- 检查：项目规则影响说明
- 检查：修改原因

> 检查完成不等于贡献已被接受；最终决定仍由有权人类维护者作出。

## 现在需要你判断的事项（4 项）

### 1. 独立维护者检查

为什么需要人：系统能确认材料结构、范围和版本绑定，但不能自动判断声明是否准确描述代码行为和风险。

贡献者说明：没有可引用的贡献者说明。

系统观察：现有治理结论要求职责分离的独立维护者检查。

材料摘要：前置材料已达到进入独立检查的结构条件。

请重点检查：

- 贡献侧与检查者是否保持职责分离
- 高风险联动影响是否得到独立检查
- 检查结论是否只代表 verification，而非最终接受

可能的处理结果：

- 说明与修改一致，可以记录本项检查完成
- 需要贡献侧补充或更正说明
- 发现不可接受风险，交由有权人类维护者处理

### 2. 已知限制

为什么需要人：系统能确认材料结构、范围和版本绑定，但不能自动判断声明是否准确描述代码行为和风险。

贡献者说明：当前结论仅覆盖本次明确列出的修改范围。

系统观察：系统只能确认限制说明已提供，不能证明其完整性。

材料摘要：系统记录有 1 份形式有效且对应当前版本的材料。

请重点检查：

- 限制说明是否覆盖当前风险范围
- 是否存在会影响合并决定但未披露的限制

可能的处理结果：

- 说明与修改一致，可以记录本项检查完成
- 需要贡献侧补充或更正说明
- 发现不可接受风险，交由有权人类维护者处理

### 3. 项目规则影响说明

为什么需要人：系统能确认材料结构、范围和版本绑定，但不能自动判断声明是否准确描述代码行为和风险。

贡献者说明：修改涉及治理规则与执行逻辑的一致性、兼容性和迁移影响。

系统观察：系统记录到治理规则、入口或治理执行逻辑发生变化。

材料摘要：系统记录有 1 份形式有效且对应当前版本的材料。

请重点检查：

- 治理规则与执行逻辑是否仍然一致
- 是否需要兼容或迁移既有治理案例
- 自修改是否可能削弱职责分离或权威边界

可能的处理结果：

- 说明与修改一致，可以记录本项检查完成
- 需要贡献侧补充或更正说明
- 发现不可接受风险，交由有权人类维护者处理

### 4. 修改原因

为什么需要人：系统能确认材料结构、范围和版本绑定，但不能自动判断声明是否准确描述代码行为和风险。

贡献者说明：这次修改用于解决贡献说明中列出的具体维护问题。

系统观察：系统只能确认修改理由已提供，不能证明理由与代码语义一致。

材料摘要：系统记录有 1 份形式有效且对应当前版本的材料。

请重点检查：

- 修改理由是否与实际范围一致
- 理由是否遗漏关键风险或兼容性影响

可能的处理结果：

- 说明与修改一致，可以记录本项检查完成
- 需要贡献侧补充或更正说明
- 发现不可接受风险，交由有权人类维护者处理

## 本次修改与风险

贡献者说明：本次贡献修改项目的 AGM 风险规则和治理执行逻辑，需要职责分离的独立检查。

系统根据文件和声明归纳：

更新治理或治理运行时文件：.agm/manifest.yml；更新治理或治理运行时文件：src/agm/vnext/risk.py

影响范围：

- AGM 治理与执行支持

综合风险：关键

- .agm/manifest.yml 触发了“项目治理规则”风险范围。
- src/agm/vnext/risk.py 触发了“治理执行逻辑”风险范围。

- 治理规则与治理执行逻辑同时变化，形成自修改联动，需要职责分离的独立检查。

> 归纳边界：系统归纳只依据文件路径、已匹配风险区域和明确声明，不代表系统已经证明代码的真实语义或行为。

## 项目要求与自动检查摘要

项目要求 8 项材料或确认。
- 4 项需要维护者判断
- 4 项已完成当前阶段的形式核对或人工检查

自动检查：
- 7 项完成形式或版本核对
- 0 项发现问题
- 1 项需要人工判断
- 0 项异常已由系统处理

<details>
<summary>查看全部项目要求</summary>

- ✓ 可检查的测试输出或文件 — 材料与版本已核对（材料已提供；形式要求已满足；已对应当前版本；材料与版本已核对）
  - 材料已提供，形式要求有效且对应当前版本；这只表示系统完成了可自动执行的核对，不表示内容正确。
- ✓ 变更文件清单 — 材料与版本已核对（材料已提供；形式要求已满足；已对应当前版本；材料与版本已核对）
  - 材料已提供，形式要求有效且对应当前版本；这只表示系统完成了可自动执行的核对，不表示内容正确。
- ○ 独立维护者检查 — 等待独立维护者检查
  - 需要与贡献侧分离的维护者完成独立检查；完成检查不等于接受。
- ! 已知限制 — 材料齐备，内容待人工检查（材料已提供；形式要求已满足；已对应当前版本；内容待人工检查）
  - 材料已提供，形式要求有效且对应当前版本；内容是否与实际修改一致仍需维护者判断。
- ! 项目规则影响说明 — 材料齐备，内容待人工检查（材料已提供；形式要求已满足；已对应当前版本；内容待人工检查）
  - 材料已提供，形式要求有效且对应当前版本；内容是否与实际修改一致仍需维护者判断。
- ! 修改原因 — 材料齐备，内容待人工检查（材料已提供；形式要求已满足；已对应当前版本；内容待人工检查）
  - 材料已提供，形式要求有效且对应当前版本；内容是否与实际修改一致仍需维护者判断。
- ✓ 修改说明 — 材料与版本已核对（材料已提供；形式要求已满足；已对应当前版本；材料与版本已核对）
  - 材料已提供，形式要求有效且对应当前版本；这只表示系统完成了可自动执行的核对，不表示内容正确。
- ✓ 测试命令与结果 — 材料与版本已核对（材料已提供；形式要求已满足；已对应当前版本；材料与版本已核对）
  - 材料已提供，形式要求有效且对应当前版本；这只表示系统完成了可自动执行的核对，不表示内容正确。

</details>

<details>
<summary>查看自动检查详情</summary>

- ✓ 材料与当前修改版本一致：所有已提供材料都绑定当前版本，或已记录为受影响范围外的保留材料。
  - 类别：项目规则要求；责任：系统已处理
- ✓ 测试是否包含命令和结果：测试材料同时包含可检查的执行说明和结果记录。
  - 类别：项目规则要求；责任：系统已处理
  - 结论边界：系统确认的是记录完整性，不代表代码正确性，也不证明测试覆盖充分。
- ✓ 测试材料是否对应当前版本：现有测试材料对应当前贡献版本或已按未受影响范围保留。
  - 类别：项目规则要求；责任：系统已处理
  - 结论边界：版本一致不代表测试覆盖了所有行为风险。
- ✓ 材料是否仍在有效期内：现有材料记录没有过期状态。
  - 类别：项目规则要求；责任：系统已处理
- – 负责人确认是否绑定当前版本：当前风险路径不要求额外负责人确认。
  - 类别：附加信息；责任：系统已处理
- ✓ 声明范围与实际变更文件一致：材料中的变更文件清单与治理案例记录的实际范围一致。
  - 类别：项目规则要求；责任：系统已处理
- i 是否记录了智能体参与：治理案例采用直接人类贡献配置，未声明智能体参与。
  - 类别：附加信息；责任：系统已处理
  - 结论边界：AGM 只呈现治理记录和声明，不是智能体使用检测器。
- – 是否记录继续委派：当前案例未声明智能体参与，因此不触发委派说明要求。
  - 类别：附加信息；责任：系统已处理
- ✓ 是否存在越权操作：当前案例审计记录中没有被拒绝的越权操作。
  - 类别：系统完整性核对；责任：系统已处理
  - 结论边界：结论范围仅限 AGM 已记录的操作。
- ✓ 结构性项目要求是否满足：当前材料的结构、必填范围和前置确认已达到进入人类判断的条件。
  - 类别：项目规则要求；责任：系统已处理
  - 结论边界：结构满足不等于语义正确，也不等于贡献已被项目接受。
- ! 声明内容是否与实际修改一致：系统已完成结构和绑定检查，但以下内容仍需人类语义判断：已知限制、项目规则影响说明、修改原因、独立维护者检查。
  - 类别：项目规则要求；责任：维护者判断
  - 结论边界：系统不会把文件路径推断、贡献者声明或智能体自述当作代码语义证明。

</details>

<details>
<summary>查看智能体与负责人材料</summary>

系统观察：

- 没有额外系统观察

贡献侧声明：

- 当前没有相关声明

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
  "case_id": "governance-self-mod",
  "raw_state": "awaiting_maintainer_verification",
  "raw_readiness": "not_ready",
  "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
  "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
  "policy_snapshot": {
    "id": "policy-0edb0142a7f75655b01879e34174d3ef",
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
      "id": "match-governance-policy-high",
      "rule_id": "governance-policy-high",
      "zone": "project_governance",
      "risk_level": "high",
      "affected_paths": [
        ".agm/manifest.yml"
      ],
      "selector_reasons": [
        "path selectors matched: .agm/manifest.yml",
        "governance entrypoints matched: .agm/manifest.yml"
      ],
      "obligation_ids": [
        "O-SUMMARY",
        "O-CHANGED-FILES",
        "O-RATIONALE",
        "O-TEST-COMMAND",
        "O-ARTIFACT",
        "O-LIMITATIONS",
        "O-POLICY-IMPACT"
      ],
      "case_required": true,
      "source": "risk_rule",
      "obligation_overrides": {}
    },
    {
      "id": "match-governance-runtime-high",
      "rule_id": "governance-runtime-high",
      "zone": "governance_runtime",
      "risk_level": "high",
      "affected_paths": [
        "src/agm/vnext/risk.py"
      ],
      "selector_reasons": [
        "path selectors matched: src/agm/vnext/risk.py"
      ],
      "obligation_ids": [
        "O-SUMMARY",
        "O-CHANGED-FILES",
        "O-RATIONALE",
        "O-TEST-COMMAND",
        "O-ARTIFACT",
        "O-LIMITATIONS",
        "O-POLICY-IMPACT"
      ],
      "case_required": true,
      "source": "risk_rule",
      "obligation_overrides": {}
    }
  ],
  "compiled_obligations": [
    {
      "id": "obl-o-artifact",
      "obligation_id": "O-ARTIFACT",
      "source_rule_ids": [
        "governance-policy-high",
        "governance-runtime-high"
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
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "status": "satisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-changed-files",
      "obligation_id": "O-CHANGED-FILES",
      "source_rule_ids": [
        "governance-policy-high",
        "governance-runtime-high"
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
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "status": "satisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-independent-review",
      "obligation_id": "O-INDEPENDENT-REVIEW",
      "source_rule_ids": [
        "governance-self-modification"
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
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "status": "unsatisfied",
      "interaction_ids": [
        "governance-self-modification"
      ]
    },
    {
      "id": "obl-o-limitations",
      "obligation_id": "O-LIMITATIONS",
      "source_rule_ids": [
        "governance-policy-high",
        "governance-runtime-high"
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
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "status": "satisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-policy-impact",
      "obligation_id": "O-POLICY-IMPACT",
      "source_rule_ids": [
        "governance-policy-high",
        "governance-runtime-high"
      ],
      "type": "evidence",
      "severity": "high",
      "blocking": true,
      "verifier_roles": [
        "maintainer",
        "policy_steward"
      ],
      "evidence_type": "policy_impact",
      "description": "Describe policy compatibility, migration, and self-modification impact.",
      "affected_scope": [
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "status": "satisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-rationale",
      "obligation_id": "O-RATIONALE",
      "source_rule_ids": [
        "governance-policy-high",
        "governance-runtime-high"
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
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "status": "satisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-summary",
      "obligation_id": "O-SUMMARY",
      "source_rule_ids": [
        "governance-policy-high",
        "governance-runtime-high"
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
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "status": "satisfied",
      "interaction_ids": []
    },
    {
      "id": "obl-o-test-command",
      "obligation_id": "O-TEST-COMMAND",
      "source_rule_ids": [
        "governance-policy-high",
        "governance-runtime-high"
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
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "status": "satisfied",
      "interaction_ids": []
    }
  ],
  "evidence_records": [
    {
      "id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
      "obligation_ids": [
        "O-ARTIFACT"
      ],
      "affected_scope": [
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "evidence_type": "artifact",
      "value": "已附上可在本地检查的测试输出。",
      "command": null,
      "environment": null,
      "artifact_path": "governance-self-mod-tests.txt",
      "artifact_hash": "e0336ec5117948a0d59de5ef8da8324ef52cccc1ce150c2ca56e1208c89bbb8f",
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
      "id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
      "obligation_ids": [
        "O-CHANGED-FILES"
      ],
      "affected_scope": [
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "evidence_type": "changed_files",
      "value": [
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
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
      "id": "evidence-e82759bb057254b28e04056067e73c27",
      "obligation_ids": [
        "O-LIMITATIONS"
      ],
      "affected_scope": [
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "evidence_type": "known_limitations",
      "value": "当前结论仅覆盖本次明确列出的修改范围。",
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
      "id": "evidence-f3b12fad64c450c784e59967d80cf723",
      "obligation_ids": [
        "O-POLICY-IMPACT"
      ],
      "affected_scope": [
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "evidence_type": "policy_impact",
      "value": "修改涉及治理规则与执行逻辑的一致性、兼容性和迁移影响。",
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
      "id": "evidence-326843434826584ea782e7ff3f48d60c",
      "obligation_ids": [
        "O-RATIONALE"
      ],
      "affected_scope": [
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "evidence_type": "rationale",
      "value": "这次修改用于解决贡献说明中列出的具体维护问题。",
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
      "id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
      "obligation_ids": [
        "O-SUMMARY"
      ],
      "affected_scope": [
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "evidence_type": "contribution_summary",
      "value": "本次贡献修改项目的 AGM 风险规则和治理执行逻辑，需要职责分离的独立检查。",
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
      "id": "evidence-5e0da51685f955908b307956f2962e2a",
      "obligation_ids": [
        "O-TEST-COMMAND"
      ],
      "affected_scope": [
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "evidence_type": "test_command",
      "value": "完整本地回归测试已通过。",
      "command": "python -m pytest -q",
      "environment": "Python / local scenario",
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
  "attempted_operations": [],
  "verification_records": [],
  "transition_history": [
    {
      "id": "transition-1859ed182d6a5c329be0f6d44ab24a68",
      "case_id": "governance-self-mod",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "case_opened",
      "target_state": "policy_resolved",
      "action": "resolve_policy",
      "reason": "Resolved canonical policy against the contribution.",
      "related_object_ids": [
        "policy-0edb0142a7f75655b01879e34174d3ef"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-d003ab68de3b5f649b6ca11b2e5be2f9",
      "case_id": "governance-self-mod",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "policy_resolved",
      "target_state": "obligations_compiled",
      "action": "compile_obligations",
      "reason": "Compiled the union of matched, profile, and interaction obligations.",
      "related_object_ids": [
        "obl-o-artifact",
        "obl-o-changed-files",
        "obl-o-independent-review",
        "obl-o-limitations",
        "obl-o-policy-impact",
        "obl-o-rationale",
        "obl-o-summary",
        "obl-o-test-command"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-adbc24c34d4c5742ac75693c163fd6ee",
      "case_id": "governance-self-mod",
      "actor": "agm-engine",
      "role": "system",
      "source_state": "obligations_compiled",
      "target_state": "evidence_incomplete",
      "action": "mark_evidence_state",
      "reason": "The new case has unsatisfied evidence obligations.",
      "related_object_ids": [
        "obl-o-artifact",
        "obl-o-changed-files",
        "obl-o-limitations",
        "obl-o-policy-impact",
        "obl-o-rationale",
        "obl-o-summary",
        "obl-o-test-command"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    },
    {
      "id": "transition-49f109a2087b5cc0af95fd19bd8c377d",
      "case_id": "governance-self-mod",
      "actor": "contributor-agent",
      "role": "contributor_agent",
      "source_state": "evidence_incomplete",
      "target_state": "awaiting_maintainer_verification",
      "action": "submit_for_verification",
      "reason": "Contributor submitted prepared evidence for maintainer verification.",
      "related_object_ids": [
        "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
        "evidence-ce0afaeb5b845e86aad1586b5ec26707",
        "evidence-e82759bb057254b28e04056067e73c27",
        "evidence-f3b12fad64c450c784e59967d80cf723",
        "evidence-326843434826584ea782e7ff3f48d60c",
        "evidence-3837ecb13fb556e59b8a9cc1f6628332",
        "evidence-5e0da51685f955908b307956f2962e2a"
      ],
      "timestamp": "2026-07-26T00:00:00Z"
    }
  ],
  "final_decision": null,
  "closure_receipt": null,
  "policy_migration_diagnostic": {
    "case_id": "governance-self-mod",
    "policy_changed": false,
    "original_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
    "current_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
    "still_valid_obligations": [
      "O-ARTIFACT",
      "O-CHANGED-FILES",
      "O-INDEPENDENT-REVIEW",
      "O-LIMITATIONS",
      "O-POLICY-IMPACT",
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
    "generated_from_case_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
    "actor": {
      "actor": "human-maintainer",
      "role": "maintainer",
      "human": true
    },
    "summary": {
      "case_id": "governance-self-mod",
      "changed_files": [
        ".agm/manifest.yml",
        "src/agm/vnext/risk.py"
      ],
      "risk_level": "critical",
      "risk_areas": [
        "governance_runtime（governance_runtime）",
        "project_governance（project_governance）"
      ],
      "autonomy_profile": "human_direct",
      "path_kind": "full",
      "path_label": "完整治理流程",
      "current_stage": "等待维护者检查",
      "blocking_issue_count": 0,
      "warning_count": 0,
      "current_responsible_parties": [
        "人类维护者"
      ],
      "next_authorized_actor_roles": [
        "maintainer"
      ],
      "raw_state": "awaiting_maintainer_verification",
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
            "object_id": "transition-1859ed182d6a5c329be0f6d44ab24a68",
            "relationship": "primary:resolve_policy"
          },
          {
            "kind": "state_transition",
            "object_id": "transition-d003ab68de3b5f649b6ca11b2e5be2f9",
            "relationship": "primary:compile_obligations"
          },
          {
            "kind": "matched_rule",
            "object_id": "match-governance-policy-high",
            "relationship": "risk_matching"
          },
          {
            "kind": "matched_rule",
            "object_id": "match-governance-runtime-high",
            "relationship": "risk_matching"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-artifact",
            "relationship": "obligation_compilation"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-changed-files",
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
            "object_id": "obl-o-policy-impact",
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
            "object_id": "governance-self-modification",
            "relationship": "interaction_matching"
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
            "object_id": "transition-adbc24c34d4c5742ac75693c163fd6ee",
            "relationship": "primary:mark_evidence_state"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
            "relationship": "binding_or_retention"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
            "relationship": "binding_or_retention"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-e82759bb057254b28e04056067e73c27",
            "relationship": "binding_or_retention"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
            "relationship": "binding_or_retention"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
            "relationship": "binding_or_retention"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
            "relationship": "binding_or_retention"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
            "object_id": "transition-49f109a2087b5cc0af95fd19bd8c377d",
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
        "obligation_id": "O-ARTIFACT",
        "check_item": "可检查的测试输出或文件",
        "project_requirement": "提供可以实际检查的测试输出或文件。",
        "current_situation": "已提供与当前贡献和项目规则绑定的材料。",
        "result": "meets_requirement",
        "result_label": "符合要求",
        "raw_status": "satisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "governance-policy-high",
          "governance-runtime-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [
          "evidence-0a495de0ff0f53c8a9ac58708248bf4c"
        ],
        "binding_fingerprints": [
          "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41"
        ],
        "finding_ids": [],
        "reference_english": "Provide a locally checkable artifact or test output.",
        "observed_english": "valid bound evidence is present",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-artifact",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-policy-high",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-runtime-high",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
            "relationship": "observed"
          }
        ],
        "display_name": "可检查的测试输出或文件",
        "reference_plain": "提供可以实际检查的测试输出或文件。",
        "observed_plain": "已提供与当前贡献和项目规则绑定的材料。",
        "observed_raw": "valid bound evidence is present",
        "material_status": "provided",
        "material_status_label": "已提供",
        "workflow_status": "completed",
        "workflow_status_label": "已完成",
        "currently_blocks_progression": false,
        "affected_scope": [
          ".agm/manifest.yml",
          "src/agm/vnext/risk.py"
        ]
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
          "governance-policy-high",
          "governance-runtime-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [
          "evidence-ce0afaeb5b845e86aad1586b5ec26707"
        ],
        "binding_fingerprints": [
          "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41"
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
            "object_id": "governance-policy-high",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-runtime-high",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
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
          ".agm/manifest.yml",
          "src/agm/vnext/risk.py"
        ]
      },
      {
        "obligation_id": "O-INDEPENDENT-REVIEW",
        "check_item": "独立维护者检查",
        "project_requirement": "由另一名具备权限且与贡献侧分离的维护者独立检查。",
        "current_situation": "前序材料满足后，由具备权限且与贡献侧分离的维护者检查。",
        "result": "not_started",
        "result_label": "尚未进行",
        "raw_status": "unsatisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "governance-self-modification"
        ],
        "interaction_ids": [
          "governance-self-modification"
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
            "object_id": "governance-self-modification",
            "relationship": "source"
          },
          {
            "kind": "interaction_rule",
            "object_id": "governance-self-modification",
            "relationship": "source"
          }
        ],
        "display_name": "独立维护者检查",
        "reference_plain": "由另一名具备权限且与贡献侧分离的维护者独立检查。",
        "observed_plain": "前序材料满足后，由具备权限且与贡献侧分离的维护者检查。",
        "observed_raw": "independent maintainer verification not recorded",
        "material_status": "missing",
        "material_status_label": "缺少",
        "workflow_status": "blocks_progression",
        "workflow_status_label": "阻止继续",
        "currently_blocks_progression": true,
        "affected_scope": [
          ".agm/manifest.yml",
          "src/agm/vnext/risk.py"
        ]
      },
      {
        "obligation_id": "O-LIMITATIONS",
        "check_item": "已知限制",
        "project_requirement": "说明已知限制；没有已知限制也要明确说明。",
        "current_situation": "已提供与当前贡献和项目规则绑定的材料。",
        "result": "meets_requirement",
        "result_label": "符合要求",
        "raw_status": "satisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "governance-policy-high",
          "governance-runtime-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [
          "evidence-e82759bb057254b28e04056067e73c27"
        ],
        "binding_fingerprints": [
          "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41"
        ],
        "finding_ids": [],
        "reference_english": "State known limitations or explicitly state none.",
        "observed_english": "valid bound evidence is present",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-limitations",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-policy-high",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-runtime-high",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-e82759bb057254b28e04056067e73c27",
            "relationship": "observed"
          }
        ],
        "display_name": "已知限制",
        "reference_plain": "说明已知限制；没有已知限制也要明确说明。",
        "observed_plain": "已提供与当前贡献和项目规则绑定的材料。",
        "observed_raw": "valid bound evidence is present",
        "material_status": "provided",
        "material_status_label": "已提供",
        "workflow_status": "completed",
        "workflow_status_label": "已完成",
        "currently_blocks_progression": false,
        "affected_scope": [
          ".agm/manifest.yml",
          "src/agm/vnext/risk.py"
        ]
      },
      {
        "obligation_id": "O-POLICY-IMPACT",
        "check_item": "项目规则影响说明",
        "project_requirement": "说明本次修改是否影响项目规则或治理流程。",
        "current_situation": "已提供与当前贡献和项目规则绑定的材料。",
        "result": "meets_requirement",
        "result_label": "符合要求",
        "raw_status": "satisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "governance-policy-high",
          "governance-runtime-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [
          "evidence-f3b12fad64c450c784e59967d80cf723"
        ],
        "binding_fingerprints": [
          "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41"
        ],
        "finding_ids": [],
        "reference_english": "Describe policy compatibility, migration, and self-modification impact.",
        "observed_english": "valid bound evidence is present",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-policy-impact",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-policy-high",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-runtime-high",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
            "relationship": "observed"
          }
        ],
        "display_name": "项目规则影响说明",
        "reference_plain": "说明本次修改是否影响项目规则或治理流程。",
        "observed_plain": "已提供与当前贡献和项目规则绑定的材料。",
        "observed_raw": "valid bound evidence is present",
        "material_status": "provided",
        "material_status_label": "已提供",
        "workflow_status": "completed",
        "workflow_status_label": "已完成",
        "currently_blocks_progression": false,
        "affected_scope": [
          ".agm/manifest.yml",
          "src/agm/vnext/risk.py"
        ]
      },
      {
        "obligation_id": "O-RATIONALE",
        "check_item": "修改原因",
        "project_requirement": "说明为什么需要这次修改。",
        "current_situation": "已提供与当前贡献和项目规则绑定的材料。",
        "result": "meets_requirement",
        "result_label": "符合要求",
        "raw_status": "satisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "governance-policy-high",
          "governance-runtime-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [
          "evidence-326843434826584ea782e7ff3f48d60c"
        ],
        "binding_fingerprints": [
          "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41"
        ],
        "finding_ids": [],
        "reference_english": "Explain why the change is needed without disclosing private reasoning.",
        "observed_english": "valid bound evidence is present",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-rationale",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-policy-high",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-runtime-high",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
            "relationship": "observed"
          }
        ],
        "display_name": "修改原因",
        "reference_plain": "说明为什么需要这次修改。",
        "observed_plain": "已提供与当前贡献和项目规则绑定的材料。",
        "observed_raw": "valid bound evidence is present",
        "material_status": "provided",
        "material_status_label": "已提供",
        "workflow_status": "completed",
        "workflow_status_label": "已完成",
        "currently_blocks_progression": false,
        "affected_scope": [
          ".agm/manifest.yml",
          "src/agm/vnext/risk.py"
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
          "governance-policy-high",
          "governance-runtime-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [
          "evidence-3837ecb13fb556e59b8a9cc1f6628332"
        ],
        "binding_fingerprints": [
          "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41"
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
            "object_id": "governance-policy-high",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-runtime-high",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
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
          ".agm/manifest.yml",
          "src/agm/vnext/risk.py"
        ]
      },
      {
        "obligation_id": "O-TEST-COMMAND",
        "check_item": "测试命令与结果",
        "project_requirement": "提供测试命令、运行环境和实际结果。",
        "current_situation": "已提供与当前贡献和项目规则绑定的材料。",
        "result": "meets_requirement",
        "result_label": "符合要求",
        "raw_status": "satisfied",
        "blocking_requirement": true,
        "source_rule_ids": [
          "governance-policy-high",
          "governance-runtime-high"
        ],
        "interaction_ids": [],
        "evidence_ids": [
          "evidence-5e0da51685f955908b307956f2962e2a"
        ],
        "binding_fingerprints": [
          "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41"
        ],
        "finding_ids": [],
        "reference_english": "Provide a concrete test command, environment, and outcome.",
        "observed_english": "valid bound evidence is present",
        "traceability": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-test-command",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-policy-high",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-runtime-high",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
            "relationship": "observed"
          }
        ],
        "display_name": "测试命令与结果",
        "reference_plain": "提供测试命令、运行环境和实际结果。",
        "observed_plain": "已提供与当前贡献和项目规则绑定的材料。",
        "observed_raw": "valid bound evidence is present",
        "material_status": "provided",
        "material_status_label": "已提供",
        "workflow_status": "completed",
        "workflow_status_label": "已完成",
        "currently_blocks_progression": false,
        "affected_scope": [
          ".agm/manifest.yml",
          "src/agm/vnext/risk.py"
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
          "O-ARTIFACT",
          "O-CHANGED-FILES",
          "O-INDEPENDENT-REVIEW",
          "O-LIMITATIONS",
          "O-POLICY-IMPACT",
          "O-RATIONALE",
          "O-SUMMARY",
          "O-TEST-COMMAND"
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
            "selector_token": "sel-aa09b9117c3b988e02073aa0fd52c6ba26434dd648d626e5e7ab3a03ae41e430",
            "action": "verify_evidence",
            "label": "可检查的测试输出或文件",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-ARTIFACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-ARTIFACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-ARTIFACT",
              "evidence_ids": [
                "evidence-0a495de0ff0f53c8a9ac58708248bf4c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-548a14860b2f7c38335f89855e79275f8023f6959bc561557d82b58a52dca0d0",
            "action": "verify_evidence",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-ce0afaeb5b845e86aad1586b5ec26707"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-2b4f51341e10ae1d44dd9233c697f996ce05c822e7360e7886b068588d789239",
            "action": "verify_evidence",
            "label": "独立维护者检查",
            "status_label": "缺少；阻止继续",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "object_id": "governance-self-modification",
                "relationship": "source"
              },
              {
                "kind": "interaction_rule",
                "object_id": "governance-self-modification",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-a3938ad06c2f9667c4938ef4a1ee760f439aef1d70d71fc575250e3b4de13188",
            "action": "verify_evidence",
            "label": "已知限制",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-LIMITATIONS"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-LIMITATIONS"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-LIMITATIONS",
              "evidence_ids": [
                "evidence-e82759bb057254b28e04056067e73c27"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-e82759bb057254b28e04056067e73c27",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-6d81f6d13e263ee9825b34ce68cdf56ef7ecdf800adfb4f00dc956db06d7c8e7",
            "action": "verify_evidence",
            "label": "项目规则影响说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-POLICY-IMPACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-POLICY-IMPACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-POLICY-IMPACT",
              "evidence_ids": [
                "evidence-f3b12fad64c450c784e59967d80cf723"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-policy-impact",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-21782ceed543fc369cc0f00b338b47547869b7d3d8c4c1b77ba114fb4cb2e294",
            "action": "verify_evidence",
            "label": "修改原因",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-RATIONALE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-RATIONALE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-RATIONALE",
              "evidence_ids": [
                "evidence-326843434826584ea782e7ff3f48d60c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-429aac5b11df03b21486cc24f48c26dc9b6187ab0cc6f2dc8a221f795c3200f1",
            "action": "verify_evidence",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-3837ecb13fb556e59b8a9cc1f6628332"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-3803be8dca776db13cc3343c3ce8ff5613be015997b522af51ba447e9c52c563",
            "action": "verify_evidence",
            "label": "测试命令与结果",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-TEST-COMMAND"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-TEST-COMMAND"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-TEST-COMMAND",
              "evidence_ids": [
                "evidence-5e0da51685f955908b307956f2962e2a"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
        "default_obligation_ids": [
          "O-INDEPENDENT-REVIEW"
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
            "selector_token": "sel-ce938738951e847ff471957fa1ecb734e70d977c3a9d6c6795b1e0c59187826b",
            "action": "request_repair",
            "label": "可检查的测试输出或文件",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-ARTIFACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-ARTIFACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-ARTIFACT",
              "evidence_ids": [
                "evidence-0a495de0ff0f53c8a9ac58708248bf4c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-5d6334ababab52928e46fc705f59d0872ffa2dc0ea33f5d502f052cdc0a1cb28",
            "action": "request_repair",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-ce0afaeb5b845e86aad1586b5ec26707"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-9baf93e101fbff49983a483189f8de95fcf5b97ebb3c99080404e9ee38225a27",
            "action": "request_repair",
            "label": "独立维护者检查",
            "status_label": "缺少；阻止继续",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "object_id": "governance-self-modification",
                "relationship": "source"
              },
              {
                "kind": "interaction_rule",
                "object_id": "governance-self-modification",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-f379122e0a1f3134cd191ee1524d9686c67c0ed462ba7a9bcaee764cac11375b",
            "action": "request_repair",
            "label": "已知限制",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-LIMITATIONS"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-LIMITATIONS"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-LIMITATIONS",
              "evidence_ids": [
                "evidence-e82759bb057254b28e04056067e73c27"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-e82759bb057254b28e04056067e73c27",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-3bc18cf39bb3e1b327b1dceca67634b3c62eadd41fe9b21961336f65d9e50d41",
            "action": "request_repair",
            "label": "项目规则影响说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-POLICY-IMPACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-POLICY-IMPACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-POLICY-IMPACT",
              "evidence_ids": [
                "evidence-f3b12fad64c450c784e59967d80cf723"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-policy-impact",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-b897f62656fb09fd198ac9ed847e43a44b6fb00769026b98211ae346b5b260d7",
            "action": "request_repair",
            "label": "修改原因",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-RATIONALE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-RATIONALE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-RATIONALE",
              "evidence_ids": [
                "evidence-326843434826584ea782e7ff3f48d60c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-4415aebdbd3335b58ca3523256f14c6ae0984f8905efdda4a299d97af779e608",
            "action": "request_repair",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-3837ecb13fb556e59b8a9cc1f6628332"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-a8b1d3acf740e2dd865e1e56a7e0d84fa76a03efe22e41ee7fa80cb2259b5d82",
            "action": "request_repair",
            "label": "测试命令与结果",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-TEST-COMMAND"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-TEST-COMMAND"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-TEST-COMMAND",
              "evidence_ids": [
                "evidence-5e0da51685f955908b307956f2962e2a"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
            "selector_token": "sel-07c57135e591e818749c16888d7dca83bf3151d191dbac079ee20e5a9c1de043",
            "action": "reject_evidence",
            "label": "可检查的测试输出或文件",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-ARTIFACT"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-0a495de0ff0f53c8a9ac58708248bf4c"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
              "evidence_type": "artifact"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-35d926f8495b27d0933d54cc738f22000b29f77e75d25cc5218b80ca79ccd2be",
            "action": "reject_evidence",
            "label": "变更文件清单",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-CHANGED-FILES"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-ce0afaeb5b845e86aad1586b5ec26707"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
              "evidence_type": "changed_files"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-829c215fce2efcc0bc83f9c70e16685a538d2ebe6c4d2c5a7c222eb2a9d3f340",
            "action": "reject_evidence",
            "label": "已知限制",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-LIMITATIONS"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-e82759bb057254b28e04056067e73c27"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-e82759bb057254b28e04056067e73c27",
              "evidence_type": "known_limitations"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-e82759bb057254b28e04056067e73c27",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-7d76b32e6f2b4625358369d3a5b6ee2708a584de816d4dccceaf4396f21021b6",
            "action": "reject_evidence",
            "label": "项目规则影响说明",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-POLICY-IMPACT"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-f3b12fad64c450c784e59967d80cf723"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-f3b12fad64c450c784e59967d80cf723",
              "evidence_type": "policy_impact"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-998335e3960e82534011ca89a7daefff2ac933e18a86b7ee60d170d5046edca2",
            "action": "reject_evidence",
            "label": "修改原因",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-RATIONALE"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-326843434826584ea782e7ff3f48d60c"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-326843434826584ea782e7ff3f48d60c",
              "evidence_type": "rationale"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-a321e6774250de84a1dcc079e12bf23bee1520f7393b2ae030fe79d6567c0769",
            "action": "reject_evidence",
            "label": "修改说明",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-SUMMARY"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-3837ecb13fb556e59b8a9cc1f6628332"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
              "evidence_type": "contribution_summary"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-8ebe0fa5ce54f1d1cbb8a69f80283ef5ff427f4c7e72c501d98a8fea4011d711",
            "action": "reject_evidence",
            "label": "测试命令与结果",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-TEST-COMMAND"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-5e0da51685f955908b307956f2962e2a"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-5e0da51685f955908b307956f2962e2a",
              "evidence_type": "test_command"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
          "O-INDEPENDENT-REVIEW"
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
            "selector_token": "sel-ac602e939a4a4baae6266758d5eadb8559d8281e80ceb0e94a783a0c170cc07f",
            "action": "ask_clarification",
            "label": "可检查的测试输出或文件",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-ARTIFACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-ARTIFACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-ARTIFACT",
              "evidence_ids": [
                "evidence-0a495de0ff0f53c8a9ac58708248bf4c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-640d7b2164fa6b8e58a4f2d9a9fa89a43112d6900cecb0b477b5faf4c17e2476",
            "action": "ask_clarification",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-ce0afaeb5b845e86aad1586b5ec26707"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-0e04a216156bd59c4248905a06de03211fb82514f55fa53f984dbd93d4fe6827",
            "action": "ask_clarification",
            "label": "独立维护者检查",
            "status_label": "缺少；阻止继续",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "object_id": "governance-self-modification",
                "relationship": "source"
              },
              {
                "kind": "interaction_rule",
                "object_id": "governance-self-modification",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-b92ae5b3351af07be98f027a1a4b4511e6877f32c735cdef7755ef10d8fb9001",
            "action": "ask_clarification",
            "label": "已知限制",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-LIMITATIONS"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-LIMITATIONS"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-LIMITATIONS",
              "evidence_ids": [
                "evidence-e82759bb057254b28e04056067e73c27"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-e82759bb057254b28e04056067e73c27",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-bd8b61216a25dab8d860123112a6fcfe6a8b883a074d3ef3f537a93ee72226c6",
            "action": "ask_clarification",
            "label": "项目规则影响说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-POLICY-IMPACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-POLICY-IMPACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-POLICY-IMPACT",
              "evidence_ids": [
                "evidence-f3b12fad64c450c784e59967d80cf723"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-policy-impact",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-61178c1ecf4c048fa2b36cba76fc43a02d55b4ccb58997e84d0b1d7d99f3461d",
            "action": "ask_clarification",
            "label": "修改原因",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-RATIONALE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-RATIONALE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-RATIONALE",
              "evidence_ids": [
                "evidence-326843434826584ea782e7ff3f48d60c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-e9ac1e60287168b64773e1821f501b91e8b6a192de0d8a32400fe739803f738c",
            "action": "ask_clarification",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-3837ecb13fb556e59b8a9cc1f6628332"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-5febcb1503c71880d7c04fb0f0b7f92db22e797550264a282bbad803d8f8d0ef",
            "action": "ask_clarification",
            "label": "测试命令与结果",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-TEST-COMMAND"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-TEST-COMMAND"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-TEST-COMMAND",
              "evidence_ids": [
                "evidence-5e0da51685f955908b307956f2962e2a"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
          "O-INDEPENDENT-REVIEW"
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
            "selector_token": "sel-ab9b2c319a358114637a8e3d6027b5024bed7b4a706f13478f13bcb8e173f9d2",
            "action": "record_policy_conflict",
            "label": "可检查的测试输出或文件",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-ARTIFACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-ARTIFACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-ARTIFACT",
              "evidence_ids": [
                "evidence-0a495de0ff0f53c8a9ac58708248bf4c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-b85ee25d24c8f97eabf9e16799ccf6725aa9e835ae74658cab23242e4abde654",
            "action": "record_policy_conflict",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-ce0afaeb5b845e86aad1586b5ec26707"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-8e7a1534406cfdcc93e4f2bdf91313d74792c29700eda6d47213ed348c16bf4f",
            "action": "record_policy_conflict",
            "label": "独立维护者检查",
            "status_label": "缺少；阻止继续",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "object_id": "governance-self-modification",
                "relationship": "source"
              },
              {
                "kind": "interaction_rule",
                "object_id": "governance-self-modification",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-1d31168826cca5f79be960cb1a21d452778139f55c5f053ec8e47fa35b4ef6f0",
            "action": "record_policy_conflict",
            "label": "已知限制",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-LIMITATIONS"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-LIMITATIONS"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-LIMITATIONS",
              "evidence_ids": [
                "evidence-e82759bb057254b28e04056067e73c27"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-e82759bb057254b28e04056067e73c27",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-89c82b4ebe736ebd3bfb4df5eceee29e77a7d177f4c9d1df2485b44bd9652431",
            "action": "record_policy_conflict",
            "label": "项目规则影响说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-POLICY-IMPACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-POLICY-IMPACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-POLICY-IMPACT",
              "evidence_ids": [
                "evidence-f3b12fad64c450c784e59967d80cf723"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-policy-impact",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-9193eb10e9bc19ccd28c68cd9b00cbe83dc4c709edab392dfe14a62fc7bcb23d",
            "action": "record_policy_conflict",
            "label": "修改原因",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-RATIONALE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-RATIONALE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-RATIONALE",
              "evidence_ids": [
                "evidence-326843434826584ea782e7ff3f48d60c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-4201eca371978ac1067423377249fa88065e09ea73d8d4f43f276328f5567414",
            "action": "record_policy_conflict",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-3837ecb13fb556e59b8a9cc1f6628332"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-c9d6b8a4ed86047ba54b1836cc2a307548d5ab883cb09730dde240d1c8389cd7",
            "action": "record_policy_conflict",
            "label": "测试命令与结果",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-TEST-COMMAND"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-TEST-COMMAND"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-TEST-COMMAND",
              "evidence_ids": [
                "evidence-5e0da51685f955908b307956f2962e2a"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
    "explanations": [],
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
      "readiness": "not_ready",
      "risk_rules": [
        {
          "id": "match-governance-policy-high",
          "rule_id": "governance-policy-high",
          "zone": "project_governance",
          "risk_level": "high",
          "affected_paths": [
            ".agm/manifest.yml"
          ],
          "selector_reasons": [
            "path selectors matched: .agm/manifest.yml",
            "governance entrypoints matched: .agm/manifest.yml"
          ],
          "obligation_ids": [
            "O-SUMMARY",
            "O-CHANGED-FILES",
            "O-RATIONALE",
            "O-TEST-COMMAND",
            "O-ARTIFACT",
            "O-LIMITATIONS",
            "O-POLICY-IMPACT"
          ],
          "case_required": true,
          "source": "risk_rule",
          "obligation_overrides": {}
        },
        {
          "id": "match-governance-runtime-high",
          "rule_id": "governance-runtime-high",
          "zone": "governance_runtime",
          "risk_level": "high",
          "affected_paths": [
            "src/agm/vnext/risk.py"
          ],
          "selector_reasons": [
            "path selectors matched: src/agm/vnext/risk.py"
          ],
          "obligation_ids": [
            "O-SUMMARY",
            "O-CHANGED-FILES",
            "O-RATIONALE",
            "O-TEST-COMMAND",
            "O-ARTIFACT",
            "O-LIMITATIONS",
            "O-POLICY-IMPACT"
          ],
          "case_required": true,
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
      "interaction_rules": [
        {
          "id": "governance-self-modification",
          "all_rule_ids": [
            "governance-policy-high",
            "governance-runtime-high"
          ],
          "risk_level": "critical",
          "obligation_ids": [
            "O-INDEPENDENT-REVIEW"
          ],
          "separation_of_duty": true,
          "description": "Policy and its executable governance runtime change together."
        }
      ],
      "compiled_obligations": [
        {
          "id": "obl-o-artifact",
          "obligation_id": "O-ARTIFACT",
          "source_rule_ids": [
            "governance-policy-high",
            "governance-runtime-high"
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
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "status": "satisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-changed-files",
          "obligation_id": "O-CHANGED-FILES",
          "source_rule_ids": [
            "governance-policy-high",
            "governance-runtime-high"
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
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "status": "satisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-independent-review",
          "obligation_id": "O-INDEPENDENT-REVIEW",
          "source_rule_ids": [
            "governance-self-modification"
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
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "status": "unsatisfied",
          "interaction_ids": [
            "governance-self-modification"
          ]
        },
        {
          "id": "obl-o-limitations",
          "obligation_id": "O-LIMITATIONS",
          "source_rule_ids": [
            "governance-policy-high",
            "governance-runtime-high"
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
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "status": "satisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-policy-impact",
          "obligation_id": "O-POLICY-IMPACT",
          "source_rule_ids": [
            "governance-policy-high",
            "governance-runtime-high"
          ],
          "type": "evidence",
          "severity": "high",
          "blocking": true,
          "verifier_roles": [
            "maintainer",
            "policy_steward"
          ],
          "evidence_type": "policy_impact",
          "description": "Describe policy compatibility, migration, and self-modification impact.",
          "affected_scope": [
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "status": "satisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-rationale",
          "obligation_id": "O-RATIONALE",
          "source_rule_ids": [
            "governance-policy-high",
            "governance-runtime-high"
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
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "status": "satisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-summary",
          "obligation_id": "O-SUMMARY",
          "source_rule_ids": [
            "governance-policy-high",
            "governance-runtime-high"
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
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "status": "satisfied",
          "interaction_ids": []
        },
        {
          "id": "obl-o-test-command",
          "obligation_id": "O-TEST-COMMAND",
          "source_rule_ids": [
            "governance-policy-high",
            "governance-runtime-high"
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
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "status": "satisfied",
          "interaction_ids": []
        }
      ],
      "evidence_records": [
        {
          "id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
          "obligation_ids": [
            "O-ARTIFACT"
          ],
          "affected_scope": [
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
          "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
          "evidence_type": "artifact",
          "value": "已附上可在本地检查的测试输出。",
          "command": null,
          "environment": null,
          "artifact_path": "governance-self-mod-tests.txt",
          "artifact_hash": "e0336ec5117948a0d59de5ef8da8324ef52cccc1ce150c2ca56e1208c89bbb8f",
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
          "id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
          "obligation_ids": [
            "O-CHANGED-FILES"
          ],
          "affected_scope": [
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
          "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
          "evidence_type": "changed_files",
          "value": [
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
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
          "id": "evidence-e82759bb057254b28e04056067e73c27",
          "obligation_ids": [
            "O-LIMITATIONS"
          ],
          "affected_scope": [
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
          "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
          "evidence_type": "known_limitations",
          "value": "当前结论仅覆盖本次明确列出的修改范围。",
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
          "id": "evidence-f3b12fad64c450c784e59967d80cf723",
          "obligation_ids": [
            "O-POLICY-IMPACT"
          ],
          "affected_scope": [
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
          "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
          "evidence_type": "policy_impact",
          "value": "修改涉及治理规则与执行逻辑的一致性、兼容性和迁移影响。",
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
          "id": "evidence-326843434826584ea782e7ff3f48d60c",
          "obligation_ids": [
            "O-RATIONALE"
          ],
          "affected_scope": [
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
          "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
          "evidence_type": "rationale",
          "value": "这次修改用于解决贡献说明中列出的具体维护问题。",
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
          "id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
          "obligation_ids": [
            "O-SUMMARY"
          ],
          "affected_scope": [
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
          "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
          "evidence_type": "contribution_summary",
          "value": "本次贡献修改项目的 AGM 风险规则和治理执行逻辑，需要职责分离的独立检查。",
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
          "id": "evidence-5e0da51685f955908b307956f2962e2a",
          "obligation_ids": [
            "O-TEST-COMMAND"
          ],
          "affected_scope": [
            ".agm/manifest.yml",
            "src/agm/vnext/risk.py"
          ],
          "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
          "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
          "evidence_type": "test_command",
          "value": "完整本地回归测试已通过。",
          "command": "python -m pytest -q",
          "environment": "Python / local scenario",
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
      "attempted_operations": [],
      "contribution_fingerprint": "ca3c9b1db2449d4653441d68a96bb549522d33b0721d047b27ba7dece4bf5b41",
      "policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
      "policy_snapshot": {
        "id": "policy-0edb0142a7f75655b01879e34174d3ef",
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
          "id": "transition-1859ed182d6a5c329be0f6d44ab24a68",
          "case_id": "governance-self-mod",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "case_opened",
          "target_state": "policy_resolved",
          "action": "resolve_policy",
          "reason": "Resolved canonical policy against the contribution.",
          "related_object_ids": [
            "policy-0edb0142a7f75655b01879e34174d3ef"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-d003ab68de3b5f649b6ca11b2e5be2f9",
          "case_id": "governance-self-mod",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "policy_resolved",
          "target_state": "obligations_compiled",
          "action": "compile_obligations",
          "reason": "Compiled the union of matched, profile, and interaction obligations.",
          "related_object_ids": [
            "obl-o-artifact",
            "obl-o-changed-files",
            "obl-o-independent-review",
            "obl-o-limitations",
            "obl-o-policy-impact",
            "obl-o-rationale",
            "obl-o-summary",
            "obl-o-test-command"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-adbc24c34d4c5742ac75693c163fd6ee",
          "case_id": "governance-self-mod",
          "actor": "agm-engine",
          "role": "system",
          "source_state": "obligations_compiled",
          "target_state": "evidence_incomplete",
          "action": "mark_evidence_state",
          "reason": "The new case has unsatisfied evidence obligations.",
          "related_object_ids": [
            "obl-o-artifact",
            "obl-o-changed-files",
            "obl-o-limitations",
            "obl-o-policy-impact",
            "obl-o-rationale",
            "obl-o-summary",
            "obl-o-test-command"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        },
        {
          "id": "transition-49f109a2087b5cc0af95fd19bd8c377d",
          "case_id": "governance-self-mod",
          "actor": "contributor-agent",
          "role": "contributor_agent",
          "source_state": "evidence_incomplete",
          "target_state": "awaiting_maintainer_verification",
          "action": "submit_for_verification",
          "reason": "Contributor submitted prepared evidence for maintainer verification.",
          "related_object_ids": [
            "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
            "evidence-ce0afaeb5b845e86aad1586b5ec26707",
            "evidence-e82759bb057254b28e04056067e73c27",
            "evidence-f3b12fad64c450c784e59967d80cf723",
            "evidence-326843434826584ea782e7ff3f48d60c",
            "evidence-3837ecb13fb556e59b8a9cc1f6628332",
            "evidence-5e0da51685f955908b307956f2962e2a"
          ],
          "timestamp": "2026-07-26T00:00:00Z"
        }
      ],
      "final_decision": null,
      "closure_receipt": null,
      "policy_migration_diagnostic": {
        "case_id": "governance-self-mod",
        "policy_changed": false,
        "original_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
        "current_policy_fingerprint": "e8d4a424445f914a36ad726b6f3aec6f0f11fbc6d034faec9de88aedd2318564",
        "still_valid_obligations": [
          "O-ARTIFACT",
          "O-CHANGED-FILES",
          "O-INDEPENDENT-REVIEW",
          "O-LIMITATIONS",
          "O-POLICY-IMPACT",
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
          "O-ARTIFACT": "Provide a locally checkable artifact or test output.",
          "O-CHANGED-FILES": "Identify the files and scopes covered by the contribution.",
          "O-INDEPENDENT-REVIEW": "Require independent maintainer verification with separation of duty.",
          "O-LIMITATIONS": "State known limitations or explicitly state none.",
          "O-POLICY-IMPACT": "Describe policy compatibility, migration, and self-modification impact.",
          "O-RATIONALE": "Explain why the change is needed without disclosing private reasoning.",
          "O-SUMMARY": "Provide a concise factual contribution summary.",
          "O-TEST-COMMAND": "Provide a concrete test command, environment, and outcome."
        },
        "matched_rule_reasons": {
          "governance-policy-high": [
            "path selectors matched: .agm/manifest.yml",
            "governance entrypoints matched: .agm/manifest.yml"
          ],
          "governance-runtime-high": [
            "path selectors matched: src/agm/vnext/risk.py"
          ]
        },
        "interaction_rules": {
          "governance-self-modification": "Policy and its executable governance runtime change together."
        },
        "authority_notice": "Verification or readiness is not acceptance. Final decisions remain with authorized human maintainers."
      }
    },
    "authority_notice": "本页面只把 AGM 的真实状态、依据和合法操作整理成人类可读形式。材料齐备、维护者检查完成，或者已经具备进入最终决定的条件，都不等于代码已经被项目接受。最终决定只属于获授权的人类维护者。",
    "responsibility": {
      "primary_roles": [
        "maintainer"
      ],
      "display_label": "人类维护者",
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
          "O-ARTIFACT",
          "O-CHANGED-FILES",
          "O-INDEPENDENT-REVIEW",
          "O-LIMITATIONS",
          "O-POLICY-IMPACT",
          "O-RATIONALE",
          "O-SUMMARY",
          "O-TEST-COMMAND"
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
            "selector_token": "sel-aa09b9117c3b988e02073aa0fd52c6ba26434dd648d626e5e7ab3a03ae41e430",
            "action": "verify_evidence",
            "label": "可检查的测试输出或文件",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-ARTIFACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-ARTIFACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-ARTIFACT",
              "evidence_ids": [
                "evidence-0a495de0ff0f53c8a9ac58708248bf4c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-548a14860b2f7c38335f89855e79275f8023f6959bc561557d82b58a52dca0d0",
            "action": "verify_evidence",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-ce0afaeb5b845e86aad1586b5ec26707"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-2b4f51341e10ae1d44dd9233c697f996ce05c822e7360e7886b068588d789239",
            "action": "verify_evidence",
            "label": "独立维护者检查",
            "status_label": "缺少；阻止继续",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "object_id": "governance-self-modification",
                "relationship": "source"
              },
              {
                "kind": "interaction_rule",
                "object_id": "governance-self-modification",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-a3938ad06c2f9667c4938ef4a1ee760f439aef1d70d71fc575250e3b4de13188",
            "action": "verify_evidence",
            "label": "已知限制",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-LIMITATIONS"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-LIMITATIONS"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-LIMITATIONS",
              "evidence_ids": [
                "evidence-e82759bb057254b28e04056067e73c27"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-e82759bb057254b28e04056067e73c27",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-6d81f6d13e263ee9825b34ce68cdf56ef7ecdf800adfb4f00dc956db06d7c8e7",
            "action": "verify_evidence",
            "label": "项目规则影响说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-POLICY-IMPACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-POLICY-IMPACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-POLICY-IMPACT",
              "evidence_ids": [
                "evidence-f3b12fad64c450c784e59967d80cf723"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-policy-impact",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-21782ceed543fc369cc0f00b338b47547869b7d3d8c4c1b77ba114fb4cb2e294",
            "action": "verify_evidence",
            "label": "修改原因",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-RATIONALE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-RATIONALE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-RATIONALE",
              "evidence_ids": [
                "evidence-326843434826584ea782e7ff3f48d60c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-429aac5b11df03b21486cc24f48c26dc9b6187ab0cc6f2dc8a221f795c3200f1",
            "action": "verify_evidence",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-3837ecb13fb556e59b8a9cc1f6628332"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-3803be8dca776db13cc3343c3ce8ff5613be015997b522af51ba447e9c52c563",
            "action": "verify_evidence",
            "label": "测试命令与结果",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-TEST-COMMAND"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-TEST-COMMAND"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-TEST-COMMAND",
              "evidence_ids": [
                "evidence-5e0da51685f955908b307956f2962e2a"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
        "default_obligation_ids": [
          "O-INDEPENDENT-REVIEW"
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
            "selector_token": "sel-ce938738951e847ff471957fa1ecb734e70d977c3a9d6c6795b1e0c59187826b",
            "action": "request_repair",
            "label": "可检查的测试输出或文件",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-ARTIFACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-ARTIFACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-ARTIFACT",
              "evidence_ids": [
                "evidence-0a495de0ff0f53c8a9ac58708248bf4c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-5d6334ababab52928e46fc705f59d0872ffa2dc0ea33f5d502f052cdc0a1cb28",
            "action": "request_repair",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-ce0afaeb5b845e86aad1586b5ec26707"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-9baf93e101fbff49983a483189f8de95fcf5b97ebb3c99080404e9ee38225a27",
            "action": "request_repair",
            "label": "独立维护者检查",
            "status_label": "缺少；阻止继续",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "object_id": "governance-self-modification",
                "relationship": "source"
              },
              {
                "kind": "interaction_rule",
                "object_id": "governance-self-modification",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-f379122e0a1f3134cd191ee1524d9686c67c0ed462ba7a9bcaee764cac11375b",
            "action": "request_repair",
            "label": "已知限制",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-LIMITATIONS"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-LIMITATIONS"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-LIMITATIONS",
              "evidence_ids": [
                "evidence-e82759bb057254b28e04056067e73c27"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-e82759bb057254b28e04056067e73c27",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-3bc18cf39bb3e1b327b1dceca67634b3c62eadd41fe9b21961336f65d9e50d41",
            "action": "request_repair",
            "label": "项目规则影响说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-POLICY-IMPACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-POLICY-IMPACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-POLICY-IMPACT",
              "evidence_ids": [
                "evidence-f3b12fad64c450c784e59967d80cf723"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-policy-impact",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-b897f62656fb09fd198ac9ed847e43a44b6fb00769026b98211ae346b5b260d7",
            "action": "request_repair",
            "label": "修改原因",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-RATIONALE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-RATIONALE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-RATIONALE",
              "evidence_ids": [
                "evidence-326843434826584ea782e7ff3f48d60c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-4415aebdbd3335b58ca3523256f14c6ae0984f8905efdda4a299d97af779e608",
            "action": "request_repair",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-3837ecb13fb556e59b8a9cc1f6628332"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-a8b1d3acf740e2dd865e1e56a7e0d84fa76a03efe22e41ee7fa80cb2259b5d82",
            "action": "request_repair",
            "label": "测试命令与结果",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-TEST-COMMAND"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-TEST-COMMAND"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-TEST-COMMAND",
              "evidence_ids": [
                "evidence-5e0da51685f955908b307956f2962e2a"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
            "selector_token": "sel-07c57135e591e818749c16888d7dca83bf3151d191dbac079ee20e5a9c1de043",
            "action": "reject_evidence",
            "label": "可检查的测试输出或文件",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-ARTIFACT"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-0a495de0ff0f53c8a9ac58708248bf4c"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
              "evidence_type": "artifact"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-35d926f8495b27d0933d54cc738f22000b29f77e75d25cc5218b80ca79ccd2be",
            "action": "reject_evidence",
            "label": "变更文件清单",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-CHANGED-FILES"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-ce0afaeb5b845e86aad1586b5ec26707"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
              "evidence_type": "changed_files"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-829c215fce2efcc0bc83f9c70e16685a538d2ebe6c4d2c5a7c222eb2a9d3f340",
            "action": "reject_evidence",
            "label": "已知限制",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-LIMITATIONS"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-e82759bb057254b28e04056067e73c27"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-e82759bb057254b28e04056067e73c27",
              "evidence_type": "known_limitations"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-e82759bb057254b28e04056067e73c27",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-7d76b32e6f2b4625358369d3a5b6ee2708a584de816d4dccceaf4396f21021b6",
            "action": "reject_evidence",
            "label": "项目规则影响说明",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-POLICY-IMPACT"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-f3b12fad64c450c784e59967d80cf723"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-f3b12fad64c450c784e59967d80cf723",
              "evidence_type": "policy_impact"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-998335e3960e82534011ca89a7daefff2ac933e18a86b7ee60d170d5046edca2",
            "action": "reject_evidence",
            "label": "修改原因",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-RATIONALE"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-326843434826584ea782e7ff3f48d60c"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-326843434826584ea782e7ff3f48d60c",
              "evidence_type": "rationale"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-a321e6774250de84a1dcc079e12bf23bee1520f7393b2ae030fe79d6567c0769",
            "action": "reject_evidence",
            "label": "修改说明",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-SUMMARY"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-3837ecb13fb556e59b8a9cc1f6628332"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
              "evidence_type": "contribution_summary"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
                "relationship": "action_target"
              }
            ]
          },
          {
            "selector_token": "sel-8ebe0fa5ce54f1d1cbb8a69f80283ef5ff427f4c7e72c501d98a8fea4011d711",
            "action": "reject_evidence",
            "label": "测试命令与结果",
            "status_label": "当前材料有效，可记录拒绝依据",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-TEST-COMMAND"
            ],
            "object_type": "evidence",
            "object_ids": [
              "evidence-5e0da51685f955908b307956f2962e2a"
            ],
            "blocking": true,
            "material_status": "valid",
            "workflow_status": "",
            "technical_details": {
              "evidence_id": "evidence-5e0da51685f955908b307956f2962e2a",
              "evidence_type": "test_command"
            },
            "traceability": [
              {
                "kind": "evidence",
                "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
          "O-INDEPENDENT-REVIEW"
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
            "selector_token": "sel-ac602e939a4a4baae6266758d5eadb8559d8281e80ceb0e94a783a0c170cc07f",
            "action": "ask_clarification",
            "label": "可检查的测试输出或文件",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-ARTIFACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-ARTIFACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-ARTIFACT",
              "evidence_ids": [
                "evidence-0a495de0ff0f53c8a9ac58708248bf4c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-640d7b2164fa6b8e58a4f2d9a9fa89a43112d6900cecb0b477b5faf4c17e2476",
            "action": "ask_clarification",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-ce0afaeb5b845e86aad1586b5ec26707"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-0e04a216156bd59c4248905a06de03211fb82514f55fa53f984dbd93d4fe6827",
            "action": "ask_clarification",
            "label": "独立维护者检查",
            "status_label": "缺少；阻止继续",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "object_id": "governance-self-modification",
                "relationship": "source"
              },
              {
                "kind": "interaction_rule",
                "object_id": "governance-self-modification",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-b92ae5b3351af07be98f027a1a4b4511e6877f32c735cdef7755ef10d8fb9001",
            "action": "ask_clarification",
            "label": "已知限制",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-LIMITATIONS"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-LIMITATIONS"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-LIMITATIONS",
              "evidence_ids": [
                "evidence-e82759bb057254b28e04056067e73c27"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-e82759bb057254b28e04056067e73c27",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-bd8b61216a25dab8d860123112a6fcfe6a8b883a074d3ef3f537a93ee72226c6",
            "action": "ask_clarification",
            "label": "项目规则影响说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-POLICY-IMPACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-POLICY-IMPACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-POLICY-IMPACT",
              "evidence_ids": [
                "evidence-f3b12fad64c450c784e59967d80cf723"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-policy-impact",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-61178c1ecf4c048fa2b36cba76fc43a02d55b4ccb58997e84d0b1d7d99f3461d",
            "action": "ask_clarification",
            "label": "修改原因",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-RATIONALE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-RATIONALE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-RATIONALE",
              "evidence_ids": [
                "evidence-326843434826584ea782e7ff3f48d60c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-e9ac1e60287168b64773e1821f501b91e8b6a192de0d8a32400fe739803f738c",
            "action": "ask_clarification",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-3837ecb13fb556e59b8a9cc1f6628332"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-5febcb1503c71880d7c04fb0f0b7f92db22e797550264a282bbad803d8f8d0ef",
            "action": "ask_clarification",
            "label": "测试命令与结果",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-TEST-COMMAND"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-TEST-COMMAND"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-TEST-COMMAND",
              "evidence_ids": [
                "evidence-5e0da51685f955908b307956f2962e2a"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
          "O-INDEPENDENT-REVIEW"
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
            "selector_token": "sel-ab9b2c319a358114637a8e3d6027b5024bed7b4a706f13478f13bcb8e173f9d2",
            "action": "record_policy_conflict",
            "label": "可检查的测试输出或文件",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-ARTIFACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-ARTIFACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-ARTIFACT",
              "evidence_ids": [
                "evidence-0a495de0ff0f53c8a9ac58708248bf4c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-b85ee25d24c8f97eabf9e16799ccf6725aa9e835ae74658cab23242e4abde654",
            "action": "record_policy_conflict",
            "label": "变更文件清单",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-ce0afaeb5b845e86aad1586b5ec26707"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-8e7a1534406cfdcc93e4f2bdf91313d74792c29700eda6d47213ed348c16bf4f",
            "action": "record_policy_conflict",
            "label": "独立维护者检查",
            "status_label": "缺少；阻止继续",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "object_id": "governance-self-modification",
                "relationship": "source"
              },
              {
                "kind": "interaction_rule",
                "object_id": "governance-self-modification",
                "relationship": "source"
              }
            ]
          },
          {
            "selector_token": "sel-1d31168826cca5f79be960cb1a21d452778139f55c5f053ec8e47fa35b4ef6f0",
            "action": "record_policy_conflict",
            "label": "已知限制",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-LIMITATIONS"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-LIMITATIONS"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-LIMITATIONS",
              "evidence_ids": [
                "evidence-e82759bb057254b28e04056067e73c27"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-e82759bb057254b28e04056067e73c27",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-89c82b4ebe736ebd3bfb4df5eceee29e77a7d177f4c9d1df2485b44bd9652431",
            "action": "record_policy_conflict",
            "label": "项目规则影响说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-POLICY-IMPACT"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-POLICY-IMPACT"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-POLICY-IMPACT",
              "evidence_ids": [
                "evidence-f3b12fad64c450c784e59967d80cf723"
              ],
              "finding_ids": []
            },
            "traceability": [
              {
                "kind": "compiled_obligation",
                "object_id": "obl-o-policy-impact",
                "relationship": "reference"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-9193eb10e9bc19ccd28c68cd9b00cbe83dc4c709edab392dfe14a62fc7bcb23d",
            "action": "record_policy_conflict",
            "label": "修改原因",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-RATIONALE"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-RATIONALE"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-RATIONALE",
              "evidence_ids": [
                "evidence-326843434826584ea782e7ff3f48d60c"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-4201eca371978ac1067423377249fa88065e09ea73d8d4f43f276328f5567414",
            "action": "record_policy_conflict",
            "label": "修改说明",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
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
                "evidence-3837ecb13fb556e59b8a9cc1f6628332"
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
                "relationship": "observed"
              }
            ]
          },
          {
            "selector_token": "sel-c9d6b8a4ed86047ba54b1836cc2a307548d5ab883cb09730dde240d1c8389cd7",
            "action": "record_policy_conflict",
            "label": "测试命令与结果",
            "status_label": "已提供；已完成",
            "affected_scope": [
              ".agm/manifest.yml",
              "src/agm/vnext/risk.py"
            ],
            "obligation_ids": [
              "O-TEST-COMMAND"
            ],
            "object_type": "obligation",
            "object_ids": [
              "O-TEST-COMMAND"
            ],
            "blocking": true,
            "material_status": "provided",
            "workflow_status": "completed",
            "technical_details": {
              "obligation_id": "O-TEST-COMMAND",
              "evidence_ids": [
                "evidence-5e0da51685f955908b307956f2962e2a"
              ],
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
                "object_id": "governance-policy-high",
                "relationship": "source"
              },
              {
                "kind": "risk_or_profile_rule",
                "object_id": "governance-runtime-high",
                "relationship": "source"
              },
              {
                "kind": "evidence",
                "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
        "output": "# 贡献者待办清单\n\n案例：governance-self-mod\n当前责任方：人类维护者\n原因：贡献侧要求已经满足，当前轮到有权限的维护者检查；检查完成仍不等于接受。\n\n## 待处理项\n\n当前没有需要贡献侧补充或更新的材料。\n\n完成后请按当前 repair/提交范围交回；最终决定仍由人类维护者作出。",
        "trace_refs": [],
        "state_changing": false
      },
      {
        "action_id": "export_reviewer_summary",
        "label": "下载维护者摘要",
        "description": "导出当前风险、责任方和阻断项摘要，不作接受判断。",
        "output_type": "text/markdown",
        "output": "# 维护者审核摘要\n\n案例：governance-self-mod\n当前状态：等待维护者检查\n风险：critical\n当前责任方：人类维护者\n责任方依据：贡献侧要求已经满足，当前轮到有权限的维护者检查；检查完成仍不等于接受。\n\n## 阻断或待检查项\n\n- 独立维护者检查：缺少；阻止继续；范围：.agm/manifest.yml、src/agm/vnext/risk.py\n\n本摘要是治理状态说明，不是接受决定。",
        "trace_refs": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-artifact",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-policy-high",
            "relationship": "source"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-runtime-high",
            "relationship": "source"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
            "relationship": "observed"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-changed-files",
            "relationship": "reference"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
            "relationship": "observed"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-independent-review",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-self-modification",
            "relationship": "source"
          },
          {
            "kind": "interaction_rule",
            "object_id": "governance-self-modification",
            "relationship": "source"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-limitations",
            "relationship": "reference"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-e82759bb057254b28e04056067e73c27",
            "relationship": "observed"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-policy-impact",
            "relationship": "reference"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
            "relationship": "observed"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-rationale",
            "relationship": "reference"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
            "relationship": "observed"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-summary",
            "relationship": "reference"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
            "relationship": "observed"
          },
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-test-command",
            "relationship": "reference"
          },
          {
            "kind": "evidence",
            "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
        "output": "{\n  \"case_id\": \"governance-self-mod\",\n  \"changed_files\": [\n    \".agm/manifest.yml\",\n    \"src/agm/vnext/risk.py\"\n  ],\n  \"matched_risk_rules\": [\n    {\n      \"rule_id\": \"governance-policy-high\",\n      \"zone\": \"project_governance\",\n      \"affected_paths\": [\n        \".agm/manifest.yml\"\n      ]\n    },\n    {\n      \"rule_id\": \"governance-runtime-high\",\n      \"zone\": \"governance_runtime\",\n      \"affected_paths\": [\n        \"src/agm/vnext/risk.py\"\n      ]\n    }\n  ],\n  \"requirement_scopes\": {\n    \"O-ARTIFACT\": [\n      \".agm/manifest.yml\",\n      \"src/agm/vnext/risk.py\"\n    ],\n    \"O-CHANGED-FILES\": [\n      \".agm/manifest.yml\",\n      \"src/agm/vnext/risk.py\"\n    ],\n    \"O-INDEPENDENT-REVIEW\": [\n      \".agm/manifest.yml\",\n      \"src/agm/vnext/risk.py\"\n    ],\n    \"O-LIMITATIONS\": [\n      \".agm/manifest.yml\",\n      \"src/agm/vnext/risk.py\"\n    ],\n    \"O-POLICY-IMPACT\": [\n      \".agm/manifest.yml\",\n      \"src/agm/vnext/risk.py\"\n    ],\n    \"O-RATIONALE\": [\n      \".agm/manifest.yml\",\n      \"src/agm/vnext/risk.py\"\n    ],\n    \"O-SUMMARY\": [\n      \".agm/manifest.yml\",\n      \"src/agm/vnext/risk.py\"\n    ],\n    \"O-TEST-COMMAND\": [\n      \".agm/manifest.yml\",\n      \"src/agm/vnext/risk.py\"\n    ]\n  }\n}",
        "trace_refs": [
          {
            "kind": "matched_rule",
            "object_id": "match-governance-policy-high",
            "relationship": "change_scope"
          },
          {
            "kind": "matched_rule",
            "object_id": "match-governance-runtime-high",
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
        "output": "案例 governance-self-mod 当前交给：人类维护者。\n贡献侧要求已经满足，当前轮到有权限的维护者检查；检查完成仍不等于接受。\n完成后交给角色：人类维护者。",
        "trace_refs": [
          {
            "kind": "compiled_obligation",
            "object_id": "obl-o-independent-review",
            "relationship": "reference"
          },
          {
            "kind": "risk_or_profile_rule",
            "object_id": "governance-self-modification",
            "relationship": "source"
          },
          {
            "kind": "interaction_rule",
            "object_id": "governance-self-modification",
            "relationship": "source"
          }
        ],
        "state_changing": false
      }
    ],
    "materiality_declaration": null,
    "rejected_operation_notice": null
  },
  "trace_index": {
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
        "object_id": "governance-policy-high",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-runtime-high",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
        "relationship": "observed"
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
        "object_id": "governance-policy-high",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-runtime-high",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
        "relationship": "observed"
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
        "object_id": "governance-self-modification",
        "relationship": "source"
      },
      {
        "kind": "interaction_rule",
        "object_id": "governance-self-modification",
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
        "object_id": "governance-policy-high",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-runtime-high",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-e82759bb057254b28e04056067e73c27",
        "relationship": "observed"
      }
    ],
    "trace:requirement:governance-impact": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-policy-impact",
        "relationship": "source"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-policy-impact",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-policy-high",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-runtime-high",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
        "relationship": "observed"
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
        "object_id": "governance-policy-high",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-runtime-high",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
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
        "object_id": "governance-policy-high",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-runtime-high",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
        "relationship": "observed"
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
        "object_id": "governance-policy-high",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-runtime-high",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
        "relationship": "observed"
      }
    ],
    "trace:automatic-check:material_version_binding": [
      {
        "kind": "evidence",
        "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
        "relationship": "material_version_binding"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
        "relationship": "material_version_binding"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-e82759bb057254b28e04056067e73c27",
        "relationship": "material_version_binding"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
        "relationship": "material_version_binding"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
        "relationship": "material_version_binding"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
        "relationship": "material_version_binding"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
        "relationship": "material_version_binding"
      }
    ],
    "trace:automatic-check:test_command_and_result": [
      {
        "kind": "evidence",
        "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
        "relationship": "test_command_and_result"
      }
    ],
    "trace:automatic-check:test_version_binding": [
      {
        "kind": "evidence",
        "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
        "relationship": "test_version_binding"
      }
    ],
    "trace:automatic-check:evidence_freshness": [
      {
        "kind": "evidence",
        "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
        "relationship": "evidence_freshness"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
        "relationship": "evidence_freshness"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-e82759bb057254b28e04056067e73c27",
        "relationship": "evidence_freshness"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
        "relationship": "evidence_freshness"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
        "relationship": "evidence_freshness"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
        "relationship": "evidence_freshness"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
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
        "object_id": "evidence-0a495de0ff0f53c8a9ac58708248bf4c",
        "relationship": "structural_obligations"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-ce0afaeb5b845e86aad1586b5ec26707",
        "relationship": "structural_obligations"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-e82759bb057254b28e04056067e73c27",
        "relationship": "structural_obligations"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
        "relationship": "structural_obligations"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
        "relationship": "structural_obligations"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-3837ecb13fb556e59b8a9cc1f6628332",
        "relationship": "structural_obligations"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-5e0da51685f955908b307956f2962e2a",
        "relationship": "structural_obligations"
      }
    ],
    "trace:automatic-check:semantic_declaration_consistency": [
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
        "object_id": "obl-o-policy-impact",
        "relationship": "semantic_declaration_consistency"
      },
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-rationale",
        "relationship": "semantic_declaration_consistency"
      }
    ],
    "trace:judgment:independent-review": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-independent-review",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-self-modification",
        "relationship": "source"
      },
      {
        "kind": "interaction_rule",
        "object_id": "governance-self-modification",
        "relationship": "source"
      }
    ],
    "trace:judgment:known-limitations": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-limitations",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-policy-high",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-runtime-high",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-e82759bb057254b28e04056067e73c27",
        "relationship": "observed"
      }
    ],
    "trace:judgment:governance-impact": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-policy-impact",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-policy-high",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-runtime-high",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-f3b12fad64c450c784e59967d80cf723",
        "relationship": "observed"
      }
    ],
    "trace:judgment:change-rationale": [
      {
        "kind": "compiled_obligation",
        "object_id": "obl-o-rationale",
        "relationship": "reference"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-policy-high",
        "relationship": "source"
      },
      {
        "kind": "risk_or_profile_rule",
        "object_id": "governance-runtime-high",
        "relationship": "source"
      },
      {
        "kind": "evidence",
        "object_id": "evidence-326843434826584ea782e7ff3f48d60c",
        "relationship": "observed"
      }
    ]
  }
}
```

</details>
