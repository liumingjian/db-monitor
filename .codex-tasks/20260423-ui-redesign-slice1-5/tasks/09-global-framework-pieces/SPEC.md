# Slice 1.5 — 子 #9 Global Framework Pieces SPEC

## 决策来源
- ADR-0012 D4 TopBar 规格（⌘K / 通知铃铛）
- ADR-0012 D6 Tier 4 全局框架件（健康指示器 / ⌘K 命令面板 / Notification 抽屉 / on-call 模式）
- Q17 九条规则（SHARED-BRIEF + 任务 brief）
- 子 #5 Alerts SPEC 约定的 `alerts.oncall` localStorage key

## Q17 九条规则对照
1. **⌘K 命令面板触发**：`cmd+k` / `ctrl+k` 全局唤起；TopBar 中点击搜索按钮也进入；再按 `Esc` 关闭。
2. **Local fuzzy search（禁用外部 search 库）**：自写 token-based scorer（前缀 + 子序列 + 子串 bonus），零运行时依赖，纯 TS。
3. **搜索域**：导航路由（来自 `nav.*` i18n + 路由静态表）+ 实例列表（`apiClient.listInstances()`）+ 规则列表（`apiClient.listRules()`）。
4. **Keyboard-first**：`↑/↓` 移动 active item，`Enter` 跳转，`Esc` 关闭，`⌘K` 重新唤起。
5. **Modal 用 Dialog primitive**：`Dialog` + `DialogContent` + `DialogOverlay`（已在 packages/ui/src/primitives/dialog.tsx）。
6. **Notification 抽屉 3 tab**：告警（alerts）/ 通知投递（notify history）/ 系统（system）。从 TopBar 铃铛图标触发。
7. **On-call 模式 toggle 持久化**：`localStorage` key `alerts.oncall`（与子 #5 共享）；存 `{ enabled, enabledAt }`；页面加载时检查 2h 是否已过，已过则 auto-off。
8. **OS Notification API 推送**：开启时请求 permission；granted 后订阅到 `alerts.oncall.pulse` 事件（后续 Alerts 页可以 `window.dispatchEvent` 触发）；denied 时 console.warn 回退到页内 Toast（不静默丢弃）。
9. **2h auto-off**：setTimeout 计时器 + localStorage 时间戳双重保险（跨 tab / 刷新都有效）；计时到点自动关闭 toggle + 关闭 OS notification 订阅 + 清理事件。

## 交付清单
- `packages/ui/src/layout/command-palette.tsx`（新增，纯 UI，受控）
- `packages/ui/src/layout/notification-drawer.tsx`（新增，纯 UI，受控）
- `packages/ui/src/layout/on-call-banner.tsx`（新增，纯 UI，toggle + 状态 badge）
- `packages/ui/src/layout/fuzzy-match.ts`（新增，零依赖 scorer + 单元测试可达）
- `packages/ui/src/layout/index.ts`（追加 export）
- `apps/web/src/components/shell/app-command-palette.tsx`（bridge，加载 items 并驱动 `CommandPalette`）
- `apps/web/src/components/shell/app-notification-drawer.tsx`（bridge，驱动 NotificationDrawer）
- `apps/web/src/components/shell/on-call-context.tsx`（Provider + hook；持久化 `alerts.oncall`；OS Notification API；2h auto-off）
- `apps/web/src/components/shell/command-palette-context.tsx`（Provider + hook：open/close/toggle；全局 `⌘K` 监听）
- `apps/web/src/components/shell/index.ts`（barrel）
- `apps/web/app/api/command-palette/route.ts`（Route Handler：返回 nav + instances + rules 的 command items；复用 `requireServerSession` + `createServerApiClient`）
- `apps/web/src/providers.tsx`（包裹 CommandPaletteProvider + OnCallProvider + AppCommandPalette + AppNotificationDrawer）
- `apps/web/messages/zh-CN.json` 追加 `commandPalette.*` / `notifications.*` / `oncall.*`
- `apps/web/tests/command-palette.test.ts`（fuzzy + on-call 2h 时间线 + store 行为）

## 不改
- `packages/ui/src/primitives/`、`packages/ui/src/styles/tokens.css`
- `packages/ui/src/layout/{app-shell,icon-rail,contextual-sidebar,top-bar,canonical-page-template}.tsx`
- `apps/web/app/design-demo/page.tsx`
- 他人 i18n namespace

## Done-When
- `pnpm --filter web lint` 无 error
- `pnpm --filter web typecheck` 无 error
- `pnpm --filter web test`：新增测试 + 104 原测试全绿（不降级）
- `pnpm --filter web build` 全路由通过
- `apps/web/app/api/command-palette/route.ts` 在未登录态返回 401（依赖 requireServerSession）
- `⌘K` 在任意已登录页面可唤起并过滤；`Esc` 可关闭
- on-call 在非安全上下文（OS Notification API 不可用）console.warn + 页内 Toast
- 2h auto-off 在 localStorage 时间戳过期时立即生效（刷新触发）
