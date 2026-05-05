# Overview Layout 候选 — section-heading + hairline divider 模板

PR β.1 的核心战术问题：怎么把"每段一个 `rounded-md border bg-bg-base p-4`"
的卡中卡视觉，换成单页面里**一眼能读到段落层级**的扁平模板。

下面 3 个候选都守同一组 ADR-0012 钉子（暗色 `#0b0d0f` 基底 / cyan `#3DDCCA`
accent / 4 色 severity / 4-6-8 圆角 / shadcn / ECharts / 三分法 / 通用态）和
ADR-0016（单 sidebar）。区别只在 **章节头排印 + 分隔符 + 段间节奏 + 留白密度**
4 个维度，让 Boss 用主观体感拍板，不必在视觉锁定上重新争论。

每个候选都是完整 1440×900 的 overview 页面（sidebar + topbar + EntitySummary +
KPI strip + TabBar + Trends 8 charts + Fleet 24 cells + Snapshot 6 rows），可以
直接 Chrome 打开看真实尺寸下的差异。

| 维度 | Variant A — Stripe-API Dense | Variant B — GitHub Insights Neutral | Variant C — Linear Spacious |
| --- | --- | --- | --- |
| **参考产品** | Stripe Dashboard / API Reference | GitHub Insights / Vercel Observability | Linear Inbox / Notion |
| **段头排印** | 11px 全大写 + 0.10em letter-spacing 小标签 (`SECTION · TRENDS`) | 15px H3 加粗 + 13px 灰色副标 | 11px 全大写 eyebrow + 圆点 + 16px H3 + 末端 desc |
| **分隔符** | **每段头部下方贯通 hairline** (`border-bottom`) 全宽 | 段头容器底部一条 hairline，离段头近、离内容远 | **完全不画分隔线**，靠纯留白分段 |
| **段间节奏** | 24px (mt-6) | 32px (mt-8) | 64px (mb-16) |
| **章节内容密度** | 高 — 4 列 chart grid，gap-4 / 8 列 fleet grid，gap-2 / 表行高 36px | 中 — 4 列 chart grid，gap-5 / 6 列 fleet grid，gap-3 / 表行高 40px | 中低 — 4 列 chart grid，gap-6 / 8 列 fleet grid，gap-2.5 / 表行高 44px |
| **章节副信息位置** | 段头同行右侧（"最近 6h · 5min 粒度"） | 段头下面单独一行小字 | 段头同行最右淡色文字 |
| **气质 / 信号** | 工程师工具 · 信息密度优先 · "有产品力的扁平" | 产品经理仪表盘 · 中性 · 易读 · "GitHub 风" | 设计驱动 SaaS · 留白 · 现代 · "Linear 风" |
| **首屏装下的内容** | KPI + 8 charts + 8 fleet 行（满铺） | KPI + 8 charts + 4 fleet 行 | KPI + 5 charts（其余需滚动） |
| **mobile 500×844 风险** | 低 — 高密度模板向下塌陷天然紧凑 | 中 — 段间 32px 在小屏上仍偏松 | 高 — 64px 段距在 500px 宽下显得空 |
| **代码量增益** | 低 — 段头基本 1 行 + 1 个 `<hr>` | 中 — 段头是一个 `flex` 容器加 border-bottom | 中 — 段头三段 + 圆点装饰 |
| **守钉子情况** | ✅ ADR-0012 D1-D7 全守；密度仍在表格三分法允许 | ✅ ADR-0012 D1-D7 全守 | ✅ ADR-0012 D1-D7 全守；mobile 适配需额外 breakpoint |

## 看法（推荐倾向）

如果要**一次重排到位、压住后续 7 页批量复制（PR γ）的复制成本**，建议
**Variant B** — H3 + 段尾 hairline 是最容易被 React 抽成
`<SectionHeading title subtitle? endSlot? />` 的语义，密度也是 Boss 既懂又不
压缩 KPI/chart 现有空间的中位选择。Variant A 信息密度更接近"工程师工具"
的极端，Variant C 偏向"设计稿好看，落地到 mobile 偏松"。

但 layout 是产品观点问题，不是工程问题。**最终选哪个由 Boss 拍板**。

## 决策方式

Boss 在三者中选一个，把以下文件落到本目录：

```
raw/CHOSEN.md
```

格式（示例）：

```markdown
# CHOSEN — Variant B

理由：
- ADR-0012 D6 守（H3 即 16px 加粗，符合现有 type scale）
- 抽 `<SectionHeading>` 最直接，PR γ 复制成本低
- mobile 32px 段距也能下移到 24px 不破布局

后续步骤按 TODO.csv #3-#9 执行。
```

写完后我就开始执行 TODO.csv 步骤 3—6（按选定 layout 重排 4 个 overview 组件）。
