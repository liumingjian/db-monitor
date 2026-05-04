# Slice 1 投产值班演练报告（占位）

> 状态: **PENDING**（演练未开始）
> 计划窗口: 客户验收前 4 小时窗口
> 决议: 2026-04-22 Boss 决议 child #5 DEFERRED 至客户验收前；占位文件先固化以避免遗忘
> 模板锁定: 4 场景必填 + `签字:` 行 + 每场景 PASS/FAIL 显式标注

## 演练规则

1. 由 1 名值班 DBA 真人执行，时长 4 小时
2. 每个场景必须走完闭环：**故障注入 → 飞书告警送达 → DBA web 上看到 → 采取动作 → 告警消除**
3. 任一场景未走完即视为 **FAIL**；不允许"补一下"
4. 演练中发现的新问题**只记录不修**（进 Slice 2/3 决策）
5. 4 场景全 PASS 后由 DBA 在末尾以纯文本方式签字（"签字: 姓名 / 日期"）

## 准入条件（演练前必查）

- [ ] `pnpm test:notifier:signoff` 全绿（最近一次运行日期: ____）
- [ ] `pnpm test:hardening:signoff` 全绿
- [ ] 飞书 webhook 凭据已通过 env 注入（`DB_MONITOR_FEISHU_*`）
- [ ] SMTP 凭据已通过 env 注入（`DB_MONITOR_SMTP_*`），`SMTPSettings.from_env()` 不返回 None
- [ ] `alert_channel_bindings` 已为 4 条测试规则注入 binding（feishu 主 / smtp 备）
- [ ] 测试 MySQL 实例 1 台 + 测试 Oracle 实例 1 台 validation=PASSED
- [ ] DBA 已加入飞书测试群、能收到 webhook 推送
- [ ] DBA 已配 web admin 账号、`SETTINGS_READ` + `INSTANCES_ACTION` 权限

## 场景 1 — MySQL 连接数打满

> 对标规则: `mysql.threads_connected > max_connections * 0.9` (severity=critical)

**注入步骤**:
- 在测试 MySQL 上 `for i in $(seq 1 N); do mysql -e "select sleep(600)" &; done` 直至超过 90% max_connections

**期望路径**:
1. ≤30 秒内 db-monitor 评估命中
2. ≤30 秒内飞书群收到告警卡片（含规则名/实例/命中值/跳转链接）
3. DBA 点击跳转 → web 上 alerts 页看到该 alert
4. DBA 进入 instance detail → processes tab → 选择 sleep 连接 → kill
5. 连接数下降 → 告警自动 resolved（≤2 个评估周期内）

**实测结果**:
- 飞书送达延迟: ____ 秒
- web 可见延迟: ____ 秒
- kill 操作是否走审计 (`instance.process.kill`): ____
- 告警自动 resolve 时长: ____
- **状态: PENDING**（演练后改为 PASS / FAIL）

**异常 / 备注**:
- ____

## 场景 2 — MySQL 主从复制延迟

> 对标规则: `mysql.replication.seconds_behind_master > 60` (severity=warning) → 升级 critical at >300

**注入步骤**:
- 在 slave 上 `STOP SLAVE SQL_THREAD;`
- 在 master 上 `pgbench`/`sysbench` 写入约 5 分钟
- `START SLAVE SQL_THREAD;` 让追赶可观察

**期望路径**:
1. seconds_behind_master 上升 → warning 告警送达飞书
2. 持续上涨触及 critical 阈值 → 第二条 critical 告警
3. DBA 检查 web 上的 instance detail replication tab（**Slice 1 占位 tab**，看到"复制详情归 Slice 2"也算通过；只要列表 + 当前延迟可见）
4. SQL_THREAD 启动后延迟下降 → 两条告警依次 resolved

**实测结果**:
- warning 送达延迟: ____ 秒
- critical 升级触发时刻: ____
- 复制 tab Slice 2 占位是否合理: ____
- **状态: PENDING**

**异常 / 备注**:
- ____

## 场景 3 — 慢查询阻塞 + kill 回路

> 对标规则: `mysql.slow_queries.long_running_count > 5` (severity=warning)

**注入步骤**:
- 一个长事务持有热表行锁: `BEGIN; UPDATE hot_table SET v = v + 1 WHERE id = 1;`（不 commit）
- 并发 10 个 session 试图更新同一行（受阻于行锁）
- 注入慢查询: `SELECT SLEEP(120) FROM information_schema.tables LIMIT 1`

**期望路径**:
1. 慢查询命中规则 → 飞书告警
2. processlist 面板出现 N 个 Locked / Statistics / Sleep 状态长进程
3. DBA 在 web 上 sort by time DESC → 选中阻塞源 + 慢查询 → 二次确认（输入 thread_id 精确匹配）→ kill
4. 阻塞链解除；告警 ≤2 个评估周期 resolved

**实测结果**:
- 慢查询 tab 是否能直接看到 SLEEP(120) 那条: ____
- kill dialog 二次确认是否真要求输入 thread_id: ____
- 服务端 confirm_thread_id 校验是否生效（输错被拒绝）: ____
- 审计 `instance.process.kill` 是否落 audit log: ____
- **状态: PENDING**

**异常 / 备注**:
- ____

## 场景 4 — Oracle 表空间 override 触发

> 对标规则: `oracle.tablespace.used_pct > 85` （default=85） + 单 instance override threshold=70

**注入步骤**:
- 选 1 张测试 oracle 表空间已用率约 75% 的实例
- 在 web 上 rules → 该规则 → overrides → 加 override(instance=A, threshold=70, enabled=true)
- 等待评估周期（300 秒）

**期望路径**:
1. 评估命中的是 **override 70%**，不是默认 85%
2. 告警送达飞书 + 邮件（这一场景验证 SMTP 备链路）
3. DBA 扩容 / 添加 datafile 让使用率回落到 65%
4. 告警 resolved；审计能看到"匹配阈值=70 (override)"

**实测结果**:
- 是否使用 override 阈值: ____
- 飞书 + SMTP 双通道是否同时收到: ____
- override 状态在 audit log 是否可追溯: ____
- **状态: PENDING**

**异常 / 备注**:
- ____

## 演练总结

- 4 场景结果汇总: 场景1=____ / 场景2=____ / 场景3=____ / 场景4=____
- 飞书送达 P95: ____ 秒
- SMTP 降级触发次数: ____
- 演练中发现新问题（不修，记入 Slice 2/3 backlog）:
  - ____
- 是否建议 Slice 1 关闭: ____ (Y / N)

## 签字（演练完成后填写）

> 演练 4 场景全部 PASS 时方可填写本节。任一场景 FAIL 不签字、不收口。

签字: ____ / ____（DBA 姓名 / 日期）

## 后续动作

- [ ] 4 场景 PASS 后写 `CONTEXT.md` Slice 1 → done
- [ ] `EPIC_ROADMAP.md` Epic 15 + Epic 16 标 DONE
- [ ] 触发 Slice 2 planning materialization
