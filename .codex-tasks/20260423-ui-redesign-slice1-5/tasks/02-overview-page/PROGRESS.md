# Progress — Child #2 Overview page

## Summary
- 父任务: `.codex-tasks/20260423-ui-redesign-slice1-5/`
- 子 ID: 2
- 形态: single-full
- 状态: DONE（scoped gates 全绿；epic gate 待 #10）
- 起点: 2026-04-23
- 收尾: 2026-04-23

## Recovery
- 写作用域: `apps/web/app/overview/` + `apps/web/src/components/overview/**` + `messages/zh-CN.json` `overviewPage.*`
- 依赖: child #0 DONE（tokens / AppShell / CanonicalPageTemplate / primitives / useAutoRefresh / chart-N palette 已齐）
- Q9 规则 9 条落地清单见 SPEC.md

## Open decisions
- AppShell 组装暂放在 `apps/web/src/components/overview/overview-shell.tsx`（client 包裹），等 #9 接管后抽到全局 `app/layout`。
- ECharts 主题切换实现：`readChartPalette()` 在客户端每次 refresh 时重新读 CSS var；不监听 `data-theme` 属性变更（Boss 指令里只要求 30s auto-refresh，不要求即时重绘）。
- Fleet Health Matrix 用原生按钮 + `<Link>` (next/link) —— 可访问性要求 button/link 语义；不引入 tooltip primitive 以外的组件。
- WindowSelector 使用 URL search param，保持 server-side refetch 能力。

## Validation log (2026-04-23)

Scoped gates (all green within this subtask's write scope):

- `pnpm --filter web exec biome check app/overview src/components/overview` → 0 errors.
- `pnpm --filter web exec tsc --noEmit -p tsconfig.json` 过滤 `overview` scope → 0 errors（全项目 tsc 有 2 个错误，属于兄弟子任务 #3 `src/components/instances-list/instances-list-shell.tsx:124` 与 #8 `src/components/settings-audit/audit-feed.tsx:16`，不在本 child 写作用域，由对应 child/epic 收口）。
- `pnpm --filter web test` → 114/114 pass（基线 104；其余由兄弟子任务补入）。
- `pnpm --filter web build` → 被上述兄弟子任务的 type error 以及根 layout 引用的 `@fontsource-variable/bricolage-grotesque`（#9 归口）阻塞，**非本任务注入**，属 epic-level gate，归 child #10 收官。

Overview 自身的全部 route-level 代码：lint / typecheck 均通过。8 chart + Fleet Health Matrix + instances snapshot table 均接入 `OverviewResponse` 真数据；CSS var chart palette（`--chart-1..8`）硬约束无硬编码 hex。

## 交付清单

- `apps/web/app/overview/page.tsx` — Server Component，Canonical 7 段式，按 Q9 五行布局
- `apps/web/src/components/overview/overview-shell.tsx` — 页面级 AppShell + CanonicalPageTemplate wrapper（#9 接管后删除）
- `apps/web/src/components/overview/overview-chart-palette.ts` — CSS var → ECharts color 统一读取器
- `apps/web/src/components/overview/overview-line-chart.tsx` — ECharts 6 line chart (dynamic import + resize observer)
- `apps/web/src/components/overview/fleet-health-matrix.tsx` — 可点击的实例矩阵（Server Component）
- `apps/web/src/components/overview/instances-snapshot-table.tsx` — row5 table（Server Component）
- `apps/web/src/components/overview/overview-auto-refresh.tsx` — `useAutoRefresh(30_000)` 包装 + pause/resume
- `apps/web/src/components/overview/window-selector.tsx` — 15m/1h/6h/24h segmented selector
- `apps/web/messages/zh-CN.json` — 追加 `overviewPage.*` namespace（46 keys）

## Risks / watch list
- Next 16 + React 19 下 ECharts 6 SSR：必须 `"use client"` + dynamic import / `useEffect` 挂载；禁止 Server 渲染 `<div>` 之外内容。
- 现有 `metric-chart.tsx` 不复用（旧实现走 SVG 自造），走新实现以符合 ADR-0012。
