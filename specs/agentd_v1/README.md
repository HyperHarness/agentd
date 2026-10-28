# agentd 可执行设计契约

这是从零开发新 agentd 的**候选接口设计**，不是现有 daemon 的接口，也不包含新服务实现。`v1` 表示拟定的 HTTP 协议主版本；目前具体化的是产品 **V0** 范围。D 是待评审设计，P 是候选参数，通过生成或校验不会改变其决定状态。

从[架构总览](../../docs/SOFTWARE_ARCHITECTURE_PROPOSAL.md)了解系统边界，从[接口行为专题](../../docs/design/INTERFACE_GUIDE.md)了解授权、幂等与客户端约定；查具体字段时直接使用[生成的 API 参考](generated/API_REFERENCE.md)。

## 文件分工

| 文件 | 维护内容 |
| --- | --- |
| [models.py](models.py) | 唯一类型定义：请求、响应、任务、执行输入、交付清单、审核证据、管理配置；严格字段与跨字段校验；DRAFT_PARAMETERS 保存协议候选数值 |
| [operations.py](operations.py) | 唯一传输映射：方法/路径、角色、请求/响应类型、状态码、错误、幂等、CLI/MCP 映射及行为专题引用 |
| [generate.py](generate.py) | 根据上述来源确定性生成三份产物，不添加时间戳或随机内容 |
| [generated/openapi.json](generated/openapi.json) | OpenAPI 3.1，可供文档查看器或后续客户端生成器读取 |
| [generated/schemas.json](generated/schemas.json) | JSON Schema 2020-12 定义集合，按 `$defs` 中的模型名选择校验入口 |
| [generated/API_REFERENCE.md](generated/API_REFERENCE.md) | 操作索引、字段表、错误和 P 参数，由源码生成，不手改 |
| [examples/](examples/) | 机器可读正例；请求、响应、Worker 交付和证据样例各自绑定对应模型 |
| [check.py](check.py) | 生成物一致性、路由与 schema 引用、行为文档锚点、正反样例、严格 JSON 解码及证据摘要检查 |

字段定义不在 Markdown 中另抄一份。状态转换、事务、权限重核、外部动作和崩溃恢复仍由[专题协议](../../docs/SOFTWARE_ARCHITECTURE_PROPOSAL.md#阅读导航与文档权威)负责，不能以类型声明替代。

## 生成与校验

在资料根目录（`/home/cying/agentd-new`）运行，虚拟环境准备或复用方式见[统一入口](../../README.md#校验方法)。本次运行环境为 Python 3.14.4、Pydantic 2.13.5、jsonschema 4.26.0；这里只记录设计工具的已验组合，不据此冻结新产品运行时选型。模型使用 Pydantic 的 MISSING sentinel，其他版本需单独验证兼容性。

修改定义后生成产物：

```sh
.venv/bin/python -m specs.agentd_v1.generate
```

检查是否忘记重新生成；只比较，不写文件：

```sh
.venv/bin/python -m specs.agentd_v1.generate --check
```

运行完整离线合同检查，其中包含生成物一致性检查：

```sh
.venv/bin/python -m specs.agentd_v1.check
```

这些命令不导入生产 agentd，不启动服务、访问数据库、连接外部客户端或调用模型。生成命令仅覆盖本目录 `generated/` 下的三份派生文件。检查结果中 `runtime_model_host_validation=NOT_RUN` 保留真实验收边界。

## 按任务查阅

| 工作 | 入口 |
| --- | --- |
| 前端、CLI、MCP 对接 | [操作索引](generated/API_REFERENCE.md#操作索引) → 所需操作 → 请求/响应字段链接；续租 B16 仅供连接适配器，不注册为模型工具 |
| 后端实现用例 | operations.py 的传输约定 + [接口行为](../../docs/design/INTERFACE_GUIDE.md) + [事务恢复](../../docs/design/RELIABILITY_AND_STORAGE.md) |
| Worker 适配 | [输入与交付行为](../../docs/design/TASK_AND_REVIEW_PROTOCOL.md#worker-delivery) + ExecutionInput、WorkerDelivery 模型 + [交付样例](examples/worker-delivery.code.json) |
| reviewer 适配 | [独立验证与租约](../../docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-materials) + ReviewClaim、ReviewDecision、ReviewEvidenceManifest 模型 |
| 调整协议参数 | models.py 的 DRAFT_PARAMETERS → [生成参数表](generated/API_REFERENCE.md#p-参数候选)；主机预算、数据保留与性能指标仍在所属专题 |
| 新增字段或操作 | 修改源码，补能体现边界的样例/反例，重新生成并检查；同步受影响的行为与兼容约定 |

## 校验能证明什么

JSON Schema 检查结构、必填字段、枚举和可表达的数值约束；Pydantic 另检查 UTF-8 字节限额、摘要及部分跨字段不变量。原始 JSON 还必须经过 `strict_json_loads` / `parse_model`，否则普通解析器可能吞掉重复键或非有限数字。HTTP 查询参数需先按其声明类型显式解析，再交给严格模型，不能把所有字符串隐式转换。

服务当前状态才能证明的约束仍由实现检查，例如当前角色、候选归属、精确验收项覆盖、有效租约、期望版本、文件实际内容和事务顺序。需要上下文的模型验证也不能替代服务端获取并重核权威事实。OpenAPI 的权限描述与 P 参数元数据不是已实现的授权或准入逻辑。

本目录暂不生成 HTTP handler、数据库模型或前端业务代码。以后可从 OpenAPI 派生客户端类型，但生成客户端不会自动实现幂等重放、恢复判断和独立审核。V1 新增功能在对应阶段补合同；尚未定义的路径不视为可用。
