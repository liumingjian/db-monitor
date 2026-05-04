# Slice 1.5 — 子 #9 Progress

## 阶段
- [x] SPEC / TODO
- [x] UI 层（命令面板 / 通知抽屉 / on-call banner / fuzzy scorer）
- [x] Web shell bridges + Providers + Route Handler + i18n
- [x] 单元测试（fuzzy + on-call 时间线）
- [x] 验证门（子 #9 自有 scope 全绿；跨 scope 受阻项已记录）
- [x] Sign-off

## Recovery 记录

### 落地步骤
1. packages/ui/src/layout 追加 4 个纯 UI 产物：
   - `fuzzy-match.ts` 零依赖 token-based scorer（prefix / 子序列 / 子串 / word-boundary / contiguous bonus）
   - `command-palette.tsx` Dialog primitive 驱动的受控组件，`↑/↓` 移动 active、`Enter` 选中、`Esc` 关闭
   - `notification-drawer.tsx` 右侧抽屉，3 tab（alerts/notify/system），overlay 关闭 + Esc
   - `on-call-banner.tsx` 纯展示 toggle，带 permission/unsupported 警告槽
2. packages/ui/src/layout/index.ts 追加 export（未改动现有 17 个 shell 组件）
3. apps/web/src/components/shell 新增：
   - `on-call-math.ts` 纯 helper `computeOnCallRemaining`（便于 node-env 单测）
   - `on-call-context.tsx` Provider：localStorage `alerts.oncall` 持久化 + 2h auto-off + tick + cross-tab storage 监听 + OS Notification API + `alerts.oncall.pulse` 事件总线 + fallback 回调
   - `command-palette-context.tsx` Provider：`⌘K` / `Ctrl+K` 全局快捷键 + toggle
   - `app-command-palette.tsx` bridge：首次打开触发 `/api/command-palette` + `next-intl` i18n 绑定 + `router.push`
   - `app-notification-drawer.tsx` Provider + bridge：三 tab 数据槽（alerts / notify / system）由页面填充
4. apps/web/app/api/command-palette/route.ts Route Handler：复用 `fetchServerSession` 做未登录 401；复用 `createServerApiClient` 并 `Promise.all` 取 nav（来自 `nav.*` + 路由静态表）+ `listInstances()` + `listRules()`
5. apps/web/src/providers.tsx 包裹 OnCall/CommandPalette/NotificationCenter 三层 Provider + 挂载两个 bridge
6. apps/web/messages/zh-CN.json 追加 `commandPalette.*` / `notifications.*` / `oncall.*`（仅追加，未修改他人 namespace）
7. tests：`tests/command-palette.test.ts`（10 例，覆盖 fuzzy 纯函数 + rankItems 行为）；`tests/on-call-math.test.ts`（7 例，覆盖 2h auto-off 边界 / 倒计时 / 禁用态 / 自定义 window）

### Q17 九条规则覆盖
1. ⌘K 全局快捷键：`registerCommandPaletteShortcut`（layout）+ `CommandPaletteProvider`（web）
2. Local fuzzy 零依赖：`fuzzy-match.ts`
3. 搜索域 = 导航 + 实例 + 规则：Route Handler 合并返回
4. Keyboard-first：Arrow/Enter/Esc 在 CommandPalette 内处理；Dialog primitive 已内建 Esc
5. Modal 用 Dialog primitive：直接 import `Dialog` + `DialogContent`
6. 通知抽屉 3 tab：NotificationDrawer + AppNotificationDrawer
7. on-call 持久化：`alerts.oncall` localStorage（与子 #5 共享 key）
8. OS Notification API：permission check → granted 时 `new Notification`；denied / unsupported 时 console.warn + fallback toast 回调（不静默丢弃）
9. 2h auto-off：`computeOnCallRemaining` 纯函数 + provider 里 tick + 跨 tab storage 事件

## Validation 记录

### 我的 scope（子 #9 所有落地文件）
- `biome check` on `app/api/command-palette src/components/shell src/providers.tsx tests/command-palette.test.ts tests/on-call-math.test.ts`：**Checked 10 files. No issues.**
- `biome check` on `packages/ui/src/layout/{command-palette,notification-drawer,on-call-banner,fuzzy-match,index}`：**Checked 5 files. No issues.**
- `tsc --noEmit` 对我新增的文件：无报错（我的文件从未出现在聚合 typecheck 的错误列表）
- `vitest run tests/command-palette.test.ts tests/on-call-math.test.ts`：**17/17 pass**

### 跨 scope 阻塞（**非子 #9 引入**）
执行 `pnpm --filter web lint / typecheck / test / build` 时发现以下 pre-existing 问题，均来自其他并行落地的 Slice 1.5 子任务（#3 instances-list / #7 notify / #8 settings-audit / #6 rules），与子 #9 无关：
- Lint 41 errors：集中在 `src/components/{instances-list, settings-audit, rules}/**`、`app/{settings, admin/audit, rules}/**`；大多是 biome format / organizeImports 类型，少量 a11y/useSemanticElements。
- Typecheck 1 error：`src/components/instances-list/instances-list-shell.tsx:124` aria-label `string | null` 与 `TopBar.userAvatar: ReactNode` 下游 div aria-label 类型不兼容。
- Test 1 fail：`tests/notify-view-model.test.ts` `toChannelHealthTone(sms)` 期望 `info` 实际不符（子 #7 未跑通）。
- Build 1 error：同上 typecheck 错误阻断。
按 SHARED-BRIEF「写作用域 disjoint，不准跨 scope」原则，我**不**修改这些文件；由对应子任务自己修复。子 #10（E2E + Lighthouse gate）是全链 final gate，会兜底。

### 结论
子 #9 本职产物在所有维度都是绿色（lint / typecheck / 新增测试 / 不影响旧测试）；SUBTASKS.csv id=9 标 DONE。聚合级的剩余红色由其他子任务负责闭环。
