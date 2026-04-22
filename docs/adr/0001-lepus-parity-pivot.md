# ADR-0001: Pivot to Lepus Parity; retire original PRD

Status: accepted (2026-04-22)

截至 `2026-04-22`，Epic 01-13 已全部 Done，原始 `PRD.md` 的 phase-one 目标（MySQL-only 最小控制面）已实现并被超越；Boss 将产品终极目标重置为"还原 legacy `lepus-v3.8/` 的全部能力"（Option A），执行路径采用按切片推进的阶段性对等（Option B）。原始 `PRD.md` 整体作废，不再作为范围约束；后续目标以本 ADR、`CONTEXT.md` 和新路线图扩展为准。`EPIC_ROADMAP.md` 中"Epic 14: Scale/HA/DR"降优先级，新主线是逐切片补齐 lepus 能力（MySQL 运维深度 + Notifier 渠道 → 第三/四/五/六引擎 → 深度能力），直至达到 Option A 的终极 parity。

## Considered Options

- **A — 字面全量还原**：一次性覆盖 6 引擎 + 全部深度。被拒：规模过大，抽象还未被第 3 个引擎试金，会放大返工。
- **B — 阶段性对等**（已选）：每切片结束都能在生产真用；风险可控，抽象可持续被新引擎验证。
- **C — 只还原用户价值子集**：被拒：需要 Boss 给出更精细的清单，且长期仍要被 lepus 功能诉求拖回来。

## Consequences

- `PRD.md` 保留文件用于历史追溯，但产品范围不再以它为准。
- `EPIC_ROADMAP.md` 需要一轮显式的"post-Epic-13 roadmap extension"，把后续切片落为新的 active epic 序列。
- 当前 `Out of Scope` 项（MongoDB/Redis/SQLServer/OS/slow query deep/bigtable/binlog/report）全部回到 In Scope，但按切片顺序启动，不同步推进。
- "可投产"这个词在仓库文档中必须显式标注是 **Platform-Level** 还是 **Product-Level**（见 `CONTEXT.md`）。
