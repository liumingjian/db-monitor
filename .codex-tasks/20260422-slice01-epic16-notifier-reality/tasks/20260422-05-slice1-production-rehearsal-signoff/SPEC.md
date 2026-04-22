# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- Slice 1 投产 gate：1 名 DBA 真人值班 4 小时，走完 4 种故障场景的 观测→告警→响应→关闭 闭环
- 产出 `REHEARSAL_REPORT.md`（txt 签字 + 每场景截图或日志）
- 通过后把 `CONTEXT.md` Slice sequence 中 Slice 1 改 `done`

## Scope

### 四个演练场景（必须按序执行）

1. **MySQL 连接数打满**
   - 注入: `sysbench` 或脚本开 ≈90% `max_connections`
   - 期望链路: rule-engine 触发 → 飞书卡片送达（含 instance / 当前值 / 阈值） → DBA 在 web 上看到命中 → kill 若干空闲连接 → 告警自动消除（评估下个窗口 OK）

2. **MySQL 从库复制延迟**
   - 注入: 在从库 `STOP SLAVE SQL_THREAD`，等待 pt-heartbeat lag 累积
   - 期望链路: 告警送达 → web 显示 lag 曲线 → DBA `START SLAVE` → 告警消除

3. **MySQL 慢查询阻塞**
   - 注入: 构造一条 `SELECT ... FOR UPDATE` 长事务 + 另一会话并发写
   - 期望链路: slow query 面板显示 blocker → 告警送达（如果配置了 blocking rule）或由 DBA 主动进 processlist 面板 → 点击 kill → 阻塞解除

4. **Oracle 表空间 > 85%（命中 per-instance override）**
   - 注入: 对某个测试表空间 `alter ... resize`，让 used_pct 超 override 阈值（而非 rule 默认阈值）
   - 期望链路: 告警送达 → 验证命中的是 override 不是默认阈值 → DBA 扩容 → 告警消除

### 每场景必须产出

- 飞书卡片截图或 webhook 日志
- `notify_history` 里对应行（rule_id / channel / status=delivered）
- web UI 截图（命中规则页 + 相关详情面）
- 操作时间线（注入时刻 / 告警送达时刻 / 动作时刻 / 消除时刻）

### 最终交付

- `.codex-tasks/20260422-slice01-epic16-notifier-reality/REHEARSAL_REPORT.md`
  - 每场景一节：时间线 + 观察 + 缺陷 + PASS/FAIL
  - 末尾 DBA 姓名 + 日期签字行
- `CONTEXT.md` Slice sequence 更新: Slice 1 → `done`, Slice 2 → `planned`
- `EPIC_ROADMAP.md` Epic 15 + 16 标 DONE

## Non-Goals

- 不做"同时并发 4 场景"压测
- 不做 7×24 观察
- 不做跨 org 多租户演练（Slice 4）
- 不试图发现 Slice 2+ 要解决的问题，发现了只记录不修

## Final Validation Command

```bash
test -f .codex-tasks/20260422-slice01-epic16-notifier-reality/REHEARSAL_REPORT.md && grep -c "^## 场景" .codex-tasks/20260422-slice01-epic16-notifier-reality/REHEARSAL_REPORT.md | grep -q 4 && grep -q "签字:" .codex-tasks/20260422-slice01-epic16-notifier-reality/REHEARSAL_REPORT.md
```
