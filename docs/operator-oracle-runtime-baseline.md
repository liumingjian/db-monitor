# Operator Oracle Runtime Baseline

## Scope

这份 runbook 固化 Epic 12 `Oracle Runtime Reliability and Live-Gate Productionization` 的最小 operator 基线。
目标不是扩展新的产品面，而是把 Oracle runtime/live-gate 的前置检查、signoff、失败隔离和回滚入口固化为显式步骤。

## Preconditions

- 已安装 `docker`
- 已安装 `pnpm`
- 已准备仓库根目录下的 `.venv`
- 当前根级 `pnpm` 命令已适配 macOS，本地无需系统 PowerShell
- 本地端口 `5432`、`15211` 未被其他进程占用
- 若本机存在历史 Oracle 容器 `oracle-xe-local`，确认它当前状态是可预期的；repo-local runner 会优先复用它

## Canonical Flow

1. 先执行 Oracle runtime doctor：
   - `pnpm test:oracle-runtime:doctor`
2. doctor 通过后，再执行 root signoff：
   - `pnpm test:oracle-runtime:signoff`

## Doctor Semantics

`pnpm test:oracle-runtime:doctor` 会完成以下最小 preflight：

1. 校验 Python Oracle 驱动是否可导入：
   - `uv run python -c "import oracledb; print(oracledb.__version__)"`
2. 拉起 Oracle live gate 所需的最小本地依赖：
   - PostgreSQL
   - Oracle XE 或可复用的 `oracle-xe-local`
3. 在 Oracle 容器内部执行 `sqlplus` 自检：
   - `select 1 from dual`
4. 若 doctor 失败，repo-local runner 会直接输出：
   - container health
   - 最近容器日志
   - `sqlplus` 自检结果

## Canonical Signoff

1. 在仓库根目录执行：
   - `pnpm test:oracle-runtime:signoff`
2. 该命令会顺序执行：
   - `python3 -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' uv run pytest tests/ops/test_oracle_runtime_baseline.py tests/ops/test_macos_environment_entrypoints.py tests/api/control_plane/test_oracle_validation.py -q`
   - `pnpm test:oracle-runtime:doctor`
   - `pnpm test:control-plane:postgres`
   - `pnpm test:control-plane:oracle`

## Failure Isolation

1. 任一命令失败都视为 signoff 未通过，立即停止本次 signoff。
2. 若失败出现在 doctor 的 Python 驱动导入阶段：
   - 先检查 `.venv`
   - 再执行 `uv sync`
3. 若失败信息包含 `DPY-3010`：
   - 这表示 Oracle 11g XE 不支持 `python-oracledb` thin mode
   - 当前仓库的预期恢复路径不是手工跳过，而是让 `sqlplus` docker fallback 接管
4. 若失败出现在 live gate：
   - 先单独重跑 `pnpm test:oracle-runtime:doctor`
   - 再查看 `docker compose ps oracle-xe`
   - 再查看 `docker logs $(docker compose ps -q oracle-xe)`
5. 若当前机器走的是 `oracle-xe-local` 复用路径：
   - 先确认 legacy container 处于 Running
   - 再重跑 doctor，而不是直接跳过 Oracle live gate

## Rollback Trigger

出现以下任一信号，默认停止继续 signoff 并进入回滚：

- `pnpm test:oracle-runtime:doctor` 失败
- `pnpm test:control-plane:postgres` 失败
- `pnpm test:control-plane:oracle` 失败
- Oracle 容器 health 无法稳定进入 healthy
- `sqlplus` 自检失败，且最近容器日志无法解释当前错误

## Rollback Procedure

1. 停止本轮 compose 拉起的依赖：
   - `docker compose stop postgres oracle-xe`
2. 若本轮显式启动了 legacy 容器 `oracle-xe-local`，记录其状态并按本地运维约定恢复。
3. 记录最后一个失败 gate、最后一次 doctor 输出、容器日志和当前命令，再重新开始下一次尝试。

## Checklists

- Runtime checklist: [operator-oracle-runtime-checklist.md](./operator-oracle-runtime-checklist.md)
- Rollback checklist: [operator-oracle-runtime-rollback-checklist.md](./operator-oracle-runtime-rollback-checklist.md)
