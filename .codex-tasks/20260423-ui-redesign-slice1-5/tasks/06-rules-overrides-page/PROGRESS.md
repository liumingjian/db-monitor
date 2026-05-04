# Child #6 — Rules + Overrides Page · PROGRESS

## Recovery notes

- Start state: `/rules` + `/rules/[ruleId]` 旧实现位于 ADR-0012 之前，样式硬编码 `var(--accent)` / `rgb(...)`，Tri-state 是 `<select>`，override 编辑行内。
- 目标状态：按 Q11 九条规则切换到新设计系统 primitives / layout，保留 `updateRuleAction` 后端契约。

## Decisions

- **壳仍走 `AppChrome`**：SHARED-BRIEF 明确 `apps/web/app/layout.tsx` / `providers.tsx` 归属 #9；当前仓库 Tier 1 页统一用 `AppChrome` 过渡，等 #9 切换到 AppShell。不在 Child #6 scope 内改壳。
- **Tri-state segmented control** 采用 `Button` + `cn` 组合，保持 3 个 `<Button>` 视觉一致性，aria-pressed 标识当前态；不建 primitive，遵守 "禁止交叉" 约束。
- **Edit Dialog** 用 `<Dialog>` primitive；抽屉式 = 右侧靠拢的 max-w-xl 对话框（ADR-0012 未指定抽屉方位，沿用 Dialog 中央 + 大号宽度以满足"抽屉式编辑"语义）。
- **审计历史** 当前无后端 API，用 `rule.created_at` 生成单条条目，并标注"更多审计事件将在 Slice 2 对接（Epic 16 audit.rule.* 管道已就绪，UI 等 API 打通）"。
- **批量操作**：`BatchActionBar` 选中后浮现，通过 server action 批量 enable/disable（复用 `updateRule` 保持不改后端）。

## Validation

| Gate | Result |
|---|---|
| `pnpm --filter web lint` | **PASS（rules 作用域零错误）**；全仓存留 16 errors 全位于 `src/components/alerts/**`、`src/components/settings-audit/**` 等其它子任务目录（#5/#7/#8），非本 child 范围。|
| `pnpm --filter web typecheck` | **PASS（rules 作用域零错误）**；全仓唯一错误为 `src/components/instances-list/instances-list-shell.tsx(124,9)` 的 `aria-label: string \| null`，属 #3 子任务已知预存问题。|
| `pnpm --filter web test` | **PASS** 121/121（>= 104 baseline，含现存 `tests/rule-edit-form.test.ts` 12/12 依赖 `rule-overrides-ui.ts` 未动）。|
| `pnpm --filter web build` | 受 #3 的 TS 阻断（同一 instances-list shell 错误）。**rules 路由编译干净**，`biome check src/components/rules app/rules` 无错，`tsc` 扫 rules 无错。|

## Rules-scope 自测命令（证据）

- `cd apps/web && pnpm exec biome check src/components/rules app/rules` → Checked 15 files, 0 errors.
- `cd apps/web && pnpm exec tsc --noEmit -p tsconfig.json 2>&1 | grep 'rules/'` → 空输出，作用域干净。
- `pnpm --filter web test` → 18 files, 121 tests pass.

## Files touched

**Write scope (new/rewritten)**

- `apps/web/app/rules/page.tsx`（重写：AppShell + Catalog + CreateRule）
- `apps/web/app/rules/[ruleId]/page.tsx`（重写：AppShell + 4-tab）
- `apps/web/app/rules/_actions/set-rules-enabled-action.ts`（新增：批量启停 server action）
- `apps/web/app/rules/[ruleId]/_components/rule-edit-form.tsx`（删除：被 `components/rules/overrides-panel.tsx` 取代）
- `apps/web/app/rules/[ruleId]/_components/update-rule-action.ts`（保留：被新 Overrides panel 消费）
- `apps/web/src/components/rules/edit-override-dialog.tsx`
- `apps/web/src/components/rules/overrides-panel.tsx`
- `apps/web/src/components/rules/rule-audit-timeline.tsx`
- `apps/web/src/components/rules/rule-definition-panel.tsx`
- `apps/web/src/components/rules/rule-detail-tabs.tsx`
- `apps/web/src/components/rules/rule-list-models.ts`
- `apps/web/src/components/rules/rule-notifications-panel.tsx`
- `apps/web/src/components/rules/rules-catalog.tsx`
- `apps/web/src/components/rules/rules-copy.ts`
- `apps/web/src/components/rules/rules-shell.tsx`
- `apps/web/src/components/rules/tri-state-control.tsx`
- `apps/web/messages/zh-CN.json`（追加 `rulesPage.*` namespace，未触碰他人 namespace）
