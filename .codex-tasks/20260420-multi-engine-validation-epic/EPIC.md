# Epic Specification

## Goal

- 以 Oracle 作为第二引擎试金石，验证当前平台边界是否真的能从 `MySQL-first` 走向 `engine-aware`，且不回退已稳定的 MySQL 主链

## Why This Epic Is Next

- Epic 02 已证明 runtime、schema、recovery 和 release gate 成立
- Epic 03 已证明 alert lifecycle、noise control、triage 和 notifier workflow 已收口
- Epic 04 已证明 analytics depth、capacity semantics 和 route-backed presets 已稳定成立
- 当前 roadmap 中剩余的主误差已不再是“系统是否可用”，而是“当前抽象是否真的可以承载第二引擎”
- 仓库内已有足够证据把 Oracle 冻结成明确的第二引擎候选：
  - `legacy/lepus-v3.8` 中 Oracle 是清晰存在的历史能力面
  - `PRD.md` 把 Oracle 明确列为 phase-one 之后才进入的多引擎扩展对象

## Scope

- 显式冻结 Oracle 作为第二引擎试金石，并写清当前 MySQL-only 假设面
- 把控制面资产契约从 `MySQLInstance` 收敛到 engine-aware 资产模型，同时保留 MySQL 兼容路径
- 增加 Oracle 接入与验证基线，不追求一步到位的全量能力
- 把 scheduler / collection / pipeline contract 从 `mysql-only` 推到 `engine-aware dispatch`
- 在 web inventory / detail / onboarding 上暴露最小 engine-aware 语义
- 为本 epic 形成根级 signoff 证据链

## Non-Goals

- 不追求 Lepus 的 all-engine parity
- 不在本 epic 内完成 Oracle 的完整 analytics parity
- 不为了多引擎先引入租户、组织或复杂共享协作模型
- 不用“兼容层”掩盖真实抽象失真

## Done-When

- 团队可以明确回答“哪些平台边界已经 engine-aware，哪些仍必须维持 MySQL 特化”
- Oracle 作为第二引擎试金石具备最小可测试接入路径
- MySQL 主链的 control-plane、pipeline 和 web path 未被回归打坏

## Close-Out Review

- Epic 04 证明了什么：
  - analytics 已从基础趋势浏览推进到更深的 throughput / engine-health 观察
  - capacity semantics 与 preset baseline 已在现有 overview / detail 路径中稳定成立
  - root signoff 已通过 `openapi`、analytics Python suites、web gates、live ClickHouse 和 smoke
- Epic 04 没证明什么：
  - 控制面资产模型是否真的摆脱了 `MySQLInstance` 假设
  - scheduler / pipeline / rule / web contract 是否真的可以承载第二引擎
  - 当前抽象是在“未来可扩展”还是“只对 MySQL 看起来整洁”
- 默认下一个 epic：
  - `Epic 05: Multi-Engine Expansion and Abstraction Validation`
- 为什么是它：
  - 当前 roadmap 中，只有它直接对应“多引擎抽象是否真实成立”这一剩余主误差
  - `PRD.md` 和 `legacy/lepus-v3.8` 已给出 Oracle 作为第二引擎试金石的仓库证据，足以满足“明确第二引擎”的前置条件
- 什么证据才足以跳到别的 epic：
  - 如果产品方向突然转向组织/租户治理，才会考虑跳到 Epic 06
  - 如果 Oracle 目标在仓库与业务边界上都无法冻结，则应停在规划层而不是盲目进入实现
