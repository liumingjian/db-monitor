# ADR-0002: Slice sequence and engine scope for Lepus Parity

Status: accepted (2026-04-22)

在 ADR-0001 确定 Option B（阶段性对等）后，本轮访谈锁定了完整切片序列：Slice 1（MySQL/Oracle 产品级完整度）→ Slice 2（告警成熟度+通知扩展）→ Slice 3（OS/SNMP）→ Slice 4（SQLServer）→ Slice 5（MySQL 深度）→ Slice 6（Oracle 深度）→ Slice 7（Redis，条件性）→ Slice 8（大屏+报表+收官），总估时 31-45 周。

## Considered Options

- **MongoDB 作为第三引擎**：被拒。Boss 明确"不用 MongoDB，先不考虑"——即永不复刻，不是推后。MongoDB 的存在会稀释切片预算，且业务侧无真实用户。
- **Redis+SQLServer 合并一个切片**：被拒。Redis 降级为"条件性"，应与 SQLServer 解耦；合并会导致 Redis 的抽象讨论拖住 SQLServer 的上线。
- **引擎并行扩展（切片 3-5 并行）**：未选。并行会放大"抽象未经验证就被第二引擎考验"的返工风险，不值得用时间换风险。
- **先做深度后做广度**：未选。在 6 引擎未覆盖前就做 MySQL 深度会导致"MySQL 深度分析很好看但 Oracle 还没告警"的不均衡。

## Consequences

- `Lepus Parity` 的最终形态是 **4 个引擎深度对等（MySQL/Oracle/OS/SQLServer）+ 1 引擎条件性（Redis）+ MongoDB 永不复刻**。这改变了 ADR-0001 里隐含的"全部 6 引擎"表述，已同步更新 `CONTEXT.md`。
- 切片 7（Redis）启动需要新的显式触发条件：业务方提出有 Redis 实例需要纳入监控范围；否则切片 8 可直接跟在切片 6 后。
- 永不复刻清单（MongoDB、飞信、CI 框架辅助控制器、`awrreport`）写入 `CONTEXT.md` Slice sequence 节；任何未来希望补回的请求必须通过新 ADR 显式 supersede 本条。
- 切片之间的 1 周 stabilization buffer 不另设 epic，隐含在浮动估时中。
- Epic 14（Scale/HA/DR）保持 deferred，直至切片 8 收尾后再做一次全局 close-out review。
