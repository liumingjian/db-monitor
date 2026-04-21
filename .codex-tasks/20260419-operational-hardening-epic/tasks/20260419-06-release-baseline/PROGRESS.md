# Progress

## Summary

- Task shape: single-full
- Goal: 建立 operator 可执行的发布与回滚基线

## Recovery

- 任务: 把 hardening 结果转成可操作的发布/回滚流程
- 形态: single-full
- 进度: 4/4
- 当前: 已完成
- 文件: `.codex-tasks/20260419-operational-hardening-epic/tasks/20260419-06-release-baseline/TODO.csv`
- 下一步: 将 epic 控制权切换到 `#7 hardening signoff`

## Notes

- 上游 `#2/#3/#4/#5` 已完成，发布/回滚基线进入可编码状态
- 已新增：
  - `docs/operator-release-baseline.md`
  - `docs/operator-release-checklist.md`
  - `docs/operator-rollback-checklist.md`
  - `tests/ops/test_release_baseline.py`
- 发布基线已绑定到真实命令：
  - `pnpm dev:deps:up`
  - `pnpm smoke`
  - `pnpm test:api:readiness`
  - `pnpm test:background-processes`
  - `pnpm test:schema:bootstrap`
  - `pnpm test:recovery-paths`
  - `pnpm dev:deps:down`
- 本任务验证已通过：
  - `uv run pytest tests/ops`
  - `pnpm smoke`
  - `uv run ruff check apps tests gates`
  - `uv run mypy apps tests gates`
