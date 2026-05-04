# Progress — Slice 1.5 UI Redesign

## Summary

- 任务形态: Epic
- 状态: **DONE（代码侧收官）**（#0–#10 全部 DONE；Lighthouse Perf 需客户环境 prod build 重跑）
- 决策锁定: 2026-04-22
- 进度: 11/11 子任务

## Recovery

- 父任务: Slice 1.5 UI Redesign
- 形态: epic
- 进度: 11/11 DONE（代码侧）+ /rules cookie-only GET 500 根因修复
- 当前: Epic 收官；Lighthouse Perf 需在客户 prod 环境重跑才算真 Perf 数
- 文件: `.codex-tasks/20260423-ui-redesign-slice1-5/SUBTASKS.csv`
- 下一步: 客户验收前在生产构建 `pnpm --filter web build && next start` 后重跑 `pnpm --filter web exec playwright test` + `node apps/web/tests-e2e/lighthouse-runner.mjs` 取真实 Perf 数

## /rules cookie-only GET 500 根因 + 修复（2026-05-04）

- **根因**：`apps/web/src/components/rules/rules-copy.ts` 的 `buildRulesCatalogCopy` 把 3 个函数字段（`countAll` / `errorSave` / `rowsSelectedLabel`）注入 `RulesCatalogCopy`，再作为 props 跨 Server→`"use client"` 边界传给 `RulesCatalog`。RSC payload 序列化不支持函数；dev mode 宽容、prod build 直接 500。
- **修复**：
  - `RulesCatalogCopy` 删除 3 个函数字段；client 组件 `RulesCatalog` 引入 `useTranslations("rulesPage")`，本地构造文本。
  - `buildRulesCatalogCopy` 返回纯字符串 copy。
  - 新增 `apps/web/tests/rules-catalog-copy.test.ts` 守护 copy 字段全为 string，防回归。
- **验证**：lint 175 + typecheck + test 135 + prod build 25 routes 全绿；端到端 prod cookie-only GET 留客户验收前与 Lighthouse 一同重跑。

## 启动前提（entry gate）

1. Slice 1 Epic 15（监控深度）全部 DONE ✅
2. Slice 1 Epic 16（通知实感）child #1-#4 DONE ✅（child #5 真人演练 2026-04-22 Boss 决议 DEFERRED，不作为本切片 gate）
3. Boss 明确批准启动 Slice 1.5 ✅

**2026-04-22：3 条前提已满足，状态转为 READY TO START。**

## 决策来源

17 轮 `/domain-model` 访谈（Q1–Q17）+ Q18 `A/A` 投票收官：
- Q1 基础档位：Polish Current + Tier 3 honest placeholders
- Q2 技术栈：shadcn/ui + ECharts + 自有 tokens
- Q3 设计语言：双主题 + 暗色默认 + cyan brand + 四色严重度轴
- Q4 导航：Icon Rail + 上下文侧栏
- Q5 Tier 分层：10 张 Tier 1 + label 体系 + Tier 3 占位 + Tier 4 框架
- Q6 i18n：next-intl + HarmonyOS Sans SC + 混合术语策略
- Q7 页面模板：Canonical 7 段式
- Q8 表格范式：Catalog / Feed / Snapshot 三分法
- Q9 Overview：5 行 8 chart + 1 table
- Q10 Alerts：4 tab + on-call 模式 + Alert Drawer 5 段
- Q11 Rules：Tri-state 继承 + 抽屉编辑 + 审计历史
- Q12 Instances：表格 + 栅格双视图
- Q13 Instance Detail：8 tab + Kill 防误杀
- Q14 Notify：Feed drawer + Channels 只读
- Q15 Settings + Audit：侧导航 + 独立 Audit 页
- Q16 Login + 通用态：60/40 + 12 条通用态规则
- Q17 全局框架：⌘K + Notification 抽屉 + on-call 模式

全部落盘到 ADR-0012 + CONTEXT.md UI Terms 段。

## Validation

- 2026-04-23 child #0：lint/typecheck 绿 / test 104 / build 12 路由（含 /design-demo）
- 2026-04-23 Wave-1 收官（#1/#2/#3/#5/#6/#7/#8/#9）全局对账：lint 147 / typecheck 绿 / test 127 / build 20 路由
- 2026-04-23 child #4 Instance detail 收官：lint 158 files 绿 / typecheck 绿 / test 134 / build 25 路由（含 audit、configuration、performance、replication 新子路由 + /alerts/[alertId] + /admin/channels + /admin/audit + /api/command-palette）
- 2026-04-23 child #10 最终闸门：Playwright **50/50 pass**（12 业务 + 1 视觉 spec）/ 视觉基线 **24 张**（12 路由 × dark+light）/ Lighthouse 4/5（/overview /instances /alerts /settings：A11y 96-98、BP 96，Perf=64 dev-mode；/rules cookie-only GET 500）/ lint 175 · typecheck · test 134 · build 25 全绿

## Tier 3 诚实占位（Slice 2 回填清单）

- Instances list：edit / delete / 批量启停 / 批量删除（disabled + tooltip "Slice 2 上线"）
- Instance detail 复制 tab：后端无 replication 端点
- Instance detail 配置 tab：后端无 parameter 端点
- Alerts 告警抑制：disabled + Slice 2 文案
- Channels 写能力：Slice 1.5 只读 banner，写 API 归 Slice 2
- 字体：HarmonyOS Sans SC 走法务流程，当前 Noto Sans SC 临时替代

## Reference

- ADR-0012: `docs/adr/0012-ui-redesign-design-system-and-page-architecture.md`
- EPIC.md: 本目录同级
- CONTEXT.md § UI Terms
