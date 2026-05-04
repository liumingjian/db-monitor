# Child #7 — Notify History + Channels Page

> Parent: `.codex-tasks/20260423-ui-redesign-slice1-5`
> Dependencies: Child #0 (design system foundation) DONE
> Scope: 单 full task — 同时交付两张 Tier 1 页

## 1. 目标

按 ADR-0012 Q14 的 9 条规则把 `/admin/notify-history` 与 `/admin/channels` 两张 Tier 1 页面铺到 Canonical page template 上：

- **Notify history**：Feed 游标分页表格 + 6 段抽屉（Summary / Recipient / Payload / Attempts timeline / Related alert / Actions）
- **Channels**：只读视图（Slice 1.5 范围内；写能力留给 Slice 2 `PostgresBindingRepository` 落地后）

## 2. Q14 九条规则（Slice 1.5 实施解读）

| # | 规则 | 本切片落地点 |
|---|---|---|
| 1 | Notify history 使用 **Feed**（Q8 表格三分法）而非 Catalog | `searchParams.cursor` + `limit` 游标分页（基于 `attempted_at` 排序） |
| 2 | 列：channel / status / rule_id / instance_id / attempt / attempted_at / delivered_at | 表头 + 行，时间走 mono，null 显示 `—` |
| 3 | status 映射到四色严重度轴 | delivered→ok / failed→critical / skipped→muted / pending→info；**禁止自造颜色** |
| 4 | 过滤 chip：channel / status / rule_id / instance_id | chip 条 + URL searchParams 持久化 |
| 5 | 行点击打开 **6 段 drawer** | Summary / Recipient / Payload / Attempts timeline / Related alert / Actions |
| 6 | drawer 的 "Attempts timeline" 聚合同一 `rule_id + channel + payload_hash` 的所有 attempts | 客户端按 `rule_id/channel` 聚合当前页数据，展示 attempt 时间线（按钮状态+时间+error） |
| 7 | "Related alert" 只读链接到对应 rule / instance detail 页 | 指向 `/rules/<rule_id>` 与 `/instances/<instance_id>`；没有 instance 则显示 `fleet-wide` |
| 8 | **Channels 只读视图**，明确标注 "Slice 1.5 视图，编辑能力待 Slice 2"；禁止任何 POST/PUT/DELETE | Channels 页展示当前已注册通道目录 + 每通道最近投递摘要（`listNotifyHistory` 聚合），顶部 banner 明示只读 |
| 9 | 通用态规范：Skeleton 加载、空态三分法（首次/过滤/业务空）、时间 <24h 相对 ≥24h 绝对 | `<Skeleton>`；三种空态文案分支；`formatRelativeTime` / `formatTimestamp` |

## 3. 写作用域（disjoint）

```
apps/web/app/admin/notify-history/**        （改写 page.tsx + 新增私有 _components 可选）
apps/web/app/admin/channels/**              （新建）
apps/web/src/components/notify/**           （新建共享组件：NotifyDrawer / FilterChips / 行单元）
apps/web/messages/zh-CN.json                （追加 notifyHistory.* + channels.* namespace）
```

禁止触碰：
- `packages/ui/src/**`（#0 产物）
- `apps/web/app/layout.tsx` / `apps/web/src/providers.tsx`（#9）
- `apps/web/messages/zh-CN.json` 的十个已存 namespace 内部

## 4. 数据契约（不得改动）

- `apiClient.listNotifyHistory({ channel?, status?, rule_id?, limit? })` → `NotifyHistoryResponse[]`
- `NotifyHistoryResponse { attempt, attempted_at, channel, delivered_at, error, instance_id, organization_id, rule_id, status }`

**注意**：API 目前只提供 `limit` 一种限流方式、无 cursor 字段。本切片的 Feed 游标分页通过 **页尾最后一行 `attempted_at` 做 `before` 过滤** 的客户端策略实现；若 Slice 2 扩展 API 再改。在 API 未扩 `before` 参数前，分页只支持"下一页"单向游标（通过客户端缓存处理），本切片实现单页 + "载入下一页"按钮：每次将 `limit` 提升。

> **Debug-First**：不得给不存在的 filter（e.g. `instance_id`）静默吞错。`instance_id` 不在 `ListNotifyHistoryFilters` 里——在 URL 里接受但过滤通过客户端侧 post-filter 实现，并在 UI chip tooltip 上注明"客户端过滤（Slice 2 后端扩容）"。

## 5. Done-When

1. `/admin/notify-history` 与 `/admin/channels` 两条 Next.js 路由构建通过
2. 两张页面采用 Canonical page template（`AppShell + IconRail + ContextualSidebar + TopBar + CanonicalPageTemplate`）
3. 任何 status 颜色通过 `EntityBadge` 或 tokens（`bg-severity-*`）；**无 hardcoded hex**
4. Channels 页顶部有明示 banner："Slice 1.5 只读视图，编辑能力待 Slice 2"
5. Channels 页不出现任何 POST/PUT/DELETE；`page.tsx` 只读 `listNotifyHistory`
6. drawer 6 段齐全，每段有 i18n key
7. `pnpm --filter web lint` / `typecheck` / `test`（≥104）/ `build`（≥ 12 路由）全绿
8. `zh-CN.json` 只追加 `notifyHistory.*` + `channels.*`，不改已有 namespace

## 6. Not-doing（超出范围一律拒绝）

- 不做 POST/PUT/DELETE（Channels）
- 不动 layout.tsx / providers.tsx
- 不动 tokens.css / primitives / layout components
- 不做 Slice 2 才需要的 WeCom / SMS 通道 UI
- 不做 E2E / 视觉回归（归子 #10）
