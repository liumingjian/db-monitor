# Epic 16 Slice 1 投产 Handoff 手册

> 交付日期: 2026-04-22
> 交付范围: Epic 16 child #1-#4（代码侧全部 DONE）
> 未含范围: child #5 真人 DBA 演练 + 凭据配置（Boss 侧人工 gate）

## 0. 一分钟结论

- 代码侧 Done-When gate（#1/#3）已全部达成
- `pnpm test:hardening:signoff` 的离线半段（lint / typecheck / ruff / mypy / pytest）一次过
- 剩下仅人工 gate：**凭据配置 + 4 小时 DBA 演练 + 签字**，这两项按 Boss 规划不在本交付内
- 本手册给出 Boss 可以一把验证的命令 + 期望输出 + 失败兜底

## 1. 一键验证（推荐 Boss 直接跑这一条）

```powershell
pnpm openapi:check
pnpm test:notifier:signoff
pnpm test:hardening:signoff  # 其中 readiness/schema/recovery/smoke 段需要本机起 compose 依赖
```

期望终态：

- `openapi:check` → `OpenAPI snapshot matches`
- `test:notifier:signoff` → openapi ✓ / 102 pytest ✓ / pnpm test 72 ✓ / typecheck ✓
- `test:hardening:signoff`：离线段（lint / typecheck / ruff / mypy 187 files / pytest 273）**本 handoff 交付当日已一次过**；后半段依赖本机 compose，Boss 跑之前请确认 docker 可用

若某条失败，优先看"第 6 节 失败兜底"。

## 2. 可独立核对的证据点

| 证据 | 命令 | 预期 |
|---|---|---|
| notifier 合流测试 | `uv run pytest tests/alerting_notification -q` | 41 passed |
| 背压护栏 | `uv run pytest tests/rule_engine/test_dispatch_backpressure.py -q` | 1 passed（0.5s 内完成） |
| 告警回归 | `uv run pytest tests/alerting_contract tests/alerting_workflow tests/alerting_noise tests/alerting_delivery tests/api/alerting -q` | 全 passed |
| Schema v11 | `uv run pytest tests/schema/test_schema_bootstrap.py -q` | alert_channel_bindings + notify_history 断言通过 |
| 类型完整 | `uv run mypy apps tests gates` | 187 source files, no issues |
| 全量 pytest | `uv run pytest tests -q` | 273 passed in ~10s |
| OpenAPI 契约 | `pnpm openapi:check` | snapshot matches |

这些都是 **纯离线** 证据，Boss 在自己的机器上执行即可复现。

## 3. 这次交付做了什么（Epic 16 child #1-#4）

### 3.1 新增核心代码

```
apps/api/src/db_monitor_api/alerting/notification/
├── __init__.py              # 统一出口（ChannelRegistry/DispatchCoordinator/...）
├── protocol.py              # Notifier Protocol + NotifyPayload/NotifyResult/NotifyStatus
├── registry.py              # ChannelRegistry + 错误类型
├── service.py               # RuleHitEvent/ChannelBinding/BindingRepository + dispatch
├── fallback.py              # dispatch_with_fallback（feishu→smtp 同事件内降级）
├── coordinator.py           # DispatchCoordinator + RuleHitSink + NullRuleHitSink
├── repository.py            # NotifyHistoryRepository + InMemory 实现
├── bindings.py              # InMemoryBindingRepository
├── query_service.py         # NotifyHistoryService（admin 查询用）
├── router.py                # GET /admin/notify-history
└── channels/
    ├── feishu.py            # 飞书富卡片 + HMAC 签名 + @成员 + 指数退避
    ├── smtp.py              # SMTP multipart HTML + stdlib smtplib
    └── smtp_settings.py     # DB_MONITOR_SMTP_* 环境变量读取
```

### 3.2 改动到既有模块

| 文件 | 改动 |
|---|---|
| `alerting/evaluation.py` | 新增 `rule_hit_sink` 旁路参数（默认 NullRuleHitSink），不动原 notifier 路径 |
| `alerting/service.py` | `AlertingService.rule_hit_sink` 字段 |
| `bootstrap.py` | 装配 ChannelRegistry + InMemoryBindingRepository + DispatchCoordinator(max=128) → AlertingService |
| `runtime.py` | 新增 `notify_history_service` |
| `app.py` | 挂载 notify-history router |
| `db_monitor_schema/contract.py` | schema version 10 → 11 |
| `db_monitor_schema/postgres.py` | 新增 alert_channel_bindings + notify_history 表 + 索引 |
| `packages/api-client/src/index.ts` | listNotifyHistory + API_CONTRACT_VERSION 0.15.0 |
| `apps/web/app/admin/notify-history/page.tsx` | 新增只读管理面 |
| `contracts/openapi.snapshot.json` | 新增 /admin/notify-history endpoint |

### 3.3 新增 Gate 脚本

- `scripts/test-notifier-signoff.ps1`
- `package.json` → `pnpm test:notifier:signoff`
- `scripts/powershell_shim.py` 注册 `handle_notifier_signoff`

## 4. 投产前仍需 Boss 执行的两件事（**本次交付未含**）

### 4.1 凭据 / binding 配置

两种做法任选：

**A. 环境变量（SMTP 端必须）**

```powershell
# 备用通道 SMTP —— 必填
$env:DB_MONITOR_SMTP_HOST = "smtp.example.com"
$env:DB_MONITOR_SMTP_PORT = "587"
$env:DB_MONITOR_SMTP_USERNAME = "<user>"
$env:DB_MONITOR_SMTP_PASSWORD = "<pass>"
$env:DB_MONITOR_SMTP_SENDER = "alerts@example.com"
$env:DB_MONITOR_SMTP_USE_TLS = "true"
```

环境变量未全的时候 `SMTPSettings.from_env()` 返回 `None`，SMTP 通道不会注册 → 降级只会写 `notify_history.skipped`，不会误投邮件。

**B. binding 注入（主通道飞书 webhook）**

代码侧当前 `InMemoryBindingRepository` 在 bootstrap 里是空的。正式投产前 Boss 需要：

1. 决定接入方式：继续 in-memory（重启丢失） / 落 Postgres（已有 `alert_channel_bindings` 表，仓储尚未实现）
2. 如果短期就用内存态，可以在 bootstrap 里临时 register：

```python
binding_repository.register(
    rule_id="<你的规则id>",
    channel="feishu",
    config={
        "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/<token>",
        "secret": "<signing secret>",        # 飞书卡片校验签名
        "at_user_ids": ["ou_xxx"],          # 可选 @成员
    },
)
binding_repository.register(
    rule_id="<你的规则id>",
    channel="smtp",
    config={"to": ["oncall@example.com"]},
)
```

> ⚠️ 注入代码里 **不要** 写死 webhook/secret，应当走 env。当前 bootstrap 没有读 env 的分支 —— 属于"投产前需要加"的小尾巴，但本次交付按 Boss 口径不做实现。

### 4.2 4 小时真人值班演练（child #5）

见 `EPIC.md` 第 5 节的 4 个剧本：
1. MySQL 连接数打满
2. MySQL 主从复制延迟
3. MySQL 慢查询 kill 回路
4. Oracle 表空间 > 85%

产物：`.codex-tasks/20260422-slice01-epic16-notifier-reality/REHEARSAL_REPORT.md`（DBA 文本签字）。

## 5. Boss 自检 Checklist（勾完即本次交付范围合格）

- [ ] `pnpm openapi:check` → `OpenAPI snapshot matches`
- [ ] `uv run pytest tests -q` → `273 passed`
- [ ] `uv run mypy apps tests gates` → `no issues found in 187 source files`
- [ ] `pnpm lint` → `No fixes applied` / 0 errors
- [ ] `pnpm typecheck` → 全路径无错
- [ ] `pnpm test:notifier:signoff` → 全绿
- [ ] `tests/schema/test_schema_bootstrap.py` 断言包含 `alert_channel_bindings` 与 `notify_history`
- [ ] 手开 `apps/api/src/db_monitor_api/alerting/notification/` 目录，确认 11 个 .py 文件 + channels/ 3 个
- [ ] `packages/api-client/src/index.ts` 中 `API_CONTRACT_VERSION` 为 `"0.15.0"`，含 `listNotifyHistory`
- [ ] `contracts/openapi.snapshot.json` 包含 `/admin/notify-history` 路径

## 6. 失败兜底

| 症状 | 根因 / 行动 |
|---|---|
| `openapi:check` 报 diff | 说明有人动了路由又没跑 `pnpm openapi:update`；对比 diff 再决定是漏更新还是真改了契约 |
| `mypy` 报 `Cannot find implementation` | 从仓库根跑，不要进 `apps/api/src` 跑；PYTHONPATH 走 `pyproject.toml` 的 mypy 配置 |
| `test_dispatch_backpressure` 超时 > 5s | 本机慢或 0.5s 慢 sink 被放大；重跑一次确认；如持续，检查是否被别的进程抢 CPU |
| `notify_history` 表缺失 | 重启 api 会自动建表（`_bootstrap_notification_tables`）；若手工 psql 清过库，走 `test:schema:bootstrap` 重建 |
| SMTP 通道"莫名不发" | `DB_MONITOR_SMTP_*` 有一个没配就全链路降级为 skipped；`echo $env:DB_MONITOR_SMTP_HOST` 自检 |
| 飞书报 `sign verify fail` | binding config 的 `secret` 对不上，不是代码 bug；飞书 webhook 后台看签名是否开 |
| `admin/notify-history` 403 | 当前账号缺 `SETTINGS_READ` 权限；用 admin seed 账号登录 |
| 背压测试出现 `slow_calls == 0` | 事件循环没把 create_task 起起来；一般是被 0 yield 抢光 CPU；把 `_SAMPLE_ITERATIONS` 减半或在测试里加 `await asyncio.sleep(0)` |

## 7. 投产后观察面

- `GET /admin/notify-history?limit=50`：最近 50 条投递记录
- `GET /admin/notify-history?status=failed&rule_id=...`：逐规则排障
- `GET /admin/notify-history?channel=smtp`：看降级通道是否真的接过手
- PG 表 `notify_history`：直接 SQL 做更深分析（payload_hash、attempt、error 列齐全）

## 8. 本次交付不做、但已为之留点的扩展

| 扩展 | 预留点 | 触发时机 |
|---|---|---|
| Postgres 版 `alert_channel_bindings` 仓储 | schema 已建表；只差 `PostgresBindingRepository` 实现 | 需要 binding 持久化跨重启时 |
| 从 env/settings 注入 binding | 本次 bootstrap 是空 binding | Boss 决定正式投产前的 binding 接入方案 |
| WeCom / SMS 通道 | `ChannelRegistry` 已是 pluggable 架构 | Slice 2 |
| Notifier 限流 / 抑制 | `DispatchCoordinator` 只管 anti-windup | Slice 3（告警生命周期切片） |
| 失败重放 | `notify_history.status=failed` 查询已就位 | Slice 3 |

---

**本手册之外的任何承诺（例如"投产就绪"）一律不成立**：Done-When gate #4/#5/#6 仍由人工演练 + CONTEXT/ROADMAP 回写承担，这三项 Boss 安排真人演练完成后再写入。
