# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为组织与成员关系建立 Postgres schema / bootstrap / verify 基线

## Final Validation Command

```bash
uv run pytest tests/schema/test_schema_bootstrap.py tests/api/runtime/test_runtime_settings.py tests/integration/control_plane/test_control_plane_postgres.py
```
