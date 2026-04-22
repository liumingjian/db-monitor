# ADR-0003: Slice 1 executes monitoring depth before notification reality

Status: accepted (2026-04-22)

切片 1 拆成两个串行 Epic：**Epic 15（监控深度 + per-instance 阈值）先做**，**Epic 16（Notifier 飞书/邮件 + 真实值班演练 signoff）后做**。Boss 指令"告警推送可以滞后，核心是监控功能"是主导因素：DBA 日常动作以查状态/排障为主，告警推送是偶发触发，先把 web 监控面上线能给内部用户提供立刻可用的体感升级；Notifier 作为闭环最后一段，在 Epic 16 补齐并承接切片 1 的真实演练 signoff。

## Considered Options

- **单一大 Epic（7 child 跨 4-6 周）**：被拒。child 跨度过长，close-out review 间隔过长，中途 signoff 无法分级。
- **Notifier 先做、监控后做**（Q5 最初推荐的顺序）：被拒。Boss 显式反转优先级；且监控面先上线能给 DBA 立刻可用的体感升级，不依赖 Notifier 也可过渡（现有 lepus 继续发告警）。
- **Notifier 整体移出切片 1 到切片 2**（Q6 解读 2）：被拒。Notifier 仍属于切片 1 的产品级闭环必要段，真实值班演练判据离不开端到端推送。
- **Notifier 推迟到切片 8 收尾**（Q6 解读 3）：被拒。跨引擎共享基础能力不能拖到最后。

## Consequences

- Epic 15 的 signoff 判据是**离线 gate + 新能力 smoke**；**不**包含真实演练。这显式允许 Epic 15 先关，即使 Notifier 还没做完。
- Epic 16 的 signoff 判据是**切片 1 完整真实演练**（4 类故障跑通）；**不允许**降级为平台 gate。若 DBA 时间排不开，切片 1 延后关闭而不是降低验收标准。
- Epic 15 结束与 Epic 16 启动之间不留显式 stabilization buffer（两者都在同一个切片 1 内）。
- Per-instance 阈值划归监控组（Epic 15），理由：它属于"DBA 配置异常识别"的监控配置面，不属于推送渠道。
