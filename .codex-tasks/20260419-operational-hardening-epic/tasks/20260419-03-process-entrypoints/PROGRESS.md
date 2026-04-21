# Progress

## Summary

- Task shape: single-full
- Goal: 为 scheduler 和 worker 建立真实可运行的进程入口

## Recovery

- 任务: 让后台采集链路从“库函数可调”进入“进程可跑、状态可见”
- 形态: single-full
- 进度: 4/4
- 当前: 子任务已完成，等待 parent epic 切换到 `#4 schema bootstrap`
- 文件: `.codex-tasks/20260419-operational-hardening-epic/tasks/20260419-03-process-entrypoints/TODO.csv`
- 下一步: 将 parent epic 的 `#3` 标记为 `DONE`，并进入 `#4 schema bootstrap`

## Notes

- 当前主风险不是业务逻辑不存在，而是后台进程没有正式执行协议
- contract 先于 while-loop 实现，否则容易把隐式行为直接写死进入口
- 当前进程 gate 采用两层证据：background process gate 证明显式进程行为，metrics live gate 保持写入链路不退化
