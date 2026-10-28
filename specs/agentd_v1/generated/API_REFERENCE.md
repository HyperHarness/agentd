<!-- GENERATED FILE: edit models.py / operations.py, then run python -m specs.agentd_v1.generate. -->
# agentd V0 生成接口参考

[D 待评审] 从零开发的 V0 拟议接口合同，尚非在线 API 或实现声明。[P 待选参数] 所列初值用于离线校验与评审，不代表已批准的产品默认值。由 specs/agentd_v1/models.py 与 operations.py 生成；禁止手改生成物。生成及校验不导入生产 agentd、不启动服务、不调用模型。

来源：[模型声明](../models.py) · [操作注册表](../operations.py) · [生成器](../generate.py)。机器可读：[OpenAPI 3.1](openapi.json) · [JSON Schema 2020-12](schemas.json)。

结构校验不能证明鉴权、幂等事务、Git 对象真实性、资源隔离、进程闭合或模型能力；行为前置条件须结合[接入合同](../../../docs/design/INTERFACE_GUIDE.md#http-contract)实现和验收。

## 公共传输约定

所有 GET 均被动且无请求体；读取不领取、不续租、不启动模型。B16 由连接适配器调用，不暴露为模型工具。角色 Bearer 仅对应 lead/reviewer；Dashboard 管理使用 `agentd_session` cookie。cookie 写操作同时要求 `X-CSRF-Token` 与受信 `Origin`。这两个命名为 D 拟定合同。

除建立/退出管理会话外，所有写操作必须携带 `Idempotency-Key` 与已观察的 `X-Agentd-Store-Epoch`；请求键属于信封，不放进业务正文。admin 的项目范围依注册表解析；lead/reviewer 不得发送 `X-Agentd-Project`。只有项目管理复用操作或 catalog 接受该项目头；对象归属始终另行核对。

请求正文使用 `application/json`；错误使用 `application/problem+json` 并遵循 [Problem](#schema-problem)。拒绝重复 JSON 键、非有限数、未声明字段及未知查询参数；字节限制由解码边界检查，无法仅靠 JSON Schema 表达。结构中 nullable 与字段可省略是不同约束。

## 操作索引

| 编号 | 方法与路径 | 操作 | 角色 |
| --- | --- | --- | --- |
| [B01](#b01) | `POST /v1/tasks` | 提交不可变任务合同 | lead, admin |
| [B02](#b02) | `GET /v1/tasks/{id}` | 读取任务详情与可用动作 | lead, admin |
| [B03](#b03) | `GET /v1/tasks` | 分页列出任务 | lead, admin |
| [B04](#b04) | `POST /v1/tasks/{id}/resume` | 按当前恢复动作继续任务 | lead, admin |
| [B05](#b05) | `POST /v1/tasks/{id}/cancel` | 登记取消并核对停止 | lead, admin |
| [B06](#b06) | `POST /v1/reviews/next` | 领取或找回一项审核 | reviewer |
| [B07](#b07) | `POST /v1/reviews/submit` | 提交独立审核判决 | reviewer |
| [B08](#b08) | `POST /v1/reviews/defer` | 暂缓无法判断的审核 | reviewer |
| [B09](#b09) | `GET /v1/inbox` | 读取角色事项与事件 | lead, reviewer |
| [B10](#b10) | `GET /v1/context` | 被动读取连接上下文 | lead, reviewer |
| [B11](#b11) | `GET /v1/model-stats` | 读取模型与难度统计 | lead, admin |
| [B12](#b12) | `GET /v1/artifacts/{id}` | 读取授权成果的原始字节块 | lead, reviewer, admin |
| [B13](#b13) | `GET /v1/requests/{request_key}` | 按原请求键核对结果 | lead, reviewer, admin |
| [B14](#b14) | `GET /v1/operations/{id}` | 读取持久操作的当前进度 | lead, reviewer, admin |
| [B15](#b15) | `POST /v1/reviews/evidence` | 保存reviewer自产证据 | reviewer |
| [B16](#b16) | `POST /v1/reviews/renew` | 连接层有界续租 | reviewer |
| [M01](#m01) | `POST /v1/session` | 建立Dashboard管理会话 | bootstrap |
| [M02](#m02) | `DELETE /v1/session` | 退出Dashboard管理会话 | admin |
| [M03](#m03) | `GET /v1/health` | 读取最小存活状态 | public |
| [M04](#m04) | `GET /v1/admin/snapshot` | 读取管理快照 | admin |
| [M05](#m05) | `PUT /v1/admin/projects/{id}` | 登记项目与固定默认配置 | admin |
| [M06](#m06) | `PUT /v1/admin/credential-sources/{id}` | 登记或轮换私有凭据来源 | admin |
| [M07](#m07) | `PUT /v1/admin/workers/{id}` | 保存固定worker配置及准入 | admin |
| [M08](#m08) | `PUT /v1/admin/dispatch` | 设置用户派发暂停 | admin |
| [M09](#m09) | `PUT /v1/admin/projects/{id}/role-bindings/{role}` | 接线或撤销角色根 | admin |
| [M10](#m10) | `POST /v1/admin/workers/{id}/checks` | 静态检查worker配置 | admin |
| [M11](#m11) | `PUT /v1/admin/catalog/{kind}/{id}` | 保存固定配置目录版本 | admin |
| [M12](#m12) | `PUT /v1/admin/tasks/{id}/resource-override` | 为下一次执行设置任务资源 | admin |
| [M13](#m13) | `PUT /v1/admin/artifacts/{id}/keep` | 设置或释放显式内容保留 | admin |

## P 参数候选

以下均为 **P 待选参数**，修改须重新生成并复核测试，不能当作已经批准的产品默认值。

| 参数 | 候选值 | 单位 | 校验责任 | 已含结构/模型检查 |
| --- | --- | --- | --- | --- |
| `id_key_max_bytes` | `128` | ASCII bytes | contract model | 是（不代表运行时已落实） |
| `title_max_bytes` | `512` | UTF-8 bytes | contract model | 是（不代表运行时已落实） |
| `json_request_max_bytes` | `1048576` | bytes | HTTP decoder / strict_json_loads | 需实现边界检查 |
| `task_spec_max_bytes` | `524288` | canonical UTF-8 JSON bytes | contract model | 是（不代表运行时已落实） |
| `goal_max_bytes` | `131072` | UTF-8 bytes | contract model | 是（不代表运行时已落实） |
| `criterion_max_bytes` | `8192` | UTF-8 bytes | contract model | 是（不代表运行时已落实） |
| `criteria_max_count` | `64` | items | contract model | 是（不代表运行时已落实） |
| `inputs_max_count` | `128` | items | contract model | 是（不代表运行时已落实） |
| `json_max_depth` | `16` | container levels | HTTP decoder / strict_json_loads | 需实现边界检查 |
| `page_default` | `20` | items | query model | 是（不代表运行时已落实） |
| `page_max` | `100` | items | query model | 是（不代表运行时已落实） |
| `artifact_chunk_default_bytes` | `65536` | bytes | query model | 是（不代表运行时已落实） |
| `artifact_chunk_max_bytes` | `262144` | bytes | contract model | 是（不代表运行时已落实） |
| `reason_max_bytes` | `16384` | UTF-8 bytes | contract model | 是（不代表运行时已落实） |
| `execution_input_max_bytes` | `1048576` | canonical UTF-8 JSON bytes | execution adapter | 需实现边界检查 |
| `manifest_max_bytes` | `1048576` | bytes | artifact store | 需实现边界检查 |
| `manifest_direct_members_max` | `128` | items | contract model / artifact store | 是（不代表运行时已落实） |
| `delivery_max_bytes` | `262144` | canonical UTF-8 JSON bytes | contract model | 是（不代表运行时已落实） |
| `candidate_members_total_max_bytes` | `1073741824` | bytes | artifact admission | 需实现边界检查 |
| `candidate_bundle_max_bytes` | `2147483648` | bytes | artifact admission | 需实现边界检查 |
| `review_evidence_segment_max_bytes` | `262144` | decoded bytes | contract model | 是（不代表运行时已落实） |
| `review_evidence_total_max_bytes` | `16777216` | bytes | manifest model / artifact store | 是（不代表运行时已落实） |
| `review_evidence_segments_max` | `64` | items | manifest model | 是（不代表运行时已落实） |
| `review_lease_ttl_seconds` | `1800` | seconds | review lease service | 需实现边界检查 |
| `review_lease_max_hold_seconds` | `28800` | seconds | review lease service | 需实现边界检查 |
| `review_activity_ttl_seconds` | `300` | seconds | review lease service | 需实现边界检查 |
| `v0_automatic_execution_recoveries` | `0` | attempts / Task | recovery policy | 需实现边界检查 |
| `v1_automatic_execution_recoveries` | `2` | attempts / Task | recovery policy | 需实现边界检查 |
| `execution_recovery_window_seconds` | `86400` | seconds from first execution fault | recovery policy | 需实现边界检查 |
| `execution_recovery_backoff_seconds` | `[30,120]` | seconds | recovery policy | 需实现边界检查 |
| `automatic_review_reopens` | `3` | attempts / Task | review recovery policy | 需实现边界检查 |
| `review_recovery_window_seconds` | `86400` | seconds from first review fault | review recovery policy | 需实现边界检查 |
| `review_recovery_backoff_seconds` | `[60,300,900]` | seconds | review recovery policy | 需实现边界检查 |
| `execution_timeout_seconds` | `7200` | seconds / Execution | supervisor / frozen recovery policy | 需实现边界检查 |
| `recheck_timeout_seconds` | `30` | seconds | recovery application | 需实现边界检查 |
| `action_ref_ttl_seconds` | `300` | seconds | task action service | 需实现边界检查 |
| `log_pipe_buffer_max_bytes` | `1048576` | bytes / stream | execution output drainer | 需实现边界检查 |
| `execution_log_budget_bytes` | `67108864` | bytes / Execution | private log storage | 需实现边界检查 |

## 逐操作合同

<a id="b01"></a>

### B01 提交不可变任务合同

`POST /v1/tasks` · `operationId=submit_task`

原子保存 TaskSpec、queued 与幂等回执；执行异步。核已配置量表及等级，未知/越界为422 INPUT_INVALID。worker忙碌或依赖未就绪仍可创建排队任务；不接收模型/worker选择。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | lead, admin / `project` |
| 请求正文 | [SubmitTaskRequest](#schema-submittaskrequest) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | `submit_task` |
| CLI | `agentd task submit --file task.json` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |
| `X-Agentd-Project` | `header` | 有条件：authenticated_role == admin and resolved_scope == project | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | admin 操作项目范围时必须明确给出项目；lead/reviewer 的项目来自连接，发送本头返回 INPUT_INVALID。实例操作不得用此头切换范围。 |
| `Origin` | `header` | 有条件：Dashboard session write or session create/delete | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 201 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, STORE_RESTORED |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：FEATURE_UNSUPPORTED, INPUT_INVALID, PROJECT_NOT_READY |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)、[docs/design/TASK_AND_REVIEW_PROTOCOL.md#input-freeze](../../../docs/design/TASK_AND_REVIEW_PROTOCOL.md#input-freeze)。

<a id="b02"></a>

### B02 读取任务详情与可用动作

`GET /v1/tasks/{id}` · `operationId=get_task`

返回当前投影与完整合同；reviewer没有通用任务查询权限；读取不启动模型或恢复任务。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | lead, admin / `project` |
| 请求正文 | 无 |
| 成功响应 | [TaskDetail](#schema-taskdetail) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 不要求 / 不要求 |
| MCP | `get_task` |
| CLI | `agentd task get ID` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `X-Agentd-Project` | `header` | 有条件：authenticated_role == admin and resolved_scope == project | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | admin 操作项目范围时必须明确给出项目；lead/reviewer 的项目来自连接，发送本头返回 INPUT_INVALID。实例操作不得用此头切换范围。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [TaskDetail](#schema-taskdetail) |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="b03"></a>

### B03 分页列出任务

`GET /v1/tasks` · `operationId=list_tasks`

游标绑定身份、项目、过滤、排序及store_epoch；多页不承诺冻结状态，不接受未知查询参数。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | lead, admin / `project` |
| 请求正文 | 无 |
| 成功响应 | [TaskPage](#schema-taskpage) |
| 查询模型 | [TaskListQuery](#schema-tasklistquery) |
| 幂等键 / 存储代次 | 不要求 / 不要求 |
| MCP | `list_tasks` |
| CLI | `agentd task list` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `cursor` | `query` | 否 | `string`；最短 `1` | 按声明类型解码；不接受未知查询参数。 |
| `limit` | `query` | 否 | `integer`；≥ `1`；≤ `100` | 按声明类型解码；不接受未知查询参数。 |
| `status` | `query` | 否 | `string`；枚举 `["queued","running","reviewing","finished","canceled"]` | 按声明类型解码；不接受未知查询参数。 |
| `outcome` | `query` | 否 | `string`；枚举 `["passed","review_failed"]` | 按声明类型解码；不接受未知查询参数。 |
| `model_id` | `query` | 否 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 按声明类型解码；不接受未知查询参数。 |
| `difficulty_level` | `query` | 否 | `integer`；— | 按声明类型解码；不接受未知查询参数。 |
| `X-Agentd-Project` | `header` | 有条件：authenticated_role == admin and resolved_scope == project | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | admin 操作项目范围时必须明确给出项目；lead/reviewer 的项目来自连接，发送本头返回 INPUT_INVALID。实例操作不得用此头切换范围。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [TaskPage](#schema-taskpage) |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：CURSOR_INVALID |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="b04"></a>

### B04 按当前恢复动作继续任务

`POST /v1/tasks/{id}/resume` · `operationId=resume_task`

action_ref固定待处理问题与版本；处置记录不能伪造进程闭合。条件不足保留waiting；不改模型、不清审核或恢复历史。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | lead, admin / `project` |
| 请求正文 | [ResumeTaskRequest](#schema-resumetaskrequest) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | `resume_task` |
| CLI | `agentd task resume ID` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |
| `X-Agentd-Project` | `header` | 有条件：authenticated_role == admin and resolved_scope == project | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | admin 操作项目范围时必须明确给出项目；lead/reviewer 的项目来自连接，发送本头返回 INPUT_INVALID。实例操作不得用此头切换范围。 |
| `Origin` | `header` | 有条件：Dashboard session write or session create/delete | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 202 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, STALE_ACTION, STORE_RESTORED, TASK_TERMINAL |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)、[docs/design/RELIABILITY_AND_STORAGE.md#recovery-actions](../../../docs/design/RELIABILITY_AND_STORAGE.md#recovery-actions)。

<a id="b05"></a>

### B05 登记取消并核对停止

`POST /v1/tasks/{id}/cancel` · `operationId=cancel_task`

取消与终态按事务顺序裁决；停止及租约撤销确认后才canceled。新key重复取消只找回原取消operation。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | lead, admin / `project` |
| 请求正文 | [CancelTaskRequest](#schema-canceltaskrequest) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | `cancel_task` |
| CLI | `agentd task cancel ID` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |
| `X-Agentd-Project` | `header` | 有条件：authenticated_role == admin and resolved_scope == project | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | admin 操作项目范围时必须明确给出项目；lead/reviewer 的项目来自连接，发送本头返回 INPUT_INVALID。实例操作不得用此头切换范围。 |
| `Origin` | `header` | 有条件：Dashboard session write or session create/delete | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 202 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, STORE_RESTORED, TASK_TERMINAL |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="b06"></a>

### B06 领取或找回一项审核

`POST /v1/reviews/next` · `operationId=next_review`

每身份至多一项有效领取；empty也记幂等结果。preferred仅重领本身份历史候选，不改领另一项；过期旧key不生成新租约。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | reviewer / `project` |
| 请求正文 | [NextReviewRequest](#schema-nextreviewrequest) |
| 成功响应 | [ReviewClaim](#schema-reviewclaim) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | `next_review` |
| CLI | `agentd review next` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [ReviewClaim](#schema-reviewclaim) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：CANDIDATE_BUSY, KEY_REUSE, REVIEW_BINDING_CONFLICT, REVIEW_LEASE_EXPIRED, STORE_RESTORED |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)、[docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-materials](../../../docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-materials)。

<a id="b07"></a>

### B07 提交独立审核判决

`POST /v1/reviews/submit` · `operationId=submit_review`

复核授权、候选、有效租约、证据完整性及取消；判决/计数/终态/outbox原子提交。已提交同key先返回原判决，不因完成关闭的租约拒绝重放。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | reviewer / `project` |
| 请求正文 | [ReviewDecision](#schema-reviewdecision) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | `submit_review` |
| CLI | `agentd review submit --file verdict.json` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：ARTIFACT_CORRUPT, ARTIFACT_UNAVAILABLE, KEY_REUSE, REVIEW_BINDING_CONFLICT, REVIEW_LEASE_EXPIRED, STORE_RESTORED |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)、[docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-materials](../../../docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-materials)。

<a id="b08"></a>

### B08 暂缓无法判断的审核

`POST /v1/reviews/defer` · `operationId=defer_review`

释放本次领取、保留候选，进入有界延后或暂停；不产生REJECT，不允许立即无限重领故障候选。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | reviewer / `project` |
| 请求正文 | [DeferReview](#schema-deferreview) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | `defer_review` |
| CLI | `agentd review defer` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, REVIEW_BINDING_CONFLICT, REVIEW_LEASE_EXPIRED, STORE_RESTORED |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)、[docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-materials](../../../docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-materials)。

<a id="b09"></a>

### B09 读取角色事项与事件

`GET /v1/inbox` · `operationId=get_inbox`

事件与当前attention分别分页；读取不领取、不解决attention。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | lead, reviewer / `project` |
| 请求正文 | 无 |
| 成功响应 | [InboxPage](#schema-inboxpage) |
| 查询模型 | [InboxQuery](#schema-inboxquery) |
| 幂等键 / 存储代次 | 不要求 / 不要求 |
| MCP | `get_inbox` |
| CLI | `agentd inbox` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `cursor` | `query` | 否 | `string`；最短 `1` | 按声明类型解码；不接受未知查询参数。 |
| `limit` | `query` | 否 | `integer`；≥ `1`；≤ `100` | 按声明类型解码；不接受未知查询参数。 |
| `attention_cursor` | `query` | 否 | `string`；最短 `1` | 按声明类型解码；不接受未知查询参数。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [InboxPage](#schema-inboxpage) |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：CURSOR_INVALID |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="b10"></a>

### B10 被动读取连接上下文

`GET /v1/context` · `operationId=get_context`

返回绑定项目/角色、支持能力、量表和limits；首次调用不要求预先知道store_epoch；不执行探针。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | lead, reviewer / `project` |
| 请求正文 | 无 |
| 成功响应 | [Context](#schema-context) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 不要求 / 不要求 |
| MCP | `get_context` |
| CLI | `agentd context` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

无路径、查询或额外声明的请求头参数；认证要求仍适用。

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [Context](#schema-context) |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="b11"></a>

### B11 读取模型与难度统计

`GET /v1/model-stats` · `operationId=get_model_stats`

缺失usage为null，展示覆盖率和原生字段重叠口径，不直接相加为总tokens；查询不能更新路由策略，未结束与取消不得从观察口径消失。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | lead, admin / `project` |
| 请求正文 | 无 |
| 成功响应 | [ModelStatsPage](#schema-modelstatspage) |
| 查询模型 | [ModelStatsQuery](#schema-modelstatsquery) |
| 幂等键 / 存储代次 | 不要求 / 不要求 |
| MCP | `get_model_stats` |
| CLI | `agentd model stats` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `cursor` | `query` | 否 | `string`；最短 `1` | 按声明类型解码；不接受未知查询参数。 |
| `limit` | `query` | 否 | `integer`；≥ `1`；≤ `100` | 按声明类型解码；不接受未知查询参数。 |
| `model_id` | `query` | 否 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 按声明类型解码；不接受未知查询参数。 |
| `difficulty_level` | `query` | 否 | `integer`；— | 按声明类型解码；不接受未知查询参数。 |
| `X-Agentd-Project` | `header` | 有条件：authenticated_role == admin and resolved_scope == project | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | admin 操作项目范围时必须明确给出项目；lead/reviewer 的项目来自连接，发送本头返回 INPUT_INVALID。实例操作不得用此头切换范围。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [ModelStatsPage](#schema-modelstatspage) |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：CURSOR_INVALID |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)、[docs/design/TASK_AND_REVIEW_PROTOCOL.md#model-statistics](../../../docs/design/TASK_AND_REVIEW_PROTOCOL.md#model-statistics)。

<a id="b12"></a>

### B12 读取授权成果的原始字节块

`GET /v1/artifacts/{id}` · `operationId=read_artifact`

对象归属及当前授权必查；offset等于size返回EOF空块，大于size为422。GET不续租；activity_ref只证明该次读取。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | lead, reviewer, admin / `project` |
| 请求正文 | 无 |
| 成功响应 | [ArtifactChunk](#schema-artifactchunk) |
| 查询模型 | [ArtifactReadQuery](#schema-artifactreadquery) |
| 幂等键 / 存储代次 | 不要求 / 不要求 |
| MCP | `read_artifact` |
| CLI | `agentd artifact read REF` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `offset` | `query` | 否 | `integer`；≥ `0` | 按声明类型解码；不接受未知查询参数。 |
| `length` | `query` | 否 | `integer`；≥ `1`；≤ `262144` | 按声明类型解码；不接受未知查询参数。 |
| `X-Agentd-Project` | `header` | 有条件：authenticated_role == admin and resolved_scope == project | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | admin 操作项目范围时必须明确给出项目；lead/reviewer 的项目来自连接，发送本头返回 INPUT_INVALID。实例操作不得用此头切换范围。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [ArtifactChunk](#schema-artifactchunk) |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：ARTIFACT_CORRUPT, ARTIFACT_UNAVAILABLE |
| 410 | [Problem](#schema-problem)：ARTIFACT_EXPIRED |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)、[docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-materials](../../../docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-materials)。

<a id="b13"></a>

### B13 按原请求键核对结果

`GET /v1/requests/{request_key}` · `operationId=get_request_result`

仅当前稳定principal与解析scope；不接受principal参数。404不证明原请求不在途，只可同key同内容重试。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | lead, reviewer, admin / `project_or_instance` |
| 请求正文 | 无 |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 不要求 / 不要求 |
| MCP | `get_request_result` |
| CLI | `agentd request get KEY` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `request_key` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `X-Agentd-Project` | `header` | 有条件：authenticated_role == admin and resolved_scope == project | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | admin 操作项目范围时必须明确给出项目；lead/reviewer 的项目来自连接，发送本头返回 INPUT_INVALID。实例操作不得用此头切换范围。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="b14"></a>

### B14 读取持久操作的当前进度

`GET /v1/operations/{id}` · `operationId=get_operation`

reviewer仅自己的操作及允许回执；管理身份按授权范围读取，不因此获得独审写权限。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | lead, reviewer, admin / `project_or_instance` |
| 请求正文 | 无 |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 不要求 / 不要求 |
| MCP | `get_operation` |
| CLI | `agentd operation get ID` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `X-Agentd-Project` | `header` | 有条件：authenticated_role == admin and resolved_scope == project | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | admin 操作项目范围时必须明确给出项目；lead/reviewer 的项目来自连接，发送本头返回 INPUT_INVALID。实例操作不得用此头切换范围。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="b15"></a>

### B15 保存reviewer自产证据

`POST /v1/reviews/evidence` · `operationId=upload_review_evidence`

只接收有界原始字节base64，不按宿主路径读文件；记录候选/principal归属，先发布后登记，不改worker候选。manifest校验所有段并传递保留pin。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | reviewer / `project` |
| 请求正文 | [EvidenceUpload](#schema-evidenceupload) |
| 成功响应 | [EvidenceReply](#schema-evidencereply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | `upload_review_evidence` |
| CLI | `agentd review evidence --handle HANDLE --file FILE` |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 201 | [EvidenceReply](#schema-evidencereply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, REVIEW_BINDING_CONFLICT, REVIEW_LEASE_EXPIRED, STORE_RESTORED |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：CONTENT_HASH_MISMATCH, INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)、[docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-materials](../../../docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-materials)。

<a id="b16"></a>

### B16 连接层有界续租

`POST /v1/reviews/renew` · `operationId=renew_review`

仅适配器使用，不是模型工具；消费新鲜且一次性的activity_ref；重放不再延长，不能超过总期限或复活过期handle。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | reviewer / `project` |
| 请求正文 | [RenewReviewRequest](#schema-renewreviewrequest) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, REVIEW_BINDING_CONFLICT, REVIEW_LEASE_EXPIRED, STORE_RESTORED |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)、[docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-leases](../../../docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-leases)。

<a id="m01"></a>

### M01 建立Dashboard管理会话

`POST /v1/session` · `operationId=create_session`

验证本地bootstrap/管理凭据与Origin后建立有限会话；凭据不回显、不写日志。Set-Cookie使用HttpOnly/SameSite，响应no-store。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | bootstrap / `instance` |
| 请求正文 | [SessionCreate](#schema-sessioncreate) |
| 成功响应 | [SessionReply](#schema-sessionreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 不要求 / 不要求 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

建立会话凭据在正文中验证；Origin 必查并限速，不要求已有会话或 store_epoch。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `Origin` | `header` | 是 | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [SessionReply](#schema-sessionreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="m02"></a>

### M02 退出Dashboard管理会话

`DELETE /v1/session` · `operationId=delete_session`

有效cookie撤销须CSRF和Origin；失效/不存在cookie仅清除浏览器cookie且不要求重新登录。重复退出无业务副作用。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | admin / `instance` |
| 请求正文 | 无 |
| 成功响应 | 无 |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 不要求 / 不要求 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

有效会话撤销必须同时验证 cookie、CSRF、Origin；匿名或失效 cookie 仅允许清 cookie。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `Origin` | `header` | 是 | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 204 | 无正文 |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="m03"></a>

### M03 读取最小存活状态

`GET /v1/health` · `operationId=get_health`

公开最小alive/version；不泄露配置、不做原生探针，不能代表执行/审核已就绪。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | public / `public` |
| 请求正文 | 无 |
| 成功响应 | [HealthReply](#schema-healthreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 不要求 / 不要求 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

公开最小存活信息；没有管理、项目或模型调用权限。

无路径、查询或额外声明的请求头参数；认证要求仍适用。

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [HealthReply](#schema-healthreply) |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="m04"></a>

### M04 读取管理快照

`GET /v1/admin/snapshot` · `operationId=get_admin_snapshot`

一次短读事务给有界快照及当前CSRF token；Cache-Control:no-store，不返回凭据值或主动探针。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | admin / `instance` |
| 请求正文 | 无 |
| 成功响应 | [AdminSnapshot](#schema-adminsnapshot) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 不要求 / 不要求 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

无路径、查询或额外声明的请求头参数；认证要求仍适用。

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [AdminSnapshot](#schema-adminsnapshot) |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="m05"></a>

### M05 登记项目与固定默认配置

`PUT /v1/admin/projects/{id}` · `operationId=save_project`

管理员登记仓库/输入根；允许接线未完但标不可用。冻结任务不追随默认值变更；V0第二活动项目拒绝。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | admin / `project_path` |
| 请求正文 | [ProjectUpdate](#schema-projectupdate) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |
| `Origin` | `header` | 是 | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 201 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, STORE_RESTORED, VERSION_CONFLICT |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：FEATURE_UNSUPPORTED, INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="m06"></a>

### M06 登记或轮换私有凭据来源

`PUT /v1/admin/credential-sources/{id}` · `operationId=save_credential_source`

秘密写私有存储，回执只含公开来源状态；secret请求摘要用不可导出HMAC，不把秘密正文记入operation。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | admin / `instance` |
| 请求正文 | [CredentialSourceUpdate](#schema-credentialsourceupdate) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |
| `Origin` | `header` | 是 | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 201 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, STORE_RESTORED, VERSION_CONFLICT |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="m07"></a>

### M07 保存固定worker配置及准入

`PUT /v1/admin/workers/{id}` · `operationId=save_worker`

执行内容变化追加config；启停仅CAS槽版本。绑定任务不热换模型；retire排空后生效，保存不调用模型。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | admin / `instance` |
| 请求正文 | [WorkerUpdate](#schema-workerupdate) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |
| `Origin` | `header` | 是 | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 201 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, STORE_RESTORED, VERSION_CONFLICT, WORKER_RETIRED |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID, RESOURCE_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)、[docs/design/RUNTIME_LIFECYCLE.md#resource-adjustments](../../../docs/design/RUNTIME_LIFECYCLE.md#resource-adjustments)。

<a id="m08"></a>

### M08 设置用户派发暂停

`PUT /v1/admin/dispatch` · `operationId=set_dispatch`

只改变用户pause，不清维护/资源hold，不停止已有worker；body中的instance/project范围逐次授权。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | admin / `body_scope` |
| 请求正文 | [DispatchUpdate](#schema-dispatchupdate) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |
| `Origin` | `header` | 是 | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, STORE_RESTORED, VERSION_CONFLICT |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="m09"></a>

### M09 接线或撤销角色根

`PUT /v1/admin/projects/{id}/role-bindings/{role}` · `operationId=set_role_binding`

两个根不得相同；凭据写私有连接文件仅返回引用。重绑/撤销使旧epoch和租约失效；重复同值不重复签发。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | admin / `project_path` |
| 请求正文 | [RoleBindingUpdate](#schema-rolebindingupdate) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `role` | `path` | 是 | `string`；枚举 `["lead","reviewer"]` | 固定业务角色。 |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |
| `Origin` | `header` | 是 | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 201 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, STORE_RESTORED, VERSION_CONFLICT |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="m10"></a>

### M10 静态检查worker配置

`POST /v1/admin/workers/{id}/checks` · `operationId=check_worker`

V0只接受static，核语法/路径/可读性/匹配；不运行原生CLI、MCP server或模型。accepted以操作查询观察。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | admin / `instance` |
| 请求正文 | [WorkerCheckRequest](#schema-workercheckrequest) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |
| `Origin` | `header` | 是 | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 202 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, STORE_RESTORED |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="m11"></a>

### M11 保存固定配置目录版本

`PUT /v1/admin/catalog/{kind}/{id}` · `operationId=save_catalog`

唯一catalog路由，按kind验证definition分支；须项目头。验证字节摘要后保存版本；不执行工具/server，旧引用保留。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | admin / `project_header` |
| 请求正文 | [CatalogUpdate](#schema-catalogupdate) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | `path` | 是 | `string`；枚举 `["native-template","tool","mcp","recovery-policy"]` | 目录种类须与definition的固定类型一致；不是任意插件。 |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |
| `X-Agentd-Project` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | admin 操作项目范围时必须明确给出项目；lead/reviewer 的项目来自连接，发送本头返回 INPUT_INVALID。实例操作不得用此头切换范围。 |
| `Origin` | `header` | 是 | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 201 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, STORE_RESTORED, VERSION_CONFLICT |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)。

<a id="m12"></a>

### M12 为下一次执行设置任务资源

`PUT /v1/admin/tasks/{id}/resource-override` · `operationId=set_task_resources`

仅非终态；完整资源向量CAS追加，不改活动cgroup、不resume。当前容量不足可保存待下一次准入。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | admin / `object_project` |
| 请求正文 | [ResourceOverrideUpdate](#schema-resourceoverrideupdate) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |
| `Origin` | `header` | 是 | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 201 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：KEY_REUSE, STORE_RESTORED, TASK_TERMINAL, VERSION_CONFLICT |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID, RESOURCE_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)、[docs/design/RUNTIME_LIFECYCLE.md#resource-adjustments](../../../docs/design/RUNTIME_LIFECYCLE.md#resource-adjustments)。

<a id="m13"></a>

### M13 设置或释放显式内容保留

`PUT /v1/admin/artifacts/{id}/keep` · `operationId=set_artifact_keep`

CAS唯一管理员keep记录；保留manifest传播全部成员，释放只影响该pin，不取消其他义务或伪造缺失内容恢复。

| 合同项 | 声明 |
| --- | --- |
| 角色 / 范围 | admin / `object_project` |
| 请求正文 | [ArtifactKeepUpdate](#schema-artifactkeepupdate) |
| 成功响应 | [CommandReply](#schema-commandreply) |
| 查询模型 | 无 |
| 幂等键 / 存储代次 | 必需 / 必需 |
| MCP | 不作为模型工具 |
| CLI | 无独立模型/CLI映射 |

按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。

| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `path` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 对象标识；仍须按当前身份与项目范围校验归属。 |
| `Idempotency-Key` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。 |
| `X-Agentd-Store-Epoch` | `header` | 是 | `string`；正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | 连接已观察的存储代次；不匹配返回 STORE_RESTORED。客户端必须重新核对，不能自动更换头后重放旧写入。 |
| `Origin` | `header` | 是 | `string`；格式 `"uri"` | 浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。本机来源本身不授予身份权限。 |

| HTTP | 响应 / 稳定错误码 |
| --- | --- |
| 200 | [CommandReply](#schema-commandreply) |
| 201 | [CommandReply](#schema-commandreply) |
| 400 | [Problem](#schema-problem)：JSON_INVALID |
| 401 | [Problem](#schema-problem)：NOT_AUTHENTICATED |
| 403 | [Problem](#schema-problem)：NOT_AUTHORIZED |
| 404 | [Problem](#schema-problem)：NOT_FOUND |
| 409 | [Problem](#schema-problem)：ARTIFACT_UNAVAILABLE, KEY_REUSE, STORE_RESTORED, VERSION_CONFLICT |
| 413 | [Problem](#schema-problem)：REQUEST_TOO_LARGE |
| 415 | [Problem](#schema-problem)：UNSUPPORTED_MEDIA_TYPE |
| 422 | [Problem](#schema-problem)：INPUT_INVALID |
| 429 | [Problem](#schema-problem)：CAPACITY_LIMIT |
| 500 | [Problem](#schema-problem)：INTERNAL_ERROR |
| 503 | [Problem](#schema-problem)：CLIENT_UNAVAILABLE, SERVICE_MAINTENANCE |

语义依据：[docs/design/INTERFACE_GUIDE.md#http-contract](../../../docs/design/INTERFACE_GUIDE.md#http-contract)、[docs/design/RELIABILITY_AND_STORAGE.md#artifact-retention](../../../docs/design/RELIABILITY_AND_STORAGE.md#artifact-retention)。

## 类型与字段

下表由模型 JSON Schema 生成；跨字段规则与原始字节规则还需执行模型校验器。每个类型提供机器可读 schema 的 JSON Pointer。

<a id="schema-action"></a>

### Action

[JSON Schema](schemas.json#/$defs/Action) · [OpenAPI schema](openapi.json#/components/schemas/Action)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `name` | 是 | `string` | 枚举 `["resume_task","cancel_task"]` | — |
| `ref` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |
| `label` | 是 | `string` | 最短 `1` | — |
| `availability` | 是 | `string` | 枚举 `["available","requires_check","unavailable"]` | — |
| `reason_code` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |
| `requirements` | 是 | array&lt;[ResolutionRequirement](#schema-resolutionrequirement)&gt; | — | — |

不接受未声明字段。

<a id="schema-adminserviceview"></a>

### AdminServiceView

[JSON Schema](schemas.json#/$defs/AdminServiceView) · [OpenAPI schema](openapi.json#/components/schemas/AdminServiceView)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `release_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `state` | 是 | `string` | 最短 `1` | — |
| `dispatch` | 是 | [DispatchResult](#schema-dispatchresult) | — | — |
| `maintenance` | 是 | `object` | 额外字段 `{"$ref":"#/$defs/JsonValue"}` | Maintenance observation; V1 lifecycle schema is separately staged. |
| `operations` | 是 | array&lt;[OperationSummary](#schema-operationsummary)&gt; | — | — |

不接受未声明字段。

<a id="schema-adminsnapshot"></a>

### AdminSnapshot

[JSON Schema](schemas.json#/$defs/AdminSnapshot) · [OpenAPI schema](openapi.json#/components/schemas/AdminSnapshot)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `service` | 是 | [AdminServiceView](#schema-adminserviceview) | — | — |
| `projects` | 是 | array&lt;[ProjectView](#schema-projectview)&gt; | — | — |
| `workers` | 是 | array&lt;[WorkerView](#schema-workerview)&gt; | — | — |
| `credential_sources` | 是 | array&lt;[CredentialSourceView](#schema-credentialsourceview)&gt; | — | — |
| `role_bindings` | 是 | array&lt;[BindingView](#schema-bindingview)&gt; | — | — |
| `catalog` | 是 | array&lt;[CatalogView](#schema-catalogview)&gt; | — | — |
| `limits` | 是 | [Limits](#schema-limits) | — | — |
| `csrf_token` | 是 | `string` | 最短 `1` | — |
| `meta` | 是 | [Meta](#schema-meta) | — | — |

不接受未声明字段。

<a id="schema-artifactchunk"></a>

### ArtifactChunk

[JSON Schema](schemas.json#/$defs/ArtifactChunk) · [OpenAPI schema](openapi.json#/components/schemas/ArtifactChunk)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `artifact` | 是 | [ArtifactRef](#schema-artifactref) | — | — |
| `offset` | 是 | `integer` | ≥ `0` | — |
| `length` | 是 | `integer` | ≥ `0`；≤ `262144` | — |
| `encoding` | 是 | `string` | 固定值 `"base64"` | — |
| `data` | 是 | `string` | — | — |
| `eof` | 是 | `boolean` | — | — |
| `next_offset` | 是 | `integer` 或 `null` | `integer`: ≥ `0`；`null`: — | — |
| `activity_ref` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |
| `meta` | 是 | [Meta](#schema-meta) | — | — |

不接受未声明字段。

<a id="schema-artifactinput"></a>

### ArtifactInput

[JSON Schema](schemas.json#/$defs/ArtifactInput) · [OpenAPI schema](openapi.json#/components/schemas/ArtifactInput)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 固定值 `"artifact"` | — |
| `artifact_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |
| `mount_path` | 是 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-artifactkeepresult"></a>

### ArtifactKeepResult

[JSON Schema](schemas.json#/$defs/ArtifactKeepResult) · [OpenAPI schema](openapi.json#/components/schemas/ArtifactKeepResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `artifact_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `explicit_keep` | 是 | `boolean` | — | — |
| `version` | 是 | `integer` | ≥ `0` | — |
| `availability` | 是 | `string` | 枚举 `["available","retiring","missing","corrupt","expired"]` | — |
| `expires_at` | 是 | `string` 或 `null` | `string`: 格式 `"date-time"`；`null`: — | — |

不接受未声明字段。

<a id="schema-artifactkeepupdate"></a>

### ArtifactKeepUpdate

[JSON Schema](schemas.json#/$defs/ArtifactKeepUpdate) · [OpenAPI schema](openapi.json#/components/schemas/ArtifactKeepUpdate)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `expected_version` | 是 | `integer` | ≥ `0` | — |
| `keep` | 是 | `boolean` | — | — |
| `reason` | 是 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-artifactreadquery"></a>

### ArtifactReadQuery

[JSON Schema](schemas.json#/$defs/ArtifactReadQuery) · [OpenAPI schema](openapi.json#/components/schemas/ArtifactReadQuery)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `offset` | 否 | `integer` | ≥ `0`；缺省 `0` | — |
| `length` | 否 | `integer` | ≥ `1`；≤ `262144`；缺省 `65536` | — |

不接受未声明字段。

<a id="schema-artifactref"></a>

### ArtifactRef

[JSON Schema](schemas.json#/$defs/ArtifactRef) · [OpenAPI schema](openapi.json#/components/schemas/ArtifactRef)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `kind` | 是 | `string` | 最短 `1` | — |
| `sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |
| `size_bytes` | 是 | `integer` | ≥ `0` | — |
| `media_type` | 是 | `string` | 最短 `1` | — |
| `availability` | 是 | `string` | 枚举 `["available","retiring","missing","corrupt","expired"]` | — |
| `retention` | 是 | [ArtifactRetention](#schema-artifactretention) | — | — |

不接受未声明字段。

<a id="schema-artifactresolutionevidence"></a>

### ArtifactResolutionEvidence

[JSON Schema](schemas.json#/$defs/ArtifactResolutionEvidence) · [OpenAPI schema](openapi.json#/components/schemas/ArtifactResolutionEvidence)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 固定值 `"artifact"` | — |
| `artifact_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |

不接受未声明字段。

<a id="schema-artifactretention"></a>

### ArtifactRetention

[JSON Schema](schemas.json#/$defs/ArtifactRetention) · [OpenAPI schema](openapi.json#/components/schemas/ArtifactRetention)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `policy_version` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `expires_at` | 是 | `string` 或 `null` | `string`: 格式 `"date-time"`；`null`: — | — |
| `explicit_keep` | 是 | `boolean` | — | — |
| `keep_version` | 是 | `integer` | ≥ `0` | — |
| `pin_count` | 是 | `integer` | ≥ `0` | — |

不接受未声明字段。

<a id="schema-assignment"></a>

### Assignment

[JSON Schema](schemas.json#/$defs/Assignment) · [OpenAPI schema](openapi.json#/components/schemas/Assignment)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `worker_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `model_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `config_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `policy_version` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `reason` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `resource_adjustment_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |

不接受未声明字段。

<a id="schema-assignmentsummary"></a>

### AssignmentSummary

[JSON Schema](schemas.json#/$defs/AssignmentSummary) · [OpenAPI schema](openapi.json#/components/schemas/AssignmentSummary)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `worker_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `model_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `config_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |

不接受未声明字段。

<a id="schema-attention"></a>

### Attention

[JSON Schema](schemas.json#/$defs/Attention) · [OpenAPI schema](openapi.json#/components/schemas/Attention)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `code` | 是 | `string` | 最短 `1` | — |
| `detail` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `subject_ref` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |
| `resolvable_by` | 是 | `string` | 枚举 `["lead","admin","reviewer","system"]` | — |
| `action_ref` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |

不接受未声明字段。

<a id="schema-bindingview"></a>

### BindingView

[JSON Schema](schemas.json#/$defs/BindingView) · [OpenAPI schema](openapi.json#/components/schemas/BindingView)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `role` | 是 | `string` | 枚举 `["lead","reviewer"]` | — |
| `root_ref` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |
| `principal_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `version` | 是 | `integer` | > `0` | — |
| `grant_epoch` | 是 | `integer` | ≥ `0` | — |
| `root_epoch` | 是 | `integer` | ≥ `0` | — |
| `enabled` | 是 | `boolean` | — | — |
| `credential_source_ref` | 是 | `string` | 最短 `1` | — |
| `notification_observation` | 是 | [NotificationObservation](#schema-notificationobservation) | — | — |

不接受未声明字段。

<a id="schema-canceltaskrequest"></a>

### CancelTaskRequest

[JSON Schema](schemas.json#/$defs/CancelTaskRequest) · [OpenAPI schema](openapi.json#/components/schemas/CancelTaskRequest)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `reason` | 否 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-canceltaskresult"></a>

### CancelTaskResult

[JSON Schema](schemas.json#/$defs/CancelTaskResult) · [OpenAPI schema](openapi.json#/components/schemas/CancelTaskResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `task_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `canceled` | 是 | `boolean` | — | — |

不接受未声明字段。

<a id="schema-candidatedeliverable"></a>

### CandidateDeliverable

[JSON Schema](schemas.json#/$defs/CandidateDeliverable) · [OpenAPI schema](openapi.json#/components/schemas/CandidateDeliverable)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `key` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `artifact` | 是 | [ArtifactRef](#schema-artifactref) | — | — |

不接受未声明字段。

<a id="schema-candidateview"></a>

### CandidateView

[JSON Schema](schemas.json#/$defs/CandidateView) · [OpenAPI schema](openapi.json#/components/schemas/CandidateView)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `candidate_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `task_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `round` | 是 | `integer` | ≥ `1`；≤ `3` | — |
| `manifest` | 是 | [ArtifactRef](#schema-artifactref) | — | — |
| `code_commit` | 是 | [GitOid](#schema-gitoid) 或 `null` | `null`: — | — |
| `deliverables` | 是 | array&lt;[CandidateDeliverable](#schema-candidatedeliverable)&gt; | — | — |
| `created_at` | 是 | `string` | 格式 `"date-time"` | — |

不接受未声明字段。

<a id="schema-catalogcontent"></a>

### CatalogContent

[JSON Schema](schemas.json#/$defs/CatalogContent) · [OpenAPI schema](openapi.json#/components/schemas/CatalogContent)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `source_root_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `members` | 是 | array&lt;[CatalogMember](#schema-catalogmember)&gt; | 最少项 `1`；最多项 `128` | — |
| `description` | 是 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-catalogmember"></a>

### CatalogMember

[JSON Schema](schemas.json#/$defs/CatalogMember) · [OpenAPI schema](openapi.json#/components/schemas/CatalogMember)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `relative_path` | 是 | `string` | 最短 `1` | — |
| `sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |

不接受未声明字段。

<a id="schema-catalogupdate"></a>

### CatalogUpdate

[JSON Schema](schemas.json#/$defs/CatalogUpdate) · [OpenAPI schema](openapi.json#/components/schemas/CatalogUpdate)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `expected_version` | 是 | `integer` | ≥ `0` | — |
| `definition` | 是 | [NativeTemplateDefinition](#schema-nativetemplatedefinition) 或 [ToolDefinition](#schema-tooldefinition) 或 [StdioMCPDefinition](#schema-stdiomcpdefinition) 或 [HttpMCPDefinition](#schema-httpmcpdefinition) 或 [RecoveryPolicyDefinition](#schema-recoverypolicydefinition) | — | — |

不接受未声明字段。

<a id="schema-catalogview"></a>

### CatalogView

[JSON Schema](schemas.json#/$defs/CatalogView) · [OpenAPI schema](openapi.json#/components/schemas/CatalogView)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 枚举 `["native-template","tool","mcp","recovery-policy"]` | — |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `version` | 是 | `integer` | > `0` | — |
| `content_sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |
| `readiness` | 是 | [Readiness](#schema-readiness) | — | — |
| `definition` | 是 | [NativeTemplateDefinition](#schema-nativetemplatedefinition) 或 [ToolDefinition](#schema-tooldefinition) 或 [StdioMCPDefinition](#schema-stdiomcpdefinition) 或 [HttpMCPDefinition](#schema-httpmcpdefinition) 或 [RecoveryPolicyDefinition](#schema-recoverypolicydefinition) | — | — |

不接受未声明字段。

<a id="schema-checkresult"></a>

### CheckResult

[JSON Schema](schemas.json#/$defs/CheckResult) · [OpenAPI schema](openapi.json#/components/schemas/CheckResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `name` | 是 | `string` | 最短 `1` | — |
| `status` | 是 | `string` | 枚举 `["pass","fail","unknown"]` | — |
| `reason` | 是 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-codedeliveryobject"></a>

### CodeDeliveryObject

[JSON Schema](schemas.json#/$defs/CodeDeliveryObject) · [OpenAPI schema](openapi.json#/components/schemas/CodeDeliveryObject)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `deliverable_key` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `candidate_commit` | 是 | `string` | 正则 `"^(?:[0-9a-f]{40}\|[0-9a-f]{64})$"` | — |

不接受未声明字段。

<a id="schema-codeworkerdelivery"></a>

### CodeWorkerDelivery

[JSON Schema](schemas.json#/$defs/CodeWorkerDelivery) · [OpenAPI schema](openapi.json#/components/schemas/CodeWorkerDelivery)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `schema_version` | 是 | `string` | 固定值 `"worker-delivery/1"` | — |
| `summary` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `artifacts` | 是 | array&lt;[WorkerArtifact](#schema-workerartifact)&gt; | 最多项 `128` | — |
| `checks` | 是 | array&lt;[WorkerCheck](#schema-workercheck)&gt; | — | — |
| `known_limitations` | 是 | array&lt;`string`&gt; | — | — |
| `kind` | 是 | `string` | 固定值 `"code"` | — |
| `code` | 是 | [CodeDeliveryObject](#schema-codedeliveryobject) | — | — |

不接受未声明字段。

<a id="schema-commandreply"></a>

### CommandReply

[JSON Schema](schemas.json#/$defs/CommandReply) · [OpenAPI schema](openapi.json#/components/schemas/CommandReply)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `operation` | 是 | [Operation](#schema-operation) | — | — |
| `meta` | 是 | [Meta](#schema-meta) | — | — |

不接受未声明字段。

<a id="schema-contentretention"></a>

### ContentRetention

[JSON Schema](schemas.json#/$defs/ContentRetention) · [OpenAPI schema](openapi.json#/components/schemas/ContentRetention)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `final_seconds` | 是 | `integer` 或 `null` | `integer`: > `0`；`null`: — | — |
| `rejected_seconds` | 是 | `integer` 或 `null` | `integer`: > `0`；`null`: — | — |
| `logs_workspace_seconds` | 是 | `integer` 或 `null` | `integer`: > `0`；`null`: — | — |

不接受未声明字段。

<a id="schema-context"></a>

### Context

[JSON Schema](schemas.json#/$defs/Context) · [OpenAPI schema](openapi.json#/components/schemas/Context)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `project` | 是 | [ProjectIdentity](#schema-projectidentity) | — | — |
| `principal` | 是 | [Principal](#schema-principal) | — | — |
| `service` | 是 | [ServiceObservation](#schema-serviceobservation) | — | — |
| `worker_pool` | 是 | [WorkerPoolObservation](#schema-workerpoolobservation) | — | — |
| `notification` | 是 | [NotificationObservation](#schema-notificationobservation) | — | — |
| `capabilities` | 是 | array&lt;`string`&gt; | — | — |
| `limits` | 是 | [Limits](#schema-limits) | — | — |
| `difficulty_scale` | 是 | [DifficultyScale](#schema-difficultyscale) | — | — |
| `recovery_policies` | 是 | array&lt;[FixedRef](#schema-fixedref)&gt; | — | — |
| `attention` | 是 | array&lt;[Attention](#schema-attention)&gt; | — | — |
| `meta` | 是 | [Meta](#schema-meta) | — | — |

不接受未声明字段。

<a id="schema-credentialsourceupdate"></a>

### CredentialSourceUpdate

[JSON Schema](schemas.json#/$defs/CredentialSourceUpdate) · [OpenAPI schema](openapi.json#/components/schemas/CredentialSourceUpdate)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `expected_version` | 是 | `integer` | ≥ `0` | — |
| `purpose` | 是 | `string` | 枚举 `["provider","mcp","notification"]` | — |
| `source` | 是 | [PrivateValueSource](#schema-privatevaluesource) 或 [OwnerFileSource](#schema-ownerfilesource) | 分支字段 `kind` | — |
| `label` | 是 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-credentialsourceview"></a>

### CredentialSourceView

[JSON Schema](schemas.json#/$defs/CredentialSourceView) · [OpenAPI schema](openapi.json#/components/schemas/CredentialSourceView)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `version` | 是 | `integer` | > `0` | — |
| `purpose` | 是 | `string` | 枚举 `["provider","mcp","notification"]` | — |
| `label` | 是 | `string` | 最短 `1` | — |
| `source_kind` | 是 | `string` | 枚举 `["private_value","owner_file"]` | — |
| `status` | 是 | `string` | 枚举 `["configured","missing","unreadable"]` | — |
| `changed_at` | 是 | `string` | 格式 `"date-time"` | — |

不接受未声明字段。

<a id="schema-criterion"></a>

### Criterion

[JSON Schema](schemas.json#/$defs/Criterion) · [OpenAPI schema](openapi.json#/components/schemas/Criterion)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `description` | 是 | `string` | 最短 `1`；最长 `8192` | — |

不接受未声明字段。

<a id="schema-criterionresult"></a>

### CriterionResult

[JSON Schema](schemas.json#/$defs/CriterionResult) · [OpenAPI schema](openapi.json#/components/schemas/CriterionResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `criterion_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `result` | 是 | `string` | 枚举 `["met","unmet","unverified"]` | — |
| `reason` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `evidence_refs` | 是 | array&lt;`string`&gt; | — | — |

不接受未声明字段。

<a id="schema-deferreview"></a>

### DeferReview

[JSON Schema](schemas.json#/$defs/DeferReview) · [OpenAPI schema](openapi.json#/components/schemas/DeferReview)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `review_handle` | 是 | `string` | 最短 `1` | — |
| `reason_code` | 是 | `string` | 枚举 `["CLIENT_INTERRUPTED","INPUT_UNAVAILABLE","ENVIRONMENT_UNAVAILABLE","OTHER"]` | — |
| `reason` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `evidence_refs` | 否 | array&lt;`string`&gt; | — | — |

不接受未声明字段。

<a id="schema-deferreviewresult"></a>

### DeferReviewResult

[JSON Schema](schemas.json#/$defs/DeferReviewResult) · [OpenAPI schema](openapi.json#/components/schemas/DeferReviewResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `candidate_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `deferred` | 是 | `boolean` | 固定值 `true` | — |

不接受未声明字段。

<a id="schema-deliverable"></a>

### Deliverable

[JSON Schema](schemas.json#/$defs/Deliverable) · [OpenAPI schema](openapi.json#/components/schemas/Deliverable)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `key` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `kind` | 是 | `string` | 枚举 `["code_commit","report","file"]` | — |
| `description` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `required` | 是 | `boolean` | — | — |

不接受未声明字段。

<a id="schema-dependency"></a>

### Dependency

[JSON Schema](schemas.json#/$defs/Dependency) · [OpenAPI schema](openapi.json#/components/schemas/Dependency)

D/V1 shape; nonempty dependency lists are rejected by the V0 input.

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `task_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `purpose` | 是 | `string` | 枚举 `["gate","input"]` | — |
| `selector` | 是 | [DependencySelector](#schema-dependencyselector) 或 `null` | `null`: — | — |
| `mount_path` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |

不接受未声明字段。

<a id="schema-dependencyselector"></a>

### DependencySelector

[JSON Schema](schemas.json#/$defs/DependencySelector) · [OpenAPI schema](openapi.json#/components/schemas/DependencySelector)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 枚举 `["passed_commit","artifact"]` | — |
| `artifact_key` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |

不接受未声明字段。

<a id="schema-difficulty"></a>

### Difficulty

[JSON Schema](schemas.json#/$defs/Difficulty) · [OpenAPI schema](openapi.json#/components/schemas/Difficulty)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `scale_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `level` | 是 | `integer` | — | Range is determined by the registered scale, not hardcoded to 1–5. |
| `reason` | 是 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-difficultylevel"></a>

### DifficultyLevel

[JSON Schema](schemas.json#/$defs/DifficultyLevel) · [OpenAPI schema](openapi.json#/components/schemas/DifficultyLevel)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `level` | 是 | `integer` | — | — |
| `description` | 是 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-difficultyscale"></a>

### DifficultyScale

[JSON Schema](schemas.json#/$defs/DifficultyScale) · [OpenAPI schema](openapi.json#/components/schemas/DifficultyScale)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `levels` | 是 | array&lt;[DifficultyLevel](#schema-difficultylevel)&gt; | 最少项 `1` | — |

不接受未声明字段。

<a id="schema-difficultysummary"></a>

### DifficultySummary

[JSON Schema](schemas.json#/$defs/DifficultySummary) · [OpenAPI schema](openapi.json#/components/schemas/DifficultySummary)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `scale_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `level` | 是 | `integer` | — | — |

不接受未声明字段。

<a id="schema-dispatchresult"></a>

### DispatchResult

[JSON Schema](schemas.json#/$defs/DispatchResult) · [OpenAPI schema](openapi.json#/components/schemas/DispatchResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `user_paused` | 是 | `boolean` | — | — |
| `effective_paused` | 是 | `boolean` | — | — |
| `blocking_reasons` | 是 | array&lt;[Attention](#schema-attention)&gt; | — | — |
| `version` | 是 | `integer` | ≥ `0` | — |

不接受未声明字段。

<a id="schema-dispatchscope"></a>

### DispatchScope

[JSON Schema](schemas.json#/$defs/DispatchScope) · [OpenAPI schema](openapi.json#/components/schemas/DispatchScope)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 枚举 `["instance","project"]` | — |
| `project_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |

不接受未声明字段。

<a id="schema-dispatchupdate"></a>

### DispatchUpdate

[JSON Schema](schemas.json#/$defs/DispatchUpdate) · [OpenAPI schema](openapi.json#/components/schemas/DispatchUpdate)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `expected_version` | 是 | `integer` | ≥ `0` | — |
| `scope` | 是 | [DispatchScope](#schema-dispatchscope) | — | — |
| `paused` | 是 | `boolean` | — | — |
| `reason` | 否 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-emptyreviewclaim"></a>

### EmptyReviewClaim

[JSON Schema](schemas.json#/$defs/EmptyReviewClaim) · [OpenAPI schema](openapi.json#/components/schemas/EmptyReviewClaim)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `status` | 是 | `string` | 固定值 `"empty"` | — |
| `reason` | 是 | `string` | 枚举 `["queue_empty","review_paused","no_eligible_candidate"]` | — |
| `meta` | 是 | [Meta](#schema-meta) | — | — |

不接受未声明字段。

<a id="schema-environmentcredentialref"></a>

### EnvironmentCredentialRef

[JSON Schema](schemas.json#/$defs/EnvironmentCredentialRef) · [OpenAPI schema](openapi.json#/components/schemas/EnvironmentCredentialRef)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `name` | 是 | `string` | 最短 `1` | — |
| `credential_source_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |

不接受未声明字段。

<a id="schema-evidencereply"></a>

### EvidenceReply

[JSON Schema](schemas.json#/$defs/EvidenceReply) · [OpenAPI schema](openapi.json#/components/schemas/EvidenceReply)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `artifact` | 是 | [ArtifactRef](#schema-artifactref) | — | — |
| `operation_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `activity_ref` | 是 | `string` | 最短 `1` | — |
| `meta` | 是 | [Meta](#schema-meta) | — | — |

不接受未声明字段。

<a id="schema-evidencesegment"></a>

### EvidenceSegment

[JSON Schema](schemas.json#/$defs/EvidenceSegment) · [OpenAPI schema](openapi.json#/components/schemas/EvidenceSegment)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `index` | 是 | `integer` | ≥ `0` | — |
| `artifact_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |
| `size_bytes` | 是 | `integer` | ≥ `0`；≤ `262144` | — |

不接受未声明字段。

<a id="schema-evidenceupload"></a>

### EvidenceUpload

[JSON Schema](schemas.json#/$defs/EvidenceUpload) · [OpenAPI schema](openapi.json#/components/schemas/EvidenceUpload)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `review_handle` | 是 | `string` | 最短 `1` | — |
| `name` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `kind` | 是 | `string` | 最短 `1` | — |
| `media_type` | 是 | `string` | 最短 `1` | — |
| `content_base64` | 是 | `string` | — | — |
| `sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |

不接受未声明字段。

<a id="schema-executabledefinition"></a>

### ExecutableDefinition

[JSON Schema](schemas.json#/$defs/ExecutableDefinition) · [OpenAPI schema](openapi.json#/components/schemas/ExecutableDefinition)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `path` | 是 | `string` | 最短 `1` | — |
| `sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |

不接受未声明字段。

<a id="schema-executionconfiguration"></a>

### ExecutionConfiguration

[JSON Schema](schemas.json#/$defs/ExecutionConfiguration) · [OpenAPI schema](openapi.json#/components/schemas/ExecutionConfiguration)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `relay_url` | 是 | `string` | 最短 `1` | — |
| `credential_source_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `model_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `parameters` | 是 | array&lt;[ModelParameter](#schema-modelparameter)&gt; | — | — |
| `native_template_ref` | 是 | [FixedRef](#schema-fixedref) | — | — |
| `base_resources` | 是 | [ResourceVector](#schema-resourcevector) | — | — |

不接受未声明字段。

<a id="schema-executioninput"></a>

### ExecutionInput

[JSON Schema](schemas.json#/$defs/ExecutionInput) · [OpenAPI schema](openapi.json#/components/schemas/ExecutionInput)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `schema_version` | 是 | `string` | 固定值 `"execution-input/1"` | — |
| `task_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `execution_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `launch_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `task_spec_ref` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `task_spec_sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |
| `resolved_inputs_ref` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `resolved_inputs_sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |
| `mode` | 是 | `string` | 枚举 `["initial","revision","resume_session","handoff_session","restart_same_contract"]` | — |
| `candidate_ordinal` | 是 | `integer` | ≥ `1`；≤ `3` | — |
| `workspace` | 是 | [ExecutionWorkspace](#schema-executionworkspace) | — | — |
| `previous_candidate_ref` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |
| `review_feedback_ref` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |
| `delivery_schema_ref` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `delivery_target` | 是 | `string` | 最短 `1` | — |
| `session_ref` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |

不接受未声明字段。

<a id="schema-executionobservation"></a>

### ExecutionObservation

[JSON Schema](schemas.json#/$defs/ExecutionObservation) · [OpenAPI schema](openapi.json#/components/schemas/ExecutionObservation)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `observation` | 是 | `string` | 枚举 `["none","preparing","active","interrupted","unknown","stopping","closed"]` | — |
| `execution_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |

不接受未声明字段。

<a id="schema-executionrecoverypolicy"></a>

### ExecutionRecoveryPolicy

[JSON Schema](schemas.json#/$defs/ExecutionRecoveryPolicy) · [OpenAPI schema](openapi.json#/components/schemas/ExecutionRecoveryPolicy)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `automatic_attempts` | 是 | `integer` | ≥ `0` | — |
| `total_elapsed_seconds` | 是 | `integer` | ≥ `0` | — |
| `execution_timeout_seconds` | 是 | `integer` | > `0` | — |
| `backoff_seconds` | 是 | array&lt;`integer`&gt; | — | — |

不接受未声明字段。

<a id="schema-executionworkspace"></a>

### ExecutionWorkspace

[JSON Schema](schemas.json#/$defs/ExecutionWorkspace) · [OpenAPI schema](openapi.json#/components/schemas/ExecutionWorkspace)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `path` | 是 | `string` | 最短 `1` | — |
| `repository_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |
| `base_commit` | 是 | [GitOid](#schema-gitoid) 或 `null` | `null`: — | — |

不接受未声明字段。

<a id="schema-externalreceiptevidence"></a>

### ExternalReceiptEvidence

[JSON Schema](schemas.json#/$defs/ExternalReceiptEvidence) · [OpenAPI schema](openapi.json#/components/schemas/ExternalReceiptEvidence)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 固定值 `"external_receipt"` | — |
| `system` | 是 | `string` | 最短 `1` | — |
| `receipt_id` | 是 | `string` | 最短 `1` | — |
| `checked_at` | 是 | `string` | 格式 `"date-time"` | — |
| `observation` | 是 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-fielderror"></a>

### FieldError

[JSON Schema](schemas.json#/$defs/FieldError) · [OpenAPI schema](openapi.json#/components/schemas/FieldError)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `pointer` | 是 | `string` | — | — |
| `code` | 是 | `string` | 最短 `1` | — |
| `detail` | 是 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-fileinput"></a>

### FileInput

[JSON Schema](schemas.json#/$defs/FileInput) · [OpenAPI schema](openapi.json#/components/schemas/FileInput)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 固定值 `"file"` | — |
| `source_root_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `relative_path` | 是 | `string` | 最短 `1` | — |
| `sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |
| `mount_path` | 是 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-fixedref"></a>

### FixedRef

[JSON Schema](schemas.json#/$defs/FixedRef) · [OpenAPI schema](openapi.json#/components/schemas/FixedRef)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `version` | 是 | `integer` | > `0` | — |

不接受未声明字段。

<a id="schema-gitinput"></a>

### GitInput

[JSON Schema](schemas.json#/$defs/GitInput) · [OpenAPI schema](openapi.json#/components/schemas/GitInput)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 固定值 `"git"` | — |
| `source_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `commit` | 是 | [GitOid](#schema-gitoid) | — | — |
| `mount_path` | 是 | `string` | 最短 `1` | — |
| `purpose` | 是 | `string` | 枚举 `["base","material"]` | — |

不接受未声明字段。

<a id="schema-gitoid"></a>

### GitOid

[JSON Schema](schemas.json#/$defs/GitOid) · [OpenAPI schema](openapi.json#/components/schemas/GitOid)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `algorithm` | 是 | `string` | 枚举 `["sha1","sha256"]` | — |
| `value` | 是 | `string` | 正则 `"^[0-9a-f]+$"` | — |

不接受未声明字段。

<a id="schema-healthreply"></a>

### HealthReply

[JSON Schema](schemas.json#/$defs/HealthReply) · [OpenAPI schema](openapi.json#/components/schemas/HealthReply)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `status` | 是 | `string` | 固定值 `"alive"` | — |
| `release_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `api_version` | 是 | `string` | 固定值 `"1"` | — |

不接受未声明字段。

<a id="schema-heldreviewclaim"></a>

### HeldReviewClaim

[JSON Schema](schemas.json#/$defs/HeldReviewClaim) · [OpenAPI schema](openapi.json#/components/schemas/HeldReviewClaim)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `status` | 是 | `string` | 固定值 `"claimed"` | — |
| `review_handle` | 是 | `string` | 最短 `1` | — |
| `candidate` | 是 | [CandidateView](#schema-candidateview) | — | — |
| `task_spec` | 是 | [TaskSpec](#schema-taskspec) | — | — |
| `evidence_index` | 是 | [ArtifactRef](#schema-artifactref) | — | — |
| `materialization_manifest_ref` | 是 | [ArtifactRef](#schema-artifactref) | — | — |
| `lease_expires_at` | 是 | `string` | 格式 `"date-time"` | — |
| `max_hold_until` | 是 | `string` | 格式 `"date-time"` | — |
| `operation_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `meta` | 是 | [Meta](#schema-meta) | — | — |

不接受未声明字段。

<a id="schema-httpmcpdefinition"></a>

### HttpMCPDefinition

[JSON Schema](schemas.json#/$defs/HttpMCPDefinition) · [OpenAPI schema](openapi.json#/components/schemas/HttpMCPDefinition)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `transport` | 是 | `string` | 固定值 `"http"` | — |
| `url` | 是 | `string` | 最短 `1` | — |
| `credential_source_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |
| `description` | 是 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-inboxevent"></a>

### InboxEvent

[JSON Schema](schemas.json#/$defs/InboxEvent) · [OpenAPI schema](openapi.json#/components/schemas/InboxEvent)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `event_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `kind` | 是 | `string` | 最短 `1` | — |
| `task_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |
| `operation_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |
| `summary` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `created_at` | 是 | `string` | 格式 `"date-time"` | — |

不接受未声明字段。

<a id="schema-inboxpage"></a>

### InboxPage

[JSON Schema](schemas.json#/$defs/InboxPage) · [OpenAPI schema](openapi.json#/components/schemas/InboxPage)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `items` | 是 | array&lt;[InboxEvent](#schema-inboxevent)&gt; | 最多项 `100` | — |
| `next_cursor` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |
| `attention` | 是 | array&lt;[Attention](#schema-attention)&gt; | 最多项 `100` | — |
| `attention_next_cursor` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |
| `meta` | 是 | [Meta](#schema-meta) | — | — |

不接受未声明字段。

<a id="schema-inboxquery"></a>

### InboxQuery

[JSON Schema](schemas.json#/$defs/InboxQuery) · [OpenAPI schema](openapi.json#/components/schemas/InboxQuery)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `cursor` | 否 | `string` | 最短 `1` | — |
| `limit` | 否 | `integer` | ≥ `1`；≤ `100`；缺省 `20` | — |
| `attention_cursor` | 否 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-inputroot"></a>

### InputRoot

[JSON Schema](schemas.json#/$defs/InputRoot) · [OpenAPI schema](openapi.json#/components/schemas/InputRoot)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `path` | 是 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-jsonvalue"></a>

### JsonValue

[JSON Schema](schemas.json#/$defs/JsonValue) · [OpenAPI schema](openapi.json#/components/schemas/JsonValue)

| 值 | 类型/分支 | 约束 |
| --- | --- | --- |
| 根值 | 见 schema | — |

<a id="schema-knownusage"></a>

### KnownUsage

[JSON Schema](schemas.json#/$defs/KnownUsage) · [OpenAPI schema](openapi.json#/components/schemas/KnownUsage)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `input_tokens` | 是 | `integer` 或 `null` | `integer`: ≥ `0`；`null`: — | — |
| `output_tokens` | 是 | `integer` 或 `null` | `integer`: ≥ `0`；`null`: — | — |
| `cache_tokens` | 是 | `integer` 或 `null` | `integer`: ≥ `0`；`null`: — | — |
| `reasoning_tokens` | 是 | `integer` 或 `null` | `integer`: ≥ `0`；`null`: — | — |
| `coverage` | 是 | `number` | ≥ `0`；≤ `1` | — |
| `scope` | 是 | `string` | 枚举 `["worker","all_roles","partial"]` | — |

不接受未声明字段。

<a id="schema-latencystats"></a>

### LatencyStats

[JSON Schema](schemas.json#/$defs/LatencyStats) · [OpenAPI schema](openapi.json#/components/schemas/LatencyStats)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `sample_count` | 是 | `integer` | ≥ `0` | — |
| `median_seconds` | 是 | `number` 或 `null` | `number`: ≥ `0`；`null`: — | — |

不接受未声明字段。

<a id="schema-limits"></a>

### Limits

[JSON Schema](schemas.json#/$defs/Limits) · [OpenAPI schema](openapi.json#/components/schemas/Limits)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `version` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `values` | 是 | `object` | 额外字段 `{"$ref":"#/$defs/JsonValue"}` | Named support-profile values; not arbitrary service actions. |

不接受未声明字段。

<a id="schema-meta"></a>

### Meta

[JSON Schema](schemas.json#/$defs/Meta) · [OpenAPI schema](openapi.json#/components/schemas/Meta)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `api_version` | 是 | `string` | 固定值 `"1"` | — |
| `instance_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `store_epoch` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `observed_at` | 是 | `string` | 格式 `"date-time"` | — |
| `observed_revision` | 是 | `integer` | ≥ `0` | — |

不接受未声明字段。

<a id="schema-modelparameter"></a>

### ModelParameter

[JSON Schema](schemas.json#/$defs/ModelParameter) · [OpenAPI schema](openapi.json#/components/schemas/ModelParameter)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `name` | 是 | `string` | 最短 `1` | — |
| `value` | 是 | `string` 或 `integer` 或 `number` 或 `boolean` 或 `null` | `string`: —；`integer`: —；`number`: —；`boolean`: —；`null`: — | — |

不接受未声明字段。

<a id="schema-modelstat"></a>

### ModelStat

[JSON Schema](schemas.json#/$defs/ModelStat) · [OpenAPI schema](openapi.json#/components/schemas/ModelStat)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `model_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `difficulty` | 是 | [DifficultySummary](#schema-difficultysummary) | — | — |
| `passed` | 是 | `integer` | ≥ `0` | — |
| `review_failed` | 是 | `integer` | ≥ `0` | — |
| `canceled` | 是 | `integer` | ≥ `0` | — |
| `unfinished` | 是 | [UnfinishedCounts](#schema-unfinishedcounts) | — | — |
| `completion_rate` | 是 | `number` 或 `null` | `number`: ≥ `0`；≤ `1`；`null`: — | — |
| `known_usage` | 是 | [KnownUsage](#schema-knownusage) | — | — |
| `latency` | 是 | [LatencyStats](#schema-latencystats) | — | — |
| `routing` | 是 | [RoutingExplanation](#schema-routingexplanation) | — | — |

不接受未声明字段。

<a id="schema-modelstatspage"></a>

### ModelStatsPage

[JSON Schema](schemas.json#/$defs/ModelStatsPage) · [OpenAPI schema](openapi.json#/components/schemas/ModelStatsPage)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `items` | 是 | array&lt;[ModelStat](#schema-modelstat)&gt; | 最多项 `100` | — |
| `next_cursor` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |
| `meta` | 是 | [Meta](#schema-meta) | — | — |

不接受未声明字段。

<a id="schema-modelstatsquery"></a>

### ModelStatsQuery

[JSON Schema](schemas.json#/$defs/ModelStatsQuery) · [OpenAPI schema](openapi.json#/components/schemas/ModelStatsQuery)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `cursor` | 否 | `string` | 最短 `1` | — |
| `limit` | 否 | `integer` | ≥ `1`；≤ `100`；缺省 `20` | — |
| `model_id` | 否 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `difficulty_level` | 否 | `integer` | — | — |

不接受未声明字段。

<a id="schema-nativetemplatedefinition"></a>

### NativeTemplateDefinition

[JSON Schema](schemas.json#/$defs/NativeTemplateDefinition) · [OpenAPI schema](openapi.json#/components/schemas/NativeTemplateDefinition)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `source_root_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `members` | 是 | array&lt;[CatalogMember](#schema-catalogmember)&gt; | 最少项 `1`；最多项 `128` | — |
| `description` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `settings_entry` | 是 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-nextreviewrequest"></a>

### NextReviewRequest

[JSON Schema](schemas.json#/$defs/NextReviewRequest) · [OpenAPI schema](openapi.json#/components/schemas/NextReviewRequest)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `preferred_candidate_id` | 否 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |

不接受未声明字段。

<a id="schema-nextreviewresult"></a>

### NextReviewResult

[JSON Schema](schemas.json#/$defs/NextReviewResult) · [OpenAPI schema](openapi.json#/components/schemas/NextReviewResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `claim` | 是 | [ReviewClaim](#schema-reviewclaim) | — | — |

不接受未声明字段。

<a id="schema-notificationobservation"></a>

### NotificationObservation

[JSON Schema](schemas.json#/$defs/NotificationObservation) · [OpenAPI schema](openapi.json#/components/schemas/NotificationObservation)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `configured` | 是 | `boolean` | — | — |
| `verified` | 是 | `boolean` | — | — |
| `status` | 是 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-operation"></a>

### Operation

[JSON Schema](schemas.json#/$defs/Operation) · [OpenAPI schema](openapi.json#/components/schemas/Operation)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `operation_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `kind` | 是 | `string` | 枚举 `["submit_task","resume_task","cancel_task","next_review","submit_review","defer_review","upload_review_evidence","renew_review","save_project","save_credential_source","save_worker","set_dispatch","set_role_binding","check_worker","save_catalog","set_task_resources","set_artifact_keep"]` | — |
| `scope` | 是 | [OperationScope](#schema-operationscope) | — | — |
| `request_key` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `phase` | 是 | `string` | 枚举 `["accepted","completed","waiting","failed"]` | — |
| `version` | 是 | `integer` | ≥ `0` | — |
| `created_at` | 是 | `string` | 格式 `"date-time"` | — |
| `updated_at` | 是 | `string` | 格式 `"date-time"` | — |
| `resource_refs` | 是 | array&lt;[ResourceRef](#schema-resourceref)&gt; | — | — |
| `result` | 是 | [SubmitTaskResult](#schema-submittaskresult) 或 [ResumeTaskResult](#schema-resumetaskresult) 或 [CancelTaskResult](#schema-canceltaskresult) 或 [NextReviewResult](#schema-nextreviewresult) 或 [SubmitReviewResult](#schema-submitreviewresult) 或 [DeferReviewResult](#schema-deferreviewresult) 或 [UploadReviewEvidenceResult](#schema-uploadreviewevidenceresult) 或 [RenewReviewResult](#schema-renewreviewresult) 或 [SaveProjectResult](#schema-saveprojectresult) 或 [CredentialSourceView](#schema-credentialsourceview) 或 [SaveWorkerResult](#schema-saveworkerresult) 或 [DispatchResult](#schema-dispatchresult) 或 [RoleBindingResult](#schema-rolebindingresult) 或 [WorkerCheckResult](#schema-workercheckresult) 或 [SaveCatalogResult](#schema-savecatalogresult) 或 [ResourceOverrideResult](#schema-resourceoverrideresult) 或 [ArtifactKeepResult](#schema-artifactkeepresult) 或 `null` | `null`: — | — |
| `attention` | 是 | array&lt;[Attention](#schema-attention)&gt; | — | — |
| `problem` | 是 | [Problem](#schema-problem) 或 `null` | `null`: — | — |

不接受未声明字段。

<a id="schema-operationscope"></a>

### OperationScope

[JSON Schema](schemas.json#/$defs/OperationScope) · [OpenAPI schema](openapi.json#/components/schemas/OperationScope)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `project_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |

不接受未声明字段。

<a id="schema-operationsummary"></a>

### OperationSummary

[JSON Schema](schemas.json#/$defs/OperationSummary) · [OpenAPI schema](openapi.json#/components/schemas/OperationSummary)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `operation_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `kind` | 是 | `string` | 枚举 `["submit_task","resume_task","cancel_task","next_review","submit_review","defer_review","upload_review_evidence","renew_review","save_project","save_credential_source","save_worker","set_dispatch","set_role_binding","check_worker","save_catalog","set_task_resources","set_artifact_keep"]` | — |
| `phase` | 是 | `string` | 枚举 `["accepted","completed","waiting","failed"]` | — |
| `version` | 是 | `integer` | ≥ `0` | — |
| `updated_at` | 是 | `string` | 格式 `"date-time"` | — |

不接受未声明字段。

<a id="schema-operatorstatementevidence"></a>

### OperatorStatementEvidence

[JSON Schema](schemas.json#/$defs/OperatorStatementEvidence) · [OpenAPI schema](openapi.json#/components/schemas/OperatorStatementEvidence)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 固定值 `"operator_statement"` | — |
| `statement` | 是 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-ownerfilesource"></a>

### OwnerFileSource

[JSON Schema](schemas.json#/$defs/OwnerFileSource) · [OpenAPI schema](openapi.json#/components/schemas/OwnerFileSource)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 固定值 `"owner_file"` | — |
| `path` | 是 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-pagequery"></a>

### PageQuery

[JSON Schema](schemas.json#/$defs/PageQuery) · [OpenAPI schema](openapi.json#/components/schemas/PageQuery)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `cursor` | 否 | `string` | 最短 `1` | — |
| `limit` | 否 | `integer` | ≥ `1`；≤ `100`；缺省 `20` | — |

不接受未声明字段。

<a id="schema-principal"></a>

### Principal

[JSON Schema](schemas.json#/$defs/Principal) · [OpenAPI schema](openapi.json#/components/schemas/Principal)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `role` | 是 | `string` | 枚举 `["lead","reviewer"]` | — |

不接受未声明字段。

<a id="schema-privatevaluesource"></a>

### PrivateValueSource

[JSON Schema](schemas.json#/$defs/PrivateValueSource) · [OpenAPI schema](openapi.json#/components/schemas/PrivateValueSource)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 固定值 `"private_value"` | — |
| `value` | 是 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-problem"></a>

### Problem

[JSON Schema](schemas.json#/$defs/Problem) · [OpenAPI schema](openapi.json#/components/schemas/Problem)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `type` | 是 | `string` | 最短 `1` | — |
| `title` | 是 | `string` | 最短 `1` | — |
| `status` | 是 | `integer` | ≥ `400`；≤ `599` | — |
| `detail` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `instance` | 是 | `string` | 最短 `1` | — |
| `code` | 是 | `string` | 最短 `1` | — |
| `retry` | 是 | `string` | 枚举 `["never","same_request","refresh_then_new_request","query_request"]` | — |
| `operation_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |
| `request_recorded` | 是 | `boolean` 或 `null` | `boolean`: —；`null`: — | — |
| `field_errors` | 是 | array&lt;[FieldError](#schema-fielderror)&gt; | — | — |

不接受未声明字段。

<a id="schema-projectdefinition"></a>

### ProjectDefinition

[JSON Schema](schemas.json#/$defs/ProjectDefinition) · [OpenAPI schema](openapi.json#/components/schemas/ProjectDefinition)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `name` | 是 | `string` | 最短 `1` | — |
| `repository` | 是 | [RepositoryDefinition](#schema-repositorydefinition) 或 `null` | `null`: — | — |
| `input_roots` | 是 | array&lt;[InputRoot](#schema-inputroot)&gt; | — | — |
| `default_requirements` | 是 | [Requirements](#schema-requirements) | — | — |
| `recovery_policy_ref` | 是 | [FixedRef](#schema-fixedref) 或 `null` | `null`: — | — |
| `shared_resource_registry` | 是 | array&lt;[SharedResourceDefinition](#schema-sharedresourcedefinition)&gt; | — | — |
| `content_retention` | 否 | [ContentRetention](#schema-contentretention) | — | — |

不接受未声明字段。

<a id="schema-projectidentity"></a>

### ProjectIdentity

[JSON Schema](schemas.json#/$defs/ProjectIdentity) · [OpenAPI schema](openapi.json#/components/schemas/ProjectIdentity)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `name` | 是 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-projectimpact"></a>

### ProjectImpact

[JSON Schema](schemas.json#/$defs/ProjectImpact) · [OpenAPI schema](openapi.json#/components/schemas/ProjectImpact)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `future_tasks` | 是 | `boolean` | — | — |
| `bound_tasks` | 是 | `boolean` | — | — |

不接受未声明字段。

<a id="schema-projectupdate"></a>

### ProjectUpdate

[JSON Schema](schemas.json#/$defs/ProjectUpdate) · [OpenAPI schema](openapi.json#/components/schemas/ProjectUpdate)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `name` | 是 | `string` | 最短 `1` | — |
| `repository` | 是 | [RepositoryDefinition](#schema-repositorydefinition) 或 `null` | `null`: — | — |
| `input_roots` | 是 | array&lt;[InputRoot](#schema-inputroot)&gt; | — | — |
| `default_requirements` | 是 | [Requirements](#schema-requirements) | — | — |
| `recovery_policy_ref` | 是 | [FixedRef](#schema-fixedref) 或 `null` | `null`: — | — |
| `shared_resource_registry` | 是 | array&lt;[SharedResourceDefinition](#schema-sharedresourcedefinition)&gt; | — | — |
| `content_retention` | 否 | [ContentRetention](#schema-contentretention) | — | — |
| `expected_version` | 是 | `integer` | ≥ `0` | — |

不接受未声明字段。

<a id="schema-projectview"></a>

### ProjectView

[JSON Schema](schemas.json#/$defs/ProjectView) · [OpenAPI schema](openapi.json#/components/schemas/ProjectView)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `name` | 是 | `string` | 最短 `1` | — |
| `repository` | 是 | [RepositoryDefinition](#schema-repositorydefinition) 或 `null` | `null`: — | — |
| `input_roots` | 是 | array&lt;[InputRoot](#schema-inputroot)&gt; | — | — |
| `default_requirements` | 是 | [Requirements](#schema-requirements) | — | — |
| `recovery_policy_ref` | 是 | [FixedRef](#schema-fixedref) 或 `null` | `null`: — | — |
| `shared_resource_registry` | 是 | array&lt;[SharedResourceDefinition](#schema-sharedresourcedefinition)&gt; | — | — |
| `content_retention` | 是 | [ContentRetention](#schema-contentretention) | — | — |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `version` | 是 | `integer` | > `0` | — |
| `repository_identity` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |
| `readiness` | 是 | [Readiness](#schema-readiness) | — | — |

不接受未声明字段。

<a id="schema-readiness"></a>

### Readiness

[JSON Schema](schemas.json#/$defs/Readiness) · [OpenAPI schema](openapi.json#/components/schemas/Readiness)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `state` | 是 | `string` | 枚举 `["ready","unavailable","unknown"]` | — |
| `reasons` | 是 | array&lt;[Attention](#schema-attention)&gt; | — | — |
| `observed_at` | 是 | `string` | 格式 `"date-time"` | — |

不接受未声明字段。

<a id="schema-recoverypolicydefinition"></a>

### RecoveryPolicyDefinition

[JSON Schema](schemas.json#/$defs/RecoveryPolicyDefinition) · [OpenAPI schema](openapi.json#/components/schemas/RecoveryPolicyDefinition)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `execution` | 是 | [ExecutionRecoveryPolicy](#schema-executionrecoverypolicy) | — | — |
| `review` | 是 | [ReviewRecoveryPolicy](#schema-reviewrecoverypolicy) | — | — |
| `check_timeout_seconds` | 是 | `integer` | > `0` | — |

不接受未声明字段。

<a id="schema-renewreviewrequest"></a>

### RenewReviewRequest

[JSON Schema](schemas.json#/$defs/RenewReviewRequest) · [OpenAPI schema](openapi.json#/components/schemas/RenewReviewRequest)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `review_handle` | 是 | `string` | 最短 `1` | — |
| `activity_ref` | 是 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-renewreviewresult"></a>

### RenewReviewResult

[JSON Schema](schemas.json#/$defs/RenewReviewResult) · [OpenAPI schema](openapi.json#/components/schemas/RenewReviewResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `candidate_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `lease_expires_at` | 是 | `string` | 格式 `"date-time"` | — |
| `max_hold_until` | 是 | `string` | 格式 `"date-time"` | — |

不接受未声明字段。

<a id="schema-reportworkerdelivery"></a>

### ReportWorkerDelivery

[JSON Schema](schemas.json#/$defs/ReportWorkerDelivery) · [OpenAPI schema](openapi.json#/components/schemas/ReportWorkerDelivery)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `schema_version` | 是 | `string` | 固定值 `"worker-delivery/1"` | — |
| `summary` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `artifacts` | 是 | array&lt;[WorkerArtifact](#schema-workerartifact)&gt; | 最多项 `128` | — |
| `checks` | 是 | array&lt;[WorkerCheck](#schema-workercheck)&gt; | — | — |
| `known_limitations` | 是 | array&lt;`string`&gt; | — | — |
| `kind` | 是 | `string` | 固定值 `"report"` | — |
| `report_name` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |

不接受未声明字段。

<a id="schema-repositorydefinition"></a>

### RepositoryDefinition

[JSON Schema](schemas.json#/$defs/RepositoryDefinition) · [OpenAPI schema](openapi.json#/components/schemas/RepositoryDefinition)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `source_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `path` | 是 | `string` | 最短 `1` | — |
| `review_export` | 是 | `string` | 固定值 `"reachable_history"` | — |

不接受未声明字段。

<a id="schema-requirements"></a>

### Requirements

[JSON Schema](schemas.json#/$defs/Requirements) · [OpenAPI schema](openapi.json#/components/schemas/Requirements)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `tool_refs` | 是 | array&lt;[FixedRef](#schema-fixedref)&gt; | — | — |
| `mcp_refs` | 是 | array&lt;[FixedRef](#schema-fixedref)&gt; | — | — |
| `shared_resources` | 是 | array&lt;[ResourceRequirement](#schema-resourcerequirement)&gt; | — | — |

不接受未声明字段。

<a id="schema-resolution"></a>

### Resolution

[JSON Schema](schemas.json#/$defs/Resolution) · [OpenAPI schema](openapi.json#/components/schemas/Resolution)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `issue_ref` | 是 | `string` | 最短 `1` | — |
| `decision` | 是 | `string` | 枚举 `["not_applied","already_applied","safe_to_repeat","compensated","environment_repaired","restart_from_fixed_inputs"]` | — |
| `note` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `evidence` | 是 | array&lt;[ArtifactResolutionEvidence](#schema-artifactresolutionevidence) 或 [ExternalReceiptEvidence](#schema-externalreceiptevidence) 或 [OperatorStatementEvidence](#schema-operatorstatementevidence)&gt; | — | — |

不接受未声明字段。

<a id="schema-resolutionrequirement"></a>

### ResolutionRequirement

[JSON Schema](schemas.json#/$defs/ResolutionRequirement) · [OpenAPI schema](openapi.json#/components/schemas/ResolutionRequirement)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `issue_ref` | 是 | `string` | 最短 `1` | — |
| `kind` | 是 | `string` | 枚举 `["external_effect","environment_check","progress_loss"]` | — |
| `description` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `allowed_decisions` | 是 | array&lt;`string`&gt; | — | — |
| `evidence_required` | 是 | `boolean` | — | — |

不接受未声明字段。

<a id="schema-resolvedinputsview"></a>

### ResolvedInputsView

[JSON Schema](schemas.json#/$defs/ResolvedInputsView) · [OpenAPI schema](openapi.json#/components/schemas/ResolvedInputsView)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `manifest` | 是 | [ArtifactRef](#schema-artifactref) | — | — |
| `base_commit` | 是 | [GitOid](#schema-gitoid) 或 `null` | `null`: — | — |

不接受未声明字段。

<a id="schema-resourceoverrideresult"></a>

### ResourceOverrideResult

[JSON Schema](schemas.json#/$defs/ResourceOverrideResult) · [OpenAPI schema](openapi.json#/components/schemas/ResourceOverrideResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `task_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `override_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `version` | 是 | `integer` | > `0` | — |
| `effective_from` | 是 | `string` | 固定值 `"next_execution"` | — |
| `resources` | 是 | [ResourceVector](#schema-resourcevector) | — | — |

不接受未声明字段。

<a id="schema-resourceoverrideupdate"></a>

### ResourceOverrideUpdate

[JSON Schema](schemas.json#/$defs/ResourceOverrideUpdate) · [OpenAPI schema](openapi.json#/components/schemas/ResourceOverrideUpdate)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `expected_version` | 是 | `integer` | ≥ `0` | — |
| `resources` | 是 | [ResourceVector](#schema-resourcevector) | — | — |
| `reason` | 是 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-resourceoverrideview"></a>

### ResourceOverrideView

[JSON Schema](schemas.json#/$defs/ResourceOverrideView) · [OpenAPI schema](openapi.json#/components/schemas/ResourceOverrideView)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `version` | 是 | `integer` | ≥ `0` | — |
| `override_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |
| `resources` | 是 | [ResourceVector](#schema-resourcevector) 或 `null` | `null`: — | — |

不接受未声明字段。

<a id="schema-resourceref"></a>

### ResourceRef

[JSON Schema](schemas.json#/$defs/ResourceRef) · [OpenAPI schema](openapi.json#/components/schemas/ResourceRef)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 最短 `1` | — |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |

不接受未声明字段。

<a id="schema-resourcerequirement"></a>

### ResourceRequirement

[JSON Schema](schemas.json#/$defs/ResourceRequirement) · [OpenAPI schema](openapi.json#/components/schemas/ResourceRequirement)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `resource_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `access_mode` | 是 | `string` | 枚举 `["read","write"]` | — |

不接受未声明字段。

<a id="schema-resourcevector"></a>

### ResourceVector

[JSON Schema](schemas.json#/$defs/ResourceVector) · [OpenAPI schema](openapi.json#/components/schemas/ResourceVector)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `cpu_quota` | 是 | `number` | > `0` | Percent of one logical CPU; 100 means one CPU. |
| `memory_bytes` | 是 | `integer` | > `0` | — |
| `pids` | 是 | `integer` | > `0` | — |
| `swap_bytes` | 是 | `integer` | ≥ `0` | — |

不接受未声明字段。

<a id="schema-resumetaskrequest"></a>

### ResumeTaskRequest

[JSON Schema](schemas.json#/$defs/ResumeTaskRequest) · [OpenAPI schema](openapi.json#/components/schemas/ResumeTaskRequest)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `action_ref` | 是 | `string` | 最短 `1` | — |
| `resolutions` | 否 | array&lt;[Resolution](#schema-resolution)&gt; | — | — |

不接受未声明字段。

<a id="schema-resumetaskresult"></a>

### ResumeTaskResult

[JSON Schema](schemas.json#/$defs/ResumeTaskResult) · [OpenAPI schema](openapi.json#/components/schemas/ResumeTaskResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `task_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `recovery_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `execution_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |
| `review_reopened` | 是 | `boolean` | — | — |

不接受未声明字段。

<a id="schema-reviewclaim"></a>

### ReviewClaim

[JSON Schema](schemas.json#/$defs/ReviewClaim) · [OpenAPI schema](openapi.json#/components/schemas/ReviewClaim)

| 值 | 类型/分支 | 约束 |
| --- | --- | --- |
| 根值 | [EmptyReviewClaim](#schema-emptyreviewclaim) 或 [HeldReviewClaim](#schema-heldreviewclaim) | 分支字段 `status` |

<a id="schema-reviewdecision"></a>

### ReviewDecision

[JSON Schema](schemas.json#/$defs/ReviewDecision) · [OpenAPI schema](openapi.json#/components/schemas/ReviewDecision)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `review_handle` | 是 | `string` | 最短 `1` | — |
| `verdict` | 是 | `string` | 枚举 `["PASS","REJECT"]` | — |
| `reason` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `evidence_refs` | 是 | array&lt;[ReviewEvidenceRef](#schema-reviewevidenceref)&gt; | — | — |
| `criterion_results` | 是 | array&lt;[CriterionResult](#schema-criterionresult)&gt; | 最少项 `1`；最多项 `64` | — |

不接受未声明字段。

<a id="schema-reviewevidencemanifest"></a>

### ReviewEvidenceManifest

[JSON Schema](schemas.json#/$defs/ReviewEvidenceManifest) · [OpenAPI schema](openapi.json#/components/schemas/ReviewEvidenceManifest)

D: validates metadata; actual concatenated bytes must be checked by ArtifactStore.

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `schema_version` | 是 | `string` | 固定值 `"review-evidence/1"` | — |
| `members` | 是 | array&lt;[EvidenceSegment](#schema-evidencesegment)&gt; | 最少项 `1`；最多项 `64` | — |
| `total_size_bytes` | 是 | `integer` | ≥ `0`；≤ `16777216` | — |
| `total_sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |

不接受未声明字段。

<a id="schema-reviewevidenceref"></a>

### ReviewEvidenceRef

[JSON Schema](schemas.json#/$defs/ReviewEvidenceRef) · [OpenAPI schema](openapi.json#/components/schemas/ReviewEvidenceRef)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `artifact_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |

不接受未声明字段。

<a id="schema-reviewobservation"></a>

### ReviewObservation

[JSON Schema](schemas.json#/$defs/ReviewObservation) · [OpenAPI schema](openapi.json#/components/schemas/ReviewObservation)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `observation` | 是 | `string` | 枚举 `["none","queued","leased","paused","unavailable"]` | — |
| `candidate_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |

不接受未声明字段。

<a id="schema-reviewrecoverypolicy"></a>

### ReviewRecoveryPolicy

[JSON Schema](schemas.json#/$defs/ReviewRecoveryPolicy) · [OpenAPI schema](openapi.json#/components/schemas/ReviewRecoveryPolicy)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `automatic_reclaims` | 是 | `integer` | ≥ `0` | — |
| `total_elapsed_seconds` | 是 | `integer` | ≥ `0` | — |
| `backoff_seconds` | 是 | array&lt;`integer`&gt; | — | — |

不接受未声明字段。

<a id="schema-rolebindingresult"></a>

### RoleBindingResult

[JSON Schema](schemas.json#/$defs/RoleBindingResult) · [OpenAPI schema](openapi.json#/components/schemas/RoleBindingResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `principal_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `version` | 是 | `integer` | > `0` | — |
| `grant_epoch` | 是 | `integer` | ≥ `0` | — |
| `root_epoch` | 是 | `integer` | ≥ `0` | — |
| `connection_alias` | 是 | `string` | 最短 `1` | — |
| `credential_source_ref` | 是 | `string` | 最短 `1` | — |
| `enabled` | 是 | `boolean` | — | — |

不接受未声明字段。

<a id="schema-rolebindingupdate"></a>

### RoleBindingUpdate

[JSON Schema](schemas.json#/$defs/RoleBindingUpdate) · [OpenAPI schema](openapi.json#/components/schemas/RoleBindingUpdate)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `expected_version` | 是 | `integer` | ≥ `0` | — |
| `enabled` | 是 | `boolean` | — | — |
| `root_ref` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |

不接受未声明字段。

<a id="schema-routingexplanation"></a>

### RoutingExplanation

[JSON Schema](schemas.json#/$defs/RoutingExplanation) · [OpenAPI schema](openapi.json#/components/schemas/RoutingExplanation)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `mode` | 是 | `string` | 枚举 `["random","capability"]` | — |
| `reason` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `policy_version` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |

不接受未声明字段。

<a id="schema-savecatalogresult"></a>

### SaveCatalogResult

[JSON Schema](schemas.json#/$defs/SaveCatalogResult) · [OpenAPI schema](openapi.json#/components/schemas/SaveCatalogResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `kind` | 是 | `string` | 枚举 `["native-template","tool","mcp","recovery-policy"]` | — |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `version` | 是 | `integer` | > `0` | — |
| `content_sha256` | 是 | `string` | 正则 `"^[0-9a-f]{64}$"` | — |
| `readiness` | 是 | [Readiness](#schema-readiness) | — | — |

不接受未声明字段。

<a id="schema-saveprojectresult"></a>

### SaveProjectResult

[JSON Schema](schemas.json#/$defs/SaveProjectResult) · [OpenAPI schema](openapi.json#/components/schemas/SaveProjectResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `resource_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `version` | 是 | `integer` | > `0` | — |
| `impact` | 是 | [ProjectImpact](#schema-projectimpact) | — | — |

不接受未声明字段。

<a id="schema-saveworkerresult"></a>

### SaveWorkerResult

[JSON Schema](schemas.json#/$defs/SaveWorkerResult) · [OpenAPI schema](openapi.json#/components/schemas/SaveWorkerResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `config_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `slot_version` | 是 | `integer` | > `0` | — |
| `affected_tasks` | 是 | array&lt;`string`&gt; | — | — |
| `attention` | 是 | array&lt;[Attention](#schema-attention)&gt; | — | — |

不接受未声明字段。

<a id="schema-serviceobservation"></a>

### ServiceObservation

[JSON Schema](schemas.json#/$defs/ServiceObservation) · [OpenAPI schema](openapi.json#/components/schemas/ServiceObservation)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `state` | 是 | `string` | 枚举 `["ready","maintenance","degraded"]` | — |
| `dispatch_paused` | 是 | `boolean` | — | — |

不接受未声明字段。

<a id="schema-sessioncreate"></a>

### SessionCreate

[JSON Schema](schemas.json#/$defs/SessionCreate) · [OpenAPI schema](openapi.json#/components/schemas/SessionCreate)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `credential` | 是 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-sessionidentity"></a>

### SessionIdentity

[JSON Schema](schemas.json#/$defs/SessionIdentity) · [OpenAPI schema](openapi.json#/components/schemas/SessionIdentity)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `principal_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `expires_at` | 是 | `string` | 格式 `"date-time"` | — |

不接受未声明字段。

<a id="schema-sessionreply"></a>

### SessionReply

[JSON Schema](schemas.json#/$defs/SessionReply) · [OpenAPI schema](openapi.json#/components/schemas/SessionReply)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `session` | 是 | [SessionIdentity](#schema-sessionidentity) | — | — |
| `csrf_token` | 是 | `string` | 最短 `1` | — |
| `meta` | 是 | [Meta](#schema-meta) | — | — |

不接受未声明字段。

<a id="schema-sharedresourcedefinition"></a>

### SharedResourceDefinition

[JSON Schema](schemas.json#/$defs/SharedResourceDefinition) · [OpenAPI schema](openapi.json#/components/schemas/SharedResourceDefinition)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `resource_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `scope` | 是 | `string` | 枚举 `["instance","project","external"]` | — |
| `kind` | 是 | `string` | 枚举 `["file","port","database","service","cache"]` | — |
| `canonical_identity` | 是 | `string` | 最短 `1` | — |
| `isolation_mode` | 是 | `string` | 枚举 `["namespace","exclusive","shared_read"]` | — |
| `namespace_rule` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |

不接受未声明字段。

<a id="schema-stdiomcpdefinition"></a>

### StdioMCPDefinition

[JSON Schema](schemas.json#/$defs/StdioMCPDefinition) · [OpenAPI schema](openapi.json#/components/schemas/StdioMCPDefinition)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `transport` | 是 | `string` | 固定值 `"stdio"` | — |
| `executable` | 是 | [ExecutableDefinition](#schema-executabledefinition) | — | — |
| `args` | 是 | array&lt;`string`&gt; | — | — |
| `environment_refs` | 是 | array&lt;[EnvironmentCredentialRef](#schema-environmentcredentialref)&gt; | — | — |
| `tool_refs` | 是 | array&lt;[FixedRef](#schema-fixedref)&gt; | — | — |
| `description` | 是 | `string` | 最短 `1`；最长 `16384` | — |

不接受未声明字段。

<a id="schema-submitreviewresult"></a>

### SubmitReviewResult

[JSON Schema](schemas.json#/$defs/SubmitReviewResult) · [OpenAPI schema](openapi.json#/components/schemas/SubmitReviewResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `review_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `candidate_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `verdict` | 是 | `string` | 枚举 `["PASS","REJECT"]` | — |
| `task_status` | 是 | `string` | 枚举 `["queued","running","reviewing","finished","canceled"]` | — |
| `outcome` | 是 | `string` 或 `null` | `string`: 枚举 `["passed","review_failed"]`；`null`: — | — |
| `rejections` | 是 | `integer` | ≥ `0`；≤ `3` | — |
| `committed_task_version` | 是 | `integer` | ≥ `0` | — |

不接受未声明字段。

<a id="schema-submittaskrequest"></a>

### SubmitTaskRequest

[JSON Schema](schemas.json#/$defs/SubmitTaskRequest) · [OpenAPI schema](openapi.json#/components/schemas/SubmitTaskRequest)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `spec` | 是 | [TaskSpecInput](#schema-taskspecinput) | — | — |

不接受未声明字段。

<a id="schema-submittaskresult"></a>

### SubmitTaskResult

[JSON Schema](schemas.json#/$defs/SubmitTaskResult) · [OpenAPI schema](openapi.json#/components/schemas/SubmitTaskResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `task_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |

不接受未声明字段。

<a id="schema-taskdetail"></a>

### TaskDetail

[JSON Schema](schemas.json#/$defs/TaskDetail) · [OpenAPI schema](openapi.json#/components/schemas/TaskDetail)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `summary` | 是 | [TaskSummary](#schema-tasksummary) | — | — |
| `spec` | 是 | [TaskSpec](#schema-taskspec) | — | — |
| `resolved_inputs` | 是 | [ResolvedInputsView](#schema-resolvedinputsview) 或 `null` | `null`: — | — |
| `assignment` | 是 | [Assignment](#schema-assignment) 或 `null` | `null`: — | — |
| `resource_override` | 是 | [ResourceOverrideView](#schema-resourceoverrideview) | — | — |
| `current_candidate` | 是 | [CandidateView](#schema-candidateview) 或 `null` | `null`: — | — |
| `execution_history_ref` | 是 | [ArtifactRef](#schema-artifactref) 或 `null` | `null`: — | — |
| `artifacts` | 是 | array&lt;[ArtifactRef](#schema-artifactref)&gt; | — | — |
| `related_tasks` | 是 | array&lt;`string`&gt; | — | — |
| `meta` | 是 | [Meta](#schema-meta) | — | — |

不接受未声明字段。

<a id="schema-tasklistquery"></a>

### TaskListQuery

[JSON Schema](schemas.json#/$defs/TaskListQuery) · [OpenAPI schema](openapi.json#/components/schemas/TaskListQuery)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `cursor` | 否 | `string` | 最短 `1` | — |
| `limit` | 否 | `integer` | ≥ `1`；≤ `100`；缺省 `20` | — |
| `status` | 否 | `string` | 枚举 `["queued","running","reviewing","finished","canceled"]` | — |
| `outcome` | 否 | `string` | 枚举 `["passed","review_failed"]` | — |
| `model_id` | 否 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `difficulty_level` | 否 | `integer` | — | — |

不接受未声明字段。

<a id="schema-taskpage"></a>

### TaskPage

[JSON Schema](schemas.json#/$defs/TaskPage) · [OpenAPI schema](openapi.json#/components/schemas/TaskPage)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `items` | 是 | array&lt;[TaskSummary](#schema-tasksummary)&gt; | 最多项 `100` | — |
| `next_cursor` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |
| `meta` | 是 | [Meta](#schema-meta) | — | — |

不接受未声明字段。

<a id="schema-taskscope"></a>

### TaskScope

[JSON Schema](schemas.json#/$defs/TaskScope) · [OpenAPI schema](openapi.json#/components/schemas/TaskScope)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `include` | 是 | array&lt;`string`&gt; | — | — |
| `exclude` | 是 | array&lt;`string`&gt; | — | — |

不接受未声明字段。

<a id="schema-taskspec"></a>

### TaskSpec

[JSON Schema](schemas.json#/$defs/TaskSpec) · [OpenAPI schema](openapi.json#/components/schemas/TaskSpec)

Effective immutable TaskSpec: defaults were resolved by the submit service.

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `schema_version` | 是 | `string` | 固定值 `"1"` | — |
| `kind` | 是 | `string` | 枚举 `["code","report"]` | — |
| `title` | 是 | `string` | 最短 `1`；最长 `512` | — |
| `goal` | 是 | `string` | 最短 `1`；最长 `131072` | — |
| `scope` | 是 | [TaskScope](#schema-taskscope) | — | — |
| `difficulty` | 是 | [Difficulty](#schema-difficulty) | — | — |
| `inputs` | 是 | array&lt;[GitInput](#schema-gitinput) 或 [FileInput](#schema-fileinput) 或 [ArtifactInput](#schema-artifactinput)&gt; | 最多项 `128` | — |
| `acceptance` | 是 | array&lt;[Criterion](#schema-criterion)&gt; | 最少项 `1`；最多项 `64` | — |
| `deliverables` | 是 | array&lt;[Deliverable](#schema-deliverable)&gt; | 最少项 `1` | — |
| `requirements` | 是 | [Requirements](#schema-requirements) | — | — |
| `recovery_policy_ref` | 是 | [FixedRef](#schema-fixedref) | — | — |
| `dependencies` | 是 | array&lt;[Dependency](#schema-dependency)&gt; | 最多项 `0` | — |
| `related_task_id` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |
| `project_config_ref` | 是 | [FixedRef](#schema-fixedref) | — | — |

不接受未声明字段。

<a id="schema-taskspecinput"></a>

### TaskSpecInput

[JSON Schema](schemas.json#/$defs/TaskSpecInput) · [OpenAPI schema](openapi.json#/components/schemas/TaskSpecInput)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `schema_version` | 是 | `string` | 固定值 `"1"` | — |
| `kind` | 是 | `string` | 枚举 `["code","report"]` | — |
| `title` | 是 | `string` | 最短 `1`；最长 `512` | — |
| `goal` | 是 | `string` | 最短 `1`；最长 `131072` | — |
| `scope` | 是 | [TaskScope](#schema-taskscope) | — | — |
| `difficulty` | 是 | [Difficulty](#schema-difficulty) | — | — |
| `inputs` | 是 | array&lt;[GitInput](#schema-gitinput) 或 [FileInput](#schema-fileinput) 或 [ArtifactInput](#schema-artifactinput)&gt; | 最多项 `128` | — |
| `acceptance` | 是 | array&lt;[Criterion](#schema-criterion)&gt; | 最少项 `1`；最多项 `64` | — |
| `deliverables` | 是 | array&lt;[Deliverable](#schema-deliverable)&gt; | 最少项 `1` | — |
| `requirements` | 否 | [Requirements](#schema-requirements) | — | — |
| `recovery_policy_ref` | 否 | [FixedRef](#schema-fixedref) | — | — |
| `dependencies` | 否 | array&lt;[Dependency](#schema-dependency)&gt; | 最多项 `0` | V0 supports independent tasks. |
| `related_task_id` | 否 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: —；缺省 `null` | — |

不接受未声明字段。

<a id="schema-tasksummary"></a>

### TaskSummary

[JSON Schema](schemas.json#/$defs/TaskSummary) · [OpenAPI schema](openapi.json#/components/schemas/TaskSummary)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `task_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `title` | 是 | `string` | 最短 `1`；最长 `512` | — |
| `kind` | 是 | `string` | 枚举 `["code","report"]` | — |
| `status` | 是 | `string` | 枚举 `["queued","running","reviewing","finished","canceled"]` | — |
| `outcome` | 是 | `string` 或 `null` | `string`: 枚举 `["passed","review_failed"]`；`null`: — | — |
| `version` | 是 | `integer` | ≥ `0` | — |
| `difficulty` | 是 | [DifficultySummary](#schema-difficultysummary) | — | — |
| `review_rejections` | 是 | `integer` | ≥ `0`；≤ `3` | — |
| `assignment` | 是 | [AssignmentSummary](#schema-assignmentsummary) 或 `null` | `null`: — | — |
| `execution` | 是 | [ExecutionObservation](#schema-executionobservation) | — | — |
| `review` | 是 | [ReviewObservation](#schema-reviewobservation) | — | — |
| `attention` | 是 | array&lt;[Attention](#schema-attention)&gt; | — | — |
| `actions` | 是 | array&lt;[Action](#schema-action)&gt; | — | — |
| `created_at` | 是 | `string` | 格式 `"date-time"` | — |
| `updated_at` | 是 | `string` | 格式 `"date-time"` | — |

不接受未声明字段。

<a id="schema-tooldefinition"></a>

### ToolDefinition

[JSON Schema](schemas.json#/$defs/ToolDefinition) · [OpenAPI schema](openapi.json#/components/schemas/ToolDefinition)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `source_root_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `members` | 是 | array&lt;[CatalogMember](#schema-catalogmember)&gt; | 最少项 `1`；最多项 `128` | — |
| `description` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `entrypoint` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |

不接受未声明字段。

<a id="schema-unfinishedcounts"></a>

### UnfinishedCounts

[JSON Schema](schemas.json#/$defs/UnfinishedCounts) · [OpenAPI schema](openapi.json#/components/schemas/UnfinishedCounts)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `queued` | 是 | `integer` | ≥ `0` | — |
| `running` | 是 | `integer` | ≥ `0` | — |
| `reviewing` | 是 | `integer` | ≥ `0` | — |
| `interrupted` | 是 | `integer` | ≥ `0` | Observation subset, not a fourth additive task phase. |

不接受未声明字段。

<a id="schema-uploadreviewevidenceresult"></a>

### UploadReviewEvidenceResult

[JSON Schema](schemas.json#/$defs/UploadReviewEvidenceResult) · [OpenAPI schema](openapi.json#/components/schemas/UploadReviewEvidenceResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `artifact` | 是 | [ArtifactRef](#schema-artifactref) | — | — |
| `activity_ref` | 是 | `string` 或 `null` | `string`: 最短 `1`；`null`: — | — |

不接受未声明字段。

<a id="schema-workerartifact"></a>

### WorkerArtifact

[JSON Schema](schemas.json#/$defs/WorkerArtifact) · [OpenAPI schema](openapi.json#/components/schemas/WorkerArtifact)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `name` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `relative_path` | 是 | `string` | 最短 `1` | — |
| `kind` | 是 | `string` | 最短 `1` | — |
| `media_type` | 是 | `string` | 最短 `1` | — |

不接受未声明字段。

<a id="schema-workercheck"></a>

### WorkerCheck

[JSON Schema](schemas.json#/$defs/WorkerCheck) · [OpenAPI schema](openapi.json#/components/schemas/WorkerCheck)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `name` | 是 | `string` | 最短 `1` | — |
| `status` | 是 | `string` | 枚举 `["passed","failed","not_run"]` | — |
| `evidence_names` | 是 | array&lt;`string`&gt; | — | — |

不接受未声明字段。

<a id="schema-workercheckrequest"></a>

### WorkerCheckRequest

[JSON Schema](schemas.json#/$defs/WorkerCheckRequest) · [OpenAPI schema](openapi.json#/components/schemas/WorkerCheckRequest)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `config_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `kind` | 是 | `string` | 固定值 `"static"` | — |

不接受未声明字段。

<a id="schema-workercheckresult"></a>

### WorkerCheckResult

[JSON Schema](schemas.json#/$defs/WorkerCheckResult) · [OpenAPI schema](openapi.json#/components/schemas/WorkerCheckResult)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `config_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `checked_at` | 是 | `string` | 格式 `"date-time"` | — |
| `checks` | 是 | array&lt;[CheckResult](#schema-checkresult)&gt; | — | — |

不接受未声明字段。

<a id="schema-workerdelivery"></a>

### WorkerDelivery

[JSON Schema](schemas.json#/$defs/WorkerDelivery) · [OpenAPI schema](openapi.json#/components/schemas/WorkerDelivery)

| 值 | 类型/分支 | 约束 |
| --- | --- | --- |
| 根值 | [CodeWorkerDelivery](#schema-codeworkerdelivery) 或 [ReportWorkerDelivery](#schema-reportworkerdelivery) | 分支字段 `kind` |

<a id="schema-workerdeliverybase"></a>

### WorkerDeliveryBase

[JSON Schema](schemas.json#/$defs/WorkerDeliveryBase) · [OpenAPI schema](openapi.json#/components/schemas/WorkerDeliveryBase)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `schema_version` | 是 | `string` | 固定值 `"worker-delivery/1"` | — |
| `summary` | 是 | `string` | 最短 `1`；最长 `16384` | — |
| `artifacts` | 是 | array&lt;[WorkerArtifact](#schema-workerartifact)&gt; | 最多项 `128` | — |
| `checks` | 是 | array&lt;[WorkerCheck](#schema-workercheck)&gt; | — | — |
| `known_limitations` | 是 | array&lt;`string`&gt; | — | — |

不接受未声明字段。

<a id="schema-workerpoolobservation"></a>

### WorkerPoolObservation

[JSON Schema](schemas.json#/$defs/WorkerPoolObservation) · [OpenAPI schema](openapi.json#/components/schemas/WorkerPoolObservation)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `configured` | 是 | `boolean` | — | — |
| `eligible` | 是 | `integer` | ≥ `0` | — |
| `busy` | 是 | `integer` | ≥ `0` | — |

不接受未声明字段。

<a id="schema-workerupdate"></a>

### WorkerUpdate

[JSON Schema](schemas.json#/$defs/WorkerUpdate) · [OpenAPI schema](openapi.json#/components/schemas/WorkerUpdate)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `expected_version` | 是 | `integer` | ≥ `0` | — |
| `admission_mode` | 是 | `string` | 枚举 `["enabled","draining","disabled"]` | — |
| `retire_requested` | 是 | `boolean` | — | — |
| `configuration` | 是 | [ExecutionConfiguration](#schema-executionconfiguration) | — | — |

不接受未声明字段。

<a id="schema-workerview"></a>

### WorkerView

[JSON Schema](schemas.json#/$defs/WorkerView) · [OpenAPI schema](openapi.json#/components/schemas/WorkerView)

| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `admission_mode` | 是 | `string` | 枚举 `["enabled","draining","disabled"]` | — |
| `retire_requested` | 是 | `boolean` | — | — |
| `retired` | 是 | `boolean` | — | — |
| `configuration` | 是 | [ExecutionConfiguration](#schema-executionconfiguration) | — | — |
| `slot_version` | 是 | `integer` | > `0` | — |
| `config_id` | 是 | `string` | 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128` | — |
| `effective_config_observation` | 是 | `object` | 额外字段 `{"$ref":"#/$defs/JsonValue"}` | — |
| `occupied_by` | 是 | `string` 或 `null` | `string`: 正则 `"^[A-Za-z0-9][A-Za-z0-9._-]*$"`；最短 `1`；最长 `128`；`null`: — | — |
| `bound_unfinished_tasks` | 是 | array&lt;`string`&gt; | — | — |
| `readiness` | 是 | [Readiness](#schema-readiness) | — | — |

不接受未声明字段。
