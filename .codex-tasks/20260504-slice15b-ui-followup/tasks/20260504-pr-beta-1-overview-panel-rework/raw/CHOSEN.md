# CHOSEN — Variant A (Stripe-Dense)

> Boss 决策时间: 2026-05-05
> 决策范围: PR β.1 overview 聚合页 panel 战术立模板

## 选定方案

**Variant A — Stripe-API Dense**

- 段头: 11px 全大写 + 0.10em letter-spacing 小标签（例: `SECTION · TRENDS`）
- 分隔符: **每段头部下方贯通 hairline (`border-bottom`) 全宽**
- 段间节奏: 24px (mt-6)
- 章节内容密度: 高 — 4 列 chart grid (gap-4) / 8 列 fleet grid (gap-2) / 表行 36px
- 章节副信息: 段头同行右侧（"最近 6h · 5min 粒度"）
- 气质: 工程师工具 · 信息密度优先 · "有产品力的扁平"

## 守钉子（ADR-0012）

- D1 暗色基底 ✅ — `--bg-base: #0b0d0f`
- D2 cyan accent ✅ — `--accent: #3DDCCA`
- D3 4 色 severity ✅ — ok/warn/crit/info 四档色板
- D5 4-6-8 圆角 ✅ — sm 4px / md 6px / lg 8px
- D6 字体（type scale）✅ — 11/12/13/14/16/18/22 已对齐
- D7 ECharts / shadcn / i18n / 三分法 / Tier 分层 / 通用态 ✅ — 模板未引入新依赖；表格行高 36px 在三分法允许范围；Card primitive 未被段头复用

## Boss 补充约束（2026-05-05）

### 1. 页面统一使用中文

**评估**: 实际产品 web 端 zh-CN.json 已全部中文（`apps/web/messages/zh-CN.json:42-53`）：
观测/告警/运维/管理/总览/实例/规则/通知投递/通道配置/审计/设置。

mockup HTML 用英文是我手写的设计参考物料，不会上线。重排实际组件时会自动通过
`useTranslations("nav")` 取中文 key — 落地后产品自然全中文。

**结论**: 实际代码无需额外动作；mockup 中英不影响产品。

### 2. 侧边栏一级模块平铺太多 → 增加二级模块

**评估**: 现状 sidebar 已经是两级结构（`packages/ui/src/layout/sidebar.tsx:12, 192-218`）：

- **一级 = 4 个 group**（观测 / 告警 / 运维 / 管理）
- **二级 = 8 个 item**，按 group 分组展示，组头是 11px 大写小标
- 默认全部展开常驻（一级和二级都可见）

Boss 看 Variant-A.png 时直观感受到"一级太多"，原因是**默认所有 8 个二级 item 同时
可见**，视觉上像 8 个并列项，而非 4 + 4。

**判断分支**:

- **A**：Boss 接受现状（一级=4 group / 二级=8 item / 默认全展开）→ 不动 sidebar，保持
  β.1 SPEC Non-goals "不动 sidebar / TopBar"。
- **B**：Boss 要 disclosure 折叠（默认只展示 4 个 group 头部，点击展开本组的二级 item）
  → 改 `packages/ui/src/layout/sidebar.tsx`，新增 collapsed-by-group 状态 +
  localStorage 持久化 + keyboard nav，约 100-200 行。**与 β.1 SPEC Non-goals 直接
  冲突**，应切独立 PR β.1.5（sidebar disclosure），不污染 β.1 overview 焦点。

**默认推进路径**: 守 SPEC Non-goals（分支 A），先把 overview 4 个组件重排做完
（Step 3-6）；步骤 7 双视口走查时把 sidebar 现状截图给 Boss，让 Boss 在视觉
对照下决定要不要切 PR β.1.5 做 disclosure。

**Boss 如要立刻在 β.1 里做（分支 B）**: 打断本 child 任务，先扩 SPEC Non-goals →
in-scope，再续推。

## 后续步骤

按 TODO.csv #3-#9 执行：

3. 重排 `apps/web/src/components/overview/overview-shell.tsx`
4. 重排 `apps/web/src/components/overview/fleet-health-matrix.tsx`
5. 重排 `apps/web/src/components/overview/instances-snapshot-table.tsx`
6. 重排 `apps/web/src/components/overview/overview-line-chart.tsx`
7. 双视口（500×844 + 1440）走查 + before/after 截图
8. workspace 闸门: typecheck + lint + smoke
9. push + PR β.1
