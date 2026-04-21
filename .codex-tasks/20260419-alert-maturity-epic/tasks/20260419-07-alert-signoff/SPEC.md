# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 汇总 Epic 03 的 root-level signoff gates
- 形成可复现的 alert maturity 验证入口与运行说明
- 用统一门禁证明告警工作流在 backend、web 与 live gate 上收口

## Non-Goals

- 不在本任务中继续扩范围做额外功能
- 不用手工描述替代可执行 gate

## Constraints

- signoff 必须覆盖 backend、web 和 live alert evidence
- 只有当前 epic 相关门禁可复现时，才允许标记完成
- 任何门禁缺失都必须显式暴露，而不是跳过

## Deliverables

- root signoff script
- signoff contract tests
- runbook or checklist updates for alert maturity

## Final Validation Command

```bash
powershell -ExecutionPolicy Bypass -File ./scripts/test-alert-maturity-signoff.ps1
```
