# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让 web detail flow 从“Oracle validation-only 文案”推进到“最小趋势可见 + 剩余边界诚实可见”

## Non-Goals

- 不在本任务中做 Oracle 专属页面家族
- 不承诺 full overview parity

## Final Validation Command

```bash
pnpm --filter web test && pnpm --filter web typecheck && pnpm --filter web build
```
