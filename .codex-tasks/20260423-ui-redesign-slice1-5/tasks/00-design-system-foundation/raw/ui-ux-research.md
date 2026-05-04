# UI/UX Research - db-monitor Redesign (Slice 1)

Source: `ui-ux-pro-max` skill CSV DB (v2.5.0). Baseline: ADR-0012 locked. Below补细节，不推翻。

## 1. 产品类型建议（查询 #1: product / monitoring dashboard, n=3）
三条命中均指向 dashboard 类产品：Smart Home/IoT、Analytics、Financial Dashboard。共同推荐：
- **主样式**：Dark Mode (OLED) + Data-Dense；次样式：Minimalism、Heat Map、Accessible & Ethical。
- **Dashboard 模式**：Real-Time Monitoring（IoT）+ Drill-Down Analytics + Comparative（Analytics）。
- **色板焦点**：Dark bg + status indicators（red/green/amber）+ trust blue。
- **启示**：db-monitor 应同时覆盖 "Real-Time Monitoring"（Q9 Overview 实时指标）+ "Drill-Down Analytics"（Q8 表格下钻）双模式；严重度色轴与 Financial Dashboard "red/green alerts + trust blue" 同构，印证 ADR-0012 四色轴方向正确。

## 2. 暗色企业后台样式（查询 #2: style / dark theme enterprise, n=5）
命中 5 条：Dark Mode (OLED)、Modern Dark (Cinema Mobile)、Cyberpunk UI、Enterprise SaaS (Mobile, 浅色)、Neumorphism。与 ADR-0012 最相关的是 #1 OLED 和 #2 Modern Dark。

**与 ADR-0012 对照**：
- 一致：暗色优先、高对比、status-driven accent、--bg 分层（deep/base/elevated 对应 #0B0D12 / #13161D / #1C2029）、hairline border `rgba(255,255,255,0.08)`、`color-scheme: dark`、WCAG AA+。
- 可吸收的新信息：
  - **避免纯 `#000000`**（OLED smear + 过度刺眼）——ADR-0012 的 #0B0D12 正确，#1 OLED 的 #000000 建议不采纳。
  - **cubic-bezier(0.16, 1, 0.3, 1)** 作为全局 easing（Expo.out）。
  - **Accent 辉光**：`--accent-glow: rgba(61,220,202,0.20)`（把 ADR-0012 的 #3DDCCA 套进 Modern Dark 的 glow pattern）。
  - **Border token**：`--border: rgba(255,255,255,0.08)` hairline，用于卡片/分隔，替代实色边框。
  - **Surface 透明层**：`--surface: rgba(255,255,255,0.05)` 用于 elevated card overlay。
  - 不采纳：Cyberpunk 的 scanlines/glitch（与企业严肃度冲突）；Cinema 的 BlurView 大面积 glassmorphism（会牺牲数据密度可读性）。

## 3. 字体配对建议（查询 #3: typography / technical dashboard, n=3）
命中：Dashboard Data (Fira Code + Fira Sans)、Brutalist Raw (Space Mono ×2)、**Developer Mono (JetBrains Mono + IBM Plex Sans)**。

**与 ADR-0012 对照**：ADR-0012 选定 HarmonyOS Sans SC（中文）+ IBM Plex Sans（西文）+ JetBrains Mono NL（代码/数值）。**Result 3 Developer Mono 完全印证**西文 + mono 配对——权威数据库推荐 JetBrains Mono + IBM Plex Sans 用于 developer tools / documentation / code editors，与 db-monitor 场景吻合，**无冲突**。

**可吸收的新细节**：
- CSS 权重范围：IBM Plex Sans 300/400/500/600/700；JetBrains Mono 400/500/600/700。
- Tailwind fontFamily token：`mono: ['JetBrains Mono NL', 'JetBrains Mono', 'monospace']`、`sans: ['HarmonyOS Sans SC', 'IBM Plex Sans', 'sans-serif']`（HarmonyOS 在前，西文回退 IBM Plex）。
- 表格数值列显式 `font-variant-numeric: tabular-nums`（来自 Dashboard Data 的 "Code for data, Sans for labels" 分工）。

## 4. 色板（查询 #4: color / dark dashboard, n=5）
5 条 Dashboard 色板中 4 条为暗色：Financial (#020617 bg / #0F172A primary)、Smart Home/IoT (#0F172A bg)、Podcast (#0F0F23 bg)、Music (#0F0F23 bg)。

**与 ADR-0012 色板对照**：
| Token | ADR-0012 | 外部建议 | 结论 |
|---|---|---|---|
| bg deep | #0B0D12 | #020617 / #0F172A / #0F0F23 | ADR-0012 略深于 IoT，比 Financial 浅——合理中间位，不改 |
| bg surface | #13161D | #0E1223 / #1B2336 / #1B1B30 | 同区间 |
| bg elevated | #1C2029 | #1A1E2F / #272F42 / #27273B | 同区间 |
| accent | #3DDCCA（品牌 teal） | #22C55E (green) / #F97316 (orange) | 外部多用 green=positive；ADR-0012 teal 作为 brand 且复用为"正常/在线"，与严重度四色轴的 #3DDCCA 同色需在 UI 上做语义分离（brand 高亮 vs severity OK），建议把 severity OK 保留 teal，brand 点缀只用于 logo / primary CTA |
| destructive | #FF5A67 | #EF4444 / #DC2626 | ADR-0012 略偏橙红（更醒目），保留 |
| muted fg | — | #94A3B8 | 可吸收为 `--fg-muted: #94A3B8` |
| border | — | #334155 / #475569 | 与 Modern Dark 的 `rgba(255,255,255,0.08)` 二选一；推荐 rgba 方案（更符合暗色分层） |

**新补充值**（不改 ADR-0012 锁定值，只补空白位）：
- `--fg-primary: #F8FAFC`、`--fg-muted: #94A3B8`、`--on-accent: #0B0D12`、`--ring: #3DDCCA` 用于 focus outline。

## 5. 图表类型推荐（查询 #5: chart / time series monitoring, n=5）
5 条全部高度相关：Anomaly Detection、Trend Over Time、Real-Time Streaming、Time-Series Forecast、Stock OHLC。

**对 Q9 Overview 8 chart 方案的启发**：
- **Trend Over Time → Line / Area Chart**（QPS、连接数、TPS 历史趋势）：<1000 pts 用 SVG；≥1000 pts 用 Canvas + 降采样；>10000 聚合到时间桶。ECharts 符合。
- **Real-Time Streaming → Streaming Area**（实时指标）：buffer 最近 60–300s；**必须**提供 pause/resume 控件；current value 单独以大号 KPI 文本呈现；遵守 `prefers-reduced-motion`。这是**新约束**，要加入 Q9 交互规范。
- **Anomaly Detection → Line + Highlights**（慢查询 spike、错误率突刺）：正常线 + 异常点用 shape marker（非仅颜色区分）+ 文本 annotation；推荐与告警 badge 联动。
- **Time-Series Forecast → Line + Confidence Band**（容量预测，如果 Slice 涉及）：历史 30–90 天，预测 ≤30% 可视区间，实线 + 虚线 + 15% 透明 band。
- **Stock OHLC**：与 db-monitor 无关，**不采纳**。
- **库推荐交叉**：D3/Plotly/ApexCharts/Chart.js/Recharts 被多次提及，**ECharts 未出现**。ADR-0012 已锁 ECharts，不改；但需在实现时自检 ECharts 能覆盖 streaming + anomaly + confidence band 三种形态（ECharts `dataZoom` + `markPoint` + `markArea` 能胜任）。

**颜色规范（来自 chart CSV）**：
- Trend primary: `#0080FF`；多系列用 solid/dashed/dotted 线型区分，不仅靠颜色。
- Anomaly marker: red filled circle + 告警带 `#FFF3CD` 背景 zone（暗色下需反相为 `rgba(255,181,71,0.15)`）。
- Streaming pulse: 暗色下 `#00FF00`——**不采纳**，应用 ADR-0012 的 `#3DDCCA`（品牌 + OK severity）。
- Forecast：实线 #0080FF + 虚线 #FF9500 + 15% 同色填充。

**可访问性硬约束（写入 Q9 规范）**：
- 颜色+线型双通道（color-blind safe）。
- 可切换数据表（togglable data table with timestamps and values）。
- Streaming 图必须 pause 按钮 + KPI 大字 + reduced-motion 冻结。

## 6. 表格 UX 最佳实践（查询 #6: ux / data density tables, n=3 返回）
3 条命中（其中第 3 条 "Auto-Play Video" 与表格无关，剔除）：
- **Table Handling (Responsive, Medium)**：窄视口用 horizontal scroll 或 card layout；`overflow-x-auto` wrapper；禁止表格撑破视口。
- **Bulk Actions (Data Entry, Low)**：多选 + bulk edit；checkbox 列 + action bar；禁止逐行操作。

**对 Q8 表格三分法（左过滤 / 中主表 / 右详情）校验**：
- 三分法本身 CSV 未直接提及，但不违背"overflow-x-auto + card fallback"原则：中区表格可滚动，右详情可收折。
- **必须补入 Q8 规范**：checkbox 列 + 顶部 action bar（批量禁用/标记/导出）。当前 Q8 规范若无批量操作，属于已知反模式"Repeated actions per row"，需纠正。
- 小屏（<1280px）右详情 drawer 化，主表保留 `overflow-x-auto`，避免 layout break。
- 补充（CSV 未覆盖，但是 data-dense 通识，可选吸收）：行高紧凑模式（36/44/56 三档）、sticky header、列 resize、数值列右对齐 + tabular-nums。

## 7. 告警 UX 最佳实践（查询 #7: ux / alerting notification n=3 → 0 命中；回退 "notification" n=5 → 0；再回退 "error feedback" n=5 → 5 命中）
**检索失败记录**：直接查 "alerting notification" 与 "notification" 均 0 命中，数据库无告警垂类条目。以 "error feedback" 最近邻替代，取 4 条可复用条目（排除 #5 AI 反馈）。

对 Q10 Alerts 页的启发：
- **Error Recovery (Feedback, Medium)**：每条告警卡片必须有 "Try again" / "静默" / "去处理" 等明确下一步 + help link；禁止只有告警文案无动作。
- **Error Feedback (Interaction, High)**：告警必须 near problem —— 列表页缩略 badge + 详情页 inline 红边 + 消息文本。
- **Error Messages (Accessibility, High)**：所有新告警实时通告用 `role="alert"` 或 `aria-live="assertive"`；禁止仅视觉红点。Q10 Alerts Toast/抽屉需补 ARIA。
- **Error Placement (Forms, Medium)**：规则配置表单的错误要放在对应字段下方，禁止顶部汇总。Q10 告警规则编辑器需遵守。

## 8. 可吸收的新决策（补细节，不推翻 ADR-0012）
按优先级整理，可直接落到 Slice 1 design tokens / 规范文档：

**T1 Token 补位**（写入 `tokens.css` / Tailwind config）
- `--bg-deep: #0B0D12` / `--bg-base: #13161D` / `--bg-elevated: #1C2029`（ADR-0012 已锁，重申）。
- `--fg-primary: #F8FAFC` / `--fg-muted: #94A3B8` / `--on-accent: #0B0D12`（新增）。
- `--border-hairline: rgba(255,255,255,0.08)` / `--surface-overlay: rgba(255,255,255,0.05)`（新增）。
- `--accent: #3DDCCA` / `--accent-glow: rgba(61,220,202,0.20)` / `--ring: #3DDCCA`（glow 新增）。
- `--sev-critical: #FF5A67` / `--sev-warning: #FFB547` / `--sev-info: #5EA8FF` / `--sev-ok: #3DDCCA`（ADR-0012 已锁）。
- `--easing-standard: cubic-bezier(0.16, 1, 0.3, 1)`（新增）。

**T2 字体细节**
- Tailwind `fontFamily`: `sans: ['HarmonyOS Sans SC','IBM Plex Sans','sans-serif']`、`mono: ['JetBrains Mono NL','JetBrains Mono','monospace']`。
- 数值列统一 `font-variant-numeric: tabular-nums`。

**T3 Q9 Overview 图表规范补入**
- Streaming chart 强制 pause/resume + KPI 大字 + `prefers-reduced-motion` 冻结动画。
- Anomaly 用 shape marker + text annotation 双通道。
- 线型 solid/dashed/dotted 区分多系列，不仅靠颜色。
- 所有图提供 togglable data table fallback。
- ECharts 实现 anomaly 用 `markPoint`，confidence band 用 `markArea`，streaming 用 `dataZoom` + buffered append。

**T4 Q8 表格规范补入**
- 必须有 checkbox 多选列 + 顶部 action bar（批量操作）。
- `overflow-x-auto` 容器；<1280px 右详情降级为 drawer。
- 数值列右对齐 + tabular-nums。

**T5 Q10 Alerts 规范补入**
- 每条告警必须有明确 "下一步" 动作按钮 + 帮助链接。
- 新告警 Toast/Drawer 用 `role="alert"` + `aria-live="assertive"`。
- 规则表单错误 inline 放到字段下方，不做顶部汇总。

**T6 明确不采纳**
- 纯 `#000000` 背景（OLED smear）。
- Cyberpunk scanlines / glitch 特效。
- 大面积 BlurView glassmorphism（伤数据密度）。
- Streaming chart 的 `#00FF00` 脉冲色（与品牌 teal 统一到 `#3DDCCA`）。
- Stock OHLC candlestick（不适配 db-monitor 场景）。
