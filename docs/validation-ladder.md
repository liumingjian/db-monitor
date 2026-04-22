# Slice 1 — Validation Ladder (L0 / L1 / L2)

Status: working artifact（随 Slice 1 实施更新）  
Scope: Epic 15 + Epic 16 的全部验证命令，按反馈回路速度分层  
Purpose: 防止"L0 没稳 → 直接冲 L2"浪费 CI / 真实环境时间；显式标注哪些风险**只能**在 L2 看得见——这些风险不允许靠 L0/L1 通过就声称完成

## L0 — Fast Feedback Loop

秒-分钟级本地命令；任何 child 任务开始实现后必须先打通 L0。

| 命令 | 覆盖面 | 必跑场景 |
|---|---|---|
| `pnpm lint` | web / packages biome 静态检查 | 任何前端改动 |
| `pnpm typecheck` | `packages/api-client` + `packages/ui` + `apps/web` TS 类型 | OpenAPI snapshot 或 typed client 再生后 |
| `pnpm openapi:check` | `contracts/openapi.snapshot.json` 与实际路由一致 | 任何 API 新增 / 字段扩展 |
| `uv run pytest tests/api/runtime -q` | runtime inspection API 单元测试（Epic 15 child `#1..#4`） | API 路由 / service 改动 |
| `uv run pytest tests/rule_engine -q` | rule-engine 评估逻辑单元测试（含 overrides LEFT JOIN） | Epic 15 child `#5` 或相关重构 |
| `uv run pytest tests/schema -q` | ClickHouse / PostgreSQL DDL 契约（非实连） | 任何 schema DDL 改动 |

**规则**：L0 不稳定不进 L1。出现 flake 先按 CSE SKILL §4.2 去噪，不进 L2。

## L1 — Medium Integration Loop

分钟级；跑真实 bootstrap 但不触发完整 signoff gate。

| 命令 | 覆盖面 | 必跑场景 |
|---|---|---|
| `pnpm test:schema:bootstrap` | PG + CH schema bootstrap 真实建库 | Epic 15 child `#1`/`#3`/`#4`/`#5` 的 schema 落地 |
| `pnpm test:integration` | `tests/integration/` 跨模块集成 | rule-engine + Notifier 联动（Epic 16 child `#4`） |
| `pnpm test:control-plane:postgres` | API + PG 真连接 | overrides API 的真实 SQL 行为 |
| `pnpm test:analytics:clickhouse` | API + CH 真连接 | processlist / slow-query / tablespace 列表查询的真实分区行为 |
| `pnpm smoke:web` | playwright 走通主路径 | 任一新 UI tab 上线后（processlist / slow queries / tablespaces / rule overrides） |

**规则**：L1 暴露的失败**禁止**通过"L0 绿了所以问题在环境"绕过——先按 SKILL §4.3 的 schema-sensitive 规则分语义/契约/真实三层定位。

## L2 — Slow Signoff Loop

十分钟-小时级；发布门禁。

| 命令 | 覆盖面 | 必跑场景 |
|---|---|---|
| `pnpm test:hardening:signoff` | 平台级 hardening 回归 | Epic 15 child `#6` offline signoff |
| `pnpm test:alert-maturity:signoff` | 告警链路回归 | Epic 16 child `#4` 完成后 |
| `pnpm test:oracle-runtime:signoff` | Oracle runtime 回归 | Epic 15 child `#4` 完成后 |
| `pnpm test:launch-readiness:signoff` | launch readiness 整体回归 | Epic 15 / Epic 16 收尾前 |
| **真实值班演练（Epic 16 child `#5`）** | 4 故障场景 × 端到端 | Slice 1 投产签字，**无法**用自动化 gate 替代 |

## Only-L2-Visible Risks

下列风险**只能**在 L2 或真实演练中看见，L0/L1 全绿**不蕴含**这些风险已解决——必须在 Epic 15 / Epic 16 的 close-out 中显式对照：

1. **ClickHouse 采集写入瞬时峰值压垮连接池**（ADR-0005 容量估算的真实验证）  
   观测：worker 插入 QPS、CH 连接数；L1 的 bootstrap 只建表不灌流量。

2. **performance_schema 环形缓冲 miss**（ADR-0007 被监控实例侧副作用）  
   观测：MySQL `events_statements_summary_global_by_event_name` 在并发下的丢失率；单测用 fixture 无法复现。

3. **Override LEFT JOIN 在规则详情 API 响应路径上的 p95 回归**（Control Contract 硬边界：≤10%）  
   观测：`pnpm test:hardening:signoff` 的性能基线对比；L0 单测看不出延迟分布。

4. **kill 端点对真实 MySQL 连接的副作用**（ADR-0006 安全网最小化范围）  
   观测：被监控实例 `Com_kill` 计数 + 审计 `instance.process.kill`；单测用 stub 不能触达。

5. **Notifier fire-and-forget task 队列膨胀**（ADR-0009 将定义 anti-windup 上界）  
   观测：进程级任务计数 / 内存；rule-engine 评估 p95；只有长时间运行才显现。

6. **飞书 webhook 速率限制 / SMTP 发件人信誉**（外部约束）  
   观测：`notify_history.error` 分布；演练时才真实触达外部。

**规则**：任一 Only-L2-Visible Risk 在 close-out review 时未拿到对照证据 → 默认判"未验证"而非"已通过"；CSE SKILL §6 "把离线测试当 gate" 是高风险反模式，必须避免。
