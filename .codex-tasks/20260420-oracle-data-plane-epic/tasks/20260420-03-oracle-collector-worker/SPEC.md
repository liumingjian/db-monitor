# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让 validated Oracle instance 进入真实 collector / worker / sink 闭环
- 基于最小批准指标集写入 Oracle telemetry，而不是继续只做 validation

## Non-Goals

- 不追求 Oracle 全量采集
- 不在本任务中完成 analytics UI

## Final Validation Command

```bash
uv run pytest tests/scheduler tests/worker_mysql tests/worker_oracle tests/integration/metrics_pipeline \
  && pnpm test:control-plane:oracle
```
