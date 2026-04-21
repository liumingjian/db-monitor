# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让控制面资产和系统设置显式挂到活动组织上下文

## Final Validation Command

```bash
uv run pytest tests/api/assets tests/integration/control_plane && pnpm openapi:check
```
