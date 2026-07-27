# AGM Reviewer Guidance Layer

- 案例: `multi-risk-missing`
- 本次路径: 完整治理流程
- 当前阶段: 等待贡献侧补齐或更新材料
- 风险: 关键
- 阻断问题: 8
- 需要关注: 0
- 当前责任方: 贡献者、贡献侧智能体
- 责任方依据: 受影响材料尚未准备或更新完成，当前还不能进入维护者检查。

## 五步流程

1. ✓ **系统识别要求** — 已完成：适用规则和本次要求已由 AGM 引擎生成。
2. ● **贡献者准备材料** — 当前阶段：贡献者正在准备或补齐本次所需材料。
3. ○ **负责人确认** — 尚未开始：材料准备完成后才进入负责人确认。
4. ○ **维护者检查** — 尚未开始：贡献侧要求完成后才进入维护者检查。
5. ○ **人类维护者最终决定** — 尚未开始：前序治理要求完成后才进入最终决定。

## 项目要求对比

| 检查项 | 项目要求 | 当前情况 | 材料状态 | 流程状态 |
| --- | --- | --- | --- | --- |
| 智能体行动与委派说明 | 说明智能体做了什么、用了哪些权限、是否有人监督，以及是否把具有独立行动能力的工作继续交给了另一个智能体。 | 尚未提供。 | 缺少 | 等待贡献者处理 |
| 可核验测试制品 | 提供可以实际检查的测试输出或文件。 | 尚未提供。 | 缺少 | 等待贡献者处理 |
| 登录、认证与权限影响 | 说明本次修改是否改变登录、认证或权限行为。 | 尚未提供。 | 缺少 | 等待贡献者处理 |
| 变更文件清单 | 列出这次修改涉及的文件和范围。 | 尚未提供。 | 缺少 | 等待贡献者处理 |
| 负责人确认 | 由负责人确认自己审阅了当前代码版本、材料和明确范围。 | 尚未到负责人确认阶段。 | 缺少 | 等待负责人确认 |
| 独立维护者检查 | 由另一名具备权限且与贡献侧分离的维护者独立检查。 | 尚未到独立维护者检查阶段。 | 缺少 | 阻止继续 |
| 已知限制 | 说明已知限制；没有已知限制也要明确说明。 | 尚未提供。 | 缺少 | 等待贡献者处理 |
| 修改理由 | 说明为什么需要这次修改。 | 尚未提供。 | 缺少 | 等待贡献者处理 |
| 修改说明 | 简要说明这次修改做了什么。 | 尚未提供。 | 缺少 | 等待贡献者处理 |
| 测试命令与结果 | 提供测试命令、运行环境和实际结果。 | 尚未提供。 | 缺少 | 等待贡献者处理 |

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
  - 拒绝无效材料: 操作 reject_evidence 不能从当前状态 evidence_incomplete 执行。
  - 请求说明: 操作 ask_clarification 不能从当前状态 evidence_incomplete 执行。
  - 要求负责人重新确认: 操作 invalidate_attestation 不能从当前状态 evidence_incomplete 执行。
  - 解决项目规则冲突: 操作 resolve_policy_conflict 不能从当前状态 evidence_incomplete 执行。
  - 补交指定范围: 当前角色没有 resubmit 权限。 可执行角色：contributor, contributor_agent。
  - 负责人确认当前范围: 当前角色没有 confirm_attestation 权限。 可执行角色：accountable_human。
  - 执行有权覆盖: 操作 authorized_override 不能从当前状态 evidence_incomplete 执行。
  - 提交人类最终接受决定: 操作 decide_accept 不能从当前状态 evidence_incomplete 执行。
  - 提交人类最终拒绝决定: 操作 decide_reject 不能从当前状态 evidence_incomplete 执行。
  - 提交人类修改决定: 操作 decide_request_changes 不能从当前状态 evidence_incomplete 执行。
  - 关闭案例: 操作 decide_close 不能从当前状态 evidence_incomplete 执行。

## Authority boundary

本页面只把 AGM 的真实状态、依据和合法操作整理成人类可读形式。材料齐备、核验完成或 eligible 均不等于接受；最终决定只属于获授权的人类维护者。


## 操作预览

你准备执行：**请求补充或更新材料**

操作 request_repair 不能从当前状态 evidence_incomplete 执行。

### 将处理

- 登录、认证与权限影响

### 将保留

- 无

### 预计变化

- 案例不会发生变化。

### 执行后

- 本次操作不会改变案例状态。
- 当前责任方仍是贡献者、贡献侧智能体。
- 这不等于代码已经被项目接受。

<details>
<summary>技术操作、内部 ID 与原始状态</summary>

```json
{
  "operation": "request_repair",
  "source_state": "evidence_incomplete",
  "target_state": "evidence_incomplete",
  "effects": [],
  "affected_obligation_ids": [
    "O-AUTH-IMPACT"
  ],
  "retained_evidence_ids": [],
  "invalidated_attestation_ids": [],
  "invalidated_evidence_ids": [],
  "processed_objects": [
    "O-AUTH-IMPACT"
  ],
  "workflow_step_before": "prepare_materials",
  "workflow_step_after": "prepare_materials",
  "creates_records": [],
  "preview_fingerprint": "8025aa30042039553fd8e7e5a3788b197815ce8169271433cd4212fc7a2c3e0d",
  "traceability": [
    {
      "kind": "permission_rule",
      "object_id": "maintainer:request_repair",
      "relationship": "authority"
    },
    {
      "kind": "governance_case",
      "object_id": "multi-risk-missing",
      "relationship": "source_state"
    }
  ]
}
```

</details>
