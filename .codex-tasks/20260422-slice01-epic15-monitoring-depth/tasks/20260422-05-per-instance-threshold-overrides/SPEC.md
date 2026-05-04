# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让同一条规则可以对不同实例有不同阈值/启停：新建 `rule_instance_overrides` 关联表；rule-engine 评估 `(rule, instance)` 时通过 LEFT JOIN 查覆盖；API 响应把 overrides 内嵌在规则详情；web 规则编辑页新增"Per-instance overrides"子表

## Key Decisions (Inputs)

- `docs/adr/0004-per-instance-threshold-overrides.md`

## PostgreSQL Schema

```sql
CREATE TABLE rule_instance_overrides (
    rule_id UUID NOT NULL REFERENCES alert_rules(rule_id) ON DELETE CASCADE,
    instance_id UUID NOT NULL REFERENCES control_mysql_instances(instance_id) ON DELETE CASCADE,
    threshold NUMERIC NULL,
    enabled BOOLEAN NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (rule_id, instance_id)
);
```

- override 字段**只有** `threshold` 和 `enabled`；不做 severity/window override

## Rule-Engine Evaluation

- 实施落点（ADR-0011 D4 归档）：`apps/api/src/db_monitor_api/alerting/postgres_repository.py:180-191` 的 `list_rules()` SQL 加 `LEFT JOIN rule_instance_overrides USING (rule_id)` + `json_agg(json_build_object('instance_id', o.instance_id, 'threshold', o.threshold, 'enabled', o.enabled, 'updated_at', o.updated_at)) FILTER (WHERE o.rule_id IS NOT NULL) AS overrides`；`list_rules()` 仍返回 |rules| 行（非 |rules|×|overrides|）
- `AlertRule` domain model（`alerting/domain.py:42-54`）追加字段 `overrides: tuple[RuleInstanceOverride, ...]`
- `_evaluate_sample()`（`evaluation.py:106-119`）阈值比较前查 override dict（内存查找）：

```python
override = rule_overrides.get(sample.instance_id)  # 内存 O(1)
effective_threshold = override.threshold if override and override.threshold is not None else rule.threshold
effective_enabled = override.enabled if override and override.enabled is not None else rule.enabled
# 若 effective_enabled=false，跳过该 (rule, instance) 对
```

- 硬边界（ADR-0011 D5）：(1) `list_rules()` 仍 |rules| 行；(2) `_evaluate_sample()` **不**新增任何 DB call；(3) 既有 `find_active_alert()` N+1 不退化为 N+2
- Best-effort 埋点（非 signoff 门）：`evaluate_samples()` 首尾插 `time.perf_counter()`，结构化日志写 `event="rule.evaluation.completed"` + `duration_ms` + `rule_count` + `sample_count`

## API Contract

- Rule detail response 新增字段 `overrides: List[{instance_id, threshold?, enabled?, updated_at}]`
- `POST /alerting/rules` 和 `PUT /alerting/rules/{rule_id}` 请求 body 接受 `overrides: [...]`（可选）
- 单独端点**不开**（ADR-0004：内嵌在规则详情）
- 审计 action 命名：`rules.override.upsert` / `rules.override.delete`（见 ADR-0011 D2）

## Web

- `apps/web/app/rules/` 规则编辑页新增"Per-instance overrides"子表（沿用规则编辑页现有布局；规则编辑页非 instance detail 子路由，不涉及 ADR-0011 D1）
- 每行：instance 下拉选择 / threshold 可选输入 / enabled 可选三态开关 (inherit/on/off) / 删除按钮
- 顶部有 "+ Add override" 按钮逐条添加
- 不做批量导入/导出（ADR-0004 明定排除）

## Non-Goals

- 不支持 severity override
- 不支持 evaluation_window override
- 不做批量导入/导出
- 不做基于 tag/label 的自动绑定（留到切片 2 或更后讨论）

## Final Validation Command

```bash
uv run pytest tests/api/alerting/test_rule_overrides.py tests/rule_engine/test_override_evaluation.py \
  && pnpm openapi:check \
  && pnpm --filter web typecheck
```
