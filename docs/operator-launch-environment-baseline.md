# Operator Launch Environment Baseline

## Scope

这份文档把 Epic 13 的 internal single-environment launch 环境合同固化为显式表格。
目标不是描述所有未来环境，而是说明当前仓库要通过 root signoff 时，operator
必须准备哪些变量、端口和外部依赖。

## Runtime Variables

| 变量 | 是否必需 | 当前用途 | 说明 |
| --- | --- | --- | --- |
| `DB_MONITOR_RUNTIME` | 是 | API runtime | 当前批准值为 `postgres` |
| `DB_MONITOR_POSTGRES_DSN` | 是 | API / schema / recovery / process gates | 控制面 PostgreSQL DSN |
| `DB_MONITOR_REDIS_URL` | 是 | scheduler / worker / recovery gates | 调度与队列 Redis URL |
| `DB_MONITOR_CLICKHOUSE_DATABASE` | 是 | analytics / schema / process gates | ClickHouse database |
| `DB_MONITOR_CLICKHOUSE_ENDPOINT` | 是 | analytics / schema / process gates | ClickHouse endpoint |
| `DB_MONITOR_CLICKHOUSE_USERNAME` | 是 | analytics / schema / process gates | ClickHouse 用户名 |
| `DB_MONITOR_CLICKHOUSE_PASSWORD` | 是 | analytics / schema / process gates | ClickHouse 密码，必须通过环境注入 |
| `DB_MONITOR_API_BASE_URL` | 条件必需 | web smoke | 由 repo-local smoke runner 注入，通常不手工设置 |

## Oracle Variables

只有当当前上线窗口需要维持 Oracle 支持基线时，才要求以下变量处于可用状态：

| 变量 | 当前用途 | 说明 |
| --- | --- | --- |
| `DB_MONITOR_ORACLE_SQLPLUS_DOCKER_CONTAINER` | Oracle sqlplus fallback | 指向可用的 Oracle 容器 |
| `DB_MONITOR_ORACLE_TEST_HOST` | Oracle live gate | 通常为 `127.0.0.1` |
| `DB_MONITOR_ORACLE_TEST_PORT` | Oracle live gate | 当前本地基线为 `15211` |
| `DB_MONITOR_ORACLE_TEST_SERVICE` | Oracle live gate | 当前本地基线为 `XE` |
| `DB_MONITOR_ORACLE_TEST_USERNAME` | Oracle live gate | 当前本地基线为 `system` |
| `DB_MONITOR_ORACLE_TEST_PASSWORD` | Oracle live gate | 必须通过环境注入，不得写入源码 |

## Port Contract

| 端口 | 用途 | 何时需要 |
| --- | --- | --- |
| `38100` | smoke API | `pnpm smoke` / `pnpm test:hardening:signoff` |
| `38101` | smoke web | `pnpm smoke` / `pnpm test:hardening:signoff` |
| `5432` | PostgreSQL | hardening / launch signoff |
| `6379` | Redis | background / recovery / metrics pipeline gates |
| `8123` | ClickHouse HTTP | analytics / schema / process gates |
| `3306` | MySQL probe path | release baseline 中的 MySQL runtime path |
| `15211` | Oracle XE | Oracle runtime signoff |

## Secret Handling

- `DB_MONITOR_CLICKHOUSE_PASSWORD` 与 `DB_MONITOR_ORACLE_TEST_PASSWORD` 必须通过环境注入，不得提交到源码。
- DSN、endpoint、容器名等可记录到 operator 运行记录中，但密码和明文 secret 不应进入 Git 跟踪文件。
- 若变量缺失，预期行为是 signoff 明确失败，而不是静默降级。

## Notes

- 当前基线服务于单环境、单租户的内部上线窗口。
- 若后续进入 HA / DR 或多环境 promotion，必须扩展新的 roadmap epic，而不是在当前文档里隐式扩 scope。
