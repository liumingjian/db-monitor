# db-monitor

内部数据库监控平台。目标从"MySQL-first 单引擎最小可用"切换到"还原 legacy lepus-v3.8 的全部能力"：短期按阶段（Option B）推进现有引擎的产品级投产，最终态覆盖 lepus 的全部 6 引擎与深度功能（Option A）。原始 `PRD.md` 已被显式丢弃，参见 `docs/adr/0001-lepus-parity-pivot.md`。

## Language

**Lepus Parity**:
项目终极目标——覆盖 legacy `lepus-v3.8/` 的引擎与深度能力，但已被 2026-04-22 决议裁剪：支持 MySQL、Oracle、OS、SQLServer 四个引擎的产品级深度；**MongoDB 永不复刻**；**Redis 是条件性切片**（仅当业务真正提出需求时激活）。深度能力包括：slow query deep analysis、bigtable、binlog auto-purge、SNMP、per-instance 阈值、大屏、报表邮件。飞信、CodeIgniter 的 widget/language/menu/license/profile/awrreport 永不复刻。
_Avoid_: "功能对等"、"lepus 复刻"（无边界语义，容易被解读为 UI 复刻）；"6 引擎"（已裁为 4+1 条件）。

**Option A**:
字面对等——最终态必须交付 lepus 的全部引擎与深度能力。长期目标。
_Avoid_: "全量还原"、"完全复刻"。

**Option B**:
阶段性对等——按切片推进；每个切片结束后现有引擎都能在生产真用，再扩下一个引擎或深度。当前执行路径。
_Avoid_: "分阶段"、"分批"（太泛）。

**Slice**:
Option B 下的一次完整产品级增量。完成的判据不是"代码合并"，而是"该切片覆盖的引擎/能力在真实环境能被 DBA 用来值班"。
_Avoid_: "epic"（epic 是实施单位，slice 是产品价值单位；一个 slice 可能跨多个 epic，也可能只占一个 epic 的一部分）。

**Platform-Level Productionization**:
`Epic 13` 已收口的内容——平台自身（lint、schema、gates、deployment baseline、operator checklists）达到"可以内部单环境上线"。这**不等于**产品可投产。
_Avoid_: "可投产"、"launch readiness"（这两个词在当前语境下会误以为产品也投产了）。

**Product-Level Productionization**:
当前真正的目标——已支持引擎的用户价值（值班、排障、告警、处理闭环）达到可以替代 lepus 用于生产。当前 Gap 主要在 Notifier 实际渠道、MySQL 运维深度（processlist / slow query）、per-instance 阈值粒度。
_Avoid_: "能用"、"好用"（无验收标准）。

**Legacy Lepus**:
`lepus-v3.8/` 目录下的历史代码。仅作为领域参考、指标启发、告警行为参考；不作为运行时、表结构或代码结构的复用源。
_Avoid_: "旧系统"（歧义）、"lepus"（未限定版本时易误解）。

## Relationships

- **db-monitor** 的终极目标是达到 **Lepus Parity**（Option A）。
- **db-monitor** 的当前执行路径是 **Option B**，由若干 **Slice** 顺序推进。
- 每个 **Slice** 的完成判据是 **Product-Level Productionization**（对其覆盖范围而言）。
- **Platform-Level Productionization** 是 **Product-Level Productionization** 的必要非充分条件：平台可上线才谈得上产品可投产，但平台 green 不意味着产品 green。
- **Legacy Lepus** 是 **Lepus Parity** 的验收对照物，但**不是**实现蓝图。

## Flagged ambiguities

- "可投产"在历史文档中同时指 **Platform-Level Productionization**（Epic 13 的意思）和 **Product-Level Productionization**（Boss 当前要求的意思）——2026-04-22 决议：涉及发布时显式标明是哪一级。
- 原始 `PRD.md` 明确将 `Oracle/MongoDB/Redis/SQLServer/OS`、`slow query deep analysis`、`bigtable`、`binlog maintenance`、`advanced report`、`multitenancy` 列为 Out of Scope——2026-04-22 决议：PRD 整体作废，新目标以 CONTEXT.md + ADR-0001 为准。
- "engine coverage" 在现有 roadmap 文档里等于 "已写入枚举 + 有最小闭环"，但在 **Lepus Parity** 语境下等于"深度对等"。后续讨论指标时必须显式区分 "engine onboarding" vs "engine parity"。

## Scope & scale constraints (2026-04-22)

- **用户画像**：内部 DBA 小队，5-8 人。单组织（`DEFAULT_ORGANIZATION_ID`），不对外多租户。
- **实例规模**：100 量级（MySQL 为主，Oracle 少量）。第一版 scheduler + Redis queue + 顺序 worker 的架构在这个规模内够用；但 `per-instance 阈值开关` 在此规模下是刚需（全局规则会导致误报泛滥）。
- **通知渠道优先级**：飞书 > 邮件 > 短信。企业微信作为飞书的并行后续补丁，不进切片 1。飞信废弃不复刻。
- **失败容忍度**：中等——平台短时（<15 分钟）不可用可接受；持续告警盲区视为事故。因此 `Epic 14 (Scale/HA/DR)` 继续 deferred，直至产品深度补完。

## Slice 1 scope (2026-04-22 locked)

切片 1 的目标：让 DBA 第一次能用 db-monitor 值班和排障，覆盖面=**现有 MySQL+Oracle 的产品级完整度**，不新增引擎。

**In scope**：
1. **Notifier / 飞书渠道**：`apps/notifier` 从占位符变成可用服务，飞书是第一真实通道。
2. **Notifier / 邮件渠道**：SMTP 兜底 + 领导可见 + 审计用。
3. **Per-instance 阈值开关**：规则的"启用/阈值"可以按实例覆盖；对标 lepus `db_servers_mysql.alarm_*` + `threshold_warning/critical_*` 字段级开关。**方案已锁为新建 `rule_instance_overrides` 关联表**（rule_id FK × instance_id FK × threshold NULL × enabled NULL，PK=(rule_id, instance_id)）；override 字段只有 `threshold` + `enabled`，不做 severity/window override；overrides 内嵌规则详情 API 响应；web 子表逐条编辑，不做批量导入/导出。详见 `docs/adr/0004-per-instance-threshold-overrides.md`。
4. **MySQL processlist + kill**：对标 lepus `lp_mysql/process`；新增采集函数 + 流式查询 API + web 页；kill 走审计。
5. **MySQL slow query 基础列表**：对标 lepus `lp_mysql/slowquery` 的浅层；"某实例最近 N 分钟 slow_log 最慢 K 条" + 时间/instance 过滤。**不做** pt-query-digest 深度（留切片 6+）。
6. **Oracle tablespace 列表**：对标 lepus `lp_oracle/tablespace`；采集 + API + web detail 新增 tab/卡。

**Out of scope（明确推后）**：
- 企业微信、短信 → 切片 2+
- Bigtable / Binlog purge / 备份 / 大屏 / 报表邮件 / pt-query-digest → 切片 6+
- Oracle session 深度 / AWR → 切片 3+
- MongoDB / Redis / SQLServer / OS → 切片 2/3/4/5（顺序待定，见 Q4）

**验收（Done 判据）**：一次真实值班演练。DBA 在测试 MySQL 上主动制造 4 类故障（连接数打满 / 复制延迟 / 慢查询拖死 / 磁盘告警），全程用 db-monitor 跑完"飞书收到告警 → 进入 processlist → kill 或处置 → 告警自动恢复或 ack"。演练通过才关切片。离线 gate + smoke 通过只是**必要非充分**条件。

### Slice 1 execution order (locked — 监控先，通知后)

**Epic 15 — Monitoring depth & rule granularity（先做，2-3 周）**
1. MySQL processlist 采集：worker 每 30 秒快照 → ClickHouse `mysql_processlist`（TTL 7 天，全量含 Sleep）；list API 从 ClickHouse 读，支持 user/host/command/min_time 筛选 + 历史回放。详见 `docs/adr/0005-mysql-runtime-inspection-data-flow.md`
2. MySQL processlist kill 端点 `POST /instances/{instance_id}/processlist/{process_id}/kill`；新增 `Permission.INSTANCES_ACTION`（不复用 WRITE）；kill 走临时实时连接（不经 ClickHouse）；安全网最小化（只禁监控用户自身连接 + validation≠PASSED 时按钮禁用）；审计 `instance.process.kill`。详见 `docs/adr/0006-runtime-action-permission-and-safety.md`
3. MySQL slow query 短窗列表：worker 每 60 秒增量拉 `performance_schema.events_statements_history_long`（按 EVENT_ID 增量，不重复采集）→ ClickHouse `mysql_slow_query_events`（TTL 7 天；digest 字段存但 UI 不展示，给切片 5 铺路）；阈值 `instance.slow_threshold_seconds` 默认 1 秒；API 按 min_duration/user/schema/digest/time 筛选；web 实例 detail 新增 "Slow queries" tab（15 分钟窗口、Top 50 默认）；PS 未开启的实例 tab 显示空 + 提示，不阻塞 validation。详见 `docs/adr/0007-mysql-slow-query-data-source.md`
4. Oracle tablespace：采集用 `dba_tablespace_usage_metrics`（含 autoextend 上限，不是 lepus 的 `dba_data_files` 组合）；频次 300 秒；只按 tablespace 级别聚合（datafile 明细推到切片 6）；专表 `oracle_tablespaces`（30 天 TTL）；web detail 新增 "Tablespaces" tab + 使用率排序 + 24h mini-sparkline + 30 天趋势全屏图；**告警规则不在切片 1，推到切片 2**（per-tablespace 告警需要规则扩 label_selector）。详见 `docs/adr/0008-multi-dimensional-metrics-dedicated-tables.md`
5. Per-instance 阈值（schema + API + web；详见 ADR-0004）
6. Epic 15 离线 signoff：lint + typecheck + gates + 新能力 smoke（不含真实演练）

**Epic 16 — Notification reality & slice-1 acceptance（后做，2-3 周）**
1. Notifier 抽象重构（Protocol 占位 → 可插拔 factory）
2. 飞书渠道实现（webhook / @成员 / 卡片格式） + 失败重试
3. SMTP 邮件渠道实现 + 模板
4. 端到端集成（rule 命中 → 飞书/邮件 真到达；Notifier 超时不阻塞 rule-engine）
5. **切片 1 真实值班演练 signoff**（四类故障跑通；不允许用平台 gate 代替）

**为什么监控先**：DBA 日常高频动作是查状态/排障，Notifier 是偶发触发。Epic 15 结束时 DBA 已经能用 db-monitor 干活（告警仍由现有 lepus 过渡发），Epic 16 结束时 db-monitor 才成为完整替代。两次小升级优于一次大跳。

## Slice sequence (2026-04-22 locked)

总路径：8 个切片，31-45 周（8-10 个月）到达 **Lepus Parity**。每两切片之间留 1 周 stabilization 已隐含在浮动估时里。

| # | 主题 | 核心内容 | 估时 | 状态 |
|---|---|---|---|---|
| 1 | MySQL/Oracle 产品级完整度 | 见上一节 Slice 1 scope | 4-6 周 | Done（代码侧；真人值班演练 deferred 至客户验收窗口） |
| 2 | 告警成熟度 + 通知面扩展 | 企业微信、短信、告警去重/抑制深化（对标 `alarm_temp`）、审计范围扩展 | 2-3 周 | Active — 见 `.codex-tasks/20260504-slice02-alert-maturity-epic/`，ADR-0013/0014/0015 |
| 3 | OS/SNMP 第三引擎 | SNMP 采集、host CPU/内存/磁盘/网络、per-host 阈值 | 6-8 周 | planned |
| 4 | SQLServer 第四引擎 | 连接/进程/等待、复制、最小告警与 web detail | 3-5 周 | planned |
| 5 | MySQL 深度层 | pt-query-digest 风格 slow query 深度、bigtable 扫描、binlog auto-purge、备份监控 | 6-8 周 | planned |
| 6 | Oracle 深度层 | Oracle session 深入、tablespace 历史趋势（AWR 看是否保留由届时决议） | 4-6 周 | planned |
| 7 | Redis 引擎（**条件性**） | 连接数、命令速率、阻塞、复制 | 3-5 周 | conditional — 需业务显式提出需求才激活 |
| 8 | 大屏 + 报表 + 收官 | screen 大屏（overview 实时 AJAX 版）、报表邮件（`task/send_report_mail`）、admin_log 审计增强、永不复刻清单归档 | 3-4 周 | planned |

**永不复刻**：MongoDB 引擎、飞信短信、CodeIgniter widget/language/menu/license/profile/application/auth/error 控制器、`lp_mysql/awrreport` 页。

## UI Terms (Slice 1.5 UI redesign, 2026-04-22 locked)

17 轮 `/domain-model` 访谈锁定，详见 `docs/adr/0012-ui-redesign-design-system-and-page-architecture.md`。

**Tier 1/2/3/4**:
UI 功能分层。Tier 1 = 必须做的 10 张 Tier 1 页（Login/Overview/Instances/Detail/Alerts/Rules+Overrides/Notify history/Channels/Settings/Audit）；Tier 2 = label 体系替代 `machine_room + application` 二元组；Tier 3 = 占位卡片（Slice 2+ 功能）；Tier 4 = 全局框架件（⌘K / 通知抽屉 / on-call 模式 / 健康指示器）。
_Avoid_: "Core/Extended/Placeholder"（既有中文生态惯用 Tier 命名）。

**Icon Rail**:
左侧 64px 窄栏的 4 个分组图标（`OBSERVE / ALERT / OPERATE / ADMIN`），点击后在右侧展开 216px 上下文侧栏。替代原先"全量展开左侧树"范式。
_Avoid_: "左侧菜单"、"侧边导航"（语义不够精确）。

**Canonical page template**:
所有 Tier 1 业务页的统一 7 段结构：面包屑 40px / entity summary 88px / quick metrics 64px / tab bar 44px / content。Settings 页与 Login 页是唯二例外。
_Avoid_: "通用布局"、"标准布局"。

**Catalog / Feed / Snapshot**:
UI 表格的三种数据形态。**Catalog** 分页（50/页，Instances/Rules/参数），**Feed** 游标分页（Audit/Notify history），**Snapshot** 页面级刷新不分页（Processlist/Tablespace），带 diff-refresh 保留滚动 + 高亮变化。混用视为 bug。
_Avoid_: "分页表"、"实时表"（粒度不对）。

**Tri-state inheritance (override)**:
Rule 的 per-instance override 继承态。后端 `RuleInstanceOverride.enabled: bool | None`，`None = 继承基线`。UI 忠实映射为三态 segmented（继承 / 强开 / 强关），不使用二态 switch 糊弄（会把 None 和 False 混淆）。
_Avoid_: "启用/禁用"（二态误导）。

**四色严重度轴**:
全局状态色：紧急 `#FF5A67` / 警告 `#FFB547` / 提示 `#5EA8FF` / 健康 `#3DDCCA`。后端 `RuleSeverity` 只有 critical/warning 两级；info 和 healthy 仅用于 UI 展示层（告警派生状态 + 实例健康聚合）。
_Avoid_: "红黄绿三色"（不匹配）。

**占位卡片 (placeholder card)**:
Tier 3 功能尚未落地时的统一视觉单元：圆角 + 左侧 Slice 色带 + 大标题 + 一句话解释 + 预期价值 bullet + Slice 标记 + 预计交付窗口。**禁止**在 Tier 1 主路径上出现，**禁止**静默删除。Settings 页的"功能 Slice 状态看板"是所有占位卡片的索引总览。
_Avoid_: "敬请期待"、"功能开发中"（无承诺语义）。

**On-call 模式**:
Alerts 页的值班 toggle。开启时紧急告警触发浏览器 Notification + ping sound，2h 自动关闭。与 Notification 抽屉语义切割：on-call = 实时 push 态；抽屉 = 历史 / 个人通知流。
_Avoid_: "值班开关"（与 schedule 管理混淆）。

**⌘K 命令面板**:
全页通用快捷键 (`⌘K` / `Ctrl+K`)，640px popup，分组搜索（导航 / 实例 / 规则 / 告警 / 动作 / 最近访问）。前端 local-fuzzy（预加载实体元数据），仅告警走实时后端。特殊前缀：`>` 动作 / `!` 告警 / `@` 用户。
_Avoid_: "搜索框"、"快捷搜索"（功能被低估）。

### UI 关键不变量
- UI 默认**中文** + 默认**暗色主题**，主题与语言切换走 SystemSetting 持久化。
- 业务页使用 Canonical page template；Settings 页侧导航；Login 页 60/40 splitscreen。
- 组件内禁止 hardcoded hex 色，必须引用 Tailwind token / CSS var（主题切换前提）。
- 所有中文字符串必须进入 `messages/zh-CN.json`，组件内禁止硬编码中文。
- Tier 3 占位卡片必须标 Slice + 预计交付窗口，不允许模糊词。
- Kill 会话 / 删除规则 / 删除 binding 等危险操作必须要求输入关键字二次确认。
