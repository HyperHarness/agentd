"""Generate the proposed contract without importing or starting agentd.

Run ``python -m specs.agentd_v1.generate`` to refresh committed artifacts, or
``python -m specs.agentd_v1.generate --check`` to compare without writing.
Pydantic declarations describe structures; operations.py describes transports.
Neither is an implementation of authorization, transactions or a daemon.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any

from . import models
from .operations import ID_SCHEMA, OPERATIONS, Operation


OUTPUT_DIR = Path(__file__).resolve().parent / "generated"
SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
NOTICE = (
    "[D 待评审] 从零开发的 V0 拟议接口合同，尚非在线 API 或实现声明。"
    "[P 待选参数] 所列初值用于离线校验与评审，不代表已批准的产品默认值。"
    "由 specs/agentd_v1/models.py 与 operations.py 生成；禁止手改生成物。"
    "生成及校验不导入生产 agentd、不启动服务、不调用模型。"
)


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def _replace_refs(value: Any, source: str, target: str) -> Any:
    if isinstance(value, dict):
        return {
            key: (child.replace(source, target, 1) if key == "$ref" and isinstance(child, str)
                  and child.startswith(source) else _replace_refs(child, source, target))
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [_replace_refs(child, source, target) for child in value]
    # Discriminator mappings are URI references too, but their keys are model
    # tags, not "$ref". Rewrite just reference-prefix strings, never prose.
    if isinstance(value, str) and value.startswith(source):
        return value.replace(source, target, 1)
    return value


def build_schemas() -> dict[str, Any]:
    """Return one self-contained Draft 2020-12 bundle with local references."""
    definitions: dict[str, Any] = {}

    def register(name: str, schema: dict[str, Any]) -> None:
        if name in definitions and definitions[name] != schema:
            raise ValueError(f"Different schemas reuse the name {name!r}")
        definitions[name] = schema

    for name, model in sorted(models.MODEL_REGISTRY.items()):
        schema = copy.deepcopy(model.model_json_schema(mode="validation", ref_template="#/$defs/{model}"))
        for nested_name, nested in schema.pop("$defs", {}).items():
            register(nested_name, nested)
        register(name, schema)
    return {
        "$schema": SCHEMA_DIALECT,
        "title": "agentd V0 proposed contract schemas",
        "description": NOTICE,
        "$defs": definitions,
        "x-agentd-design-status": "D-proposed-not-implemented",
        "x-agentd-registered-models": sorted(models.MODEL_REGISTRY),
        "x-draft-parameters": copy.deepcopy(models.DRAFT_PARAMETERS),
    }


def _security(operation: Operation) -> list[dict[str, list[str]]]:
    if operation.auth == "public":
        return []
    write = operation.method not in {"GET", "HEAD"}
    cookie = {"DashboardSession": []}
    if write:
        cookie["CsrfToken"] = []
    if operation.auth == "logout":
        # Anonymous clearing never revokes an authenticated session; the
        # description and x-authentication-rules make that distinction explicit.
        return [cookie, {}]
    if operation.auth == "session":
        return [cookie]
    alternatives = []
    if set(operation.roles) & {"lead", "reviewer"}:
        alternatives.append({"RoleBearer": []})
    if "admin" in operation.roles:
        alternatives.append(cookie)
    return alternatives


def _authentication_rules(operation: Operation) -> str:
    if operation.operation_id == "create_session":
        return "建立会话凭据在正文中验证；Origin 必查并限速，不要求已有会话或 store_epoch。"
    if operation.auth == "public":
        return "公开最小存活信息；没有管理、项目或模型调用权限。"
    if operation.auth == "logout":
        return "有效会话撤销必须同时验证 cookie、CSRF、Origin；匿名或失效 cookie 仅允许清 cookie。"
    return (
        "按服务认证结果检查固定角色及当前项目/授权代次；不接受正文自报身份。"
        "只有 lead/reviewer 使用角色 Bearer；admin 使用 Dashboard cookie。"
        "cookie 写操作同时核 CSRF 与 Origin；Bearer 操作不借用 cookie 权限。"
        "对象可见性、租约、取消及事务前重核仍是业务要求，OpenAPI security 不代替这些检查。"
    )


def _header(name: str, description: str, *, required: bool = True,
            schema: dict[str, Any] | None = None, **extensions: Any) -> dict[str, Any]:
    return {"name": name, "in": "header", "required": required, "description": description,
            "schema": copy.deepcopy(schema or ID_SCHEMA), **extensions}


def _parameters(operation: Operation, definitions: dict[str, Any]) -> list[dict[str, Any]]:
    parameters = [
        {"name": parameter.name, "in": "path", "required": True,
         "description": parameter.description, "schema": copy.deepcopy(parameter.schema)}
        for parameter in operation.path_parameters
    ]
    if operation.query_model:
        query = definitions[operation.query_model]
        required = set(query.get("required", []))
        for name, schema in query.get("properties", {}).items():
            parameters.append({
                "name": name, "in": "query", "required": name in required,
                "description": schema.get("description", "按声明类型解码；不接受未知查询参数。"),
                "schema": copy.deepcopy(schema), "style": "form", "explode": True,
            })
    if operation.idempotent:
        parameters.append(_header(
            "Idempotency-Key", "请求键；CLI/MCP 的 request_key 映射至此。作用域为稳定 principal + 解析后的项目/实例。"
            "相同 key 仅允许重放原方法、路径、版本和业务内容；重复不再执行副作用。"))
    if operation.store_epoch:
        parameters.append(_header(
            "X-Agentd-Store-Epoch", "连接已观察的存储代次；不匹配返回 STORE_RESTORED。"
            "客户端必须重新核对，不能自动更换头后重放旧写入。"))
    if "admin" in operation.roles and operation.scope in {"project", "project_header", "project_or_instance"}:
        mixed = bool(set(operation.roles) & {"lead", "reviewer"})
        conditional = mixed or operation.scope == "project_or_instance"
        parameters.append(_header(
            "X-Agentd-Project", "admin 操作项目范围时必须明确给出项目；lead/reviewer 的项目来自连接，"
            "发送本头返回 INPUT_INVALID。实例操作不得用此头切换范围。",
            required=not conditional,
            **{"x-required-when": "authenticated_role == admin and resolved_scope == project",
               "x-forbidden-when": "authenticated_role in [lead, reviewer] or resolved_scope == instance"}))
    cookie_write = operation.method not in {"GET", "HEAD"} and (
        "admin" in operation.roles or operation.operation_id == "create_session")
    if cookie_write:
        mixed = bool(set(operation.roles) & {"lead", "reviewer"})
        parameters.append(_header(
            "Origin", "浏览器管理写入须匹配受信的本机 Dashboard origin；建立/退出会话同样检查。"
            "本机来源本身不授予身份权限。", required=not mixed,
            schema={"type": "string", "format": "uri"},
            **{"x-required-when": "Dashboard session write or session create/delete"}))
    return parameters


def _response_headers(operation: Operation) -> dict[str, Any]:
    headers: dict[str, Any] = {
        "Cache-Control": {"description": "不缓存身份、配置及任务材料响应。", "schema": {"type": "string", "const": "no-store"}}
    }
    if operation.operation_id in {"create_session", "delete_session"}:
        headers["Set-Cookie"] = {
            "description": "建立或清除 agentd_session；HttpOnly/SameSite，具体有效期为待选参数。",
            "schema": {"type": "string"},
        }
    return headers


def _responses(operation: Operation) -> dict[str, Any]:
    responses: dict[str, Any] = {}
    for status in operation.success_statuses:
        response: dict[str, Any] = {
            "description": {
                200: "当前结果或持久回执；最终业务阶段以响应字段为准。",
                201: "已创建并持久保存的回执；不代表异步任务已完成。",
                202: "操作已登记，后续进度通过 get_operation 查询。",
                204: "退出已处理，无响应正文。",
            }.get(status, "操作成功。"),
            "headers": _response_headers(operation),
        }
        if operation.response_model is not None and status != 204:
            response["content"] = {"application/json": {"schema": {"$ref": f"#/components/schemas/{operation.response_model}"}}}
        responses[str(status)] = response
    for status, codes in operation.errors:
        responses[str(status)] = {
            "description": " / ".join(codes),
            "content": {
                "application/problem+json": {
                    "schema": {
                        "allOf": [
                            {"$ref": "#/components/schemas/Problem"},
                            {"type": "object", "properties": {"status": {"const": status}, "code": {"enum": list(codes)}}},
                        ]
                    }
                }
            },
            "x-agentd-error-codes": list(codes),
        }
    return responses


def build_openapi() -> dict[str, Any]:
    bundle = build_schemas()
    definitions = _replace_refs(bundle["$defs"], "#/$defs/", "#/components/schemas/")
    paths: dict[str, Any] = {}
    ids: set[str] = set()
    for operation in OPERATIONS:
        if operation.operation_id in ids or operation.method.lower() in paths.get(operation.path, {}):
            raise ValueError(f"Duplicate operation {operation.id}")
        ids.add(operation.operation_id)
        for name in (operation.request_model, operation.response_model, operation.query_model):
            if name is not None and name not in models.MODEL_REGISTRY:
                raise ValueError(f"Unknown model {name!r} in {operation.id}")
        if operation.method in {"GET", "HEAD"} and operation.request_model:
            raise ValueError(f"Read operation {operation.id} must not have a body")
        entry: dict[str, Any] = {
            "operationId": operation.operation_id,
            "summary": f"{operation.id} {operation.summary}",
            "description": operation.semantics,
            "tags": ["business" if operation.id.startswith("B") else "management"],
            "security": _security(operation),
            "parameters": _parameters(operation, definitions),
            "responses": _responses(operation),
            "x-agentd-contract-id": operation.id,
            "x-agentd-design-status": "D-proposed-not-implemented",
            "x-agentd-roles": list(operation.roles),
            "x-agentd-scope": operation.scope,
            "x-agentd-authentication-rules": _authentication_rules(operation),
            "x-agentd-idempotency-key": operation.idempotent,
            "x-agentd-store-epoch-required": operation.store_epoch,
            "x-agentd-reject-unknown-query": True,
            "x-agentd-semantic-documents": list(operation.docs),
            "x-agentd-mcp-tool": operation.mcp,
            "x-agentd-cli": operation.cli,
            "x-agentd-adapter-only": operation.operation_id == "renew_review",
        }
        if operation.request_model:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{operation.request_model}"}}},
            }
        paths.setdefault(operation.path, {})[operation.method.lower()] = entry
    return {
        "openapi": "3.1.0",
        "jsonSchemaDialect": SCHEMA_DIALECT,
        "info": {"title": "agentd V0 proposed HTTP contract", "version": "1-draft", "description": NOTICE},
        "tags": [{"name": "business", "description": "B01–B16，其中续租仅供连接适配器。"},
                 {"name": "management", "description": "M01–M13；管理身份不拥有独审判决权限。"}],
        "paths": paths,
        "components": {
            "schemas": definitions,
            "securitySchemes": {
                "RoleBearer": {"type": "http", "scheme": "bearer", "bearerFormat": "opaque project-role credential",
                               "description": "只用于绑定项目和稳定 principal 的 lead/reviewer；须核撤销与当前授权代次。"},
                "DashboardSession": {"type": "apiKey", "in": "cookie", "name": "agentd_session",
                                     "description": "[D] 本机管理员会话 cookie；不能冒用 reviewer 角色。"},
                "CsrfToken": {"type": "apiKey", "in": "header", "name": "X-CSRF-Token",
                              "description": "[D] cookie 写操作必须验证的 CSRF token；仍须检查 Origin。"},
            },
        },
        "x-agentd-design-status": "D-proposed-not-implemented",
        "x-agentd-generated-from": ["specs/agentd_v1/models.py", "specs/agentd_v1/operations.py"],
        "x-agentd-runtime-implementation": False,
        "x-draft-parameters": copy.deepcopy(models.DRAFT_PARAMETERS),
    }


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _anchor(name: str) -> str:
    return "schema-" + re.sub(r"[^a-z0-9_-]", "-", name.lower())


def _model_link(name: str | None) -> str:
    return f"[{name}](#{_anchor(name)})" if name else "无"


def _schema_type(schema: dict[str, Any]) -> str:
    if "$ref" in schema:
        return _model_link(schema["$ref"].rsplit("/", 1)[-1])
    for keyword in ("oneOf", "anyOf", "allOf"):
        if keyword in schema:
            joiner = " 且 " if keyword == "allOf" else " 或 "
            return joiner.join(_schema_type(branch) for branch in schema[keyword])
    kind = schema.get("type")
    if kind == "array":
        return f"array&lt;{_schema_type(schema.get('items', {}))}&gt;"
    if isinstance(kind, list):
        return " 或 ".join(f"`{item}`" for item in kind)
    if kind:
        return f"`{kind}`"
    if "const" in schema:
        return "固定值"
    return "见 schema"


def _compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _constraints(schema: dict[str, Any]) -> str:
    names = {
        "const": "固定值", "enum": "枚举", "format": "格式", "pattern": "正则",
        "minimum": "≥", "maximum": "≤", "exclusiveMinimum": ">", "exclusiveMaximum": "<",
        "multipleOf": "倍数", "minLength": "最短", "maxLength": "最长", "minItems": "最少项",
        "maxItems": "最多项", "uniqueItems": "唯一项", "minProperties": "最少字段", "maxProperties": "最多字段",
        "additionalProperties": "额外字段", "contentEncoding": "编码", "contentMediaType": "内容类型",
    }
    result = [f"{label} `{_compact(schema[name])}`" for name, label in names.items() if name in schema]
    if "discriminator" in schema:
        result.append(f"分支字段 `{schema['discriminator']['propertyName']}`")
    for keyword in ("oneOf", "anyOf", "allOf"):
        for branch in schema.get(keyword, []):
            if "$ref" not in branch and (constraint := _constraints(branch)):
                result.append(f"{_schema_type(branch)}: {constraint}")
    return "；".join(result) or "—"


def _field_table(schema: dict[str, Any]) -> list[str]:
    properties = schema.get("properties")
    if properties is None:
        return ["| 值 | 类型/分支 | 约束 |", "| --- | --- | --- |",
                f"| 根值 | {_cell(_schema_type(schema))} | {_cell(_constraints(schema))} |", ""]
    required = set(schema.get("required", []))
    lines = ["| 字段 | 必填 | 类型 | 约束 / 缺省 | 说明 |", "| --- | --- | --- | --- | --- |"]
    for name, field in properties.items():
        constraints = _constraints(field)
        if "default" in field:
            constraints += f"；缺省 `{_compact(field['default'])}`"
        lines.append(f"| `{name}` | {'是' if name in required else '否'} | {_cell(_schema_type(field))} | "
                     f"{_cell(constraints)} | {_cell(field.get('description', '—'))} |")
    if not properties:
        lines.append("| （无字段） | — | — | — | — |")
    lines.append("")
    if schema.get("additionalProperties") is False:
        lines.extend(["不接受未声明字段。", ""])
    return lines


def _draft_parameter_table() -> list[str]:
    """Render the exported P candidates without maintaining a second value list."""
    value = models.DRAFT_PARAMETERS
    lines = ["## P 参数候选", "", "以下均为 **P 待选参数**，修改须重新生成并复核测试，不能当作已经批准的产品默认值。", ""]
    if isinstance(value, dict) and all(isinstance(item, dict) for item in value.values()):
        lines.extend(["| 参数 | 候选值 | 单位 | 校验责任 | 已含结构/模型检查 |", "| --- | --- | --- | --- | --- |"])
        for name, item in value.items():
            checked = "是（不代表运行时已落实）" if item.get("schema_or_model_check") else "需实现边界检查"
            lines.append(f"| `{_cell(name)}` | `{_cell(_compact(item.get('value')))}` | {_cell(item.get('unit', '—'))} | "
                         f"{_cell(item.get('owner', '—'))} | {checked} |")
    elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
        columns = list(dict.fromkeys(key for item in value for key in item))
        lines.extend(["| " + " | ".join(_cell(column) for column in columns) + " |",
                      "| " + " | ".join("---" for _ in columns) + " |"])
        for item in value:
            lines.append("| " + " | ".join(_cell(item.get(column, "—")) for column in columns) + " |")
    else:
        raise ValueError("DRAFT_PARAMETERS must be a dict of dicts or list of dicts")
    return [*lines, ""]


def build_reference() -> str:
    bundle = build_schemas()
    openapi = build_openapi()
    lines = [
        "<!-- GENERATED FILE: edit models.py / operations.py, then run python -m specs.agentd_v1.generate. -->",
        "# agentd V0 生成接口参考", "", NOTICE, "",
        "来源：[模型声明](../models.py) · [操作注册表](../operations.py) · [生成器](../generate.py)。"
        "机器可读：[OpenAPI 3.1](openapi.json) · [JSON Schema 2020-12](schemas.json)。", "",
        "结构校验不能证明鉴权、幂等事务、Git 对象真实性、资源隔离、进程闭合或模型能力；"
        "行为前置条件须结合[接入合同](../../../docs/design/INTERFACE_GUIDE.md#http-contract)实现和验收。", "",
        "## 公共传输约定", "",
        "所有 GET 均被动且无请求体；读取不领取、不续租、不启动模型。B16 由连接适配器调用，不暴露为模型工具。"
        "角色 Bearer 仅对应 lead/reviewer；Dashboard 管理使用 `agentd_session` cookie。"
        "cookie 写操作同时要求 `X-CSRF-Token` 与受信 `Origin`。这两个命名为 D 拟定合同。", "",
        "除建立/退出管理会话外，所有写操作必须携带 `Idempotency-Key` 与已观察的 `X-Agentd-Store-Epoch`；"
        "请求键属于信封，不放进业务正文。admin 的项目范围依注册表解析；lead/reviewer 不得发送 `X-Agentd-Project`。"
        "只有项目管理复用操作或 catalog 接受该项目头；对象归属始终另行核对。", "",
        "请求正文使用 `application/json`；错误使用 `application/problem+json` 并遵循 "
        + _model_link("Problem") + "。拒绝重复 JSON 键、非有限数、未声明字段及未知查询参数；"
        "字节限制由解码边界检查，无法仅靠 JSON Schema 表达。结构中 nullable 与字段可省略是不同约束。", "",
        "## 操作索引", "",
        "| 编号 | 方法与路径 | 操作 | 角色 |", "| --- | --- | --- | --- |",
    ]
    for operation in OPERATIONS:
        lines.append(f"| [{operation.id}](#{operation.id.lower()}) | `{operation.method} {operation.path}` | "
                     f"{operation.summary} | {_cell(', '.join(operation.roles) or 'public')} |")
    lines.extend(["", *_draft_parameter_table(), "## 逐操作合同", ""])
    for operation in OPERATIONS:
        entry = openapi["paths"][operation.path][operation.method.lower()]
        lines.extend([
            f'<a id="{operation.id.lower()}"></a>', "",
            f"### {operation.id} {operation.summary}", "",
            f"`{operation.method} {operation.path}` · `operationId={operation.operation_id}`", "",
            f"{operation.semantics}", "",
            "| 合同项 | 声明 |", "| --- | --- |",
            f"| 角色 / 范围 | {_cell(', '.join(operation.roles) or 'public')} / `{operation.scope}` |",
            f"| 请求正文 | {_model_link(operation.request_model)} |",
            f"| 成功响应 | {_model_link(operation.response_model)} |",
            f"| 查询模型 | {_model_link(operation.query_model)} |",
            f"| 幂等键 / 存储代次 | {'必需' if operation.idempotent else '不要求'} / {'必需' if operation.store_epoch else '不要求'} |",
            f"| MCP | {_cell('`' + operation.mcp + '`' if operation.mcp else '不作为模型工具')} |",
            f"| CLI | {_cell('`' + operation.cli + '`' if operation.cli else '无独立模型/CLI映射')} |",
            "", _authentication_rules(operation), "",
        ])
        if entry["parameters"]:
            lines.extend(["| 参数 | 位置 | 必填 | 类型 / 约束 | 说明 |", "| --- | --- | --- | --- | --- |"])
            for parameter in entry["parameters"]:
                condition = parameter.get("x-required-when")
                required = "是" if parameter["required"] else (f"有条件：{condition}" if condition else "否")
                lines.append(f"| `{parameter['name']}` | `{parameter['in']}` | {_cell(required)} | "
                             f"{_cell(_schema_type(parameter['schema']))}；{_cell(_constraints(parameter['schema']))} | "
                             f"{_cell(parameter['description'])} |")
            lines.append("")
        else:
            lines.extend(["无路径、查询或额外声明的请求头参数；认证要求仍适用。", ""])
        lines.extend(["| HTTP | 响应 / 稳定错误码 |", "| --- | --- |"])
        for status in operation.success_statuses:
            lines.append(f"| {status} | {_model_link(operation.response_model) if status != 204 else '无正文'} |")
        for status, codes in operation.errors:
            lines.append(f"| {status} | {_model_link('Problem')}：{_cell(', '.join(codes))} |")
        lines.extend(["", "语义依据：" + "、".join(f"[{path}](../../../{path})" for path in operation.docs) + "。", ""])
    lines.extend(["## 类型与字段", "", "下表由模型 JSON Schema 生成；跨字段规则与原始字节规则还需执行模型校验器。"
                  "每个类型提供机器可读 schema 的 JSON Pointer。", ""])
    for name, schema in sorted(bundle["$defs"].items()):
        lines.extend([f'<a id="{_anchor(name)}"></a>', "", f"### {name}", "",
                      f"[JSON Schema](schemas.json#/$defs/{name}) · [OpenAPI schema](openapi.json#/components/schemas/{name})", ""])
        if schema.get("description"):
            lines.extend([schema["description"], ""])
        lines.extend(_field_table(schema))
    return "\n".join(lines).rstrip() + "\n"


def rendered_files() -> dict[str, str]:
    return {"openapi.json": _json(build_openapi()), "schemas.json": _json(build_schemas()),
            "API_REFERENCE.md": build_reference()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare generated artifacts without writing files")
    arguments = parser.parse_args(argv)
    rendered = rendered_files()
    if arguments.check:
        mismatches = [name for name, contents in rendered.items()
                      if not (OUTPUT_DIR / name).is_file() or (OUTPUT_DIR / name).read_bytes() != contents.encode("utf-8")]
        if mismatches:
            print("Generated contract is missing or stale: " + ", ".join(mismatches))
            print("Run: python -m specs.agentd_v1.generate")
            return 1
        print(f"Generated contract is current ({len(rendered)} files; no files written).")
        return 0
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, contents in rendered.items():
        (OUTPUT_DIR / name).write_bytes(contents.encode("utf-8"))
    print(f"Generated {len(rendered)} contract files in {OUTPUT_DIR}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
