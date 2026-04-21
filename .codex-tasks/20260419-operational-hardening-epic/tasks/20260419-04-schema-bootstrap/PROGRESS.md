# Progress

## Summary

- Task shape: single-full
- Goal: 建立显式 schema bootstrap 与 version baseline

## Recovery

- 任务: 去掉隐式建表路径，补上可验证的 schema bootstrap 契约
- 形态: single-full
- 进度: 4/4
- 当前: 已完成
- 文件: `.codex-tasks/20260419-operational-hardening-epic/tasks/20260419-04-schema-bootstrap/TODO.csv`
- 下一步: 将 epic 控制权切换到 `#5 recovery guards`

## Notes

- 已新增 `db_monitor_schema` 包，明确承载 PostgreSQL / ClickHouse bootstrap、verify 和 version baseline
- `PostgresControlPlaneRepository`、`PostgresAlertingRepository`、`ClickHouseMetricSink` 已移除隐式建表副作用
- API runtime、scheduler、worker 现在在启动路径先做 schema verify；缺失 schema 会显式失败
- 新增 `scripts/test-schema-bootstrap.ps1` 与 `gates/schema/test_schema_bootstrap_live.py`，验证未 bootstrap 先失败、bootstrap 后再启动
- 受影响 live gates 已改成在各自等待点显式 bootstrap，避免把容器时滞误判成 schema 失败
- 本任务验证已通过：
  - `uv run pytest tests/schema`
  - `uv run ruff check apps tests gates`
  - `uv run mypy apps tests gates`
  - `powershell -ExecutionPolicy Bypass -File ./scripts/test-schema-bootstrap.ps1`
  - `powershell -ExecutionPolicy Bypass -File ./scripts/test-control-plane-postgres.ps1`
  - `powershell -ExecutionPolicy Bypass -File ./scripts/test-alert-pipeline-postgres.ps1`
  - `powershell -ExecutionPolicy Bypass -File ./scripts/test-api-runtime-readiness.ps1`
  - `powershell -ExecutionPolicy Bypass -File ./scripts/test-background-processes.ps1`
  - `powershell -ExecutionPolicy Bypass -File ./scripts/test-metrics-pipeline-live.ps1`
  - `powershell -ExecutionPolicy Bypass -File ./scripts/test-analytics-clickhouse.ps1`
