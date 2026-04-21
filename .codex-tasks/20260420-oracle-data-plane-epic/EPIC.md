# Epic Specification

## Goal

- 把 Oracle 从当前“onboarding / validation only”的状态推进到“最小可采集、最小可查询、最小可呈现”的真实数据面闭环，同时不回退已稳定的 MySQL 与组织治理主链

## Why This Epic Is Next

- 现有 roadmap 01-06 已全部完成，继续开发前必须先基于真实 repo gap 扩展 roadmap
- Epic 05 与后续 Oracle live gate 已证明：
  - Oracle 作为第二引擎试金石已具备真实 control-plane onboarding / validation baseline
  - 当前本地 macOS 环境可以通过 Oracle XE 容器完成真实连通性 gate
- 但仓库 truth 仍显式保留以下主误差：
  - scheduler 只调度 MySQL
  - metric sink / schema / normalization 仍是 `mysql-only`
  - analytics API 与 web detail 仍只承载 MySQL telemetry

## Scope

- 冻结 engine-aware metric sample 与 ClickHouse 状态面基线
- 为 Oracle 增加最小 collector / worker / dispatch 闭环
- 在 analytics API 中暴露最小 Oracle instance trends，而不是继续只做 validation
- 在 web detail flow 中诚实呈现 Oracle 趋势与能力边界
- 为本 epic 形成根级 signoff 与 live gate 证据链

## Non-Goals

- 不追求 Lepus 级别的 Oracle 全量指标、表空间、慢查询或报表覆盖
- 不在本 epic 内完成 Oracle alerting parity 或 rule-engine 扩展
- 不把 overview fleet ranking、preset semantics 或 capacity copy 一次性做成全引擎统一
- 不为了 Oracle 扩展而回退当前 MySQL data-plane 的稳定性

## Done-When

- 已验证的 Oracle 实例可以进入真实采集路径，并把最小指标写入 ClickHouse
- analytics API 与 web detail 至少能对 Oracle 提供最小趋势读取，而不是停留在 validation-only
- MySQL 主链、组织治理主链和现有根级 gates 仍保持 green

## Close-Out Review

- Epic 06 证明了什么：
  - 组织身份、组织成员关系、控制面、告警和 web surface 已围绕同一个组织事实源收敛
  - 根级 signoff 已证明 governance 扩展没有打坏默认单组织主路径
- Epic 06 没证明什么：
  - 第二引擎是否已经具备真实 telemetry data-plane
  - engine-aware metric schema、collector contract 与 analytics/query 面是否真的成立
  - Oracle 是否还能继续只停留在 validation-only 而不造成产品边界失真
- 当前 stage 为什么不是别的方向：
  - runtime / release / recovery 在 Epic 02 已关
  - alert maturity、analytics depth、multi-engine validation、tenant governance 均已关
  - 当前 repo 中最明确、最持续暴露的剩余主误差就是 Oracle data-plane 缺口

## Child Deliverables

- 完成 post-Epic-06 close-out 收口，并把 Oracle data-plane epic 激活为新的 truth source
- 冻结 engine-aware metric sample / ClickHouse schema baseline
- 实现 Oracle collector 与 worker dispatch 的最小闭环
- 暴露最小 Oracle analytics API / typed contract
- 在 web detail flow 中暴露 Oracle trends 与真实能力边界
- 运行 Oracle data-plane signoff gates

## Dependency Notes

- 子任务 `#1` 负责完成 close-out review 与 epic 激活收口
- 子任务 `#2` 是后续 Oracle collector、analytics 与 web 的状态面基础
- 子任务 `#3` 依赖 `#2`
- 子任务 `#4` 依赖 `#2;#3`
- 子任务 `#5` 依赖 `#4`
- 子任务 `#6` 依赖 `#3;#4;#5`

## Child Task Types

- `single-full`
