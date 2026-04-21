# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为 PostgreSQL 与 ClickHouse 建立显式 schema bootstrap 与 version baseline
- 消除“运行时首次写入顺手建表”的隐式 schema 行为
- 让 schema drift 可以被检测、验证和恢复

## Non-Goals

- 不做复杂迁移框架扩展
- 不在 schema 仍不稳定时引入多版本兼容胶水

## Constraints

- schema 初始化必须显式可执行
- 版本信息必须可读取、可验证、可失败
- 不允许隐藏式 `CREATE TABLE IF NOT EXISTS` 成为唯一生产建模路径

## Deliverables

- PostgreSQL bootstrap contract
- ClickHouse bootstrap contract
- schema version baseline
- schema live gate

## Final Validation Command

```bash
uv run pytest tests/schema && powershell -ExecutionPolicy Bypass -File ./scripts/test-schema-bootstrap.ps1
```
