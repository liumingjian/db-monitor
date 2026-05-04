# db-monitor UI Redesign Slice 1.5 — Current State Inventory

## 1. Route Inventory

**All routes Server Components** (no `use client` in page.tsx; 3 uses found in child components only).

| Route | URL | Page Type | E2E Covered |
|-------|-----|-----------|-------------|
| Home | `/` | Server (redirect → `/overview`) | No |
| Login | `/login` | Server Component | Yes (step 1-2) |
| Overview | `/overview` | Server Component | Yes (step 8) |
| Instances List | `/instances` | Server Component | Yes (step 7 start) |
| Instance Detail | `/instances/[instanceId]` | Server Component | Yes (step 7 detail) |
| Alerts List | `/alerts` | Server Component | Yes (step 4) |
| Alert Detail | `/alerts/[alertId]` | Server Component | No |
| Rules List | `/rules` | Server Component | Yes (step 5) |
| Rule Edit | `/rules/[ruleId]` | Server Component | No |
| Settings | `/settings` | Server Component | Yes (step 9) |
| Slow Queries | `/instances/[instanceId]/slow-queries` | Server Component | No |
| Processes | `/instances/[instanceId]/processes` | Server Component | No |
| Tablespaces | `/instances/[instanceId]/tablespaces` | Server Component | No |
| Tablespace Trend | `/instances/[instanceId]/tablespaces/[tablespaceName]/trend` | Server Component | No |
| Notify History | `/admin/notify-history` | Server Component | Yes (step 6, Epic 16 new) |

**Child Components used**: `AppChrome` in most pages; `AnalyticsPresetNav`, `MetricChart`, `TimeWindowNav` in analytics pages; `AlertTriagePanel`, `kill-process-dialog`, various form components in detail pages.

## 2. Layout & Providers Structure

**`app/layout.tsx`**:
- Imports fonts: `@fontsource/ibm-plex-sans` (Latin 400/500/600) + `@fontsource-variable/bricolage-grotesque` (Variable)
- Wraps children with `<ShellProviders>` (from `src/providers.tsx`)
- No explicit theme provider; style driven by CSS variables in `globals.css`
- Lang: `"en"` (hardcoded, not i18n-aware)

**`src/providers.tsx`**:
- `ShellProviders` wraps React Query `QueryClientProvider`
- Single provider: `@tanstack/react-query` (v5.99.2)
- `createShellQueryClient()` from `data-layer.ts` manages caching

**`src/components/app-chrome.tsx`**:
- Main layout shell: left sidebar (nav items) + main content area
- Uses `buildWebShellModel()` from `app-shell.ts` to render shell structure
- Hardcoded CSS variables (`--surface`, `--panel`, `--ink`, `--muted`, `--accent`)
- No theme toggle implemented yet

**Second layout file**: `app/instances/[instanceId]/layout.tsx` (nested, purpose unclear from brief check).

## 3. Shared UI Code Locations

**`apps/web/src/` modules**:
- `monitoring-ui.ts` (37KB): Main UI model builder — alert/instance/rule filters, instance capability boundary, chart frames, form field contracts
- `monitoring-actions.ts` (5KB): Server actions for create instance, manage rules
- `monitoring-preview.ts` (15KB): Mock data for Storybook / preview
- `processlist-ui.ts` (6KB): Process filtering, table rendering logic
- `slow-queries-ui.ts` (6KB): Slow query table & sparkline rendering
- `tablespaces-ui.ts` (3KB): Tablespace bar/trend chart rendering
- `rule-overrides-ui.ts` (4KB): Rule override tri-state logic
- `auth.ts` (1.5KB): Session resolution, membership checks
- `server-api.ts` (2.4KB): API client factory, session guards
- `analytics-presets.ts` (1.8KB): Time window & metric preset definitions
- `settings-management.ts` (965B): System setting CRUD helpers
- `data-layer.ts` (2.1KB): React Query client config
- `app-shell.ts` (2.8KB): Shell navigation & panel models

**`apps/web/src/components/` (6 components)**:
- `app-chrome.tsx` — Main layout wrapper
- `alert-triage-panel.tsx` — Alert detail right panel
- `metric-chart.tsx` — ECharts wrapper for analytics
- `instance-tab-nav.tsx` — Tab switcher for instance sections
- `analytics-preset-nav.tsx` — Time window & preset selector
- `time-window-nav.tsx` — Time range picker

**`packages/ui/src/index.ts` (227 lines only)**:
- Exports form field, table column, chart frame contracts
- Constants: `SHELL_NAVIGATION`, `LOGIN_FORM_FIELDS`, `INSTANCE_FORM_FIELDS`, `RULE_OPERATORS`, `RULE_SEVERITIES`, `OVERVIEW_CHART_FRAME`, etc.
- Zero React components — pure TypeScript contracts + export lists
- Version locked: `UI_FOUNDATION_VERSION = "0.2.0"`

## 4. Tailwind v4 Configuration

**Tailwind v4 setup**:
- `tailwindcss` v4.2.2 + `@tailwindcss/postcss` v4.2.2 installed
- **No `tailwind.config.ts`** found (Tailwind v4 uses `@import "tailwindcss"` in CSS)
- **Global CSS**: `app/globals.css` with `@import "tailwindcss"` at top
- **CSS Variables defined** in `:root` — `--surface`, `--panel`, `--panel-strong`, `--ink`, `--muted`, `--accent`
- **Color scheme**: Light theme only (no dark mode CSS variables)
- **PostCSS**: v8.5.10 installed; no explicit `postcss.config.js` visible (likely using Tailwind's defaults)

**Current design tokens** (from globals.css):
- Surface: `#f3efe7` (warm cream)
- Panel: `#f7f4ee` (lighter cream)
- Ink: `#172033` (dark blue-gray)
- Muted: `#5c6577` (gray)
- Accent: `#c25b2e` (warm burnt orange)

## 5. Dependency Inventory

**In use**:
- ECharts v6.0.0: **2 imports found** (`src/components/metric-chart.tsx`)
- @tanstack/react-query v5.99.2: **2 imports found** (`src/providers.tsx`, `src/data-layer.ts`)
- @db-monitor/ui (workspace): **5+ imports** (navigation, form contracts, severity enums)

**Not yet installed (per ADR-0012 requirements)**:
- `next-intl` — i18n runtime (ADR mandates for zh-CN default)
- `class-variance-authority` — component styling utility
- `clsx` — classname merging
- `tailwind-merge` — Tailwind conflict resolution
- `lucide-react` — Icon library (ADR requires icons for OBSERVE/ALERT/OPERATE/ADMIN rail)
- `@fontsource/jetbrains-mono-nl` — Mono font for code/IDs (ADR requires JetBrains Mono NL)
- `@fontsource/harmonyos-sans-sc` — CJK display font (ADR requires HarmonyOS Sans SC)
- `shadcn/ui` — Component library (ADR mandates for Radix + Tailwind integration)

## 6. Hard-Coded Chinese Text

**Count**: ~89 occurrences total (`53 in /app/`, `36 in /src/`)

**Sample of first 10**:
1. `/rules/page.tsx`: "编辑"
2. `/rules/[ruleId]/page.tsx`: "← 返回规则列表"
3. `/rules/[ruleId]/page.tsx`: "编辑规则："
4. `/rules/[ruleId]/page.tsx`: "默认阈值"
5. `/rules/[ruleId]/page.tsx`: "已保存覆盖配置"
6. `/rules/[ruleId]/_components/update-rule-action.ts`: "缺少 rule_id"
7. `/rules/[ruleId]/_components/update-rule-action.ts`: "override 行未选择实例"
8. `/rules/[ruleId]/_components/update-rule-action.ts`: "保存失败：未知错误"
9. `/rules/[ruleId]/_components/rule-edit-form.tsx`: "按实例覆盖"
10. `/rules/[ruleId]/_components/rule-edit-form.tsx`: "+ 添加覆盖"

**Scale**: Distributed across rules, instance detail, process/slow-query/tablespace UIs; requires bulk i18n extraction into `messages/zh-CN.json`.

## 7. Type & Test Coverage

**tsconfig.json (root)**:
- `target: "ES2022"` — Modern JavaScript
- `strict: true` — Full type checking enabled
- `moduleResolution: "NodeNext"` — ESM-first
- No path aliases configured (no baseUrl)

**tests/** directory**: 15 test files
- `alerts.test.ts`, `auth.test.ts`, `dashboard.test.ts`, `data-layer.test.ts`
- `instances.test.ts`, `login-route.test.ts`, `presets.test.ts`
- `processlist-ui.test.ts`, `rule-edit-form.test.ts`, `settings-management.test.ts`
- `shell.test.ts`, `slow-queries-ui.test.ts`, `tablespaces-ui.test.ts`
- `time-window.test.ts`, `smoke.test.ts`

**vitest.config.ts**:
- Environment: `"node"` (not jsdom; suitable for server-side logic)
- Include: `tests/**/*.test.ts`
- Default resolveConditions: `["browser", "module"]`

## 8. Risk & Backward-Compatibility Constraints

**Must preserve**:
- Login form selectors: `input[name="username"]`, `input#username`, `input[name="password"]`, `input#password`, `button[type="submit"]` — Playwright E2E depends on these (step 1-2)
- API endpoint `/api/login` (form action target)
- Route URLs (all 14 routes tested or expected): `/login`, `/overview`, `/instances`, `/instances/[id]`, `/alerts`, `/rules`, `/settings`, `/admin/notify-history`
- Session flow: `fetchServerSession()` guard for auth-protected routes
- `@db-monitor/ui` contract exports (form fields, table columns, navigation items, operators/severities)

**Can refactor**:
- Inline CSS variable hardcodes → replace with Tailwind tokens from v4 config
- `Bricolage Grotesque` font → replace with `HarmonyOS Sans SC` (display) per ADR
- Color scheme from light-only → dual-theme dark-first (requires CSS variable expansion)
- Page chrome layout from fixed `lg:grid-cols-[260px_1fr]` → Icon Rail (64px) + Sidebar (216px) per ADR
- Mock data in `monitoring-preview.ts` → can refactor for Storybook once design system live
- ECharts integration (only 1 component, low coupling) — chart config safe to redesign

**Can discard** (low/zero impact):
- Current `.playwright-e2e/run.mjs` screenshot folder (./screenshots) if output location changes
- `monitoring-preview.ts` hardcoded PREVIEW_* objects once Storybook established
- Obsolete font imports if HarmonyOS Sans SC migration approved

