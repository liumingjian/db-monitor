# Slice 1.5 · Child #6 — Rules + Overrides Page

> 依据：ADR-0012 + SHARED-BRIEF.md + Slice 1.5 EPIC.md · Q11 全部 9 条规则 · ADR-0004（Per-instance threshold overrides 后端依据）

## 目标

用 ADR-0012 设计系统重铺 `/rules` 列表页 + `/rules/[ruleId]` 详情页：
- Catalog 列表：支持 engine / severity / 关键字过滤，批量选择；
- 详情 4 Tab：定义（Definition） / Overrides（Tri-state 继承 segmented） / 通知（Notifications 占位） / 审计历史（Audit Timeline）；
- Overrides 行编辑采用抽屉式 Dialog（非独立路由）；
- Tri-state 继承 = `inherit / override / off` 三段 Button 组合，沿用 ADR-0004 后端契约 (`enabled: boolean | null`, `threshold: number | null`)。

## Q11 九条规则（落地映射）

| # | 规则 | 落点 |
|---|---|---|
| Q11-1 | Rules 走 Catalog 表格（50/页）+ 详情抽屉/页 | `/rules` list 左右 2 栏：Catalog table + Detail panel |
| Q11-2 | 详情 4 Tab（定义/Overrides/通知/审计） | 详情页 `<Tabs>` 四 tab |
| Q11-3 | Overrides 按实例分行、Tri-state 启停 + 阈值覆盖 | Overrides Tab 表格 |
| Q11-4 | Tri-state segmented button `inherit / override / off` | `TriStateControl` = 3 × `<Button>` 组合 |
| Q11-5 | Override 编辑走抽屉式 Dialog，不跳路由 | `EditOverrideDialog` 基于 `<Dialog>` primitive |
| Q11-6 | 审计历史时间线（按时间倒序，过滤 action） | `RuleAuditTimeline` 静态 Feed（后端后续补） |
| Q11-7 | Catalog 批量操作：启停 / 删除 / 导出（Slice 2 后端） | `BatchActionBar` 选中后浮现，当前可启停批量 |
| Q11-8 | 所有颜色走 tokens，严重度走 EntityBadge（`critical/warning`） | 统一 `<EntityBadge>` + `<Badge>` |
| Q11-9 | 空态用 Skeleton + EmptyState，禁 spinner | Skeleton + `EmptyState` 文案 |

**Tri-state 技术壁垒要点**：
- `enabled` 三态存储 `on / inherit / off` → 提交前映射 `true / null / false`（`fromEnabledTriState`）；
- `threshold` 空串 → `null`（继承默认）；
- Dialog 保存前必须 `OverrideValidationError` 拦截重复实例 / 非法 threshold；
- Tri-state segmented 用 **3 个 Button + cn** 组合，不再新增 primitive（遵守禁令）。

## 写作用域

- `apps/web/app/rules/page.tsx`（Server Component，重写）
- `apps/web/app/rules/[ruleId]/page.tsx`（Server Component，重写，作为 detail 4-tab 承载）
- `apps/web/app/rules/[ruleId]/_components/rule-edit-form.tsx`（Client）—— **删除旧实现**，重构成 4 tab 内容
- `apps/web/app/rules/[ruleId]/_components/update-rule-action.ts`（**保留**，仅扩展）
- `apps/web/src/components/rules/**`（新建）
- `apps/web/messages/zh-CN.json` → 追加 `rulesPage.*` namespace
- `.codex-tasks/20260423-ui-redesign-slice1-5/tasks/06-rules-overrides-page/`

## 禁止

- 不动 `packages/ui/src/**`
- Tri-state 不新增 primitive（Button + cn 足够）
- 不碰其他页面/components 目录
- 不改 `AppChrome`（#9 归属）
- 不绕过 `server-api.ts`

## Done-When

1. `/rules`：Catalog 表格 + Engine/Severity/关键字过滤 chips + 批量启停；
2. `/rules/[ruleId]`：EntitySummary header + 4 tab + Overrides Tri-state + Edit Dialog；
3. Tri-state 提交走 existing `buildUpdateRulePayload`（保持后端契约）；
4. `pnpm --filter web lint` 无 error；
5. `pnpm --filter web typecheck` 无 error；
6. `pnpm --filter web test` 不降级（104 tests baseline）；
7. `pnpm --filter web build` 全路由通过；
8. `messages/zh-CN.json` 追加 `rulesPage.*` namespace；
9. 在 PROGRESS.md 记录证据。
