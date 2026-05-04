# Progress — Child #3 Instances list page

## Summary
- 父任务: `.codex-tasks/20260423-ui-redesign-slice1-5/`
- 子 ID: 3
- 形态: single-full
- 状态: IN PROGRESS
- 起点: 2026-04-23
- 裁决: **A 方案**（双视图 + 行内 sparkline + filter chip + 新建抽屉接真 action + 空态 + 重验证接真；Tier 3 honest placeholders + 底部横幅）

## Recovery
- 写作用域: `apps/web/app/instances/page.tsx` + `apps/web/src/components/instances-list/**` + `messages/zh-CN.json` `instancesPage.*`
- 依赖: child #0 DONE（tokens / AppShell / CanonicalPageTemplate / primitives / Dialog / Tooltip / useAutoRefresh / chart-N palette 已齐）
- 复用 child #2 产物：`apps/web/src/components/overview/overview-chart-palette.ts` 的 `readChartPalette()` 作为 sparkline 色源
- Q12 规则 8 条落地清单见 SPEC.md

## Open decisions

- **Shell 组装**暂放在 `apps/web/src/components/instances-list/instances-list-shell.tsx`（client 包裹），等 #9 接管全局。
- **重验证 action**：不扩展 `packages/api-client/**`（read-only 约束）；`validateInstanceAction` 在 `monitoring-actions.ts` 内直接 `fetch` `${API_BASE}/control/instances/{id}/validate`，通过 `cookies()` 转发 session cookie，通过 `InstanceResponse` 类型断言回填响应。失败抛错 → server action 边界展示（Next.js 标准错误 UI），**不吞错**。
- **Sparkline 色源**：跨页复用 `overview-chart-palette.readChartPalette()`，不复制一份（DRY）。
- **Sparkline 并发上限**：列表 > 30 行跳过 trend 拉取，sparkline 占位提示"超过 30 条实例，sparkline 暂不渲染"（honest fallback，非 silent degradation —— 明示阈值）。
- **CPU metric 缺失**：Slice 1 后端未暴露；sparkline 三选项为 **连接数 / QPS / 活跃**，明确不伪造 CPU。SPEC.md 已列入遗留项。
- **Tier 3 按钮**：渲染 `<Button disabled>` + `<Tooltip>`，**绝不**绑定 server action；提交失败的假流程禁止出现。
- **Slice2Banner localStorage key**：`instances.slice2Banner.dismissed`；hydration-safe 做法是初始 state = `false`（显示横幅），mount 后 `useEffect` 读 localStorage，若 dismissed 则 setState 隐藏。
- **view=table|grid / spark=connections|qps|active** 走 URL search param，保持 server-side refetch 一致性。

## Validation log
- 2026-04-23: `pnpm --filter web lint` 绿
- 2026-04-23: `pnpm --filter web typecheck` 绿
- 2026-04-23: `pnpm --filter web test` 127 / 127 pass（baseline 104）
- 2026-04-23: `pnpm --filter web build` 15 路由全通过（含 `/instances` Dynamic）

## Final status
- 状态: **DONE**（2026-04-23）
- 最终产物:
  - `apps/web/app/instances/page.tsx`（Server Component 全面重写）
  - `apps/web/src/components/instances-list/` 共 12 个新文件（list-shell / list-content / filter-chips / toolbar / table / grid / sparkline / create-drawer / revalidate-button / empty-state / slice2-banner / tier3-placeholder-actions / types）
  - `apps/web/src/monitoring-actions.ts` 新增 `validateInstanceAction`（直接 fetch + cookie 转发，不改 api-client）
  - `apps/web/messages/zh-CN.json` 追加 `instancesPage.*` namespace

## Decision & remarks
- **CPU sparkline 取代为 active（threads_running / sessions_active）**：Slice 1 后端未暴露 CPU metric，禁止伪造；aria-label 显式包含后端 metric 名以保持审计可追溯。SPEC.md 遗留项已记（Slice 2 回填）。
- **api-client 保持只读**：`validateInstanceAction` 通过 `fetch` + `getServerApiBaseUrl()` + `cookies()` 转发走真实 `POST /control/instances/{id}/validate`；失败显式抛错交由 server-action 边界 Toast 化。无 silent fallback。
- **Tier 3 按钮严格占位**：编辑 / 删除 / 批量启停 / 批量删除，均 `<Button disabled>` + `<Tooltip>`；**无** server action 绑定。横幅一条 + localStorage dismiss。
- **Fanout 阈值 30 显式**：超出行显式在 UI 标注"暂不渲染 sparkline"，非静默降级；常量在 `types.ts:SPARKLINE_FANOUT_LIMIT` 可随后端批量能力落地调整。

## Risks / watch list

- **Next 16 + React 19 下 ECharts 6 SSR**：sparkline 必须 `"use client"` + dynamic import；禁止 Server 渲染 ECharts。
- **Trend fanout 性能**：每行 `getInstanceTrends` 是 1 次请求；30 行 × 1 window 的并发在 `cache: no-store` 下走实网请求。上限 30 行 + `Promise.all` 控制。
- **Dialog 合法 a11y**：抽屉（drawer）语义走 `<Dialog>` primitive（已有），非从零自造；如需 side-sheet 外观，额外加 className 定位即可，禁止改 primitive。
- **Cookie forwarding**：validateInstanceAction 必须转发 session cookie，否则 401；参考 `server-api.ts` 已有 `buildCookieHeader` 的思路（内部函数，需在 action 内复刻或提取到 helper）。
