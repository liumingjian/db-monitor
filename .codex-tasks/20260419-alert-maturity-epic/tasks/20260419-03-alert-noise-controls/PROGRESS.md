# Progress

## Summary

- Task shape: single-full
- Goal: 建立 alert dedupe / suppression / grouping 噪音控制语义

## Recovery

- 任务: 在不丢失根因证据的前提下压低告警噪音
- 形态: single-full
- 进度: 4/4
- 当前: 子任务已完成
- 文件: `.codex-tasks/20260419-alert-maturity-epic/tasks/20260419-03-alert-noise-controls/TODO.csv`
- 下一步: 进入子任务 `#5 notifier-delivery`

## Notes

- `#2` 已完成，当前已具备 active-alert contract 与 workflow history
- 当前唯一现成的 noise control 只有：
  - 同一 `rule_id + instance_id` 在未 resolved 前不会重复 open 新 alert
- 当前缺口：
  - 没有 suppression window
  - 没有被 suppress/grouped 的显式 evidence 事件
- 当前冻结决议：
  - group key 固定为 `rule_id + instance_id`
  - 不做跨实例聚合
  - 只有 suppression window 到期时才写 `suppressed` evidence
- 本轮完成结果：
  - 引入 `AlertNoiseControlPolicy`
  - repeated active match 在 suppression window 内继续静默去重，但超过窗口会写 `SUPPRESSED` history evidence
  - `SUPPRESSED` evidence 会保留 group key 与触发值，避免降噪丢失根因线索
  - unit / integration / PostgreSQL live gate 均已通过
