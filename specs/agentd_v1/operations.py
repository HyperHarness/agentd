"""Proposed V0 transport contract; no production handlers or service imports.

The registry is the source for generated OpenAPI and the readable API index.
Role, epoch, ownership and state checks are semantic requirements, not claims
that schema validation provides authorization or implements these operations.
"""

from dataclasses import dataclass

from pydantic import TypeAdapter

from .models import Id


ID_SCHEMA = TypeAdapter(Id).json_schema(mode="validation")
PROTOCOL_DOC = "docs/design/INTERFACE_GUIDE.md#http-contract"
REVIEW_DOC = "docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-materials"
LEASE_DOC = "docs/design/TASK_AND_REVIEW_PROTOCOL.md#review-leases"
RECOVERY_DOC = "docs/design/RELIABILITY_AND_STORAGE.md#recovery-actions"
RESOURCE_DOC = "docs/design/RUNTIME_LIFECYCLE.md#resource-adjustments"
RETENTION_DOC = "docs/design/RELIABILITY_AND_STORAGE.md#artifact-retention"
INPUT_DOC = "docs/design/TASK_AND_REVIEW_PROTOCOL.md#input-freeze"
STATS_DOC = "docs/design/TASK_AND_REVIEW_PROTOCOL.md#model-statistics"

ERROR_STATUS = {
    "JSON_INVALID": 400, "NOT_AUTHENTICATED": 401, "NOT_AUTHORIZED": 403, "NOT_FOUND": 404,
    "KEY_REUSE": 409, "VERSION_CONFLICT": 409, "STALE_ACTION": 409, "CURSOR_INVALID": 409,
    "STORE_RESTORED": 409, "TASK_TERMINAL": 409, "REVIEW_LEASE_EXPIRED": 409,
    "REVIEW_BINDING_CONFLICT": 409, "CANDIDATE_BUSY": 409, "ARTIFACT_UNAVAILABLE": 409,
    "ARTIFACT_CORRUPT": 409, "WORKER_RETIRED": 409,
    "ARTIFACT_EXPIRED": 410, "REQUEST_TOO_LARGE": 413, "UNSUPPORTED_MEDIA_TYPE": 415,
    "INPUT_INVALID": 422, "PROJECT_NOT_READY": 422, "FEATURE_UNSUPPORTED": 422,
    "CONTENT_HASH_MISMATCH": 422, "RESOURCE_INVALID": 422,
    "CAPACITY_LIMIT": 429, "INTERNAL_ERROR": 500, "SERVICE_MAINTENANCE": 503, "CLIENT_UNAVAILABLE": 503,
}
READ_ERRORS = ("NOT_AUTHENTICATED", "NOT_AUTHORIZED", "NOT_FOUND", "INPUT_INVALID", "INTERNAL_ERROR",
               "SERVICE_MAINTENANCE", "CLIENT_UNAVAILABLE")
WRITE_ERRORS = READ_ERRORS + ("JSON_INVALID", "KEY_REUSE", "STORE_RESTORED", "REQUEST_TOO_LARGE",
                             "UNSUPPORTED_MEDIA_TYPE", "CAPACITY_LIMIT")


def error_cases(*codes: str) -> tuple[tuple[int, tuple[str, ...]], ...]:
    grouped: dict[int, set[str]] = {}
    for code in codes:
        grouped.setdefault(ERROR_STATUS[code], set()).add(code)
    return tuple((status, tuple(sorted(values))) for status, values in sorted(grouped.items()))


@dataclass(frozen=True)
class Parameter:
    name: str
    schema: dict
    description: str


def identifier(name: str = "id") -> Parameter:
    return Parameter(name, dict(ID_SCHEMA), "对象标识；仍须按当前身份与项目范围校验归属。")


@dataclass(frozen=True)
class Operation:
    id: str
    operation_id: str
    method: str
    path: str
    summary: str
    roles: tuple[str, ...]
    scope: str
    request_model: str | None = None
    response_model: str | None = "CommandReply"
    query_model: str | None = None
    path_parameters: tuple[Parameter, ...] = ()
    success_statuses: tuple[int, ...] = (200,)
    errors: tuple[tuple[int, tuple[str, ...]], ...] = ()
    # True means the explicit request-key replay protocol is required. False
    # does not deny the natural idempotence of reads or session deletion.
    idempotent: bool = False
    store_epoch: bool = False
    mcp: str | None = None
    cli: str | None = None
    semantics: str = ""
    docs: tuple[str, ...] = (PROTOCOL_DOC,)
    auth: str = "role_or_session"


def business(id: str, operation_id: str, method: str, path: str, summary: str, *,
             roles: tuple[str, ...] = ("lead", "admin"), scope: str = "project", extra_errors: tuple[str, ...] = (),
             **kwargs) -> Operation:
    write = method != "GET"
    return Operation(id, operation_id, method, path, summary, roles, scope,
                     errors=error_cases(*(WRITE_ERRORS if write else READ_ERRORS), *extra_errors),
                     idempotent=write, store_epoch=write, **kwargs)


def management(id: str, operation_id: str, path: str, summary: str, request_model: str, *,
               method: str = "PUT", scope: str = "instance", compare_version: bool = True,
               extra_errors: tuple[str, ...] = (), **kwargs) -> Operation:
    return Operation(id, operation_id, method, path, summary, ("admin",), scope,
                     request_model=request_model,
                     errors=error_cases(*WRITE_ERRORS, *(("VERSION_CONFLICT",) if compare_version else ()), *extra_errors),
                     idempotent=True, store_epoch=True, auth="session", **kwargs)


OPERATIONS = (
    business("B01", "submit_task", "POST", "/v1/tasks", "提交不可变任务合同", request_model="SubmitTaskRequest",
             success_statuses=(201,), mcp="submit_task", cli="agentd task submit --file task.json",
             extra_errors=("PROJECT_NOT_READY", "FEATURE_UNSUPPORTED"), docs=(PROTOCOL_DOC, INPUT_DOC),
             semantics="原子保存 TaskSpec、queued 与幂等回执；执行异步。核已配置量表及等级，未知/越界为422 INPUT_INVALID。"
             "worker忙碌或依赖未就绪仍可创建排队任务；不接收模型/worker选择。"),
    business("B02", "get_task", "GET", "/v1/tasks/{id}", "读取任务详情与可用动作", response_model="TaskDetail",
             path_parameters=(identifier(),), mcp="get_task", cli="agentd task get ID",
             semantics="返回当前投影与完整合同；reviewer没有通用任务查询权限；读取不启动模型或恢复任务。"),
    business("B03", "list_tasks", "GET", "/v1/tasks", "分页列出任务", response_model="TaskPage",
             query_model="TaskListQuery", mcp="list_tasks", cli="agentd task list", extra_errors=("CURSOR_INVALID",),
             semantics="游标绑定身份、项目、过滤、排序及store_epoch；多页不承诺冻结状态，不接受未知查询参数。"),
    business("B04", "resume_task", "POST", "/v1/tasks/{id}/resume", "按当前恢复动作继续任务",
             request_model="ResumeTaskRequest", path_parameters=(identifier(),), success_statuses=(200, 202),
             mcp="resume_task", cli="agentd task resume ID", extra_errors=("STALE_ACTION", "TASK_TERMINAL"),
             docs=(PROTOCOL_DOC, RECOVERY_DOC),
             semantics="action_ref固定待处理问题与版本；处置记录不能伪造进程闭合。条件不足保留waiting；不改模型、不清审核或恢复历史。"),
    business("B05", "cancel_task", "POST", "/v1/tasks/{id}/cancel", "登记取消并核对停止",
             request_model="CancelTaskRequest", path_parameters=(identifier(),), success_statuses=(200, 202),
             mcp="cancel_task", cli="agentd task cancel ID", extra_errors=("TASK_TERMINAL",),
             semantics="取消与终态按事务顺序裁决；停止及租约撤销确认后才canceled。新key重复取消只找回原取消operation。"),
    business("B06", "next_review", "POST", "/v1/reviews/next", "领取或找回一项审核", roles=("reviewer",),
             request_model="NextReviewRequest", response_model="ReviewClaim", mcp="next_review", cli="agentd review next",
             extra_errors=("REVIEW_LEASE_EXPIRED", "REVIEW_BINDING_CONFLICT", "CANDIDATE_BUSY"), docs=(PROTOCOL_DOC, REVIEW_DOC),
             semantics="每身份至多一项有效领取；empty也记幂等结果。preferred仅重领本身份历史候选，不改领另一项；过期旧key不生成新租约。"),
    business("B07", "submit_review", "POST", "/v1/reviews/submit", "提交独立审核判决", roles=("reviewer",),
             request_model="ReviewDecision", mcp="submit_review", cli="agentd review submit --file verdict.json",
             extra_errors=("REVIEW_LEASE_EXPIRED", "REVIEW_BINDING_CONFLICT", "ARTIFACT_UNAVAILABLE", "ARTIFACT_CORRUPT"),
             docs=(PROTOCOL_DOC, REVIEW_DOC),
             semantics="复核授权、候选、有效租约、证据完整性及取消；判决/计数/终态/outbox原子提交。已提交同key先返回原判决，不因完成关闭的租约拒绝重放。"),
    business("B08", "defer_review", "POST", "/v1/reviews/defer", "暂缓无法判断的审核", roles=("reviewer",),
             request_model="DeferReview", mcp="defer_review", cli="agentd review defer",
             extra_errors=("REVIEW_LEASE_EXPIRED", "REVIEW_BINDING_CONFLICT"), docs=(PROTOCOL_DOC, REVIEW_DOC),
             semantics="释放本次领取、保留候选，进入有界延后或暂停；不产生REJECT，不允许立即无限重领故障候选。"),
    business("B09", "get_inbox", "GET", "/v1/inbox", "读取角色事项与事件", roles=("lead", "reviewer"),
             response_model="InboxPage", query_model="InboxQuery", mcp="get_inbox", cli="agentd inbox",
             extra_errors=("CURSOR_INVALID",), semantics="事件与当前attention分别分页；读取不领取、不解决attention。"),
    business("B10", "get_context", "GET", "/v1/context", "被动读取连接上下文", roles=("lead", "reviewer"),
             response_model="Context", mcp="get_context", cli="agentd context",
             semantics="返回绑定项目/角色、支持能力、量表和limits；首次调用不要求预先知道store_epoch；不执行探针。"),
    business("B11", "get_model_stats", "GET", "/v1/model-stats", "读取模型与难度统计", response_model="ModelStatsPage",
             query_model="ModelStatsQuery", mcp="get_model_stats", cli="agentd model stats", extra_errors=("CURSOR_INVALID",),
             docs=(PROTOCOL_DOC, STATS_DOC),
             semantics="缺失usage为null，展示覆盖率和原生字段重叠口径，不直接相加为总tokens；"
             "查询不能更新路由策略，未结束与取消不得从观察口径消失。"),
    business("B12", "read_artifact", "GET", "/v1/artifacts/{id}", "读取授权成果的原始字节块",
             roles=("lead", "reviewer", "admin"), response_model="ArtifactChunk", query_model="ArtifactReadQuery",
             path_parameters=(identifier(),), mcp="read_artifact", cli="agentd artifact read REF",
             extra_errors=("ARTIFACT_UNAVAILABLE", "ARTIFACT_CORRUPT", "ARTIFACT_EXPIRED"), docs=(PROTOCOL_DOC, REVIEW_DOC),
             semantics="对象归属及当前授权必查；offset等于size返回EOF空块，大于size为422。GET不续租；activity_ref只证明该次读取。"),
    business("B13", "get_request_result", "GET", "/v1/requests/{request_key}", "按原请求键核对结果",
             roles=("lead", "reviewer", "admin"), scope="project_or_instance",
             path_parameters=(identifier("request_key"),), mcp="get_request_result", cli="agentd request get KEY",
             semantics="仅当前稳定principal与解析scope；不接受principal参数。404不证明原请求不在途，只可同key同内容重试。"),
    business("B14", "get_operation", "GET", "/v1/operations/{id}", "读取持久操作的当前进度",
             roles=("lead", "reviewer", "admin"), scope="project_or_instance", path_parameters=(identifier(),),
             mcp="get_operation", cli="agentd operation get ID",
             semantics="reviewer仅自己的操作及允许回执；管理身份按授权范围读取，不因此获得独审写权限。"),
    business("B15", "upload_review_evidence", "POST", "/v1/reviews/evidence", "保存reviewer自产证据",
             roles=("reviewer",), request_model="EvidenceUpload", response_model="EvidenceReply", success_statuses=(201,),
             mcp="upload_review_evidence", cli="agentd review evidence --handle HANDLE --file FILE",
             extra_errors=("REVIEW_LEASE_EXPIRED", "REVIEW_BINDING_CONFLICT", "CONTENT_HASH_MISMATCH"), docs=(PROTOCOL_DOC, REVIEW_DOC),
             semantics="只接收有界原始字节base64，不按宿主路径读文件；记录候选/principal归属，先发布后登记，不改worker候选。manifest校验所有段并传递保留pin。"),
    business("B16", "renew_review", "POST", "/v1/reviews/renew", "连接层有界续租", roles=("reviewer",),
             request_model="RenewReviewRequest", extra_errors=("REVIEW_LEASE_EXPIRED", "REVIEW_BINDING_CONFLICT"),
             docs=(PROTOCOL_DOC, LEASE_DOC),
             semantics="仅适配器使用，不是模型工具；消费新鲜且一次性的activity_ref；重放不再延长，不能超过总期限或复活过期handle。"),
    Operation("M01", "create_session", "POST", "/v1/session", "建立Dashboard管理会话", ("bootstrap",), "instance",
              request_model="SessionCreate", response_model="SessionReply", auth="public",
              errors=error_cases("JSON_INVALID", "NOT_AUTHENTICATED", "NOT_AUTHORIZED", "REQUEST_TOO_LARGE",
                                 "UNSUPPORTED_MEDIA_TYPE", "INPUT_INVALID", "CAPACITY_LIMIT", "INTERNAL_ERROR"),
              semantics="验证本地bootstrap/管理凭据与Origin后建立有限会话；凭据不回显、不写日志。Set-Cookie使用HttpOnly/SameSite，响应no-store。"),
    Operation("M02", "delete_session", "DELETE", "/v1/session", "退出Dashboard管理会话", ("admin",), "instance",
              response_model=None, success_statuses=(204,), auth="logout",
              errors=error_cases("NOT_AUTHORIZED", "INTERNAL_ERROR"),
              semantics="有效cookie撤销须CSRF和Origin；失效/不存在cookie仅清除浏览器cookie且不要求重新登录。重复退出无业务副作用。"),
    Operation("M03", "get_health", "GET", "/v1/health", "读取最小存活状态", (), "public",
              response_model="HealthReply", auth="public", errors=error_cases("INTERNAL_ERROR", "CLIENT_UNAVAILABLE"),
              semantics="公开最小alive/version；不泄露配置、不做原生探针，不能代表执行/审核已就绪。"),
    Operation("M04", "get_admin_snapshot", "GET", "/v1/admin/snapshot", "读取管理快照", ("admin",), "instance",
              response_model="AdminSnapshot", auth="session", errors=error_cases(*READ_ERRORS),
              semantics="一次短读事务给有界快照及当前CSRF token；Cache-Control:no-store，不返回凭据值或主动探针。"),
    management("M05", "save_project", "/v1/admin/projects/{id}", "登记项目与固定默认配置", "ProjectUpdate",
               scope="project_path", path_parameters=(identifier(),), success_statuses=(200, 201),
               extra_errors=("FEATURE_UNSUPPORTED",),
               semantics="管理员登记仓库/输入根；允许接线未完但标不可用。冻结任务不追随默认值变更；V0第二活动项目拒绝。"),
    management("M06", "save_credential_source", "/v1/admin/credential-sources/{id}", "登记或轮换私有凭据来源",
               "CredentialSourceUpdate", path_parameters=(identifier(),), success_statuses=(200, 201),
               semantics="秘密写私有存储，回执只含公开来源状态；secret请求摘要用不可导出HMAC，不把秘密正文记入operation。"),
    management("M07", "save_worker", "/v1/admin/workers/{id}", "保存固定worker配置及准入", "WorkerUpdate",
               path_parameters=(identifier(),), success_statuses=(200, 201), extra_errors=("WORKER_RETIRED", "RESOURCE_INVALID"),
               docs=(PROTOCOL_DOC, RESOURCE_DOC),
               semantics="执行内容变化追加config；启停仅CAS槽版本。绑定任务不热换模型；retire排空后生效，保存不调用模型。"),
    management("M08", "set_dispatch", "/v1/admin/dispatch", "设置用户派发暂停", "DispatchUpdate", scope="body_scope",
               semantics="只改变用户pause，不清维护/资源hold，不停止已有worker；body中的instance/project范围逐次授权。"),
    management("M09", "set_role_binding", "/v1/admin/projects/{id}/role-bindings/{role}", "接线或撤销角色根", "RoleBindingUpdate",
               scope="project_path", success_statuses=(200, 201),
               path_parameters=(identifier(), Parameter("role", {"type": "string", "enum": ["lead", "reviewer"]}, "固定业务角色。")),
               semantics="两个根不得相同；凭据写私有连接文件仅返回引用。重绑/撤销使旧epoch和租约失效；重复同值不重复签发。"),
    management("M10", "check_worker", "/v1/admin/workers/{id}/checks", "静态检查worker配置", "WorkerCheckRequest",
               method="POST", compare_version=False, path_parameters=(identifier(),), success_statuses=(200, 202),
               semantics="V0只接受static，核语法/路径/可读性/匹配；不运行原生CLI、MCP server或模型。accepted以操作查询观察。"),
    management("M11", "save_catalog", "/v1/admin/catalog/{kind}/{id}", "保存固定配置目录版本", "CatalogUpdate",
               scope="project_header", success_statuses=(200, 201),
               path_parameters=(Parameter("kind", {"type": "string", "enum": ["native-template", "tool", "mcp", "recovery-policy"]},
                                          "目录种类须与definition的固定类型一致；不是任意插件。"), identifier()),
               semantics="唯一catalog路由，按kind验证definition分支；须项目头。验证字节摘要后保存版本；不执行工具/server，旧引用保留。"),
    management("M12", "set_task_resources", "/v1/admin/tasks/{id}/resource-override", "为下一次执行设置任务资源", "ResourceOverrideUpdate",
               scope="object_project", path_parameters=(identifier(),), success_statuses=(200, 201),
               extra_errors=("RESOURCE_INVALID", "TASK_TERMINAL"), docs=(PROTOCOL_DOC, RESOURCE_DOC),
               semantics="仅非终态；完整资源向量CAS追加，不改活动cgroup、不resume。当前容量不足可保存待下一次准入。"),
    management("M13", "set_artifact_keep", "/v1/admin/artifacts/{id}/keep", "设置或释放显式内容保留", "ArtifactKeepUpdate",
               scope="object_project", path_parameters=(identifier(),), success_statuses=(200, 201),
               extra_errors=("ARTIFACT_UNAVAILABLE",), docs=(PROTOCOL_DOC, RETENTION_DOC),
               semantics="CAS唯一管理员keep记录；保留manifest传播全部成员，释放只影响该pin，不取消其他义务或伪造缺失内容恢复。"),
)
