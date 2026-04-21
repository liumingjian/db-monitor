# Epic Specification

## Goal

- 在不破坏当前 MySQL-first 主链的前提下，把 analytics 从“基础趋势可看”推进到“可切窗口、可看更深指标、可感知容量风险、可沉淀稳定视图”

## Why This Epic Is Next

- Epic 02 已证明 runtime、schema、recovery 和 release gate 成立
- Epic 03 已证明 alert lifecycle、noise control、triage 和 notifier workflow 已收口
- 当前最大的真实缺口已经从“系统能否跑稳/告警是否可值班”转移到“analytics 深度和容量判断能力仍然偏浅”

## Scope

- 概览与实例详情的时间窗口切换
- 更丰富的 MySQL 趋势与引擎健康指标
- 面向容量风险的 summary / ranking / risk signals
- 稳定可回放的 analytics 视图预设基线
- 本 epic 的 root signoff gate

## Non-Goals

- 不扩展多引擎
- 不引入通用 BI 平台能力
- 不把 saved views 演化成复杂共享协作系统

## Done-When

- 用户不仅能看到基础趋势，还能回答“更长窗口下负载怎么变化”“哪些实例更接近容量风险”“如何稳定回到同一种分析视图”

## Close-Out Review

- Epic 03 证明了什么：
  - 告警生命周期、抑制、ack/owner/note、delivery suppression 和 triage surface 已具备持续值班语义
  - 根级 alert maturity signoff 与 live PostgreSQL / recovery gate 已可复现
- Epic 03 没证明什么：
  - analytics 是否足够深
  - 容量趋势与风险判断是否成立
  - 用户能否稳定回到特定分析视图
- 默认下一个 epic：
  - `Epic 04: Analytics and Capacity Insight Expansion`
- 为什么是它：
  - 当前 roadmap 中，只有它直接对应“分析深度、趋势洞察、容量判断”这组剩余主误差
- 什么证据才足以跳到别的 epic：
  - 如果当前真实阻塞变成多引擎抽象失真，才会考虑 Epic 05
  - 如果业务突然转向组织/租户治理，才会考虑 Epic 06
