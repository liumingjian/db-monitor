# Progress

## Summary

- Task shape: single-full
- Goal: per-instance threshold overrides via `rule_instance_overrides` 关联表

## Recovery

- 任务: Epic 15 child #5
- 形态: single-full
- 进度: 6/8
- 当前: TODO #7 待启动 (web overrides sub-table) — backend + OpenAPI 完工，web 由下一个 subagent 接手
- 文件: `.codex-tasks/20260422-slice01-epic15-monitoring-depth/tasks/20260422-05-per-instance-threshold-overrides/TODO.csv`
- 下一步: TODO #7 — 规则编辑页 Per-instance overrides 子表

## Reference

- ADR-0004（schema 决议）
- ADR-0011 D2（audit action 命名 `rules.override.*`）/ D4（评估入口 `evaluation.py:43-74`）/ D5（acceptance 新口径）
- lepus-v3.8/sql/lepus_table.sql（`db_servers_mysql.alarm_*` + `threshold_*` 为领域对照；**不**抄实现）

## Notes

- override 字段只做 threshold + enabled；severity 和 evaluation_window 不在切片 1
- rule-engine acceptance 硬边界（ADR-0011 D5，取代原"p95 ≤ 10%"口径）：(1) `list_rules()` 仍返回 |rules| 行（json_agg 聚合 overrides）；(2) `_evaluate_sample()` 不新增 DB call；(3) 既有 `find_active_alert()` N+1 不退化为 N+2；顺带插 `perf_counter` 埋点（非 signoff 门）

## Latest Evidence (2026-04-22)

### Worktree

- Worktree: `/Users/lmj/projects/ai-project/db-monitor/.claude/worktrees/agent-ac5ef618`
- Branch: `worktree-agent-ac5ef618`（基于 main `0bb8fa6`；Boss 会合并）
- 与主仓库另一个 subagent 并行跑；`POSTGRES_SCHEMA_VERSION` 本 worktree 升至 **10**（主仓库若已升到 9，合并时 Boss 调号）

### 验证命令 / 输出

| TODO | 验证命令 | 结果 |
|---|---|---|
| #1 | `uv run pytest tests/schema/test_schema_bootstrap.py -q` | 4 passed |
| #2 | `uv run pytest tests/api/alerting/test_rule_overrides.py -k "test_repo" -q` | 3 passed |
| #3 | `uv run pytest tests/rule_engine/test_override_evaluation.py -q` | 6 passed |
| #4 | `uv run pytest tests/api/alerting/test_rule_overrides.py -k "test_api" -q` | 2 passed |
| #5 | `uv run pytest tests/api/audit/test_rule_override_audit.py -q` | 2 passed |
| #6 | `pnpm openapi:check` | `OpenAPI snapshot matches` |

### 既有测试回归

- `tests/schema/ tests/rule_engine/ tests/alerting_contract/ tests/alerting_delivery/ tests/alerting_noise/ tests/alerting_workflow/ tests/api/alerting/ tests/api/audit/ tests/integration/alert_pipeline/` = **42 passed**
- 不相关 live DB 残留：`tests/integration/control_plane/test_control_plane_postgres.py` 因 live PG 中有另一个 subagent 创建的 `instance_parameters` 表依赖 `control_mysql_instances`，DROP 失败；此错与本 child #5 无关，是另一个 subagent 的 work-in-progress schema

### D5 硬边界证据

- (1) `InMemoryAlertingRepository.list_rules()` + `PostgresAlertingRepository.list_rules()` 均返回 |rules| 行（PG 用 `json_agg ... FILTER (WHERE o.rule_id IS NOT NULL)` + `GROUP BY r.*` 聚合；InMemory 用 `_hydrate_rule_overrides` 方法聚合）；`test_list_rules_returns_one_row_per_rule_with_json_aggregated_overrides` 锁定
- (2) `test_evaluation_does_not_call_list_rules_twice_or_new_repo_methods` 使用 `patch.object(..., wraps=...)` 跟踪 call_count，断言 `get_rule` 0 次、`list_rules` 1 次
- (3) 同上测试断言 `find_active_alert.call_count == |matching samples|`（2 次，N+1 不退化为 N+2）
- (4) `evaluate_samples()` 首尾 `time.perf_counter()`，写结构化日志 `event="rule.evaluation.completed" duration_ms rule_count sample_count`（JSON stringified 通过 stdlib logging，非 signoff 门）

### 变更清单

- `apps/api/src/db_monitor_schema/contract.py`：`POSTGRES_SCHEMA_VERSION` 8 → 10
- `apps/api/src/db_monitor_schema/postgres.py`：新增 `_CREATE_RULE_INSTANCE_OVERRIDES_SQL` + bootstrap 调用 + required table 注册
- `apps/api/src/db_monitor_api/alerting/domain.py`：新增 `RuleInstanceOverride` dataclass；`AlertRule.overrides: tuple[...]`（default `()`）
- `apps/api/src/db_monitor_api/alerting/repository.py`：Protocol + InMemory 加 `upsert_override` / `delete_override` / `get_rule` / `update_rule` 方法；`list_rules` 通过 `_hydrate_rule_overrides` 聚合
- `apps/api/src/db_monitor_api/alerting/postgres_repository.py`：`list_rules()` SQL 改为 `LEFT JOIN rule_instance_overrides USING (rule_id) + json_agg(...) GROUP BY r.*`；新增 `get_rule` / `upsert_override` / `delete_override` / `update_rule`；`_row_to_rule` 解析 overrides；新增 `_parse_override_rows`
- `apps/api/src/db_monitor_api/alerting/evaluation.py`：`evaluate_samples()` 插 perf_counter + 结构化日志；`_evaluate_sample()` 接收 `override: RuleInstanceOverride | None` 参数；新增 `_effective_threshold` / `_effective_enabled` / `_index_overrides` / `_log_evaluation_completed`；`_open_alert` 用 `effective_threshold` 记录 alert
- `apps/api/src/db_monitor_api/alerting/service.py`：新增 `OverrideDraft` / `RuleNotFoundError`；新增 `get_rule` / `update_rule` / `upsert_rule_override` / `delete_rule_override` / `replace_rule_overrides` / `_validate_override_instance`；`create_rule` 接受 `overrides` kwarg
- `apps/api/src/db_monitor_api/alerting/router.py`：新增 `RuleOverrideRequest` / `RuleOverrideResponse` / `UpdateRuleRequest`；`CreateRuleRequest` + `AlertRuleResponse` 加 `overrides`；新增 `GET /alerts/rules/{rule_id}` + `PUT /alerts/rules/{rule_id}` 端点；`_build_rule_response` 填充 overrides；新增 `_build_override_response` / `_to_override_drafts`
- `gates/schema/test_schema_bootstrap_live.py`：`_reset_postgres_schema()` 加 `DROP TABLE IF EXISTS rule_instance_overrides`（在 `alert_rules` 之前，遵守 FK 依赖序）
- `tests/schema/test_schema_bootstrap.py`：扩断言覆盖 `rule_instance_overrides`
- `tests/api/alerting/test_rule_overrides.py`：**新建**，5 测试（3 test_repo + 2 test_api）
- `tests/rule_engine/test_override_evaluation.py`：**新建**，6 测试（含 D5 硬边界证据）
- `tests/api/audit/test_rule_override_audit.py`：**新建**，2 测试
- `contracts/openapi.snapshot.json`：重新生成，扩展 `RuleOverrideRequest` / `RuleOverrideResponse` / `/alerts/rules/{rule_id}` GET+PUT；无 breaking
- `packages/api-client/src/index.ts`：新增 `RuleOverrideRequest` / `RuleOverrideResponse` / `UpdateAlertRuleRequest` 类型；`AlertRuleResponse` 加 `overrides`；`CreateAlertRuleRequest` 加 `overrides?`；`ApiClient` 加 `getRule` / `updateRule`

## Handoff to Web Subagent (TODO #7/#8)

### API 形状

- `GET /alerts/rules/{rule_id}` → `AlertRuleResponse`（含 `overrides: RuleOverrideResponse[]`）
- `PUT /alerts/rules/{rule_id}` 接受 `UpdateAlertRuleRequest`（`overrides?: RuleOverrideRequest[]`）
- `POST /alerts/rules` 接受 `CreateAlertRuleRequest`（`overrides?: RuleOverrideRequest[]`）
- `RuleOverrideRequest`: `{ instance_id: string; enabled?: boolean | null; threshold?: number | null }`
- `RuleOverrideResponse`: `{ instance_id; enabled: bool|null; threshold: number|null; updated_at: string }`
- 语义：PUT 的 `overrides[]` 是**完整替换**（missing instance_id → delete；listed instance_id → upsert）
- enabled 三态：`undefined/null`（inherit）/ `true` / `false`
- threshold 可选：`null` → 继承 `rule.threshold`；number → 覆盖

### 前端建议落点

- 规则编辑页（`apps/web/app/rules/`）新增"Per-instance overrides"子表
- 每行：instance 下拉（从当前规则 `instance_ids` 或全量 control-plane 取） / threshold 输入 / enabled 三态开关 / 删除按钮
- 保存时调 `updateRule(ruleId, { ..., overrides: [...] })`；typed client 已暴露
- 顶部 `+ Add override` 按钮
- smoke（TODO #8）：创建规则 → 添加 override → 保存 → 重新加载 → 断言 overrides 回填

### Audit 事件

- `rules.override.upsert` / `rules.override.delete`（resource 形如 `alert-rule:{rule_id}:instance:{instance_id}`）
- `rules.update`（新增）

### 注意事项

- Web subagent 不需碰 backend；所有 backend hooks 已就绪
- Typed client 已更新；`import { AlertRuleResponse, RuleOverrideRequest, RuleOverrideResponse, UpdateAlertRuleRequest } from "@db-monitor/api-client"`
- Permission：复用 `RULES_WRITE`（不新增 Permission 枚举）
- Post-merge 由 Boss 处理：若主仓库 schema version 已到 9（subagent 1 加的 `instance_parameters`），需把本 worktree 的 `POSTGRES_SCHEMA_VERSION = 10` 保持 / 合并 bootstrap 函数调用顺序
