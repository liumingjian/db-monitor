# ADR-0010: Slice 1 cutover and one-way door inventory

Status: accepted (2026-04-22)

Slice 1 的签字由 Epic 16 child `#5`（真人值班演练）提供。**签字生效后**，Slice 1 范围内的若干决策与产物将变得事实上不可逆——回滚会打穿后续 Slice 的依赖链。本 ADR 显式清点哪些是 **one-way door**、哪些仍是 **two-way door**、以及每类决策的回退触发器和窗口。Lepus 无运行用户，本 ADR 不涉及任何 Lepus 并行 / 切流 / 关停问题。

## One-Way Doors（签字后不可逆）

| # | 决策 | 不可逆原因 | 回退代价 |
|---|---|---|---|
| 1 | `Permission.INSTANCES_ACTION` 枚举加入 | 角色-权限矩阵一旦上线并被 admin/operator 消费，回滚会让已分配权限的账户失效；审计日志已按 `instance.<resource>.<verb>` 格式落库 | PG 迁移回滚 + 审计数据迁移 + 角色矩阵重配；演练签字后默认不走这条回退路径 |
| 2 | ClickHouse 专表 `mysql_processlist` / `mysql_slow_query_events` / `oracle_tablespaces` 落库 | Epic 15 签字后已承载真实采集数据；删表会丢失 7-30 天的可回放历史；后续 Slice（OS/SQLServer）将复用该表命名规范（ADR-0008） | DROP TABLE 数据永久丢失；不回收表名（命名规范冻结） |
| 3 | PostgreSQL `rule_instance_overrides` schema + CASCADE FK | 规则编辑 UI 已允许 DBA 录入 per-instance 覆盖；回滚会让"已声明的例外"全部丢失并让规则重新全量触发 | 备份 override 行 → DROP TABLE → 还原到全局规则；误报重新泛滥 |
| 4 | PostgreSQL `notify_history` schema（Epic 16 child `#1`） | 送达历史是审计证据，监管/复盘均依赖；演练后真实事件已写入 | 备份后 DROP；丢失合规证据链 |
| 5 | `CONTEXT.md` Slice sequence 把 Slice 1 从 `locked` 改为 `done` | 该改动触发 Slice 2 planning materialization；反转会让 Slice 2 的骨架作废 | 手工回写 + Slice 2 骨架归档（不删除、加 `aborted` 标记） |

## Two-Way Doors（仍可回滚）

| # | 决策 | 可回滚因为 |
|---|---|---|
| A | `instance.processlist_interval_seconds` 默认值 | 运行期可配；改默认不改 schema |
| B | `instance.slow_threshold_seconds` 默认值 | 同上 |
| C | ADR-0009 的 `3 / 1-3-9s / 20s / 500 / 60s / 10` 数字 | 同上；ADR-0009 显式规定"启动值"而非"最终值" |
| D | 飞书卡片格式 | adapter 内部展示层，可增量演化 |
| E | SMTP 模板 HTML | 同 D |
| F | rule-engine LEFT JOIN overrides 的具体 SQL 写法 | 只要行为等价，实现可重构 |

## Cutover Protocol

Slice 1 签字动作按下列顺序执行，前一步未完成禁止进入下一步：

1. **Epic 15 offline signoff** — `pnpm test:hardening:signoff` + `pnpm test:schema:bootstrap` + 4 个新 UI smoke 主路径通过（Epic 15 child `#6`）
2. **Epic 16 end-to-end integration signoff** — `tests/api/alerting/notification/test_e2e_dispatch.py` + `tests/rule_engine/test_dispatch_backpressure.py` 绿（Epic 16 child `#4`）
3. **演练 signoff** — Epic 16 child `#5` 的 `REHEARSAL_REPORT.md` 4 场景 PASS + DBA 签字
4. **CONTEXT.md + EPIC_ROADMAP.md 更新** — Slice 1 标 `done`、Epic 15/16 标 DONE、Slice 2 进入 planning materialization

步骤 3 与步骤 4 之间留**24 小时观察窗口**，用于捕获演练当下未显现的 Only-L2-Visible 风险（见 `docs/validation-ladder.md`）。若观察窗口内任一 rollback trigger 触发，回到步骤 3 之前的状态——即"演练失败、Slice 1 未签字"，不尝试"签了再回"。

## Rollback Triggers（24 小时观察窗口内）

一旦出现以下任一信号，Slice 1 签字默认**撤回**（回到 Epic 16 child `#5` 重新演练）：

- `pnpm test:hardening:signoff` 出现本 Slice 引入的回归
- `notify_history.status='dropped'` 比例超过 5%（anti-windup 实际生效但默认上界过低）
- rule-engine 评估 p95 相比 Slice 1 启动前基线退化超过 10%（override LEFT JOIN 性能假设失效）
- ClickHouse 三张新表中任一表的日增长率超过 ADR-0005/0007/0008 估算的 2 倍
- 演练中未暴露但 24 小时内出现的 kill 端点误操作（审计 `instance.process.kill` 对非预期 pid）

## Consequences

- Epic 16 child `#5` 的 `REHEARSAL_REPORT.md` 末尾必须引用本 ADR 的 Cutover Protocol 步骤清单，作为签字前置 checklist
- Slice 2 planning materialization 任务依赖本 ADR 的"One-Way Doors 清单"作为冻结边界——不允许 Slice 2 以"顺便优化"理由改动任一 one-way door 决策
- `EPIC_ROADMAP.md` Slice 1 状态切换动作只能由执行本 ADR Cutover Protocol 步骤 4 的提交完成；其他 PR 默认不允许触碰该状态字段
- 本 ADR 不讨论产品级多环境 / 多租户的 cutover（Slice 4 才涉及）；本切片只面向内部单环境单组织
