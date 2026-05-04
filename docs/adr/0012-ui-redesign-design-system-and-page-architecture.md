# ADR-0012: UI Redesign — Design System and Page Architecture

Date: 2026-04-22
Status: Accepted (via domain-model interview, Boss approved Q1–Q17 with `A`, Q18 vote `A/A`)

## Context

Slice 1 在 2026-04-22 进入投产前的最后窗口，Playwright E2E + 专业 UI 架构师复盘给现有前端打了 **70/100**：视觉识别尚可，但数据可视化、状态色轴、占位文案、页面架构都撑不起客户验收。Boss 明确要求：
1. 必须覆盖 legacy `lepus-v3.8` 的 UI 功能面（实例维度的深度诊断能力是最大差距）。
2. 必须达到"企业后台最佳实践"视觉标准，第一眼决定验收满意度。
3. UI 是 **交付给客户验收** 的产品正面，不是内部工具。

17 轮 `/domain-model` 访谈锁定了设计系统、导航、页面模板、表格范式、10 张 Tier 1 页的具体规格与跨页通用态。

## Decision

**本 ADR 锁死下列技术与设计选型**，Slice 1.5（UI 重做窗口）必须整体执行，不做局部替换：

### D1 — 组件与图表栈
- **组件库**：`shadcn/ui`（Radix primitives + Tailwind）+ 自有 Tailwind tokens。
- **图表库**：`ECharts 6`（已在 package.json，尚未使用）。
- **废弃**：Ant Design Pro / 纯自造 / 停留在"打磨现有"。

### D2 — 设计语言
- **主题**：双主题 dual-theme，**暗色默认**（`#0B0D12 / #13161D / #1C2029`），亮色可切（顶 bar toggle，持久化到 SystemSetting `ui.theme`）。
- **品牌色**：cyan `#3DDCCA`（唯一强调色）。
- **四色严重度轴**：紧急 `#FF5A67` / 警告 `#FFB547` / 提示 `#5EA8FF` / 健康 `#3DDCCA`。
- **圆角**：4/6/8 三档。
- **禁用**：purple gradient on white、glassmorphism、3D 插画、spinning circle loading。
- **字体**：
  - Display + Body：`HarmonyOS Sans SC`（中）+ `IBM Plex Sans`（英西文）。
  - Mono（数字/SQL/ID）：`JetBrains Mono NL`。
  - 避开 Inter / Roboto / Arial / system 默认。

### D3 — i18n 与术语
- **默认中文**（`zh-CN`），`next-intl` 驱动。
- **术语词典**（混合策略，避免生硬翻译）：
  - 英文保留：`Processlist` / `Webhook` / `HMAC` / `Throttle` / `Backpressure`
  - 中文化：告警严重度（紧急 / 警告 / 提示）、操作动词（确认 / 指派 / 备注）、组织角色
  - 数据库专有名词保持英文大小写（MySQL / Oracle / ClickHouse）

### D4 — 导航与布局
- **Icon Rail**（左侧 64px 窄栏，4 个图标组）：`OBSERVE / ALERT / OPERATE / ADMIN`。
- **上下文侧栏**（Icon Rail 点击后二级展开 216px）。
- **Top bar**：面包屑 + `⌘K` 命令面板入口 + 主题 toggle + 通知铃铛 + 当前用户。
- **Canonical page template**（7 段式）：面包屑 40px / entity summary 88px / quick metrics 64px / tab bar 44px / content / (page footer optional) / (FAB disabled)。
- **密度控制**：只作用于表格行高（紧凑/舒适 二档），不影响图表与卡片。

### D5 — 表格数据形态（三分法）
- **Catalog**：分页，50/页（Instances / Rules / 参数列表 / 用户 / SystemSetting）。
- **Feed**：游标分页（Audit / Notify history）。
- **Snapshot**：页面级刷新，不分页（Processlist / Tablespace），带 diff-refresh 保留滚动 + 高亮变化。

### D6 — Tier 分层与占位策略
- **Tier 1**（必须做，Slice 1.5 范围）：Login / Overview / Instances 列表 / Instance Detail / Alerts / Rules+Overrides / Notify history / Channels / Settings / Audit。10 张。
- **Tier 2**：label 体系替代原 `machine_room + application` 二元组。
- **Tier 3**（占位卡片）：Screen 大屏 / pt-query-digest / Bigtable / Binlog / SQLServer / OS / Redis / 报表邮件 / WeCom / 告警抑制。每张卡必须标 Slice + 预计交付窗口。
- **Tier 4**（全局框架件）：健康指示器 / ⌘K 命令面板 / Notification 抽屉 / on-call 模式。

### D7 — 通用态规范
- **Loading**：骨架屏 Skeleton（非 spinner）。
- **Empty**：三分法（首次配置 / 过滤空 / 业务空），各有引导文案与插画。
- **Error**：inline banner (4xx) / 页级兜底 (5xx+网络) / error boundary (client 异常)；全部显示 trace_id。
- **Permission (403)**：页级卡片 `权限不足，请联系管理员`；侧边栏入口提前过滤。
- **Toast**：4 色 + 右上堆叠 + 3s 自动（error 5s）+ 不提供"撤销"。
- **Confirm Modal**：危险操作强制输入关键字启用按钮（Kill / Delete）；禁止弹窗叠加。
- **时间**：`<24h 相对时间` / `≥24h 绝对时间 mono`，hover 互换。
- **数字**：千分位；百分比 1 位小数；字节 SI（KB/MB/GB）；耗时量级自适应。`0` 与 `—` 严格区分。

## Alternatives Considered

| 方案 | 放弃原因 |
|---|---|
| **Ant Design Pro / Arco Design Pro** | "中后台默认感"过强，客户验收第一眼就会认出来，失去差异化；色板/字体难深度定制。 |
| **纯自造组件库** | 工期爆炸，Slice 1.5 无法闭环；可访问性 / 键盘交互 / 焦点管理要自己重写 Radix 已经做过的事。 |
| **只打磨现有 UI** | Q1 Boss 已裁决"Polish Current"只作为兜底底线；70 分版本的结构问题（导航、数据可视化、占位文案）靠打磨无法跨越。 |
| **Recharts / Visx 替代 ECharts** | ECharts 的热力图 / 拓扑图 / sparkline / 大数据量折线性能在监控场景明显更强；已装未用。 |
| **仅英文 UI** | 客户验收人群母语中文；中文术语比翻译软件输出的英文更自然。 |
| **亮色默认** | 监控场景多在值班室 / 夜班 / 大屏，暗色是行业共识（Grafana / Datadog / Linear）。 |

## Consequences

### 正向
- **客户验收差异化**：视觉识别度显著高于"通用中后台"；第一眼即可与 Grafana / Lepus 区分。
- **设计一致性**：Canonical page template + 表格三分法 + 通用态规范让新页面开发成本下降 60%+。
- **国际化铺路**：`next-intl` runtime 装上后 Slice 2/3 加多语言是配置级改动。
- **暗色主题 = 值班场景首选**：减少值班室屏幕干扰。

### 负向 / 锁定代价
- **图表库锁死 ECharts**：迁到 Recharts/Visx 需要重写所有图表组件（预计 2 人周）。
- **主题切换必须 CSS variable 全链路**：Tailwind tokens 通过 CSS var 暴露，组件内不得 hardcode 颜色。
- **i18n 必须从零抽取**：所有硬编码中文字符串需要进入 `messages/zh-CN.json`，无法增量迁移。
- **字体加载影响首屏**：HarmonyOS Sans SC + IBM Plex + JetBrains Mono 约 500KB，要配合 `font-display: swap` + Next.js font optimization。
- **Slice 1.5 工期**：3-5 周（依 subagent 并行度），Slice 2 启动需要等 UI 地基完成（`子 0` 子任务）。

### 路径依赖（将影响未来 ADR）
- Slice 2 后端新增通道（WeCom / SMS）UI 直接走已定义的 Channels 页范式。
- Slice 2 `PostgresBindingRepository` 实现后，Notify Channels 页从只读转写入，不需要重新设计。
- Slice 3 告警抑制 / 静音 / 升级 功能 → 已为其在 Alerts 页预留 `告警抑制 (Slice 2)` 灰按钮占位。

## Enforcement

- `apps/web/` 禁止在组件中出现 hardcoded hex 色；必须引用 Tailwind token 或 CSS var。
- `apps/web/` 禁止在组件中出现未进入 `messages/zh-CN.json` 的中文硬编码字符串。
- Playwright E2E 覆盖必须从当前 11/12 提升到 12/12 + 视觉回归快照 + Lighthouse > 90。
- 任何新页必须遵循 Canonical page template；偏离需写子 ADR 说明。
- Tier 3 占位卡片上线后，若对应功能落地必须同步替换占位卡片；**不允许**占位卡片静默删除。

## Followup (2026-05-04)

> Status: Slice 1.5b 收尾延展，**不修订 D1-D7 锁定项**。

Slice 1.5 验收数据复盘发现两条残留：

1. `apps/web/app/alerts/page.tsx` 与 `apps/web/app/alerts/[alertId]/page.tsx` 仍 import 旧
   `apps/web/src/components/app-chrome.tsx`（亮色 marketing-style），与其他 8 个 Tier 1 页面
   走 AppShell 的暗色 ops 方向不一致。`SUBTASKS.csv #5` 标 DONE 与代码状态不符，已改回
   `IN_PROGRESS` 并在 notes 备注 followup 指针。
2. `SUBTASKS.csv #10` Lighthouse Perf=64 备注是 dev-mode penalty，prod build + next start
   尚未重跑。视觉回归 24 个基线在 alerts 迁移 + panel 重排后将作废，需 update-snapshots 重建。

本 followup 在守 ADR-0012 D1-D7 的前提下补足上述残留，并对 D4 / D7 做 **不修订** 的延展约束：

- **D4 不修订**：IconRail 64 + ContextualSidebar 216 永久展开拓扑保留，`/alerts` 走 AppShell
  与其他页一致；不引入"按需展开 / hover-flyout / 单 sidebar"等会破 D4 的 chrome 改造
- **D4 钉子（密度只控表格行高，不影响图表与卡片）保留**：聚合页 panel 重排只允许通过
  **减少 panel 数量**（去除重发明的 `<section className="rounded-md border bg-bg-base p-4">`
  自造卡片，改用 `<header>` + `border-b border-border-hairline` 的 section-heading + hairline
  divider 模式）实现密度收口；**不允许**压 Card primitive 的 padding / radius / shadow
- **D7 不修订**：loading skeleton / empty 三分法 / error 三层 / toast 4 色 / Confirm Modal /
  时间数字格式照旧
- **聚合页 vs 详情页战术分流**（D4 内允许的细化）：聚合页（overview / alerts / rules / admin/audit /
  admin/notify-history）走 section-heading + hairline；详情页（instance/[id]、settings 子页）
  保留 Card primitive 帮助分隔信息流

执行切片：

- **PR α**：alerts chrome 收尾 + 合规承接（删 app-chrome.tsx + alerts 两页迁 AppShell + 修正
  SUBTASKS.csv 状态 + 本 Followup 段）
- **PR β**：overview panel 战术立模板（调 ui-ux-pro-max skill 出 layout 候选 + Boss 拍板 +
  fleet-health-matrix / instances-snapshot-table / overview-line-chart 重排）
- **PR γ**：其他 page 批量复制 + 视觉回归 update-snapshots + Lighthouse prod build ≥ 90 +
  Boss 走查 9 页

详见 `.codex-tasks/20260504-slice15b-ui-followup/EPIC.md`。

## Linked

- `/domain-model` 访谈记录 Q1–Q18（访谈原文保留在 `.claude/projects/*` session 中）。
- `.codex-tasks/20260423-ui-redesign-slice1-5/EPIC.md`（执行计划）。
- `.codex-tasks/20260504-slice15b-ui-followup/EPIC.md`（Slice 1.5b 收尾延展）。
- ADR-0006：Runtime action permission（Kill 按钮权限门槛来源）。
- ADR-0004：Per-instance threshold overrides（Rules 页 Tri-state 继承态的后端依据）。
- Epic 16 HANDOFF：`/admin/notify-history` UI 规格（Q14）的后端依据。
