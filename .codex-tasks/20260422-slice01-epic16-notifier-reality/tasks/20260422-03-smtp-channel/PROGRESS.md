# Progress

## Summary

- Task shape: single-full
- Goal: SMTP 备通道（HTML 模板 + 基础配置），供 Feishu 降级接管

## Recovery

- 任务: Epic 16 child #3
- 形态: single-full
- 进度: 0/4
- 当前: PLANNED（依赖 child #1；与 child #2 可并行）
- 文件: `.codex-tasks/20260422-slice01-epic16-notifier-reality/tasks/20260422-03-smtp-channel/TODO.csv`
- 下一步: child #1 DONE 后 → TODO `#1` SMTP settings

## Reference

- Epic 16 EPIC.md Scope 第 3 项
- Lepus `lepus_alarm_mail_content`（字段对照；不抄实现）

## Notes

- SMTP 配置只走 .env / settings，不入库（避免多租户 UI 下沉）
- 降级逻辑（Feishu 失败 → SMTP）不在本子任务，在 child #4
