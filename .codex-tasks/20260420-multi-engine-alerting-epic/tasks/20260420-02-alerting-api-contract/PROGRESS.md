# Progress

## Summary

- Task shape: single-full
- Goal: 实现 engine-aware rule catalog 与 alert API contract

## Recovery

- 任务: child `#2` 已完成，engine-aware rule catalog 与 alert API contract 已经从 baseline 进入真实实现
- 形态: single-full
- 进度: 3/3
- 当前: 所有步骤已完成，等待 child `#3` 接手 evaluation / alert pipeline 的第二引擎运行语义
- 文件: `.codex-tasks/20260420-multi-engine-alerting-epic/tasks/20260420-02-alerting-api-contract/TODO.csv`
- 下一步: 进入 child `#3`，把已落地的 engine-aware rule contract 继续推进到 evaluation、alert pipeline、noise-control 与 recovery fixtures

## Contract Delivery

- `AlertRule` / `AlertRecord` 现在显式携带 `engine`
- `/alerts/rules` 的 request / response 现在要求并返回 `engine`
- `/alerts` 与 `/alerts/{alert_id}` 的 alert payload 现在返回 `engine`
- 新增 `/alerts/rule-catalog`，返回当前批准的 engine-scoped alert metrics
- rule creation 现在会同时验证：
  - `metric_name` 是否属于该 engine 的批准 catalog
  - `instance_ids` 是否全部存在于当前组织范围内
  - `instance_ids` 的 engine 是否与 rule.engine 一致
- PostgreSQL `alert_rules` / `alert_records` schema 现在有显式 `engine` 列，并对历史数据执行 `mysql` backfill

## Evidence

- backend:
  - `apps/api/src/db_monitor_api/alerting/catalog.py` 新增 engine-scoped rule catalog
  - `apps/api/src/db_monitor_api/alerting/domain.py` / `router.py` / `service.py` / `evaluation.py` 已贯通 `engine`
  - `apps/api/src/db_monitor_api/alerting/postgres_repository.py` 与 `apps/api/src/db_monitor_schema/postgres.py` 已增加 `engine` persistence/backfill
- contract:
  - `packages/api-client/src/index.ts` 新增 `engine` 字段与 `listRuleCatalog()`
  - `contracts/openapi.snapshot.json` 已同步新的 alert contract
- tests:
  - `tests/api/alerting/test_alerting_contract.py` 现在覆盖 MySQL + Oracle rule payload、rule catalog route、cross-engine scope rejection
  - `tests/alerting_contract/test_alert_workflow_contract.py` 与相邻 alerting suites 已更新为显式 `engine`

## Validation

- `uv run pytest tests/api/alerting tests/alerting_contract`
- `uv run pytest tests/schema/test_schema_bootstrap.py`
- `uv run pytest tests/integration/control_plane/test_control_plane_postgres.py`
- `uv run pytest tests/rule_engine tests/alerting_delivery tests/alerting_noise tests/alerting_workflow tests/notifier tests/recovery`
- `pnpm --filter web typecheck`
- `pnpm openapi:update`
- `pnpm openapi:check`
