# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 把 scheduler / collection / pipeline dispatch seam 从 mysql-only 推到 engine-aware

## Final Validation Command

```bash
uv run pytest tests/scheduler tests/integration/metrics_pipeline tests/worker_mysql
```
