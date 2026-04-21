# Progress

## Summary

- Task shape: epic
- Goal: 用一轮有边界的 closeout epic，把原始 PRD 剩余的控制面欠账收口成可验证状态

## Recovery

- 任务: child `#1` 已完成；当前 active child 已切换为 `#2` 审计持久化与最小查询面
- 形态: epic
- 进度: 1/5
- 当前: child `#2` `Persist audit logs and expose minimum query surface`
- 文件: `.codex-tasks/20260421-prd-debt-closeout-epic/SUBTASKS.csv`
- 下一步: 进入 child `#2` 的 schema-sensitive control cycle，先冻结 audit persistence boundary，再决定 PostgreSQL audit repository 与最小 read path 的落点

## Control Contract

- Primary Setpoint: 把 `docs/prd-closeout.md` 中的 remaining gaps 从“文档说明”推进到“代码与验证已成立”
- Acceptance: 新 epic truth artifacts 与所有 child skeleton 已落盘；当前 active child 能通过 focused gate 关闭两个列表筛选 gap；后续 child 仍可从磁盘恢复
- Guardrails: 不回退现有 auth、organization、alerting、analytics 与多引擎基线；不把 closeout 扩成新的产品 phase
- Sampling Plan: 先做无 schema 风险的筛选面，再进入 audit persistence / user management 等共享状态子任务，最后用 signoff 收口
- Constraints: 只有 `SUBTASKS.csv` 中列出的 child 能进入实现；未进入 `IN_PROGRESS` 的 child 不允许提前写产品代码

## Latest Evidence

- child `#1` 已完成并通过 focused signoff：
  - `uv run pytest tests/integration/control_plane/test_control_plane.py tests/api/alerting/test_alerting_contract.py -q`
  - `pnpm openapi:check`
  - `pnpm --filter web test`
  - `pnpm typecheck`
- child `#1` 关闭的产品 gap：
  - `/control/instances` 现在支持 `name` / `environment` / `label` / `status`
  - `/alerts` 现在支持 `status` / `severity` / `instance` / `opened_after` / `opened_before`
  - `packages/api-client` 已提供对应 filter objects
  - `/instances` 与 `/alerts` 页面都已变成 server-rendered GET filter form
- `docs/prd-closeout.md` 现在应从 “6 项 remaining gaps” 收敛为 “4 项 remaining gaps”
- `EPIC_ROADMAP.md` 已把 `Epic 10: PRD Debt and Control-Plane Closeout` 设为当前 active epic
- `.codex-tasks/20260421-prd-debt-closeout-epic/` 及所有 child recovery skeleton 已创建完成，满足 `AGENT.md` 的 planning materialization 规则
- 当前新的主误差已转移到 child `#2`：
  - runtime 仍以 `InMemoryAuditRepository` 为主
  - 用户/角色管理 child 不应继续建立在内存 audit seam 上
  - 这是接下来最合适的共享状态收口点

## Notes

- 这是 closeout epic，不是新的产品扩展 epic
- child `#1` 已证明：列表筛选可以先在 service 层诚实收口，而不需要提前把 repository/query model 改成更重的 shared contract
- child `#2` 和 `#3` 涉及共享状态与审计真相，下一轮必须继续遵循 schema-sensitive gate
