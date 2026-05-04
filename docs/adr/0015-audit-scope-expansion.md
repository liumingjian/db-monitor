# ADR-0015: Audit Scope Expansion

> Status: Draft（Slice 2 Epic 起步前 Boss 决议后转 Accepted）
> Date: 2026-05-04
> Supersedes: 无
> Related: Epic 10（PRD debt closeout 引入了 audit_entries 表）；Epic 15 引入 `instance.process.kill` 审计；Epic 16 引入 `notify_history` 表

## Context

当前审计覆盖：

- `audit_entries` 表（来自 Epic 10）：用户登录、用户角色变更、组织成员变更
- `instance.process.kill`（来自 Epic 15）：MySQL kill 操作
- `notify_history`（来自 Epic 16）：告警投递记录（事实上也是审计的一种）

`CONTEXT.md` Slice 2 范围：审计范围扩展。当前缺口：

- **规则改动**：rule.create / rule.update / rule.delete / override.update / override.delete 全无审计 → DBA 改了阈值无人知道
- **实例配置改动**：实例新增 / 删除 / 验证状态变化 / 阈值 override 全无审计
- **通道 binding 改动**：alert_channel_bindings 写入 / 删除（即使 PostgresBindingRepository 还在 Slice 3，binding 注入操作本身需要审计）
- **抑制窗口配置改动**：ADR-0014 引入的 `suppression_window_seconds` 改动也属于规则改动审计的一部分

## Decision

### 1. 审计动作类型

`audit_entries.action` 枚举扩展（在已有的 `auth.login` / `user.role.update` / `instance.process.kill` 基础上新增）：

| Action | Trigger | Target | Diff fields |
|---|---|---|---|
| `rule.create` | POST /alerts/rules | rule_id | full rule object |
| `rule.update` | PATCH /alerts/rules/{id} | rule_id | changed fields only |
| `rule.delete` | DELETE /alerts/rules/{id} | rule_id | (none, action records deletion) |
| `rule.override.upsert` | PUT /alerts/rules/{id}/overrides/{instance_id} | rule_id+instance_id | threshold/enabled before/after |
| `rule.override.delete` | DELETE /alerts/rules/{id}/overrides/{instance_id} | rule_id+instance_id | (none) |
| `instance.create` | POST /control/instances | instance_id | full instance object |
| `instance.update` | PATCH /control/instances/{id} | instance_id | changed fields only |
| `instance.delete` | DELETE /control/instances/{id} | instance_id | (none) |
| `instance.validation.update` | (system, after validation run) | instance_id | validation_state before/after |
| `channel_binding.create` | POST /admin/channel-bindings | binding_id | rule_id + channel + config_hash |
| `channel_binding.delete` | DELETE /admin/channel-bindings/{id} | binding_id | (none) |

注意：`channel_binding.config` 含 webhook/secret，**不**进 audit；只记 `config_hash`（SHA256）

### 2. 审计 Schema

- `audit_entries` 现有表保持不变；不新增表
- 新增 `audit_entries.target_type ENUM('user','rule','instance','process','channel_binding','organization')` 字段（NOT NULL，default `''` 兼容）
- 新增 `audit_entries.diff_summary JSONB NULL` 字段，存 changed fields before/after
- `audit_entries.actor_user_id` 保留；系统触发 = NULL + `actor_subject='system'`
- schema version v12 → v13（与 ADR-0014 一并）

### 3. 注入点

- 不在 router 层手写审计调用（容易漏）
- 在 service 层用 `@audited(action='rule.update', diff=...)` 装饰器或 explicit `audit_service.log(...)` 调用
- 系统触发的审计（如 `instance.validation.update`）走 worker / scheduler 层
- 失败的请求**不**写审计（HTTP 4xx/5xx 不入表，防止审计被攻击者用来污染日志）

### 4. 查询 Surface

- `/admin/audit?actor=...&target_type=...&action=...&from=...&to=...`：扩展现有 audit query 接口
- web Audit 页（Slice 1.5 已建）新增 4 个过滤维度：actor / target_type / action / time
- 不做实时 streaming（轮询足够）；不做导出 CSV（推 Slice 8 的报表家族）

### 5. 不做

- 不做完整变更审计（如 ClickHouse 写入审计、worker 调度审计 — 量级太大）
- 不做敏感字段加密（webhook secret 走 hash 而非加密；如果将来需要审计原值，得 ADR 重审）
- 不做基于审计的告警（如"30 分钟内有人改了 5 条 rule"— 推 Slice 3+）
- 不做审计回放 / undo（audit 是事实记录，不是事务日志）

## Consequences

### Positive

- DBA 改阈值 / 改 binding 都有可追溯链
- 客户验收时可以一把展示"系统所有写操作都有审计"
- 现有 `audit_entries` 表复用，不引入新存储

### Negative / Tradeoff

- 写路径每个写 endpoint + 1 条审计写入；估算 < 0.5ms/req，对 p99 影响可忽略
- audit_entries 表行数增长会更快；现有 TTL = 永久，需要 Slice 3+ 加 TTL 或归档策略
- 装饰器 / explicit 调用混用模式需要在 review 阶段检查"是不是漏了一个写 endpoint"

### Risks

- `diff_summary` 中存的 before 值可能含敏感配置（如阈值规则名 = 业务敏感词）；审计读权限必须严格 = `SETTINGS_READ`
- 如果未来需要审计 worker 内部状态变化（如 collector 抛出错误），diff_summary JSON 结构可能不够灵活；本 ADR 不解决这一点

## Decision Window

- 2026-05-04 起草
- Slice 2 Epic 起步前 Boss 决议；锁定后转 Accepted
