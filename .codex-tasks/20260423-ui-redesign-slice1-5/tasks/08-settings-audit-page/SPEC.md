# Child #8 — Settings + Audit Page

## Goal

按 Q15 十条规则重写 `apps/web/app/settings/**`（6 分组侧导航）并新建 `apps/web/app/admin/audit/**`（独立 Feed 页 + 4 段 diff drawer），使这两张 Tier 1 页符合 ADR-0012 Canonical page template + 设计系统 tokens + i18n namespace 规范。

## Scope — In

### Settings 页（`/settings`）

1. **布局**：Canonical page template 7 段 + 页面内**左侧二级导航**（6 分组），右侧内容滚动；共用 `AppShell` / `IconRail` / `ContextualSidebar` / `TopBar`。
2. **6 分组**（Q15 规则 1/2/3）：
   - **General**：组织概要 / 当前用户 / 活动 membership / 语言 + 主题偏好（只读展示，写入归 #9 TopBar ThemeToggle）
   - **Data retention**：引用 SystemSetting 中 retention 相关 key（`retention.*`）；只有 admin 可写
   - **Notifications**：SystemSetting 中 `notify.*` key；配合 `#7` 的 Channels 只读视图做入口引导链接
   - **Integrations**：SystemSetting 中 `integration.*` / `webhook.*`；无 key 时显示"尚未配置"引导卡
   - **Advanced**：其余未归类 SystemSetting（按字母序）+ User/Role 管理（admin 专属）
   - **About**：契约版本 / 前端构建 / Slice 标记 / ADR 链接
3. **组件**：`SettingsSideNav` / `SettingsGroupShell` / `SettingsKeyValueForm` / `UserRoleCard` / `SettingsGroupEmpty`
4. **写能力**：复用现有 `updateSettingAction` / `updateUserRolesAction`（来自 `apps/web/src/monitoring-actions`）；admin 不足时显示 Q15 规则 9 的 read-only 提示（`error.notPermitted`）。

### Audit 页（`/admin/audit`）

5. **布局**：Canonical page template + 1 段 EntitySummary + Feed（非分页表格，按 `occurred_at desc` 前 200 条）。
6. **数据源**（真数据前端合成，Q15 规则 5/6）：
   - `listAlerts()` → 每条 alert 的 `acknowledged_at` / `owner_assigned_at` / `resolved_at` / `opened_at` 各生成一条 audit 事件
   - `listSettings()` → 每个 setting 最新 `updated_at` 一条
   - `listNotifyHistory({ limit: 50 })` → 每条 delivery attempt 一条（事件类型 `notify.attempted|delivered|failed`）
7. **4 段 drawer**（Q15 规则 7/8）：
   - Actor：display_name / username / role badges（如属于 current session 则高亮 "you"；否则仅显示 user_id 占位 "—"）
   - Target：事件的主体 entity type + id + label（alert/setting/notify/rule）
   - Before / After diff：以 `<pre>` 展示 JSON key-value 对比；`SystemSetting` 显示 value changed；`alert.status` 显示 status 迁移；`notify_history` 显示 attempt 状态
   - Metadata：occurred_at（绝对时间 + relative tooltip）/ trace_id（如有）/ severity / engine / event type 原始 enum
8. **通用态**（Q15 规则 10）：empty（`empty.noData` + 引导）/ loading（`Skeleton` 行）/ error（inline banner + trace_id）；permission 403 走 `error.notPermitted`。

## Scope — Out

- 写入 Channel / Webhook 配置（归 #7 Channels 页 + Slice 2 PostgresBindingRepository）
- 审计导出 CSV（Slice 2）
- 时间范围 filter / actor filter（Slice 2；占位 disabled chip）
- 新建后端 `/audit` API（本切片不触后端；前端合成真数据）

## Done-When

1. `pnpm --filter web lint` 0 error
2. `pnpm --filter web typecheck` 绿
3. `pnpm --filter web test` 不降级（现状 104 tests）
4. `pnpm --filter web build` 全路由通过（新增 `/admin/audit` Static/Dynamic 路由）
5. 新增 i18n key 仅出现在 `settingsPage.*` 与 `audit.*` namespace，其他 namespace 无改动
6. Settings 6 分组切换可用，空组显示 empty guidance；admin-only 分组在非 admin session 下显示 read-only hint
7. Audit feed 至少显示 1 条真数据（结合 seed 数据）；drawer 4 段完整；diff 渲染 JSON before/after
8. 组件内无 hardcoded hex / 无 bg-white / 无 text-black/ 直接值；统一走 tokens / primitives

## References

- ADR-0012 § D4 / D5 / D7（Canonical page + Feed 三分法 + 通用态）
- SHARED-BRIEF §「写作用域」/「禁止交叉」/「协作约定」
- Domain-model Q15 十条规则
- `apps/web/src/settings-management.ts`（写能力复用）
- `packages/api-client/src/index.ts`（数据源 contract）
