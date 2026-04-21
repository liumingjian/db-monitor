# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让 API 从默认本地内存启动提升为可配置的正式运行时
- 为 API 增加 live / ready 探针，显式暴露 PostgreSQL 与 ClickHouse 依赖状态
- 建立一个 live gate，证明正式运行时在本地依赖环境中可以启动并通过就绪检查

## Non-Goals

- 不在本任务中实现 scheduler / worker 的长期运行循环
- 不引入新的业务接口或页面

## Constraints

- 默认开发体验不能退化：未配置正式运行时环境时，`db_monitor_api.main` 仍应可本地导出 OpenAPI
- 正式运行时不得再偷偷回退到 in-memory analytics repository
- readiness 失败必须显式返回失败状态，不允许假绿

## Deliverables

- API 运行时配置加载器
- PostgreSQL / ClickHouse 依赖探针
- `/health/live` 与 `/health/ready` 路由
- live readiness gate 脚本和测试

## Final Validation Command

```bash
uv run pytest tests/api/health tests/api/runtime && powershell -ExecutionPolicy Bypass -File ./scripts/test-api-runtime-readiness.ps1
```
