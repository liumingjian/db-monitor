# Progress

## Summary

- Task shape: epic
- Goal: 验证 Oracle 作为第二引擎试金石时，当前平台边界是否真的具备 engine-aware 扩展能力

## Recovery

- 任务: Epic 05 已完成根级 signoff
- 形态: epic
- 进度: 6/6
- 当前: Epic 05 `Multi-Engine Expansion and Abstraction Validation` 已完成
- 文件: `.codex-tasks/20260420-multi-engine-validation-epic/SUBTASKS.csv`
- 下一步: 如需继续 roadmap，需要先按 `AGENT.md` 执行下一 epic 的 close-out review 与 planning materialization

## Notes

- Epic 04 已完成并通过 root signoff，因此当前主误差从 analytics depth 转到 abstraction validity
- Oracle 已被显式冻结为第二引擎试金石：
  - `PRD.md` 已把 Oracle 列为 phase-one 之后才进入的多引擎扩展对象
  - `legacy/lepus-v3.8` 提供了历史 Oracle 能力面的仓库证据
- 子任务 `#2` 已完成，证明当前平台至少在控制面资产层已经具备真实的 engine 维度：
  - 资产模型 / 状态面 / OpenAPI / api-client / web 基线均已携带 `engine`
  - 兼容 MySQL 的 legacy route 仍可工作，因此没有为了抽象而打断既有路径
  - 通过门禁：`uv run pytest tests/api/assets tests/integration/control_plane tests/schema/test_schema_bootstrap.py`、`pnpm openapi:check`、`pnpm --filter web test`、`pnpm --filter web typecheck`
- 子任务 `#3` 已完成，证明 Oracle 已经拥有最小可测试接入路径：
  - Oracle create/validate 已通过 injected validator 在 in-memory 和 Postgres 控制面路径打通
  - OpenAPI 已显式说明 Oracle 使用 DSN/service name 与显式端口语义
  - 该任务关闭时曾显式保留 live Oracle gate；后续已由 `.codex-tasks/20260420-oracle-live-gate/` 在 macOS 本地以 `oracledb` + docker `sqlplus` fallback 闭环
- 子任务 `#4` 已完成，证明 pipeline 调度面已经具备最小真实的 engine-aware seam：
  - `CollectionJob` 现在携带 `engine`，并兼容旧 MySQL 队列载荷
  - scheduler 只为当前受支持的引擎排队，Oracle 不会再隐式滑入 MySQL worker
  - queue 名、sink 表、collector、worker 仍是 MySQL-specific gap，并且已经被明确记录
- 子任务 `#5` 已完成，证明 web surface 已经能诚实承载当前多引擎状态：
  - inventory / detail / onboarding 都显示 engine identity
  - Oracle 可以从当前 web form 进入控制面
  - Oracle detail route 不再伪装成具备 MySQL analytics parity
- 子任务 `#6` 已完成，Epic 05 根级 signoff 已通过：
  - `pnpm openapi:check`
  - `uv run pytest tests/api/assets tests/integration/control_plane tests/scheduler tests/integration/metrics_pipeline`
  - `pnpm --filter web test`
  - `pnpm --filter web typecheck`
  - `pnpm --filter web build`
  - `pnpm smoke`
- 本 epic 仍然不宣称 Oracle analytics parity；原先在 epic close-out 时显式保留的本机 live Oracle gap 已由后续任务 `.codex-tasks/20260420-oracle-live-gate/` 关闭
