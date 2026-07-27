# AGM Reviewer Guidance Layer

- 案例: `policy-migration`
- 本次路径: 轻量审核
- 当前阶段: 等待贡献侧补齐或更新材料
- 风险: 低
- 阻断问题: 2
- 需要关注: 1
- 当前责任方: 人类贡献者、贡献侧智能体
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
- **记录项目规则冲突**: 案例转入补充处理，由项目规则负责人或维护者处理。

## 只读交接工具

- **复制缺失项清单**: 生成可直接交给贡献侧的缺失、过时或无效材料清单。
- **导出贡献者待办清单**: 导出包含责任方、待处理项和范围的 Markdown 清单。
- **下载维护者摘要**: 导出当前风险、责任方和阻断项摘要，不作接受判断。
- **查看变化范围**: 查看变更文件、匹配规则和各要求的影响范围。
- **复制当前责任方说明**: 生成不改变案例状态的 handoff note。

## 暂不可用操作摘要

- 还有 13 项操作因当前阶段、权限或对象范围暂不可用
  - 检查提交材料: 当前处于“等待贡献者补齐材料”，还不能执行“检查提交材料”。
  - 要求补充或修改: 当前处于“等待贡献者补齐材料”，还不能执行“要求补充或修改”。
  - 拒绝当前材料: 当前角色没有“拒绝当前材料”的权限。可以执行这一步的角色：人类维护者或维护者侧检查人员。
  - 请求补充说明: 当前角色没有“请求补充说明”的权限。可以执行这一步的角色：人类维护者或维护者侧检查人员。
  - 将旧负责人确认标记为失效: 当前角色没有“将旧负责人确认标记为失效”的权限。可以执行这一步的角色：人类维护者或维护者侧检查人员。
  - 处理项目规则冲突: 当前处于“等待贡献者补齐材料”，还不能执行“处理项目规则冲突”。
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

你准备执行：**记录项目规则冲突**

当前角色和案例状态允许生成此操作计划。

当前可以继续处理的角色：项目规则负责人或人类维护者。

### 将处理

- 修改说明

### 将保留

- 无

### 预计变化

- 案例流程：等待贡献者补齐材料 → 发现问题，等待指定范围修改。案例转入补充处理，由项目规则负责人或维护者处理。
- 修改说明：尚未满足 → 项目规则冲突。案例转入补充处理，由项目规则负责人或维护者处理。

### 执行后

- 当前责任方将转交给项目规则负责人、人类维护者。
- 案例将进入“贡献者准备材料”。
- 这不等于代码已经被项目接受。

<details>
<summary>技术操作、内部 ID 与原始状态</summary>

```json
{
  "operation": "record_policy_conflict",
  "current_role": "policy_steward",
  "required_roles": [
    "maintainer",
    "maintainer_verifier",
    "policy_steward"
  ],
  "source_state": "evidence_incomplete",
  "target_state": "repair_requested",
  "effects": [
    {
      "target": "案例状态",
      "before": "evidence_incomplete",
      "after": "repair_requested",
      "explanation": "案例转入补充处理，由项目规则负责人或维护者处理。",
      "source_object_ids": [
        "transition-fb1c3eb898d154ed98f2004b45dc4d73"
      ]
    },
    {
      "target": "O-SUMMARY",
      "before": "unsatisfied",
      "after": "policy_conflict",
      "explanation": "案例转入补充处理，由项目规则负责人或维护者处理。",
      "source_object_ids": [
        "obl-o-summary"
      ]
    }
  ],
  "affected_obligation_ids": [
    "O-SUMMARY"
  ],
  "requested_obligation_ids": [
    "O-SUMMARY"
  ],
  "retained_evidence_ids": [],
  "invalidated_attestation_ids": [],
  "invalidated_evidence_ids": [],
  "processed_objects": [
    "O-SUMMARY"
  ],
  "workflow_step_before": "prepare_materials",
  "workflow_step_after": "prepare_materials",
  "creates_records": [
    "state_transition",
    "finding",
    "repair_request"
  ],
  "preview_fingerprint": "4b7b3cd670bc4eb743a1e23b13e6b4b903bfe465fd411df39f0f48285b38267c",
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
  ]
}
```

</details>
