# Progress

## Summary

- Task shape: single-full
- Goal: 冻结 engine-aware metric sample 与 ClickHouse schema baseline

## Recovery

- 任务: 已完成 state-plane 的 mysql-only seam 收敛
- 形态: single-full
- 进度: 3/3
- 当前: 已完成
- 文件: `.codex-tasks/20260420-oracle-data-plane-epic/tasks/20260420-02-metric-contract-baseline/TODO.csv`
- 下一步: 切换到子任务 `#3 Implement Oracle collector and worker dispatch baseline`

## Control Contract

- Primary Setpoint: 第二引擎 telemetry 可以被状态面诚实表示，而不再被 `mysql-only` contract 锁死
- Acceptance: `MetricSample` 和 ClickHouse schema 都带有显式 `engine` 语义；MySQL pipeline / analytics regression 继续 green
- Guardrails: 不声称 Oracle collector 已完成；不回退当前 MySQL data-plane；不打破 schema bootstrap contract
- Sampling Plan: 先 L0 修改 sample/schema/sink/repository，再跑 schema + pipeline + analytics targeted suites
- Constraints: 如果 schema 语义变化，需要同步更新 live gate 的 reset/bootstrap 口径

## Notes

- 当前仓库最深的 mysql-only seam 不在控制面，而在 telemetry state-plane
- 这一步是 Oracle collector 之前的必要收敛，不做会让后续 worker / analytics 实现继续建立在错误表意上
- 已完成的最小控制输入：
  - `MetricSample` 现在显式持有 `engine`
  - ClickHouse schema version 提升到 `2`
  - metrics table 从 `mysql_metrics` 改为更中性的 `metric_samples`
  - sink payload 与 ClickHouse analytics repository 都会读写 `engine`
- 本轮验证证据：
  - `uv run pytest tests/schema/test_schema_bootstrap.py tests/integration/metrics_pipeline/test_metrics_pipeline.py tests/integration/analytics_queries/test_analytics_queries.py`
  - `uv run pytest tests/api/analytics`
