# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为 dashboard、实例详情和趋势图实现稳定的分析查询 API
- 将 ClickHouse 指标查询与控制面元数据组合成面向 UI 的 REST/JSON 响应
- 提供可生成 OpenAPI 客户端的稳定响应模型

## Non-Goals

- 不负责采集指标
- 不将图表拼装逻辑塞进前端页面或原始 SQL 调用

## Constraints

- 查询 API 必须经由 `FastAPI` service/repository 边界输出
- 响应模型应直接服务 phase-one 的 overview、instance detail 和 core trend 场景
- 仅覆盖 PRD 中的核心 MySQL 指标，不扩展到高级分析报表
- 返回结果必须足够结构化，以便前端直接消费 ECharts

## Environment

- **Project root**: `C:\Users\14142\Desktop\ai-project\db-monitor`
- **Language/runtime**: `Python 3.12`
- **Package manager**: `uv`
- **Test framework**: `pytest`
- **Build command**: `uv run pytest`
- **Existing test count**: `0 planned`

## Risk Assessment

- [ ] 若查询 DTO 与前端场景不匹配，后续页面层会堆积转换逻辑
- [ ] 若时间窗口与聚合粒度约定不稳，趋势图与告警读取会不一致
- [ ] 若控制面元数据与指标查询耦合方式混乱，实例详情页会变脆弱

## Deliverables

- 概览与实例趋势分析 service/repository
- chart-ready API DTO 与 OpenAPI 模型
- overview、instance detail、replication/core metric 查询接口
- 分析查询自动化测试

## Done-When

- [ ] 概览和实例详情 API 可直接支撑 phase-one UI
- [ ] 查询服务对控制面元数据和 ClickHouse 指标边界清晰
- [ ] OpenAPI 模型稳定，适合生成类型化客户端

## Final Validation Command

```bash
uv run pytest tests/api/analytics tests/integration/analytics_queries
```

## Demo Flow

1. 读取 overview 概览数据
2. 读取某个实例的时间序列趋势
3. 用同一组 API 驱动 ECharts 图表和摘要卡片

