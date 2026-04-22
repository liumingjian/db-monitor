# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 把当前 internal launch baseline 扩成一条显式的 Docker target-environment 路径
- 在不改写既有 root signoff 语义的前提下，提供可重复执行的容器化 bootstrap、seed 和 e2e smoke

## Deliverables

- 一套 Docker target stack 编排与应用镜像入口
- 一条 repo-local 的 Docker target signoff 命令
- 更新后的 operator runbook 与对应 ops contract tests
