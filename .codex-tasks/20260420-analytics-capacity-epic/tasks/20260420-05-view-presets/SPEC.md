# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 给 analytics 视图提供最小稳定预设，减少重复手动切换窗口和入口

## Final Validation Command

```bash
uv run pytest tests/api/analytics tests/api/assets && pnpm --filter web test && pnpm --filter web typecheck
```
