# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 实现 `scheduler + Redis + worker-mysql` 的 agentless 指标采集链路
- 将核心 MySQL 指标归一化并写入 `ClickHouse`
- 给控制面和告警链路提供稳定的指标数据源

## Non-Goals

- 不覆盖多引擎 worker
- 不实现慢查询深度分析、Bigtable 扫描或备份监控

## Constraints

- 采集器只负责采集和写入，不得直接发送通知
- MySQL 指标范围必须限制在 PRD 已批准的高价值核心指标
- Redis 只用于任务分发，不承载业务真相
- 控制面状态回写必须显式设计，不得混入采集脚本的隐式副作用

## Environment

- **Project root**: `C:\Users\14142\Desktop\ai-project\db-monitor`
- **Language/runtime**: `Python 3.12`
- **Package manager**: `uv`
- **Test framework**: `pytest`
- **Build command**: `uv run pytest`
- **Existing test count**: `0 planned`

## Risk Assessment

- [ ] 指标命名和归一化模型若不稳定，会影响分析 API 和规则引擎
- [ ] MySQL 权限需求若没有明确最小集合，接入成功率会不稳定
- [ ] ClickHouse 写入模型若与查询模型脱节，后续分析侧会返工

## Deliverables

- scheduler 调度契约与任务分发逻辑
- Redis 任务载荷模型
- worker-mysql 采集器与指标归一化写入
- ClickHouse 时序/快照写入基础

## Done-When

- [ ] 调度到采集再到写入链路可以跑通
- [ ] 核心 MySQL 指标落库模型稳定
- [ ] worker 层有自动化测试覆盖失败暴露与正常路径

## Final Validation Command

```bash
uv run pytest tests/scheduler tests/worker_mysql tests/integration/metrics_pipeline
```

## Demo Flow

1. 从控制面读取已接入实例
2. 由 scheduler 投递采集任务到 Redis
3. worker-mysql 拉取任务、采集指标并写入 ClickHouse

