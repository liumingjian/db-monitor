# Epic Specification

## Goal

- 把系统从 “phase-one 功能闭环已跑通” 提升到 “具备正式运行时、可探测、可发布、可恢复” 的状态

## Non-Goals

- 不扩展第二种数据库引擎
- 不新增新的业务页面或复杂产品功能
- 不用 silent fallback 或 mock 成功路径伪装稳定性

## Constraints

- 优先修正真实运行时缺口，而不是继续堆离线能力
- 每个子任务都必须给出明确的运行面证据，不允许只停留在单元测试
- 保持现有边界：`FastAPI` 仍是业务 API，`PostgreSQL + ClickHouse + Redis` 责任不混淆

## Close-Out Review

- Phase-one close-out 结论：默认进入 `Operational Hardening and Delivery Readiness`
- 触发原因：
  - 当前主业务逻辑已成形，但后台进程入口和正式运行时配置仍不完整
  - API 默认仍偏向本地内存运行态，真实依赖健康性没有统一探针
  - 下一阶段最大风险在“可运行、可诊断、可恢复”，而不是页面数量不足

## Child Deliverables

- 完成 phase-one close-out review，并把 Epic 02 激活为新的 truth source
- 实现 API 正式运行时配置切换、依赖探针和启动契约
- 实现 scheduler / worker 的可运行进程入口、轮询节奏和失败暴露
- 建立控制面与分析面的 schema bootstrap / version baseline
- 建立核心后台链路的重试、幂等和恢复证据
- 建立发布前检查、运行手册和回滚基线
- 汇总 hardening gates 作为 Epic 02 的阶段签收入口

## Dependency Notes

- 子任务 `#1` 激活 epic 并产出当前阶段的 close-out review
- 子任务 `#2` 是后续后台运行时工作的前提，因为 API 必须先进入可探测的正式运行时
- 子任务 `#3` 依赖 `#2`
- 子任务 `#4` 依赖 `#2;#3`
- 子任务 `#5` 依赖 `#3;#4`
- 子任务 `#6` 依赖 `#2;#3;#4;#5`
- 子任务 `#7` 依赖 `#2;#3;#4;#5;#6`

## Child Task Types

- `single-full`

## Done-When

- [ ] `SUBTASKS.csv` 中所有激活子任务达到其 validation command
- [ ] API 与后台进程具备明确的正式运行时入口、依赖就绪探针和失败暴露
- [ ] 发布、恢复和运行诊断具备可执行的最小操作基线
