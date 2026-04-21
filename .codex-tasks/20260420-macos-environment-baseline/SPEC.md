# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 将当前仓库需要的开发 / gate / smoke / live 验证入口改为可在 macOS 上直接执行
- 保持现有 `pnpm` 根级命令、runbook 与 epic gate 语义稳定
- 为后续 epic 开发建立可复用的 macOS 本地环境基线

## Non-Goals

- 不在本任务中扩展新的产品功能
- 不重写无关业务逻辑
- 不为了跨平台而删掉现有 live gate

## Constraints

- 必须优先适配当前真实会用到的环境脚本、signoff、smoke 和 live gate
- 不能把现有根级命令改成需要用户手工拼命令
- 任何无法在 macOS 直接运行的入口都必须显式暴露或修复，不能靠文档备注掩盖

## Deliverables

- macOS 可执行的根级环境 / gate / smoke 脚本入口
- 相应的 package script、测试与文档更新
- 通过至少一条运维 hardening gate 和一条 alert maturity gate 的 macOS 验证证据

## Final Validation Command

```bash
pnpm test:hardening:signoff && pnpm test:alert-maturity:signoff
```
