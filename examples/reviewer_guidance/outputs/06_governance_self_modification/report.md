# AGM Reviewer Guidance Layer

- 案例: `governance-self-mod`
- 本次路径: 完整治理流程
- 当前阶段: 等待维护者检查
- 风险: 关键
- 阻断问题: 0
- 需要关注: 0
- 当前责任方: 人类维护者
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
| 可核验测试制品 | 提供可以实际检查的测试输出或文件。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |
| 变更文件清单 | 列出这次修改涉及的文件和范围。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |
| 独立维护者检查 | 由另一名具备权限且与贡献侧分离的维护者独立检查。 | 前序材料满足后，由具备权限且与贡献侧分离的维护者检查。 | 缺少 | 阻止继续 |
| 已知限制 | 说明已知限制；没有已知限制也要明确说明。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |
| 项目规则与治理影响 | 说明本次修改是否影响项目规则或治理流程。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |
| 修改理由 | 说明为什么需要这次修改。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |
| 修改说明 | 简要说明这次修改做了什么。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |
| 测试命令与结果 | 提供测试命令、运行环境和实际结果。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |

## 当前相关操作

- **检查待核验项** (`verify_evidence`): 受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。
- **请求补充或更新材料** (`request_repair`): 仅指定范围需要修复和重新检查，未受影响材料保留。
- **拒绝无效材料** (`reject_evidence`): 该材料标记为 rejected，并建立 scoped repair。
- **请求说明** (`ask_clarification`): 案例返回贡献侧回答，所选范围需要重新检查。

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

- 还有 9 项操作因当前阶段、权限或对象范围暂不可用
  - 要求负责人重新确认: 当前没有仍然有效的负责人确认可供失效处理。
  - 解决项目规则冲突: 操作 resolve_policy_conflict 不能从当前状态 awaiting_maintainer_verification 执行。
  - 补交指定范围: 当前角色没有 resubmit 权限。 可执行角色：contributor, contributor_agent。
  - 负责人确认当前范围: 当前角色没有 confirm_attestation 权限。 可执行角色：accountable_human。
  - 执行有权覆盖: 操作 authorized_override 不能从当前状态 awaiting_maintainer_verification 执行。
  - 提交人类最终接受决定: 操作 decide_accept 不能从当前状态 awaiting_maintainer_verification 执行。
  - 提交人类最终拒绝决定: 操作 decide_reject 不能从当前状态 awaiting_maintainer_verification 执行。
  - 提交人类修改决定: 操作 decide_request_changes 不能从当前状态 awaiting_maintainer_verification 执行。
  - 关闭案例: 操作 decide_close 不能从当前状态 awaiting_maintainer_verification 执行。

## Authority boundary

本页面只把 AGM 的真实状态、依据和合法操作整理成人类可读形式。材料齐备、核验完成或 eligible 均不等于接受；最终决定只属于获授权的人类维护者。


## 操作预览

```json
{
  "action": "verify_evidence",
  "title": "检查待核验项",
  "actor": {
    "actor": "independent-maintainer",
    "role": "maintainer",
    "human": true
  },
  "authorized": true,
  "authorization_reason": "当前角色和案例状态允许生成此操作计划。",
  "source_state": "awaiting_maintainer_verification",
  "target_state": "ready_for_human_decision",
  "effects": [
    {
      "target": "案例状态",
      "before": "awaiting_maintainer_verification",
      "after": "ready_for_human_decision",
      "explanation": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
      "source_object_ids": [
        "transition-01e145b640864caba91d7a8ee2a41bf6"
      ]
    },
    {
      "target": "O-ARTIFACT",
      "before": "satisfied",
      "after": "verified",
      "explanation": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
      "source_object_ids": [
        "obl-o-artifact"
      ]
    },
    {
      "target": "O-CHANGED-FILES",
      "before": "satisfied",
      "after": "verified",
      "explanation": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
      "source_object_ids": [
        "obl-o-changed-files"
      ]
    },
    {
      "target": "O-INDEPENDENT-REVIEW",
      "before": "unsatisfied",
      "after": "verified",
      "explanation": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
      "source_object_ids": [
        "obl-o-independent-review"
      ]
    },
    {
      "target": "O-LIMITATIONS",
      "before": "satisfied",
      "after": "verified",
      "explanation": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
      "source_object_ids": [
        "obl-o-limitations"
      ]
    },
    {
      "target": "O-POLICY-IMPACT",
      "before": "satisfied",
      "after": "verified",
      "explanation": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
      "source_object_ids": [
        "obl-o-policy-impact"
      ]
    },
    {
      "target": "O-RATIONALE",
      "before": "satisfied",
      "after": "verified",
      "explanation": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
      "source_object_ids": [
        "obl-o-rationale"
      ]
    },
    {
      "target": "O-SUMMARY",
      "before": "satisfied",
      "after": "verified",
      "explanation": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
      "source_object_ids": [
        "obl-o-summary"
      ]
    },
    {
      "target": "O-TEST-COMMAND",
      "before": "satisfied",
      "after": "verified",
      "explanation": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
      "source_object_ids": [
        "obl-o-test-command"
      ]
    }
  ],
  "affected_obligation_ids": [
    "O-ARTIFACT",
    "O-CHANGED-FILES",
    "O-INDEPENDENT-REVIEW",
    "O-LIMITATIONS",
    "O-POLICY-IMPACT",
    "O-RATIONALE",
    "O-SUMMARY",
    "O-TEST-COMMAND"
  ],
  "retained_evidence_ids": [],
  "invalidated_attestation_ids": [],
  "next_authorized_actor_roles": [
    "maintainer"
  ],
  "requires_confirmation": true,
  "mutates_case": false,
  "preview_fingerprint": "1e8cd8b3f3e9712847aa1ee833283e9e9f7f50bb7955c92671dcad3f2309b899",
  "traceability": [
    {
      "kind": "permission_rule",
      "object_id": "maintainer:verify_evidence",
      "relationship": "authority"
    },
    {
      "kind": "governance_case",
      "object_id": "governance-self-mod",
      "relationship": "source_state"
    },
    {
      "kind": "state_machine_rule",
      "object_id": "awaiting_maintainer_verification:verify_evidence:verification_complete",
      "relationship": "transition_plan"
    }
  ],
  "processed_objects": [
    "O-ARTIFACT",
    "O-CHANGED-FILES",
    "O-INDEPENDENT-REVIEW",
    "O-LIMITATIONS",
    "O-POLICY-IMPACT",
    "O-RATIONALE",
    "O-SUMMARY",
    "O-TEST-COMMAND"
  ],
  "invalidated_evidence_ids": [],
  "responsibility_before": {
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
