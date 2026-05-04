# SPEC — Slice 1.5 Child #3: Instances list page

> 父任务: `.codex-tasks/20260423-ui-redesign-slice1-5/`
> 决策源: ADR-0012（Q7 / Q8 / Q12 / Q16）+ SHARED-BRIEF + SUBTASKS.csv id=3
> 前置: child #0（设计系统地基） DONE
> 写作用域: `apps/web/app/instances/page.tsx` + `apps/web/app/instances/_list/**`（可选子段）+ `apps/web/src/components/instances-list/**` + `apps/web/messages/zh-CN.json` 的 `instancesPage.*` namespace

## 目标

把 `/instances` 从旧 AppChrome 的"分栏表单 + 卡片列表"全面重做成 ADR-0012 Canonical 页，承担 Slice 1.5 Catalog 表格范式的门面，提供 Fleet 级实例浏览、筛选、双视图切换、行内 sparkline、真实的新建与重验证能力。

## Boss 裁决：A 方案最终作用域

**Tier 1 真实落地**：

1. 双视图（表格 / 栅格）切换 —— URL `?view=table|grid`
2. 行内 sparkline（mini line chart）—— 3 metric 可切换：
   - **连接数**（`mysql_threads_connected` / `oracle_sessions_total`）
   - **QPS**（`mysql_queries_per_second` / `oracle_user_calls_per_second`）
   - **活跃**（`mysql_threads_running` / `oracle_sessions_active`） — 代替"CPU"（Slice 1 后端未暴露 CPU metric，禁止伪造）
3. 顶部 filter chip 条：env / status（passed/failed）/ label
4. 新建抽屉（Dialog primitive 扩展）—— 接真 `createInstanceAction`
5. 空态 + 首次接入引导（零实例时的 Canonical empty state）
6. 重验证按钮 —— 接真 `POST /control/instances/{instance_id}/validate`（新增 `validateInstanceAction` server action，直接走 `fetch` + 复用 `getServerApiBaseUrl()` + cookie 转发，**不触碰** `packages/api-client/**`）

**Tier 3 honest placeholders**（按钮/菜单渲染为 `disabled`，Tooltip 文案"将在 Slice 2 上线"，**禁止**假 server action / 假状态流转）：

- 编辑抽屉
- 删除按钮
- 批量启用/停用
- 批量删除

**Tier 3 横幅**：底部浅色可关闭横幅一条 "批量运维能力将在 Slice 2 交付"，关闭状态 localStorage 持久化（key = `instances.slice2Banner.dismissed`）。

## Done-When

1. `/instances` 渲染 Canonical 7 段式（PageBreadcrumb → EntitySummary → QuickMetrics → TabBar (视图切换) → PageContent），包裹在 AppShell (IconRail + ContextualSidebar + TopBar)。
2. 表格 / 栅格双视图通过 URL `?view=` 参数共享；缺省 `table`。
3. 每行/每卡内嵌 mini sparkline，metric 通过 URL `?spark=connections|qps|active` 切换，缺省 `connections`。
4. Filter chip 条支持 env / status / label；应用后写回 URL search param，与现有 `buildInstanceListFilterValues` 兼容。
5. 新建抽屉使用 `@db-monitor/ui` `Dialog`，表单提交走 `createInstanceAction`（已存在）。
6. 重验证按钮每行一个；点击触发 `validateInstanceAction`（本任务新增），成功后 `revalidatePath('/instances')`；失败按 Q16 规则 3 冒 Toast。
7. 空态：列表为 0 时渲染 "首次接入引导" 卡片（含"新建实例"主 CTA + 文档链接占位）；当前过滤条件为 0 时渲染"过滤无结果" 空态并提供"清除过滤"。
8. Tier 3 按钮：编辑 / 删除 / 批量启用/停用 / 批量删除 —— 渲染 `disabled`，`<Tooltip>` 显示"将在 Slice 2 上线"；**不写任何 server action**。
9. 底部横幅："批量运维能力将在 Slice 2 交付"，`×` 关闭后写 localStorage，刷新不再显示。
10. ECharts sparkline 只用 `var(--chart-N)` + `--fg-*` + `--border-*`；禁止硬编码 hex；走 `overview-chart-palette.ts` 暴露的 `readChartPalette()` 作为色源（跨页复用）。
11. 加载 / 空态 = `<Skeleton>`；无 spinner / glassmorphism / 硬编码中文 namespace（新增全部进 `instancesPage.*`）。

## Q12 八条规则对应清单

| # | 规则 | 本页落地 |
|---|---|---|
| 1 | Canonical 7 段式 | AppShell + CanonicalPageTemplate 包裹 ✓ |
| 2 | 表格 + 栅格双视图（Catalog 范式） | `?view=table|grid` + TabBar 切换 ✓ |
| 3 | 行内 sparkline | `InstanceSparkline` mini ECharts（3 metric 可切换）✓ |
| 4 | Filter chip 条 | `InstancesFilterChips`（env / status / label）✓ |
| 5 | 抽屉式新建（Create） | `CreateInstanceDrawer` + Dialog + createInstanceAction ✓ |
| 6 | 空态 + 首次接入引导 | `InstancesEmptyState` + 清除过滤 CTA ✓ |
| 7 | 重验证（Re-validate） | `RevalidateInstanceButton` + validateInstanceAction ✓ |
| 8 | Tier 3 honest placeholders | 编辑 / 删除 / 批量 —— disabled + Tooltip "Slice 2 上线" ✓ |

## 遗留项（移交 Slice 2）

- 编辑实例（PUT `/control/instances/{id}`）—— 后端是否提供？ Slice 2 前端接入时确认。
- 删除实例（DELETE `/control/instances/{id}`）—— 同上。
- 批量启用/停用 —— 后端无对应端点；需与 backend 联合设计（Slice 2）。
- 批量删除 —— 同上。
- CPU metric —— Slice 1 后端未暴露；Slice 2 看是否启用 `os_cpu_usage` 等系统级采集。
- 文档链接（"查看接入指南"）—— 文档站 Slice 2 上线前先链 `#docs-coming-soon`（honest placeholder）。

## 数据源

- 列表：`apiClient.listInstances(filters)` （Server Component 直接调用）
- sparkline：每行并行 `apiClient.getInstanceTrends(instance_id, '1h')`，取 3 个候选 metric 的 points；在 Server Component 用 `Promise.all` 聚合；`sparkValues = Record<instance_id, Record<metric_key, number[]>>`。
  - 注意：列表超过 30 条时，对超出行跳过 trend 拉取（sparkline 回落为 Skeleton + "超过 30 条实例，sparkline 暂不渲染" 提示），避免一次并发 30+ 请求拖慢首屏。
- 重验证：新增 `validateInstanceAction(formData)` 到 `apps/web/src/monitoring-actions.ts`；直接 `fetch` `${API_BASE}/control/instances/${id}/validate` + 转发 cookie；成功后 `revalidatePath('/instances')`；失败抛错由 React Server Action 边界展示。

## 非目标（Out of Scope）

- 命令面板（⌘K）、Notification Drawer、on-call 模式：归 #9。
- `providers.tsx` / `app/layout.tsx` 改造：归 #9；本页先用 page-local 组装。
- Instance Detail 页：归 #4；本页只负责跳转入口。
- 编辑 / 删除 / 批量操作的真实能力：归 Slice 2（本页仅 honest placeholder）。
- CPU metric 落地：归 Slice 2（后端待定）。

## 禁止项（本任务 Red Lines）

1. 不改 `packages/api-client/**`（只读）。
2. 不改 `apps/api/**`（只读）。
3. 不改 `packages/ui/src/primitives/**`、`packages/ui/src/layout/**`、`packages/ui/src/styles/tokens.css`。
4. 不改 `apps/web/app/layout.tsx` / `apps/web/src/providers.tsx`（#9）。
5. 不改 `apps/web/messages/zh-CN.json` 现有 10 个 namespace；只追加 `instancesPage.*`。
6. 不使用 spinner；禁硬编码 hex；禁 glassmorphism；禁 mock/fake server action。
7. 禁止为 Tier 3 按钮实现任何后端旁路（假 toast / 假 revalidate / 假状态流转）。

## 验收门（必须全绿）

- `pnpm --filter web lint` 无 error
- `pnpm --filter web typecheck` 无 error
- `pnpm --filter web test` 不降级（基线 104 tests）
- `pnpm --filter web build` 所有路由通过
