# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为 scheduler / worker / alert lifecycle 建立重试、幂等与恢复基线
- 让失败恢复路径具备显式证据，而不是依赖“再跑一次试试”
- 防止同一失败被静默放大成重复写入、重复通知或脏状态

## Non-Goals

- 不实现复杂分布式编排系统
- 不用 silent fallback 掩盖失败

## Constraints

- 恢复动作必须显式暴露状态变化
- 幂等边界必须与状态面事实源一致
- 退避与重试必须可配置、可测试、可失败

## Deliverables

- pipeline recovery contract
- alert lifecycle recovery contract
- retry/backoff/idempotency tests
- recovery live gate

## Final Validation Command

```bash
uv run pytest tests/recovery tests/integration && powershell -ExecutionPolicy Bypass -File ./scripts/test-recovery-paths.ps1
```
