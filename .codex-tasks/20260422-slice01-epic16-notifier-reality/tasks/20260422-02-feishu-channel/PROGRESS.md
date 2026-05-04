# Progress

## Summary

- Task shape: single-full
- Goal: 飞书 webhook 主通道（签名 + 富卡片 + @ + 重试）

## Recovery

- 任务: Epic 16 child #2
- 形态: single-full
- 进度: 0/5
- 当前: PLANNED（依赖 child #1）
- 文件: `.codex-tasks/20260422-slice01-epic16-notifier-reality/tasks/20260422-02-feishu-channel/TODO.csv`
- 下一步: child #1 DONE 后 → TODO `#1` 签名 + payload builder

## Reference

- Epic 16 EPIC.md Scope 第 2 项
- 飞书 open-platform 自定义机器人文档（签名算法）

## Notes

- 本切片只做内建卡片模板；自定义模板在 Slice 3
- 与 child #3（SMTP）可并行；共享 `notify_history` 写入约定
