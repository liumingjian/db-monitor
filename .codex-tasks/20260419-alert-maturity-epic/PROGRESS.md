# Progress

## Summary

- Task shape: epic
- Goal: 让告警从基础触发能力演进到可持续值班使用的 alert maturity 阶段

## Recovery

- 任务: 激活 `Alert Maturity and On-Call Workflow` 并推进第一个真实实现子任务
- 形态: epic
- 进度: 7/7
- 当前: Epic 03 已完成
- 文件: `.codex-tasks/20260419-alert-maturity-epic/SUBTASKS.csv`
- 下一步: 如需沿 roadmap 继续推进，先执行 Epic 03 close-out review，再按 `AGENT.md` 的 epic transition protocol 决定是否激活下一 epic

## Notes

- 本 epic 由 `EPIC_ROADMAP.md` 的 conditional next 通过 close-out review 激活，而不是临时发明新方向
- Epic 02 已证明 runtime、schema、recovery 和 release gate 基线成立，因此本轮主误差转移到告警质量与值班闭环
- 当前 alert domain 只有 `open/resolved` 与基础通知历史，尚不具备 ack/owner/note/suppression 语义
- 全部已批准 child task skeleton 已一次性落盘，满足 planning completeness 规则
- 子任务 `#2` 已完成：contract 已收敛为 `OPEN / ACKNOWLEDGED / RESOLVED`，PostgreSQL schema 提升到 v2，active-alert lookup 不再因 acknowledged 状态重复开告警
- 子任务 `#4` 已完成：acknowledge / owner / note workflow 已落到 repository history、API route、OpenAPI snapshot 与 typed client contract
- 子任务 `#3` 已完成：group key 明确固定为 `rule_id + instance_id`，repeated active matches 会按 suppression window 追加 `SUPPRESSED` evidence，而不是 silent drop
- 子任务 `#5` 已完成：notifier retry 只会在 would-retry 分支上被 ACK/owner 截断，并追加 `NOTIFICATION_SUPPRESSED` evidence，初次 open failure 仍显式暴露
- 子任务 `#6` 已完成：alert list/detail 页面和 server actions 已接到 typed client/back-end truth，且通过 `pytest`、`vitest`、`tsc`、`next build` 与 `biome`
- 子任务 `#7` 已完成：repo-root `pnpm test:alert-maturity:signoff` 已串起 OpenAPI、backend/web gates、live PostgreSQL alert gate 与 recovery gate，并在缺少系统 PowerShell 的 macOS 环境中通过 repo-local shim 收敛执行入口
