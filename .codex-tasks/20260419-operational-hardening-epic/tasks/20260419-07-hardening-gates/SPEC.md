# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 汇总 Epic 02 的 hardening gates，形成新的阶段签收入口
- 确认运行时、后台进程、schema、恢复与 operator baseline 被统一验证

## Non-Goals

- 不新增业务功能
- 不用人工观察替代自动化签收

## Constraints

- 必须从仓库根目录可触发
- 必须覆盖本 epic 的核心风险面，而不是只重复 phase-one gate
- gate 失败时必须清晰暴露失败层级

## Deliverables

- root hardening gate command
- 子门禁聚合入口
- hardening signoff evidence

## Final Validation Command

```bash
powershell -ExecutionPolicy Bypass -File ./scripts/test-hardening-signoff.ps1
```
