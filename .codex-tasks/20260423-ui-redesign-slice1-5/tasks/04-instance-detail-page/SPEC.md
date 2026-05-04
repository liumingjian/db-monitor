# 04 — Instance detail page (Slice 1.5)

> 决策源: ADR-0012 (Q13 — Instance Detail: 8 tab + Kill 防误杀) + SHARED-BRIEF + SUBTASKS.csv id=4
> 执行形态: **single-full**（tab 间共享 instance / quick metrics / shell，拆 8 子任务反而增加粘合成本）

## 目标

按 Q13 十条规则重写 `apps/web/app/instances/[instanceId]/**`：
- 引入 8 tab（概览 / 性能 / 会话 / SQL / 存储 / 复制 / 配置 / 审计）
- 顶部 Quick Metrics Strip，30s auto-refresh（`useAutoRefresh`）
- Kill 二次确认（用户键入 `thread_id` 全匹配才启用）
- Canonical 7 段式 + AppShell + 设计系统 tokens
- Tier 3 honest placeholder（复制 / 配置）
- 审计 tab 前端合成（`listAlerts` + `listNotifyHistory` 按 instance_id 过滤）

## Q13 十条规则对照

1. **8 tab 布局**：概览 / 性能 / 会话 / SQL / 存储 / 复制 / 配置 / 审计。tab 子路由，URL 决定激活项。engine 不匹配的 tab（如 MySQL 无存储）仍显示但占位说明。
2. **Quick Metrics Strip 30s auto-refresh**：顶部 5–6 key metric（validation / server_role / QPS / 连接 / 慢查询 / 复制延迟若可见），走 `useAutoRefresh(30_000)`。Trend 缺失退化为 `—`，标注 "尚未上报"（不伪造）。
3. **Kill 二次确认**：点 Kill → `Dialog` 弹窗 → 用户键入 `thread_id` 字符串精确匹配 `entry.process_id`，才启用确认按钮；`reason` 必填；提交后进入 `pending` 态；成功后 toast/banner + 关闭。
4. **Canonical 7 段**：PageBreadcrumb / EntitySummary / QuickMetrics / TabBar / PageContent，不自造骨架。
5. **Severity 四色 token**：`EntityBadge` tone / `critical|warning|info|ok`，禁止硬编码 hex。
6. **数字 `tabular-nums`**：所有表格数值列、metric value 使用 `font-mono tabular-nums`。
7. **无 spinner**：pending/refetch 态用 `Skeleton`；Kill 提交期间按钮 disabled + 文案切换。
8. **Tier 3 placeholder**：复制 tab 与 配置 tab 给出 "Slice 2 交付" 说明卡（不伪造数据、不新增后端端点）。
9. **空 / 加载 / 错误三分**：每 tab 单独处理；validation 未通过 → 限定引导；无采集 → 引导；无匹配 → 引导。
10. **不硬编码 hex**：复用 tokens (`var(--accent)` 等已存在的仅限 legacy 颜色）；新建文件全部走 packages/ui tokens（`text-fg-primary`, `border-border-hairline`, `bg-surface-overlay` 等）。

## Tier 分层

| Tab | Tier | 说明 |
|---|---|---|
| 概览 | 1 真数据 | `getInstance` + `getInstanceTrends` |
| 性能 | 1 真数据 | `getInstanceTrends(window)` + preset nav |
| 会话 | 1 真数据 | `getInstanceProcesslist` + `killProcess`（含二次确认） |
| SQL | 1 真数据 | `getInstanceSlowQueries`（engine=mysql） |
| 存储 | 1 真数据 | `listTablespaces` + `getTablespaceHistory`（engine=oracle） |
| 复制 | 3 占位 | 后端无端点，Tier 3 "Slice 2 交付" |
| 配置 | 3 占位 | 后端无端点，Tier 3 "Slice 2 交付" |
| 审计 | 1 合成 | `listAlerts(instance=id)` + `listNotifyHistory()` 前端 filter instance_id；无专属端点但可用现有能力 |

## 写作用域

- `apps/web/app/instances/[instanceId]/**`
  - `layout.tsx`（AppShell + 8 tab 装配）
  - `page.tsx`（概览 tab）
  - `performance/page.tsx`（性能 tab，新建；原 page.tsx 的 trend+preset 模块迁过来）
  - `processes/page.tsx`（会话 tab，保留并接入二次确认）
  - `slow-queries/page.tsx`（SQL tab）
  - `tablespaces/page.tsx`（存储 tab）
  - `replication/page.tsx`（Tier 3 占位，新建）
  - `configuration/page.tsx`（Tier 3 占位，新建）
  - `audit/page.tsx`（审计 tab，前端合成，新建）
  - `_components/kill-process-dialog.tsx`（重写为 thread_id 二次确认）
  - `_components/kill-process-action.ts`（保持，或微调）
- `apps/web/src/components/instance-detail/**`（新建）
  - `instance-detail-shell.tsx` — AppShell + IconRail + TopBar + 8 tab
  - `instance-quick-metrics.tsx` — `use client` + `useAutoRefresh(30_000)` + router.refresh
  - `tier3-placeholder-card.tsx`
  - `audit-feed.tsx`（前端合成 timeline）
- `apps/web/messages/zh-CN.json` 的 `instanceDetail.*` namespace（追加）

## Done-when

- `pnpm --filter web lint` 无 error
- `pnpm --filter web typecheck` 无 error
- `pnpm --filter web test` 至少维持 127（新增测试允许，不降级）
- `pnpm --filter web build` 至少保持 20 路由（新增 `performance` / `replication` / `configuration` / `audit` 4 条子路由 → 预期 24 路由）
- Q13 10 条规则全绿，UI 内可见
