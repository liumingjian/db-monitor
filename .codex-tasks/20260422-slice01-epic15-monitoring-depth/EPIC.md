# Epic Specification

## Goal

- 补齐现有 MySQL 与 Oracle 两引擎的"产品级监控深度"：DBA 能在 web 上看 MySQL processlist + kill、看最近窗口内的慢查询 Top N、看 Oracle tablespace 使用率与趋势；同时把规则粒度从"全实例单阈值"推进到"per-instance 覆盖"。

## Why This Epic Is Next

- 2026-04-22 roadmap reset 之后，切片 1 的两半段中**监控先做、通知后做**已被锁（`docs/adr/0003`）
- 当前仓库 Gap 已被两轮 subagent 盘点准确定位：
  - `apps/api` 只支持 MySQL 的 7 项核心指标 + Oracle health，缺 processlist / slow query / tablespace
  - `alert_rules` 表只支持 `instance_ids[]` 列表级作用域，100 实例规模下会导致误报泛滥
  - `apps/notifier` 仍是占位符（由 Epic 16 补齐，不在本 Epic 范围）
- Option A（Lepus Parity）要求未来每个新引擎都走同一套"采集→CH / 命令→实时 / 多维指标→专表"模式，本 Epic 是该模式的第一次工程化落地

## Scope

- MySQL processlist 采集 + ClickHouse `mysql_processlist` 专表 + list API + web 页
- MySQL processlist kill 端点 + `Permission.INSTANCES_ACTION` + 审计 + 最小安全网
- MySQL slow query 短窗列表：performance_schema 增量采集 → ClickHouse `mysql_slow_query_events` + API + 实例 detail "Slow queries" tab
- Oracle tablespace：`dba_tablespace_usage_metrics` 采集 → ClickHouse `oracle_tablespaces` 专表 + API + 实例 detail "Tablespaces" tab
- Per-instance 阈值：新表 `rule_instance_overrides`（PK (rule_id, instance_id)）+ rule-engine LEFT JOIN 评估 + API 响应内嵌 + web 子表
- Epic 15 离线 signoff：lint + typecheck + gates + 新能力 smoke（**不**含真实演练，该验收由 Epic 16 承接）

## Non-Goals

- 不实现任何 Notifier 渠道（飞书 / 邮件 / 企微 / 短信）——留给 Epic 16
- 不做真实值班演练 signoff——留给 Epic 16
- 不做 pt-query-digest 风格 slow query 深度分析（digest 聚合 / percentile / count trend）——留给 Slice 5
- 不做 datafile 级别的 Oracle 明细——留给 Slice 6
- 不做 tablespace per-name 告警规则（需要 rule schema 扩 `label_selector`）——留给 Slice 2
- 不做 system/replication 连接的 kill 保护——留给 Slice 5
- 不扩其他引擎（MongoDB 永不做；Redis/SQLServer/OS 走各自 slice）

## Done-When

- 6 个 child 均 `DONE`
- `pnpm test:hardening:signoff` 通过
- 新能力 smoke 测试覆盖 processlist list/filter、slow query list/filter、tablespace list/trend、per-instance override create/update/evaluate 的主路径
- 新增 ADR（如果过程中发现需要）已落盘，不引入对 ADR-0001..0008 的 silent supersede

## Project Control Topology

- 总体设计部:
  - 本 Epic 以 `CONTEXT.md` + `docs/adr/0001..0008` + `lepus-v3.8/` 的领域参考为输入
  - 禁止把 Epic 15 扩成引擎新增或深度分析；遇到真实演练需求直接挂到 Epic 16
- 主落点:
  - 数据面（scheduler/worker）采集链路 + ClickHouse 专表 schema
  - 控制面（apps/api）新增 runtime inspection / slow query / tablespace / override 路由
  - 前端（apps/web）实例 detail 新 tabs + 规则编辑面新增 overrides 子表
- 次级影响面:
  - 状态面：新增 `rule_instance_overrides` PostgreSQL 表（migration）、`oracle_tablespaces`/`mysql_processlist`/`mysql_slow_query_events` 三张 ClickHouse 表
  - OpenAPI 契约扩展（非破坏性）与 typed client 再生
  - `Permission` 枚举新增 `INSTANCES_ACTION`；默认角色矩阵更新
- 冻结边界:
  - 不动 auth / organization / overview / alerting workflow 的既有契约语义
  - 不改 notifier protocol（由 Epic 16 重构）
  - 不扩引擎枚举

## Complexity Transfer Ledger

| 字段 | 说明 |
| --- | --- |
| 复杂性原位置 | 当前"值班排障"这一块复杂性不在 db-monitor，而压在 DBA 的 lepus / SSH / ad-hoc SQL 工作流上 |
| 新位置 | 本 Epic 把 processlist / slow query / tablespace / per-instance 阈值的采集、存储、展示和审计显式沉淀到 repo-local 代码和 schema |
| 收益 | 值班动作从"跨系统切换 + 命令行 + 人工记忆"变成"db-monitor 一站式"；历史回放能力前所未有（lepus 做不到）|
| 新成本 | 三张新 ClickHouse 表的存储、TTL 策略和查询性能需要持续维护；新增 `INSTANCES_ACTION` 权限必须被后续引擎的运行时命令正确复用 |
| 失效模式 | processlist 采集压垮被监控实例；slow query 环形缓冲区 miss 被静默忽略；per-instance overrides 与 rule default 漂移；kill 端点在 validation 失败时误被调用 |

## Control Contract

- Primary Setpoint:
  - 让 MySQL / Oracle 的日常排障工作流从 lepus 迁移到 db-monitor 的技术基线就绪
- Acceptance:
  - 6 child 全部 `DONE`
  - `pnpm test:hardening:signoff` 绿；新 ClickHouse 表与 PostgreSQL 迁移在 `test:schema:bootstrap` 下成立
  - 新 smoke 覆盖新增 4 个 UI 面（processlist / slow queries / tablespaces / rule overrides）的主路径
- Guardrails:
  - 不在采集器里写任何 Notifier 调用
  - 不把 processlist 采集频次默认调到 < 10 秒（会压垮被监控实例）
  - 不允许 kill 端点复用 `INSTANCES_WRITE`
  - 不允许 slow query 采集失败被静默吞（必须进入审计或 worker error 日志）
- Sampling Plan:
  - child `#1` → child `#2`（同族）
  - child `#3` 独立
  - child `#4` 独立
  - child `#5` 独立（schema 改动面最大，放中段）
  - child `#6` 聚合 signoff
- Known Delays / Delay Budget:
  - ClickHouse schema migration 与 OpenAPI snapshot 再生各占 0.5-1 天
  - web 新 tab 组件化要和既有 instance detail 页面结构对齐
- Recovery Target:
  - 任一 child 失败时，可以单独回滚 schema / API / web 任一层而不影响其他 child
- Rollback Trigger:
  - `pnpm test:hardening:signoff` 因本 Epic 产生不可忽略回归
  - `performance_schema` 采集在测试实例上引起可观测负载
  - `rule_instance_overrides` 评估逻辑与既有全局规则产生冲突
- Constraints:
  - 只允许触碰 `apps/api`、`apps/web`、`apps/scheduler`、`apps/worker-mysql`（+ Oracle 采集逻辑在 pipeline）、`contracts/`、`packages/api-client`、`gates/`、`tests/`、`scripts/`、`.codex-tasks/20260422-slice01-epic15-monitoring-depth/`
- Boundary:
  - `apps/api/src/db_monitor_api/`（新增 runtime inspection / slow query / tablespace / overrides 模块）
  - `apps/api/src/db_monitor_pipeline/`（processlist / slow_query / tablespace collector）
  - `apps/api/src/db_monitor_schema/`（ClickHouse 新表 DDL + PostgreSQL migration）
  - `apps/web/app/instances/[instanceId]/`（新 tabs）
  - `apps/web/app/rules/`（overrides 子表）
  - `contracts/openapi.snapshot.json`
  - `packages/api-client/src/`
  - `tests/api/`、`tests/integration/`、`tests/worker_mysql/`、`tests/worker_oracle/`
- Coupling Notes:
  - `INSTANCES_ACTION` 一旦加入，所有后续 slice 的运行时命令都应复用；Epic 本身需要在 `dependencies.py` 和 RBAC 矩阵中完成注册
  - 三张新 ClickHouse 表必须在 `gates/schema/test_schema_bootstrap_live.py` 中被 asserted 创建
  - overrides 评估硬边界（见 ADR-0011 D5）：(1) `list_rules()` 仍返回 |rules| 行，overrides 用 `json_agg` 聚合；(2) `_evaluate_sample()` 不新增任何 DB call；(3) `find_active_alert()` 的既有 N+1 不退化为 N+2；child `#5` 顺带插 best-effort `perf_counter` 埋点（非 signoff 门）

## Close-Out Review

- Epic 13 证明了什么:
  - 平台级投产基线 / release gates / oracle-runtime baseline 已就绪
- Epic 13 没证明什么:
  - 产品级投产——DBA 能否用 db-monitor 替代 lepus 做日常排障
- 2026-04-22 新证据:
  - Boss 显式将目标重置为 Lepus Parity（Option A），Option B 按 8 个 slice 推进
- 默认下一个 epic:
  - `Epic 15: Monitoring Depth & Rule Granularity`（即本 Epic）
- 为什么是它:
  - 切片 1 的"监控先、通知后"顺序已被 `docs/adr/0003` 锁定
  - 它是距离"产品级投产"最近的一次最小可验证变更集

## Child Deliverables

- `#1`: MySQL processlist 采集 + list API + web 页
- `#2`: MySQL processlist kill 端点 + 权限 + 审计 + 最小安全网
- `#3`: MySQL slow query 短窗列表（PS 采集 + API + web tab）
- `#4`: Oracle tablespace 视图（采集 + API + web tab）
- `#5`: Per-instance 阈值（PostgreSQL migration + rule-engine 评估 + API + web）
- `#6`: Epic 15 离线 signoff

## Dependency Notes

- `#2` 依赖 `#1`（复用 processlist 采集 + 实例连接复用路径）
- `#3`、`#4`、`#5` 三者相互独立，可并行
- `#6` 依赖 `#1;#2;#3;#4;#5`

## Child Task Types

- `single-full`

## Multi-Model View

本 Epic 复杂度主要来自"同一份数据被三种不同的消费节奏使用"：采集写入、DBA 交互查询、规则引擎评估。单靠主落点 / 次级影响面两层拓扑解释不清楚。按 CSE 最佳实践同时建立三个模型：

### 静态契约域

- **API 合同**：`GET /instances/{id}/processlist`、`POST /instances/{id}/processlist/{pid}/kill`、`GET /instances/{id}/slow-queries`、`GET /instances/{id}/tablespaces`、`GET/PUT /alerting/rules/{id}`（`overrides` 字段）。全部是**向后兼容扩展**，不 break 既有字段语义。
- **权限枚举**：新增 `Permission.INSTANCES_ACTION`；默认角色矩阵：admin/operator 持有、viewer 不持有。
- **ClickHouse schema**：`mysql_processlist`（TTL 7d）、`mysql_slow_query_events`（TTL 7d、digest 字段仅写不展示）、`oracle_tablespaces`（TTL 30d）。命名遵循 ADR-0008 `<engine>_<concept_plural>`。
- **PostgreSQL schema**：`rule_instance_overrides`（PK `(rule_id, instance_id)`、CASCADE FK）。
- **审计 action 命名**：`instances.process.kill`、`rules.override.upsert` / `.delete`（遵循现有 `<resource_plural>.<sub>.<verb>` 风格，详见 ADR-0011 D2——收窄 ADR-0006 的命名口径）。

### 动态状态域

- **实例生命周期对齐**：child `#1`/`#2`/`#3` 依赖 `instance.validation_status`——`PASSED` 才允许 kill 按钮可点；`PASSED` 以外 processlist/slow-query tab 显示空态但**不**阻塞展示（ADR-0007 未开 PS 实例的行为）。
- **Override 生效状态机**：`override row 存在` × `threshold 非空` × `enabled 非空` 形成 2³ 种有效组合；rule-engine LEFT JOIN 后走"override 字段非空则覆盖，否则继承 rule 默认"。`enabled=false` 是**终止态**，直接跳过该 `(rule, instance)` 评估。
- **采集器失败语义**：processlist/slow-query/tablespace 任一次采集失败必须显式进入 worker error 日志，**禁止静默吞**（Control Contract Guardrail）。连续 N 次失败后进入降速退避，不在本 Epic 写死——推到 ADR-0009 统一规则。

### 容量排队域

基于 ADR-0005/0007/0008 的单点估算，汇总 Slice 1 整体容量视图：

| 数据流 | 采集频次 | 单次写入量级 | 日写入量级（100 实例） | TTL | 7-30 天总量 |
|---|---|---|---|---|---|
| MySQL processlist | 30 s | 平均 50 连接/实例 | ≈ 1.4 亿行/天 | 7 d | ≈ 10 亿行 |
| MySQL slow query | 60 s（增量） | 视 PS buffer miss 率而定 | 预估上界 5000 万行/天 | 7 d | ≈ 3.5 亿行 |
| Oracle tablespace | 300 s | 单实例 ≈ 20 tablespace | ≈ 580 万行/天（按 Oracle 子集 20 实例） | 30 d | ≈ 1.7 亿行 |
| Override 评估 LEFT JOIN | 随 rule-engine 评估频次 | 100 实例 × 活跃规则数 | 每评估窗口 1 次 | — | — |
| Notifier dispatch（本 Epic 不落实现） | — | — | — | — | 推到 Epic 16 ADR-0009 |

**主要排队点**：
1. ClickHouse 写入批量化窗口——若 worker 不做 batch insert，100 实例 × 30s 瞬时并发会把 CH 连接打满。ADR-0005 默认策略是 batch；child `#1` 的 TODO `#2` 必须验证。
2. `performance_schema.events_statements_history_long` 环形缓冲——MySQL 默认 10000 条、单实例高并发慢查询可能 miss。Slice 1 不改被监控实例配置（ADR-0007），miss 率作为观测项纳入演练观察清单。
3. rule-engine LEFT JOIN overrides——100 实例 × 数十条规则 × 每评估窗口一次 JOIN，必须走 `(rule_id, instance_id)` 索引（PK 天然满足），**禁止**在规则详情 API 的响应路径上做全表扫描。

**观测盲区（本 Epic 未覆盖，必须在 Slice 2+ 补）**：
- ClickHouse 分区合并压力的长期趋势（30 天后 `oracle_tablespaces` 分区数量）
- performance_schema buffer miss 的主动告警（本 Epic 只在 UI 显示"未开 PS"，未监控 miss 率）
- Override 与规则默认阈值漂移的审计（管理员批量改规则时的影响面扫描）

## Pre-flight Decisions（ADR-0011）

本 Epic 动工前已锁定 4 条决议 + 1 条归档，见 `docs/adr/0011-slice1-epic15-preflight-decisions.md`：

- **D1** — instance detail tab 采用 Next.js 子路由（`processes/` / `slow-queries/` / `tablespaces/`），非客户端 Tabs 容器
- **D2** — runtime audit action 命名走 `<resource_plural>.<sub>.<verb>`：`instances.process.kill` / `rules.override.upsert`（收窄 ADR-0006 命名口径）
- **D3** — per-instance 运行期配置走新表 `instance_parameters` JSONB，Slice 1 参与键 `processlist_interval_seconds` / `slow_threshold_seconds`
- **D4**（归档） — rule-engine 评估入口 `evaluation.py:43-74` `evaluate_samples()`；样本预加载，LEFT JOIN overrides 不触发 CH 读；既有 N+1 在 `_evaluate_sample()` 的 `find_active_alert()`，Epic 15 不修
- **D5** — rule-engine acceptance 口径换为"无新 DB call + LEFT JOIN 不退化 N+1"硬边界 + best-effort `perf_counter` 埋点（取代原"p95 ≤ 10%"口径，因无 baseline 不可验证）

child `#1..#6` 实施时必须参照本节；任一条被证伪需开新 ADR supersede，不就地编辑。
