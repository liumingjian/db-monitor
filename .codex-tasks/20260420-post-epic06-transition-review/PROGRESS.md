# Progress

## Summary

- Task shape: single-full
- Goal: 完成 Epic 06 之后的正式 transition review，并为 post-phase-one 的下一阶段建立可恢复的 epic 入口

## Recovery

- 任务: 关闭 Epic 06 之后，重新判断是否还存在默认 roadmap epic；如果没有，则先扩展 roadmap，再激活新的 epic
- 形态: single-full
- 进度: 3/3
- 当前: 已完成
- 文件: `.codex-tasks/20260420-post-epic06-transition-review/TODO.csv`
- 下一步: Oracle data-plane epic 已完整物化，当前可从 `.codex-tasks/20260420-oracle-data-plane-epic/` 继续执行

## Control Contract

- Primary Setpoint: 在不伪造“默认 next”的前提下，为 Epic 06 之后的继续开发提供一个基于真实 repo gap 的正式新 epic
- Acceptance: 本任务 `PROGRESS.md` 明确写出 Epic 06 close-out review、旧 roadmap 是否已耗尽、为什么选择新的下一阶段，以及新的 epic truth artifacts 已存在
- Guardrails: 不把已经 DONE 的旧 epic 重新激活；不把 Oracle validation-only gap 说成“已经支持多引擎数据面”；不回退当前 MySQL 与组织治理主链
- Sampling Plan: 先读 roadmap / PRD / 已完成 epic truth，再读明确保留 Oracle gap 的 child-task 和 UI 文案，最后扩展 roadmap 并物化新 epic
- Constraints: 只有在现有 roadmap 01-06 全部 DONE 的事实成立后，才允许进入 roadmap extension

## Close-Out Review

- Epic 06 证明了什么：
  - auth/session 已显式携带 active organization 与 membership scope
  - control-plane assets、system settings、alerting workflow 与 audit evidence 已显式挂到 `organization_id`
  - web shell / settings surface 已能表达当前组织治理语义
  - 根级 signoff 证明 organization-awareness 与默认单组织路径同时成立
- Epic 06 没证明什么：
  - 第二引擎是否已经具备真实数据面闭环
  - ClickHouse 状态面、worker、analytics API 与 web detail 是否能承载 Oracle telemetry
  - post-phase-one 之后是否还存在未完成的既有 roadmap epic
- 当前 roadmap 状态：
  - `EPIC_ROADMAP.md` 原始 01-06 路线已全部被仓库 truth source 关闭
  - 因此这一步不是“从现有 roadmap 中再挑一个默认 next”，而是“先扩展 roadmap，再激活新的 active epic”
- 为什么选择 `Oracle Data Plane and Minimum Insights`：
  - Epic 05 明确保留了 Oracle 在 dispatch、sink、normalization、worker、analytics 和 web 上仍是 validation-only / MySQL-only 的 gap
  - `apps/web/src/monitoring-ui.ts` 仍显式声明 Oracle 当前没有 trend analytics、preset views 和 capacity readouts
  - `RESEARCH.md` 已把“统一指标模型 + engine-specific extensions”作为产品级方向写明，当前正缺第二引擎的数据面闭环来验证它
- 什么证据才会支持跳到别的方向：
  - 如果根级 signoff 显示当前平台又回到 runtime/release 不稳定，应先回到 hardening 层
  - 如果组织治理引入了真实生产阻塞，应先处理 governance regression
  - 在当前仓库 evidence 下，这两类信号都没有比 Oracle data-plane gap 更强

## Decision Gate

- 当前结论：
  - 现有 roadmap 01-06 已全部完成，不存在可直接继续激活的旧 epic
  - 用户已明确要求进入“下一阶段 epic 规划并有序推进开发”，因此可以在完成 close-out review 后扩展 roadmap
- 当前结果：
  - `EPIC_ROADMAP.md` 已扩展到 post-phase-one 的 `Epic 07: Oracle Data Plane and Minimum Insights`
  - 新 epic 已完整物化到 `.codex-tasks/20260420-oracle-data-plane-epic/`
