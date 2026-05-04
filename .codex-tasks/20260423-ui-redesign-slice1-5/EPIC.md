# Epic: UI Redesign (Slice 1.5)

> 创建日期: 2026-04-22
> 启动时机: **Slice 1 收官后**（Boss 在 Q18 选择节奏 A）
> 预计工期: 3-5 周（依 subagent 并行度）
> 决策出处: `docs/adr/0012-ui-redesign-design-system-and-page-architecture.md` + 17 轮 `/domain-model` 访谈 (Q1–Q17)

## 0. 本切片解决的问题

Slice 1 收官时 Playwright E2E + UI 架构师复盘给前端打了 70/100，达不到客户验收窗口所需的"第一眼 wow"。Boss 明确要求覆盖 lepus 功能面 + 达到企业后台最佳实践。本切片把 Slice 1 已有后端能力重新铺到 10 张 Tier 1 页 + 3 件全局框架，把 UI 从 70 分拉到客户验收可 sign-off 的水平。

## 1. Done-When (Acceptance Gates)

1. 10 张 Tier 1 页全部按 ADR-0012 Canonical page template 落地，视觉一致性通过设计 QA
2. 双主题切换全链路可用（暗色默认），无 hardcoded hex 色残留
3. i18n 完成中文抽取，`messages/zh-CN.json` 覆盖所有 UI 文案
4. 表格三分法（Catalog/Feed/Snapshot）各至少一页实现
5. Playwright E2E 从当前 11/12 提升到 12/12 + 新增视觉回归快照
6. Lighthouse Performance / Accessibility / Best Practices 均 > 90
7. ⌘K 命令面板、Notification 抽屉、on-call 模式三件全局框架件可用
8. Tier 3 占位卡片按 ADR-0012 规格铺开并与 Settings 页"功能 Slice 状态看板"联通

## 2. Scope — In

| # | 子任务 | Tier 1 页 / 框架件 | 依赖 | 预估 |
|---|---|---|---|---|
| 0 | 设计系统地基 | tokens / 主题切换 / 字体加载 / layout framework / i18n runtime / Canonical template 组件 / Toast / Modal / Skeleton | (none) | 5-7 天 |
| 1 | Login | Q16 | #0 | 2 天 |
| 2 | Overview | Q9 | #0 | 4-5 天 |
| 3 | Instances 列表 | Q12 | #0 | 3 天 |
| 4 | Instance Detail | Q13（8 tab，内部再分解） | #0, #3 | 7-9 天 |
| 5 | Alerts | Q10 | #0 | 4 天 |
| 6 | Rules + Overrides | Q11（含 Tri-state） | #0 | 4 天 |
| 7 | Notify history + Channels | Q14 | #0 | 3 天 |
| 8 | Settings + Audit | Q15 | #0 | 4 天 |
| 9 | 全局框架件 | ⌘K / Notification 抽屉 / on-call 模式 | #0 | 3 天 |
| 10 | E2E + 视觉回归 + Lighthouse | Done-When #5/#6 | #1–#9 | 2 天 |

## 3. Scope — Out

- Slice 2 后端能力（WeCom / SMS / PostgresBindingRepository / SSO）：UI 侧按 Tier 3 占位卡片处理
- 移动端（Q9 明确排除）
- 多语言第二语种：i18n 框架装上，但只抽取中文；英文 Slice 2 再补
- pt-query-digest / Bigtable / Binlog 深度：占位卡片

## 4. Control Contract（不变量 / 预算）

- **不变量 A**：10 张 Tier 1 页必须全部使用 Canonical page template；偏离写子 ADR。
- **不变量 B**：组件内禁止 hardcoded hex 色，必须走 Tailwind token / CSS var。
- **不变量 C**：组件内禁止硬编码中文字符串，必须走 `messages/zh-CN.json`。
- **不变量 D**：Tier 3 占位卡片必须标 Slice + 预计交付窗口，不允许模糊词。
- **预算**：页面首屏 JS < 300KB gzip；图表首屏 > 3 张时走 lazy load；字体总加载 < 600KB。

## 5. Risk & Mitigation

| 风险 | 缓解 |
|---|---|
| 子 0（设计地基）卡壳会拖全部 | 子 0 单人 focus，完成前其他子任务只做设计稿 + 数据契约确认 |
| ECharts 锁定后主题切换 bug | 写 `useEChartsTheme` hook 统一处理，子 0 即落地 |
| 字体加载抖动影响首屏 | Next.js font optimization + `font-display: swap` + preload critical subset |
| 视觉回归快照脆性 | 初期允许 5% diff tolerance，后期收紧到 2% |
| Slice 2 后端返工 | 本切片只做 Slice 1 已有后端能力的 UI；Slice 2 后端先稳定再铺对应 UI |

## 6. Non-goals / 不做

- 不做用户体验调研（DBA + 产品验收为主，基于 ADR-0012 直接落地）
- 不做 A/B 测试（客户验收窗口不允许）
- 不做竞品功能覆盖穷举（Grafana / Datadog 功能面不是本切片目标）
- 不做完整 Storybook（只做核心组件的 MDX 文档）

## 7. Parallelism Playbook（subagent 使用指引）

- 子 #0 完成后，子 #1 #2 #3 #5 #6 #7 #8 #9 可并行启动（彼此独立）
- 子 #4 依赖 #3（Instance Detail 从 Instances 列表点击进入，要验通路），单人顺序做
- 子 #10 在其他全部 DONE 后单人做最终 gate
- **并行触发模式**：每个 Tier 1 页以 Agent 子任务 + 独立 worktree 驱动；严格按 ADR-0012 规格实施，不引入偏离

## 8. References

- ADR-0012：设计系统 + 页面架构
- ADR-0004：Per-instance threshold overrides（Rules 页 Tri-state 依据）
- ADR-0006：Runtime action permission（Kill 按钮权限门槛）
- ADR-0011：Slice 1 preflight decisions
- `CONTEXT.md` § UI Terms
- Epic 16 HANDOFF（Notify history UI 后端依据）
