# AGM Reviewer Guidance Layer

- 案例: `material-partial`
- 本次路径: 轻量审核
- 当前阶段: 等待贡献侧补齐或更新材料
- 风险: 低
- 阻断问题: 1
- 需要关注: 0
- 当前责任方: 贡献者、贡献侧智能体
- 责任方依据: 受影响材料尚未准备或更新完成，当前还不能进入维护者检查。

## 五步流程

1. ✓ **系统识别要求** — 已完成：适用规则和本次要求已由 AGM 引擎生成。
2. ↺ **贡献者准备材料** — 返回修改：补交后仍有缺失、过时或无效材料，需要贡献侧继续处理。
3. — **负责人确认** — 本次不要求：当前义务集合不要求负责人确认。
4. ↺ **维护者检查** — 返回修改：受影响材料尚未齐备，当前不能开始重新检查。
5. ○ **人类维护者最终决定** — 尚未开始：前序治理要求完成后才进入最终决定。

## 项目要求对比

| 检查项 | 项目要求 | 当前情况 | 材料状态 | 流程状态 |
| --- | --- | --- | --- | --- |
| 智能体行动与委派说明 | 说明智能体做了什么、用了哪些权限、是否有人监督，以及是否把具有独立行动能力的工作继续交给了另一个智能体。 | 已提供与当前贡献和项目规则绑定的材料。 | 仍然有效 | 已完成 |
| 变更文件清单 | 列出这次修改涉及的文件和范围。 | 已提供与当前贡献和项目规则绑定的材料。 | 仍然有效 | 已完成 |
| 修改说明 | 简要说明这次修改做了什么。 | 现有材料对应旧版本或已过有效期，需要更新后再继续。 | 需要更新 | 等待贡献者处理 |

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
  - 检查待核验项: 这些项目的材料或负责人确认尚未满足，当前不能核验：O-SUMMARY
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
  "authorized": false,
  "authorization_reason": "这些项目的材料或负责人确认尚未满足，当前不能核验：O-SUMMARY",
  "source_state": "resubmitted",
  "target_state": "resubmitted",
  "effects": [],
  "affected_obligation_ids": [
    "O-SUMMARY"
  ],
  "retained_evidence_ids": [
    "evidence-ff9a84de45064d098b889c7a8b04c52f",
    "evidence-4790b765290e447d92c34a364a38d36b"
  ],
  "invalidated_attestation_ids": [],
  "next_authorized_actor_roles": [
    "contributor",
    "contributor_agent"
  ],
  "requires_confirmation": false,
  "mutates_case": false,
  "preview_fingerprint": "69298465fceed0695549f5cdfc33431ef4ef45657532df9d048b0e26b599a93b",
  "traceability": [
    {
      "kind": "permission_rule",
      "object_id": "maintainer_verifier:verify_evidence",
      "relationship": "authority"
    },
    {
      "kind": "governance_case",
      "object_id": "material-partial",
      "relationship": "source_state"
    },
    {
      "kind": "state_machine_rule",
      "object_id": "resubmitted:verify_evidence:verification_complete",
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
      "contributor",
      "contributor_agent"
    ],
    "display_label": "贡献者、贡献侧智能体",
    "reason": "受影响材料尚未准备或更新完成，当前还不能进入维护者检查。",
    "blocking_items": [
      "修改说明"
    ],
    "next_handoff_roles": [
      "accountable_human",
      "maintainer_verifier",
      "maintainer"
    ]
  },
  "workflow_step_before": "prepare_materials",
  "workflow_step_after": "prepare_materials",
  "creates_records": [],
  "requires_human_attestation_after": false,
  "requires_maintainer_verification_after": true,
  "final_acceptance_recorded": false,
  "final_acceptance_still_required": true
}
```
