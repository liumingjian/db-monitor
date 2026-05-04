# Epic — Slice 1.5b: UI Redesign Followup

> Status: **Active**
> Slice: 1.5b（Slice 1.5 收尾延展，不新增 Slice）
> 前置依赖: Slice 1.5 已结但 SUBTASKS.csv #5 (Alerts page) / #10 (E2E + visual + Lighthouse gate) 验收数据有水分
> 后置继任: Slice 2（独立并行，不阻塞）
> 估时: 7-10 天（PR β 拆 β.0 / β.1 后 +2-3 天）
> 决策来源: 2026-05-04 grilling 第一轮（Q1-Q10 全锁定）+ ADR-0012 Followup 段 + 2026-05-04 grilling 第二轮（Q1-Q5 sidebar consolidation 推荐打包通过）+ ADR-0016

## Goal

收尾 Slice 1.5 没扫干净的 UI 残留，并完成 panel 战术延展，使前端达到 ADR-0012 D1-D7
所要求的"客户验收级别视觉标准"。**不破 ADR-0012**，所有动作守 D1-D7 锁定项。

具体目标：

- **风格统一**：`/alerts` 和 `/alerts/[alertId]` 从旧 AppChrome（亮色 marketing-style）迁到 AppShell（深色 ops 方向），
  与其他 8 个 Tier 1 页面对齐
- **panel 战术延展**：聚合页（overview / alerts / rules）走 `section-heading + hairline divider` 模式；
  detail 页（instance/[id]）保留 Card primitive。不压卡片 padding（守 ADR-0012 D4 钉子）
- **审计链合规**：Slice 1.5 SUBTASKS.csv 虚假 DONE 状态修正 + ADR-0012 末尾加 Followup 备注
- **验收门**：视觉回归基准重建 + Lighthouse ≥ 90 + Boss 主观走 9 个改造页面

## Why This Epic Is Next

- **风格分裂是字面意义的**：`apps/web/app/alerts/page.tsx:3` 当前 `import { AppChrome } from "../../src/components/app-chrome"`，
  而其他 8 个 page 走 AppShell。深色 app 上漂浮一个白色 marketing 卡片，是用户打开 `/alerts` 第一眼就看到的不一致
- **Slice 1.5 验收数据有水分**：`.codex-tasks/20260423-ui-redesign-slice1-5/SUBTASKS.csv` #5 / #10
  标 DONE，但代码不在状态。ADR-0012 自己的 Enforcement 写过"占位卡片不允许静默删除"，
  同精神推论：CSV 标 DONE 但代码没收尾也不该静默修
- **panel 卡中卡感**是"前端糟糕"的次要源头：overview 等聚合页每个内容区都裹一层重发明的
  `<section className="rounded-md border bg-bg-base p-4">`，导致整页看起来是"几十个浮动卡片"。
  ADR-0012 D4 钉子限制不能压卡片 padding 减肥，但允许减少 panel 数量

## Scope — In

1. **PR α — alerts chrome 收尾 + 合规承接**（child #1，PR #7 待 Boss 合）
   - 建本 epic（EPIC.md + SUBTASKS.csv）
   - 修正 Slice 1.5 #5 / #10 状态 → IN_PROGRESS
   - ADR-0012 末尾加 `## Followup (2026-05-04)` 段
   - 删 `apps/web/src/components/app-chrome.tsx`
   - 新建 `apps/web/src/components/alerts/alerts-app-shell.tsx`（复制 InstancesListShell 模式，activeGroup="alert"）
   - 改 `apps/web/app/alerts/page.tsx` + `apps/web/app/alerts/[alertId]/page.tsx` 用 AlertsAppShell
   - Tailwind v4 `@source` 声明 `packages/ui` 修复 utility class 缺失
   - 规则 sidebar 图标补 `SlidersHorizontal` + 移除 LifeBuoy 双语义
   - 机器门：lint + typecheck + test + build 全绿
   - 实际耗时 1 天

2. **PR β.0 — sidebar 重做 + AppShell 重构（ADR-0016）**（child #2）
   - 写 `docs/adr/0016-sidebar-consolidation.md`（修订 ADR-0012 D4 仅一项）
   - 新建 `packages/ui/src/layout/sidebar.tsx`（240↔64 折叠 / grouped 4 段 / `[` 快捷键 / `localStorage["ui.sidebar.collapsed"]` / hover tooltip）
   - 删 `packages/ui/src/layout/icon-rail.tsx` + `packages/ui/src/layout/contextual-sidebar.tsx`（primitive + types + index export）
   - `AppShell` 接口 breaking change：删 `iconRail` prop；增加 `chrome="full" | "screen"` 模式参数（screen 模式下 sidebar hidden）
   - `SidebarItemModel.group` 必填字段（"observe" | "alert" | "operate" | "admin"）
   - 7 个 page-local shell 重写：overview / rules / alerts-app / instances-list / instance-detail / notify / admin
   - 机器门：lint + typecheck + test + build 全绿
   - 估时 2-3 天

3. **PR β.1 — overview panel 战术立模板**（child #3）
   - 调 `ui-ux-pro-max` skill 出 3 个 overview layout 候选 + 截图，Boss 拍板
   - 重排 `overview-shell` / `fleet-health-matrix` / `instances-snapshot-table` / `overview-line-chart`
     成 section-heading + hairline divider 模式
   - 不动 Card primitive 本身样式（守 ADR-0012 D4 钉子，密度只控表格行高）
   - 估时 2-3 天

4. **PR γ — 其他 page 批量复制 + 验收**（child #4）
   - instances list / instance/[id] / rules / admin/audit / admin/notify-history /
     admin/channels / settings 7 页复制 overview panel 模板
   - 视觉回归 update-snapshots（24 个 baseline 在新 sidebar 形态 + 新 panel 模板下全部重建）
   - Lighthouse 5 路由 prod build 跑 Perf/A11y/BP ≥ 90
   - Boss 主观走 9 个改造页面拍 OK
   - Slice 1.5 #5 / #10 状态从 IN_PROGRESS 改回 DONE（标 Slice 1.5b 收尾完成）
   - 估时 1.5-2 天

## Scope — Out

- 不破 ADR-0012 D1-D3 / D5-D7（暗色 / cyan accent / 4 色 severity / 4-6-8 圆角 / 字体 / ECharts / shadcn / i18n / 表格三分法 / Tier 分层 / 通用态）
- **D4 单条修订**：通过 ADR-0016 重定义为单 sidebar 拓扑（PR β.0 范围内）；其他 D 项保持锁死
- 不重选 accent color（cyan `#3DDCCA` 保留）
- 不引入新组件库 / 新图表库 / 新 i18n 框架
- 不动 Slice 2 工作（WeCom / SMS / dedup / audit-expansion / signoff），并行不冲突
- 不做 sidebar 二级嵌套（如 instance/[id] 8 tab 仍走 page 内 TabBar，不进 sidebar）
- 不做 hover-flyout 子菜单（保留 ADR-0012 Followup 与 ADR-0016 双重禁用）
- 不做 mobile/tablet 响应式 drawer（< 768px 仅 sidebar hidden，drawer overlay 归 Slice 2/3）

## Risks

- **PR β 调 ui-ux-pro-max skill 输出不收敛**：若 3 个 layout 候选 Boss 都不满意，需要再迭代。
  缓解：限定 skill 输出范围在 ADR-0012 D2 锁死的视觉语言（暗色 + cyan + 4 色 severity + 4-6-8 圆角）
- **PR γ 视觉回归基准重建工作量被低估**：Slice 1.5 #10 备注的 24 个 baseline × 视觉变更 = 全部重建。
  缓解：preflight 跑一次 `pnpm test:e2e:update`，把所有截图差异显式确认后再 commit baseline
- **Lighthouse Perf 退化**：Slice 1.5 #10 备注 Perf=64 是 dev-mode penalty，prod build 应回升。
  本 epic 必须 prod build + next start 再跑 Lighthouse，避免重蹈覆辙
- **PR α/β/γ rebase 互相影响**：选择串行而非并行避免；β 等 α 合后开，γ 等 β 合后开

## Linked

- ADR-0012 (UI redesign design system) — 本 epic 守此 ADR，末尾加 Followup 段
- `.codex-tasks/20260423-ui-redesign-slice1-5/EPIC.md` — Slice 1.5 上游 epic
- `.codex-tasks/20260423-ui-redesign-slice1-5/SUBTASKS.csv` — 本 epic 修正其 #5 / #10 状态
- `.codex-tasks/20260504-slice02-alert-maturity-epic/EPIC.md` — Slice 2 并行 epic（不冲突）
