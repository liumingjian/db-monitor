# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 建立控制面的认证、会话和 RBAC 基础能力
- 提供 `login/logout/me` 与权限校验边界
- 为所有控制面写操作补上审计入口

## Non-Goals

- 不实现实例接入或指标采集
- 不将权限判断下沉到前端或绕过 API 边界

## Constraints

- 业务 API 必须通过 `FastAPI`
- 授权逻辑必须落在后端 service/repository 边界内
- RBAC 必须服务于单租户内部场景，不预埋多租户模型
- 失败必须显式暴露，不允许静默放行

## Environment

- **Project root**: `C:\Users\14142\Desktop\ai-project\db-monitor`
- **Language/runtime**: `Python 3.12`
- **Package manager**: `uv`
- **Test framework**: `pytest`
- **Build command**: `uv run pytest`
- **Existing test count**: `0 planned`

## Risk Assessment

- [ ] 认证模型若与后续实例/规则资源边界不一致，会导致权限返工
- [ ] 会话与审计若耦合在路由层，后续测试会变脆弱
- [ ] 若未明确最小权限语义，phase-one UI 容易过度授权

## Deliverables

- 认证与会话 domain/service/repository 基础
- `login/logout/me` API
- RBAC 角色、权限、资源检查机制
- 审计记录入口

## Done-When

- [ ] 控制面接口具备明确身份边界
- [ ] RBAC 能覆盖实例、规则、设置等核心资源
- [ ] 认证与授权可通过自动化测试验证

## Final Validation Command

```bash
uv run pytest tests/api/auth tests/api/rbac
```

## Demo Flow

1. 使用管理员账号登录
2. 调用 `me` 接口确认会话信息
3. 用不同角色访问受保护资源，验证允许与拒绝路径

