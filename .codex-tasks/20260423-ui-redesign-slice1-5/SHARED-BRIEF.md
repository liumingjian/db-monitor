# Slice 1.5 前端重做 — 共享简报

所有子任务（#1–#9）agent 开工前必读。保持该文件为唯一规则源，避免在每个 child SPEC 里重复。

## 决策来源（不可越权）

1. **ADR-0012**: `docs/adr/0012-ui-redesign-design-system-and-page-architecture.md`（Q1–Q18 全部 18 轮访谈结论）
2. **CONTEXT.md § UI Terms**: 术语表
3. **child #0 已交付的设计系统**（已收官，不准改）:
   - `packages/ui/src/styles/tokens.css` — 所有 CSS vars，禁止硬编码色值
   - `packages/ui/src/primitives/` — 17 个 shadcn 化组件（Button/Input/Dialog/Tabs/…）
   - `packages/ui/src/layout/` — 17 个布局组件（AppShell/IconRail/ContextualSidebar/TopBar/CanonicalPageTemplate/PageBreadcrumb/EntitySummary/QuickMetrics/TabBar/PageContent/…）
   - `packages/ui/src/utils/` — `cn` / `formatBytes` / `formatDuration` / `formatPercent` / `formatRelativeTime` / `formatNumber` / `formatTimestamp` / `useTheme` / `useDensity` / `useAutoRefresh`
4. **Demo 参考**: `apps/web/app/design-demo/page.tsx` 展示如何组合 AppShell + CanonicalPageTemplate + primitives

## 核心设计语言

- 双主题（`<html data-theme="dark" | "light">`），暗色默认，cyan 品牌色（dark: `#3ddcca`, light: `#0f766e`）
- 四色严重度：critical / warning / info / ok，**严禁自造颜色**
- 字体：Noto Sans SC（中文）+ IBM Plex Sans（拉丁）+ JetBrains Mono（数字/代码）
- 数字一律 `tabular-nums`，通过 `font-mono` class 或 token
- 圆角 `--radius-sm|md|lg` = 4|6|8 px
- Border 用 `border-border-hairline`/`subtle`/`strong`，禁止硬编码
- 禁止 spinner，全部骨架屏 `<Skeleton>`

## 写作用域（disjoint，违者 reject）

| 子任务 | 页面根 | components 目录 | 专属 i18n namespace |
|---|---|---|---|
| #1 Login | `apps/web/app/login/` | `apps/web/src/components/login/` | `loginPage.*`（已有 `login.*` 请扩展） |
| #2 Overview | `apps/web/app/overview/` | `apps/web/src/components/overview/` | `overviewPage.*` |
| #3 Instances list | `apps/web/app/instances/page.tsx` + `apps/web/app/instances/_list/` | `apps/web/src/components/instances-list/` | `instancesPage.*` |
| #4 Instance detail | `apps/web/app/instances/[instanceId]/**` | `apps/web/src/components/instance-detail/` | `instanceDetail.*` |
| #5 Alerts | `apps/web/app/alerts/**` | `apps/web/src/components/alerts/` | `alertsPage.*` |
| #6 Rules + Overrides | `apps/web/app/rules/**` | `apps/web/src/components/rules/` | `rulesPage.*` |
| #7 Notify history + Channels | `apps/web/app/admin/notify-history/**` + 新建 `apps/web/app/admin/channels/` | `apps/web/src/components/notify/` | `notifyHistory.*` + `channels.*` |
| #8 Settings + Audit | `apps/web/app/settings/**` + 新建 `apps/web/app/admin/audit/` | `apps/web/src/components/settings-audit/` | `settingsPage.*` + `audit.*` |
| #9 Global framework | `apps/web/src/providers.tsx` + `apps/web/app/layout.tsx` + `packages/ui/src/layout/command-palette.tsx` 等新增 | `apps/web/src/components/shell/` | `commandPalette.*` + `notifications.*` + `oncall.*` |

## 禁止交叉

1. **不准改** `packages/ui/src/primitives/`、`packages/ui/src/layout/app-shell.tsx`、`packages/ui/src/layout/icon-rail.tsx`、`packages/ui/src/layout/contextual-sidebar.tsx`、`packages/ui/src/layout/top-bar.tsx`、`packages/ui/src/layout/canonical-page-template.tsx`、`packages/ui/src/styles/tokens.css` —— 这些是 #0 交付产物
2. **不准改** `apps/web/app/design-demo/page.tsx`
3. **不准改** `apps/web/app/layout.tsx` / `apps/web/src/providers.tsx` —— 归 #9
4. **不准改** `apps/web/messages/zh-CN.json` 里已存在的 `common / severity / nav / topbar / login / loading / empty / error / toast / time` 十个 namespace；如需新增 key，**只追加自己 namespace**
5. **禁止** 在页面里 `new` 出 HTTP client 或直接调后端；统一用 `apps/web/src/data-layer.ts` / `server-api.ts` 已有能力
6. **禁止** 绕过 `packages/ui` 直接写原始 Tailwind 去重实现已有 primitive
7. **禁止** 新建 `@fontsource/*` 以外的字体包

## 协作约定

1. **i18n 策略**（务实）：
   - 页面内中文字符串 **可以硬编码**（与现状一致），但所有新增 parameterized / 用户可见文案 **必须** 进 zh-CN.json 你的 namespace
   - 新增 namespace 时，通过 Edit tool 追加到 JSON 结尾，避免与并行 agent 冲突（先 Read 确认最新状态再 Edit）
2. **data fetching**: Server Components 首选；如必须 client 数据获取，走 `apps/web/src/data-layer.ts` 封装
3. **验证门**（每个子任务必须全绿才能标 DONE）：
   - `pnpm --filter web lint` 无 error
   - `pnpm --filter web typecheck` 无 error
   - `pnpm --filter web test` 不降级（现状 104 tests）
   - `pnpm --filter web build` 全路由通过
4. **禁止** 在 TODO.csv 之外自造文档；所有决策写进 `tasks/<child>/PROGRESS.md`

## 交付契约

每个子任务产出：
- `tasks/<child>/SPEC.md`（目标 + Q-rules 链接 + Done-when）
- `tasks/<child>/TODO.csv`（3–8 行 leaf-level 步骤）
- `tasks/<child>/PROGRESS.md`（recovery + validation 记录）
- 代码：按页面根 + components 目录写作用域落盘
- i18n 追加：只在自己 namespace 下追加，禁止改动他人 namespace
