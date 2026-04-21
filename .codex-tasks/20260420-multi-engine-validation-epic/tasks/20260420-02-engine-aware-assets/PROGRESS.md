# Progress

## Summary

- Task shape: single-full
- Goal: 建立 engine-aware 的资产契约基线

## Recovery

- 任务: 已完成 engine-aware 资产契约收敛
- 形态: single-full
- 进度: 3/3
- 当前: 已完成最终验证
- 文件: `.codex-tasks/20260420-multi-engine-validation-epic/tasks/20260420-02-engine-aware-assets/TODO.csv`
- 下一步: 将父 epic 切换到子任务 `#3 Add Oracle onboarding and validation baseline`

## Notes

- 控制面资产事实源已升级为 engine-aware，并保留了 mysql-only 兼容入口：
  - 资产模型和 Postgres 状态面新增 `engine`
  - OpenAPI 主契约切换到 `/control/instances`，legacy `/control/mysql-instances` 继续可用但不再出现在 schema 中
  - web 当前仍显式提交 `engine: "mysql"`，避免在 Oracle UI 尚未到位前制造假抽象
- 本轮验证证据：
  - `uv run pytest tests/api/assets tests/integration/control_plane tests/schema/test_schema_bootstrap.py`
  - `pnpm openapi:check`
  - `pnpm --filter web test`
  - `pnpm --filter web typecheck`
- 这一步已经把最核心的控制面 seam 收敛到位，后续 Oracle onboarding、scheduler dispatch 和 web 承载可以在真实 engine 维度上继续展开
