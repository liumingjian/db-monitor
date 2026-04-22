# Progress

## Summary

- Task shape: single-full
- Goal: 恢复当前分支的 release / hardening gates

## Recovery

- 任务: child `#3` 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 已关闭；branch-level release / hardening gates 已恢复
- 文件: `.codex-tasks/20260422-production-launch-readiness-epic/tasks/20260422-03-release-gate-restoration/TODO.csv`
- 下一步: 无。child `#4-#6` 已建立在已恢复的 gate 之上

## Latest Evidence

- 当前 hardening gate 的第一层阻塞是 `Biome` drift：
  - 对 lint scope 执行了 `pnpm exec biome check --write ...`
  - web 与 api-client 的 import-order / format 漂移已收口
- 第二层阻塞是 `mypy` contract drift：
  - `apps/api/src/db_monitor_api/control_plane/oracle_validation.py` 补齐了 Oracle cursor / connection protocol
  - 多个 live gate / tests 已补齐 `organization_id`、`engine` 和 `MonkeyPatch` 标注
  - analytics JSON helper 已改为显式 `cast(...)`
- 最终验证：
  - `pnpm test:hardening:signoff` 通过
