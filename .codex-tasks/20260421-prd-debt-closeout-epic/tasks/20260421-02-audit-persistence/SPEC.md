# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 把审计日志从运行时内存仓储推进到 PostgreSQL 持久化与最小查询面

## Non-Goals

- 不把审计系统扩成通用日志平台
- 不在本 task 中重写所有控制面写路径

## Final Validation Command

```bash
uv run pytest tests/api/auth tests/integration/control_plane/test_control_plane_postgres.py tests/schema/test_schema_bootstrap.py
```
