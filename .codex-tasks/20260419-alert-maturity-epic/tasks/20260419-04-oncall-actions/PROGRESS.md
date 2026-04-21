# Progress

## Summary

- Task shape: single-full
- Goal: 建立 ack / owner / note 的持久化值班 workflow

## Recovery

- 任务: 让告警处理动作进入统一状态机与审计历史
- 形态: single-full
- 进度: 4/4
- 当前: 子任务已完成
- 文件: `.codex-tasks/20260419-alert-maturity-epic/tasks/20260419-04-oncall-actions/TODO.csv`
- 下一步: 等待 `#3` 收口 noise control 后进入 notifier delivery 语义

## Notes

- 本任务不追求工单化，只收口最小值班处理语义
- 已交付：
  - `POST /alerts/{id}/acknowledge`
  - `PUT /alerts/{id}/owner`
  - `POST /alerts/{id}/notes`
- 已验证：
  - same-user repeat acknowledge / same-owner repeat assignment 不会重复写 history
  - resolved alert acknowledge 会显式报错，而不是静默成功
