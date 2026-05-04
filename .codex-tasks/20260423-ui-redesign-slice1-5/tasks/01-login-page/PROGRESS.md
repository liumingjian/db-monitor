# Child #1 Progress — Login Page

## Recovery Notes

- 依赖: child #0 DONE。复用 `@db-monitor/ui` 的 `Input / Label / Button / Skeleton / ThemeToggle`。
- 写作用域: `apps/web/app/login/page.tsx`、`apps/web/src/components/login/**`、`loginPage.*` namespace 追加。
- 禁区: 不改 `packages/ui/*`、不改 `apps/web/app/layout.tsx`、不改 `apps/web/src/providers.tsx`、不改 `/api/login`、不动 `login.*` 等已存在的 10 个 namespace。
- 现有登录路径: browser POST `/api/login`（Node route）→ 303 redirect 到 `next`，失败时 throw。新 UI 用 `fetch` 以便拿 status + trace_id 展示 inline banner / 页级 panel。
- `/login` 页在未登录时由 `middleware` 透传；已登录自动 redirect 到 `/overview`（`page.tsx` 内 `fetchServerSession`）。
- 现有测试: `tests/login-route.test.ts` 测 route 行为；新增 UI 只做 server component + client 组件组合，不新增单元测试（避免改变 test 总数 104 之前还是之后取决于 #0 现状——目标是 **不降级**）。

## Decisions

1. **CSS-only 粒子实现**: 用一个 `<div>` 容器，内部放 3 个无 children 的 `<span>` 点位，配合 `login.module.css` 里的 `@keyframes` + `radial-gradient` + `filter: blur()`。这样 keyframes 仅本页生效，不污染全局。
2. **错误态细分**:
   - HTTP 401/422: `inline-banner` 紧贴在表单标题下
   - HTTP 5xx 或 fetch network throw: 用「页级」banner 替换整张表单卡中部（仍保持左侧 BrandPanel），含「重试」按钮 & trace_id
   - React render 异常: 用 React 19 `<ErrorBoundary>` 即 Next.js `error.tsx`。本次不新增 `app/login/error.tsx`（避免扩大 scope）；依赖 Next.js 默认 error boundary。
3. **trace_id 来源**: `/api/login` 现实现把后端响应直接 `throw new Error(await response.text())`，route 外层会 500。我们在客户端 fetch 时看到 `!response.ok` 就读 json body 里的 `trace_id` 字段（若存在）；若不存在就不展示 label 行。
4. **布局断点**: `md` (≥ 768px) 起用 60/40；以下单列。
5. **`login.*` 已有 keys 不触碰**: 新文案全部进 `loginPage.*`。

## Validation

执行时间: 2026-04-23

### 作用域内验证（我的文件 7 个：`app/login/page.tsx` + `src/components/login/**` + `messages/zh-CN.json`）

- **lint (scope)**: `biome check app/login src/components/login messages/zh-CN.json` → **PASS**（`Checked 7 files, No fixes applied`）
- **typecheck**: `pnpm --filter web typecheck` → **PASS**（EXIT=0，无错误）
- **test**: `pnpm --filter web test` → **PASS**（16 文件 / 104 测试全绿，不降级）

### 全局门（跨 agent 管道）

- **全局 lint**: `pnpm --filter web lint` → **FAIL**
  - 根因：其他并行 agent 作用域（`src/components/alerts/**`、`src/components/overview/**`、`src/components/rules/**`、`src/components/instances-list/**` 等）存在 9 处 format / a11y / useExhaustiveDependencies 错误
  - 我的文件：零错误
  - 处置：按 SHARED-BRIEF「disjoint 写作用域，违者 reject」，**不越界**修其他 agent 文件
- **全局 build**: `pnpm --filter web build` → **FAIL**
  - 根因：`src/components/rules/rules-catalog.tsx:10` import `formatTimestamp` 但 `@db-monitor/ui` 未导出此符号（child #0 交付 `packages/ui/src/utils/format.ts` 无 formatTimestamp；SHARED-BRIEF §3 utils 清单列了 formatTimestamp，属文档 vs 代码契约不一致）
  - 我的文件：`page.tsx` + `components/login/**` 全部 compile 通过（Next.js "Compiled successfully in 2.5s"），类型检查二阶段才在 rules 文件触发 fail
  - 处置：同上，不越界

### 结论

本子任务（Login page）的代码交付闭环完成；自身作用域 4 门验证全绿。全局 lint / build 两门因其他并行 agent 的已知遗留问题**仍红**，按 SHARED-BRIEF 不应由本 agent 修复。

依据 SHARED-BRIEF §3「四门全绿才能标 DONE」，**不自动**把 SUBTASKS.csv row id=1 标为 DONE；本 PROGRESS.md 完整记录现状与根因，请 Boss 仲裁：
1. 选项 A：允许本子任务在「作用域内 4 门绿」下标 DONE，登记 blocker = {alerts/overview/rules/instances-list 管道红 + ui 包 formatTimestamp 未导出}
2. 选项 B：等并行 agent 全部 DONE + #0 追加 formatTimestamp 后再跑一次全局四门；本子任务保持 PENDING

