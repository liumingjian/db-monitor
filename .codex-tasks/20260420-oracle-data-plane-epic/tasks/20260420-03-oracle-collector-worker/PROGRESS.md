# Progress

## Summary

- Task shape: single-full
- Goal: 建立 Oracle collector / worker 的最小真实闭环

## Recovery

- 任务: 已完成 Oracle collector / worker 最小真实闭环
- 形态: single-full
- 进度: 3/3
- 当前: 已完成
- 文件: `.codex-tasks/20260420-oracle-data-plane-epic/tasks/20260420-03-oracle-collector-worker/TODO.csv`
- 下一步: 切换到子任务 `#4 Expose minimal Oracle analytics API contract`

## Control Contract

- Primary Setpoint: validated Oracle instance 可以进入真实 collector / worker / sink 闭环，而不是继续停留在 validation-only
- Acceptance: Oracle 的最小指标集明确；worker path 能把这些指标写到当前 engine-aware telemetry state-plane；MySQL worker flow 不回归
- Guardrails: 不追求全量 Oracle parity；不把本地 sqlplus fallback 误包装成通用远端采集策略；不破坏现有 MySQL dispatch/worker 契约
- Sampling Plan: 先用 repo-local Oracle reference 冻结最小指标，再决定 query runner，然后补 worker tests 与 live proof
- Constraints: 当前 macOS 本地 Oracle 11g XE 已知 thin mode 不可用，因此 collector 需要显式考虑 python driver 与 repo-local sqlplus fallback 的边界

## Notes

- 已知 repo-local Oracle 指标候选来自 `lepus-v3.8/check_oracle.py` 与 `include/lepus_oracle.py`
- 当前最小候选集：
  - `oracle_server_available`
  - `oracle_sessions_total`
  - `oracle_sessions_active`
  - `oracle_session_waits`
  - `oracle_user_calls_total`
  - `oracle_physical_reads_total`
  - `oracle_uptime_seconds`
- 已完成的最小控制输入：
  - `PythonOracleMetricsCollector` 已支持 python driver 优先、repo-local sqlplus fallback 次之的采集策略
  - scheduler 现在会为 validated Oracle instance 入队
  - `EngineAwareMetricsWorker` 会按 `job.engine` 在 MySQL / Oracle worker 间分流
  - Oracle integration pipeline regression 已能证明 `scheduler -> queue -> worker -> sink` 闭环
- 本轮验证证据：
  - `uv run pytest tests/scheduler tests/worker_mysql tests/worker_oracle tests/integration/metrics_pipeline`
  - `pnpm test:control-plane:oracle`
