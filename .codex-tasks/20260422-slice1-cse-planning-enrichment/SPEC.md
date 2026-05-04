# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

在不动任何运行代码的前提下，把 Slice 1（Epic 15 + Epic 16）的**项目级控制拓扑**补到 CSE 最佳实践要求的维度：

1. 为 Epic 15 建立显式的多模型视角（静态契约 / 动态状态 / 容量排队三域）
2. 为 Slice 1 的 5 个高耦合 knob 产出统一的黑盒输入-输出影响矩阵
3. 为 Slice 1 画出 L0/L1/L2 验证梯，并显式标注"只能 L2 验证"的风险
4. 补齐 Epic 16 EPIC.md 的 Complexity Transfer Ledger
5. 落地 ADR-0009：Notifier 的 anti-chatter / anti-windup / 退避上界
6. 落地 ADR-0010：Slice 1 cutover 与 one-way door 清单（不涉及 Lepus 双发，Lepus 无运行用户）

## Key Inputs

- `CONTEXT.md`（Slice 1 锁定范围与术语）
- `docs/adr/0001..0008`（现有门禁，冻结不动）
- `~/.claude/skills/cybernetic-systems-engineering/SKILL.md`（CSE 最佳实践）
- `.codex-tasks/20260422-slice01-epic15-monitoring-depth/EPIC.md`（增广对象）
- `.codex-tasks/20260422-slice01-epic16-notifier-reality/EPIC.md`（增广对象）

## Control Contract

- **Primary Setpoint**
  - Slice 1 进入实施前，项目级控制拓扑达到 CSE 最佳实践的"必备"层——多模型视角、knob 矩阵、验证梯、动态控制病规则、one-way door 清单全部落盘为可审计工件
- **Acceptance**
  - 6 个 TODO 全部 `DONE`
  - 新增 2 份 `docs/` 文件（`slice1-control-knobs.md`、`validation-ladder.md`）
  - 新增 2 份 ADR（0009、0010）`Status: accepted`
  - Epic 15/16 EPIC.md 的增补节落盘
  - `grep -l "Multi-Model View" .codex-tasks/20260422-slice01-epic15-monitoring-depth/EPIC.md` 命中
  - `grep -l "Complexity Transfer Ledger" .codex-tasks/20260422-slice01-epic16-notifier-reality/EPIC.md` 命中
- **Guardrails**
  - 不改任何运行代码、schema DDL、API 合同、OpenAPI snapshot
  - 不动 ADR-0001..0008 的既有决议文本（只能通过新 ADR supersede）
  - 不改 `CONTEXT.md` 的 Slice 1 锁定段（TODO 中的 `CONTEXT.md` 引用只做阅读）
  - 不改 Epic 15/16 的 SUBTASKS.csv 或任何 child SPEC.md / TODO.csv 的技术合同（只能补 CSE 元信息节）
  - 不提前启动 Epic 15 child #1 的代码实施
- **Sampling Plan**
  - 每个 TODO 完成后单独标 `DONE`，不合并提交
  - 每个新 ADR 生成后立即用 `grep -q "Status: accepted"` 验证
- **Known Delays / Delay Budget**
  - 无——本任务纯文档写作，预计单会话 1-2 小时完成
- **Recovery Target**
  - 任一 TODO 写坏可通过 `git checkout -- <file>` 单独回滚
- **Rollback Trigger**
  - Boss 在审阅过程中指出任一诊断维度判断错误 → 对应 TODO 直接回滚 + 本任务 `FAILED` + 重新走 plan
- **Constraints**
  - 只允许新增或增补：`docs/adr/0009-*.md`、`docs/adr/0010-*.md`、`docs/slice1-control-knobs.md`、`docs/validation-ladder.md`、2 份 EPIC.md 的末尾追加段
  - 不允许触碰任何 `apps/`、`packages/`、`contracts/`、`gates/`、`tests/`、`scripts/`、`lepus-v3.8/`
- **Boundary**
  - `.codex-tasks/20260422-slice1-cse-planning-enrichment/`（本任务目录）
  - `docs/adr/`（新增 2 份）
  - `docs/`（新增 2 份）
  - `.codex-tasks/20260422-slice01-epic15-monitoring-depth/EPIC.md`（追加）
  - `.codex-tasks/20260422-slice01-epic16-notifier-reality/EPIC.md`（追加）
- **Coupling Notes**
  - ADR-0009 为 Epic 16 child `#4`（end-to-end-integration）提供实现时必须遵守的参数上界；不改 child SPEC
  - ADR-0010 在 Slice 1 关闭时被 Epic 16 child `#5` 的演练签字流程 consume
  - `slice1-control-knobs.md` 的参数默认值与 ADR-0005/0006/0007 保持一致，不改名
- **Approximation Validity**
  - 本任务产出的容量数字（1.4 亿行/天等）沿用 ADR-0005 估算，有效期到 Epic 15 child `#1` 真实采集数据上线；实际值需在演练后回写

## Scope

见 `TODO.csv`。

## Non-Goals

- 不修 bug、不加 feature、不改 schema
- 不启动 Epic 15 的代码实施
- 不写任何关于 Lepus 的过渡/并行/关停策略（Lepus 无运行用户，已确认）
- 不扩 ADR 到 Slice 2+ 的议题（本任务只锁 Slice 1）

## Final Validation Command

```bash
test -f docs/adr/0009-notifier-dynamic-control-discipline.md \
  && test -f docs/adr/0010-slice1-cutover-one-way-door-inventory.md \
  && test -f docs/slice1-control-knobs.md \
  && test -f docs/validation-ladder.md \
  && grep -q "Status: accepted" docs/adr/0009-notifier-dynamic-control-discipline.md \
  && grep -q "Status: accepted" docs/adr/0010-slice1-cutover-one-way-door-inventory.md \
  && grep -q "Multi-Model View" .codex-tasks/20260422-slice01-epic15-monitoring-depth/EPIC.md \
  && grep -q "Complexity Transfer Ledger" .codex-tasks/20260422-slice01-epic16-notifier-reality/EPIC.md
```
