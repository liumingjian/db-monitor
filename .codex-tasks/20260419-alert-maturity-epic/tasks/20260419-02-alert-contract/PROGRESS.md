# Progress

## Summary

- Task shape: single-full
- Goal: 冻结 alert lifecycle state contract 与 persistence boundary

## Recovery

- 任务: 为后续 on-call workflow 建立稳定的 alert 状态真相源
- 形态: single-full
- 进度: 4/4
- 当前: 子任务已完成
- 文件: `.codex-tasks/20260419-alert-maturity-epic/tasks/20260419-02-alert-contract/TODO.csv`
- 下一步: 进入子任务 `#3 alert-noise-controls`

## Notes

- 当前 `AlertStatus` 只有 `OPEN` 与 `RESOLVED`
- 当前 `AlertEventType` 只有 `OPENED` / `NOTIFIED` / `NOTIFICATION_FAILED` / `RESOLVED`
- 当前 repository contract 只有 `find/list/get/upsert/history/rule`，没有显式 workflow mutation boundary
- 当前 Web `/alerts` 只有列表与详情只读视图，尚无值班动作入口
- 当前冻结草案：
  - `AlertStatus`: `OPEN` / `ACKNOWLEDGED` / `RESOLVED`
  - `AlertRecord` 扩展 owner/ack 时间与用户字段
  - `NOTE_ADDED` 先以 history event 形式落盘，避免提前引入独立 note table
- 本轮完成结果：
  - repository lookup 从 `find_open_alert` 升级为 `find_active_alert`，避免 acknowledged alert 再次触发重复 open
  - PostgreSQL schema version 升级到 `2`，并显式持久化 ack/owner 字段
  - API、新 OpenAPI snapshot、typed client 与 smoke preview 已与新 contract 对齐
  - PostgreSQL schema / alert / recovery live gates 已通过
