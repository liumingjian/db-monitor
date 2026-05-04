# Progress

## Summary

- Task shape: single-full
- Goal: 把 WeCom（企业微信）作为第三条 Notifier 通道接入，复用 Epic 16 的 ChannelRegistry / DispatchCoordinator 抽象，不引入新核心改动

## Recovery

- 任务: Slice 2 child #1
- 形态: single-full
- 进度: 0/N（待 ADR-0013 转 Accepted 后展开 SPEC.md + TODO.csv）
- 当前: PLANNED（依赖 ADR-0013 决议）
- 文件: `.codex-tasks/20260504-slice02-alert-maturity-epic/tasks/20260504-01-wecom-channel/`
- 下一步: ADR-0013 转 Accepted → 撰写 SPEC.md（fixture / config schema / 测试矩阵） → TODO.csv 展开

## Reference

- ADR-0013 WeCom + SMS 通道
- Epic 16 child #2（飞书通道）作为最近的同类参考；测试拓扑可直接复用
- `apps/api/src/db_monitor_api/alerting/notification/channels/feishu.py` 作为 webhook 通道的实现模板

## Notes

- 不接 WeCom 应用消息 / 消息中心 API；仅 webhook 路径
- markdown 卡片排版能力比飞书弱，但满足"事件/规则/实例/命中值/链接"5 字段
- 失败 fallback SMTP（`dispatch_with_fallback` 已支持任意通道 → SMTP）
