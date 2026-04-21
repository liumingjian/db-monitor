# Epic Specification

## Goal

- 在不打断当前单组织默认路径的前提下，把平台从“内部单租户约定”推进到“显式组织治理边界”，让 auth、RBAC、控制面、告警面和 web surface 都能围绕同一个组织事实源收敛

## Why This Epic Is Next

- 这不是 roadmap 的默认 next，而是一次显式的产品方向激活
- Epic 05 已证明当前平台边界可以承载第二引擎试金石，原先保留的 Oracle live gate 也已由 follow-up 任务关闭
- 用户已明确批准激活 `Epic 06: Tenant and Organization Governance`
- 这条批准构成了跨越 `PRD.md` 单租户冻结边界的显式授权，因此可以从 deferred 状态进入执行

## Scope

- 冻结当前组织治理的最小边界：组织身份、成员关系、活动组织上下文和组织级访问事实源
- 让 auth / session / RBAC 显式携带组织上下文，而不是继续隐含“全局唯一工作区”
- 让控制面资产、设置、告警与审计逐步挂到组织事实源
- 在 API / OpenAPI / typed client / web shell 中暴露组织上下文与最小治理入口
- 为本 epic 建立根级 signoff 证据链

## Non-Goals

- 不引入账单、配额、商业 SaaS 多租户或自助注册体系
- 不在本 epic 内追求跨组织物理数据隔离或独立部署编排
- 不引入复杂的组织层级、策略 DSL 或共享协作模型
- 不因为治理扩展而回退当前单组织默认路径

## Done-When

- 团队可以明确回答“哪些事实已经按组织收敛，哪些仍是全局共享”
- auth/session、控制面、告警与 web 主路径都能显式识别活动组织
- 当前单组织默认路径仍然可运行，不因治理引入而失真

## Close-Out Review

- Epic 05 证明了什么：
  - 平台关键边界已经从 `mysql-only` 推进到 `engine-aware`
  - Oracle 第二引擎试金石已具备最小 onboarding / validation / live-gate 证据
  - MySQL 主链没有因第二引擎试金石被回归打坏
- Epic 05 没证明什么：
  - 当前产品是否已经具备显式组织治理边界
  - auth / RBAC / 控制面 / 告警 / web 是否能在组织上下文下保持一致
  - 单组织约定是否还能继续作为隐式事实源
- 默认下一个 epic：
  - 路线图中唯一剩余 epic 是 `Epic 06: Tenant and Organization Governance`
- 为什么现在激活：
  - 用户已明确批准跨越当前 `PRD.md` 的单租户冻结边界
  - 这次激活是产品方向选择，不是技术实现中的顺手扩张
- 什么证据才会支持不激活：
  - 如果用户没有显式批准组织 / 租户治理，正确动作应是保持 roadmap 关闭，而不是伪造新的默认方向

## Child Deliverables

- 完成 Epic 05 close-out 交接，并把 Epic 06 激活为新的 truth source
- 冻结组织身份与活动组织会话契约
- 建立组织 / 成员关系的 Postgres schema 与 bootstrap 基线
- 让控制面资产与设置显式挂到组织上下文
- 让告警、工作流与审计记录显式挂到组织上下文
- 在 API / OpenAPI / typed client / web shell 中暴露组织治理最小入口
- 汇总治理 signoff gates 作为阶段签收入口

## Dependency Notes

- 子任务 `#1` 负责 close-out review 与 epic 激活收口
- 子任务 `#2` 是所有后续组织治理工作的身份契约基础
- 子任务 `#3` 依赖 `#2`
- 子任务 `#4` 依赖 `#2;#3`
- 子任务 `#5` 依赖 `#2;#3;#4`
- 子任务 `#6` 依赖 `#2;#3;#4;#5`
- 子任务 `#7` 依赖 `#2;#3;#4;#5;#6`

## Child Task Types

- `single-full`
