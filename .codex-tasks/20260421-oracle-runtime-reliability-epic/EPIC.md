# Epic Specification

## Goal

- 把 Oracle runtime 与 live-gate 证据链从“当前环境可跑”推进到“可重复、可恢复、可交接”的运维基线

## Why This Epic Is Next

- post-Epic-11 close-out review 已证明：mixed-engine product contract 已完成，当前主误差不再是产品 surface
- 当前 repo 的剩余 gap 集中在 Oracle runtime repeatability，而不是新的产品功能：
  - `package.json` 只有 `test:control-plane:oracle`，但没有 root-level runtime doctor/signoff
  - `docs/` 还没有 Oracle runtime/live-gate operator baseline 与 rollback checklist
  - `scripts/powershell_shim.py` 与 `apps/api/src/db_monitor_api/control_plane/oracle_validation.py` 仍缺少 operator-friendly diagnostics / runtime hints

## Scope

- 冻结 Oracle runtime control contract baseline，包括前置条件、doctor/signoff 口径、失败隔离与恢复界面
- 让 root-level Oracle runtime doctor 与 live-gate diagnostics 成为正式入口
- 交付 operator baseline、checklists 与 rollback guidance
- 用 runtime contract / ops tests 和 signoff 证明这些入口可复用

## Non-Goals

- 不扩展新的产品 surface
- 不重写整体 release/deployment family
- 不引入第三引擎或新的 analytics/reporting scope
- 不把 runtime hardening 偷换成新的业务功能

## Done-When

- Oracle runtime / live-gate 有明确的 doctor、signoff、runbook、rollback 与 failure isolation 入口
- 团队知道何时必须跑 live gate、失败时如何恢复，以及哪些离线 green 不能替代真实 gate
- 现有 `pnpm test:control-plane:oracle` 与 Postgres control-plane regression 未因 runtime hardening 回退

## Project Control Topology

- 总体设计部:
  - 本 epic 以 `EPIC_ROADMAP.md`、Epic 11 truth artifacts 与 `.codex-tasks/20260420-oracle-live-gate/` 为参考输入，禁止借 runtime hardening 顺手扩成新的产品 phase
- 主落点:
  - 控制面
- 次级影响面:
  - 状态面：Postgres 与 Oracle 本地基础设施、compose 服务与 gate 入口保持一致
  - 数据面：无新的业务路径，但 control-plane validation 的运行时提示会影响用户可见错误细节
- 冻结边界:
  - 不修改 analytics / alerting / web 产品 contract
  - 不扩展多租户、组织治理与 auth scope
  - 不引入仓库外的手工恢复步骤

## Complexity Transfer Ledger

| 字段 | 说明 |
| --- | --- |
| 复杂性原位置 | 当前 Oracle runtime 复杂性压在临时环境知识、单条 live-gate 命令和 operator 口头记忆里 |
| 新位置 | 本 epic 把复杂性显式转移到 repo-local doctor/signoff 入口、runbook/checklists 与 diagnostics surface |
| 收益 | runtime evidence 可复用，失败时更快定位，不再依赖“碰巧这台机器跑过一次” |
| 新成本 | scripts/tests/docs 的维护面变宽，需要保持入口、文档和 gate 同步 |
| 失效模式 | doctor/signoff 与真实 gate 漂移，或 diagnostics 引入新的 silent fallback |

## Control Contract

- Primary Setpoint:
  - 让 Oracle runtime / live-gate 进入“可重复、可恢复、可交接”的运维基线
- Acceptance:
  - `SUBTASKS.csv` 中所有 child 均 `DONE`
  - doctor/signoff/runbook/checklist/rollback 资产已存在
  - runtime signoff 命令通过
- Guardrails:
  - 不回退 `pnpm test:control-plane:oracle` 与 `pnpm test:control-plane:postgres`
  - 不引入 fake success path 或 silent fallback
  - 不让文档、脚本、tests 三者失去同步
- Sampling Plan:
  - 先冻结 runtime contract baseline，再进入 doctor/diagnostics、operator baseline、contract tests，最后做 signoff
- Known Delays / Delay Budget:
  - Oracle XE 首次启动、健康检查与 live gate 仍是主要时滞
- Recovery Target:
  - 任一 runtime child 失败后，应能快速定位到依赖、容器、sqlplus、validator 或 Postgres gate 的具体阻塞点
- Rollback Trigger:
  - 任一 child 引入 fake green path
  - 任一 child 破坏现有 control-plane oracle/postgres gates
- Constraints:
  - 只允许触碰 runtime-related scripts、docs、tests、oracle validation hints 与 epic truth files
- Boundary:
  - `apps/api/src/db_monitor_api/control_plane/oracle_validation.py`
  - `scripts/`
  - `tests/api/control_plane`
  - `tests/ops`
  - `docs/`
  - `package.json`
- Coupling Notes:
  - runtime doctor 与 signoff 依赖同一组 compose/container/env assumptions
  - operator docs 必须和根级 package scripts 与 shim handlers 保持一致
  - control-plane validation hints 必须与真实 fallback 行为一致，不能编造不存在的恢复路径

## Close-Out Review

- Epic 11 证明了什么:
  - mixed-engine product contract 已闭环
  - Oracle live gate 可以在当前环境跑通
- Epic 11 没证明什么:
  - runtime evidence 是否可稳定复用
  - operator 是否知道何时重跑、失败时怎么恢复
- 默认下一个 epic:
  - `Epic 12: Oracle Runtime Reliability and Live-Gate Productionization`
- 为什么是它:
  - 当前主误差已从产品面转向 runtime confidence
  - 这是 roadmap 中最后一个已定义且仍未完成的方向

## Child Deliverables

- 完成 post-Epic-11 review 与 Epic 12 activation 收口
- 冻结 Oracle runtime control contract baseline
- 实现 Oracle runtime doctor 与 richer diagnostics
- 交付 operator baseline、checklists 与 root signoff
- 补齐 runtime contract / ops tests
- 运行 root signoff 并关闭 epic

## Dependency Notes

- 子任务 `#1` 负责完成 post-Epic-11 review 与 epic activation 收口
- 子任务 `#2` 是后续 runtime doctor/docs/tests/signoff 的 contract baseline
- 子任务 `#3` 依赖 `#2`
- 子任务 `#4` 依赖 `#2;#3`
- 子任务 `#5` 依赖 `#3;#4`
- 子任务 `#6` 依赖 `#3;#4;#5`

## Child Task Types

- `single-full`
