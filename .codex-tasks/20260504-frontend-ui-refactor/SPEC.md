# Frontend UI Refactor (Slice 1.5b follow-up)

## Goal

Close the user-facing gaps identified in the 2026-05-04 UI architecture audit
of the DB Monitor web app. Deliver a single PR scoped to **fix-only**: no new
features, no new pages, no design-system overhaul. Ship the bare minimum that
makes the product (a) not break on common paths, (b) survive a phone, and
(c) read like a finished product instead of an internal sprint demo.

## Source of Findings

`./CLAUDE conversation 2026-05-04`, summarized below by priority. The audit
captured screenshots under `.tmp-uiux/01..11`.

## Scope (in)

### P0 — Blocking

- **P0-1** `/admin/notify-history` 5xx whitescreen falls back to bare Next.js
  error page (no app shell, no nav). Wrap server fetch in try/catch and route
  to `NotifyEmptyState` with retry. Add global `app/error.tsx` +
  `app/global-error.tsx` so any other future failure stays inside AppShell.
- **P0-2** Mobile (≤ md breakpoint): sidebar takes ~50% of viewport, KPI
  values truncate to one char, status pills stack vertical-by-character.
  - `packages/ui/src/layout/sidebar.tsx`: collapse to icon-rail at `<md`,
    add slide-over drawer behavior with hamburger trigger in top bar.
  - `packages/ui/src/layout/app-shell.tsx`: support `flex-col md:flex-row`
    arrangement.
  - `packages/ui/src/layout/quick-metrics.tsx`: `grid-cols-2 md:grid-cols-4
    xl:grid-cols-5` instead of fixed N.

### P1 — Information architecture & consistency

- **P1-3** Breadcrumb is rendered twice (top-bar + every page's
  `EntitySummary`). Remove the in-page copy, keep top-bar as single source.
- **P1-4** "Slice 1.5", "Slice 2", "Slice 1.5 只读视图", "Slice 2 规划"
  internal sprint labels are user-visible. Replace with neutral language in
  `apps/web/messages/zh-CN.json` (e.g. "只读" / "即将上线") — keep dev codes
  inside `<abbr title="…">` only where genuinely useful.
- **P1-5** Sidebar groups (`observe / alert / operate / admin`) and breadcrumb
  roots disagree (e.g. `/admin/channels` is in sidebar group "运维" but its
  breadcrumb root reads "管理"). Centralize the group→root mapping in
  `packages/ui/src/layout/types.ts` and have all pages consume one source.
- **P1-7** `QuickMetrics` value cell does not use `tabular-nums`; numbers jitter
  during refresh. Add the class. Also unify unit placement (compact suffix to
  the right of value, not below).

### P2 — Readability & accessibility

- **P2-9** Instances filter: placeholder used as label. Add visible labels.
- **P2-10** Audit log: ISO timestamps with microseconds. Use `formatRelativeTime`
  + `<time title="…">` for full ISO on hover.
- **P2-11** Login theme-toggle: icon contrast < 2:1 on dark; bump opacity / add
  visible focus ring.
- **P2-12** Top-bar command-palette trigger contrast in light mode; lift
  border to `border-border-strong` in light token.
- **P2-13** Disabled batch-action group on Instances: replace with single
  inline notice + `<details>` overflow, instead of three dead buttons.
- **P2-15** Make clickable cards/rows feedback-visible: add
  `hover:bg-surface-overlay active:scale-[.99]` to FleetHealthMatrix tiles
  and snapshot rows.

## Scope (out — explicitly deferred)

These were called out in the audit but require a design call before code:

- **P1-6 (Overview chart decorative colors)** Removing per-metric color tints
  is a brand decision. Keep current palette in this PR; track in a follow-up.
- **P2-13 (Sidebar follows light theme)** Same — a brand call. Either commit
  to "always-dark sidebar" with an ADR, or recolor; either way it is its own
  PR.
- **P2-16 (Alerts filter density)** UX redesign, separate task.

## Non-goals

- No new pages, no new icons, no font changes.
- No backend changes. P0-1 only adds client-side resilience; the underlying
  notify-history 5xx (if real) is owned by the backend team.
- No test infra changes. Existing vitest/playwright suites must keep passing.

## Assumptions

- Branch `codex/slice15b-pr-beta-0-sidebar-consolidation` is the correct
  base. We extend it with one additional follow-up commit batch.
- Translation file `apps/web/messages/zh-CN.json` is the single i18n source
  for Chinese strings; English fallback file (if any) follows the same keys.
- Tailwind v4 `@source` already covers `packages/ui/src/**` — no build config
  changes needed.

## Validation Strategy

For each step:

1. **Static**: `pnpm typecheck` (must stay green) + `pnpm lint`.
2. **Runtime**: open the affected route in the running dev server at
   `http://localhost:39101/`, login `admin/admin-password`, capture
   before/after screenshot under `.codex-tasks/.../raw/`.
3. **Mobile**: chrome-devtools MCP `resize_page` to 500×844 and re-shoot.
4. **Smoke**: `pnpm smoke:web` at the end of the whole PR, not per step.

If validation cannot be run for a step (e.g. backend currently down), record
`SKIP` in the TODO row's `notes` column with reason.

## Rollback

Each leaf commit is reversible by `git revert`. No DB migration, no contract
change, no schema bump.

## Done Definition

- All in-scope TODO rows are `DONE`.
- `pnpm typecheck && pnpm lint && pnpm smoke:web` all pass.
- Mobile screenshot at 500px shows: sidebar collapsed/drawn, KPI grid not
  truncated, status pills horizontal.
- `/admin/notify-history` shows AppShell + NotifyEmptyState (or table) under
  both happy path and forced-error path.
- No "Slice 1.5"/"Slice 2" string remains in user-facing translation values.
