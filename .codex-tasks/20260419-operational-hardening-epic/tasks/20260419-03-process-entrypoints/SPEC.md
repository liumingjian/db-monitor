# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为 scheduler 和 MySQL worker 建立真实可运行的进程入口
- 让进程显式暴露空闲、处理成功和失败状态，而不是停留在打印应用名
- 建立最小轮询节奏、停止语义和失败暴露协议

## Non-Goals

- 不在本任务中实现复杂 supervisor 或分布式协调
- 不把失败吞掉伪装成稳定运行

## Constraints

- 入口必须复用现有 scheduler / queue / worker / sink 领域逻辑
- 失败必须显式可见，退出码或日志不得伪成功
- 轮询节奏必须可配置，且避免空转打满 CPU

## Deliverables

- scheduler process 配置与主循环
- worker process 配置与主循环
- 可测试的 run-once / loop 协议
- 对应测试和 live/background gate
- 与现有 metrics live gate 的协同验证

## Final Validation Command

```bash
uv run pytest tests/operations/processes && powershell -ExecutionPolicy Bypass -File ./scripts/test-background-processes.ps1 && powershell -ExecutionPolicy Bypass -File ./scripts/test-metrics-pipeline-live.ps1
```
