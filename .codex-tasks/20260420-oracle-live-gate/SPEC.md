# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 将 `wnameless/oracle-xe-11g-r2:latest` 接入当前仓库的本地基础设施，作为 macOS 开发与验证环境的一部分
- 为 Oracle 补齐可在本机真实运行的驱动、compose 服务与 live gate，关闭此前仅停留在 injected validator 的缺口
- 保持现有 MySQL / Postgres 控制面路径与根级脚本入口稳定

## Non-Goals

- 不在本任务中补 Oracle analytics parity 或调度链路全量支持
- 不扩展新的产品能力边界，只补齐当前已声明 Oracle onboarding baseline 的真实环境验证
- 不引入需要用户手工维护的临时命令或仓库外部脚本

## Constraints

- 必须复用用户已确认存在的本地 Oracle 镜像 `wnameless/oracle-xe-11g-r2:latest`
- 必须继续遵守当前仓库的 macOS 入口模式：根级 `pnpm` 脚本通过 repo-local runner 调起
- 必须把 live Oracle gate 建立在真实 `PythonOracleConnectionValidator` 之上，不能再用 static validator 伪装通过
- 不能打破现有 `test:control-plane:postgres` 与 `tests/ops` 约定

## Deliverables

- `compose.yaml` 中可复用的 Oracle XE 本地基础设施服务
- Python Oracle 驱动依赖与最小初始化配置
- 根级 `pnpm test:control-plane:oracle` 入口及其 macOS 合同测试
- 一条真实经过 Oracle 容器的控制面 live gate
- 当前任务与此前 epic gap 的收口记录

## Final Validation Command

```bash
uv run python -c "import oracledb; print(oracledb.__version__)" \
  && pnpm test:control-plane:postgres \
  && pnpm test:control-plane:oracle \
  && uv run pytest tests/ops
```
