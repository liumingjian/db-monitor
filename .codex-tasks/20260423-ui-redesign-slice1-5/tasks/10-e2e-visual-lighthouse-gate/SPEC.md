# Child #10 — E2E + 视觉回归 + Lighthouse 最终闸门

## 目标（三件套）

1. **Playwright E2E**：≥ 12 条规格，覆盖 Slice 1.5 所有 Tier 1 页和 #9 全局框架件
2. **视觉回归快照**：dark + light × 12 条关键页 = 24 张 `toHaveScreenshot()` 基线，存 `apps/web/tests-e2e/__screenshots__/`
3. **Lighthouse**：5 个 Tier 1 路由（/overview, /instances, /alerts, /rules, /settings）Perf / A11y / BestPractices ≥ 90，结果存 `raw/lighthouse/<route>.json`

## 环境前提（entry gate）

- 真实后端 + 真实 web 已在跑（不 mock）：
  - `apps/api` 监听 `http://127.0.0.1:8000`
  - `apps/web` 监听 `http://127.0.0.1:3000`
- Admin 账号 `admin / admin-password` 可登录（通过 `DB_MONITOR_E2E_USERNAME` / `DB_MONITOR_E2E_PASSWORD` 覆盖）
- 测试发现后端实例/告警/规则表都可能为空；spec 内做「有数据断数据、无数据断空态」分叉，不伪造数据
- Playwright 已装（root devDep `@playwright/test ^1.55.0`）；Lighthouse 通过 `npx lighthouse` 调用（全局包，无 pnpm devDep 依赖，避开 workspace pollution）

## 12 条规格清单（最低覆盖）

| # | 规格文件 | 断言 |
|---|---|---|
| 01 | `login.spec.ts` | 登录页 60/40 splitscreen 渲染；admin/admin-password 登录成功跳转 /overview；错误凭证 401 inline banner + `errorCredentials` 文案；可选 trace_id 行存在；服务端 5xx 场景通过构造错误 URL 或已知 bad-password 触发 inline 错误（真 5xx 需 backend 停机，跳过） |
| 02 | `overview.spec.ts` | 登录态下 /overview 渲染 CanonicalPageTemplate；8 个 chart 插槽（有数据 ≥ 1 canvas，无数据 `chartEmpty` 空态）；1 张 InstancesSnapshotTable（heading `tableTitle`）；Fleet Health Matrix heading 可见；时间窗切换 1h → 24h URL 变化 |
| 03 | `instances-list.spec.ts` | /instances 渲染；双视图 segmented（table/grid）切换 → URL `view=` 变化；sparkline 三选一 → URL `spark=` 变化；filter chip 表单存在；点击 `createCta` 打开新建抽屉（Dialog role=dialog + `createTitle`）；revalidate 按钮存在（数据空时可忽略） |
| 04 | `instance-detail.spec.ts` | 当 `DB_MONITOR_E2E_INSTANCE_ID` 可用（或 /instances 列表首行命中）则进详情页；8 个 tab 链接（概览/性能/会话/SQL/存储/复制/配置/审计）逐个跳转；点击 processes tab，若有 Kill 按钮存在则 fill 错的 confirm → 提交按钮 `disabled`，fill 正确 thread_id → 启用；若 processes 为空断空态（不跳过） |
| 05 | `alerts.spec.ts` | /alerts 渲染；4 tab 链接 active/timeline/acknowledged/resolved 可切换（URL `tab=`）；filter chips 存在；若有告警行则点击第一行打开 Drawer 并断 URL `/alerts/<id>?...` 保留 filters，返回 /alerts；若无告警断空态 |
| 06 | `rules.spec.ts` | /rules 渲染 catalog；若 catalog 有行则点击进详情，断 TriState segmented（aria-pressed）可切换；若无行断空态 CTA；主页「Create rule」表单 heading 存在 |
| 07 | `notify-channels.spec.ts` | /admin/notify-history 渲染 Feed + 空态断言；/admin/channels 顶部只读 banner 出现；若 feed 有行则点击进 6 段 drawer 并验证 drawer 标题存在 |
| 08 | `settings-audit.spec.ts` | /settings 渲染 6 分组 sideNav（General/Retention/Notifications/Integrations/Advanced/About），逐个点击切换 active；/admin/audit 渲染 Feed + 空态或行 |
| 09 | `command-palette.spec.ts` | 从 /overview 按 Meta+K 或 Control+K 打开 Dialog；ArrowDown 改变 `aria-selected`；Esc 关闭（Dialog 卸载） |
| 10 | `notification-drawer.spec.ts` | 点击 top-bar 通知铃铛按钮 → Drawer 打开；3 tab（alerts/notify/system）；Esc 或 close 按钮关闭 |
| 11 | `oncall-persistence.spec.ts` | /alerts 打开，toggle on-call → localStorage `alerts.oncall` = `"on"`；导航 /overview 后回 /alerts，toggle 状态保持；toggle off → localStorage = `"off"` |
| 12 | `theme-toggle.spec.ts` | /overview 点 top-bar 主题按钮 → `<html data-theme>` 由 dark → light；localStorage `db-monitor:ui-theme` = `"light"`；刷新后保持；再切回 dark |

额外：`visual.spec.ts` 集中跑 24 张 toHaveScreenshot（12 路由 × 2 主题），与上面 12 条业务断言解耦。

## Tier 3 占位的明确断言策略

ADR-0012 规定 Tier 3 功能以 **占位卡片 / disabled 按钮** 铺开，不得被误判为 bug。E2E 对这些元素的断言：

- **Instances list 的 edit / delete / 批量启停按钮**（`aria-label="tier3EditLabel"` 等）：断言 `isDisabled()=true`，点击后 URL 不变、无 dialog 弹出、无请求（不跳过、正向断言）
- **Alerts 告警抑制**：disabled 按钮存在且带 Slice 2 文案
- **Channels 写能力**：顶部只读 banner 存在且文案包含 "只读"/Slice 2
- **Instance detail 复制 tab + 配置 tab**：TabBar link 可跳，目标页渲染 Tier3PlaceholderCard（heading 存在，不是 404）
- **Rules 审计抑制 / 批量操作**：页面无此按钮或 disabled 状态

这样 Tier 3 不会被 "缺 feature" 误读，而是被显式 pin 住「这是故意占位」。

## 写作用域（disjoint）

允许新建/修改：
- `apps/web/playwright.config.ts`
- `apps/web/tests-e2e/**`（新目录）
- `apps/web/tests-e2e/__screenshots__/**`（首跑生成）
- `apps/web/package.json`（新增 `test:e2e` / `test:e2e:update` / `lighthouse:ci` scripts）
- 根 `package.json`（如需 devDep 补丁——优先避免）
- `.codex-tasks/20260423-ui-redesign-slice1-5/tasks/10-e2e-visual-lighthouse-gate/**`

禁止修改：
- Slice 1.5 子 #1-#9 任何页面 / component / primitive / layout
- `apps/api/**` 后端
- `packages/ui/**` / `packages/api-client/**`
- 既有 `smoke/phase-one.spec.ts` 和 `playwright.smoke.config.ts`（那是 Epic 15 的 release smoke，不归本切片）

## Lighthouse 策略

- 使用 `npx lighthouse <url> --output=json --output-path=... --chrome-flags="--headless --no-sandbox" --only-categories=performance,accessibility,best-practices --preset=desktop`
- 5 个路由 = 5 份 JSON 结果
- 门槛：Performance ≥ 90、Accessibility ≥ 90、Best Practices ≥ 90（SEO 不要求）
- 若某路由不达标：**不修其他 agent 代码**，把数值 + 首 3 条 audit 建议列入 PROGRESS.md 「遗留风险」章，标为 Slice 2 回填
- 登录态：Lighthouse 运行时无 session cookie，走 redirect → /login，因此只对 `/login` 做全三项评估；其他 4 路由在「首屏即 login redirect 页面」下评估——这与 Slice 1.5 的 UI 一致（redirect 前会渲染 /login）。若想带 session 跑 Lighthouse，需要 `lhci` + Puppeteer fixture，Slice 2 补。
  - 本切片实现：对 5 路由分别跑 `npx lighthouse <url>` 得 JSON；结果即便是 redirect 到 login 的 perf 分，也是真实数据，不伪造。

## Done-When

1. `pnpm --filter web test:e2e` 全绿（允许 flaky retry 1 次）
2. `apps/web/tests-e2e/__screenshots__/` 含 ≥ 24 张 PNG 基线（dark + light × 12 条路由）
3. `raw/lighthouse/*.json` 5 份结果，PROGRESS.md 记录每路由 Perf/A11y/BP 分数
4. `pnpm --filter web lint && typecheck && test && build` 仍全绿（新增 e2e 文件过 biome）
5. `SUBTASKS.csv` id=10 → DONE + completed_at=2026-04-23
6. 父 PROGRESS.md 追加 Slice 1.5 收官 validation 段

## Q 规则对照

- Q16 rule 3（错误态）：Login 规格命中 `errorCredentials` + trace_id
- Q9 / Q10 / Q11 / Q12 / Q13 / Q14 / Q15 / Q16 / Q17：对应 12 条 specs 一一覆盖

## 遗留风险（声明）

1. **后端实例表空**：E2E 数据驱动断言用「if-有数据」分叉；不伪造数据
2. **视觉快照漂移**：首次生成 baseline，后续跑可能因字体回落 / 时钟刷新抖动；设置 `maxDiffPixelRatio: 0.02` + `animations: "disabled"` 缓解
3. **Lighthouse 无 session**：5 路由除 /login 外都会跳转 login，perf 分是 redirect+login 页的，符合实际首屏感受
4. **Kill 二次确认**：依赖 processlist 有行；无行时断空态（Tier3 不达）
