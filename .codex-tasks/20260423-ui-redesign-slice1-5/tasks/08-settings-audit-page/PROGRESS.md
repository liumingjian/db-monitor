# Progress — Child #8 Settings + Audit Page

## Summary

- 任务形态: single-full
- Goal: 按 Q15 十条规则重写 `/settings`（6 分组侧导航）+ 新建 `/admin/audit`（Feed + 4 段 diff drawer）
- 上游: ADR-0012 Canonical page template + SHARED-BRIEF 协作约定 + Q15 规则

## Recovery

- 任务: Slice 1.5 子 #8 Settings + Audit
- 形态: single-full
- 进度: 6/6 DONE
- 当前: 全 Step 收官；SUBTASKS.csv id=8 已标 DONE
- 文件:
  - `apps/web/app/settings/page.tsx`
  - `apps/web/app/admin/audit/page.tsx`
  - `apps/web/src/components/settings-audit/*` （10 个文件，含 2 模型）
  - `apps/web/messages/zh-CN.json` → 追加 `settingsPage.*` + `audit.*`
  - `.codex-tasks/20260423-ui-redesign-slice1-5/tasks/08-settings-audit-page/`（SPEC / TODO / PROGRESS）

## Architecture decisions

1. **Audit 数据源**：后端未提供全局 `/audit` API（Slice 1 Out of scope），前端 Server Component 合成 `AuditEvent[]`，来源 = `listAlerts`（opened/ack/owner/resolved 四事件） + `listSettings`（updated_at） + `listNotifyHistory`（delivered/failed/skipped）。不造假 API。
2. **写能力复用**：`/settings` 复用 `updateSettingAction` / `updateUserRolesAction`，不新建 server action。
3. **布局**：两张页都用 `AppShell` + `CanonicalPageTemplate`（Slice 1.5 设计系统）。AdminShell 声明为 client 组件以满足 TopBar `onCommandOpen` required callback 契约；⌘K 实现归 #9。旧 `AppChrome` 保留（仍被 /overview 等未重做页面使用），不拆。
4. **Settings 分组策略**：按 key 前缀分片（`retention.*` / `notify.|notification.*` / `integration.|webhook.*` / `ui.|locale.*` → General / 其余 → Advanced），About 为静态页（契约版本 + ADR 链接）。
5. **权限**：admin-only 分组在非 admin session 渲染 read-only hint；非 admin 仍可读 `/admin/audit`（可见性由后端接口鉴权决定）。

## Validation (2026-04-23)

- `pnpm exec biome check src/components/settings-audit app/settings app/admin/audit`：12 files 0 error（biome --write 应用了 organizeImports + 格式化）
- `pnpm exec tsc --noEmit` 作用域内：0 error
- `pnpm --filter web test`：19 files / 127 tests 全绿（>104 基线，不降级）
- **全仓 build 阻塞**：`apps/web/src/components/instances-list/instances-list-shell.tsx:124:9` TS2322（`aria-label: string | null` 不兼容 `undefined`）。该文件归 child #3 写作用域，非本子任务引入。与 SUBTASKS.csv 记录的子 #2 / #6 同模式：交 #10 epic gate 统一解决。

## 关键偏差记录

1. **i18n 并行冲突重试**：第一次 Edit 因另一并行 agent 正在加 rulesPage 导致字符串未命中；Read → Edit 定位到新 tail (channels) 后追加；重跑 JSON.parse 通过。
2. **无 /audit 后端 API**：Slice 1 不开 audit API，采用前端合成策略，把现有数据源（alerts/settings/notify）统一进 AuditEvent shape，满足 Q15 规则 5/6。
3. **build 跨任务阻塞**：全仓 build 受并行子 #3 `instances-list-shell.tsx` TS error 阻塞；作用域内 lint / typecheck / test 全绿；按 SHARED-BRIEF 禁止跨作用域，没有私自去修 #3 的代码。
