# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 收敛 capacity insights、signal leaders 与 preset semantics，使其与新的 mixed-engine parity 面一致

## Non-Goals

- 不把 diagnostics 扩成新的深度报表系统
- 不重写 overview 页面信息架构

## Constraints

- 必须建立在 child `#3` 和 `#4` 的 contract 与 UI surface 之上
- 必须明确哪些 leader semantics 仍在 scope 外，而不是用空文案掩盖

## Deliverables

- diagnostics / leaders / presets 收敛
- web test/build evidence

## Final Validation Command

```bash
pnpm --filter web test && pnpm --filter web build
```
