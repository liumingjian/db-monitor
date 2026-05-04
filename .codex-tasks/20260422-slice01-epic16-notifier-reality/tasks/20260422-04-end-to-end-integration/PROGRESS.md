# Progress

## Summary

- Task shape: single-full
- Goal: rule-engine 命中 → Notifier 异步送达；timeout/失败不回压；Feishu→SMTP 降级

## Recovery

- 任务: Epic 16 child #4
- 形态: single-full
- 进度: 5/5
- 当前: DONE（2026-04-22）
- 文件: `.codex-tasks/20260422-slice01-epic16-notifier-reality/tasks/20260422-04-end-to-end-integration/TODO.csv`
- 下一步: 返回父 epic；等待 child #5 真人 DBA 演练（harness 外）

## Validation

- `uv run pytest tests/alerting_notification tests/api/alerting tests/alerting_contract tests/alerting_workflow tests/alerting_delivery tests/alerting_noise tests/rule_engine tests/schema/test_schema_bootstrap.py tests/api/health -q` → 102 passed
- `uv run mypy apps/api/src/db_monitor_api/alerting apps/api/src/db_monitor_api/bootstrap.py apps/api/src/db_monitor_api/runtime.py tests/rule_engine/test_dispatch_backpressure.py` → 28 source files, clean
- `uv run ruff check ...` → all checks passed
- `pnpm test:notifier:signoff` → openapi:check ✓, 102 pytest ✓, pnpm test 72/72 ✓, pnpm typecheck ✓

## Reference

- Epic 16 EPIC.md Scope 第 4 项 + Control Contract（rule-engine p95 硬边界）
- ADR-0003（Notifier 不得阻塞评估核心）

## Notes

- 降级只在同一事件内触发，不做跨事件状态机；跨事件的抑制 / 升级切到 Slice 3
- `pnpm test:notifier:signoff` 在本子任务落地后就具备最终验证能力
