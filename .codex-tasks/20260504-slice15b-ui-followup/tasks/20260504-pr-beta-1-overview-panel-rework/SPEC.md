# PR β.1 — Overview Panel 战术立模板

## Goal

把 overview 聚合页（顶层 dashboard）的视觉模板从当前的"卡中卡 panel"
（`<section className="rounded-md border bg-bg-base p-4">…`）改为
**section-heading + hairline divider** 模板，让聚合页一眼能读到信息层级，
而不是一眼看到一堆漂浮卡片。

本 PR **只动 overview 一页**，作为后续 PR γ 批量复制的"战术立模板"。

## Source / Decisions

- 父 epic：`.codex-tasks/20260504-slice15b-ui-followup/EPIC.md` child #3
- 设计来源：本 PR 启动后调 `ui-ux-pro-max` skill 出 3 个 layout 候选 +
  Boss 拍板（**未启动前不能动代码**）
- 视觉锁定：ADR-0012 D1-D3 / D5-D7（暗色 / cyan accent / 4 色 severity /
  4-6-8 圆角 / 字体 / ECharts / shadcn / i18n / 表格三分法 / Tier 分层 /
  通用态）；D4 通过 ADR-0016 已重定义为单 sidebar 拓扑
- 技术约束：不压卡片 padding（守 ADR-0012 D4 钉子）；不引入新组件库 / 新
  图表库；不动 Card primitive 本身样式

## Scope (in)

**Files** — 仅 overview 一页：

- `apps/web/src/components/overview/overview-shell.tsx`
- `apps/web/src/components/overview/fleet-health-matrix.tsx`
- `apps/web/src/components/overview/instances-snapshot-table.tsx`
- `apps/web/src/components/overview/overview-line-chart.tsx`

**Visual** — section-heading + hairline divider：

- 每个内容段（fleet health / snapshot table / charts）用统一的
  `<SectionHeading>` + `<hr className="border-border-muted" />` 起头
- 移除内容段之间额外的 `rounded-md border` 容器（如有）
- 表格行高与现状一致（密度只在表格三分法允许范围内调，不变 card padding）
- Card primitive 仅在"卡片本身"语义保留（如 KPI grid），不再裹聚合段

## Scope (out — 显式延期 / 不做)

- 其他 7 页（instances list / instance detail / rules / admin/audit /
  admin/notify-history / admin/channels / settings）— PR γ 批量复制
- 视觉回归 baseline 重建（24 基线）— PR γ 末尾统一处理
- Lighthouse prod build ≥ 90 验收 — PR γ 验收
- 重选 accent color（cyan `#3DDCCA` 保留）
- 引入新组件库 / 新图表库
- mobile/tablet 响应式 drawer（< 768px 仅 sidebar hidden，drawer 归 Slice 2/3）
- hover-flyout 子菜单（ADR-0012 Followup + ADR-0016 双重禁用）

## Non-goals

- 不动 KPI grid 的视觉（QuickMetrics 在 PR β.0 已统一过）
- 不改 i18n 字符串
- 不动 sidebar / TopBar
- 不引入新 i18n 框架

## Assumptions

- 当前 main 已含 PR β.0 (`ef75859`) — sidebar 与 AppShell 已统一
- ui-ux-pro-max skill 输出会被限定在 ADR-0012 D2 锁死的视觉语言（暗色 +
  cyan + 4 色 severity + 4-6-8 圆角）
- 视觉回归基线在本 PR **不重建**，预期会失败；标 `expected_failure` 或
  显式 skip，PR γ 末尾统一更新

## Validation Strategy

1. **Static**：`pnpm typecheck` + `pnpm lint` 必须绿
2. **Runtime**：`/` 路由在 `pnpm dev` / `pnpm dev:up` 下能正常渲染，
   核心数据（fleet status / snapshot rows / chart series）不丢
3. **Visual**：本 PR 不重建 baseline，截图对比放在 raw/ 仅做记录
4. **Mobile**：500×844 下 overview 不破布局
5. **Smoke**：`pnpm smoke:web` 末尾全 PR 跑一次

## Rollback

单 PR squash 合并；如出问题 `git revert` 一次性回退。无 schema / contract
变更。

## Done Definition

- ui-ux-pro-max 候选 + Boss 选定方案落档（raw/ 留 PNG / 截图）
- overview 4 个组件按选定方案重排
- `pnpm typecheck && pnpm lint && pnpm smoke:web` 全绿
- Boss 在 dev 环境主观走过 overview 页拍 OK
- 标记 epic SUBTASKS.csv child #3 为 DONE（待 PR 合并后改）
