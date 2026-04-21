# Progress

## Summary

- Task shape: epic
- Goal: 让 phase-one 产物进入可探测、可运行、可恢复的运维硬化阶段

## Recovery

- 任务: 激活 `Operational Hardening and Delivery Readiness` 并推进第一个运行时硬化子任务
- 形态: epic
- 进度: 7/7
- 当前: Epic 02 已完成
- 文件: `.codex-tasks/20260419-operational-hardening-epic/SUBTASKS.csv`
- 下一步: 等待 Boss 指定后续 epic

## Notes

- 本 epic 由 `EPIC_ROADMAP.md` 的默认 next 激活，而不是临时新增方向
- 第一优先级是修正 “代码逻辑存在，但正式运行时不足” 的真实缺口
- 子任务 `#2` 已完成：正式运行时可通过环境变量激活，并具备 PostgreSQL / ClickHouse readiness 证据
- 当前 epic 已满足新的 planning completeness 规则：全部已批准 child task skeleton 已一次性落盘
- 子任务 `#3` 已完成：scheduler / worker 具备 env-driven oneshot/loop 入口、live Redis/Postgres background gate，以及与现有 metrics live gate 的协同验证
- 子任务 `#4` 已完成：schema bootstrap 已从隐式副作用收敛为显式 contract / CLI / live gate，API 与后台进程启动路径会先 verify schema baseline
- 子任务 `#5` 已完成：recovery guards 已收敛 queue dedupe、worker collector retry/backoff、非幂等 sink failure guard，以及 alert notification retry resume path
- 子任务 `#6` 已完成：operator release baseline 已将现有 root scripts/gates 编成 runbook、release checklist 和 rollback checklist
- 子任务 `#7` 已完成：已形成 root hardening signoff command，并完成 lint/typecheck/tests/live gates/smoke 的统一签收
- 只有当运行时探针和 live gate 成立后，才推进后台进程入口和恢复语义
