# Progress

## Summary

- Task shape: single-full
- Goal: 将 Oracle XE 纳入当前仓库的 macOS 本地基础设施，并补齐真实 Oracle live control-plane gate

## Recovery

- 任务: 关闭 Epic 05 明确保留的 Oracle live gate 缺口
- 形态: single-full
- 进度: 4/4
- 当前: 已完成
- 文件: `.codex-tasks/20260420-oracle-live-gate/TODO.csv`
- 下一步: 当前 Oracle live gate 缺口已关闭；如需继续 roadmap，回到新的 epic 选择流程

## Control Contract

- Primary Setpoint: 当前仓库可以在 macOS 上通过本地 Oracle XE 容器完成真实 Oracle 连接校验，并提供稳定的根级 gate 入口
- Acceptance: `uv run python -c "import oracledb; print(oracledb.__version__)"`、`pnpm test:control-plane:oracle`、`pnpm test:control-plane:postgres`、`uv run pytest tests/ops`
- Guardrails: 不改变已完成的 Oracle onboarding baseline 产品契约；不打破现有 Postgres gate；不引入仓库外手工步骤
- Sampling Plan: 先做 L0 依赖与 compose 配置验证，再跑 L1 合同测试，最后跑 L2 真实 Oracle live gate 与 Postgres 回归 gate
- Known Delays: Oracle XE 首次启动和健康检查可能需要分钟级时间；`uv sync` 会更新本地依赖环境
- Recovery Target: 若 Oracle live gate 失败，应能在本任务内定位到驱动、网络、初始化 SQL 或控制面路由中的具体阻塞点
- Rollback Trigger: 若为接入 Oracle 而破坏现有根级脚本约定或引入 fake validator 通路，立即收缩到最小 infra/gate 方案
- Constraints: 仅允许修改本地基础设施、运行依赖、gate 入口、相关测试与任务文档，不扩展未承诺的 Oracle 功能面
- Boundary: `compose.yaml`、`pyproject.toml` / `uv.lock`、`scripts/powershell_shim.py`、`package.json`、`gates/`、`tests/ops/`、相关任务文档
- Coupling Notes: 本任务同时触碰控制面 gate、状态面 Postgres/Oracle infra 和 macOS 脚本入口，必须保持三者口径一致

## Notes

- Epic 05 已完成，不再继续按 roadmap 自动切换下一 epic；这轮是用户显式触发的新单任务
- 当前仓库已有 Oracle onboarding baseline，但只在 injected validator 路径下验证过
- 现已补齐：
  - `compose.yaml` 中的 profiled `oracle-xe` 本地服务
  - `oracledb` 运行依赖与 `uv.lock`
  - `PythonOracleConnectionValidator` 的 docker `sqlplus` fallback，用于 macOS 本地 11g XE live gate
  - `pnpm test:control-plane:oracle` 根级入口、PowerShell shim 与对应合同测试
- 用户已明确当前 Docker 中已有 `wnameless/oracle-xe-11g-r2:latest`，因此基础设施部分可以直接复用该镜像
- 已收集到关键环境证据：
  - `uv run --with oracledb python ...` 直连 11g XE 返回 `DPY-3010`，说明 Oracle 11g 对 thin mode 不兼容
  - `docker exec oracle-xe-local ... sqlplus ...` 可从容器内真实完成 `select 1 from dual`
  - `pnpm test:control-plane:oracle` 已通过，证明 root script -> shim -> validator fallback -> Postgres control-plane 持久化链路已闭环
  - runner 现已优先复用本机现存 `oracle-xe-local` 容器；若不存在，再回落到仓库 compose 的 profiled `oracle-xe` 服务，避免容器命名冲突
  - 历史 Epic 05 / child-task 文档中关于“live Oracle gate 仍开放”的描述已更新为“当时开放，后续已由本任务关闭”

## Latest Validation

- `uv lock`
- `uv run python -c "import oracledb; print(oracledb.__version__)"`
- `uv run pytest tests/api/control_plane/test_oracle_validation.py tests/ops/test_macos_environment_entrypoints.py`
- `uv run pytest tests/api/control_plane/test_oracle_validation.py tests/api/assets tests/integration/control_plane`
- `pnpm test:control-plane:postgres`
- `pnpm test:control-plane:oracle`
- `uv run pytest tests/ops`
