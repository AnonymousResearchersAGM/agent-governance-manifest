# AGM Reviewer Guidance Layer

- 案例: `scoped-repair`
- 本次路径: 轻量审核
- 当前阶段: 等待维护者重新检查指定范围
- 风险: 低
- 阻断问题: 1
- 需要关注: 0
- 当前责任方: 维护者侧检查人员、项目规则负责人、人类维护者
- 责任方依据: 受影响材料已补充或仍然有效；当前只需重新检查指定修复范围。

## 五步流程

1. ✓ **系统识别要求** — 已完成：适用规则和本次要求已由 AGM 引擎生成。
2. ✓ **贡献者准备材料** — 已完成：本次所需材料已提交到后续流程。
3. — **负责人确认** — 本次不要求：当前义务集合不要求负责人确认。
4. ● **维护者检查** — 当前阶段：当前轮到有权限的维护者检查材料与绑定。
5. ○ **人类维护者最终决定** — 尚未开始：前序治理要求完成后才进入最终决定。

## 项目要求对比

| 检查项 | 项目要求 | 当前情况 | 材料状态 | 流程状态 |
| --- | --- | --- | --- | --- |
| 智能体行动与委派说明 | 说明智能体做了什么、用了哪些权限、是否有人监督，以及是否把具有独立行动能力的工作继续交给了另一个智能体。 | 材料已补充或仍然有效；当前等待维护者重新检查这一项。 | 已提供 | 等待维护者重新检查 |
| 变更文件清单 | 列出这次修改涉及的文件和范围。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |
| 修改说明 | 简要说明这次修改做了什么。 | 已提供与当前贡献和项目规则绑定的材料。 | 已提供 | 已完成 |

## 当前相关操作

- **检查提交材料**：受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。
- **要求补充或修改**：仅指定范围需要修复和重新检查，未受影响材料保留。
- **拒绝当前材料**：该材料将标记为已拒绝，并建立指定范围的补充或修改请求。
- **请求补充说明**：案例返回贡献侧回答，所选范围需要重新检查。

## 其他可用操作（折叠区内容）

- **查看变化范围**: 只读操作，不改变案例状态。
- **记录项目规则冲突**: 案例转入补充处理，由项目规则负责人或维护者处理。

## 只读交接工具

- **复制缺失项清单**: 生成可直接交给贡献侧的缺失、过时或无效材料清单。
- **导出贡献者待办清单**: 导出包含责任方、待处理项和范围的 Markdown 清单。
- **下载维护者摘要**: 导出当前风险、责任方和阻断项摘要，不作接受判断。
- **查看变化范围**: 查看变更文件、匹配规则和各要求的影响范围。
- **复制当前责任方说明**: 生成不改变案例状态的 handoff note。

## 暂不可用操作摘要

- 还有 9 项操作因当前阶段、权限或对象范围暂不可用
  - 将旧负责人确认标记为失效: 当前没有仍然有效的负责人确认可供失效处理。
  - 处理项目规则冲突: 当前角色没有“处理项目规则冲突”的权限。可以执行这一步的角色：人类维护者或项目规则负责人。
  - 重新提交修改后的材料: 当前角色没有“重新提交修改后的材料”的权限。可以执行这一步的角色：人类贡献者或贡献侧智能体。
  - 确认负责人声明: 当前角色没有“确认负责人声明”的权限。可以执行这一步的角色：负责人。
  - 由有权维护者执行覆盖处理: 当前角色没有“由有权维护者执行覆盖处理”的权限。可以执行这一步的角色：人类维护者。
  - 最终接受: 当前角色没有“最终接受”的权限。可以执行这一步的角色：人类维护者。
  - 最终拒绝: 当前角色没有“最终拒绝”的权限。可以执行这一步的角色：人类维护者。
  - 要求继续修改: 当前角色没有“要求继续修改”的权限。可以执行这一步的角色：人类维护者。
  - 关闭本次审核记录: 当前角色没有“关闭本次审核记录”的权限。可以执行这一步的角色：人类维护者。

## Authority boundary

本页面只把 AGM 的真实状态、依据和合法操作整理成人类可读形式。材料齐备、维护者检查完成，或者已经具备进入最终决定的条件，都不等于代码已经被项目接受。最终决定只属于获授权的人类维护者。


## 操作预览

你准备执行：**只重新检查“智能体行动与委派说明”**

当前角色和案例状态允许生成此操作计划。

当前可以继续处理的角色：人类维护者。

### 将处理

- 智能体行动与委派说明

### 将保留

- 变更文件清单
- 修改说明

### 预计变化

- 案例流程：等待维护者检查 → 等待人类维护者最终决定。受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。
- 智能体行动与委派说明：材料已满足 → 已检查。受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。
- 本次问题：待处理 → 已关闭。本次重新检查通过后，关联问题将关闭。
- 本次修复请求：已补充，等待重新检查 → 已关闭。所关联的问题在本次重新检查后关闭。

### 执行后

- 本次指定材料将被标记为已检查。
- 关联的问题和修复请求将被关闭。
- 当前责任方将转交给人类维护者。
- 案例将进入“人类维护者最终决定”。
- 这不等于代码已经被项目接受。

<details>
<summary>技术操作、内部 ID 与原始状态</summary>

```json
{
  "operation": "verify_evidence",
  "current_role": "maintainer_verifier",
  "required_roles": [
    "maintainer",
    "maintainer_verifier",
    "policy_steward"
  ],
  "source_state": "awaiting_maintainer_verification",
  "target_state": "ready_for_human_decision",
  "effects": [
    {
      "target": "案例状态",
      "before": "awaiting_maintainer_verification",
      "after": "ready_for_human_decision",
      "explanation": "受影响项会记录维护者检查；全部阻断项完成后进入人类最终决定。",
      "source_object_ids": [
        "transition-a89fe0ba563e576790b2b4a8090466f3"
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
      "target": "finding-998704f5c08b576f882422ff5d00c5cd",
      "before": "open",
      "after": "resolved",
      "explanation": "本次重新检查通过后，关联问题将关闭。",
      "source_object_ids": [
        "finding-998704f5c08b576f882422ff5d00c5cd"
      ]
    },
    {
      "target": "指定修复请求",
      "before": "resubmitted",
      "after": "resolved",
      "explanation": "所关联的问题在本次重新检查后关闭。",
      "source_object_ids": [
        "repair-cb5bf46ed270569b89e88c9153331193"
      ]
    }
  ],
  "affected_obligation_ids": [
    "O-AGENT-SCOPE"
  ],
  "requested_obligation_ids": [
    "O-AGENT-SCOPE"
  ],
  "retained_evidence_ids": [
    "evidence-7525c42fd5d650df850b5f6ebf095485",
    "evidence-2cb3732e2b49561598dc8daee791f8d9"
  ],
  "invalidated_attestation_ids": [],
  "invalidated_evidence_ids": [],
  "processed_objects": [
    "O-AGENT-SCOPE"
  ],
  "workflow_step_before": "maintainer_check",
  "workflow_step_after": "human_final_decision",
  "creates_records": [
    "state_transition",
    "maintainer_verification"
  ],
  "preview_fingerprint": "d07af4c15950bd54bb1dd0dbfb5c8df159a2e242d4f641d1e8dfee5ae1c80e17",
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
      "object_id": "awaiting_maintainer_verification:verify_evidence:verification_complete",
      "relationship": "transition_plan"
    }
  ]
}
```

</details>
