# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让 overview 页面、dashboard model 与 capability messaging 收敛到新的 parity baseline

## Non-Goals

- 不在本任务中改 runtime / live-gate
- 不引入新的页面或信息架构

## Constraints

- 必须建立在 child `#3` 的后端 contract 之上
- preview fixtures、dashboard tests 与页面 copy 必须一起更新

## Deliverables

- web overview parity surface
- preview / tests / typecheck evidence

## Final Validation Command

```bash
pnpm --filter web test && pnpm --filter web typecheck
```
