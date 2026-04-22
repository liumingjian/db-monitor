# ADR-0004: Per-instance threshold overrides via association table

Status: accepted (2026-04-22)

切片 1 需要支持"同一条规则、实例 A 阈值 900、实例 B 阈值 950、实例 C 关闭"这样的粒度（100 实例规模下全局规则必然误报泛滥）。在扩 rule 表 JSON 列 (A)、新建 `rule_instance_overrides` 关联表 (B)、把阈值迁回 instance 表 (C)、引入 rule_bindings 模板-binding 模型 (D) 之间，选定 **B**：新表 `rule_instance_overrides(rule_id FK, instance_id FK, threshold NUMERIC NULL, enabled BOOLEAN NULL, updated_at, PRIMARY KEY (rule_id, instance_id))`。override 字段仅限 `threshold` 和 `enabled`；severity/evaluation_window 不做 override（lepus 也没有，场景罕见）。overrides 内嵌在规则详情 API 响应里（不单独开端点）；web 侧子表逐条编辑；所有增删改走 `AuditService`，action 名 `alert.rule.override.upsert` / `alert.rule.override.delete`。rule-engine 评估 `(rule, instance)` 对时 `LEFT JOIN rule_instance_overrides`，用 COALESCE 拿到最终阈值。

## Considered Options

- **方案 A（rule 表加 JSONB overrides 列）**：被拒。JSON 列没有外键约束，instance 删除后留脏数据；lepus 的 schema drift 问题就是从这种"松散真相"长出来的（RESEARCH.md 第 5 条 Legacy Problem），不抄。
- **方案 C（阈值迁回 instance 表）**：被拒。等于把 UI/配置/告警重新绑到同一张表，就是 lepus 最早出问题的耦合模式（ADR-0001 里已经把这个架构明确作废）。双真相源扩到第三引擎时会再爆炸。
- **方案 D（rule_bindings 模板-binding 模型）**：被拒。对切片 1 太重；模板-binding 是值得的抽象，但应等到切片 3 (OS) 或切片 5 (MySQL 深度) 出现真实复用需求时再提取，不应提前引入。

## Consequences

- rule 表结构不动；`rule.threshold` 继续是默认阈值，`rule.instance_ids[]` 继续表示"作用域"，overrides 表表示"作用域内的例外"。三层职责正交。
- 所有后续引擎（OS/SQLServer/MySQL 深度/Oracle 深度）共用这套 schema，不需要每次新引擎时改 rule 表。
- instance 删除走 FK CASCADE，自动清理其 overrides；不需要应用层补偿。
- rule-engine evaluation 增加一次 LEFT JOIN；在 100 实例 × 若干规则的数据量下成本可忽略。
- OpenAPI 里 `RuleDetailResponse` 新增 `overrides: List[RuleInstanceOverride]` 字段，typed client 同步再生；这是一次非破坏性扩展，不影响已有调用方。
