# Progress

## Summary

- Task shape: single-full
- Goal: 暴露最小 Oracle analytics API / typed contract

## Recovery

- 任务: 已完成最小 Oracle analytics API / typed contract 收口
- 形态: single-full
- 进度: 3/3
- 当前: 已完成，等待父 epic 切到 `#5`
- 文件: `.codex-tasks/20260420-oracle-data-plane-epic/tasks/20260420-04-oracle-analytics-api/TODO.csv`
- 下一步: 由子任务 `#5` 消费当前 generic instance trends contract，把 Oracle web detail flow 从 validation-only 推进到最小趋势可见

## Notes

- 已完成的最小控制输入：
  - analytics service 现在按实例 `engine` 选择 availability metric 和 detail metric specs
  - `/analytics/instances/{instance_id}/trends` 成为新的主 detail route
  - `/analytics/mysql-instances/{instance_id}/trends` 继续保留为兼容 alias，但不再出现在 OpenAPI schema 中
  - typed client 已改为走 generic instance trends route，并把 contract version 提升到 `0.6.0`
- 当前 Oracle detail contract 只覆盖批准的最小趋势集：
  - `oracle_uptime_seconds`
  - `oracle_sessions_total`
  - `oracle_sessions_active`
  - `oracle_session_waits`
  - `oracle_user_calls_per_second`
  - `oracle_physical_reads_per_second`
- 明确未交付的 parity 边界：
  - 本任务没有把 overview fleet ranking / preset semantics 一次性做成全引擎统一
  - 本任务没有引入 Oracle 专属页面家族或容量洞察文案重写
  - web detail flow 仍需在下一子任务中消费这些新 metric names，并把 validation-only gating 替换为真实最小趋势展示
- 额外修复：
  - overview instance snapshot 之前把 `replication_lag_seconds` 错指到 outbound throughput spec；现已修正并补入回归断言

## Validation

- `uv run pytest tests/api/analytics tests/integration/analytics_queries`
- `pnpm openapi:update`
- `pnpm openapi:check`
- `pnpm --filter web test -- tests/data-layer.test.ts`
