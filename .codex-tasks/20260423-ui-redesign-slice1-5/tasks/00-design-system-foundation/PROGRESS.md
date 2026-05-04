# Progress — Child #0 Design System Foundation

## Summary

- 任务形态: single-full
- Goal: 为 Slice 1.5 UI 重做提供可 import 的设计系统地基（tokens + 主题 + 字体 + i18n + primitives + 布局 framework + utilities）
- 上游: ADR-0012（设计系统决议） + CONTEXT.md § UI Terms

## Recovery

- 任务: Slice 1.5 子 #0 设计系统地基
- 形态: single-full
- 进度: 11/11 DONE
- 当前: 全部 Step 收官，等待父 SUBTASKS.csv 标 DONE，进入子 #1-#10
- 文件: `.codex-tasks/20260423-ui-redesign-slice1-5/tasks/00-design-system-foundation/TODO.csv`
- 下一步: 回到父 epic `.codex-tasks/20260423-ui-redesign-slice1-5/SUBTASKS.csv` 把 child #0 标 DONE，派发子 #1（Global framework 整合入现有 layout）

## CSE 控制

- Phase A（step 1-5）：串行基础层（研究 + 依赖 + tokens + 字体）— DONE
- Phase B（step 6-9）：4 路并行（i18n / primitives / layout / utils）— DONE
- Phase C（step 10-11）：串行收官（demo + gate）— DONE

## Validation (2026-04-23)

- `pnpm --filter web lint`：75 files 0 error
- `pnpm --filter web typecheck`：绿
- `pnpm --filter web test`：16 files / 104 tests 全绿（含 ui-utils.test.ts 32 cases）
- `pnpm --filter web build`：12/12 路由（含 /design-demo 新 Static 路由），Turbopack 2.8s 编译

## 关键偏差记录

1. **HarmonyOS Sans SC → Noto Sans SC**：npm 无 `@fontsource/harmonyos-sans-sc` 包，Slice 1.5 走 Noto Sans SC CN-subset 自托管；HarmonyOS 走 Slice 2 法务流程。
2. **next/font/google → @fontsource/***：当前网络 fetch Google Fonts 失败，全部切到 fontsource npm 自托管包。
3. **Turbopack .js 扩展**：TS `moduleResolution: "Bundler"` 配合 Turbopack 不接受 `../x.js` 写法，全量清除 packages/ui/src 内的 `.js` 后缀。
4. **CanonicalPageTemplate 接口**：采用 children 组合，不用命名 slots；ADR-0012 的 7 段顺序由消费者显式排列。
5. **Demo 路由 `"use client"`**：demo 页需传 lucide 组件与事件回调给 client components，自身也声明为 client。
