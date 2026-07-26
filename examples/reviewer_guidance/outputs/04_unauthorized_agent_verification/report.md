# AGM Reviewer Guidance Layer

- 案例: `unauthorized-agent`
- 本次路径: 轻量审核
- 当前阶段: 等待维护者检查
- 风险: 低
- 阻断问题: 0
- 需要关注: 0
- 当前责任方: 维护者核验人、项目规则负责人、人类维护者
- 责任方依据: 贡献侧要求已经满足，当前轮到有权限的维护者检查；检查完成仍不等于接受。

## 五步流程

1. ✓ **系统识别要求** — 已完成：适用规则和本次要求已由 AGM 引擎生成。
2. ✓ **贡献者准备材料** — 已完成：本次所需材料已提交到后续流程。
3. — **负责人确认** — 本次不要求：当前义务集合不要求负责人确认。
4. ● **维护者检查** — 当前阶段：当前轮到有权限的维护者检查材料与绑定。
5. ○ **人类维护者最终决定** — 尚未开始：前序治理要求完成后才进入最终决定。

## 项目要求对比

| 检查项 | 项目要求 | 当前情况 | 材料状态 | 流程状态 |
| --- | --- | --- | --- | --- |
| 变更文件清单 | 列出这次修改涉及的文件和范围。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |
| 修改说明 | 简要说明这次修改做了什么。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |

## 当前相关操作

- 当前角色没有直接改变状态的相关操作；可使用下方只读交接工具。

## 其他可用操作（折叠区内容）

- **查看变化范围**: 只读操作，不改变案例状态。

## 只读交接工具

- **复制缺失项清单**: 生成可直接交给贡献侧的缺失、过时或无效材料清单。
- **导出贡献者待办清单**: 导出包含责任方、待处理项和范围的 Markdown 清单。
- **下载维护者摘要**: 导出当前风险、责任方和阻断项摘要，不作接受判断。
- **查看变化范围**: 查看变更文件、匹配规则和各要求的影响范围。
- **复制当前责任方说明**: 生成不改变案例状态的 handoff note。

## 暂不可用操作摘要

- 还有 14 项操作因当前阶段、权限或对象范围暂不可用
  - 检查待核验项: 当前角色没有 verify_evidence 权限。 可执行角色：maintainer, maintainer_verifier, policy_steward。
  - 请求补充或更新材料: 当前角色没有 request_repair 权限。 可执行角色：maintainer, maintainer_verifier, policy_steward。
  - 拒绝无效材料: 当前角色没有 reject_evidence 权限。 可执行角色：maintainer, maintainer_verifier。
  - 请求说明: 当前角色没有 ask_clarification 权限。 可执行角色：maintainer, maintainer_verifier。
  - 要求负责人重新确认: 当前角色没有 invalidate_attestation 权限。 可执行角色：maintainer, maintainer_verifier。
  - 记录项目规则冲突: 当前角色没有 record_policy_conflict 权限。 可执行角色：maintainer, maintainer_verifier, policy_steward。
  - 解决项目规则冲突: 当前角色没有 resolve_policy_conflict 权限。 可执行角色：maintainer, policy_steward。
  - 补交指定范围: 操作 resubmit 不能从当前状态 awaiting_maintainer_verification 执行。
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
    "actor": "contributor-agent",
    "role": "contributor_agent",
    "human": false
  },
  "authorized": false,
  "authorization_reason": "当前角色没有 verify_evidence 权限。 可执行角色：maintainer, maintainer_verifier, policy_steward。",
  "source_state": "awaiting_maintainer_verification",
  "target_state": "awaiting_maintainer_verification",
  "effects": [],
  "affected_obligation_ids": [
    "O-CHANGED-FILES",
    "O-SUMMARY"
  ],
  "retained_evidence_ids": [],
  "invalidated_attestation_ids": [],
  "next_authorized_actor_roles": [
    "maintainer_verifier",
    "policy_steward",
    "maintainer"
  ],
  "requires_confirmation": false,
  "mutates_case": false,
  "preview_fingerprint": "13d1b45b657460e2a97074de2c561ecf6439b3b3b2c55b11511d144e50cad9a7",
  "traceability": [
    {
      "kind": "permission_rule",
      "object_id": "contributor_agent:verify_evidence",
      "relationship": "authority"
    },
    {
      "kind": "governance_case",
      "object_id": "unauthorized-agent",
      "relationship": "source_state"
    },
    {
      "kind": "state_machine_rule",
      "object_id": "awaiting_maintainer_verification:verify_evidence:verification_complete",
      "relationship": "transition_plan"
    }
  ],
  "processed_objects": [
    "O-CHANGED-FILES",
    "O-SUMMARY"
  ],
  "invalidated_evidence_ids": [],
  "responsibility_before": {
    "primary_roles": [
      "maintainer_verifier",
      "policy_steward",
      "maintainer"
    ],
    "display_label": "维护者核验人、项目规则负责人、人类维护者",
    "reason": "贡献侧要求已经满足，当前轮到有权限的维护者检查；检查完成仍不等于接受。",
    "blocking_items": [],
    "next_handoff_roles": [
      "maintainer"
    ]
  },
  "responsibility_after": {
    "primary_roles": [
      "maintainer_verifier",
      "policy_steward",
      "maintainer"
    ],
    "display_label": "维护者核验人、项目规则负责人、人类维护者",
    "reason": "贡献侧要求已经满足，当前轮到有权限的维护者检查；检查完成仍不等于接受。",
    "blocking_items": [],
    "next_handoff_roles": [
      "maintainer"
    ]
  },
  "workflow_step_before": "maintainer_check",
  "workflow_step_after": "maintainer_check",
  "creates_records": [],
  "requires_human_attestation_after": false,
  "requires_maintainer_verification_after": true,
  "final_acceptance_recorded": false,
  "final_acceptance_still_required": true
}
```
