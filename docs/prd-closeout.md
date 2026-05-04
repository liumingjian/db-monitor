# PRD Closeout

## Purpose

这份文档用于回答一个具体问题：当前仓库离原始 [PRD.md](../PRD.md) 还有多远。

结论先写在前面：

- 原始 `PRD.md` 的 `MySQL-first phase one` 主链已经基本交付
- 当前仓库已经明显超出原始 PRD，进入了多引擎、组织治理和更深运维闭环阶段
- 原始 PRD 里最后一批 control-plane closeout 欠账，已经通过 `Epic 10: PRD Debt and Control-Plane Closeout` 收口完成
- 如果继续推进，下一步不再是补 phase-one 债，而是基于新的 repo gap 做后续 roadmap extension

## Status Summary

| 范围 | 当前状态 | 说明 |
|---|---|---|
| 原始 PRD 主链 | 基本完成 | 登录、RBAC enforcement、实例接入、采集链路、overview/detail、规则告警、设置页、工程门禁都已落地 |
| 原始 PRD 的运维/质量目标 | 已完成并超额 | 发布、恢复、schema、background process、smoke/signoff 已形成完整闭环 |
| 原始 PRD 之外的能力 | 已明显超出 | Oracle 第二引擎、engine-aware overview、multi-engine alerting、organization governance 已落地 |
| PRD closeout 欠账 | 已完成 | `Epic 10` 已把用户管理、筛选面、审计持久化和 detail semantics 一次性收口 |

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

## Closeout Results

下面这些项曾经是原始 PRD 最后剩余的 closeout 欠账；当前已经全部有代码、测试和 signoff 证据。

| Gap | 当前判断 | 为什么还算 gap |
|---|---|---|
| 用户/角色管理产品面 | 已完成 | `Epic 10 / child #3` 已补齐 admin-only 用户目录、角色目录、existing-user role update API、typed client 和 `/settings` 管理面 |
| 实例列表筛选 | 已完成 | `Epic 10 / child #1` 已为 `/control/instances`、typed client 和 `/instances` 页面补齐名称、环境、标签、状态筛选 |
| 告警列表筛选 | 已完成 | `Epic 10 / child #1` 已为 `/alerts`、typed client 和 `/alerts` 页面补齐状态、级别、时间、实例筛选 |
| 审计日志持久化与查询 | 已完成（最小产品面） | `Epic 10 / child #2` 已补齐 `audit_entries`、`PostgresAuditRepository` 和 admin-only `/auth/audit-entries`，关键控制面写路径已进入 PostgreSQL 审计真相 |
| TPS 指标显式交付 | 已完成 | `Epic 10 / child #4` 已为 MySQL detail cards 补齐 `mysql_transactions_per_second`，并补了对应的 metrics/analytics 测试链 |
| 实例角色/版本显式展示 | 已完成 | `Epic 10 / child #4` 已让 detail payload 和实例详情页显式展示 `server_role` / `server_version` readout |

## Current Closeout Track

当前 repo 已经完成了 `Epic 10: PRD Debt and Control-Plane Closeout`。

当前 closeout track 已无剩余目标；如果继续推进，需要回到新的 roadmap close-out / extension 流程。

## Bottom Line

当前仓库不是“离 `PRD.md` 还很远”，而是：

- `PRD.md` 主链已经大体完成
- 仓库实现已经超过原始 PRD 边界
- 原始 PRD 剩余的 control-plane closeout 欠账已经收口完成
- 后续新增工作应被视为新的 roadmap extension，而不是 phase-one debt 继续补洞
