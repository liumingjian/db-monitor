# PROGRESS — PR β.1 Overview Panel Rework

## Recovery Block

- 任务: Overview 聚合页 panel 战术立模板（section-heading + hairline divider）
- 形态: single-full（epic `20260504-slice15b-ui-followup` child #3）
- 进度: 8/9
- 当前: Step 9 — 提交 + push + 开 PR β.1，等 Boss 授权 push
- 文件: 新增 packages/ui/src/layout/section-heading.tsx + 导出；改 4 个 overview 组件 + page.tsx + zh-CN.json + smoke/phase-one.spec.ts（中文 login）
- 下一步: 等 Boss 授权后 commit + push branch + `gh pr create` 开 PR β.1（base=main）

## 前置条件（已满足）

- PR β.0 (`ef75859`) 已合并到 main：sidebar + AppShell 已统一
- ADR-0016 Accepted：单 sidebar 拓扑落地
- 工作分支 `codex/slice15b-pr-beta-1-overview-panel-rework` 已建（base=main）

## 视觉锁定（不可破）

- ADR-0012 D1（暗色基底）/ D2（cyan accent `#3DDCCA`）/ D3（4 色 severity）
- ADR-0012 D5（4-6-8 圆角）/ D6（字体）/ D7（ECharts / shadcn / i18n / 三分法 / Tier 分层 / 通用态）
- ADR-0012 D4 经 ADR-0016 重定义为单 sidebar 拓扑

## Out of Scope（其它页 / 验收门）

- 7 页批量复制 → PR γ
- 24 个视觉回归 baseline 重建 → PR γ
- Lighthouse prod build ≥ 90 → PR γ

## Log

(append entries with timestamp + step id + outcome below)

- 2026-05-04T(开启) — epic SUBTASKS.csv child #1/#2 → DONE，child #3 → IN_PROGRESS；本 child 任务三件套 (SPEC.md / TODO.csv / PROGRESS.md) 落盘；工作分支 `codex/slice15b-pr-beta-1-overview-panel-rework` 创建 (base=main, 含 PR β.0 squash `ef75859`)
- 2026-05-04T(Step 1) — DONE。调 ui-ux-pro-max skill (style/chart/ux 三 domain 检索) 收集 Data-Dense Dashboard / Swiss Modernism 2.0 / Stripe-style 信息密度参考；产出 3 个 1440x900 完整 overview mockup（sidebar + topbar + EntitySummary + KPI strip + TabBar + 8 charts + 24 fleet cells + 6 snapshot rows）：Variant-A (Stripe-Dense / 全宽 hairline / 24px 节奏)、Variant-B (GitHub-Neutral / H3+段尾 hairline / 32px 节奏)、Variant-C (Linear-Spacious / 无分隔线 / 64px 节奏)。raw/ 下 3 HTML + 3 PNG fullPage + 1 对比表 CANDIDATES.md。等 Boss 拍板 raw/CHOSEN.md。
- 2026-05-05T(Step 2) — DONE。Boss 选定 Variant A (Stripe-Dense)。两条补充约束已澄清：(a) 实际产品 zh-CN.json 已全中文，mockup 英文是设计稿不上线，重排时 i18n 自动取中文 key，无需额外动作；(b) sidebar 现状已是两级（一级=4 group / 二级=8 item / 默认全展开），Boss 看 mockup 觉得"一级平铺太多"实际是看到二级 item 同时展开。disclosure 折叠如要做 → 切独立 PR β.1.5（与本 SPEC Non-goals "不动 sidebar" 直接冲突）。默认守 Non-goals，Step 7 双视口走查时把 sidebar 现状截图给 Boss 决定是否切 PR β.1.5。raw/CHOSEN.md 落档。
- 2026-05-05T(Step 3-6) — DONE。新增 `packages/ui/src/layout/section-heading.tsx`（label / description / endSlot / 段头底部 hairline）+ 在 layout/index.ts 导出。重排 fleet-health-matrix.tsx（去外层 rounded-md border bg-bg-base p-4，用 SectionHeading；LegendRow 走 endSlot）+ instances-snapshot-table.tsx（同样去 panel，keyMetricLabel 走 endSlot）+ overview-line-chart.tsx（chart cell 保留 panel 作为数据卡，padding p-4→px-3.5 py-3 紧凑化，bg-bg-base→bg-bg-elevated 区分页面背景层次）+ page.tsx ChartGrid（包 SectionHeading "运营指标 · 8 项指标 · 最近 {window} · {bucket} 粒度"）。i18n 中文化残留：fleetMatrixTitle "Fleet Health Matrix"→"实例健康矩阵"；8 个 chartXxx 全部改中文（连接数 / 运行中线程 / QPS / 入流量 / 出流量 / 缓冲池读取 / 复制延迟 / 运行时长）；新增 chartsSectionLabel + chartsSectionDescription。验证：`pnpm --filter web typecheck` 全绿。overview-shell.tsx 本身无 panel 改动（CanonicalPageTemplate 提供页面 24px gap，已对齐 Variant-A 节奏）。
- 2026-05-05T(Step 7) — DONE。chrome-devtools MCP 走 admin 登录后双视口截图：1440 桌面 fullPage（1430x1190）+ 500x844 mobile fullPage（500x3107，hide 掉 mobile drawer 后）落 raw/after-desktop.png + raw/after-mobile.png。修了一个 dev-server stale CSS bug（重启 pm2 web 让 Tailwind v4 重扫 packages/ui/sidebar.tsx 的 md:flex），fullPage 截图改用 `evaluate_script` 临时把 main 的 overflow:hidden + h-dvh 改 visible+auto 让全部段落入帧。Mobile 上 EntitySummary badges + KPI grid 窄柱子排版是已有 mobile 问题（不是 β.1 引入），超 SPEC Non-goals "mobile/tablet 响应式 drawer"，留给 Slice 2/3。
- 2026-05-05T(Step 8) — DONE。Workspace 闸门：`pnpm typecheck` 全绿（packages/api-client + packages/ui + apps/web 三段）；`pnpm lint` 全绿（biome 216 文件 0 fix）；`pnpm smoke:web` 部分通过：login（中文选择子 `用户名` / `密码` / `登录`）+ /overview "机群总览" heading + canvas 全绿，fail 在 line 20 `/instances/inst-prod-primary` canvas 的 `toBeVisible()`。该回归源自 PR β.0 (`ef75859`) 对 `instance-detail-shell.tsx` 的改动（`git log --all -- apps/web/src/components/instance-detail/instance-detail-shell.tsx` 显示 ef75859 是该文件最后一次 commit；β.1 working-tree diff 对 `apps/web/app/instances/` 与 `apps/web/src/components/instance-detail/` 全空），SPEC Non-goals 已把"7 页批量复制"划入 PR γ scope，因此本 PR 不修。Smoke 中 login 段也同步 Chinese-ize 了 selector（β.0 漏改）。
- 2026-05-05T(Step 8 → 9 衔接) — 等 Boss 授权后 commit + push + open PR β.1。涉及 9 个 modified + 1 个 new 文件 + raw/ 工件目录。Auto Mode 5b 规定 push remote 是 shared-system 改动需要明确确认。
