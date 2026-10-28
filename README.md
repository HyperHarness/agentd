# agentd-new 需求与架构资料

本目录集中保存本轮从零重新开发 agentd 的需求、架构专题和可执行接口契约，方便统一查找与审计。整理日期：2026-10-28。当前是候选设计，尚未实施；R/D/H/P/F 决定状态沿用需求基线。

先读产品需求和架构总览，再按任务进入专题；需要核对字段与路由时直接打开生成的 API 参考。

## 阅读入口

| 资料 | 查阅内容 |
| --- | --- |
| [产品需求基线](docs/PRODUCT_REQUIREMENTS_BASELINE.md) | 产品目标、已确认要求、成功与失败标准、版本范围、指标和未决事项 |
| [软件架构总览](docs/SOFTWARE_ARCHITECTURE_PROPOSAL.md) | 系统组成、模块职责、关键决策和全套设计导航 |
| [任务与独立审核协议](docs/design/TASK_AND_REVIEW_PROTOCOL.md) | 状态与泳道、输入冻结、Worker 交付、独审材料、证据、租约、通知和统计 |
| [运行边界与生命周期](docs/design/RUNTIME_LIFECYCLE.md) | 进程与资源所有权、固定配置、共享资源、安装、升级和卸载 |
| [事务恢复与成果存储](docs/design/RELIABILITY_AND_STORAGE.md) | 并发不变量、故障窗口、恢复动作、内容保留、GC 和备份恢复 |
| [接入与接口行为](docs/design/INTERFACE_GUIDE.md) | 页面与调用分工、身份权限、凭据、HTTP、幂等及管理行为 |
| [交付与验收计划](docs/design/VALIDATION_PLAN.md) | 实现顺序、支持环境、探针、性能条件及验收场景 |
| [设计决策与历史证据](docs/design/DECISIONS_AND_EVIDENCE.md) | 方案取舍、已提炼的历史教训、待定决策和变更规则 |
| [接口契约使用说明](specs/agentd_v1/README.md) | 类型、操作清单、样例与生成/检查命令 |
| [生成的 API 参考](specs/agentd_v1/generated/API_REFERENCE.md) | 29 个操作、请求/响应字段、错误、客户端映射和参数候选 |
| [OpenAPI](specs/agentd_v1/generated/openapi.json) · [JSON Schema](specs/agentd_v1/generated/schemas.json) | 机器可读契约 |
| [接口旧入口](docs/AGENT_INTERFACE_DESIGN.md) | 原接口页的导航入口，指向同一套现行设计 |

## 文件组织与维护

- `docs/`：需求基线、简短架构总览和接口入口。
- `docs/design/`：六个专题，拥有行为和恢复约定。
- `specs/agentd_v1/`：模型定义、操作注册表、生成器、检查器、JSON 样例及生成物。
- `audit/`：本次整理的文件来源、内容摘要和离线检查结果。

产品要求在需求基线维护；行为规则在所属专题维护；字段与路由修改 `models.py` / `operations.py` 后重新生成。生成文件不手工编辑。类型和离线检查不能代替真实鉴权、事务、模型或主机验收。

本次采用复制整理，原仓库 `/home/cying/agentd` 的文件保留。这里的当前设计及契约内部链接均相对本目录解析；运行校验无需导入旧 agentd 应用。两个目录之间没有自动同步，审计清单记录的是本次整理快照；后续编辑应同时更新相应生成物和审计记录。

## 校验方法

在 `/home/cying/agentd-new` 下运行。现有机器可直接复用已验证的解释器与依赖：

```sh
/home/cying/agentd/.venv/bin/python -m specs.agentd_v1.check
```

上述命令加载本目录的契约源码。若需要独立环境，在已具备 Python 3.14 的机器上用相应解释器建立环境：

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-design.txt
.venv/bin/python -m specs.agentd_v1.check
```

依赖文件仅用于设计工具；本次整理未安装依赖或创建新运行服务。修改模型或路由后运行 `python -m specs.agentd_v1.generate`，再执行检查。`generate --check` 只比较生成物，不写文件。

核对本次整理快照的内容完整性：

```sh
sha256sum -c audit/SHA256SUMS
```

[离线校验记录](audit/VALIDATION.md)说明检查范围；[来源清单](audit/FILE_MANIFEST.json)列出每个文件的原路径、原始摘要、目标摘要及整理时是否有适配修改。清单不证明未来修改仍有效，设计中的待定参数与真实环境假设也不会因校验通过而自动定案。
