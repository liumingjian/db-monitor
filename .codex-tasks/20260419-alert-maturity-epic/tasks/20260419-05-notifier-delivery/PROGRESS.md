# Progress

## Summary

- Task shape: single-full
- Goal: 建立 notifier delivery evidence 与 escalation semantics

## Recovery

- 任务: 让 delivery retry/failure 行为服从新的 alert workflow 语义
- 形态: single-full
- 进度: 4/4
- 当前: 子任务已完成
- 文件: `.codex-tasks/20260419-alert-maturity-epic/tasks/20260419-05-notifier-delivery/TODO.csv`
- 下一步: 进入子任务 `#6 triage-surface`

## Notes

- notifier 只能消费 workflow 状态，不能成为新的控制器
- 初次 open 的通知失败仍然必须抛错暴露
- 只有“失败后本应 retry”的通知才允许被 ACK/owner 截断
- `NOTIFICATION_SUPPRESSED` 与 noise-control 的 `SUPPRESSED` 保持分离，避免混淆控制语义
- unit / integration / live recovery gate 已全部通过
