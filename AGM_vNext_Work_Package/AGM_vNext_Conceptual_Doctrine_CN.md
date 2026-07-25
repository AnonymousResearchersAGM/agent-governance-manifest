# AGM vNext：全新思想、治理机制与制品架构

**状态：** JSIS 冲刺与 AGM vNext 开发的工作基线
**日期：** 2026-07-25
**适用边界：** 本文描述的是 AGM v0.1.0 之后的新设计发展。AGM v0.1.0 仍是既有论文与实验所报告的固定研究快照；本文中的新增机制不得被写成旧实验已经验证。

---

## 1. 核心重新认识

AGM 不应再被定义为 risk、evidence、accountability 和 review-gate 四项治理功能的组合。这四项是仓库审计中用于识别贡献级可治理性的**最小可观察状态域**，也是 review time 可以恢复和检查的治理结果；它们不是 AGM 的完整本体，更不是 AGM 新颖性的来源。

AGM 的核心治理能力在于：

> 将项目级治理规则、具体贡献的实际变更、行动者的自治与权限配置，转化为一次贡献专属的、可检查、可修复、受权限约束并由人类最终裁决的治理实例。

因此，AGM 不只是保存规则，也不只是收集材料。它是一种 **contribution-level governance instantiation mechanism**：使抽象的项目规则在具体贡献上获得适用范围、义务、责任、验证权、状态转换和最终决策边界。

---

## 2. 理论层级

### 2.1 核心现象

自主或半自主代理可以扩大生产性行动能力，却不必然同步产生与之对应的：

- 可问责身份；
- 合法的验证权；
- 最终决策权；
- 对实际行动范围的充分人类理解。

由此，生产性行动可能与责任承担、验证权威和最终项目权威发生解耦。

### 2.2 核心治理机制

**双向治理契约**通过重新配置以下关系实现重新耦合：

- contribution side 的准备义务；
- accountable human 的确认责任；
- maintainer side 的验证、质疑、阻断和要求修复的权利；
- human maintainer 的最终决定权。

双向契约只有在这些权利与义务能够进入实际状态转换时才真正成立。它不能停留在“贡献者提供材料、维护者阅读报告”的松散分工。

### 2.3 组织载体

**项目侧可治理性基础设施**持续保存和执行：

- 项目规则；
- 角色与权限；
- 风险与自治配置；
- 证据义务；
- 状态转换；
- 版本适用性；
- repair、override 与 closure 规则。

### 2.4 诊断性功能架构

agent-readability、traceability、governability 三层框架继续保留，但其作用是诊断：

- agent-readability 解决代理能否理解项目环境和入口；
- traceability 解决 AI 参与及其来源是否可记录；
- governability 解决项目规则是否在具体贡献上形成可执行的义务、责任、验证和决策状态。

### 2.5 设计取向

合规赋能仍是设计取向。AGM 应减少治理发现和程序执行的摩擦，清楚暴露规则理由、缺失项、责任节点和 repair path，同时不得自动化人类责任、maintainer verification 或最终接受。

### 2.6 理论承载制品

AGM 是上述治理逻辑的理论承载制品，但 AGM 名称不是理论本身。即使去掉 AGM 名称，关于行动、责任、验证权与最终权威重新耦合的组织机制仍应成立。

---

## 3. AGM 的八阶段治理生命周期

AGM vNext 的核心生命周期为：

> **Resolve → Compile → Bind → Attest → Verify → Repair → Decide → Record**

### 3.1 Resolve：解析适用规则

输入包括：

- base-branch 的 canonical `.agm/`；
- 适用 manifest 版本；
- 实际 diff；
- 贡献者与 agent 的行动配置；
- 项目的角色、权限和 profile。

输出包括：

- Matched Rule Set；
- 风险区域与风险性质；
- autonomy profile；
- 规则冲突、缺失配置或版本问题。

### 3.2 Compile：编译贡献专属义务

根据 matched rules、风险、自治程度和交互规则，生成：

- evidence obligations；
- human attestation obligations；
- required verifier roles；
- warning 与 blocking gates；
- independent review requirements；
- final authority boundary。

这一步是 AGM 区别于静态 cues 的关键。项目级规则被编译为本次贡献具体欠下的治理义务。

### 3.3 Bind：绑定变更、证据和规则

证据必须绑定：

- contribution/diff hash；
- 受覆盖的文件、符号或变更；
- obligation ID；
- 运行环境与命令；
- 生成时间与有效期；
- applicable policy snapshot。

代码或证据发生实质变化后，系统应计算哪些证据、attestation 和 verification 失效。

### 3.4 Attest：人类责任承接

人类确认必须成为显著、独立、可审计的治理事件，而不是隐藏在 YAML 中的布尔字段。确认应记录：

- actor；
- timestamp；
- contribution/package hash；
- reviewed scope；
- reservations；
- manifest version；
- statement。

Agent 可以准备信息和提示，但不得替人类 attestation。

### 3.5 Verify：维护侧独立验证

Maintainer side 应从 base branch 独立恢复规则和义务，并执行：

- evidence verification；
- mismatch 与 conflict detection；
- attestation validity check；
- rule/version applicability check；
- accept evidence / reject evidence / request repair；
- authorized warning 或 blocking transition。

Verification 不等于最终接受。

### 3.6 Repair：一等修复协议

Repair 不是失败后的附注，而是合规赋能的正式组成：

- finding；
- repair request；
- responsible actor；
- required correction；
- affected evidence/attestation；
- resubmission；
- revalidation；
- re-review。

系统应支持局部失效传播，避免一个局部问题导致所有已验证材料无差别作废。

### 3.7 Decide：人类最终裁决

只有授权的人类 maintainer 可以执行最终：

- accept；
- reject；
- request changes；
- authorized override；
- close without merge。

AGM 的 readiness 或 verification 状态不能自动转化为 merge 权限。

### 3.8 Record：闭环记录

每个治理案例最终形成 closure receipt，记录：

- applicable policy version；
- matched rules 与最终风险状态；
- obligations 与 evidence；
- human attestations；
- maintainer verification；
- repair history；
- override；
- final decision；
- unresolved but accepted exceptions。

---

## 4. 核心制品对象

AGM vNext 至少包含以下一等对象：

1. **Governance Case**
   一次具体贡献的治理实例，拥有稳定 case ID 和生命周期。

2. **Applicable Policy Snapshot**
   该贡献适用的项目规则版本、base commit 和解析结果。

3. **Matched Rule Set**
   实际 diff 命中的全部规则，保留触发原因、作用范围和风险性质。

4. **Compiled Obligation Set**
   根据风险、自治、角色和交互规则编译出的贡献专属义务。

5. **Bound Evidence**
   与具体 obligation、diff、环境和有效期绑定的证据。

6. **Human Attestation**
   与明确范围和具体 package hash 绑定的人类责任确认。

7. **Authorized State Transition Record**
   谁以什么角色、依据什么权限、从什么状态转到什么状态。

8. **Governance Finding / Repair Request**
   可定位、可分派、可修复、可重新验证的问题对象。

9. **Contribution Governance Report**
   面向 contributor 或 maintainer 的可操作“治理检验报告”。

10. **Closure Receipt**
    事后可恢复决策过程的最终闭环记录。

---

## 5. 纯人类贡献与双路径设计

AGM 不应强迫所有传统贡献者填写声明和证据。

### 5.1 Ordinary contribution path

没有 AGM package 的贡献默认进入 ordinary path：

- 不要求贡献者证明自己是人类；
- 不要求填写 YAML；
- 按项目原有 PR、CI、CODEOWNERS 和 review 处理；
- review side 显示 `No AGM package submitted`。

重要语义是：

> absence of AGM material ≠ confirmed human authorship

系统不能把未提交 AGM package 自动解释为“已证明纯人类贡献”，否则 agent 可以通过省略材料规避治理。

### 5.2 AGM-managed contribution path

当贡献者主动声明 agent-mediated contribution，或项目规则根据风险、自治、权限和变更范围要求结构化治理时，创建 Governance Case 并进入 AGM 生命周期。

### 5.3 Policy-required path

某些高风险变更即使由纯人类完成，也可以被项目政策要求提供结构化证据。此时要求来源于变更风险和项目规则，而不是 AI 身份判断。

---

## 6. 风险、自治与多风险贡献

### 6.1 风险与自治正交

技术/组织风险和 agent autonomy 是两个独立维度：

- 纯人类也可能提交 critical 变更；
- 高自治 agent 也可能只修改低风险文档；
- 高自治会增加责任、权限和验证要求，但不必自动等同于高技术风险。

Autonomy profile 至少考虑：

- action scope；
- persistence；
- permissions；
- human supervision；
- submission authority；
- delegation / multi-agent behavior。

### 6.2 多风险贡献

贡献命中多个风险区域时，vNext 不得只取最高风险后丢弃其余要求。

应采用：

- `overall_risk_level` 作为摘要；
- 完整 Matched Rule Set 作为事实源；
- 各规则义务取并集并去重；
- 每项证据绑定具体 obligation；
- 所有 mandatory blocking obligations 采用合取逻辑；
- 报告显示每个风险区域的独立状态。

### 6.3 交互风险

某些风险组合产生新的义务，例如：

- 修改治理规则 + 修改规则执行器；
- authentication + deployment configuration；
- privacy-sensitive data + export path；
- dependency update + release workflow。

规范应支持 `interaction_rules`，在组合条件满足时增加：

- 风险升级；
- independent review；
- additional evidence；
- separation-of-duty gate。

---

## 7. 有权威类型的状态机

每一种状态必须定义：

- 谁可以 propose；
- 谁可以 attest；
- 谁可以 verify；
- 谁可以 invalidate；
- 谁可以 request repair；
- 谁可以 override；
- 谁可以 make final decision。

示例边界：

- contributor agent 可以提出 risk assessment 和 evidence；
- accountable human 可以确认其实际审核范围；
- maintainer-side verifier 可以验证 evidence 与 policy conformity；
- contributor 不能写入 `maintainer_verified`；
- tool 不能写入 `accepted`；
- authorized human maintainer 才能做 final decision 或 override。

状态转换必须追加记录，不能通过直接覆盖一个 YAML 字段隐藏历史。

---

## 8. 人类可操作界面

YAML 继续作为 canonical machine-readable source，但人类不应以直接编辑 YAML 作为主要交互方式。

### 8.1 Contributor Governance Panel

展示：

- contribution identity 和 diff hash；
- matched risk areas；
- compiled obligations；
- evidence status；
- 缺失和异常；
- 人类需要确认的精确范围；
- `Confirm / Request correction / Decline to attest` 操作。

Agent 完成任务后应主动提示用户打开面板，而不是让用户寻找 YAML 字段。

### 8.2 Maintainer Governance Panel

采用类似医院化验报告的稳定结构：

- 总体 readiness；
- 各风险区域；
- 参考要求与观测结果；
- 异常项；
- evidence binding；
- attestation；
- gate 状态；
- repair history；
- maintainer operations。

操作包括：

- verify evidence；
- reject evidence；
- request repair；
- invalidate attestation；
- record policy conflict；
- authorized override；
- final decision。

### 8.3 Project Governance Console

面向项目治理者：

- 编辑和预览规则；
- 模拟某个 diff 的义务编译；
- 检查规则冲突和不可达状态；
- 配置自治和保障 profiles；
- 管理版本与迁移；
- 检查与 CONTRIBUTING、PR templates、CI、CODEOWNERS 和 branch protection 的接口。

### 8.4 目录边界

- `.agm/`：项目公共、版本化、canonical 的规则、工作流、界面配置和 agent 接入定义；
- `.agm-work/`：具体 Governance Case 的运行时状态，通常不作为 canonical project policy；
- evidence/closure artifacts：根据项目政策决定提交、作为 CI artifact 或保存在平台侧。

---

## 9. 制度嵌入与程序性知识封装

### 9.1 Discovery adapters

AGENTS.md、CLAUDE.md、Copilot instructions 等是发现适配器，不是权威规则源。它们应简短指向 `.agm/` 和对应 workflow。

其治理意义在于利用既有 agent-facing repository conventions，让治理规则进入已有数字工作入口，减少另起炉灶的发现摩擦。

### 9.2 Portable AGM Skills

Contributor 和 maintainer Skills 应封装完整程序性知识，而不只是说明文档：

- 何时读规则；
- 如何分析实际 diff；
- 如何处理多风险；
- 如何编译义务；
- 如何收集真实 evidence；
- 何时暂停等待人类；
- 如何在 diff 改变后失效和重验；
- 如何生成报告和 repair 请求。

Skill 自动化程序，但不自动化责任和最终权威；它必须暴露规则理由，避免黑箱式点击合规。

### 9.3 Dedicated AGM Steward Agents

作为可选高级实现：

- AGM Contribution Steward；
- AGM Review Steward；
- 后续可增加 AGM Policy Steward。

专用 agent 不构成 AGM 理论和采用的必要条件。AGM 应允许普通 agent + discovery pointer、portable Skill 和 dedicated steward 三种逐级增强的采用方式。

---

## 10. AGM 与既有 cues 的关系

现有治理资源可以被 AGM 读取或调用：

- AGENTS.md 提供发现入口；
- CONTRIBUTING.md 提供项目规范；
- PR template 收集通用信息；
- CODEOWNERS 提供候选审查权配置；
- CI 提供技术验证资源；
- provenance 工具提供来源记录；
- branch protection 提供平台 gate。

AGM 的治理能力不来自把这些 cues 组装成一个大文件，而来自：

1. 解析其权威性和适用关系；
2. 结合实际贡献编译具体义务；
3. 绑定证据、责任与变更；
4. 控制有权限约束的状态转换；
5. 支持 repair、override、final decision 和 closure。

因此，cues 是 AGM 可以连接的制度与技术资源，而不是 AGM 的理论本体。

---

## 11. 对论文手稿的直接影响

### 11.1 四功能重新定位

risk、evidence、accountability、review-gate 应写成：

- 仓库审计的最小可观察诊断维度；
- 贡献级治理实例运行后在 review time 暴露的状态域。

不再把它们写成 AGM 的四个完整功能组件。

### 11.2 理论部分

理论重点应从 generation–verification asymmetry 的一般压力，推进到 autonomous agency 导致行动、责任、验证权和最终权威的解耦，以及双向治理契约如何重新耦合。

### 11.3 制品部分

制品重点应是：

- rule resolution；
- obligation compilation；
- evidence–change binding；
- authority-typed transitions；
- human-operable enactment；
- repair and closure；
- workflow embedding。

### 11.4 证据边界

现有证据可以支持：

- 仓库层面的诊断性功能缺口；
- v0.1.0 结构化材料提高 review-time 状态恢复；
- contributor-side 准备与人类/maintainer 权限边界的机制可行性。

现有证据不能支持：

- vNext 的多风险义务编译已经被实验验证；
- autonomy-sensitive profiles 已被验证；
- 新面板降低了工作量或认知负担；
- field adoption、community legitimacy 或长期组织转型。

---

## 12. 版本与实施边界

- Technovation manuscript v1.6.3 保持冻结；
- AGM v0.1.0 是已报告研究快照；
- 新实现使用独立 `v0.2-dev` 分支和开发 schema；
- vNext 功能在完成规范、测试和闭环演示前不得宣称为正式 v0.2.0；
- README、spec 和论文必须清晰区分 reported snapshot 与 new design development。

---

## 13. 一句话定义

> **AGM is a project-side governance infrastructure that resolves project rules against a concrete contribution, compiles contribution-specific obligations and authority boundaries, binds evidence and human accountability to the actual change, and supports authorized verification, repair, final human decision, and auditable closure.**
