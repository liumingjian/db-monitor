# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 实现 MySQL 资产接入和控制面核心资源 API
- 提供实例创建、连接校验、列表、详情和基础系统设置能力
- 让后续 worker、dashboard、rules 都消费统一的控制面模型

## Non-Goals

- 不实现指标采集、告警评估或前端页面
- 不兼容 Lepus 的 `db_servers_*` 表结构

## Constraints

- 控制数据必须落在 `PostgreSQL`
- API 必须经过认证和 RBAC 保护
- 资产接入流程必须显式验证连接，不允许“保存但未知是否可用”
- 连接配置与实例元数据要能被 scheduler/worker 稳定消费

## Environment

- **Project root**: `C:\Users\14142\Desktop\ai-project\db-monitor`
- **Language/runtime**: `Python 3.12`
- **Package manager**: `uv`
- **Test framework**: `pytest`
- **Build command**: `uv run pytest`
- **Existing test count**: `0 planned`

## Risk Assessment

- [ ] 资产模型若过度贴近旧系统，会重新带回耦合问题
- [ ] 连接校验若与持久化流程耦合不清，错误处理会混乱
- [ ] 系统设置若过早泛化，容易失控并挤占 phase-one 范围

## Deliverables

- 资产与数据源配置 domain/service/repository
- MySQL 实例接入与连接校验 API
- 实例列表与详情 API
- 基础系统设置 API 与审计记录

## Done-When

- [ ] 管理员可以创建并验证 MySQL 实例
- [ ] 实例列表与详情对后续 worker 和 UI 足够稳定
- [ ] 设置和资产写操作全部可审计

## Final Validation Command

```bash
uv run pytest tests/api/assets tests/integration/control_plane
```

## Demo Flow

1. 以管理员身份创建 MySQL 数据源
2. 触发连接校验并看到显式结果
3. 查看实例列表、详情和系统设置接口返回

