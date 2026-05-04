# SPEC — Slice 1.5 Child #2: Overview page

> 父任务: `.codex-tasks/20260423-ui-redesign-slice1-5/`
> 决策源: ADR-0012（Q7 / Q9 / Q16）+ SHARED-BRIEF + SUBTASKS.csv id=2
> 前置: child #0（设计系统地基） DONE
> 写作用域: `apps/web/app/overview/` + `apps/web/src/components/overview/**` + `apps/web/messages/zh-CN.json` 的 `overviewPage.*`

## 目标

把 `/overview` 从旧 AppChrome 全面重做成 ADR-0012 Canonical 页，承担 Slice 1.5 "第一眼 wow" 的主阵地：fleet-wide health 快照 + 时序关键指标 + 实例下钻入口。

## Done-When

1. `/overview` 渲染 Canonical 7 段式（PageBreadcrumb → EntitySummary → QuickMetrics → TabBar → PageContent），包裹在 AppShell (IconRail + ContextualSidebar + TopBar)。
2. 内容区遵循 5 行布局：
   - row1 KPI strip（4 metric）
   - row2 line chart（连接/线程/请求，2 chart）
   - row3 line chart（吞吐/缓冲，2 chart）
   - row4 line chart（延迟/复制 lag，2 chart + 1 健康比率 chart，共 2 chart 合并到第 3 行尾 + Fleet Health Matrix 单行填满）
   - row5 instances table
   - 累计 **8 chart + 1 table + 1 Fleet Health Matrix**。
3. Fleet Health Matrix 是一个按 instance 粒度的方格（含 engine/env 维度），每格点击跳 `/instances/[instance_id]`，hover 展示 tooltip（name / engine / env / status）。
4. 时间范围：默认 `1h`，支持 `15m / 1h / 6h / 24h` 切换（URL `?window=`，与现有 `parseTimeWindow` 兼容）。
5. 30s 自动刷新：客户端使用 `useAutoRefresh(30_000)` 触发 `router.refresh()`；pause/resume 按钮。
6. 所有 ECharts 实例颜色只使用 `var(--chart-1)`~`var(--chart-8)`；文字/坐标/grid 颜色走 `--fg-*` / `--border-*`；禁硬编码 hex。
7. 主题切换无需重渲染页面：图表从 CSS var 读色，在 theme 切换后下一次刷新自动生效（不要求即时重绘，因 auto-refresh 已覆盖）。
8. 加载 / 空状态 = `<Skeleton>`（`@db-monitor/ui` 的 primitive）；空结构（instance=0）展示 empty state 卡片（中文），禁 spinner。
9. 新增 i18n key 全部落在 `overviewPage.*` namespace，追加到 `messages/zh-CN.json` 尾部；现有 10 个 namespace 不变。

## Q9 九条规则（本任务落地清单）

1. **Canonical 7 段式**（Q7）：面包屑 40 / EntitySummary 88 / QuickMetrics 64 / TabBar 44 / PageContent。
2. **5 行布局**：row1 KPI strip / row2-row3 line charts / row4 fleet matrix / row5 table。
3. **8 chart**：连接 / 线程 / QPS / 吞吐 in / 吞吐 out / 缓冲池读 / 复制 lag / 健康比率。
4. **1 table**：instances snapshot（name / engine / env / status / labels / last metric）。
5. **Fleet Health Matrix** 可点击进入实例详情。
6. **30s auto-refresh** 走 `useAutoRefresh`，不使用 spinner，pause/resume 控件可见。
7. **默认 1h 时间范围**；URL 可共享；切换立即生效。
8. **8 色 chart palette**：ECharts `color` 配置从 CSS var 取值，色板严格 `--chart-1..8`。
9. **Skeleton 加载态 + 三段空态**（首次/过滤空/业务空），禁 hex / spinner / glassmorphism。

## 数据源

- 复用 `apps/web/src/server-api.ts` `createServerApiClient()` + `parseTimeWindow`。
- 走 `OverviewResponse`（已在 `@db-monitor/api-client`）。
- 不新建 HTTP client / API 请求；走 Server Component + `router.refresh()`。

## 非目标（Out of Scope）

- 命令面板（⌘K）：归 #9。
- Notification Drawer：归 #9。
- `providers.tsx` / `app/layout.tsx` 改造：归 #9。
- 全局 AppShell：暂用 page-local 组装（#9 接管后再移除）。
- 表格多选/批量操作：Q8 范畴，本页 table 为 snapshot only。

## 验收门（必须全绿）

- `pnpm --filter web lint` 无 error
- `pnpm --filter web typecheck` 无 error
- `pnpm --filter web test` 不降级（基线 104 tests）
- `pnpm --filter web build` 所有路由通过
