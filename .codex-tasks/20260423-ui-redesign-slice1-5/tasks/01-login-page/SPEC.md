# Child #1 — Login Page (Slice 1.5 UI 重做)

> 依据: ADR-0012 D2/D7 + CONTEXT.md § UI Terms + SHARED-BRIEF.md
> 前置: child #0 DONE（设计系统、tokens、双主题、primitives、i18n runtime 已落地）
> 写作用域（严格 disjoint）:
> - `apps/web/app/login/page.tsx`
> - `apps/web/src/components/login/**`（新建）
> - `apps/web/messages/zh-CN.json` 仅追加 `loginPage.*` 新 namespace
> - 本任务目录下 SPEC.md / TODO.csv / PROGRESS.md

## 1. 目标

把 `/login` 从「单卡居中英文表单」重做为：**60/40 splitscreen 登录页** —— 左 60 % 品牌叙事（粒子背景 + slogan + 产品价值点），右 40 % 登录表单卡（Username/Password + 行内错误 banner + 骨架屏 loading）。整页双主题自动切换，视觉达到 ADR-0012 所述「第一眼 wow」。

## 2. Q16 十二条规则映射（源: ADR-0012 D7 + CONTEXT.md § UI Terms「Login 页 60/40 splitscreen」+ Slice 1.5 子任务约束）

> 没有独立的 Q16 条目文件，下列 12 条是从 ADR-0012 D7 通用态规范 + Login 专属约束归并而来，每条落地到具体验收点。

| # | 规则 | 本页落地 |
|---|---|---|
| 1 | **Layout 60/40 splitscreen** | 左 60 % 品牌面板（hero slogan + 产品价值点 + 粒子背景），右 40 % 居中登录卡；`<md` 断点退回单列（右侧卡居中） |
| 2 | **Loading = 骨架屏，禁止 spinner** | 表单提交期间用 `<Skeleton>` 覆盖输入/按钮区域（不是 spinning circle） |
| 3 | **错误态三分法**: inline banner (4xx) / 页级兜底 (5xx+网络) / error boundary (client 异常)；**全部显示 trace_id** | 401/422 → inline banner；5xx + 网络 → 页级 error-panel；client 异常 → error boundary fallback；所有 banner 显示 trace_id（若后端返回） |
| 4 | **Empty 三分法** | Login 无列表形态，规则不适用；在 SPEC 记录 N/A |
| 5 | **403 权限页卡** | Login 场景不会命中 403，N/A |
| 6 | **Toast 规则**（4 色 / 3s / 5s error / 无撤销） | 本页不用 toast（成功直接 303 跳转），规则遵守但无实现 |
| 7 | **Confirm Modal 关键字确认** | 本页无危险操作，N/A |
| 8 | **时间相对/绝对** | 本页无时间呈现，N/A |
| 9 | **数字千分位 / 百分比 1 位小数 / 0 与 — 区分** | 本页无数字呈现，N/A |
| 10 | **禁用 spinner / glassmorphism / 3D 插画 / purple gradient** | 粒子背景用 token 四色（accent + info + warning + critical 低饱和）；无玻璃拟物、无 spinner、无 3D、无紫渐变 |
| 11 | **双主题全链路**（暗色默认 + 亮色可切） | ThemeToggle 放在右上；所有颜色走 CSS var；粒子用 `--accent-glow` / `--sev-info-bg` 等 token，自动跟随主题 |
| 12 | **粒子背景 CSS-only** | 纯 CSS `@keyframes` + `radial-gradient` + 多个 `::before/::after` float 层；无 JS、无 canvas |

*规则 4/5/6/7/8/9 在 Login 语义上 N/A，仍记录以证明阅读了规则。*

## 3. 架构设计

```
apps/web/app/login/page.tsx                  Server Component: 会话检查 + 渲染 LoginShell
apps/web/src/components/login/
  login-shell.tsx                            Client "use client": 60/40 布局容器 + ThemeToggle 角
  brand-panel.tsx                            左 60 %：slogan + 价值点 + 粒子背景容器
  particles-background.tsx                   粒子背景 CSS-only：::before/::after 浮动层
  login-form.tsx                             Client: 表单 + inline banner + 骨架屏 loading + trace_id
  login-form.module.css                      （若需 scoped keyframes；优先写进 globals-free 的方式）
  login-error-banner.tsx                     4xx inline / 5xx 页级兜底共用的 banner 组件
```

渲染链：`page.tsx (server, 会话检查)` → `LoginShell (client)` → { `BrandPanel` + `LoginForm` }。
表单提交走现有 `/api/login` server route（**不绕过**）；`<form action="/api/login" method="post">` 的默认浏览器行为在 401/5xx 情况下会 throw，route 返回 4xx/5xx HTTP。我们用 fetch + client 控制以拿到 status & trace_id，失败时展示 banner。

## 4. 数据契约

- POST `/api/login` form fields: `username`, `password`, `next` (hidden, `/overview` default)
- 成功: 303 + Set-Cookie `dbmon_session=…`；浏览器跟随 Location
- 失败: `/api/login` 现实现是 `throw new Error(await response.text())`；页面需要区分 401/422 和 5xx。**不修改** `/api/login`，我们在客户端 fetch 时用 `response.ok` + `response.status` 判断，响应体可含 `trace_id`（后端约定）。

## 5. i18n

只追加 `loginPage.*` 到 `apps/web/messages/zh-CN.json`。新增 keys:

```
loginPage.heroEyebrow            "Slice 1.5 · 企业数据库稳定性"
loginPage.heroTitle              "把数据库告警变成可交付的运维闭环"
loginPage.heroTagline            "观测 / 告警 / 运维 / 审计 四位一体，覆盖 MySQL · Oracle · ClickHouse"
loginPage.valueMonitoring        "实时指标"
loginPage.valueMonitoringDesc    "1s 粒度采集，毫秒级告警"
loginPage.valueAlert             "告警闭环"
loginPage.valueAlertDesc         "规则 / 覆写 / 通道 / 投递 全链路可审计"
loginPage.valueAudit             "合规审计"
loginPage.valueAuditDesc         "操作留痕，可导出，可追溯"
loginPage.formTitle              "登录运维台"
loginPage.formSubtitle           "使用你的账号继续"
loginPage.usernamePlaceholder    "admin"
loginPage.passwordPlaceholder    "输入你的密码"
loginPage.submitting             "正在登录…"
loginPage.errorCredentials       "用户名或密码错误，请重试"
loginPage.errorServer            "服务器暂时无法响应，请稍后再试"
loginPage.errorNetwork           "无法连接后端，请检查网络或联系管理员"
loginPage.errorUnexpected        "发生异常，请复制 trace_id 并联系管理员"
loginPage.traceIdLabel           "trace_id"
loginPage.themeToggleDark        "切换到暗色主题"
loginPage.themeToggleLight       "切换到亮色主题"
```

注：`login.*` 已有的 key（`title/subtitle/username/password/submit/errorInvalid/errorNetwork/forgotPassword`）**不重复定义也不删除**；页面需要时直接使用 `login.*` 即可（SHARED-BRIEF §1 要求不动已存在 namespace 的 key；读取不算修改）。

## 6. Done-When

1. `/login` 渲染为 60/40 splitscreen（桌面 md+）/ 单列栈（`<md`）
2. 粒子背景 100 % CSS-only（无 JS、无 canvas、无 svg 动画）
3. Username/Password 表单用 `@db-monitor/ui` 的 `Input` + `Label` + `Button`
4. 提交中用 `<Skeleton>` 覆盖（无 spinner）
5. 401/422 显示 inline error banner，含 trace_id（若有）
6. 5xx/网络错误显示页级 error panel，含 trace_id（若有）
7. 双主题切换可用，所有颜色走 CSS var，无 hardcoded hex
8. 现有 `tests/login-route.test.ts` 仍全绿（未修改 `/api/login`）
9. `pnpm --filter web lint/typecheck/test/build` 全绿
10. SUBTASKS.csv 第 id=1 行 status→DONE + completed_at=2026-04-23

## 7. 不做

- 不引入第三方粒子库（tsparticles/three.js）
- 不修改 `/api/login` route
- 不修改 `packages/ui/*`
- 不触碰 `login.*` / `common.*` / 任何已有 namespace 的既有 key
- 不引入新字体（沿用 #0 交付的 Noto Sans SC / IBM Plex / JetBrains Mono）
- 不引入新 toast（Login 成功直接 303 跳转）

## 8. 验证门

```
pnpm --filter web lint
pnpm --filter web typecheck
pnpm --filter web test        # 不降级 104 tests
pnpm --filter web build       # 全 14 路由通过
```
