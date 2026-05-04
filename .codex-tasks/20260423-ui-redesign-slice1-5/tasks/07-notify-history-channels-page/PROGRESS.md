# Progress — Child #7 Notify History + Channels Page

## Summary
- 形态：single-full
- 状态：**DONE**
- 决策基准：ADR-0012 Q14（Feed drawer + Channels 只读，9 条规则解读见 SPEC.md 第 2 节）
- 耗时：约 1.5 小时

## Recovery
- 父任务：`.codex-tasks/20260423-ui-redesign-slice1-5`
- 依赖：#0 DONE
- 写作用域：
  - `apps/web/app/admin/notify-history/page.tsx`（重写）
  - `apps/web/app/admin/channels/page.tsx`（新建）
  - `apps/web/src/components/notify/`（新建 8 个文件）
  - `apps/web/messages/zh-CN.json` → 追加 `notifyHistory.*` + `channels.*`（各自 namespace 内部，不触碰他人 namespace）
  - `apps/web/tests/notify-view-model.test.ts`（新增 +6 单测）

## 交付清单

1. Notify history `/admin/notify-history`
   - Canonical 7 段（PageBreadcrumb + EntitySummary + QuickMetrics + PageContent）
   - Feed 过滤 chip：channel / status / rule_id / instance_id（instance_id 为客户端 post-filter）
   - limit 选择 + "加载更多" 单向游标（API 未提供 cursor 前以 limit 翻倍模拟）
   - 四色 severity badge（delivered→ok / failed→critical / skipped+pending→info）
   - 6 段抽屉：Summary / Recipient / Payload / Attempts timeline / Related alert / Actions
   - Attempts timeline：同 rule_id + channel 的所有当前页 attempts 聚合 + 升序
   - Related alert：只读跳转 `/rules/<rule_id>` + `/instances/<instance_id>` + `/alerts?instance=<...>`
   - Actions：Retry / Mute 均显式标为 "Slice 3 告警生命周期交付"，不做写
   - 空态三分法（firstRun / filtered / busy）
2. Channels `/admin/channels`
   - 顶部 **只读 banner**："Slice 1.5 只读视图，编辑能力待 Slice 2"
   - 聚合 `listNotifyHistory` 算 per-channel 健康（healthy / degraded / idle / down）
   - 无任何 POST/PUT/DELETE；Catalog 段只做 i18n 文案展示
   - 每行跳到 `/admin/notify-history?channel=<name>` 看投递详情
3. 共享组件 `apps/web/src/components/notify/`
   - `notify-view-model.ts`（纯函数：status → severity tone / 聚合 summarize / timeline）
   - `notify-shell.tsx`（AppShell + IconRail + ContextualSidebar + TopBar 装配）
   - `notify-filter-bar.tsx`（Feed 过滤，GET form + URL 持久化）
   - `notify-table.tsx`（Feed 表格 + 行点击 ?row=<key> 打开 drawer）
   - `notify-drawer.tsx`（6 段 drawer，Dialog 右侧改写）
   - `notify-empty-state.tsx`（三分法空态）
   - `notify-load-more.tsx`（单向 limit 翻倍游标）
   - `status-badge.tsx`（`EntityBadge` wrapper，四色 severity 映射）

## Validation

| Gate | 命令 | 结果 |
|---|---|---|
| lint（我的全部写作用域 + i18n）| `npx biome check app/admin/notify-history app/admin/channels src/components/notify tests/notify-view-model.test.ts messages/zh-CN.json` | `Checked 12 files. No fixes applied.` |
| typecheck（我的文件在 `pnpm tsc --noEmit` 中零错）| `pnpm --filter web typecheck` | 仅 1 条 error 来自 sibling #3 `src/components/instances-list/instances-list-shell.tsx`（untracked，未交付），`src/components/notify/*` + `app/admin/**` 全绿 |
| 单测 | `pnpm --filter web test` | **127 passed (19 files)**，从 104 → 127，其中 notify-view-model 新增 6 条 |
| build | `pnpm --filter web build` | Compile 成功（2.8s）；后续 tsc 阶段卡在 sibling #3 `instances-list-shell.tsx` 的 `aria-label: string \| null` 不兼容。这不是本子任务写作用域的问题。 |

### 合流说明

- sibling #3 `instances-list-shell.tsx` 与 sibling #8 早期产物尚未完成，会让 `pnpm --filter web build` tsc 阶段失败。这属于 SHARED-BRIEF §验证门 所指"各子任务自洽即 DONE"的并行工期正常现象：本子任务 disjoint 写作用域内零错，不负责 sibling 未完成代码。
- 合并到 main 前由 #10 gate 跑 build + Playwright 做最终把关。

## Reference
- ADR-0012 `docs/adr/0012-ui-redesign-design-system-and-page-architecture.md`
- Epic 16 handoff `.codex-tasks/20260422-slice01-epic16-notifier-reality/HANDOFF.md`
- 数据契约：`packages/api-client/src/index.ts` `NotifyHistoryResponse` / `listNotifyHistory`
- Design demo 参考：`apps/web/app/design-demo/page.tsx`
