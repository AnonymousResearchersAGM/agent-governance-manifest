# AGM Reviewer Guidance Layer

- 案例: `policy-migration`
- 本次路径: 轻量审核
- 当前阶段: 等待贡献侧补齐或更新材料
- 风险: 低
- 阻断问题: 2
- 需要关注: 1
- 当前责任方: 贡献者、贡献侧智能体
- 责任方依据: 受影响材料尚未准备或更新完成，当前还不能进入维护者检查。

## 五步流程

1. ✓ **系统识别要求** — 已完成：适用规则和本次要求已由 AGM 引擎生成。
2. ● **贡献者准备材料** — 当前阶段：贡献者正在准备或补齐本次所需材料。
3. — **负责人确认** — 本次不要求：当前义务集合不要求负责人确认。
4. ○ **维护者检查** — 尚未开始：贡献侧要求完成后才进入维护者检查。
5. ○ **人类维护者最终决定** — 尚未开始：前序治理要求完成后才进入最终决定。

## 项目要求对比

| 检查项 | 项目要求 | 当前情况 | 材料状态 | 流程状态 |
| --- | --- | --- | --- | --- |
| 变更文件清单 | 列出这次修改涉及的文件和范围。 | 尚未提供。 | 缺少 | 等待贡献者处理 |
| 修改说明 | 简要说明这次修改做了什么。 | 尚未提供。 | 缺少 | 等待贡献者处理 |

## 当前相关操作

- 当前角色没有直接改变状态的相关操作；可使用下方只读交接工具。

## 其他可用操作（折叠区内容）

- **查看变化范围**: 只读操作，不改变案例状态。
- **记录项目规则冲突**: 案例转入 repair，由 policy steward 或维护者处理。

## 只读交接工具

- **复制缺失项清单**: 生成可直接交给贡献侧的缺失、过时或无效材料清单。
- **导出贡献者待办清单**: 导出包含责任方、待处理项和范围的 Markdown 清单。
- **下载维护者摘要**: 导出当前风险、责任方和阻断项摘要，不作接受判断。
- **查看变化范围**: 查看变更文件、匹配规则和各要求的影响范围。
- **复制当前责任方说明**: 生成不改变案例状态的 handoff note。

## 暂不可用操作摘要

- 还有 13 项操作因当前阶段、权限或对象范围暂不可用
  - 检查待核验项: 操作 verify_evidence 不能从当前状态 evidence_incomplete 执行。
  - 请求补充或更新材料: 操作 request_repair 不能从当前状态 evidence_incomplete 执行。
  - 拒绝无效材料: 当前角色没有 reject_evidence 权限。 可执行角色：maintainer, maintainer_verifier。
  - 请求说明: 当前角色没有 ask_clarification 权限。 可执行角色：maintainer, maintainer_verifier。
  - 要求负责人重新确认: 当前角色没有 invalidate_attestation 权限。 可执行角色：maintainer, maintainer_verifier。
  - 解决项目规则冲突: 操作 resolve_policy_conflict 不能从当前状态 evidence_incomplete 执行。
  - 补交指定范围: 当前角色没有 resubmit 权限。 可执行角色：contributor, contributor_agent。
  - 负责人确认当前范围: 当前角色没有 confirm_attestation 权限。 可执行角色：accountable_human。
  - 执行有权覆盖: 当前角色没有 authorized_override 权限。 可执行角色：maintainer。
  - 提交人类最终接受决定: 当前角色没有 decide_accept 权限。 可执行角色：maintainer。
  - 提交人类最终拒绝决定: 当前角色没有 decide_reject 权限。 可执行角色：maintainer。
  - 提交人类修改决定: 当前角色没有 decide_request_changes 权限。 可执行角色：maintainer。
  - 关闭案例: 当前角色没有 decide_close 权限。 可执行角色：maintainer。

## Authority boundary

本页面只把 AGM 的真实状态、依据和合法操作整理成人类可读形式。材料齐备、核验完成或 eligible 均不等于接受；最终决定只属于获授权的人类维护者。


## 操作预览

```json
{
  "action": "record_policy_conflict",
  "title": "记录项目规则冲突",
  "actor": {
    "actor": "policy-reviewer",
    "role": "policy_steward",
    "human": true
  },
  "authorized": true,
  "authorization_reason": "当前角色和案例状态允许生成此操作计划。",
  "source_state": "evidence_incomplete",
  "target_state": "repair_requested",
  "effects": [
    {
      "target": "案例状态",
      "before": "evidence_incomplete",
      "after": "repair_requested",
      "explanation": "案例转入 repair，由 policy steward 或维护者处理。",
      "source_object_ids": [
        "transition-a3387af59dfd4db28c555a80ea33bc6d"
      ]
    },
    {
      "target": "O-SUMMARY",
      "before": "unsatisfied",
      "after": "policy_conflict",
      "explanation": "案例转入 repair，由 policy steward 或维护者处理。",
      "source_object_ids": [
        "obl-o-summary"
      ]
    }
  ],
  "affected_obligation_ids": [
    "O-SUMMARY"
  ],
  "retained_evidence_ids": [],
  "invalidated_attestation_ids": [],
  "next_authorized_actor_roles": [
    "policy_steward",
    "maintainer"
  ],
  "requires_confirmation": true,
  "mutates_case": false,
  "preview_fingerprint": "00e0d82c9c29a56cdf8e4d7e5dcb078ddf8b0561119be2c73f2e5d11576a2fea",
  "traceability": [
    {
      "kind": "permission_rule",
      "object_id": "policy_steward:record_policy_conflict",
      "relationship": "authority"
    },
    {
      "kind": "governance_case",
      "object_id": "policy-migration",
      "relationship": "source_state"
    },
    {
      "kind": "state_machine_rule",
      "object_id": "evidence_incomplete:record_policy_conflict:repair_requested",
      "relationship": "transition_plan"
    }
  ],
  "processed_objects": [
    "O-SUMMARY"
  ],
  "invalidated_evidence_ids": [],
  "responsibility_before": {
    "primary_roles": [
      "contributor",
      "contributor_agent"
    ],
    "display_label": "贡献者、贡献侧智能体",
    "reason": "受影响材料尚未准备或更新完成，当前还不能进入维护者检查。",
    "blocking_items": [
      "变更文件清单",
      "修改说明"
    ],
    "next_handoff_roles": [
      "accountable_human",
      "maintainer_verifier",
      "maintainer"
    ]
  },
  "responsibility_after": {
    "primary_roles": [
      "policy_steward",
      "maintainer"
    ],
    "display_label": "项目规则负责人、人类维护者",
    "reason": "项目规则之间存在未解决冲突，需要具备相应权限的人类角色先记录解决依据。",
    "blocking_items": [
      "修改说明"
    ],
    "next_handoff_roles": [
      "contributor",
      "maintainer_verifier"
    ]
  },
  "workflow_step_before": "prepare_materials",
  "workflow_step_after": "prepare_materials",
  "creates_records": [
    "state_transition",
    "finding",
    "repair_request"
  ],
  "requires_human_attestation_after": false,
  "requires_maintainer_verification_after": true,
  "final_acceptance_recorded": false,
  "final_acceptance_still_required": true
}
```
