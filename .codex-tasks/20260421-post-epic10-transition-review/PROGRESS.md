# Progress

## Summary

- Task shape: single-full
- Goal: 完成 Epic 10 之后的正式 close-out review，并把下一阶段冻结到 Epic 11 planning materialization

## Recovery

- 任务: 关闭 Epic 10 之后，确认当前 roadmap 是否已经收敛到一个明确的默认下一步；如果是，则先停在 close-out review，不提前进入 Epic 11 实现
- 形态: single-full
- 进度: 3/3
- 当前: 已完成
- 文件: `.codex-tasks/20260421-post-epic10-transition-review/TODO.csv`
- 下一步: 如需继续推进，下一轮必须先进入 Epic 11 的 planning materialization，再允许开始实现

## Control Contract

- Primary Setpoint: 在不跳过 phase separation 的前提下，为 Epic 10 之后的继续开发给出一个严格符合 `AGENT.md` 的 phase-1 结论
- Acceptance: 本任务 `PROGRESS.md` 明确写出 Epic 10 close-out review、为什么 Epic 11 成为默认下一步、什么证据会阻止直接激活它，以及为什么当前下一步仍只是 planning materialization
- Guardrails: 不把 PRD closeout 说成多引擎 fleet parity；不把 close-out review 偷换成 Epic 11 产品实现；不在没有运行证据时把 Oracle runtime hardening 提前激活
- Sampling Plan: 先读 Epic 10 truth artifacts 与 `docs/prd-closeout.md`，再对照当前仓库中仍显式保留的 MySQL-only overview seams，最后冻结 transition gate
- Constraints: 当前 01-10 已全部 `Done`；但在 phase 2 物化前，11 仍不能直接开始实现

## Close-Out Review

- Epic 10 证明了什么：
  - 原始 `PRD.md` 的 phase-one 主线和最后一批 control-plane debt 已全部收口
  - 用户/角色管理、实例与告警筛选、审计持久化、TPS 与 detail readout 已有代码、测试和 signoff 证据
  - `docs/prd-closeout.md` 已把“主线 PRD 基本完成，下一步进入 roadmap extension”写成明确 truth
- Epic 10 没证明什么：
  - mixed-engine fleet overview 的 cards / charts / signal leaders 是否已经摆脱 MySQL-only 假设
  - Oracle 已有 detail analytics 是否已经真正汇入 fleet-level metric parity，而不是只停留在 coverage boundary 文案里
  - 离线 green 与真实 Oracle runtime/live gate 之间是否已经具备更稳定的复跑基线
- 当前显式 repo gap：
  - `apps/api/src/db_monitor_api/analytics/service.py` 仍把 `OVERVIEW_METRIC_ENGINES` 与 `OVERVIEW_INSTANCE_METRIC_ENGINES` 固定为 `mysql`
  - `apps/web/src/monitoring-ui.ts` 仍明确把 mixed-engine overview 呈现为 `Mixed-engine baseline` / `Metrics scoped`
  - `apps/web/app/instances/page.tsx` 与实例侧 capability copy 仍把 Oracle fleet semantics 表述为“health + trends available”，而不是 parity
- 为什么 Epic 11 现在是 default next：
  - PRD 主线差距已不再构成 blocker，当前主误差已从 closeout debt 转向 multi-engine fleet metric parity
  - 这个 gap 同时落在 analytics contract、typed client、dashboard model 和 fleet messaging 上，必须以完整 epic 收口
  - 相比之下，Oracle runtime reliability 更偏 follow-up 的 live-evidence hardening，只有当产品 contract gap 收口后仍然是主要风险，才应优先激活
- 什么证据会阻止直接进入 Epic 11：
  - 如果新的 signoff 或 live-gate 证据表明 Oracle runtime 已明显比 overview parity 更脆弱，导致“离线全绿但真实环境不可复用”成为主误差，应优先进入 `Oracle Runtime Reliability and Live-Gate Productionization`
  - 如果在当前代码树里已经不存在显式的 MySQL-only overview seam，则 Epic 11 的优先级应被重新审视

## Decision Gate

- 当前结论：
  - Epic 10 已正式关闭
  - Epic 11 `Multi-Engine Fleet Metric Parity and Overview Convergence` 现在成为默认下一步
  - 下一步是 Epic 11 planning materialization，不直接开始实现
- 当前结果：
  - 本轮只交付 post-Epic-10 close-out review truth source
  - 当前还没有创建 Epic 11 skeleton；phase 2 仍需单独执行，保持与 `AGENT.md` 的 phase separation 一致

## Validation

- `bash -lc "grep -q 'Close-Out Review' .codex-tasks/20260421-post-epic10-transition-review/PROGRESS.md && grep -q 'Epic 11' .codex-tasks/20260421-post-epic10-transition-review/PROGRESS.md && grep -q 'Oracle Runtime Reliability' .codex-tasks/20260421-post-epic10-transition-review/PROGRESS.md && grep -q 'OVERVIEW_METRIC_ENGINES' .codex-tasks/20260421-post-epic10-transition-review/PROGRESS.md"`
