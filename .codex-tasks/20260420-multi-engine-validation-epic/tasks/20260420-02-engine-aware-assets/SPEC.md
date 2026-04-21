# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 把控制面资产契约从 mysql-only 收敛到 engine-aware，同时保留当前 MySQL 兼容路径

## Final Validation Command

```bash
uv run pytest tests/api/assets tests/integration/control_plane && pnpm openapi:check && pnpm --filter web test && pnpm --filter web typecheck
```
