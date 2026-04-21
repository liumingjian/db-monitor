# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 实现基础规则评估、告警事件和通知边界
- 将告警明确拆成规则定义、规则执行、告警记录、通知分发四个部分
- 为 alert list/detail 和规则管理页面提供稳定后端能力

## Non-Goals

- 不实现复杂规则 DSL
- 不把通知逻辑塞进 worker 或采集器

## Constraints

- 告警链路必须遵守 `collection -> rule evaluation -> notification`
- phase-one 只支持基础规则集
- 告警状态与历史必须落在控制面持久层，不依赖隐式内存状态
- 通知失败必须暴露，不允许假成功

## Environment

- **Project root**: `C:\Users\14142\Desktop\ai-project\db-monitor`
- **Language/runtime**: `Python 3.12`
- **Package manager**: `uv`
- **Test framework**: `pytest`
- **Build command**: `uv run pytest`
- **Existing test count**: `0 planned`

## Risk Assessment

- [ ] 规则定义若与指标归一化模型脱节，评估层会频繁返工
- [ ] 恢复、抑制和重复事件处理若没有显式状态机，告警历史会失真
- [ ] 通知边界若不明确，容易重新回到旧系统的耦合模式

## Deliverables

- 基础规则定义和持久化模型
- rule engine 评估服务
- 告警记录、历史与状态流转
- notifier 边界与最小可用通知实现

## Done-When

- [ ] 基础规则能在归一化指标上稳定评估
- [ ] 告警记录、恢复和历史路径可追踪
- [ ] 通知发送通过显式 notifier 边界调用

## Final Validation Command

```bash
uv run pytest tests/rule_engine tests/notifier tests/integration/alert_pipeline
```

## Demo Flow

1. 创建基础阈值规则
2. 由规则引擎消费归一化指标并产生告警事件
3. 查看告警记录并确认 notifier 被显式调用

