# Epic Specification

## Goal

- 交付 `MySQL-first`、内部单租户、phase-one 数据库监控平台的完整开发 epic，使后续实现可以沿着明确依赖关系推进，从仓库基础设施一路落到认证、实例接入、指标采集、分析查询、基础告警和前端主流程。

## Non-Goals

- 兼容或迁移 Lepus 旧运行时、旧表结构或旧进程模型
- 多引擎并行交付，包括 Oracle、Redis、MongoDB、SQL Server、OS 监控
- 多租户、复杂规则 DSL、慢查询深度分析、备份监控、Bigtable 扫描、高级报表
- 容器优先开发模式或将业务逻辑放进 Next.js

## Constraints

- 技术栈必须遵守已批准方向：`Next.js + React + Tailwind CSS v4 + shadcn/ui + ECharts + TanStack Query`
- `FastAPI` 是唯一业务 API 边界，内部必须保持 `router -> service -> repository`
- 存储从第一天起拆分为 `PostgreSQL + ClickHouse + Redis`
- MySQL phase one 必须是 `agentless`，运行时采用 `scheduler + typed workers`
- API 契约必须 `OpenAPI-first`，并生成前端类型化客户端
- 开发方式必须 `local-first`，数据库测试环境可以使用 `docker compose`
- 不允许为了“先跑起来”而引入静默 fallback、mock 成功路径或兼容胶水代码

## Risk Assessment

- 控制面与分析面分库分存储，若边界设计不清，容易在资产状态、指标写入和告警状态之间出现一致性问题
- MySQL 指标标准化与最小权限要求若界定不清，worker 可能难以在不同实例类型上稳定运行
- 认证/RBAC 若晚于资产接入落地，后续控制面接口容易返工
- OpenAPI 生成与前端客户端不同步会直接造成契约漂移
- 本地开发同时涉及 Node、Python、PostgreSQL、ClickHouse、Redis、MySQL，若根级脚本和验证门禁缺失，团队启动成本会持续偏高

## Child Deliverables

- 建立 monorepo 基础设施、根级工具链和本地开发基线
- 实现认证、会话和 RBAC 控制面基础
- 实现 MySQL 资产接入、连接校验和控制面 API
- 实现 scheduler、Redis 分发和 agentless MySQL 指标采集链路
- 实现概览和实例详情所需的分析查询 API
- 实现基础规则评估、告警生命周期和通知边界
- 实现前端应用壳、认证接入和 OpenAPI 生成客户端
- 实现 phase-one 核心页面与交互流
- 实现最终契约检查、集成测试和端到端冒烟门禁

## Dependency Notes

- 子任务 `#1` 是后续所有实现的基础
- 子任务 `#2` 和 `#7` 依赖 `#1`
- 子任务 `#3` 依赖 `#1;#2`，因为资产接入必须在受控身份边界后暴露
- 子任务 `#4` 依赖 `#1;#3`，因为调度和 worker 需要消费正式的资产与连接配置
- 子任务 `#5` 依赖 `#3;#4`，因为分析 API 同时需要控制面元数据和 ClickHouse 指标
- 子任务 `#6` 依赖 `#3;#4`，因为规则评估建立在规则定义与归一化指标之上
- 子任务 `#8` 依赖 `#3;#5;#6;#7`，并复用 `#2` 已建立的认证能力
- 子任务 `#9` 依赖 `#2;#3;#4;#5;#6;#7;#8`

## Child Task Types

- `single-full`

## Roadmap Position

- 这是产品路线图中的 `Epic 01: MySQL-First Phase One Control Plane`
- 它的职责是建立可运行的 phase-one 闭环，而不是一次性证明平台未来所有方向
- 默认交接目标是 `Epic 02: Operational Hardening and Delivery Readiness`

## Default Handoff

- 当本 epic 的 `Done-When` 满足后，默认进入 `Operational Hardening and Delivery Readiness`
- 理由不是“功能已经够多”，而是 phase-one 之后最容易暴露的真实瓶颈，通常在：
  发布与迁移安全、任务幂等、失败恢复、平台自监控、运行诊断和 release gate

## Post-Phase Decision Gate

- 关闭本 epic 前，必须做一次显式 close-out review，而不是直接启动下一个实现任务
- 如果主问题集中在部署、升级、恢复、诊断、平台自监控，进入 `Epic 02`
- 如果主问题集中在告警噪音、恢复语义、通知可靠性和值班流程，可改序进入 `Epic 03`
- 如果主问题集中在趋势洞察、容量视图和分析深度，而平台本身已足够稳，可改序进入 `Epic 04`
- `Epic 05` 只有在 MySQL 模型稳定且明确选定第二引擎后才允许启动
- `Epic 06` 在单租户成为真实业务阻塞前保持 deferred，不得因预防性设计提前开启

## Handoff Inputs

- 完整的 root-level 验证结果，包括契约、集成和 smoke 输出
- 对控制面、数据面和前端主路径的已知缺陷清单
- 对运行稳定性、告警质量和分析缺口的 close-out 评估
- 对 MySQL 指标模型、资产模型和告警模型是否稳定的架构复盘

## Done-When

- [ ] `SUBTASKS.csv` 中所有子任务均为 `DONE`
- [ ] 主路径 `登录 -> 接入 MySQL 实例 -> 查看 dashboard -> 查看实例详情 -> 查看告警/规则 -> 修改系统设置` 可通过 smoke 流程验证
- [ ] OpenAPI 契约检查、后端集成测试、前端 smoke 测试和根级质量门禁全部通过
