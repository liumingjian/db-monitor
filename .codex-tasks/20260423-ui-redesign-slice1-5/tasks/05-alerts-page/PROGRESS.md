# Slice 1.5 — 子 #5 Alerts Page PROGRESS

## Context recovery
- 启动时间：2026-04-23
- 依赖：子 #0 设计系统（DONE）。不依赖 #9（on-call 实际逻辑），本任务只出 UI 占位。
- 必读已核验：SHARED-BRIEF.md / ADR-0012 / `apps/web/app/alerts/**` / `apps/web/src/data-layer.ts` / `monitoring-ui.ts`.

## Decisions
- Drawer 采用 `Dialog` primitive（shadcn/Radix 化版本），不新增 Drawer primitive（禁止改 packages/ui）。Dialog 以右侧 sheet 样式显示 5 段（内容溢出由 `overflow-y-auto`），Escape/overlay 关闭。
- 告警 drawer 开关绑定 URL path（`/alerts/[alertId]`）：详情页渲染列表 + Dialog open；列表页 Dialog closed。关闭时 `router.push('/alerts' + searchParams)`。
- on-call toggle：客户端 `useState` + `localStorage.getItem('alerts.oncall')` 回显；实际 notification + 2h 计时器留给子 #9 接入（仅 UI 就位）。
- 7 filter chips 直接写 `<a>`/`<Link>` 更新 URL searchParams；点击 "清除" chip 时从 URL 剔除键，保留其他。
- Entity summary 与 QuickMetrics 的值通过 `model.alerts` 在 server 侧汇总，避免 client 再计算。

## Validation
- `pnpm --filter web typecheck` 全局 0 错（alerts 作用域无告警）。
- `pnpm exec biome check app/alerts src/components/alerts` alerts 作用域全绿；仓库范围仍有 #6 / #7 / #8 / #9 子任务未修 lint 错（不在本任务写作域，不动）。
- `pnpm --filter web test` 16/16 file，104/104 test 通过（`tests/alerts.test.ts` 2/2）。
- `pnpm --filter web build` 13 路由全建成，含 `/alerts` + `/alerts/[alertId]`。

## Deliverables
- `apps/web/app/alerts/page.tsx`：Canonical 模板 + 4 tab + 7 chips + on-call toggle + 告警抑制占位按钮。
- `apps/web/app/alerts/[alertId]/page.tsx`：同 shell + `<AlertDrawer>` 侧抽屉 5 段，Esc/关闭按钮回到列表保留过滤态。
- `apps/web/src/components/alerts/`：
  - `alert-view-model.ts`（纯函数 counts / tab → status / related alerts）
  - `alert-filter-chips.tsx`（7 枚 chips + matchedCount）
  - `alert-oncall-toggle.tsx`（client Switch + localStorage `alerts.oncall`）
  - `alert-list.tsx`（列表 + Empty 三分法 + Severity Badge）
  - `alert-timeline.tsx`（跨 status 事件流）
  - `alert-drawer.tsx`（Dialog 承载 Summary/Timeline/LinkedSignals/RelatedAlerts/Actions 五段 + 三 server action forms）
  - `alerts-page-shell.tsx`（Canonical 模板 7 段组合）
- `apps/web/messages/zh-CN.json` 追加 `alertsPage.*` namespace（全部 chip/tab/drawer/empty/event 文案）。
- 移除过时 `apps/web/src/components/alert-triage-panel.tsx`（被 `alert-drawer.tsx` 完全替代，无外部引用）。

## 未覆盖 / 留给下游
- on-call 实际 OS notification + 2h auto-off 计时器归子 #9（当前仅 UI 占位 + localStorage 回显 + 自定义事件 `alerts:oncall-change`）。
- Linked signals 区的拓扑 / sparkline 查询归 Slice 2 指标检索（此处已显式标注文案）。
- 告警抑制按钮按 ADR-0012 路径依赖要求标注 "Slice 2" 灰态占位。

