# Progress

## Summary

- Task shape: single-full
- Goal: 完成 Epic 11 之后的正式 close-out review，并把下一阶段冻结到 Epic 12 planning materialization

## Recovery

- 任务: 关闭 Epic 11 之后，确认当前 roadmap 是否已经收敛到一个明确的默认下一步；如果是，则先停在 close-out review，不提前进入 Epic 12 实现
- 形态: single-full
- 进度: 3/3
- 当前: 已完成
- 文件: `.codex-tasks/20260421-post-epic11-transition-review/TODO.csv`
- 下一步: 如需继续推进，下一轮必须先进入 Epic 12 的 planning materialization，再允许开始实现

## Control Contract

- Primary Setpoint: 在不跳过 phase separation 的前提下，为 Epic 11 之后的继续开发给出一个严格符合 `AGENT.md` 的 phase-1 结论
- Acceptance: 本任务 `PROGRESS.md` 明确写出 Epic 11 close-out review、为什么 Epic 12 成为默认下一步、什么证据会阻止直接激活它，以及为什么当前下一步仍只是 planning materialization
- Guardrails: 不把 runtime repeatability 说成新的产品 surface；不把 close-out review 偷换成 Epic 12 实现；不在没有运行证据时发明新的 roadmap 方向
- Sampling Plan: 先读 Epic 11 truth artifacts 与 `EPIC_ROADMAP.md`，再对照当前仓库中仍显式保留的 Oracle runtime seam，最后冻结 transition gate
- Constraints: 当前 01-11 已全部 `Done`；但在 phase 2 物化前，12 仍不能直接开始实现

## Close-Out Review

- Epic 11 证明了什么：
  - mixed-engine fleet overview 的 cards / charts / instance metrics / signal leaders 已完成诚实、可验证的 parity 收口
  - repo-root signoff 已覆盖 backend、web、smoke、api-client typecheck 与 Oracle live gate
  - Google Fonts 构建漂移已被收口为本地 Fontsource 依赖，说明当前主误差已不再是 web/build contract
- Epic 11 没证明什么：
  - Oracle live gate 是否已经形成“可重复、可恢复、可交接”的 operator baseline
  - `pnpm test:control-plane:oracle` 的前置条件、失败隔离与恢复路径是否已经被制度化，而不是只在当前环境碰巧可用
  - Oracle 11g thin-mode 不兼容、sqlplus fallback、legacy container 复用与 compose fallback 之间的运行口径是否已经足够清晰
- 当前显式 repo gap：
  - `package.json` 只有 `test:control-plane:oracle`，但没有 Oracle runtime doctor/signoff 入口
  - `docs/` 下没有 Oracle runtime/live-gate operator baseline 与 checklist
  - `scripts/powershell_shim.py` 虽然能运行 Oracle live gate，但失败时不会输出面向 operator 的系统化诊断与恢复线索
  - `apps/api/src/db_monitor_api/control_plane/oracle_validation.py` 已有 sqlplus fallback，但当前 runtime hint 仍然偏实现级，不足以承担 operator baseline
- 为什么 Epic 12 现在是 default next：
  - 产品 contract 误差已收口，当前主误差转向“离线 green 与真实 Oracle runtime 复跑能力之间的差距”
  - 这个 gap 同时落在 gate 入口、运行脚本、文档/checklist、失败诊断与 contract tests 上，必须以完整 epic 收口
  - 它比继续扩产品面更接近当前真实风险，也符合 roadmap 中已冻结的 `Conditional Next` 判据
- 什么证据会阻止直接进入 Epic 12：
  - 如果仓库里已经存在明确的 Oracle runtime doctor/signoff 入口、operator baseline 文档和恢复路径，并且当前 signoff 证明它们可稳定复用，则 Epic 12 优先级应被重新审视
  - 如果新的 close-out review 发现比 runtime confidence 更强的 repo gap，则应先回到 roadmap 裁决，而不是机械激活 Epic 12

## Decision Gate

- 当前结论：
  - Epic 11 已正式关闭
  - Epic 12 `Oracle Runtime Reliability and Live-Gate Productionization` 现在成为默认下一步
  - 下一步是 Epic 12 planning materialization，不直接开始实现
- 当前结果：
  - 本轮只交付 post-Epic-11 close-out review truth source
  - 当前还没有创建 Epic 12 skeleton；phase 2 仍需单独执行，保持与 `AGENT.md` 的 phase separation 一致

## Validation

- `bash -lc "grep -q 'Close-Out Review' .codex-tasks/20260421-post-epic11-transition-review/PROGRESS.md && grep -q 'Epic 12' .codex-tasks/20260421-post-epic11-transition-review/PROGRESS.md && grep -q 'Oracle Runtime Reliability' .codex-tasks/20260421-post-epic11-transition-review/PROGRESS.md && grep -q 'test:control-plane:oracle' .codex-tasks/20260421-post-epic11-transition-review/PROGRESS.md"`
