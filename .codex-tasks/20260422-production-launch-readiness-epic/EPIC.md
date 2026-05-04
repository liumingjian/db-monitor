# Epic Specification

## Goal

- 把当前仓库从“功能与 Oracle runtime 已基本闭环”推进到“可面向内部单环境投产的正式 launch baseline”

## Why This Epic Is Next

- post-Epic-12 close-out review 已证明：当前主误差不再是产品 surface，也不再是 Oracle runtime repeatability
- 当前 repo 的剩余 gap 集中在投产闭环，而不是新增功能：
  - `docs/operator-release-baseline.md` 仍是最小 operator 发布说明，不是正式投产基线
  - `pnpm test:hardening:signoff` 本轮仍在 `pnpm lint` 处失败，说明当前 worktree 未满足仓库自己的 release gate
  - repo 内尚未收口 production deployment baseline / launch checklist / env contract / final signoff 家族
- 因此，这一轮应该优先解决“能否稳妥上线”，而不是继续扩产品面

## Scope

- 冻结 internal production launch control contract，包括上线目标、单环境边界、门禁口径与恢复期望
- 收敛 root-level release / hardening gates，让当前分支重新具备可发布资格
- 交付 production deployment baseline、operator checklist、rollback / acceptance 资产
- 补齐 launch config / secrets / ops signoff contract，并用 root signoff 证明这些入口可复用

## Non-Goals

- 不建设完整 CI/CD 平台
- 不直接进入 Kubernetes、Terraform、多环境 promotion 或复杂发布编排
- 不扩展新的产品 surface
- 不把 HA / DR / 多地域课题提前混入当前投产基线

## Done-When

- release / hardening / launch signoff 入口明确且可复用
- 内部单环境投产所需的 baseline、配置、checklist、rollback 与 acceptance 资产齐备
- 团队知道哪些门禁必须通过、哪些环境依赖必须满足、失败时如何恢复，以及哪些绿色结果仍不能替代真实 launch signoff

## Project Control Topology

- 总体设计部:
  - 本 epic 以 `EPIC_ROADMAP.md`、`docs/operator-release-baseline.md`、`docs/operator-oracle-runtime-baseline.md` 与 post-Epic-12 truth artifacts 为参考输入，禁止借 launch readiness 顺手扩成新的产品 phase 或 HA 平台
- 主落点:
  - 控制面
- 次级影响面:
  - 状态面：环境变量、部署依赖、发布门禁、operator checklist 与 rollback 资产会成为新的共享事实源
  - 数据面：不新增业务 surface，但 launch contract 会约束哪些运行路径必须在 signoff 中被覆盖
- 冻结边界:
  - 不修改产品 API / analytics / alerting 功能契约
  - 不引入仓库外的隐式手工步骤作为必须前提
  - 不把内部单环境投产偷换成云原生平台化建设

## Complexity Transfer Ledger

| 字段 | 说明 |
| --- | --- |
| 复杂性原位置 | 当前 launch 复杂性压在最小 operator 文档、脏 worktree、局部脚本和人工记忆里 |
| 新位置 | 本 epic 把复杂性显式转移到 repo-local release gates、deployment baseline、env contract 与 signoff truth files |
| 收益 | 投产条件与恢复动作可复用，减少“看起来能跑但不能发版”的假收敛 |
| 新成本 | docs / scripts / tests / env contract 的维护面变宽，需要持续保持一致 |
| 失效模式 | deployment baseline 与真实上线动作漂移，或为了过 gate 引入 silent fallback / fake green |

## Control Contract

- Primary Setpoint:
  - 让仓库进入“可面向内部单环境投产”的工程基线
- Acceptance:
  - `SUBTASKS.csv` 中所有 child 均 `DONE`
  - release gate、deployment baseline、launch config contract 与 final signoff 资产已存在且一致
  - 最终 launch readiness signoff 通过
- Guardrails:
  - 不引入 fake green path 或 silent degradation
  - 不把 dirty worktree 上的格式漂移解释成新的产品需求
  - 不让 docs、scripts、tests 与实际 signoff 口径失去同步
- Sampling Plan:
  - 先冻结 launch control contract baseline，再恢复 hardening gates，之后交付 deployment / config baseline，最后做 root signoff
- Known Delays / Delay Budget:
  - lint / test / build gates、环境依赖校验和 operator 文档收敛是主要时滞
- Recovery Target:
  - 任一 launch child 失败后，应能快速定位是 gate drift、配置缺失、部署基线不清、还是 signoff 口径不一致
- Rollback Trigger:
  - 任一 child 通过 silent fallback 伪造 green
  - 任一 child 回退 Oracle runtime signoff 或现有产品主链
- Constraints:
  - 只允许触碰 release / deployment / docs / tests / launch truth artifacts
- Boundary:
  - `package.json`
  - `scripts/`
  - `docs/`
  - `tests/ops`
  - `.codex-tasks/20260422-production-launch-readiness-epic/`
  - `EPIC_ROADMAP.md`
- Coupling Notes:
  - root hardening gate 与最终 launch signoff 必须围绕同一套 release assumptions
  - deployment baseline、env contract 与 operator checklist 必须和根级 scripts / docs / tests 保持一致
  - internal production target 仍然是单环境 / 单租户，不允许在本 epic 中被隐式改写

## Close-Out Review

- Epic 12 证明了什么:
  - Oracle runtime / live-gate 已具备 doctor、signoff、rollback 与 diagnostics family
  - 多引擎产品面已经不是当前最强阻塞
- Epic 12 没证明什么:
  - 当前分支是否满足 repo-root release / hardening gates
  - operator 是否拥有正式的 internal production deployment baseline
  - launch config / env / acceptance 是否已经收口为 repo-local contract
- 默认下一个 epic:
  - `Epic 13: Production Launch Readiness and Deployment Baseline`
- 为什么是它:
  - 当前误差中心已经从功能面切到 launch closure
  - 这是距离“能不能投产上线”最近的一次最小可验证变更

## Child Deliverables

- 完成 post-Epic-12 review 与 Epic 13 activation 收口
- 冻结 production launch control contract baseline
- 恢复 release / hardening gates
- 交付 internal production deployment baseline
- 补齐 launch config / secrets / ops signoff contract
- 运行 root launch readiness signoff 并关闭 epic

## Dependency Notes

- 子任务 `#1` 负责完成 post-Epic-12 review 与 epic activation 收口
- 子任务 `#2` 是后续 release gate / deployment baseline / signoff 的 contract baseline
- 子任务 `#3` 依赖 `#2`
- 子任务 `#4` 依赖 `#2;#3`
- 子任务 `#5` 依赖 `#3;#4`
- 子任务 `#6` 依赖 `#3;#4;#5`

## Child Task Types

- `single-full`
