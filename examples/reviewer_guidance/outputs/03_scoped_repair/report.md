# AGM Reviewer Guidance Layer

- 案例: `scoped-repair`
- 本次路径: 轻量审核
- 当前阶段: 等待维护者重新检查指定范围
- 风险: 低
- 阻断问题: 1
- 需要关注: 0
- 当前责任方: 维护者核验人、项目规则负责人、人类维护者
- 责任方依据: 受影响材料已补充或仍然有效；当前只需重新检查指定修复范围。

## 五步流程

1. ✓ **系统识别要求** — 已完成：适用规则和本次要求已由 AGM 引擎生成。
2. ✓ **贡献者准备材料** — 已完成：指定范围已补交并具备可检查材料，未受影响材料继续保留。
3. — **负责人确认** — 本次不要求：当前义务集合不要求负责人确认。
4. ● **维护者检查** — 当前阶段：当前只重新检查指定修复范围；未受影响的检查结果保留。
5. ○ **人类维护者最终决定** — 尚未开始：前序治理要求完成后才进入最终决定。

## 项目要求对比

| 检查项 | 项目要求 | 当前情况 | 材料状态 | 流程状态 |
| --- | --- | --- | --- | --- |
| 智能体行动与委派说明 | 说明智能体做了什么、用了哪些权限、是否有人监督，以及是否把具有独立行动能力的工作继续交给了另一个智能体。 | 材料已补充或仍然有效；当前等待维护者重新检查这一项。 | 已提供 | 等待维护者重新检查 |
| 变更文件清单 | 列出这次修改涉及的文件和范围。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |
| 修改说明 | 简要说明这次修改做了什么。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |

## 当前相关操作

- **检查待核验项** (`verify_evidence`): 受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。

## 其他可用操作（折叠区内容）

- **查看变化范围**: 只读操作，不改变案例状态。

## 只读交接工具

- **复制缺失项清单**: 生成可直接交给贡献侧的缺失、过时或无效材料清单。
- **导出贡献者待办清单**: 导出包含责任方、待处理项和范围的 Markdown 清单。
- **下载维护者摘要**: 导出当前风险、责任方和阻断项摘要，不作接受判断。
- **查看变化范围**: 查看变更文件、匹配规则和各要求的影响范围。
- **复制当前责任方说明**: 生成不改变案例状态的 handoff note。

## 暂不可用操作摘要

- 还有 13 项操作因当前阶段、权限或对象范围暂不可用
  - 请求补充或更新材料: 操作 request_repair 不能从当前状态 resubmitted 执行。
  - 拒绝无效材料: 操作 reject_evidence 不能从当前状态 resubmitted 执行。
  - 请求说明: 操作 ask_clarification 不能从当前状态 resubmitted 执行。
  - 要求负责人重新确认: 操作 invalidate_attestation 不能从当前状态 resubmitted 执行。
  - 记录项目规则冲突: 操作 record_policy_conflict 不能从当前状态 resubmitted 执行。
  - 解决项目规则冲突: 当前角色没有 resolve_policy_conflict 权限。 可执行角色：maintainer, policy_steward。
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
  "action": "verify_evidence",
  "title": "检查待核验项",
  "actor": {
    "actor": "verifier-1",
    "role": "maintainer_verifier",
    "human": true
  },
  "authorized": true,
  "authorization_reason": "当前角色和案例状态允许生成此操作计划。",
  "source_state": "resubmitted",
  "target_state": "ready_for_human_decision",
  "effects": [
    {
      "target": "案例状态",
      "before": "resubmitted",
      "after": "ready_for_human_decision",
      "explanation": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
      "source_object_ids": [
        "transition-edb55a1ee0c543c490e4363341dfcd4e"
      ]
    },
    {
      "target": "O-AGENT-SCOPE",
      "before": "satisfied",
      "after": "verified",
      "explanation": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
      "source_object_ids": [
        "obl-o-agent-scope"
      ]
    },
    {
      "target": "指定修复请求",
      "before": "resubmitted",
      "after": "resolved",
      "explanation": "所关联的问题在本次重新检查后关闭。",
      "source_object_ids": [
        "repair-fcae5dc548bb4440848e80210d229a8e"
      ]
    }
  ],
  "affected_obligation_ids": [
    "O-AGENT-SCOPE"
  ],
  "retained_evidence_ids": [
    "evidence-52d1959b65174b11a46526b31074ae80",
    "evidence-4544e6c323e945d7b96b3d602e6856d5"
  ],
  "invalidated_attestation_ids": [],
  "next_authorized_actor_roles": [
    "maintainer"
  ],
  "requires_confirmation": true,
  "mutates_case": false,
  "preview_fingerprint": "1b84357f01fa0924d5792f4b431cbe3cefef7ba2bfabfb30b462c3d348148da2",
  "traceability": [
    {
      "kind": "permission_rule",
      "object_id": "maintainer_verifier:verify_evidence",
      "relationship": "authority"
    },
    {
      "kind": "governance_case",
      "object_id": "scoped-repair",
      "relationship": "source_state"
    },
    {
      "kind": "state_machine_rule",
      "object_id": "resubmitted:verify_evidence:verification_complete",
      "relationship": "transition_plan"
    }
  ],
  "processed_objects": [
    "O-AGENT-SCOPE"
  ],
  "invalidated_evidence_ids": [],
  "responsibility_before": {
    "primary_roles": [
      "maintainer_verifier",
      "policy_steward",
      "maintainer"
    ],
    "display_label": "维护者核验人、项目规则负责人、人类维护者",
    "reason": "受影响材料已补充或仍然有效；当前只需重新检查指定修复范围。",
    "blocking_items": [
      "智能体行动与委派说明"
    ],
    "next_handoff_roles": [
      "maintainer"
    ]
  },
  "responsibility_after": {
    "primary_roles": [
      "maintainer"
    ],
    "display_label": "人类维护者",
    "reason": "治理检查已经达到可决策状态，但最终接受、拒绝或要求修改仍须由人类维护者明确记录。",
    "blocking_items": [],
    "next_handoff_roles": []
  },
  "workflow_step_before": "maintainer_check",
  "workflow_step_after": "human_final_decision",
  "creates_records": [
    "state_transition",
    "maintainer_verification"
  ],
  "requires_human_attestation_after": false,
  "requires_maintainer_verification_after": false,
  "final_acceptance_recorded": false,
  "final_acceptance_still_required": true
}
```
