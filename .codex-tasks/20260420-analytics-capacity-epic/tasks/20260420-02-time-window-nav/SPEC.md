# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 打通 overview / instance detail 的 approved time window 切换
- 让 web 不再硬编码 `1h`
- 保持当前 analytics API 与缓存键语义稳定

## Non-Goals

- 本任务不新增更深 metrics
- 本任务不做 saved presets

## Final Validation Command

```bash
uv run pytest tests/api/analytics tests/integration/analytics_queries && pnpm --filter web test && pnpm --filter web typecheck && pnpm --filter web build
```
