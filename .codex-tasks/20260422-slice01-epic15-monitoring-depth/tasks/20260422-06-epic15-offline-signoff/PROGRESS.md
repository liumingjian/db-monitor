# Progress

## Summary

- Task shape: single-full
- Goal: Epic 15 离线 signoff（不含真实演练）

## Recovery

- 任务: Epic 15 child #6
- 形态: single-full
- 进度: 4/4
- 当前: DONE（三项 signoff 全绿）
- 文件: `.codex-tasks/20260422-slice01-epic15-monitoring-depth/tasks/20260422-06-epic15-offline-signoff/TODO.csv`
- 下一步: Epic 15 Slice 1 关闭，Epic 16 按 Transition Protocol 激活

## Validation Log (2026-04-22)

- `pnpm test:hardening:signoff` → PASS
  - lint / typecheck / ruff / mypy / 210 unit tests
  - `gates/api/test_api_runtime_readiness_live.py` 1 passed
  - `gates/processes/test_background_processes_live.py` 1 passed
  - `gates/schema/test_schema_bootstrap_live.py` 1 passed
  - `gates/recovery/test_recovery_paths_live.py` 1 passed
  - `smoke/phase-one.spec.ts` 1 passed
- `pnpm test:schema:bootstrap` → PASS（独立复跑）
- `pnpm smoke:web` → PASS（独立复跑）

## Debug-First Fixes Landed in This Signoff

- `tests/integration/control_plane/test_control_plane_postgres.py`：按 FK 依赖序重排 DROP（`rule_instance_overrides → alert_rules → instance_parameters → control_mysql_instances`）；`build_postgres_runtime` 调用点补注 `processlist_repository/slow_query_repository/tablespace_repository=InMemory...` 避免强制 ClickHouse 依赖。
- `gates/processes/test_background_processes_live.py`、`gates/alerting/test_alert_pipeline_postgres.py`、`gates/control_plane/test_control_plane_oracle_live.py`、`gates/recovery/test_recovery_paths_live.py`：同 FK 依赖序修复。
- `gates/schema/test_schema_bootstrap_live.py::_worker_settings`：补 `DB_MONITOR_POSTGRES_DSN`（child #1/#3/#4 加入后 `WorkerProcessSettings.postgres_dsn` 成为必填）。
- 34 个附带 biome/mypy 硬化修复已在独立 commit `5b149cb` 落地（JSX 合行、`int(str(raw_value))` 强类型转型等）。

## Close-Out Review

Epic 15 Slice 1 证明的内容：
- MySQL processlist 采集 + 安全 Kill（ADR-0005/0006）在 live 栈稳定；permission matrix `instances:action` 可独立控制。
- MySQL slow query 短窗抽采（ADR-0007）已接入 ClickHouse `mysql_slow_query_events`，API 支持 min_duration/user/schema/digest/时间筛选。
- Oracle tablespace 采集（ADR-0008）走专表 `oracle_tablespaces`，UI 覆盖 used_rate 排序 + 24h sparkline + 30d 全屏图。
- Per-instance threshold overrides（ADR-0004）落地 `rule_instance_overrides` 表 + rule-engine LEFT JOIN + UI 编辑面；rules.override.* 审计进链。
- 离线门禁（lint/typecheck/mypy/unit/readiness/background/schema/recovery/smoke）在新 schema 与新 UI 面下全部成立。

Epic 15 Slice 1 未证明的内容：
- 未做真实值班演练（留给 Epic 16 child #5）。
- 未做 tablespace 级告警（留给 Slice 2）。
- 未做系统连接/复制连接 Kill 保护扩面（Slice 5）。
- 未做 slow query 聚合与 digest 统计面板（Slice 5 的聚合方向）。

Epic 16 激活条件（按仓库 Epic Transition Protocol）：
- 本 Slice 1 的 hardening + schema + smoke 三项 signoff 全绿（已满足，见 Validation Log）。
- Epic 16 骨架已提前 materialize，只需将 SUBTASKS.csv `#1` 从 PENDING 翻到 IN_PROGRESS 即可开跑。

## Reference

- Epic 15 EPIC.md Close-Out Review 模板
- ADR-0003（Epic 15 signoff 判据 = 离线 gate + smoke，**不**含真实演练）

## Notes

- 本次 signoff 发现并修复的 FK drop-order bug 曾在 child #4 报告中预警，此次由 child #6 端到端闭合。
