# PRD Closeout

## Purpose

这份文档用于回答一个具体问题：当前仓库离原始 [PRD.md](../PRD.md) 还有多远。

结论先写在前面：

- 原始 `PRD.md` 的 `MySQL-first phase one` 主链已经基本交付
- 当前仓库已经明显超出原始 PRD，进入了多引擎、组织治理和更深运维闭环阶段
- 现在真正阻塞继续推进的，不是“phase one 主链还没做出来”，而是：
  - 原始 PRD 里仍有少数 control-plane 欠账没补齐
  - roadmap 01-09 已全部完成，继续开发前必须先做新的 roadmap extension

## Status Summary

| 范围 | 当前状态 | 说明 |
|---|---|---|
| 原始 PRD 主链 | 基本完成 | 登录、RBAC enforcement、实例接入、采集链路、overview/detail、规则告警、设置页、工程门禁都已落地 |
| 原始 PRD 的运维/质量目标 | 已完成并超额 | 发布、恢复、schema、background process、smoke/signoff 已形成完整闭环 |
| 原始 PRD 之外的能力 | 已明显超出 | Oracle 第二引擎、engine-aware overview、multi-engine alerting、organization governance 已落地 |
| 仍未补齐的 PRD 欠账 | 有，但属于补洞而非重做 | 主要集中在用户管理、筛选面、审计持久化、若干 detail semantics |

## What Is Complete

| PRD area | 当前判断 | 证据锚点 |
|---|---|---|
| Auth / session | 完成 | `apps/api/src/db_monitor_api/auth/`、`tests/api/auth/`、`.codex-tasks/20260419-mysql-phase1-epic/` |
| RBAC enforcement | 完成 | `apps/api/src/db_monitor_api/dependencies.py`、`tests/api/rbac/test_rbac.py` |
| MySQL instance onboarding | 完成 | `apps/api/src/db_monitor_api/control_plane/router.py`、`tests/api/assets/` |
| Validation on create / validate | 完成 | `tests/api/assets/test_assets_onboarding.py`、`tests/api/control_plane/test_oracle_validation.py` |
| Metrics pipeline | 完成 | `apps/scheduler/`、`apps/worker-mysql/`、`tests/integration/metrics_pipeline/` |
| Analytics overview / detail | 完成 | `apps/api/src/db_monitor_api/analytics/`、`apps/web/app/overview/page.tsx`、`apps/web/app/instances/[instanceId]/page.tsx` |
| Alert lifecycle / rule pipeline | 完成 | `apps/api/src/db_monitor_api/alerting/`、`tests/rule_engine/`、`tests/integration/alert_pipeline/` |
| Settings surface | 完成 | `apps/web/app/settings/page.tsx`、`tests/api/runtime/test_runtime_settings.py` |
| Quality gates / smoke | 完成 | `package.json` root scripts、`smoke/phase-one.spec.ts`、operator baselines |

## What Exceeds The Original PRD

原始 `PRD.md` 明确把以下内容放在 phase-one 之外，或者直接列为 out of scope；但当前仓库已经把它们做进来了。

| 超出项 | 当前状态 | 说明 |
|---|---|---|
| Oracle / second engine | 已完成最小可用闭环 | 已不再停留在 validation-only |
| Engine-aware overview | 已完成 | overview / diagnostics 已能诚实表达 mixed-engine fleet |
| Multi-engine alerting | 已完成 | rule / alert / notifier / workflow 已收口 |
| Organization governance | 已完成 | auth、control-plane、alerting、web 都已挂到 organization scope |
| Operational hardening | 已完成并形成 runbook | 发布、回滚、恢复、runtime readness 均有门禁与文档 |

## Remaining Gaps

下面这些项是我认为当前最值得被当作“原始 PRD closeout 欠账”的内容。

| Gap | 当前判断 | 为什么还算 gap |
|---|---|---|
| 用户/角色管理产品面 | 部分缺失 | 当前有 seed users、session、roles、permissions、RBAC enforcement，但没有完整的用户/角色管理 API 与 UI |
| 实例列表筛选 | 缺失 | `list_instances` 当前没有按名称、环境、标签、状态的显式过滤 contract，页面也没有筛选控件 |
| 告警列表筛选 | 缺失 | 当前 alert queue 是展示面，没有按状态、级别、时间、实例的明确筛选面 |
| 审计日志持久化与查询 | 部分缺失 | 当前有 audit hooks，但 runtime 仍以 `InMemoryAuditRepository` 为主，不是正式的 PostgreSQL audit 产品面 |
| TPS 指标显式交付 | 缺失 | 当前显式交付的是 QPS、网络、uptime、replication lag、buffer-pool / Oracle sessions 等，未看到独立 TPS contract |
| 实例角色/版本显式展示 | 部分缺失 | validation 中已有 server version，但详情页当前主要展示连接信息、validation status 和 trends，没有把“角色/版本”作为正式 readout 收口 |

## Suggested Next Move

当前 repo 不再适合继续沿用“原始 PRD 还没做完”的思路推进。更合适的后续动作只有两种：

1. 如果目标是收干净 phase-one：
   - 新开一个 `PRD debt / control-plane completeness` epic
   - 重点只做用户/角色管理、筛选面、审计持久化、剩余 MySQL detail semantics
2. 如果目标是继续做产品演进：
   - 先做 roadmap extension
   - 再从新的 product gap 出发选择下一个 active epic

## Bottom Line

当前仓库不是“离 `PRD.md` 还很远”，而是：

- `PRD.md` 主链已经大体完成
- 仓库实现已经超过原始 PRD 边界
- 剩余工作更像一次有边界的 closeout / debt pass，而不是 phase-one 继续从头铺功能
