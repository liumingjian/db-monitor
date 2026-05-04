# Operator Prelaunch Rehearsal Runbook

## Scope

这份 runbook 用于 Epic 13 之后的目标环境试运行。
它的目标不是替代真实上线，而是在进入正式发布窗口前，用同一套 repo-local
contract 在目标机器上完成一次 rehearsal，并留下可审核的 go/no-go 证据。

## When To Use

- 已完成 [operator-release-baseline.md](./operator-release-baseline.md) 中的内部投产基线
- 准备把当前版本放到真实目标机器或预投产环境做一次完整试运行
- 需要决定这次窗口是继续走 launch baseline 小收口，还是已经暴露出 `Epic 14`
  级别的 scale / failure-domain 需求

## Inputs

| 字段 | 说明 |
| --- | --- |
| 目标环境标识 | 例如环境名、主机名或机房标识 |
| 执行人 | 当前 operator / owner |
| 仓库修订 | 当前 commit 或工作副本标识 |
| Oracle 支持范围 | 当前 root launch signoff 会串行包含 Oracle runtime signoff；若目标环境不能满足，必须先停止并升级 scope 决策 |
| 环境变量来源 | 例如 secret manager、shell profile、CI 注入或人工导入 |
| 回滚责任人 | 失败后谁负责执行 rollback checklist |

## Canonical Flow

1. 先填写 [operator-prelaunch-evidence-template.md](./operator-prelaunch-evidence-template.md) 的基础环境信息。
2. 按 [operator-launch-environment-baseline.md](./operator-launch-environment-baseline.md) 逐项确认变量、端口和 secrets。
3. 若目标环境不能满足 Oracle baseline，不要跳过 signoff：
   - 当前 `pnpm test:launch-readiness:signoff` 会强制包含 `pnpm test:oracle-runtime:signoff`
   - 这种情况下应先停止 rehearsal，并把范围问题升级为显式决策
4. 在目标机器上执行：
   - `pnpm test:launch-readiness:signoff`
5. 若本次 rehearsal 先用 repo-local Docker target stack 模拟目标环境：
   - 先按 [operator-docker-target-baseline.md](./operator-docker-target-baseline.md)
     执行 `pnpm docker:target:up`
   - 再执行 `pnpm test:docker-target:signoff`
6. 若命令失败，保留以下证据：
   - 最后一个失败命令
   - `.tmp-smoke-api.err.log`
   - `.tmp-smoke-web.err.log`
   - 当前缺失的环境变量、端口冲突或依赖状态
7. 若命令通过，继续做一次 operator go/no-go review：
   - gate 是否全部绿色
   - 是否存在手工恢复步骤
   - 是否出现容量、单点、恢复时间或故障域风险

## Evidence Capture

必须至少留下以下证据：

| 证据 | 要求 |
| --- | --- |
| 环境信息 | 目标环境、执行人、修订、时间戳 |
| 环境合同 | 变量、端口、依赖是否满足 |
| Gate 结果 | `hardening`、`oracle-runtime`、`launch-readiness` |
| 失败日志 | 若失败，保留 smoke / docker / signoff 输出 |
| 最终决定 | `GO`、`NO-GO` 或 `GO WITH FIXES` |

## Go / No-Go Rules

| 信号 | 结论 | 动作 |
| --- | --- | --- |
| `pnpm test:launch-readiness:signoff` 全绿，且没有未解释的运行异常 | `GO` | 进入正式发布窗口 |
| gate 失败，但问题仍局限在环境合同、依赖准备、日志或 rollback 口径 | `NO-GO` | 留在当前 launch baseline 范围修复 |
| gate 虽绿，但暴露出容量瓶颈、单点失效、备份恢复缺口、RTO/RPO 压力 | `NO-GO` | 不直接上线，整理证据并评估是否激活 `Epic 14` |
| 目标环境无法满足 Oracle baseline，而当前版本仍声称 mixed-engine 支持 | `NO-GO` | 停止发布并升级 scope 决策，不能静默跳过 Oracle signoff |

## Escalation Signals

以下信号说明问题已经不再只是 launch baseline 小收口，而可能需要 `Epic 14`：

- 单点失效会直接导致不可接受的停机
- 备份/恢复链路不存在，或无法满足明确的 RTO / RPO
- 负载、容量或故障域问题已经在 rehearsal 中真实出现
- operator 无法用当前 baseline 完成恢复，而需要新的系统级架构能力

## Related Assets

- [operator-release-baseline.md](./operator-release-baseline.md)
- [operator-launch-environment-baseline.md](./operator-launch-environment-baseline.md)
- [operator-launch-acceptance-checklist.md](./operator-launch-acceptance-checklist.md)
- [operator-docker-target-baseline.md](./operator-docker-target-baseline.md)
- [operator-prelaunch-evidence-template.md](./operator-prelaunch-evidence-template.md)
- [operator-rollback-checklist.md](./operator-rollback-checklist.md)
