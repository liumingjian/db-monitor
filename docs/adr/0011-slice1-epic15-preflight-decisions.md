# ADR-0011: Slice 1 / Epic 15 Pre-flight Decisions

- Status: accepted
- Date: 2026-04-22
- Relates to: ADR-0003, ADR-0004, ADR-0005, ADR-0006, ADR-0007, ADR-0009
- Supersedes: 无（但收窄 ADR-0006 的 audit 命名口径、替换 Epic 15 EPIC.md 的 p95 acceptance 表述）

## 背景

Epic 15 激活后、child `#1` 实施前，用 CSE "先测量后控制" 做了 3 路并行只读审计 + 1 路 targeted probe，发现 5 个在 SPEC 骨架里未锁定的硬缺口（D1..D5，D4 为归档型）。本 ADR 把 4 条决议 + 1 条归档落成可审计工件，供 child `#1..#6` 实施时引用；未来任一条被证伪，必须通过新 ADR supersede，不直接编辑本文件。

## D1 — instance detail tab 挂载模型：子路由

`apps/web/app/instances/[instanceId]/` 当前是单 SSR 页（`page.tsx`），无任何 tab 容器。Epic 15 要新增 3 个 tab，Slice 2-8 会继续涨。

**决议**：采用 Next.js App Router 的 route group 子路由承载 tab。

结构：

```
app/instances/[instanceId]/
├── layout.tsx               # 承载 tab 栏（客户端组件），读 params.instanceId
├── page.tsx                 # overview（默认 tab）
├── processes/page.tsx       # child #1 挂载
├── slow-queries/page.tsx    # child #3 挂载
└── tablespaces/page.tsx     # child #4 挂载；layout 里按 instance.engine 条件显示入口
```

Smoke 路由直接追加到 `apps/web/tests/smoke.test.ts::buildSmokeRouteSet()`。

**拒绝**：客户端 useState Tabs 容器——URL 不可分享、smoke 需 click 模拟、单文件随 tab 膨胀。

## D2 — runtime 审计 action 命名：`<resource_plural>.<sub>.<verb>`

现有 audit action 存在两条并存的命名线：

1. `instances.validate` / `instances.create` / `rules.create` / `settings.write` —— **复数资源 . 动词** 风格（runtime / CRUD 命令）
2. `alert.workflow.acknowledged` / `alert.workflow.suppressed` —— **单数域 . 子资源 . 动词** 风格（alerting 内部事件流）

**决议**：runtime/CRUD 命令一律走第 1 条命名风格，alerting 事件流不动。未来 Slice 2-8 的 runtime 命令（SQLServer 进程 kill、Oracle session kill 等）统一走此风格。

SPEC 字面调整：

| 原 SPEC 文本 | 改为 |
|---|---|
| `instance.process.kill` | `instances.process.kill` |
| `alert.rule.override.upsert` | `rules.override.upsert` |
| `alert.rule.override.delete` | `rules.override.delete` |

ADR-0006 原文保留不改；本 ADR 在"runtime action 命名"这一维度上收窄 ADR-0006 的 `instance.<resource>.<verb>` 表述。

## D3 — per-instance 运行期配置载体：新表 `instance_parameters` JSONB

`control_mysql_instances` 无任何运行期可配参数列；`labels_json` TEXT 是业务标签，不复用。Slice 1 需要 2 个键，Slice 2-8 会继续增（OS/SNMP/SQLServer/Oracle session/Redis 多引擎参数爆炸）。

**决议**：新建 PostgreSQL 表 `instance_parameters`，参数存 JSONB。

```sql
CREATE TABLE instance_parameters (
    instance_id TEXT PRIMARY KEY REFERENCES control_mysql_instances(instance_id) ON DELETE CASCADE,
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

- Slice 1 参与的键：
  - `processlist_interval_seconds`（default 30，min 10，by ADR-0005）
  - `slow_threshold_seconds`（default 1.0，by ADR-0007）
- pydantic 在 API 层做强类型校验；PG 层不加 JSONB check constraint（100 实例 × 10 键规模没必要）
- 读路径：collector / rule-engine 按需 `JOIN instance_parameters USING (instance_id)`
- 默认行为：缺行时视作 `{}`，API 层套默认值
- 权限：写入走 `INSTANCES_WRITE`（复用现有），审计 action `instances.parameters.upsert`

**拒绝**：
- 独立列方案——多引擎表重复列，Slice 2+ 每加一个参数一次 ALTER
- 复用 `labels_json`——语义混淆 + 类型不安全

## D4 — rule-engine 评估结构（探针结论归档）

非决议项；把 D4 probe 发现的事实锁下来，供 child `#5` 实施直接引用、避免重查：

- 评估入口：`apps/api/src/db_monitor_api/alerting/evaluation.py:43-74` `evaluate_samples()`
- 样本已预加载（`samples: tuple[MetricSample, ...]` 入参），**LEFT JOIN overrides 不触发任何 ClickHouse 读**
- 已存在 N+1：`_evaluate_sample()` 每个 (rule, instance, sample) 调 `repository.find_active_alert()` 一次——Epic 15 **不修**
- 无 async/concurrency、无缓存、无性能埋点
- 规则加载：每轮 `evaluate_samples()` 一次 `list_rules()`，无缓存
- LEFT JOIN 建议落点：`alerting/postgres_repository.py:180-191` 的 `list_rules()` SQL 加 `LEFT JOIN rule_instance_overrides USING (rule_id)` + `json_agg(json_build_object(...))` 聚合为数组；`AlertRule` domain model 多一个 `overrides: tuple[OverrideRow, ...]` 字段；`_evaluate_sample()` 在阈值比较前应用 override 字段

## D5 — rule-engine acceptance 口径：换硬边界 + 插 best-effort 埋点

原 EPIC.md Coupling Notes：

> overrides 评估必须不让 rule-engine p95 延迟回归超过 10%

当前 repo 无任何 p95 埋点，baseline 不存在，该硬边界**不可验证**。

**新硬边界**（child `#5` signoff 必须满足，可代码侧静态 + 单测验证）：

1. `list_rules()` 仍返回 |rules| 行（而非 |rules| × |overrides|）——overrides 用 `json_agg` 聚合成数组
2. `_evaluate_sample()` **不新增**任何 DB call
3. 加 LEFT JOIN 后 `find_active_alert()` 的 N+1 总次数等价（不退化为 N+2）

**Best-effort 埋点**（child `#5` 顺带，非 signoff 门）：

- `evaluate_samples()` 首尾插 `time.perf_counter()`，差值作为 `evaluation_duration_ms` 进结构化日志（结构：`event="rule.evaluation.completed"`, `duration_ms`, `rule_count`, `sample_count`）
- 不做 p95 聚合（没 baseline，只能看方向单调性）
- Slice 2（告警成熟度切片）再补直方图 / Prometheus 导出
- 未来如果 N+1 成真瓶颈，再开独立 ADR 引入批量 `find_active_alerts([...])`；**不在 Epic 15 范围**

## Consumers

本 ADR 改动的下游工件：

- `.codex-tasks/20260422-slice01-epic15-monitoring-depth/EPIC.md`（Control Contract → Coupling Notes、Multi-Model View → 静态契约域、末尾新增 Pre-flight Decisions 节引用本 ADR）
- `.codex-tasks/20260422-slice01-epic15-monitoring-depth/SUBTASKS.csv`（child `#2` / `#5` 的 acceptance_criteria audit action 字符串）
- child `#1` SPEC（config 载体从 `instance.processlist_interval_seconds` 改为 `instance_parameters.parameters->>'processlist_interval_seconds'`）
- child `#2` SPEC（audit action `instance.process.kill` → `instances.process.kill`）
- child `#3` SPEC（`slow_threshold_seconds` 从 `control_mysql_instances` 新增列改为 `instance_parameters` JSONB 键）
- child `#5` SPEC（audit action 改名 + LEFT JOIN 实现细节 + acceptance 新口径）

## Rollback

任一条决议在实施中被证伪：

- 开新 ADR（0012+）supersede 该条
- 同步回写 EPIC.md / SUBTASKS.csv / 对应 child SPEC
- 本 ADR 保留为历史记录，不就地编辑

## 最终验证

```bash
test -f docs/adr/0011-slice1-epic15-preflight-decisions.md \
  && grep -q "Status: accepted" docs/adr/0011-slice1-epic15-preflight-decisions.md \
  && grep -q "instance_parameters" docs/adr/0011-slice1-epic15-preflight-decisions.md \
  && grep -q "instances.process.kill" docs/adr/0011-slice1-epic15-preflight-decisions.md \
  && grep -q "evaluation_duration_ms" docs/adr/0011-slice1-epic15-preflight-decisions.md
```
