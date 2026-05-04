# Child #0 — Design System Foundation

## Goal

为 Slice 1.5 UI 重做提供**可 import 的设计系统地基**。子 #0 完成后，其他 9 个子任务（Login/Overview/.../全局框架件）可以直接复用 tokens / 主题切换 / 字体 / 布局 framework / i18n runtime / primitives，不重复造轮子。

## Scope — In

1. **Tokens + Tailwind v4 theme 配置** — 颜色 / 圆角 / 间距 / 字重 / 阴影的 CSS var 全链路
2. **双主题切换** — `data-theme="dark"` / `data-theme="light"`，暗色默认，持久化到 SystemSetting `ui.theme`
3. **字体管线** — HarmonyOS Sans SC（中）+ IBM Plex Sans（西）+ JetBrains Mono NL（mono），Next.js font optimization + preload + swap
   - **Slice 1.5 实际实现**：HarmonyOS Sans SC npm 包不存在（@fontsource 未发布），改用 **Noto Sans SC**（Google Fonts，Apache 2.0，字形/覆盖与 HarmonyOS Sans SC 几乎等价）作为临时替代。JetBrains Mono NL npm 包实际为 `@fontsource/jetbrains-mono`（v5.2.8，无 NL 后缀但是同字形家族）。
   - **Slice 2 跟进**：HarmonyOS Sans SC 走法务授权 / 官方下载 / self-host 三步，落地后替换 Noto Sans SC。
4. **i18n runtime** — `next-intl` 配置 + `messages/zh-CN.json` 骨架 + locale routing
5. **shadcn/ui primitives** — Button / Input / Dialog / Toast / Tooltip / Skeleton / Separator / DropdownMenu / Select / Tabs / Badge / Card / Label / Switch
6. **布局 framework** — AppShell（IconRail 64px + ContextualSidebar 216px + TopBar 56px + Content）+ CanonicalPageTemplate（面包屑 / EntitySummary / QuickMetrics / TabBar / Content）
7. **通用工具** — formatNumber / formatBytes / formatDuration / formatRelativeTime / useTheme / useDensity / useAutoRefresh
8. **Toast + Modal + Skeleton** 原生实现（基于 shadcn 包装，暴露 app-level API）

## Scope — Out

- 具体页面内容（由 #1-#9 子任务做）
- Dark Mode 以外主题扩展（只做 dark + light）
- 任何业务数据接入（本子只做 UI 能力）
- i18n 第二语种（只做 zh-CN，英文 Slice 2 补）

## Done-When

1. `pnpm lint` `pnpm typecheck` `pnpm test` `pnpm build` 全绿
2. 双主题切换可用（浏览器手动验证 + 快照）
3. 三种字体正确加载（DevTools Network 确认 woff2 都 200）
4. 访问任意 demo 路由触发 i18n runtime，`useTranslations()` 返回中文
5. shadcn primitives 14 个组件在 `packages/ui/src/primitives/` 下各有一个可 import 的 export
6. `AppShell` + `CanonicalPageTemplate` 在 demo 路由渲染正常
7. 工具函数 7 个在 `packages/ui/src/utils/` 有 export + 各有至少 1 个 vitest 测试

## References

- ADR-0012: 设计系统 + 页面架构
- CONTEXT.md § UI Terms
- Domain-model Q3 (主题色板) / Q6 (字体 + i18n) / Q7 (Canonical template) / Q16 (通用态)
- ui-ux-pro-max skill: `.claude/skills/ui-ux-pro-max/` (检索监控 / 暗色 / 企业后台最佳实践)
- frontend-design skill: 视觉识别度 / 避免 AI slop
