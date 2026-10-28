"""Offline checks for the proposed agentd v1 contract, never the production daemon.

Run from the repository root with its existing environment::

    .venv/bin/python -m specs.agentd_v1.check

Generated schemas check structure. Pydantic also checks the documented semantic
invariants that JSON Schema cannot express. Neither proves service authorization,
transactions, actual Git objects, resource isolation, model behavior, or delivery.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError

from . import models
from .operations import OPERATIONS


SPEC_DIR = Path(__file__).resolve().parent
REPO_DIR = SPEC_DIR.parent.parent
HTTP_METHODS = frozenset({"get", "put", "post", "delete", "options", "head", "patch", "trace"})
EXAMPLES = {
    "worker-delivery.code.json": "WorkerDelivery",
    "task-summary.interrupted.json": "TaskSummary",
    "submit-task.code.json": "SubmitTaskRequest",
    "problem.review-lease-expired.json": "Problem",
    "upload-review-evidence.text.json": "EvidenceUpload",
    "review-decision.pass.json": "ReviewDecision",
    "review-evidence-manifest.single.json": "ReviewEvidenceManifest",
    "resource-vector.valid.json": "ResourceVector",
}


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AssertionError(detail)


def load_json(path: Path) -> Any:
    # Generated schemas exceed the public HTTP request limit; no protocol request
    # is accepted here. Keep duplicate-key/non-finite protections for these files.
    return models.strict_json_loads(path.read_bytes(), max_bytes=64 * 1024 * 1024)


def resolve_pointer(document: Any, reference: str) -> Any:
    """Resolve generated local references without network access or a resolver cache."""
    require(reference == "#" or reference.startswith("#/"), f"Non-local schema reference: {reference}")
    node = document
    if reference == "#":
        return node
    for part in reference[2:].split("/"):
        token = part.replace("~1", "/").replace("~0", "~")
        try:
            node = node[int(token)] if isinstance(node, list) else node[token]
        except (KeyError, IndexError, ValueError, TypeError) as error:
            raise AssertionError(f"Unresolvable JSON pointer: {reference}") from error
    return node


def check_references(document: Any) -> int:
    count = 0

    def walk(value: Any) -> None:
        nonlocal count
        if isinstance(value, dict):
            for name, child in value.items():
                if name in {"$ref", "$dynamicRef"}:
                    require(isinstance(child, str), "Schema reference must be a string")
                    resolve_pointer(document, child)
                    count += 1
                else:
                    walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(document)
    return count


def dereference(document: dict[str, Any], value: dict[str, Any]) -> dict[str, Any]:
    while "$ref" in value:
        value = resolve_pointer(document, value["$ref"])
    return value


def check_operations(openapi: dict[str, Any]) -> int:
    registry_routes = [(operation.method.lower(), operation.path) for operation in OPERATIONS]
    for label, values in (
        ("operation ID", [operation.operation_id for operation in OPERATIONS]),
        ("contract ID", [operation.id for operation in OPERATIONS]),
        ("method/path", registry_routes),
    ):
        duplicates = [value for value, count in Counter(values).items() if count > 1]
        require(not duplicates, f"Duplicate {label}: {duplicates}")

    generated_routes: dict[tuple[str, str], dict[str, Any]] = {}
    for path, path_item in openapi.get("paths", {}).items():
        for method, operation in path_item.items():
            if method in HTTP_METHODS:
                generated_routes[(method, path)] = operation
    require(set(generated_routes) == set(registry_routes), "OpenAPI route set differs from OPERATIONS")
    generated_ids = [operation["operationId"] for operation in generated_routes.values()]
    require(len(generated_ids) == len(set(generated_ids)), "OpenAPI operationId values are not unique")

    for declared in OPERATIONS:
        operation = generated_routes[(declared.method.lower(), declared.path)]
        require(operation["operationId"] == declared.operation_id, f"operationId drift: {declared.id}")
        expected = set(re.findall(r"\{([^{}]+)\}", declared.path))
        declared_names = [parameter.name for parameter in declared.path_parameters]
        require(len(declared_names) == len(set(declared_names)), f"Duplicate registry path parameter: {declared.id}")
        require(set(declared_names) == expected, f"Registry path parameters differ: {declared.id}")

        parameters = list(openapi["paths"][declared.path].get("parameters", []))
        parameters.extend(operation.get("parameters", []))
        parameters = [dereference(openapi, parameter) for parameter in parameters]
        identities = [(parameter["in"], parameter["name"]) for parameter in parameters]
        require(len(identities) == len(set(identities)), f"Duplicate OpenAPI parameter: {declared.id}")
        path_parameters = [parameter for parameter in parameters if parameter["in"] == "path"]
        require({parameter["name"] for parameter in path_parameters} == expected,
                f"OpenAPI path parameters differ: {declared.id}")
        require(all(parameter.get("required") is True for parameter in path_parameters),
                f"Optional OpenAPI path parameter: {declared.id}")
        if declared.method.upper() in {"GET", "HEAD"}:
            require("requestBody" not in operation, f"Read request unexpectedly has a body: {declared.id}")
        responses = operation.get("responses", {})
        require(all(str(status) in responses for status in declared.success_statuses),
                f"Missing success status: {declared.id}")
        for name in (declared.request_model, declared.response_model, declared.query_model):
            if name is not None:
                require(name in models.MODEL_REGISTRY, f"Unknown model {name}: {declared.id}")
    return len(generated_routes)


def check_behavior_documents() -> int:
    """Keep generated operations attached to their non-schema behavior contract."""
    references = {reference for operation in OPERATIONS for reference in operation.docs}
    for reference in sorted(references):
        filename, separator, anchor = reference.partition("#")
        document = REPO_DIR / filename
        require(document.is_file(), f"Missing behavior document: {reference}")
        require(bool(separator and anchor), f"Missing stable behavior anchor: {reference}")
        declared_anchors = re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)["\']', document.read_text())
        require(anchor in declared_anchors, f"Missing behavior anchor: {reference}")
    return len(references)


def schema_validator(schemas: dict[str, Any], model_name: str) -> Draft202012Validator:
    require(model_name in schemas["$defs"], f"Missing generated schema: {model_name}")
    schema = {"$schema": schemas["$schema"], "$defs": schemas["$defs"], "$ref": f"#/$defs/{model_name}"}
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_model(model_name: str, data: dict[str, Any]) -> Any:
    # Test the documented JSON decode policy and Pydantic together. A direct
    # model_validate_json call alone would lose duplicate JSON object keys.
    raw = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
    return models.parse_model(models.MODEL_REGISTRY[model_name], raw)


def check_examples(schemas: dict[str, Any]) -> dict[str, dict[str, Any]]:
    present = {path.name for path in SPEC_DIR.joinpath("examples").glob("*.json")}
    require(present == set(EXAMPLES), f"Unregistered or missing examples: {present ^ set(EXAMPLES)}")
    examples = {}
    for filename, model_name in EXAMPLES.items():
        path = SPEC_DIR / "examples" / filename
        data = load_json(path)
        validate_model(model_name, data)
        schema_validator(schemas, model_name).validate(data)
        examples[filename] = data
    return examples


def check_split_regressions(schemas: dict[str, Any]) -> int:
    """Preserve three management contracts lost during the document/schema split."""
    # Retirement intent is writable; retirement completion is also observable.
    for model_name, flags in (
        ("WorkerUpdate", ("retire_requested",)),
        ("WorkerView", ("retire_requested", "retired")),
    ):
        schema = schemas["$defs"][model_name]
        for flag in flags:
            require(flag in schema.get("required", []), f"Missing required {model_name}.{flag}")
            require(schema["properties"][flag].get("type") == "boolean",
                    f"Retirement flag must be boolean: {model_name}.{flag}")

    # The bounded admin snapshot carries summaries; full operation details are
    # retrieved through B14, not embedded repeatedly in that snapshot.
    operations = schemas["$defs"]["AdminServiceView"]["properties"]["operations"]
    require(operations.get("items", {}).get("$ref") == "#/$defs/OperationSummary",
            "AdminServiceView.operations must contain OperationSummary, not Operation")
    summary = schemas["$defs"]["OperationSummary"]
    require(set(summary["properties"]) == {"operation_id", "kind", "phase", "version", "updated_at"},
            "OperationSummary must remain the five-field snapshot summary")

    # A whole omitted policy has a default. A supplied policy must state all
    # three choices, even when each is explicitly null (retain).
    retain = {"final_seconds": None, "rejected_seconds": None, "logs_workspace_seconds": None}
    require(set(schemas["$defs"]["ContentRetention"].get("required", [])) == set(retain),
            "All three ContentRetention members must be required")
    require("content_retention" in schemas["$defs"]["ProjectView"].get("required", []),
            "ProjectView must return the expanded retention policy")
    project = {
        "name": "split-contract-check",
        "repository": None,
        "input_roots": [],
        "default_requirements": {"tool_refs": [], "mcp_refs": [], "shared_resources": []},
        "recovery_policy_ref": None,
        "shared_resource_registry": [],
    }
    for payload in (project, {**project, "content_retention": retain}):
        parsed = validate_model("ProjectDefinition", payload)
        schema_validator(schemas, "ProjectDefinition").validate(payload)
        require(parsed.model_dump(mode="json")["content_retention"] == retain,
                "Omitted retention policy must expand to three null retain values")
    for policy in ({"final_seconds": None}, None):
        payload = {**project, "content_retention": policy}
        try:
            validate_model("ProjectDefinition", payload)
        except (ValidationError, ValueError):
            pass
        else:
            raise AssertionError("Pydantic accepted a partial or null retention policy")
        require(not schema_validator(schemas, "ProjectDefinition").is_valid(payload),
                "JSON Schema accepted a partial or null retention policy")
    return 3


def check_rejections(schemas: dict[str, Any], examples: dict[str, dict[str, Any]]) -> dict[str, int]:
    counts = {"structural_rejections": 0, "semantic_rejections": 0, "json_policy_rejections": 0}

    def reject(model_name: str, payload: dict[str, Any], label: str, *, structural: bool = False) -> None:
        try:
            validate_model(model_name, payload)
        except (ValidationError, ValueError):
            pass
        else:
            raise AssertionError(f"Pydantic accepted invalid {label}")
        schema_errors = list(schema_validator(schemas, model_name).iter_errors(payload))
        if structural:
            require(bool(schema_errors), f"JSON Schema accepted structurally invalid {label}")
        counts["structural_rejections" if structural else "semantic_rejections"] += 1

    spec = copy.deepcopy(examples["submit-task.code.json"]["spec"])
    for key, value in (("model_id", "forced_model"), ("unexpected_field", "unrecognized")):
        invalid = {**spec, key: value}
        reject("TaskSpecInput", invalid, f"TaskSpecInput.{key}", structural=True)

    invalid = copy.deepcopy(examples["task-summary.interrupted.json"])
    invalid["execution"]["observation"] = "closed"
    invalid["actions"] = []
    invalid["attention"] = []
    invalid.update(status="finished", outcome=None)
    reject("TaskSummary", invalid, "finished task without an outcome")
    invalid.update(outcome="passed", review_rejections=3)
    reject("TaskSummary", invalid, "PASS after three rejections")

    invalid = copy.deepcopy(examples["review-decision.pass.json"])
    invalid["criterion_results"][0]["result"] = "unverified"
    reject("ReviewDecision", invalid, "PASS with an unverified criterion")

    invalid = copy.deepcopy(examples["upload-review-evidence.text.json"])
    invalid["sha256"] = "0" * 64
    reject("EvidenceUpload", invalid, "uploaded evidence with a different digest")

    invalid = copy.deepcopy(examples["review-evidence-manifest.single.json"])
    invalid["schema_version"] = "review-evidence/unknown"
    reject("ReviewEvidenceManifest", invalid, "manifest format", structural=True)
    invalid = copy.deepcopy(examples["review-evidence-manifest.single.json"])
    invalid["members"][0]["index"] = 1
    reject("ReviewEvidenceManifest", invalid, "manifest with a missing first index")
    invalid = copy.deepcopy(examples["review-evidence-manifest.single.json"])
    repeated = {**invalid["members"][0], "index": 1}
    invalid["members"].append(repeated)
    invalid["total_size_bytes"] *= 2
    reject("ReviewEvidenceManifest", invalid, "manifest with a repeated artifact")
    invalid = copy.deepcopy(examples["review-evidence-manifest.single.json"])
    invalid["total_size_bytes"] += 1
    reject("ReviewEvidenceManifest", invalid, "manifest length mismatch")

    for key, value in (("cpu_quota", 0), ("memory_bytes", -1), ("pids", True), ("swap_bytes", -1)):
        invalid = {**examples["resource-vector.valid.json"], key: value}
        reject("ResourceVector", invalid, f"invalid resources.{key}", structural=True)

    # Duplicate members and non-finite values must fail before typed validation;
    # neither can be detected after a permissive JSON decoder loses information.
    for raw in (
        b'{"value":1,"value":2}',
        b'{"outer":{"value":1,"value":2}}',
        b'{"value":NaN}',
        b'{"value":Infinity}',
        b'{"value":-Infinity}',
    ):
        try:
            models.strict_json_loads(raw)
        except ValueError:
            counts["json_policy_rejections"] += 1
        else:
            raise AssertionError(f"JSON policy accepted {raw!r}")
    return counts


def check_example_content(examples: dict[str, dict[str, Any]]) -> int:
    """Check actual bytes of a bounded manifest fixture, not an external artifact store.

    JSON Schema cannot establish the digest of referenced artifact bytes. This
    links the sample manifest to real sample content and demonstrates the separate
    content-integrity obligation without pretending to test a service repository.
    """
    import base64

    evidence = examples["upload-review-evidence.text.json"]
    content = base64.b64decode(evidence["content_base64"], validate=True)
    manifest = examples["review-evidence-manifest.single.json"]
    member = manifest["members"][0]
    require(len(content) == member["size_bytes"] == manifest["total_size_bytes"], "Sample evidence length drift")
    digest = hashlib.sha256(content).hexdigest()
    require(digest == evidence["sha256"] == member["sha256"] == manifest["total_sha256"],
            "Sample evidence/manifest digest drift")
    return 1


def main() -> int:
    generation = subprocess.run(
        [sys.executable, "-m", "specs.agentd_v1.generate", "--check"],
        cwd=REPO_DIR,
        text=True,
        capture_output=True,
        check=False,
    )
    if generation.returncode:
        raise AssertionError(f"Generated contract files are stale:\n{generation.stdout}{generation.stderr}")
    schemas = load_json(SPEC_DIR / "generated" / "schemas.json")
    openapi = load_json(SPEC_DIR / "generated" / "openapi.json")
    require(str(openapi.get("openapi", "")).startswith("3.1."), "Expected JSON-Schema-compatible OpenAPI 3.1")
    Draft202012Validator.check_schema(schemas)
    for name, model in models.MODEL_REGISTRY.items():
        require(name == model.__name__, f"Registry model/name mismatch: {name}")
        require(name in schemas["$defs"], f"Missing registry model schema: {name}")
        schema_validator(schemas, name).check_schema(schemas["$defs"][name])
    references = check_references(schemas) + check_references(openapi)
    routes = check_operations(openapi)
    behavior_documents = check_behavior_documents()
    examples = check_examples(schemas)
    split_regressions = check_split_regressions(schemas)
    negative_counts = check_rejections(schemas, examples)
    content_checks = check_example_content(examples)
    result = {
        "result": "PASS",
        "scope": "offline_design_contract_only",
        "operations": len(OPERATIONS),
        "routes": routes,
        "registered_models": len(models.MODEL_REGISTRY),
        "schema_definitions": len(schemas["$defs"]),
        "resolved_local_references": references,
        "behavior_document_references": behavior_documents,
        "valid_examples": len(examples),
        "split_contract_regression_checks": split_regressions,
        **negative_counts,
        "sample_content_integrity_checks": content_checks,
        "generated_files_checked": 3,
        "runtime_model_host_validation": "NOT_RUN",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, ValidationError, ValueError) as error:
        print(f"FAIL (offline design contract check): {error}", file=sys.stderr)
        raise SystemExit(1) from error
