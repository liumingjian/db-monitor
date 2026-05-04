# Slice 1.5 — 子 #5 Alerts Page SPEC

## 决策来源
- ADR-0012 Q10（共 9 条规则，从 ADR-0012 + CONTEXT.md 抽取）
- ADR-0012 D2（四色严重度）/ D4（Canonical page template）/ D7（Loading/Empty/Error/Time/Number）

## Q10 九条规则对照

1. **Tab 语义四分**：Active / Timeline / Acknowledged / Resolved —— Tab 切换即 status 过滤视图；Timeline 是跨 status 的事件流。
2. **Alert Drawer 五段**：Summary / Timeline / Linked signals / Related alerts / Actions —— 点击一条告警以 Dialog（drawer 变体）呈现，Esc / overlay 关闭。
3. **七枚 Filter Chip**：severity / status / engine / instance / metric / owner / time-window（相对窗口 1h/6h/24h/自定义）—— 点击切换；每个 chip 清空即从 URL searchParams 剔除该键。
4. **On-call 模式 toggle（UI-only）**：TopBar-adjacent；`<Switch>` 控件 + badge。当前 Slice 1.5 子 #5 只渲染按钮与态（localStorage `alerts.oncall` 回显），真正 OS notification + 2h auto-off 归子 #9。
5. **Severity 四色严格映射**：critical→sev-critical / warning→sev-warning / info→sev-info / ok→sev-ok（走 Badge variant，不造色）。
6. **Canonical page template 7 段**：PageBreadcrumb → EntitySummary（Alerts 总量 / 紧急数 / 未确认数 / SLA 破损） → QuickMetrics → TabBar（4 tab）→ PageContent（chips + list）。
7. **通用态**：列表态 `<Skeleton>`（非 spinner）；Empty 三分（首次无告警 / 过滤空 / 业务空）；Error inline banner（server action 失败走 toast 由子 #9，此处仅页级 error boundary）。
8. **Tier 3 "告警抑制 Slice 2" 占位**：右上角灰按钮，标注预计交付窗口（`disabled` + `aria-disabled="true"`），CONTEXT 路径依赖。
9. **时间与数字**：opened_at / acknowledged_at 走 `formatRelativeTime`（<24h 相对 / ≥24h 绝对 mono）；current_value / threshold 走 `tabular-nums`。

## Done-When
- `apps/web/app/alerts/page.tsx` 改造为 Canonical 模板 + 4 tab + 7 chips + on-call toggle + drawer 开启入口；对应 Server Component 继续用 `requireServerSession` + `createServerApiClient`。
- `apps/web/app/alerts/[alertId]/page.tsx` 改造为同 Canonical 模板 + Drawer 5 段；Drawer 内容以 Dialog primitive 渲染。
- `apps/web/src/components/alerts/` 新增 client 子组件：`alert-tab-bar.tsx` / `alert-filter-chips.tsx` / `alert-oncall-toggle.tsx` / `alert-list.tsx` / `alert-drawer.tsx`（+ 段子组件）。
- `apps/web/messages/zh-CN.json` 追加 `alertsPage.*` namespace。
- 不动 `packages/ui/src`、`apps/web/app/layout.tsx`、`apps/web/src/providers.tsx`、他人 i18n namespace。
- `pnpm --filter web lint` / `typecheck` / `test`（104 tests 不降级）/ `build` 全绿。
