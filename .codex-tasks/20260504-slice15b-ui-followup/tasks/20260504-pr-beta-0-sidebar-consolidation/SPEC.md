# SPEC — PR β.0: Sidebar Consolidation + AppShell 重构

> 父 epic: `.codex-tasks/20260504-slice15b-ui-followup/EPIC.md` child #2
> 上游 ADR: `docs/adr/0016-sidebar-consolidation.md`（修订 ADR-0012 D4 仅一项）
> 决策来源: 2026-05-04 grilling 第二轮 Q1-Q5 推荐打包通过
> 估时: 2-3 天

## Goal

按 ADR-0016 落地单 sidebar 取代 IconRail + ContextualSidebar 双栏拓扑。**单条爆破 ADR-0012 D4，其余 D 项守不动**。

## Acceptance Criteria

机器闸门：
- pnpm lint 全绿（212 files clean）
- pnpm typecheck 全绿
- pnpm test 全绿（135+ tests）
- pnpm --filter web build 全绿（route count 不变 = 25）

行为闸门（playwright headed 验证）：
- 默认展开 240px / chevron toggle 折叠到 64px / `[` 键切换
- 折叠态 hover icon 显示 native tooltip（`title` attribute 即可，不做 popover）
- localStorage `ui.sidebar.collapsed` 持久化跨会话
- 4 段 grouped section 顺序固定 OBSERVE/ALERT/OPERATE/ADMIN
- 展开态 section heading 可见；折叠态 heading 隐藏
- active item 行高亮（左 2px accent border + bg-accent/10 + icon text-accent）
- 7 个 page 全部走新 Sidebar：/overview /alerts /alerts/[id] /rules /rules/[id] /instances /instances/[id]/* /admin/* /settings

代码门：
- `packages/ui/src/layout/icon-rail.tsx` + `contextual-sidebar.tsx` 已删（git 检查）
- `packages/ui/src/layout/sidebar.tsx` 已建
- `AppShell` 组件 `iconRail` prop 已删（接口 breaking change 显式落到类型）
- `SidebarItemModel.group` 必填（TypeScript 编译保证）
- 任意 import `IconRail` 或 `ContextualSidebar` 全仓 0 命中（grep 验证）

## Implementation Plan

### Phase 1 — Primitive 重构（packages/ui）

1. 新建 `packages/ui/src/layout/sidebar.tsx`：
   - State: `useState<boolean>(false)` for `collapsed` + sync from `localStorage["ui.sidebar.collapsed"]` on mount（`useEffect`）
   - Width: `cn("w-60", collapsed && "w-16")` — 240 ↔ 64
   - Layout: `<aside>` 顶部 toggle 区（chevron + `aria-label`）；body 4 段 grouped items
   - Each section: `<section>` with `<header>` (展开时显示) + `<ul>` items
   - 折叠态 section heading 隐藏，分隔仍保留（更细 hairline gap）
   - Item: `<a href>` 单行，icon + label，折叠时只 icon
   - Active highlight: 通过 `usePathname` + `matchPrefixes` 判定
   - Tooltip on collapsed: `title` attribute（不引入 popover 库）
   - Keyboard: `useEffect` 全局 keydown listener `[` toggle（避免在 input 内冲突 — check `e.target.tagName !== 'INPUT' | 'TEXTAREA'`）

2. 删 `icon-rail.tsx` + `contextual-sidebar.tsx`：
   - `git rm packages/ui/src/layout/icon-rail.tsx packages/ui/src/layout/contextual-sidebar.tsx`
   - 同步删 `packages/ui/src/layout/index.ts` 中两个 export
   - 删 `IconRailGroup` / `IconRailGroupId` types（不再使用）— 保留 `SidebarItemModel` 并扩 `group` 必填字段

3. 改 `packages/ui/src/layout/types.ts`：
   - `SidebarItemModel` 加 `readonly group: SidebarGroup`
   - 新建 `SidebarGroup` 类型 `"observe" | "alert" | "operate" | "admin"`
   - 删 `IconRailGroup` / `IconRailGroupId` 接口

4. 改 `packages/ui/src/layout/app-shell.tsx`：
   - 删 `iconRail?: ReactNode` prop
   - 保留 `sidebar?: ReactNode` prop（接收新 `<Sidebar>` 实例）
   - 加 `chrome?: "full" | "screen"` prop，默认 `"full"`；`"screen"` 模式下 sidebar 不渲染（为 Slice 3 大屏铺路）

5. 改 `packages/ui/src/layout/index.ts`：
   - 删 `IconRail` / `ContextualSidebar` / `IconRailGroup` / `IconRailGroupId` exports
   - 加 `Sidebar` / `SidebarGroup` exports

### Phase 2 — page-local shell 重写（apps/web/src/components/）

每个 shell 的改动模板：

**Before**:
```tsx
<AppShell
  iconRail={<IconRail groups={ICON_GROUPS} footer={<ThemeToggle .../>} />}
  sidebar={<ContextualSidebar activeGroup="alert" groupLabel="告警" items={SIDEBAR_ITEMS} />}
  topBar={<TopBar ... />}
>
```

**After**:
```tsx
<AppShell
  sidebar={<Sidebar items={SIDEBAR_ITEMS} themeToggle={<ThemeToggle .../>} />}
  topBar={<TopBar ... />}
>
```

每个 shell 的 `SIDEBAR_ITEMS` 改成：

```tsx
const SIDEBAR_ITEMS: readonly SidebarItemModel[] = [
  { group: "observe", href: "/overview", label: "总览", icon: ActivityIcon },
  { group: "observe", href: "/instances", label: "实例", icon: LifeBuoyIcon },
  { group: "alert", href: "/alerts", label: "告警", icon: BellIcon },
  { group: "alert", href: "/rules", label: "规则", icon: RulesIcon },
  { group: "operate", href: "/admin/notify-history", label: "通知投递", icon: SendIcon },
  { group: "operate", href: "/admin/channels", label: "通道配置", icon: ShieldCheckIcon },
  { group: "admin", href: "/admin/audit", label: "审计", icon: ScrollTextIcon },
  { group: "admin", href: "/settings", label: "设置", icon: SettingsIcon },
];
```

7 个 shell 全部 import 同一份 SIDEBAR_ITEMS（提取到 `apps/web/src/components/shell/sidebar-items.ts`，避免 7 处重复声明导致漂移）。

具体 shell 路径：
- `apps/web/src/components/overview/overview-shell.tsx`
- `apps/web/src/components/rules/rules-shell.tsx`
- `apps/web/src/components/alerts/alerts-app-shell.tsx`
- `apps/web/src/components/instances-list/instances-list-shell.tsx`
- `apps/web/src/components/instance-detail/instance-detail-shell.tsx`
- `apps/web/src/components/notify/notify-shell.tsx`
- `apps/web/src/components/settings-audit/admin-shell.tsx`

### Phase 3 — i18n + a11y

- 加 `messages/zh-CN.json` keys: `sidebar.toggleCollapse` / `sidebar.toggleExpand` / `sidebar.section.observe` / `.alert` / `.operate` / `.admin`
- 加 `aria-label` on toggle button（i18n 驱动）
- 加 `aria-expanded={!collapsed}` on `<aside>`
- 加 `role="navigation"` + `aria-label` on `<aside>`
- Item `aria-current="page"` 当 active

### Phase 4 — 验证

- `pnpm lint && pnpm typecheck && pnpm test && pnpm --filter web build`
- `grep -rn "IconRail\|ContextualSidebar" apps packages` 应 0 命中
- docker rebuild web image + up
- playwright headed：
  - 登录 → /overview
  - 测量 sidebar 默认 240px 展开
  - 点 chevron → 测量 64px 折叠
  - 按 `[` → 240px 展开
  - reload → 仍 240px（localStorage 持久化生效）
  - hover folded icon → 检查 `title` attribute
  - 切换 4 个 group 任一 page，验证 active highlight + section heading
  - 截图存证 expanded + collapsed 两态

### Phase 5 — ADR-0016 转 Accepted

- 所有机器门 + 行为门通过后，ADR-0016 状态 `Draft` → `Accepted`
- 提交单独 commit `Mark ADR-0016 Accepted` 标记 PR β.0 落地完成

## Risks

- **localStorage SSR 风险**：`localStorage` 在 server 不存在；`Sidebar` 必须 `"use client"` + 用 `useEffect` 在 mount 后读取，初始 SSR 渲染走默认值 `false`（展开），客户端 hydration 后再 sync 到真实偏好。第一帧可能闪一下，但优于 hydration mismatch。可选缓解：用 `next-themes` 类似的 `suppressHydrationWarning`（如确实需要，下一轮 grill 决定）。

- **`[` 快捷键冲突**：若用户在 input/textarea 中按 `[` 输入字符，必须 e.target tag 检测过滤，否则会被吞。

- **active item 判定与 matchPrefixes 现有约定**：当前 7 shell 的 IconRailGroup `matchPrefixes` 字段已经混乱（OPERATE 组在 alerts/instances-list/instance-detail 中是 `["/admin/notify-history", "/admin/channels"]`，admin-shell 中是 `["/instances"]`）。重构时统一为 4 段固定归属，借此修复 Explore agent P1 #4 报告。

- **chrome="screen" 模式 yagni 风险**：当前 Slice 1.5b 没有 screen 路由消费这个 prop。但 ADR-0016 写明为 Slice 3 铺路，且加这个 prop 的代价是 5 行（条件渲染 sidebar）。判断为可接受。

## Out of Scope

- mobile/tablet drawer overlay（< 768px sidebar hidden 即可，drawer 归 Slice 2/3）
- sidebar 内搜索 / 命令面板入口（命令面板继续走 TopBar）
- sidebar 二级嵌套（instance/[id] 8 tab 仍走 page 内 TabBar）
- hover-flyout 子菜单（ADR-0012 Followup + ADR-0016 双重禁用）
- 用户自定义 sidebar item 顺序（YAGNI）

## Linked

- `docs/adr/0016-sidebar-consolidation.md` — 本任务的设计 ADR
- `.codex-tasks/20260504-slice15b-ui-followup/EPIC.md` — 父 epic
- `.codex-tasks/20260504-slice15b-ui-followup/SUBTASKS.csv` — child #2
- 2026-05-04 grilling 第二轮 Q1-Q5 推荐打包通过（Boss "同意"）
