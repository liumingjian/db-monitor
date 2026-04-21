# Progress

## Summary

- Task shape: single-full
- Goal: 为实例列表和告警列表交付最小可用的筛选 contract 与 Web surface

## Recovery

- 任务: child 已完成，`实例筛选` 与 `告警筛选` 两个显式 gap 已关闭
- 形态: single-full
- 进度: 4/4
- 当前: 已完成
- 文件: `.codex-tasks/20260421-prd-debt-closeout-epic/tasks/20260421-01-fleet-filtering/TODO.csv`
- 下一步: 将 child `#1` 的结果回灌到 parent truth，并把 closeout 主误差转移到 child `#2` 审计持久化

## Control Contract

- Primary Setpoint: `/control/instances` 和 `/alerts` 具备显式 query filter contract，用户可以在 Web 上按 PRD 要求缩小列表范围
- Acceptance: backend focused tests 证明过滤语义成立，OpenAPI/typed client 同步，web tests/typecheck 证明 filter surface 可用
- Guardrails: 不回退当前 organization scope；不引入 pagination/sorting；不把筛选逻辑藏进前端本地数据过滤
- Sampling Plan: 先在 service 层建立最小过滤语义并补 focused tests，再同步 typed client 与 server-rendered filter form
- Constraints: 当前 child 只允许触碰 control-plane/alerting list path、typed client、instances/alerts page 和相邻测试

## Contract Baseline

- Instance filters:
  - `name`: 大小写不敏感的名称包含匹配
  - `environment`: 大小写不敏感的环境精确匹配
  - `label`: 大小写不敏感的单标签匹配
  - `status`: 复用现有 validation status 语义，支持 `passed|failed`
- Alert filters:
  - `status`: `open|acknowledged|resolved`
  - `severity`: `warning|critical`
  - `instance`: 基于 `instance_id` 的大小写不敏感包含匹配
  - `opened_after` / `opened_before`: 基于 `opened_at` 的时间窗口过滤

## Latest Evidence

- backend:
  - `apps/api/src/db_monitor_api/control_plane/router.py` 与 `service.py` 现在支持 `name` / `environment` / `label` / `status`
  - `apps/api/src/db_monitor_api/alerting/router.py` 与 `service.py` 现在支持 `status` / `severity` / `instance` / `opened_after` / `opened_before`
- contract:
  - `packages/api-client/src/index.ts` 新增 `ListInstancesFilters` 与 `ListAlertsFilters`
  - `contracts/openapi.snapshot.json` 已同步新的 query parameter contract
- web:
  - `apps/web/app/instances/page.tsx` 与 `apps/web/app/alerts/page.tsx` 现在提供 server-rendered GET filter forms
  - `apps/web/src/monitoring-ui.ts` 新增 filter normalization helpers
- tests:
  - `tests/integration/control_plane/test_control_plane.py` 新增实例筛选覆盖
  - `tests/api/alerting/test_alerting_contract.py` 新增告警筛选覆盖
  - `apps/web/tests/instances.test.ts` 与 `apps/web/tests/alerts.test.ts` 新增 filter defaults/override 覆盖

## Validation

- `uv run pytest tests/integration/control_plane/test_control_plane.py tests/api/alerting/test_alerting_contract.py -q`
- `pnpm openapi:update`
- `pnpm openapi:check`
- `pnpm --filter web test`
- `pnpm typecheck`

## Notes

- 这一步的目标是“把筛选面交付出来”，不是“把列表系统做到完整后台”
- 本 child 有意把过滤逻辑放在 service 层，以保持第一刀最小、可逆、可验证
