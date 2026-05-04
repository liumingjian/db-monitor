# ADR-0006: Runtime action permission separated from write; kill safety net minimized in slice 1

Status: accepted (2026-04-22)

运行时命令（kill、reload、flush 等"对被监控实例产生副作用"的调用）不复用 `Permission.INSTANCES_WRITE`（WRITE 是配置修改语义），而是**新增 `Permission.INSTANCES_ACTION`**，由 admin/operator 持有。viewer 不持有。第一个实际使用的端点是 `POST /instances/{instance_id}/processlist/{process_id}/kill`，审计 action 命名规则 `instance.<resource>.<verb>`（如 `instance.process.kill`）。切片 1 的 kill 安全网最小化：只禁止 kill 监控用户自己建立的连接（防踢掉采集器）+ 实例 `validation_status != PASSED` 时前端按钮禁用；**系统/复制连接（binlog dump 等）的保护推到切片 5**。

## Considered Options

- **复用 `Permission.INSTANCES_WRITE`**：被拒。WRITE 语义是"修改实例配置"，kill 是"对运行中实例下命令"，语义不同；复用会让 operator 的权限面混乱（改连接参数 vs 踢别人的连接，应该是独立决策）。
- **切片 1 就做系统连接保护**：被拒。需要识别"binlog dump"、"系统用户"、"replication channel"等多种连接类型，跨 MySQL 版本行为不一致；不是切片 1 能稳收口的范围。切片 5 做 MySQL 深度层时一起做。

## Consequences

- `Permission` 枚举新增 `INSTANCES_ACTION`；角色默认矩阵更新：admin 和 operator 持有，viewer 不持有。
- 所有后续引擎的运行时命令（OS reboot？Oracle kill session、SQLServer kill spid 等）统一走 `INSTANCES_ACTION`；如果某命令危险等级明显更高（如 OS reboot），届时再拆更细，不在切片 1 做。
- kill 端点路径格式统一为 `/instances/{instance_id}/<resource>/<resource_id>/<verb>`，不走 `/actions/xxx` 的模式——前者更 RESTful，也和现有 `/instances/{id}/validate` 风格一致。
- 切片 5 必须回补系统/复制连接保护；在 `docs/adr/` 开新 ADR 时需要显式 supersede 本 ADR 的"切片 1 最小安全网"条款。
- 审计 action 规范：`instance.<resource>.<verb>`；资源名选单数（process, session, replica-link, ...）；verb 采用动词原型（kill, reload, flush, restart...）。
