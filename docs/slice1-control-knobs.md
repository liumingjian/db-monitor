# Slice 1 — Control Knobs Black-Box Input-Output Matrix

Status: working artifact（随 Epic 15/16 实施更新）  
Scope: Slice 1（Epic 15 + Epic 16）全部暴露给运行期的调整入口  
Purpose: 所有 knob 的默认值、目标输出、外溢方向、观测点集中表；防止参数散落在各 ADR 里被独立调整、导致相邻模块意外打坏

## Matrix

| # | Knob | 默认值 | 目标 output（直接） | 连带 output（外溢） | 影响方向 | 观测点 | 调整窗口 | 主控制器 |
|---|---|---|---|---|---|---|---|---|
| 1 | `instance.processlist_interval_seconds` | `30`（下限 `10`） | processlist 快照新鲜度 | 被监控 MySQL 负载；ClickHouse `mysql_processlist` 写入 QPS；CH 存储容量 | 调小 → 新鲜度↑、负载↑、存储↑ | worker 采集延迟日志；CH `mysql_processlist` 插入率；被监控实例 `Threads_running` | 实例级别可配（ADR-0005） | worker scheduler（同一实例只允许一个采集任务） |
| 2 | `instance.slow_threshold_seconds` | `1.0` | slow query 召回量 | PS 环形缓冲 miss 率；采集 CPU；CH `mysql_slow_query_events` 写入量 | 调小 → 召回↑、miss↑、CPU↑ | worker pull 循环日志；PS `events_statements_summary_global_by_event_name` 观察（演练时） | 实例级别可配（ADR-0007） | worker scheduler |
| 3 | `rule_instance_overrides.threshold` / `.enabled` | `NULL`（继承 rule 默认） | 误报抑制 | rule-engine 评估延迟（LEFT JOIN 额外成本）；overrides 与默认漂移审计复杂度 | 启用 override → 误报↓、审计面↑ | rule-engine p95；`notify_history` 命中速率；audit log `alert.rule.override.*` | API + Web 可编辑（ADR-0004） | rule-engine evaluate path |
| 4 | Notifier 重试次数 / 退避上界 | 本任务 ADR-0009 决定——3 次尝试、指数退避 1s/3s/9s、最大单事件 20s | 送达率 | rule-engine 评估循环回压（若实现不 fire-and-forget）；飞书 webhook 速率限制触发；SMTP 发件人信誉 | 调大次数 → 送达率↑、回压风险↑、外部速率限制命中↑ | `notify_history.attempt/delivered_at/error`；rule-engine p95；飞书 webhook 响应码分布 | settings 级（全局） | notifier.service.dispatch |
| 5 | Kill 端点调用（`POST /instances/{id}/processlist/{pid}/kill`） | N/A（用户动作，非参数） | DBA 处置力；blocker 解除时间 | 监控用户自毁（防护已落 ADR-0006）；复制/系统连接误伤（Slice 5 才修）；被监控实例突发连接释放 | 触发 → 处置↓、自毁风险已防、系统连接误伤仍存 | audit log `instance.process.kill`；被监控实例 `Com_kill` 计数 | 按需触发（admin/operator） | apps/api runtime kill handler |

## Coupling Notes

- **#1 与 #2 的 CH 写入合流**：两者同命运于 ClickHouse `mysql_*` 表组的写入容量。若 #1 调到 `10s` + #2 调到 `0.1s`，CH 写入 QPS 会叠加；必须同时考虑，不能单独拉满。
- **#3 与 #4 的 alert 链路合流**：overrides 只是把命中"转移"到不同规则，不改变命中总量；真正降低 `notify_history` 写入量的是 Notifier 自身的抑制（Slice 3），Slice 1 内 #3 不应承担降噪职责。
- **#5 与 #3 的并发语义**：override 启用后某条规则对某实例关闭 ≠ 该实例无人处置——DBA 仍可能手动 kill。审计面需要同时看 `alert.rule.override.*` 和 `instance.process.kill` 才能拼出完整动作链。

## Reserved for Slice 2+

- 飞书 `at_user_ids` 策略（按 severity 分发）——Slice 2 告警成熟度
- Tablespace 采集频次 300s 的调整窗口——Slice 6 Oracle 深度层
- pt-query-digest 采样窗口——Slice 5 MySQL 深度层

## Change Discipline

- 任一 knob 的默认值调整必须同步更新本表 + 对应 ADR 的"Consequences"节
- 运行期单实例 override 默认值不写入本表（实例级覆盖是 #3 的正常用法，不是 knob 默认变更）
- 演练（Epic 16 child `#5`）中若观察到外溢超预期，先在本表登记观察，再开新 ADR 锁定新的默认值——不允许直接热改 settings 后静默消化
