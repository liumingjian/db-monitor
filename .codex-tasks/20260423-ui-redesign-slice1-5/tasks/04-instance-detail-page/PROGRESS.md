# 04 — Instance detail page PROGRESS

## Baseline (2026-04-23 08:55)

- `pnpm --filter web test` → 127 passed (19 files)
- Build baseline 20 routes（per SHARED brief）
- 现有 legacy 结构：layout.tsx（AppChrome + InstanceTabNav 2–3 tab）+ page.tsx（概览+性能混一张页）+ processes / slow-queries / tablespaces 3 个子路由 + _components/**

## Decision log

- 选择 **single-full**：8 tab 共享 instance fetch / QuickMetrics / shell，拆 8 子任务粘合成本超过合并成本
- **Overview 与 Performance 分离**：ADR-0012 Q13 要求 8 tab，原 page.tsx 把"概览 + 性能"挤在同一路由，需要把 trend+preset+capacity 拆到 `/performance` 子路由
- **审计 tab 不占位**：`listAlerts` 已支持 `instance` 过滤，`listNotifyHistory` 前端按 `instance_id` 过滤是真数据合成（不是 Tier 3 伪造），与 Settings+Audit page (#8) 的审计前端合成模式同构
- **Kill 二次确认**：选择 Dialog primitive 重写，废弃 native `<dialog>` + 原 action 保留；thread_id 字符串 exact-match（与 GitHub 删仓库、Lepus 删库模式一致）
- **QuickMetrics 30s 刷新**：走 `router.refresh()`（Server Component revalidate），不在 client 发请求；避免与 Kill/filter form 的 server actions 打架

## Validation log

- 2026-04-23 09:00 `pnpm --filter web typecheck` → 无 error
- 2026-04-23 09:00 `pnpm --filter web lint`（biome check --write 自动格式化后）→ 无 error
- 2026-04-23 09:04 `pnpm --filter web test` → **134 passed (20 files)**，较基线 127 +7（新 `tests/instance-detail.test.ts` 覆盖 buildInstanceTabs / buildInstanceQuickMetricItems / buildInstanceAuditFeed）
- 2026-04-23 09:05 `pnpm --filter web build` → 25 路由全绿（较基线 20 新增 `/instances/[instanceId]/audit`, `/.../configuration`, `/.../performance`, `/.../replication`；加 admin/channels 保留）

## 产出清单

### 新增（应用代码）
- `apps/web/app/instances/[instanceId]/layout.tsx`（重写）— AppShell + CanonicalPageTemplate + PageBreadcrumb + EntitySummary + QuickMetrics + 8 tab
- `apps/web/app/instances/[instanceId]/page.tsx`（重写）— 概览 tab：实例身份 / capability / server metadata / detail readouts
- `apps/web/app/instances/[instanceId]/performance/page.tsx`（新建）— 性能 tab：TimeWindowNav + PresetNav + metric cards + capacity readout + MetricChart
- `apps/web/app/instances/[instanceId]/replication/page.tsx`（新建）— Tier 3 placeholder
- `apps/web/app/instances/[instanceId]/configuration/page.tsx`（新建）— Tier 3 placeholder
- `apps/web/app/instances/[instanceId]/audit/page.tsx`（新建）— 审计时间线（alerts + notify history 合成）
- `apps/web/app/instances/[instanceId]/processes/page.tsx`（微调）— PageContent wrapper + token 化
- `apps/web/app/instances/[instanceId]/slow-queries/page.tsx`（微调）— PageContent wrapper + engine-unsupported notice
- `apps/web/app/instances/[instanceId]/tablespaces/page.tsx`（微调）— PageContent wrapper + engine-unsupported notice
- `apps/web/app/instances/[instanceId]/_components/kill-process-dialog.tsx`（重写）— Dialog primitive + thread_id exact-match 二次确认
- `apps/web/app/instances/[instanceId]/_components/kill-process-action.ts`（微调）— 增加 `confirm_thread_id` 服务端二次校验

### 新增（可复用组件）
- `apps/web/src/components/instance-detail/instance-detail-shell.tsx` — AppShell 装配（镜像 #3 InstancesListShell）
- `apps/web/src/components/instance-detail/instance-tabs.ts` — `buildInstanceTabs` 8 tab 工厂
- `apps/web/src/components/instance-detail/instance-tabs-bar.tsx` — client TabBar（usePathname 决 activeKey）
- `apps/web/src/components/instance-detail/instance-quick-metrics.tsx` — `useAutoRefresh(30_000)` + `router.refresh()`
- `apps/web/src/components/instance-detail/instance-metrics.ts` — `buildInstanceQuickMetricItems`（MySQL/Oracle 不同指标映射，trend 缺失 `—`）
- `apps/web/src/components/instance-detail/tier3-placeholder-card.tsx`
- `apps/web/src/components/instance-detail/audit-feed.ts` — `buildInstanceAuditFeed`

### 删除
- `apps/web/src/components/instance-tab-nav.tsx`（legacy，已被 InstanceTabsBar 取代）

### 追加 i18n
- `apps/web/messages/zh-CN.json` 的 `instanceDetail.*` namespace（41 key：breadcrumb/tab × 8/quickMetric × 6/killDialog × 8/tier3 × 5/audit × 4/notices × 6）

### 新增测试
- `apps/web/tests/instance-detail.test.ts` 7 tests

## 遗留风险

- Quick Metrics 的指标映射（`mysql_cpu_utilization` / `oracle_cpu_utilization` 等）假设采集端用这些固定 metric_name；若采集端换命名需同步更新 `instance-metrics.ts` 的 `MYSQL_METRIC_MAP` / `ORACLE_METRIC_MAP`。trend 里找不到对应 card 时显示 `—`，不伪造。
- 审计 tab 依赖 `listNotifyHistory()` 默认返回（fetch 200 条），若某实例通知历史超过该限制，尾部会被截断；后续后端若开放 `instance_id` 过滤可直接 narrow 掉 limit。
- Kill Dialog 客户端与服务端 action 都校验 `confirm_thread_id === String(processId)`；但 server action 在校验失败时只返回 `invalid_input`，UX 不会暴露具体哪项字段失败；一旦客户端 bypass，用户只看到 "请输入 kill 原因" 兜底文案（与 legacy 一致）。若需要精细提示可扩 `KillProcessErrorCode`。
- 性能 tab 的 Capacity Insight tone 仍复用 monitoring-ui 的 `"steady" | "watch" | "risk"`；已在 CSS 层映射到 `sev-*` token，但未引入 `tone="critical"` 以避免改后端模型。
