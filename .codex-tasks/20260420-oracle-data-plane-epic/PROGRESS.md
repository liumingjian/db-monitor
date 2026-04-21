# Progress

## Summary

- Task shape: epic
- Goal: 把 Oracle 从 validation-only 推进到最小真实 data-plane 与 insights baseline

## Recovery

- 任务: `Oracle Data Plane and Minimum Insights` 已完成并通过根级 signoff
- 形态: epic
- 进度: 6/6
- 当前: 全部子任务完成
- 文件: `.codex-tasks/20260420-oracle-data-plane-epic/SUBTASKS.csv`
- 下一步: 如需继续新 epic，必须先按协议完成 Epic 07 close-out review，并基于显式 repo gap 决定是否扩展 roadmap

## Control Contract

- Primary Setpoint: Oracle 不再只是“能接入/能校验”，而是获得一个最小真实 telemetry data-plane 起点
- Acceptance: 新 epic truth artifacts 完整存在；子任务 `#2` 开始关闭 state-plane 的 mysql-only seam；后续 child task 可以从磁盘恢复
- Guardrails: 不伪造 Oracle analytics parity；不回退 MySQL data-plane；不破坏 Epic 06 的组织治理语义
- Sampling Plan: 先修状态面，再修 collector / analytics / web，最后通过 live gates 与根级 signoff 收口
- Constraints: 原始 roadmap 01-06 已全部完成，本 epic 是基于显式 repo gap 的 post-phase-one continuation

## Notes

- 这是一个新的 post-phase-one active epic，而不是对旧 roadmap 中未完成 epic 的重复激活
- Epic 05 已经把 Oracle data-plane gap 写明；Epic 06 没有覆盖它
- 当前 UI 和 pipeline 仍然诚实地表明 Oracle 是 validation-only，这正是本 epic 要关闭的主误差
- 全部已批准 child task skeleton 已一次性落盘，满足 planning completeness 规则
- 子任务 `#2` 已完成：
  - `MetricSample` 现已显式携带 `engine`
  - ClickHouse schema version 提升到 `2`
  - metrics table 已从 `mysql_metrics` 收敛到通用的 `metric_samples`
  - targeted validation 已通过：
    - `uv run pytest tests/schema/test_schema_bootstrap.py tests/integration/metrics_pipeline/test_metrics_pipeline.py tests/integration/analytics_queries/test_analytics_queries.py`
    - `uv run pytest tests/api/analytics`
- 子任务 `#3` 已完成：
  - scheduler 现在会为 validated Oracle instances 入队
  - `OracleMetricsCollector` / `OracleMetricsWorker` / `EngineAwareMetricsWorker` 已打通 Oracle 的最小 collection loop
  - 当前批准的 Oracle 指标集已收敛为：
    - `oracle_server_available`
    - `oracle_sessions_total`
    - `oracle_sessions_active`
    - `oracle_session_waits`
    - `oracle_user_calls_total`
    - `oracle_physical_reads_total`
    - `oracle_uptime_seconds`
  - 本轮验证证据：
    - `uv run pytest tests/scheduler tests/worker_mysql tests/worker_oracle tests/integration/metrics_pipeline`
    - `pnpm test:control-plane:oracle`
- 子任务 `#4` 已完成：
  - analytics service 现在会按实例 `engine` 选择 availability metric 与 detail metric specs
  - 实例趋势读取已从 MySQL-only 路由推进到通用的 `/analytics/instances/{instance_id}/trends`
  - MySQL detail 别名路由仍保留，但从 OpenAPI schema 中隐藏，避免继续把新 contract 锁回 MySQL-only
  - Oracle detail contract 当前批准的最小趋势集已落地：
    - `oracle_uptime_seconds`
    - `oracle_sessions_total`
    - `oracle_sessions_active`
    - `oracle_session_waits`
    - `oracle_user_calls_per_second`
    - `oracle_physical_reads_per_second`
  - 顺手修复了 overview instance snapshot 中 `replication_lag_seconds` 取错 card spec index 的问题，并补入断言防回归
  - 本轮验证证据：
    - `uv run pytest tests/api/analytics tests/integration/analytics_queries`
    - `pnpm openapi:update`
    - `pnpm openapi:check`
    - `pnpm --filter web test -- tests/data-layer.test.ts`
- 子任务 `#5` 已完成：
  - `supportsInstanceAnalytics` 不再把 Oracle detail page 挡在 validation-only 分支外
  - 实例详情页现在会复用通用 trends contract 渲染 Oracle 最小趋势，而不是继续显示空白 detail surface
  - `monitoring-ui` 已按 `engine` 产出不同的 capacity readout 解释：
    - MySQL 继续维持现有 lag / buffer-pool / throughput 语义
    - Oracle 使用 sessions / waits / user calls / physical reads 的最小解释
  - capability 文案、instances onboarding copy、preset 文案、preview fixtures 与 web tests 已同步更新，显式保留“overview 与更深引擎诊断仍是 MySQL-first”的边界
  - 本轮验证证据：
    - `pnpm --filter web test`
    - `pnpm --filter web typecheck`
    - `pnpm --filter web build`
- 子任务 `#6` 已完成：
  - 根级 signoff 已同时覆盖：
    - OpenAPI contract snapshot
    - schema bootstrap
    - analytics API / integration / metrics pipeline / control-plane regressions
    - web test / typecheck / build
    - root smoke flow
  - Oracle live gate 已在当前 macOS + Docker 环境下重新通过：
    - `pnpm test:control-plane:oracle`
  - 本 epic 现已证明：
    - Oracle 不再停留在 validation-only，而是具备最小真实 collector -> schema -> analytics -> web detail 闭环
    - 既有 MySQL 数据面与组织治理主链在同一轮 signoff 中未发生回退
