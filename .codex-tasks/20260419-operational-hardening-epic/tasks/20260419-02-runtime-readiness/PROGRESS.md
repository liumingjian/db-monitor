# Progress

## Summary

- Task shape: single-full
- Goal: 为 API 建立正式运行时配置与依赖探针

## Recovery

- 任务: 让 `db_monitor_api.main` 可以显式选择运行时模式，并暴露 live / ready 证据
- 形态: single-full
- 进度: 4/4
- 当前: 子任务已完成，等待 parent epic 将焦点转到 `#3 process entrypoints`
- 文件: `.codex-tasks/20260419-operational-hardening-epic/tasks/20260419-02-runtime-readiness/TODO.csv`
- 下一步: 将 parent epic 的 `#2` 标记为 `DONE`，并进入 `#3 scheduler and worker operational entrypoints`

## Notes

- 当前真实缺口不是业务 API 不存在，而是正式运行时入口缺少约束与健康证据
- ready 探针必须覆盖真实依赖，而不是只返回进程存活
- `db_monitor_api.main` 现在默认保持 local runtime，但可通过环境变量切换为 PostgreSQL + ClickHouse 正式运行时
