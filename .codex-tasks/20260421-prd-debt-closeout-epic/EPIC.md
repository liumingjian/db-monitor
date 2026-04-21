# Epic Specification

## Goal

- 把 [docs/prd-closeout.md](../../../docs/prd-closeout.md) 中仍未补齐的原始 PRD 控制面欠账，收口成一轮有边界、可恢复、可验证的 closeout epic

## Why This Epic Is Next

- post-Epic-09 close-out review 已经证明：roadmap 01-09 的实现链路是完整的，当前主误差不再是“缺 phase-one 主链”
- 当前 repo 的 remaining gaps 集中在 control-plane completeness，而不是新的产品扩展方向
- 这些 gap 会同时触碰 API contract、typed client、web surface、schema/audit、RBAC 与 root signoff，需要一个完整 epic，而不是零散 patch

## Scope

- 补齐实例列表与告警列表筛选 contract、typed client、Web filter surface 与测试
- 把审计日志推进到 PostgreSQL 持久化与最小查询能力
- 补齐用户/角色管理的最小产品面
- 补齐实例详情中的 TPS 和角色/版本显式展示
- 通过 root signoff 证明 closeout 不回退现有主链

## Non-Goals

- 不新开 phase-two / phase-three 产品方向
- 不重写组织治理、多引擎告警或 engine-aware overview
- 不在本 epic 中扩展分页、复杂 IAM、报表系统或新的运营工作流

## Done-When

- [docs/prd-closeout.md](../../../docs/prd-closeout.md) 中列出的 remaining gaps 都有明确的代码、测试与 closeout 证据
- 原始 [PRD.md](../../../PRD.md) 的剩余 phase-one 控制面欠账不再需要额外解释“为什么还没做”
- repo-root gate 证明这轮 debt pass 没有回退既有 auth、control-plane、analytics、alerting 和 web 主链

## Project Control Topology

- 总体设计部:
  - 本 epic 以 `docs/prd-closeout.md`、`PRD.md`、`EPIC_ROADMAP.md` 为参考输入，禁止借 closeout 顺手扩 scope
- 主落点:
  - 控制面
- 次级影响面:
  - 状态面：审计持久化、用户/角色产品面可能引入新的 PostgreSQL 真相
  - 数据面：实例详情 readout 与筛选结果会影响用户可见主链
- 冻结边界:
  - 不修改 organization scope 语义
  - 不回退 multi-engine rule / overview contract
  - 不改变 scheduler / worker / notifier 运行边界

## Complexity Transfer Ledger

| 字段 | 说明 |
| --- | --- |
| 复杂性原位置 | 剩余 PRD 欠账目前分散在文档说明、页面 copy 和未产品化的 runtime seam 中 |
| 新位置 | 本 epic 把复杂性集中到显式 query contract、schema/audit contract、user-management contract 与 detail readout contract |
| 收益 | closeout 结束后，原始 PRD 与当前代码树不再需要持续做“额外解释” |
| 新成本 | API contract、web query surface、schema gate 与 signoff 组合更复杂，需要更严格验证 |
| 失效模式 | 为补洞顺手改穿已稳定的多引擎与组织治理边界，导致 closeout 反而制造新 drift |

## Control Contract

- Primary Setpoint:
  - 让原始 PRD 剩余的控制面欠账进入“可验证完成”状态，而不是继续停留在 closeout 文档说明层
- Acceptance:
  - `SUBTASKS.csv` 中所有 child 均 `DONE`
  - closeout signoff 命令通过
  - `docs/prd-closeout.md` 可被更新为“欠账已收口”而不是“仍有 remaining gaps”
- Guardrails:
  - 不回退现有 RBAC enforcement 与 organization scope
  - 不打坏 OpenAPI snapshot、typed client、web typecheck 与现有 API/集成测试
  - 不把审计或用户管理需求偷换成新的多租户/IAM scope
- Sampling Plan:
  - 先做最小 contract / surface 子任务，再进入 schema-sensitive 和 user-management 子任务，最后用 root signoff 收口
- Known Delays / Delay Budget:
  - OpenAPI snapshot、web typecheck、repo-root pytest 与 PostgreSQL-related gate 是主要时滞
- Recovery Target:
  - 任一 child 失败后，应能回退到前一稳定 contract，并在同一工作日内恢复到可验证状态
- Rollback Trigger:
  - 任一 child 导致现有 auth、organization、alerting 或 analytics 主链回退
  - 任一 schema 变更无法通过最小 bootstrap / contract gate
- Constraints:
  - 只允许触碰本 epic child 明确列出的 control-plane、auth、alerting、web、contract 与 schema 文件
- Boundary:
  - `apps/api/src/db_monitor_api/{auth,control_plane,alerting}`
  - `apps/api/src/db_monitor_schema`
  - `packages/api-client/src`
  - `apps/web/app/{instances,alerts,settings}`
  - `apps/web/src`
  - `tests/api/*`, `tests/integration/control_plane/*`, `apps/web/tests/*`
- Coupling Notes:
  - 用户/角色管理与审计持久化共享控制面 schema
  - 列表筛选会同时影响 router、typed client、server component 和 web tests
  - 实例 detail semantics 需要与 analytics contract 保持一致
- Approximation Validity:
  - list filter 子任务可以先用离线路由/typed client/web gate 证明 contract 正确
  - audit persistence、user-management 等 schema-sensitive 子任务仍需至少通过 PostgreSQL contract gate
- Actuator Budget:
  - 本 epic 允许修改代码、OpenAPI snapshot、typed client、schema/bootstrap 与 web tests；不允许扩大到新的 infra/process family
- Risks:
  - 用户管理与审计持久化会触碰共享 schema，需要严格 gate
  - 为 closeout 添加筛选面时，容易把 query surface 扩成 pagination/reporting
  - 实例 detail semantics 可能误把 analytics 边界重新扩大

## Close-Out Review

- Epic 09 证明了什么:
  - multi-engine alert / rule / notifier / workflow baseline 已完成
  - root signoff 已能同时覆盖 backend、web、smoke 与 Oracle live gate
- Epic 09 没证明什么:
  - 原始 PRD 的控制面欠账是否已全部产品化
  - 用户/角色管理、审计持久化、筛选面和 detail semantics 是否已经收口
- 默认下一个 epic:
  - `Epic 10: PRD Debt and Control-Plane Closeout`
- 为什么是它:
  - 这是当前唯一还需要额外 closeout 文档解释的主误差
  - 相比继续扩产品方向，它更接近 repo 当前的真实收口需求
- 什么证据才会支持不直接走它:
  - 如果 root signoff 或 live gate 表明 01-09 现有主链发生回退，则应先返回对应 epic 层级止血

## Child Deliverables

- 实现实例列表与告警列表筛选面
- 持久化审计日志并提供最小查询面
- 补齐用户/角色管理产品面
- 完成实例 detail semantics 收口
- 运行 PRD closeout signoff

## Dependency Notes

- 子任务 `#1` 是本 epic 的最小低风险入口，先关闭两个显式列表筛选 gap
- 子任务 `#2` 和 `#4` 只依赖总体边界，不依赖 `#1`
- 子任务 `#3` 依赖 `#2`，避免在审计仍是内存 runtime seam 时直接扩用户管理写路径
- 子任务 `#5` 依赖 `#1;#2;#3;#4`

## Child Task Types

- `single-full`
