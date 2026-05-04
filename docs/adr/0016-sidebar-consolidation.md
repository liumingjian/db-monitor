# ADR-0016: Sidebar Consolidation — 修订 ADR-0012 D4 双栏拓扑

Date: 2026-05-04
Status: Accepted（2026-05-04 Slice 1.5b PR β.0 实施完成、机器闸门 + Playwright 头部验证均通过）

## Context

ADR-0012 D4 在 17 轮 `/domain-model` 访谈后锁死 **IconRail 64px + ContextualSidebar 216px 永久展开** 的双栏拓扑。Slice 1.5 验收时按 D4 落地，Slice 1.5b PR α 浏览器侧验证后被 Boss 否决：

1. **视觉冗余**：IconRail 4 大组（OBSERVE/ALERT/OPERATE/ADMIN）与 ContextualSidebar 5 项 flat list 内容大量重叠 — 例如 /overview 上 IconRail Activity 图标 + ContextualSidebar "总览" 行同时存在；BellIcon + "告警" 同样重复。
2. **空间浪费**：1440 宽视口，280px chrome 占 19.4% 横向空间；监控产品的核心是图表/表格，chrome 应让位。
3. **flat-5 实现违反 D4**：overview-shell + rules-shell 把 ContextualSidebar 实现为全局 5 项 flat menu（应为当前 IconRail group 的 children）；这暴露 D4 双栏在工程实现上的歧义。

行业对标（Linear / Datadog / Grafana / GitHub / VS Code / Cursor）均采用单栏可折叠 sidebar。D4 双栏是 grill-me 在缺乏渲染验证下的早期判断，被实际渲染证伪。

本 ADR 修订 D4，**不修订** D1/D2/D3/D5/D6/D7（设计语言、组件栈、i18n、表格三分法、Tier 分层、通用态）。

## Decision

修订 ADR-0012 **D4 仅一项**：双栏拓扑废弃，统一为单栏可折叠 sidebar。

### D4' — 单 Sidebar 拓扑（取代原 IconRail + ContextualSidebar）

**视觉模型 — Grouped Section（保留 D4 4 大组语义）**
- 单 sidebar 默认 240px 宽
- 4 段固定顺序：OBSERVE → ALERT → OPERATE → ADMIN
- 段间 `border-b border-border-hairline` 分隔；展开态显示 section heading（小写、`text-fg-muted`、`text-xs`、`uppercase tracking-wider`）；折叠态 heading 隐藏，分隔保留为更细的 hairline gap
- Item 内布局：`<icon 16> <gap 12> <label>`；折叠态仅渲染 icon，label 由 hover tooltip 给出（不做 hover-flyout 子菜单）

**折叠 / 展开 UX**
- 折叠宽度 64px（与原 IconRail 等宽，避免与 main 内容区横向重排冲突）
- 展开宽度 240px
- 切换入口：sidebar 顶部右上 chevron 图标（`PanelLeftClose` ↔ `PanelLeft`）；快捷键 `[`（不需要修饰键，单键好按）
- 过渡 200ms ease-out（动效遵从 ADR-0012 D2 已有 motion baseline）
- 折叠时 hover 任意 icon 显示 native tooltip（label 内容）；不展开任何 popover/flyout

**持久化**
- `localStorage["ui.sidebar.collapsed"] = "true" | "false"`
- 默认 `false`（首次访问展开），让用户先看到完整层级再决定是否折叠
- 持久化在 client side 即可，不入 SystemSetting（per-user 偏好不进 server）

**Active 高亮**
- 仅当前 item 行：左 2px `border-accent`（cyan）+ `bg-accent/10` 弱填充 + icon `text-accent` 着色
- 不做组级（section）高亮 — 单栏内组级冗余
- Active 判定保持原有 matchPrefixes 机制；新增 children 路由（如 `/instances/[id]/processes`）必须走 page 内 TabBar，不进 sidebar 二级层

**响应式（合理假设，不阻塞 PR β.0 落地）**
- ≥ 1024px：完整行为（默认展开 240，可折叠 64）
- 768-1023px：默认折叠 64
- < 768px：sidebar `hidden`，由 TopBar 上的汉堡按钮控制 overlay drawer（不在 PR β.0 范围；列入 Slice 2/3 backlog）

**Primitive 处置**
- `IconRail` + `ContextualSidebar` 两个 primitive **立即删除**，不留 deprecated alias
- 新建 `Sidebar` primitive（`packages/ui/src/layout/sidebar.tsx`）取代之
- `SidebarItemModel` 复用并扩 `group: "observe" | "alert" | "operate" | "admin"`（必填，断言 4 段归属）
- `AppShell` 接口：删 `iconRail` prop，`sidebar` prop 接收 `Sidebar` 组件实例（类型签名变化必须显式落到接口上）

### 不修订项（守 D1/D2/D3/D5/D6/D7）

- D1 组件与图表栈：shadcn/ui + ECharts 6 不变
- D2 设计语言：dark default + cyan + 4 色严重度轴 + 4/6/8 圆角 不变
- D3 i18n：next-intl + 术语词典 不变；新 `Sidebar` primitive 的 toggle aria-label / tooltip 必须走 `messages/zh-CN.json`
- D5 表格三分法：不变
- D6 Tier 分层：不变；新 sidebar 的 4 大组 = D6 已有的 OBSERVE/ALERT/OPERATE/ADMIN 概念
- D7 通用态：不变；sidebar 折叠状态下的 active item 高亮仍走 D2 accent-cyan token

## Alternatives Considered

| 方案 | 放弃原因 |
|---|---|
| **守 D4 + 加全栏折叠** | IconRail 64 + ContextualSidebar 216 整体折叠到 0 — 不解决"两栏内容重叠"根因，只缓解空间。Boss 截图直击的"两种形式合一"需求未满足。 |
| **flat list 不分组** | Slice 2/3 加 WeCom / SMS / 抑制 / pt-query-digest / Bigtable 等 7+ 占位卡 → sidebar item 总数迅速膨胀至 12+，导航失序。Grouped section 把同质项聚合到 4 大组，可 scale。 |
| **hover-flyout 子菜单** | ADR-0012 Followup 已禁；本 ADR 保留禁用，因为 flyout 在键盘导航 / 触屏 / focus management 上始终是 UX 隐性 trap。tooltip 满足"折叠时仍知道 label"的最小需求。 |
| **Sidebar 永远展开（删 IconRail 不加折叠）** | 节省 40px（280→240），但仍占 16.7% 横向空间；Boss 明确要求"能够折叠和展开"。 |
| **三栏（保留 IconRail + 加可折叠 ContextualSidebar）** | 退步方案 — 折叠后还是有 IconRail 占着；与 Boss "使用一种形式即可" 的指令直接冲突。 |

## Consequences

### 正向
- **空间收益**：折叠态 64px 比原 280px 省 216px（77.1%）；展开态 240px 比原 280px 省 40px（14.3%）
- **视觉冗余消除**：4 大组与 children 不再两栏重复呈现
- **现代单栏 UX 对齐行业**：Linear / Datadog / GitHub / Cursor 共识形态，新用户上手成本更低
- **键盘 / 焦点管理简化**：单栏 tab order 比双栏更直观

### 负向 / 锁定代价
- **7 个 page-local shell 全部重写**：overview/rules/alerts-app/instances-list/instance-detail/notify/admin-shell — 估 2-3 天
- **2 个 primitive 删除 + 1 个新建**：IconRail / ContextualSidebar 立即删；Sidebar 新建（含折叠状态机 + tooltip + persistence + a11y）
- **Playwright 视觉回归 24 基线作废**：归 PR γ 重建（原本就要重建）
- **AppShell 接口 breaking change**：`iconRail` prop 删除；下游消费者只有 7 个 shell，PR β.0 同 PR 内修复
- **Slice 1.5 Q4 + Q17 grill-me 共识被推翻**：本 ADR 在 PR β.0 落地后，原 Q4/Q17 答复失效；新共识以本 ADR 为准

### 路径依赖
- Slice 2 加新页面（WeCom / SMS / 抑制等）必须按 4 大组归属 + 接入 `Sidebar` primitive；不允许新建独立 chrome
- Slice 3 大屏（Screen）作为独立路由，sidebar 应 `hidden`（大屏不需要导航）；`AppShell` 增加 `chrome="full" | "screen"` 模式参数（PR β.0 内顺手加）
- 新页面新增 children 路由必须用 page 内 TabBar，sidebar 永不引入二级嵌套（这是 D4' 的硬约束）

## Enforcement

- `apps/web/` 禁止 import `IconRail` / `ContextualSidebar`（PR β.0 删除后无 export）
- `apps/web/` 必须用 `@db-monitor/ui` 导出的 `Sidebar` 组件包装到 `AppShell.sidebar` prop
- `SidebarItemModel.group` 必填；新增 item 必须显式归属四大组之一，否则 TypeScript 编译失败
- 任何 page 不允许自造 sidebar / 自造折叠 toggle；统一走 `Sidebar` primitive
- ADR-0012 Followup (2026-05-04) 中提到的 "IconRail 64 + ContextualSidebar 216 永久展开拓扑保留" 一句视为被本 ADR 取代；ADR-0012 D4 钉子在 D4' 范围内不再约束工程实现

## Linked

- ADR-0012：UI Redesign（本 ADR 修订其 D4）
- ADR-0012 Followup（2026-05-04）：Slice 1.5b 收尾延展（本 ADR 是该 followup 的 PR β 阶段产出）
- `.codex-tasks/20260504-slice15b-ui-followup/EPIC.md`：Slice 1.5b 收尾延展 epic
- `.codex-tasks/20260504-slice15b-ui-followup/tasks/20260504-pr-beta-0-sidebar-consolidation/`：PR β.0 执行计划（ADR 落地路径）
- Boss grill-me 第二轮（2026-05-04）：Q1-Q5 推荐打包通过 → 本草案
