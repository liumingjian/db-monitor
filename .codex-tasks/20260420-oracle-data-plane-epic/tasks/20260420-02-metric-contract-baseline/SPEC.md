# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 把当前 `mysql-only` 的 metric sample / ClickHouse schema seam 收敛成 engine-aware baseline
- 为后续 Oracle collector、analytics API 和 web detail 提供统一状态面基础
- 在不宣称 Oracle 已可采集的前提下，保持现有 MySQL data-plane 继续 green

## Non-Goals

- 不在本任务中实现 Oracle collector 或 Oracle analytics route
- 不把 MySQL 指标名立即改造成跨引擎统一语义
- 不在本任务中扩展 OpenAPI / web surface

## Constraints

- 必须显式保留 `engine` 维度，避免第二引擎 telemetry 再次塞进隐式 MySQL 假设
- 如果需要修改 ClickHouse metrics table 语义，必须同步更新 schema version、bootstrap contract 与现有回归测试
- 不允许用“Oracle 暂时还没写入”作为继续保留 `mysql-only` table semantics 的借口

## Deliverables

- `MetricSample` 显式携带 `engine`
- ClickHouse schema / sink / repository 使用新的 engine-aware metrics storage baseline
- MySQL metrics pipeline、schema bootstrap 和 analytics read-side regression 继续通过

## Final Validation Command

```bash
uv run pytest tests/schema/test_schema_bootstrap.py \
  tests/integration/metrics_pipeline/test_metrics_pipeline.py \
  tests/integration/analytics_queries/test_analytics_queries.py
```
