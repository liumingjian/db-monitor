# Epic Specification

## Goal

- 把当前 Oracle “detail 已最小可见、overview 与更深诊断仍 MySQL-first”的产品断层推进到一个真实的 engine-aware fleet overview 与 diagnostics baseline，同时不回退 Epic 07 已稳定的 data-plane 与现有 MySQL 主链

## Why This Epic Is Next

- Epic 07 已证明 Oracle 最小 data-plane 成立，因此当前主误差已不再是“Oracle 能否采集/查询/展示最小趋势”，而是“fleet-level 产品语义是否仍停留在 MySQL-only 假设”
- 当前仓库 truth 仍显式保留以下 gap：
  - `OverviewResponse` / `OverviewInstanceResponse` 还没有 `engine` 维度
  - `apps/web/src/monitoring-ui.ts` 与 `apps/web/app/instances/page.tsx` 仍明确写着 overview semantics 与 deeper diagnostics remain `MySQL-first`
  - overview leaders / capacity insights / presets 仍主要围绕 MySQL replication lag、buffer-pool pressure 和 throughput 语义组织
- 相比之下，multi-engine alerting 仍牵动更重的共享契约面，更适合作为下一阶段的 conditional follow-up

## Scope

- 冻结 engine-aware overview contract baseline，包括 overview instance metadata、fleet summary 与 diagnostics boundary
- 在 analytics service / API contract 中实现 mixed-engine overview aggregation，而不是继续只对 MySQL 自洽
- 让 web overview surface、leaders、capacity insight 与 preset semantics 停止把已支持的 Oracle 数据面表述成隐式 MySQL-only
- 暴露更深但克制的 engine-aware diagnostics baseline，不伪装成 full parity
- 为本 epic 形成 root signoff 与 live Oracle coverage 证据链

## Non-Goals

- 不在本 epic 中完成 multi-engine alerting / rule semantics parity
- 不追求 Lepus 级别的 Oracle 全量 overview 报表或 deep-dive 诊断
- 不把 engine-aware overview 做成通用 BI 平台
- 不回退 Epic 07 已关闭的 Oracle data-plane 与 MySQL/governance 主链

## Done-When

- overview payload 与 web surface 能诚实承载 mixed-engine fleet state，而不是继续把 Oracle 支持面限制在 detail-only 路径
- mixed-engine fleet overview 的 leaders / insight / preset semantics 不再显式写成 `MySQL-first`
- MySQL detail、alerting 与 root smoke 主链未因 overview 扩展发生回退

## Close-Out Review

- Epic 07 证明了什么：
  - Oracle 已不再停留在 validation-only，而是拥有最小真实 `collector -> schema -> analytics -> web detail -> signoff` 闭环
  - 当前 macOS + Docker 环境可继续执行 Oracle live gate
  - MySQL 主路径与 Oracle 第二引擎最小 data-plane 能在同一轮 signoff 中同时成立
- Epic 07 没证明什么：
  - fleet overview contract 是否已经真正摆脱 MySQL-only 假设
  - overview leaders / diagnostics / presets 是否能诚实承载 mixed-engine fleet
  - rule / alert semantics 是否已经准备好承载第二引擎
- 默认下一个 epic：
  - `Epic 08: Engine-Aware Overview and Fleet Diagnostics`
- 为什么是它：
  - 当前仓库中最显式的剩余主误差正是 overview 与 deeper diagnostics 仍然 `MySQL-first`
  - 这比 multi-engine alerting 更接近 Epic 07 刚完成的能力边界，也更适合做最小连续扩展
- 什么证据才会支持直接跳到别的方向：
  - 如果新的 signoff 或真实运行证据表明当前主阻塞已经转向 rule / alert semantics，才会考虑直接进入 multi-engine alerting
  - 如果 runtime / release / governance 重新出现强于 overview 的回退信号，则应先回到对应层面处理

## Child Deliverables

- 完成 post-Epic-07 roadmap extension 与新 epic activation 收口
- 冻结 engine-aware overview contract baseline
- 实现 mixed-engine overview aggregation 与 analytics API
- 实现 web overview surface 与 fleet messaging 的 engine-aware 收敛
- 深化 diagnostics 与 preset semantics 的 engine-aware baseline
- 运行 root signoff 与 live Oracle coverage

## Dependency Notes

- 子任务 `#1` 负责完成 post-Epic-07 roadmap extension 与 epic activation 收口
- 子任务 `#2` 是后续 analytics / web / signoff 的 contract baseline
- 子任务 `#3` 依赖 `#2`
- 子任务 `#4` 依赖 `#2;#3`
- 子任务 `#5` 依赖 `#3;#4`
- 子任务 `#6` 依赖 `#3;#4;#5`

## Child Task Types

- `single-full`
