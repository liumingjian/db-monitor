# Epic Specification

## Goal

- 把当前 mixed-engine overview 从“baseline 已成立但 fleet metrics / leaders 仍带有 MySQL-only 假设”推进到一个诚实、可验证的 parity baseline

## Why This Epic Is Next

- post-Epic-10 close-out review 已证明：原始 PRD closeout 已经完成，当前主误差不再是 phase-one debt
- 当前 repo 的剩余 gap 集中在 overview parity，而不是新的 control-plane closeout：
  - `apps/api/src/db_monitor_api/analytics/service.py` 仍把 `OVERVIEW_METRIC_ENGINES` 与 `OVERVIEW_INSTANCE_METRIC_ENGINES` 限定为 `mysql`
  - overview cards / charts 仍主要围绕 MySQL throughput、threads、buffer-pool 和 replication lag 语义组织
  - `apps/web/src/monitoring-ui.ts` 与相关页面 copy 仍明确把 mixed-engine overview 呈现为 `Mixed-engine baseline`
- 相比之下，Oracle runtime reliability 更偏 phase-two 之后的 live-evidence hardening；在产品 contract gap 仍显式存在时，不应先于本 epic 激活

## Scope

- 冻结 fleet metric parity contract baseline，包括 overview metric families、coverage semantics 与 signal leader boundary
- 在 analytics service / API contract 中实现 mixed-engine overview cards / charts 的最小 parity
- 让 web overview surface、capability boundary、coverage readout 与 fleet messaging 停止把 mixed-engine fleet 固定在 baseline-only 文案里
- 收敛 diagnostics、signal leaders 与 preset semantics，使其与新的 mixed-engine parity 面一致
- 为本 epic 形成 targeted signoff 与 Oracle live coverage 证据链

## Non-Goals

- 不追求 Oracle 全量产品 parity 或通用 BI 报表
- 不重写 alerting、auth、control-plane、organization 或 runtime family
- 不引入第三引擎
- 不把“指标能展示”偷换成“所有引擎语义完全等价”

## Done-When

- overview payload 与 web surface 不再把 Oracle 只放在 health / detail baseline 上，而是能诚实承载最小 fleet parity
- mixed-engine fleet overview 的 cards / charts / signal leaders 不再显式停留在 `mysql-only` 假设
- MySQL overview 主链、Oracle detail 主链和现有 signoff 门禁未因 parity 扩展发生回退

## Project Control Topology

- 总体设计部:
  - 本 epic 以 `EPIC_ROADMAP.md`、`docs/prd-closeout.md`、Epic 10 truth artifacts 为参考输入，禁止借 parity 顺手扩成新报表或第三引擎
- 主落点:
  - 数据面
- 次级影响面:
  - 控制面：coverage boundary、capability messaging 与 signoff 口径会随 parity 收敛而调整
  - 状态面：无新的 schema 目标，但 API contract 与 typed client 属于共享事实源
- 冻结边界:
  - 不修改 alerting rule semantics
  - 不扩展 control-plane / auth / organization scope
  - 不改 scheduler / worker / notifier 的运行边界

## Complexity Transfer Ledger

| 字段 | 说明 |
| --- | --- |
| 复杂性原位置 | mixed-engine complexity 目前被压在 coverage boundary 文案、MySQL-only metric tuples 和页面解释里 |
| 新位置 | 本 epic 把复杂性显式转移到 engine-aware overview metric family、instance snapshot / leader semantics 与 web parity messaging |
| 收益 | mixed-engine fleet 不再需要靠“为什么还没 fully parity”的补充解释存活 |
| 新成本 | overview contract、preview fixtures 和 web model 的语义组合更复杂，需要更严格的 targeted gate |
| 失效模式 | 误把不同引擎的指标强行等价，或在 parity 过程中回退 MySQL 既有 overview 主链 |

## Control Contract

- Primary Setpoint:
  - 让 mixed-engine fleet overview 的 cards、charts、coverage boundary 和 signal leaders 进入“诚实可验证的 parity baseline”
- Acceptance:
  - `SUBTASKS.csv` 中所有 child 均 `DONE`
  - targeted analytics/web gate 通过
  - parity signoff 命令通过
- Guardrails:
  - 不回退 MySQL overview 与 Oracle detail 已有 contract
  - 不打坏 OpenAPI snapshot、typed client、web typecheck 与现有 analytics tests
  - 不伪装成 full parity 或跨引擎完全等价
- Sampling Plan:
  - 先冻结 contract baseline，再进入 analytics API parity，然后收敛 web parity / leaders / presets，最后做 signoff
- Known Delays / Delay Budget:
  - OpenAPI snapshot、web build 与 Oracle live gate 是主要时滞
- Recovery Target:
  - 任一 child 失败后，应能回退到前一稳定 contract，并在同一工作日内恢复到可验证状态
- Rollback Trigger:
  - 任一 child 导致 MySQL overview baseline 回退
  - 任一 child 让 UI 宣称了尚未支持的 parity 面
- Constraints:
  - 只允许触碰本 epic child 明确列出的 analytics、web、typed client、preview 与测试文件
- Boundary:
  - `apps/api/src/db_monitor_api/analytics`
  - `packages/api-client/src`
  - `apps/web/app/{overview,instances}`
  - `apps/web/src`
  - `tests/api/analytics`, `tests/integration/analytics_queries`, `apps/web/tests`
- Coupling Notes:
  - overview contract 会同时影响 API、typed client、preview fixtures、dashboard model 与 smoke copy
  - signal leader semantics 依赖 overview instance snapshot contract，不能只改 UI 不改 API
  - mixed-engine parity 与 Oracle runtime reliability 相关，但当前 epic 不负责解决 live-gate 稳定性本身
- Approximation Validity:
  - child #2 可以先用静态 seam + contract artifact 冻结边界
  - child #3 和 #4 必须通过 targeted backend/web gate
  - child #6 在离线 gate 之外，优先补一次 Oracle live coverage 证据
- Actuator Budget:
  - 本 epic 允许修改 analytics contract、typed client、web model / page、preview fixtures 与测试；不允许扩大到 schema / alerting / runtime infra
- Risks:
  - 不同引擎的指标族不完全同构，容易把“支持并列呈现”误做成“语义强行统一”
  - preview 与 smoke 文案如果不跟进，容易造成表面全绿但用户文案仍旧滞后

## Close-Out Review

- Epic 10 证明了什么:
  - 原始 PRD phase-one 与 control-plane closeout 已完成
  - 后续继续开发前必须进入新的 roadmap extension，而不是继续补 debt
- Epic 10 没证明什么:
  - multi-engine fleet metrics 是否已经真正完成 parity
  - Oracle runtime live evidence 是否已经足够稳定可复用
- 默认下一个 epic:
  - `Epic 11: Multi-Engine Fleet Metric Parity and Overview Convergence`
- 为什么是它:
  - 这是当前最显式的产品 gap，且直接存在于 analytics service 与 web capability 文案中
  - 它比 Oracle runtime reliability 更接近当前用户可见误差，也更适合作为最小连续扩展
- 什么证据才会支持不直接走它:
  - 如果新的 live evidence 表明 Oracle runtime / live gate 已成为强于 product parity 的主误差，则应先进入 runtime reliability epic

## Child Deliverables

- 完成 post-Epic-10 review 与 active epic activation 收口
- 冻结 fleet metric parity contract baseline
- 实现 mixed-engine overview aggregation 与 analytics API parity
- 实现 web overview parity surface 与 fleet messaging 收敛
- 收敛 diagnostics、leaders 与 preset semantics
- 运行 root signoff 与 Oracle live coverage

## Dependency Notes

- 子任务 `#1` 负责完成 post-Epic-10 review 与 epic activation 收口
- 子任务 `#2` 是后续 analytics / web / signoff 的 contract baseline
- 子任务 `#3` 依赖 `#2`
- 子任务 `#4` 依赖 `#2;#3`
- 子任务 `#5` 依赖 `#3;#4`
- 子任务 `#6` 依赖 `#3;#4;#5`

## Child Task Types

- `single-full`
