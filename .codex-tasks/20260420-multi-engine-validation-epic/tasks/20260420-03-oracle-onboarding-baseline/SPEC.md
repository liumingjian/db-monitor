# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为 Oracle 增加最小接入与校验基线，作为第二引擎试金石

## Final Validation Command

```bash
uv run pytest tests/api/assets tests/integration/control_plane && pnpm openapi:check
```
