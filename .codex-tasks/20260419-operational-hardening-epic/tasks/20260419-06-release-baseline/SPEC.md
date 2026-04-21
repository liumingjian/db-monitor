# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 建立 operator 可执行的发布、启动、检查和回滚基线
- 把当前 root gates 转化为可操作的 release baseline
- 降低“只有作者知道怎么跑起来”的风险

## Non-Goals

- 不建设完整 CI/CD 平台
- 不扩展新的业务能力

## Constraints

- 运行步骤必须短、显式、可复现
- 回滚条件必须明确，而不是留给口头经验
- 发布基线必须以当前真实 gates 为准

## Deliverables

- operator runbook baseline
- release checklist
- rollback checklist
- ops tests

## Final Validation Command

```bash
pnpm smoke && uv run pytest tests/ops
```
