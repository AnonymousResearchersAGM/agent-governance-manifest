# AGM Reviewer Guidance Layer

- 案例: `human-final-closure`
- 本次路径: 轻量审核
- 当前阶段: 人类维护者已接受并关闭
- 风险: 低
- 阻断问题: 0
- 需要关注: 0
- 当前责任方: 流程已结束
- 责任方依据: 人类最终决定和关闭记录已经生成，当前没有待交接操作。

## 五步流程

1. ✓ **系统识别要求** — 已完成：适用规则和本次要求已由 AGM 引擎生成。
2. ✓ **贡献者准备材料** — 已完成：本次所需材料已提交到后续流程。
3. — **负责人确认** — 本次不要求：当前义务集合不要求负责人确认。
4. ✓ **维护者检查** — 已完成：维护者核验阶段已完成；这不等于接受贡献。
5. ✓ **人类维护者最终决定** — 已完成：已记录人类维护者最终决定和关闭信息。

## 项目要求对比

| 检查项 | 项目要求 | 当前情况 | 材料状态 | 流程状态 |
| --- | --- | --- | --- | --- |
| 变更文件清单 | 列出这次修改涉及的文件和范围。 | 材料已由具备权限的维护者完成检查。 | 已检查 | 已完成 |
| 修改说明 | 简要说明这次修改做了什么。 | 材料已由具备权限的维护者完成检查。 | 已检查 | 已完成 |

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
  - 检查待核验项: 操作 verify_evidence 不能从当前状态 accepted 执行。
  - 请求补充或更新材料: 操作 request_repair 不能从当前状态 accepted 执行。
  - 拒绝无效材料: 操作 reject_evidence 不能从当前状态 accepted 执行。
  - 请求说明: 操作 ask_clarification 不能从当前状态 accepted 执行。
  - 要求负责人重新确认: 操作 invalidate_attestation 不能从当前状态 accepted 执行。
  - 记录项目规则冲突: 操作 record_policy_conflict 不能从当前状态 accepted 执行。
  - 解决项目规则冲突: 操作 resolve_policy_conflict 不能从当前状态 accepted 执行。
  - 补交指定范围: 当前角色没有 resubmit 权限。 可执行角色：contributor, contributor_agent。
  - 负责人确认当前范围: 当前角色没有 confirm_attestation 权限。 可执行角色：accountable_human。
  - 执行有权覆盖: 操作 authorized_override 不能从当前状态 accepted 执行。
  - 提交人类最终接受决定: 操作 decide_accept 不能从当前状态 accepted 执行。
  - 提交人类最终拒绝决定: 操作 decide_reject 不能从当前状态 accepted 执行。
  - 提交人类修改决定: 操作 decide_request_changes 不能从当前状态 accepted 执行。
  - 关闭案例: 操作 decide_close 不能从当前状态 accepted 执行。

## Authority boundary

本页面只把 AGM 的真实状态、依据和合法操作整理成人类可读形式。材料齐备、核验完成或 eligible 均不等于接受；最终决定只属于获授权的人类维护者。


## 操作预览

```json
{
  "action": "decide_accept",
  "title": "提交人类最终接受决定",
  "actor": {
    "actor": "human-maintainer",
    "role": "maintainer",
    "human": true
  },
  "authorized": true,
  "authorization_reason": "当前角色和案例状态允许生成此操作计划。",
  "source_state": "ready_for_human_decision",
  "target_state": "accepted",
  "effects": [
    {
      "target": "案例状态",
      "before": "ready_for_human_decision",
      "after": "accepted",
      "explanation": "案例 accepted 并生成 closure receipt；该动作不是自动合并。",
      "source_object_ids": [
        "transition-0414510c7de148938a0f053c5c00dc26"
      ]
    }
  ],
  "affected_obligation_ids": [],
  "retained_evidence_ids": [
    "evidence-cf1485b25c004cd18f9602db67ef8a08",
    "evidence-9c501fe370294e6ca5e307a9b6c9c755"
  ],
  "invalidated_attestation_ids": [],
  "next_authorized_actor_roles": [],
  "requires_confirmation": true,
  "mutates_case": false,
  "preview_fingerprint": "2a014cb9eef33a65ece8483c33ba0139875ec110f763de906f27c3f589f5d5c9",
  "traceability": [
    {
      "kind": "permission_rule",
      "object_id": "maintainer:decide_accept",
      "relationship": "authority"
    },
    {
      "kind": "governance_case",
      "object_id": "human-final-closure",
      "relationship": "source_state"
    },
    {
      "kind": "state_machine_rule",
      "object_id": "ready_for_human_decision:decide_accept:accepted",
      "relationship": "transition_plan"
    }
  ],
  "processed_objects": [],
  "invalidated_evidence_ids": [],
  "responsibility_before": {
    "primary_roles": [
      "maintainer"
    ],
    "display_label": "人类维护者",
    "reason": "治理检查已经达到可决策状态，但最终接受、拒绝或要求修改仍须由人类维护者明确记录。",
    "blocking_items": [],
    "next_handoff_roles": []
  },
  "responsibility_after": {
    "primary_roles": [],
    "display_label": "流程已结束",
    "reason": "人类最终决定和关闭记录已经生成，当前没有待交接操作。",
    "blocking_items": [],
    "next_handoff_roles": []
  },
  "workflow_step_before": "human_final_decision",
  "workflow_step_after": "human_final_decision",
  "creates_records": [
    "state_transition",
    "final_decision",
    "closure_receipt"
  ],
  "requires_human_attestation_after": false,
  "requires_maintainer_verification_after": false,
  "final_acceptance_recorded": true,
  "final_acceptance_still_required": false
}
```
