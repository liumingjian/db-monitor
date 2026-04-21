# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 完善当前项目的 epic 设计，让 `mysql phase-one epic` 完成后有清晰的后续推进路径
- 基于 `taskmaster` 执行理念，为后续阶段建立顶层 epic 路线图，但不提前细化子任务
- 回写当前 active epic 的交接规则、默认下一步和重新排序触发条件

## Non-Goals

- 不实现任何业务代码
- 不为未来所有 epic 预先创建 `SUBTASKS.csv` 和子任务骨架
- 不锁死后续 epic 的精细执行顺序

## Constraints

- 规划必须基于现有 `PRD.md` 与 `RESEARCH.md`
- 当前 active epic 继续保持 `taskmaster epic` 形态
- 未来 epic 只保留顶层 brief，不做叶子任务细化
- 默认下一 epic 必须明确，但允许通过显式信号改序

## Environment

- **Project root**: `C:\Users\14142\Desktop\ai-project\db-monitor`
- **Language/runtime**: `Documentation planning`
- **Package manager**: `N/A`
- **Test framework**: `N/A`
- **Build command**: `N/A`
- **Existing test count**: `N/A`

## Risk Assessment

- [ ] 若路线图只写主题、不写激活条件，当前 epic 完成后仍会陷入重新争论
- [ ] 若未来 epic 细化过深，会被前一阶段真实落地结果快速打脸
- [ ] 若当前 epic 没有明确交接门，团队容易在结束时直接跳向错误方向

## Deliverables

- 一个顶层 `EPIC_ROADMAP.md`
- 一个更新后的 `mysql phase-one epic` 交接与决策门
- 本次规划工作的 taskmaster 恢复文件

## Done-When

- [ ] 后续阶段的顶层 epic 已经定义并排好默认顺序
- [ ] 每个未来 epic 都包含边界、激活条件和不做事项
- [ ] 当前 active epic 明确写出默认 handoff 和改序条件

## Final Validation Command

```bash
powershell -NoProfile -Command "Test-Path 'EPIC_ROADMAP.md'; Test-Path '.codex-tasks/20260419-mysql-phase1-epic/EPIC.md'; Select-String -Path 'EPIC_ROADMAP.md' -Pattern 'Operational Hardening' | Out-Null; Select-String -Path '.codex-tasks/20260419-mysql-phase1-epic/EPIC.md' -Pattern 'Post-Phase Decision Gate' | Out-Null"
```

## Demo Flow

1. 先读 `EPIC_ROADMAP.md`，确认 active/default next/conditional next/deferred 的全局版图
2. 再读当前 `mysql phase-one epic` 的交接章节
3. 在当前 epic 完成时，按交接门决定是否进入默认下一 epic 或触发改序

