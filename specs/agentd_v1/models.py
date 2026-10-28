"""Executable *proposed* contracts for the agentd rewrite.

Decision status: D (design for review), with P (candidate, unapproved) limits.
Validated with the workspace's Pydantic 2.13.5. This module has no dependency on
the production ``agentd`` package and performs no filesystem/network operations.

JSON Schema expresses structural checks. Python validators additionally express
UTF-8 byte limits, digests, and cross-field checks. Neither proves authorization,
transactionality, resource isolation, complete external evidence, or actual HTTP
admission. ``strict_json_loads``/``parse_model`` provide the separate JSON policy.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import PurePosixPath, PureWindowsPath
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    RootModel,
    StringConstraints,
    ValidationInfo,
    model_validator,
)
from pydantic.experimental.missing_sentinel import MISSING


def _parameter(value: JsonValue, unit: str, owner: str, schema_check: bool = False) -> dict[str, JsonValue]:
    return {"value": value, "unit": unit, "status": "P-proposed", "owner": owner,
            "schema_or_model_check": schema_check}


DRAFT_PARAMETERS: dict[str, dict[str, JsonValue]] = {
    "id_key_max_bytes": _parameter(128, "ASCII bytes", "contract model", True),
    "title_max_bytes": _parameter(512, "UTF-8 bytes", "contract model", True),
    "json_request_max_bytes": _parameter(1048576, "bytes", "HTTP decoder / strict_json_loads"),
    "task_spec_max_bytes": _parameter(524288, "canonical UTF-8 JSON bytes", "contract model", True),
    "goal_max_bytes": _parameter(131072, "UTF-8 bytes", "contract model", True),
    "criterion_max_bytes": _parameter(8192, "UTF-8 bytes", "contract model", True),
    "criteria_max_count": _parameter(64, "items", "contract model", True),
    "inputs_max_count": _parameter(128, "items", "contract model", True),
    "json_max_depth": _parameter(16, "container levels", "HTTP decoder / strict_json_loads"),
    "page_default": _parameter(20, "items", "query model", True),
    "page_max": _parameter(100, "items", "query model", True),
    "artifact_chunk_default_bytes": _parameter(65536, "bytes", "query model", True),
    "artifact_chunk_max_bytes": _parameter(262144, "bytes", "contract model", True),
    "reason_max_bytes": _parameter(16384, "UTF-8 bytes", "contract model", True),
    "execution_input_max_bytes": _parameter(1048576, "canonical UTF-8 JSON bytes", "execution adapter"),
    "manifest_max_bytes": _parameter(1048576, "bytes", "artifact store"),
    "manifest_direct_members_max": _parameter(128, "items", "contract model / artifact store", True),
    "delivery_max_bytes": _parameter(262144, "canonical UTF-8 JSON bytes", "contract model", True),
    "candidate_members_total_max_bytes": _parameter(1073741824, "bytes", "artifact admission"),
    "candidate_bundle_max_bytes": _parameter(2147483648, "bytes", "artifact admission"),
    "review_evidence_segment_max_bytes": _parameter(262144, "decoded bytes", "contract model", True),
    "review_evidence_total_max_bytes": _parameter(16777216, "bytes", "manifest model / artifact store", True),
    "review_evidence_segments_max": _parameter(64, "items", "manifest model", True),
    "review_lease_ttl_seconds": _parameter(1800, "seconds", "review lease service"),
    "review_lease_max_hold_seconds": _parameter(28800, "seconds", "review lease service"),
    "review_activity_ttl_seconds": _parameter(300, "seconds", "review lease service"),
    "v0_automatic_execution_recoveries": _parameter(0, "attempts / Task", "recovery policy"),
    "v1_automatic_execution_recoveries": _parameter(2, "attempts / Task", "recovery policy"),
    "execution_recovery_window_seconds": _parameter(86400, "seconds from first execution fault", "recovery policy"),
    "execution_recovery_backoff_seconds": _parameter([30, 120], "seconds", "recovery policy"),
    "automatic_review_reopens": _parameter(3, "attempts / Task", "review recovery policy"),
    "review_recovery_window_seconds": _parameter(86400, "seconds from first review fault", "review recovery policy"),
    "review_recovery_backoff_seconds": _parameter([60, 300, 900], "seconds", "review recovery policy"),
    "execution_timeout_seconds": _parameter(7200, "seconds / Execution", "supervisor / frozen recovery policy"),
    "recheck_timeout_seconds": _parameter(30, "seconds", "recovery application"),
    "action_ref_ttl_seconds": _parameter(300, "seconds", "task action service"),
    "log_pipe_buffer_max_bytes": _parameter(1048576, "bytes / stream", "execution output drainer"),
    "execution_log_budget_bytes": _parameter(67108864, "bytes / Execution", "private log storage"),
}

def _limit(name: str) -> int:
    return int(DRAFT_PARAMETERS[name]["value"])


ID_MAX_BYTES = _limit("id_key_max_bytes")
TITLE_MAX_BYTES = _limit("title_max_bytes")
JSON_REQUEST_MAX_BYTES = _limit("json_request_max_bytes")
TASK_SPEC_MAX_BYTES = _limit("task_spec_max_bytes")
GOAL_MAX_BYTES = _limit("goal_max_bytes")
CRITERION_MAX_BYTES = _limit("criterion_max_bytes")
CRITERIA_MAX_COUNT = _limit("criteria_max_count")
INPUTS_MAX_COUNT = _limit("inputs_max_count")
JSON_MAX_DEPTH = _limit("json_max_depth")
PAGE_DEFAULT = _limit("page_default")
PAGE_MAX = _limit("page_max")
ARTIFACT_CHUNK_DEFAULT_BYTES = _limit("artifact_chunk_default_bytes")
ARTIFACT_CHUNK_MAX_BYTES = _limit("artifact_chunk_max_bytes")
REASON_MAX_BYTES = _limit("reason_max_bytes")
EXECUTION_INPUT_MAX_BYTES = _limit("execution_input_max_bytes")
MANIFEST_MEMBERS_MAX = _limit("manifest_direct_members_max")
DELIVERY_MAX_BYTES = _limit("delivery_max_bytes")
EVIDENCE_SEGMENT_MAX_BYTES = _limit("review_evidence_segment_max_bytes")
EVIDENCE_TOTAL_MAX_BYTES = _limit("review_evidence_total_max_bytes")
EVIDENCE_SEGMENTS_MAX = _limit("review_evidence_segments_max")
DESIGN_METADATA = {"x-decision-status": "D-proposed", "x-parameter-status": "P-proposed-not-approved"}


def _no_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {value}")


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def strict_json_loads(raw: str | bytes | bytearray, *, max_bytes: int = JSON_REQUEST_MAX_BYTES) -> Any:
    """Design decoder policy, not proof that a deployed HTTP decoder uses it."""
    if isinstance(raw, str):
        encoded = raw.encode("utf-8", errors="strict")
        source = raw
    elif isinstance(raw, (bytes, bytearray)):
        encoded = bytes(raw)
        source = encoded.decode("utf-8", errors="strict")
    else:
        raise TypeError("JSON source must be text or UTF-8 bytes")
    if len(encoded) > max_bytes:
        raise ValueError("JSON byte limit exceeded")
    if source.startswith("\ufeff"):
        raise ValueError("JSON BOM is not accepted")
    value = json.loads(source, object_pairs_hook=_unique_pairs, parse_constant=_no_constant)
    stack = [(value, 0)]
    while stack:
        item, depth = stack.pop()
        if isinstance(item, (dict, list)):
            depth += 1
            if depth > JSON_MAX_DEPTH:
                raise ValueError("JSON nesting limit exceeded")
            stack.extend((child, depth) for child in (item.values() if isinstance(item, dict) else item))
        elif isinstance(item, float) and not math.isfinite(item):
            raise ValueError("non-finite JSON number is forbidden")
    return value


def parse_model(model: type[BaseModel], raw: str | bytes | bytearray, *, context: Any = None) -> BaseModel:
    """Decode with the proposed request policy, then validate strictly."""
    return model.model_validate(strict_json_loads(raw), strict=True, context=context)


def _utf8_limit(maximum: int):
    def validate(value: str) -> str:
        if len(value.encode("utf-8", errors="strict")) > maximum:
            raise ValueError(f"UTF-8 byte length exceeds proposed limit {maximum}")
        return value
    return validate


def _text(maximum: int, *, minimum: int = 1):
    return Annotated[str, StringConstraints(strict=True, min_length=minimum, max_length=maximum),
                     AfterValidator(_utf8_limit(maximum)),
                     Field(json_schema_extra={"x-maxUtf8Bytes": maximum, "x-limit-status": "P-proposed"})]


def _relative(value: str) -> str:
    if not value or value.startswith("/") or "\\" in value or "\x00" in value:
        raise ValueError("invalid relative path")
    if any(member in {"", ".", ".."} for member in value.split("/")):
        raise ValueError("relative path contains forbidden component")
    return value


def _absolute(value: str) -> str:
    if "\x00" in value or not (PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute()):
        raise ValueError("absolute path required; platform/ownership checks remain external")
    return value


def _utc_time(value: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)", value):
        raise ValueError("UTC RFC3339 timestamp required")
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def _unique(values: list[Any], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")


def _json_size(model: BaseModel, maximum: int) -> None:
    value = json.dumps(model.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    if len(value.encode("utf-8")) > maximum:
        raise ValueError("proposed serialized JSON byte limit exceeded")


Id = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=ID_MAX_BYTES,
                                     pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")]
RequestKey = Id
Text = Annotated[str, StringConstraints(strict=True, min_length=1)]
Reason = _text(REASON_MAX_BYTES)
Title = _text(TITLE_MAX_BYTES)
Goal = _text(GOAL_MAX_BYTES)
CriterionText = _text(CRITERION_MAX_BYTES)
UInt = Annotated[int, Field(strict=True, ge=0)]
PositiveInt = Annotated[int, Field(strict=True, gt=0)]
FiniteNumber = Annotated[float, Field(strict=True, allow_inf_nan=False)]
PositiveNumber = Annotated[float, Field(strict=True, gt=0, allow_inf_nan=False)]
Ratio = Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)]
Sha256 = Annotated[str, StringConstraints(strict=True, pattern=r"^[0-9a-f]{64}$")]
Time = Annotated[str, AfterValidator(_utc_time), Field(json_schema_extra={"format": "date-time"})]
RelativePath = Annotated[str, StringConstraints(strict=True, min_length=1), AfterValidator(_relative)]
AbsolutePath = Annotated[str, StringConstraints(strict=True, min_length=1), AfterValidator(_absolute)]
TaskStatus = Literal["queued", "running", "reviewing", "finished", "canceled"]
Outcome = Literal["passed", "review_failed"]
Role = Literal["lead", "reviewer"]


class DesignModel(BaseModel):
    """D: strict proposed schema; validators are not authorization checks."""
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False,
                              json_schema_extra=DESIGN_METADATA)


class Meta(DesignModel):
    api_version: Literal["1"]
    instance_id: Id
    store_epoch: Id
    observed_at: Time
    observed_revision: UInt


class FieldError(DesignModel):
    pointer: str
    code: Text
    detail: Reason


class Problem(DesignModel):
    type: Text
    title: Text
    status: Annotated[int, Field(ge=400, le=599)]
    detail: Reason
    instance: Text
    code: Text
    retry: Literal["never", "same_request", "refresh_then_new_request", "query_request"]
    operation_id: Id | None
    request_recorded: bool | None
    field_errors: list[FieldError]

    @model_validator(mode="after")
    def unknown_requires_query(self) -> Self:
        if self.request_recorded is None and self.retry != "query_request":
            raise ValueError("unknown request result requires query_request")
        return self


class FixedRef(DesignModel):
    id: Id
    version: PositiveInt


class GitOid(DesignModel):
    algorithm: Literal["sha1", "sha256"]
    value: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]+$")]

    @model_validator(mode="after")
    def full_oid(self) -> Self:
        if len(self.value) != (40 if self.algorithm == "sha1" else 64):
            raise ValueError("Git OID must be complete for the named algorithm")
        return self


class ContentRetention(DesignModel):
    final_seconds: PositiveInt | None
    rejected_seconds: PositiveInt | None
    logs_workspace_seconds: PositiveInt | None


class ArtifactRetention(DesignModel):
    policy_version: Id
    expires_at: Time | None
    explicit_keep: bool
    keep_version: UInt
    pin_count: UInt


class ArtifactRef(DesignModel):
    id: Id
    kind: Text
    sha256: Sha256
    size_bytes: UInt
    media_type: Text
    availability: Literal["available", "retiring", "missing", "corrupt", "expired"]
    retention: ArtifactRetention


class ResourceVector(DesignModel):
    cpu_quota: PositiveNumber = Field(description="Percent of one logical CPU; 100 means one CPU.")
    memory_bytes: PositiveInt
    pids: PositiveInt
    swap_bytes: UInt


class SharedResourceDefinition(DesignModel):
    resource_id: Id
    scope: Literal["instance", "project", "external"]
    kind: Literal["file", "port", "database", "service", "cache"]
    canonical_identity: Text
    isolation_mode: Literal["namespace", "exclusive", "shared_read"]
    namespace_rule: Text | None


class ResourceRequirement(DesignModel):
    resource_id: Id
    access_mode: Literal["read", "write"]


class Requirements(DesignModel):
    tool_refs: list[FixedRef]
    mcp_refs: list[FixedRef]
    shared_resources: list[ResourceRequirement]

    @model_validator(mode="after")
    def distinct_requirements(self) -> Self:
        _unique([(ref.id, ref.version) for ref in self.tool_refs], "tool refs")
        _unique([(ref.id, ref.version) for ref in self.mcp_refs], "MCP refs")
        _unique([ref.resource_id for ref in self.shared_resources], "shared resource refs")
        return self


class GitInput(DesignModel):
    kind: Literal["git"]
    source_id: Id
    commit: GitOid
    mount_path: RelativePath
    purpose: Literal["base", "material"]


class FileInput(DesignModel):
    kind: Literal["file"]
    source_root_id: Id
    relative_path: RelativePath
    sha256: Sha256
    mount_path: RelativePath


class ArtifactInput(DesignModel):
    kind: Literal["artifact"]
    artifact_id: Id
    sha256: Sha256
    mount_path: RelativePath


InputRef = Annotated[GitInput | FileInput | ArtifactInput, Field(discriminator="kind")]


class DependencySelector(DesignModel):
    kind: Literal["passed_commit", "artifact"]
    artifact_key: Id | None

    @model_validator(mode="after")
    def selector_key(self) -> Self:
        if (self.kind == "artifact") != (self.artifact_key is not None):
            raise ValueError("only an artifact selector has a required artifact_key")
        return self


class Dependency(DesignModel):
    """D/V1 shape; nonempty dependency lists are rejected by the V0 input."""
    task_id: Id
    purpose: Literal["gate", "input"]
    selector: DependencySelector | None
    mount_path: RelativePath | None

    @model_validator(mode="after")
    def shape_for_purpose(self) -> Self:
        if self.purpose == "gate" and (self.selector is not None or self.mount_path is not None):
            raise ValueError("gate dependency has no selector or mount path")
        if self.purpose == "input" and (self.selector is None or self.mount_path is None):
            raise ValueError("input dependency requires a selector and mount path")
        return self


class Criterion(DesignModel):
    id: Id
    description: CriterionText


class Deliverable(DesignModel):
    key: Id
    kind: Literal["code_commit", "report", "file"]
    description: Reason
    required: bool


class TaskScope(DesignModel):
    include: list[Text]
    exclude: list[Text]


class Difficulty(DesignModel):
    scale_id: Id
    level: int = Field(description="Range is determined by the registered scale, not hardcoded to 1–5.")
    reason: Reason


class TaskSpecInput(DesignModel):
    schema_version: Literal["1"]
    kind: Literal["code", "report"]
    title: Title
    goal: Goal
    scope: TaskScope
    difficulty: Difficulty
    inputs: list[InputRef] = Field(max_length=INPUTS_MAX_COUNT)
    acceptance: list[Criterion] = Field(min_length=1, max_length=CRITERIA_MAX_COUNT)
    deliverables: list[Deliverable] = Field(min_length=1)
    requirements: Requirements | MISSING = MISSING
    recovery_policy_ref: FixedRef | MISSING = MISSING
    dependencies: list[Dependency] = Field(default_factory=list, max_length=0, description="V0 supports independent tasks.")
    related_task_id: Id | None = None

    @model_validator(mode="after")
    def valid_task_contract(self) -> Self:
        _unique([item.id for item in self.acceptance], "criterion ids")
        _unique([item.key for item in self.deliverables], "deliverable keys")
        _unique([item.mount_path for item in self.inputs], "input mount paths")
        code = [item for item in self.deliverables if item.kind == "code_commit" and item.required]
        reports = [item for item in self.deliverables if item.kind == "report" and item.required]
        bases = [item for item in self.inputs if isinstance(item, GitInput) and item.purpose == "base"]
        if self.kind == "code" and (len(code) != 1 or len(bases) != 1):
            raise ValueError("V0 code task requires one required code_commit and one exact Git base")
        if self.kind == "report" and (not reports or code):
            raise ValueError("report task requires a report and cannot require a code commit")
        _json_size(self, TASK_SPEC_MAX_BYTES)
        return self


class TaskSpec(TaskSpecInput):
    """Effective immutable TaskSpec: defaults were resolved by the submit service."""
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True, allow_inf_nan=False,
                              json_schema_extra=DESIGN_METADATA)
    requirements: Requirements
    recovery_policy_ref: FixedRef
    dependencies: list[Dependency] = Field(max_length=0)
    related_task_id: Id | None
    project_config_ref: FixedRef


class SubmitTaskRequest(DesignModel):
    spec: TaskSpecInput


class ArtifactResolutionEvidence(DesignModel):
    kind: Literal["artifact"]
    artifact_id: Id
    sha256: Sha256


class ExternalReceiptEvidence(DesignModel):
    kind: Literal["external_receipt"]
    system: Text
    receipt_id: Text
    checked_at: Time
    observation: Reason


class OperatorStatementEvidence(DesignModel):
    kind: Literal["operator_statement"]
    statement: Reason


ResolutionEvidence = Annotated[ArtifactResolutionEvidence | ExternalReceiptEvidence | OperatorStatementEvidence,
                               Field(discriminator="kind")]
ResolutionDecision = Literal["not_applied", "already_applied", "safe_to_repeat", "compensated",
                             "environment_repaired", "restart_from_fixed_inputs"]


class ResolutionRequirement(DesignModel):
    issue_ref: Text
    kind: Literal["external_effect", "environment_check", "progress_loss"]
    description: Reason
    allowed_decisions: list[ResolutionDecision]
    evidence_required: bool


class Resolution(DesignModel):
    issue_ref: Text
    decision: ResolutionDecision
    note: Reason
    evidence: list[ResolutionEvidence]


class ResumeTaskRequest(DesignModel):
    action_ref: Text
    resolutions: list[Resolution] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_issues(self) -> Self:
        _unique([item.issue_ref for item in self.resolutions], "resolution issues")
        return self


class CancelTaskRequest(DesignModel):
    reason: Reason | MISSING = MISSING


class Action(DesignModel):
    name: Literal["resume_task", "cancel_task"]
    ref: Text | None
    label: Text
    availability: Literal["available", "requires_check", "unavailable"]
    reason_code: Text | None
    requirements: list[ResolutionRequirement]

    @model_validator(mode="after")
    def resume_ref_required(self) -> Self:
        if self.name == "resume_task" and self.ref is None:
            raise ValueError("resume action requires a service-issued reference")
        return self


class Attention(DesignModel):
    code: Text
    detail: Reason
    subject_ref: Id | None
    resolvable_by: Literal["lead", "admin", "reviewer", "system"]
    action_ref: Text | None


class DifficultySummary(DesignModel):
    scale_id: Id
    level: int


class AssignmentSummary(DesignModel):
    worker_id: Id
    model_id: Id
    config_id: Id


class Assignment(AssignmentSummary):
    policy_version: Id
    reason: Reason
    resource_adjustment_id: Id | None


class ExecutionObservation(DesignModel):
    observation: Literal["none", "preparing", "active", "interrupted", "unknown", "stopping", "closed"]
    execution_id: Id | None


class ReviewObservation(DesignModel):
    observation: Literal["none", "queued", "leased", "paused", "unavailable"]
    candidate_id: Id | None


class TaskSummary(DesignModel):
    task_id: Id
    title: Title
    kind: Literal["code", "report"]
    status: TaskStatus
    outcome: Outcome | None
    version: UInt
    difficulty: DifficultySummary
    review_rejections: Annotated[int, Field(ge=0, le=3)]
    assignment: AssignmentSummary | None
    execution: ExecutionObservation
    review: ReviewObservation
    attention: list[Attention]
    actions: list[Action]
    created_at: Time
    updated_at: Time

    @model_validator(mode="after")
    def valid_terminal_combination(self) -> Self:
        if (self.status == "finished") != (self.outcome is not None):
            raise ValueError("only finished tasks have passed/review_failed outcome")
        if self.outcome == "review_failed" and self.review_rejections != 3:
            raise ValueError("review_failed requires exactly three valid rejections")
        if self.outcome != "review_failed" and self.review_rejections == 3:
            raise ValueError("three rejections require finished/review_failed")
        if self.status in {"finished", "canceled", "reviewing", "queued"} and self.execution.observation in {
                "preparing", "active", "unknown", "stopping"}:
            raise ValueError("this task phase cannot have an unclosed worker observation")
        return self


class CandidateDeliverable(DesignModel):
    key: Id
    artifact: ArtifactRef


class CandidateView(DesignModel):
    candidate_id: Id
    task_id: Id
    round: Annotated[int, Field(ge=1, le=3)]
    manifest: ArtifactRef
    code_commit: GitOid | None
    deliverables: list[CandidateDeliverable]
    created_at: Time

    @model_validator(mode="after")
    def unique_deliverables(self) -> Self:
        _unique([item.key for item in self.deliverables], "candidate deliverable keys")
        return self


class ResolvedInputsView(DesignModel):
    manifest: ArtifactRef
    base_commit: GitOid | None


class ResourceOverrideView(DesignModel):
    version: UInt
    override_id: Id | None
    resources: ResourceVector | None

    @model_validator(mode="after")
    def coherent_optional_override(self) -> Self:
        if (self.override_id is None) != (self.resources is None):
            raise ValueError("override identity and resources must appear together")
        if self.override_id is None and self.version != 0:
            raise ValueError("absent resource override has version zero")
        return self


class TaskDetail(DesignModel):
    summary: TaskSummary
    spec: TaskSpec
    resolved_inputs: ResolvedInputsView | None
    assignment: Assignment | None
    resource_override: ResourceOverrideView
    current_candidate: CandidateView | None
    execution_history_ref: ArtifactRef | None
    artifacts: list[ArtifactRef]
    related_tasks: list[Id]
    meta: Meta

    @model_validator(mode="after")
    def candidate_ownership(self) -> Self:
        if self.current_candidate is not None and self.current_candidate.task_id != self.summary.task_id:
            raise ValueError("candidate belongs to another task")
        if self.summary.kind != self.spec.kind:
            raise ValueError("task summary and contract kind differ")
        return self


class PageQuery(DesignModel):
    cursor: Text | MISSING = MISSING
    limit: Annotated[int, Field(ge=1, le=PAGE_MAX)] = PAGE_DEFAULT


class TaskListQuery(PageQuery):
    status: TaskStatus | MISSING = MISSING
    outcome: Outcome | MISSING = MISSING
    model_id: Id | MISSING = MISSING
    difficulty_level: int | MISSING = MISSING


class TaskPage(DesignModel):
    items: list[TaskSummary] = Field(max_length=PAGE_MAX)
    next_cursor: Text | None
    meta: Meta


class NextReviewRequest(DesignModel):
    preferred_candidate_id: Id | MISSING = MISSING


class EmptyReviewClaim(DesignModel):
    status: Literal["empty"]
    reason: Literal["queue_empty", "review_paused", "no_eligible_candidate"]
    meta: Meta


class HeldReviewClaim(DesignModel):
    status: Literal["claimed"]
    review_handle: Text
    candidate: CandidateView
    task_spec: TaskSpec
    evidence_index: ArtifactRef
    materialization_manifest_ref: ArtifactRef
    lease_expires_at: Time
    max_hold_until: Time
    operation_id: Id
    meta: Meta

    @model_validator(mode="after")
    def bounded_lease(self) -> Self:
        if datetime.fromisoformat(self.lease_expires_at.replace("Z", "+00:00")) > datetime.fromisoformat(
                self.max_hold_until.replace("Z", "+00:00")):
            raise ValueError("lease expires after its absolute deadline")
        return self


class ReviewClaim(RootModel[Annotated[EmptyReviewClaim | HeldReviewClaim, Field(discriminator="status")]]):
    model_config = ConfigDict(strict=True, json_schema_extra=DESIGN_METADATA)


class ReviewEvidenceRef(DesignModel):
    artifact_id: Id
    sha256: Sha256


class CriterionResult(DesignModel):
    criterion_id: Id
    result: Literal["met", "unmet", "unverified"]
    reason: Reason
    evidence_refs: list[Id]


class ReviewDecision(DesignModel):
    review_handle: Text
    verdict: Literal["PASS", "REJECT"]
    reason: Reason
    evidence_refs: list[ReviewEvidenceRef]
    criterion_results: list[CriterionResult] = Field(min_length=1, max_length=CRITERIA_MAX_COUNT)

    @model_validator(mode="after")
    def consistent_verdict(self, info: ValidationInfo) -> Self:
        _unique([item.criterion_id for item in self.criterion_results], "review criterion ids")
        _unique([item.artifact_id for item in self.evidence_refs], "review evidence refs")
        statuses = {item.result for item in self.criterion_results}
        if self.verdict == "PASS" and statuses != {"met"}:
            raise ValueError("PASS requires all criterion results to be met")
        if self.verdict == "REJECT" and "unmet" not in statuses:
            raise ValueError("REJECT requires at least one unmet criterion; unavailable review must defer")
        refs = {item.artifact_id for item in self.evidence_refs}
        for item in self.criterion_results:
            if not set(item.evidence_refs) <= refs:
                raise ValueError("criterion evidence must appear in the decision evidence list")
        expected = (info.context or {}).get("criterion_ids")
        if expected is not None and set(expected) != {item.criterion_id for item in self.criterion_results}:
            raise ValueError("decision must cover exactly the fixed task criteria")
        return self


class DeferReview(DesignModel):
    review_handle: Text
    reason_code: Literal["CLIENT_INTERRUPTED", "INPUT_UNAVAILABLE", "ENVIRONMENT_UNAVAILABLE", "OTHER"]
    reason: Reason
    evidence_refs: list[Id] = Field(default_factory=list)


class EvidenceSegment(DesignModel):
    index: UInt
    artifact_id: Id
    sha256: Sha256
    size_bytes: Annotated[int, Field(ge=0, le=EVIDENCE_SEGMENT_MAX_BYTES)]


class ReviewEvidenceManifest(DesignModel):
    """D: validates metadata; actual concatenated bytes must be checked by ArtifactStore."""
    schema_version: Literal["review-evidence/1"]
    members: list[EvidenceSegment] = Field(min_length=1, max_length=EVIDENCE_SEGMENTS_MAX)
    total_size_bytes: Annotated[int, Field(ge=0, le=EVIDENCE_TOTAL_MAX_BYTES)]
    total_sha256: Sha256

    @model_validator(mode="after")
    def contiguous_complete_metadata(self) -> Self:
        if [member.index for member in self.members] != list(range(len(self.members))):
            raise ValueError("evidence segment indexes must be contiguous starting at zero")
        _unique([member.artifact_id for member in self.members], "evidence segment ids")
        if sum(member.size_bytes for member in self.members) != self.total_size_bytes:
            raise ValueError("evidence total length differs from segment lengths")
        return self


def _decode_base64(value: str, maximum: int) -> bytes:
    if len(value) > ((maximum + 2) // 3) * 4:
        raise ValueError("encoded content exceeds proposed segment limit")
    try:
        result = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ValueError("invalid base64") from error
    if len(result) > maximum:
        raise ValueError("decoded content exceeds proposed segment limit")
    return result


class EvidenceUpload(DesignModel):
    review_handle: Text
    name: Id
    kind: Text
    media_type: Text
    content_base64: str
    sha256: Sha256

    @model_validator(mode="after")
    def validate_bytes(self) -> Self:
        raw = _decode_base64(self.content_base64, EVIDENCE_SEGMENT_MAX_BYTES)
        if hashlib.sha256(raw).hexdigest() != self.sha256:
            raise ValueError("uploaded evidence digest mismatch")
        if self.kind == "review_evidence_manifest":
            ReviewEvidenceManifest.model_validate(strict_json_loads(raw), strict=True)
        return self


class EvidenceReply(DesignModel):
    artifact: ArtifactRef
    operation_id: Id
    activity_ref: Text
    meta: Meta


class RenewReviewRequest(DesignModel):
    review_handle: Text
    activity_ref: Text


class ArtifactReadQuery(DesignModel):
    offset: UInt = 0
    length: Annotated[int, Field(ge=1, le=ARTIFACT_CHUNK_MAX_BYTES)] = ARTIFACT_CHUNK_DEFAULT_BYTES


class ArtifactChunk(DesignModel):
    artifact: ArtifactRef
    offset: UInt
    length: Annotated[int, Field(ge=0, le=ARTIFACT_CHUNK_MAX_BYTES)]
    encoding: Literal["base64"]
    data: str
    eof: bool
    next_offset: UInt | None
    activity_ref: Text | None
    meta: Meta

    @model_validator(mode="after")
    def chunk_offsets(self) -> Self:
        raw = _decode_base64(self.data, ARTIFACT_CHUNK_MAX_BYTES)
        if len(raw) != self.length or self.offset + self.length > self.artifact.size_bytes:
            raise ValueError("artifact chunk length or range is invalid")
        at_end = self.offset + self.length == self.artifact.size_bytes
        if self.eof != at_end or self.next_offset != (None if self.eof else self.offset + self.length):
            raise ValueError("artifact eof/next_offset contradicts the byte range")
        return self


class InboxQuery(PageQuery):
    attention_cursor: Text | MISSING = MISSING


class InboxEvent(DesignModel):
    event_id: Id
    kind: Text
    task_id: Id | None
    operation_id: Id | None
    summary: Reason
    created_at: Time


class InboxPage(DesignModel):
    items: list[InboxEvent] = Field(max_length=PAGE_MAX)
    next_cursor: Text | None
    attention: list[Attention] = Field(max_length=PAGE_MAX)
    attention_next_cursor: Text | None
    meta: Meta


class ProjectIdentity(DesignModel):
    id: Id
    name: Text


class Principal(DesignModel):
    id: Id
    role: Role


class ServiceObservation(DesignModel):
    state: Literal["ready", "maintenance", "degraded"]
    dispatch_paused: bool


class WorkerPoolObservation(DesignModel):
    configured: bool
    eligible: UInt
    busy: UInt


class NotificationObservation(DesignModel):
    configured: bool
    verified: bool
    status: Text


class Limits(DesignModel):
    version: Id
    values: dict[str, JsonValue] = Field(description="Named support-profile values; not arbitrary service actions.")


class DifficultyLevel(DesignModel):
    level: int
    description: Reason


class DifficultyScale(DesignModel):
    id: Id
    levels: list[DifficultyLevel] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_levels(self) -> Self:
        _unique([item.level for item in self.levels], "difficulty levels")
        return self


class Context(DesignModel):
    project: ProjectIdentity
    principal: Principal
    service: ServiceObservation
    worker_pool: WorkerPoolObservation
    notification: NotificationObservation
    capabilities: list[Text]
    limits: Limits
    difficulty_scale: DifficultyScale
    recovery_policies: list[FixedRef]
    attention: list[Attention]
    meta: Meta


class ModelStatsQuery(PageQuery):
    model_id: Id | MISSING = MISSING
    difficulty_level: int | MISSING = MISSING


class UnfinishedCounts(DesignModel):
    queued: UInt
    running: UInt
    reviewing: UInt
    interrupted: UInt = Field(description="Observation subset, not a fourth additive task phase.")


class KnownUsage(DesignModel):
    input_tokens: UInt | None
    output_tokens: UInt | None
    cache_tokens: UInt | None
    reasoning_tokens: UInt | None
    coverage: Ratio
    scope: Literal["worker", "all_roles", "partial"]


class LatencyStats(DesignModel):
    sample_count: UInt
    median_seconds: Annotated[float, Field(ge=0, allow_inf_nan=False)] | None


class RoutingExplanation(DesignModel):
    mode: Literal["random", "capability"]
    reason: Reason
    policy_version: Id


class ModelStat(DesignModel):
    model_id: Id
    difficulty: DifficultySummary
    passed: UInt
    review_failed: UInt
    canceled: UInt
    unfinished: UnfinishedCounts
    completion_rate: Ratio | None
    known_usage: KnownUsage
    latency: LatencyStats
    routing: RoutingExplanation

    @model_validator(mode="after")
    def completion_denominator(self) -> Self:
        denominator = self.passed + self.review_failed
        if denominator == 0 and self.completion_rate is not None:
            raise ValueError("zero completed-review samples requires null completion_rate")
        if denominator and (self.completion_rate is None or not math.isclose(
                self.completion_rate, self.passed / denominator, rel_tol=1e-9, abs_tol=1e-12)):
            raise ValueError("completion_rate must equal S/(S+R)")
        return self


class ModelStatsPage(DesignModel):
    items: list[ModelStat] = Field(max_length=PAGE_MAX)
    next_cursor: Text | None
    meta: Meta


class WorkerArtifact(DesignModel):
    name: Id
    relative_path: RelativePath
    kind: Text
    media_type: Text


class WorkerCheck(DesignModel):
    name: Text
    status: Literal["passed", "failed", "not_run"]
    evidence_names: list[Id]


class WorkerDeliveryBase(DesignModel):
    schema_version: Literal["worker-delivery/1"]
    summary: Reason
    artifacts: list[WorkerArtifact] = Field(max_length=MANIFEST_MEMBERS_MAX)
    checks: list[WorkerCheck]
    known_limitations: list[Reason]

    @model_validator(mode="after")
    def artifact_references(self) -> Self:
        names = [artifact.name for artifact in self.artifacts]
        _unique(names, "worker artifact names")
        for check in self.checks:
            if not set(check.evidence_names) <= set(names):
                raise ValueError("worker check references an undeclared artifact")
        _json_size(self, DELIVERY_MAX_BYTES)
        return self


class CodeDeliveryObject(DesignModel):
    deliverable_key: Id
    candidate_commit: Annotated[str, StringConstraints(pattern=r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")]


class CodeWorkerDelivery(WorkerDeliveryBase):
    kind: Literal["code"]
    code: CodeDeliveryObject


class ReportWorkerDelivery(WorkerDeliveryBase):
    kind: Literal["report"]
    report_name: Id

    @model_validator(mode="after")
    def declared_report(self) -> Self:
        if self.report_name not in {artifact.name for artifact in self.artifacts}:
            raise ValueError("report_name must refer to a declared artifact")
        return self


class WorkerDelivery(RootModel[Annotated[CodeWorkerDelivery | ReportWorkerDelivery, Field(discriminator="kind")]]):
    model_config = ConfigDict(strict=True, json_schema_extra=DESIGN_METADATA)

    @model_validator(mode="after")
    def matching_task_deliverables(self, info: ValidationInfo) -> Self:
        spec = (info.context or {}).get("task_spec")
        if spec is not None:
            if not isinstance(spec, (TaskSpecInput, TaskSpec)):
                raise ValueError("task_spec validation context must contain a validated task contract")
            if self.root.kind != spec.kind:
                raise ValueError("worker delivery and task kind differ")
            names = {item.name for item in self.root.artifacts}
            if isinstance(self.root, CodeWorkerDelivery):
                code_key = next(item.key for item in spec.deliverables
                                if item.kind == "code_commit" and item.required)
                if self.root.code.deliverable_key != code_key:
                    raise ValueError("code deliverable_key differs from the required code_commit key")
            if isinstance(self.root, ReportWorkerDelivery) and self.root.report_name not in {
                    item.key for item in spec.deliverables if item.kind == "report" and item.required}:
                raise ValueError("report_name must identify a required report deliverable")
            for item in spec.deliverables:
                if item.required and item.kind in {"report", "file"} and item.key not in names:
                    raise ValueError("required task deliverable key must match artifact.name")
        return self


class ExecutionWorkspace(DesignModel):
    path: AbsolutePath
    repository_id: Id | None
    base_commit: GitOid | None

    @model_validator(mode="after")
    def paired_git_binding(self) -> Self:
        if (self.repository_id is None) != (self.base_commit is None):
            raise ValueError("workspace repository and base commit must appear together")
        return self


class ExecutionInput(DesignModel):
    schema_version: Literal["execution-input/1"]
    task_id: Id
    execution_id: Id
    launch_id: Id
    task_spec_ref: Id
    task_spec_sha256: Sha256
    resolved_inputs_ref: Id
    resolved_inputs_sha256: Sha256
    mode: Literal["initial", "revision", "resume_session", "handoff_session", "restart_same_contract"]
    candidate_ordinal: Annotated[int, Field(ge=1, le=3)]
    workspace: ExecutionWorkspace
    previous_candidate_ref: Id | None
    review_feedback_ref: Id | None
    delivery_schema_ref: Id
    delivery_target: AbsolutePath
    session_ref: Text | None

    @model_validator(mode="after")
    def session_and_revision_context(self) -> Self:
        if self.mode == "resume_session" and self.session_ref is None:
            raise ValueError("resume_session requires an exact session reference")
        if self.mode == "revision" and (self.previous_candidate_ref is None or self.review_feedback_ref is None):
            raise ValueError("revision requires the rejected candidate and feedback")
        _json_size(self, EXECUTION_INPUT_MAX_BYTES)
        return self


class Readiness(DesignModel):
    state: Literal["ready", "unavailable", "unknown"]
    reasons: list[Attention]
    observed_at: Time


class RepositoryDefinition(DesignModel):
    source_id: Id
    path: AbsolutePath
    review_export: Literal["reachable_history"]


class InputRoot(DesignModel):
    id: Id
    path: AbsolutePath


class ProjectDefinition(DesignModel):
    name: Text
    repository: RepositoryDefinition | None
    input_roots: list[InputRoot]
    default_requirements: Requirements
    recovery_policy_ref: FixedRef | None
    shared_resource_registry: list[SharedResourceDefinition]
    content_retention: ContentRetention = Field(default_factory=lambda: ContentRetention(
        final_seconds=None, rejected_seconds=None, logs_workspace_seconds=None))

    @model_validator(mode="after")
    def unique_registry_entries(self) -> Self:
        _unique([item.id for item in self.input_roots], "input root ids")
        _unique([item.resource_id for item in self.shared_resource_registry], "shared resource ids")
        return self


class ProjectUpdate(ProjectDefinition):
    expected_version: UInt


class ProjectView(ProjectDefinition):
    content_retention: ContentRetention
    id: Id
    version: PositiveInt
    repository_identity: Text | None
    readiness: Readiness


class PrivateValueSource(DesignModel):
    kind: Literal["private_value"]
    value: Text = Field(repr=False, json_schema_extra={"writeOnly": True})


class OwnerFileSource(DesignModel):
    kind: Literal["owner_file"]
    path: AbsolutePath


class CredentialSourceUpdate(DesignModel):
    expected_version: UInt
    purpose: Literal["provider", "mcp", "notification"]
    source: Annotated[PrivateValueSource | OwnerFileSource, Field(discriminator="kind")]
    label: Text


class CredentialSourceView(DesignModel):
    id: Id
    version: PositiveInt
    purpose: Literal["provider", "mcp", "notification"]
    label: Text
    source_kind: Literal["private_value", "owner_file"]
    status: Literal["configured", "missing", "unreadable"]
    changed_at: Time


class ModelParameter(DesignModel):
    name: Text
    value: str | int | FiniteNumber | bool | None


class ExecutionConfiguration(DesignModel):
    relay_url: Text
    credential_source_id: Id
    model_id: Id
    parameters: list[ModelParameter]
    native_template_ref: FixedRef
    base_resources: ResourceVector

    @model_validator(mode="after")
    def unique_parameter_names(self) -> Self:
        _unique([item.name for item in self.parameters], "model parameter names")
        return self


AdmissionMode = Literal["enabled", "draining", "disabled"]


class WorkerUpdate(DesignModel):
    expected_version: UInt
    admission_mode: AdmissionMode
    retire_requested: bool
    configuration: ExecutionConfiguration


class WorkerView(DesignModel):
    id: Id
    admission_mode: AdmissionMode
    retire_requested: bool
    retired: bool
    configuration: ExecutionConfiguration
    slot_version: PositiveInt
    config_id: Id
    effective_config_observation: dict[str, JsonValue]
    occupied_by: Id | None
    bound_unfinished_tasks: list[Id]
    readiness: Readiness


class DispatchScope(DesignModel):
    kind: Literal["instance", "project"]
    project_id: Id | None

    @model_validator(mode="after")
    def project_scope_id(self) -> Self:
        if (self.kind == "project") != (self.project_id is not None):
            raise ValueError("only project scope has a project_id")
        return self


class DispatchUpdate(DesignModel):
    expected_version: UInt
    scope: DispatchScope
    paused: bool
    reason: Reason | MISSING = MISSING


class RoleBindingUpdate(DesignModel):
    expected_version: UInt
    enabled: bool
    root_ref: Text | None


class BindingView(DesignModel):
    role: Role
    root_ref: Text | None
    principal_id: Id
    version: PositiveInt
    grant_epoch: UInt
    root_epoch: UInt
    enabled: bool
    credential_source_ref: Text
    notification_observation: NotificationObservation


class WorkerCheckRequest(DesignModel):
    config_id: Id
    kind: Literal["static"]


class CatalogMember(DesignModel):
    relative_path: RelativePath
    sha256: Sha256


class CatalogContent(DesignModel):
    source_root_id: Id
    members: list[CatalogMember] = Field(min_length=1, max_length=MANIFEST_MEMBERS_MAX)
    description: Reason

    @model_validator(mode="after")
    def distinct_members(self) -> Self:
        _unique([item.relative_path for item in self.members], "catalog member paths")
        return self


class NativeTemplateDefinition(CatalogContent):
    settings_entry: RelativePath

    @model_validator(mode="after")
    def settings_member(self) -> Self:
        if self.settings_entry not in {item.relative_path for item in self.members}:
            raise ValueError("native settings entry must be a declared member")
        return self


class ToolDefinition(CatalogContent):
    entrypoint: RelativePath | None

    @model_validator(mode="after")
    def entrypoint_member(self) -> Self:
        if self.entrypoint is not None and self.entrypoint not in {item.relative_path for item in self.members}:
            raise ValueError("tool entrypoint must be a declared member")
        return self


class ExecutableDefinition(DesignModel):
    path: AbsolutePath
    sha256: Sha256


class EnvironmentCredentialRef(DesignModel):
    name: Text
    credential_source_id: Id


class StdioMCPDefinition(DesignModel):
    transport: Literal["stdio"]
    executable: ExecutableDefinition
    args: list[str]
    environment_refs: list[EnvironmentCredentialRef]
    tool_refs: list[FixedRef]
    description: Reason


class HttpMCPDefinition(DesignModel):
    transport: Literal["http"]
    url: Text
    credential_source_id: Id | None
    description: Reason


class ExecutionRecoveryPolicy(DesignModel):
    automatic_attempts: UInt
    total_elapsed_seconds: UInt
    execution_timeout_seconds: PositiveInt
    backoff_seconds: list[PositiveInt]

    @model_validator(mode="after")
    def bounded_attempts(self) -> Self:
        if len(self.backoff_seconds) != self.automatic_attempts:
            raise ValueError("one backoff is required per automatic execution recovery")
        if self.automatic_attempts and self.total_elapsed_seconds == 0:
            raise ValueError("automatic recovery requires a positive total time bound")
        return self


class ReviewRecoveryPolicy(DesignModel):
    automatic_reclaims: UInt
    total_elapsed_seconds: UInt
    backoff_seconds: list[PositiveInt]

    @model_validator(mode="after")
    def bounded_reclaims(self) -> Self:
        if len(self.backoff_seconds) != self.automatic_reclaims:
            raise ValueError("one backoff is required per automatic review reopening")
        if self.automatic_reclaims and self.total_elapsed_seconds == 0:
            raise ValueError("automatic review reopening requires a positive total time bound")
        return self


class RecoveryPolicyDefinition(DesignModel):
    execution: ExecutionRecoveryPolicy
    review: ReviewRecoveryPolicy
    check_timeout_seconds: PositiveInt


CatalogKind = Literal["native-template", "tool", "mcp", "recovery-policy"]
CatalogDefinition = NativeTemplateDefinition | ToolDefinition | StdioMCPDefinition | HttpMCPDefinition | RecoveryPolicyDefinition
CATALOG_TYPES: dict[str, tuple[type[BaseModel], ...]] = {
    "native-template": (NativeTemplateDefinition,), "tool": (ToolDefinition,),
    "mcp": (StdioMCPDefinition, HttpMCPDefinition), "recovery-policy": (RecoveryPolicyDefinition,),
}


class CatalogUpdate(DesignModel):
    expected_version: UInt
    definition: CatalogDefinition

    @model_validator(mode="after")
    def route_kind_matches(self, info: ValidationInfo) -> Self:
        kind = (info.context or {}).get("catalog_kind")
        if kind is not None and (kind not in CATALOG_TYPES or not isinstance(self.definition, CATALOG_TYPES[kind])):
            raise ValueError("catalog definition does not match the route kind")
        return self


class CatalogView(DesignModel):
    kind: CatalogKind
    id: Id
    version: PositiveInt
    content_sha256: Sha256
    readiness: Readiness
    definition: CatalogDefinition

    @model_validator(mode="after")
    def declared_catalog_kind(self) -> Self:
        if not isinstance(self.definition, CATALOG_TYPES[self.kind]):
            raise ValueError("catalog definition kind mismatch")
        return self


class ResourceOverrideUpdate(DesignModel):
    expected_version: UInt
    resources: ResourceVector
    reason: Reason


class ArtifactKeepUpdate(DesignModel):
    expected_version: UInt
    keep: bool
    reason: Reason


class SessionCreate(DesignModel):
    credential: Text = Field(repr=False, json_schema_extra={"writeOnly": True})


class SessionIdentity(DesignModel):
    principal_id: Id
    expires_at: Time


class SessionReply(DesignModel):
    session: SessionIdentity
    csrf_token: Text
    meta: Meta


class HealthReply(DesignModel):
    status: Literal["alive"]
    release_id: Id
    api_version: Literal["1"]


class SubmitTaskResult(DesignModel):
    task_id: Id


class ResumeTaskResult(DesignModel):
    task_id: Id
    recovery_id: Id
    execution_id: Id | None
    review_reopened: bool


class CancelTaskResult(DesignModel):
    task_id: Id
    canceled: bool


class SubmitReviewResult(DesignModel):
    review_id: Id
    candidate_id: Id
    verdict: Literal["PASS", "REJECT"]
    task_status: TaskStatus
    outcome: Outcome | None
    rejections: Annotated[int, Field(ge=0, le=3)]
    committed_task_version: UInt

    @model_validator(mode="after")
    def committed_review_result(self) -> Self:
        if self.verdict == "PASS":
            valid = self.task_status == "finished" and self.outcome == "passed" and self.rejections < 3
        elif self.rejections == 3:
            valid = self.task_status == "finished" and self.outcome == "review_failed"
        else:
            valid = self.task_status == "queued" and self.outcome is None and self.rejections in (1, 2)
        if not valid:
            raise ValueError("committed review result violates the task terminal rules")
        return self


class DeferReviewResult(DesignModel):
    candidate_id: Id
    deferred: Literal[True]

    @model_validator(mode="before")
    @classmethod
    def strict_true(cls, value: Any) -> Any:
        # Pydantic's Literal[True] otherwise accepts integer 1 even in strict mode.
        if isinstance(value, dict) and "deferred" in value and value["deferred"] is not True:
            raise ValueError("deferred must be the JSON boolean true")
        return value


class NextReviewResult(DesignModel):
    claim: ReviewClaim


class UploadReviewEvidenceResult(DesignModel):
    artifact: ArtifactRef
    activity_ref: Text | None


class RenewReviewResult(DesignModel):
    candidate_id: Id
    lease_expires_at: Time
    max_hold_until: Time


class ProjectImpact(DesignModel):
    future_tasks: bool
    bound_tasks: bool


class SaveProjectResult(DesignModel):
    resource_id: Id
    version: PositiveInt
    impact: ProjectImpact


class SaveWorkerResult(DesignModel):
    config_id: Id
    slot_version: PositiveInt
    affected_tasks: list[Id]
    attention: list[Attention]


class DispatchResult(DesignModel):
    user_paused: bool
    effective_paused: bool
    blocking_reasons: list[Attention]
    version: UInt


class RoleBindingResult(DesignModel):
    principal_id: Id
    version: PositiveInt
    grant_epoch: UInt
    root_epoch: UInt
    connection_alias: Text
    credential_source_ref: Text
    enabled: bool


class CheckResult(DesignModel):
    name: Text
    status: Literal["pass", "fail", "unknown"]
    reason: Reason


class WorkerCheckResult(DesignModel):
    config_id: Id
    checked_at: Time
    checks: list[CheckResult]


class SaveCatalogResult(DesignModel):
    kind: CatalogKind
    id: Id
    version: PositiveInt
    content_sha256: Sha256
    readiness: Readiness


class ResourceOverrideResult(DesignModel):
    task_id: Id
    override_id: Id
    version: PositiveInt
    effective_from: Literal["next_execution"]
    resources: ResourceVector


class ArtifactKeepResult(DesignModel):
    artifact_id: Id
    explicit_keep: bool
    version: UInt
    availability: Literal["available", "retiring", "missing", "corrupt", "expired"]
    expires_at: Time | None


OperationKind = Literal["submit_task", "resume_task", "cancel_task", "next_review", "submit_review", "defer_review",
                        "upload_review_evidence", "renew_review", "save_project", "save_credential_source",
                        "save_worker", "set_dispatch", "set_role_binding", "check_worker", "save_catalog",
                        "set_task_resources", "set_artifact_keep"]
OperationResult = (SubmitTaskResult | ResumeTaskResult | CancelTaskResult | NextReviewResult | SubmitReviewResult |
                   DeferReviewResult | UploadReviewEvidenceResult | RenewReviewResult | SaveProjectResult |
                   CredentialSourceView | SaveWorkerResult | DispatchResult | RoleBindingResult | WorkerCheckResult |
                   SaveCatalogResult | ResourceOverrideResult | ArtifactKeepResult)
OPERATION_RESULT_TYPES: dict[str, type[BaseModel]] = {
    "submit_task": SubmitTaskResult, "resume_task": ResumeTaskResult, "cancel_task": CancelTaskResult,
    "next_review": NextReviewResult, "submit_review": SubmitReviewResult, "defer_review": DeferReviewResult,
    "upload_review_evidence": UploadReviewEvidenceResult, "renew_review": RenewReviewResult,
    "save_project": SaveProjectResult, "save_credential_source": CredentialSourceView, "save_worker": SaveWorkerResult,
    "set_dispatch": DispatchResult, "set_role_binding": RoleBindingResult, "check_worker": WorkerCheckResult,
    "save_catalog": SaveCatalogResult, "set_task_resources": ResourceOverrideResult, "set_artifact_keep": ArtifactKeepResult,
}


class OperationScope(DesignModel):
    project_id: Id | None


class ResourceRef(DesignModel):
    kind: Text
    id: Id


class Operation(DesignModel):
    operation_id: Id
    kind: OperationKind
    scope: OperationScope
    request_key: RequestKey
    phase: Literal["accepted", "completed", "waiting", "failed"]
    version: UInt
    created_at: Time
    updated_at: Time
    resource_refs: list[ResourceRef]
    result: OperationResult | None
    attention: list[Attention]
    problem: Problem | None

    @model_validator(mode="after")
    def fixed_result_type(self) -> Self:
        if self.result is not None and not isinstance(self.result, OPERATION_RESULT_TYPES[self.kind]):
            raise ValueError("operation result does not match its fixed kind")
        if self.phase == "completed" and self.result is None:
            raise ValueError("completed operation requires its committed result")
        return self


class CommandReply(DesignModel):
    operation: Operation
    meta: Meta


class OperationSummary(DesignModel):
    operation_id: Id
    kind: OperationKind
    phase: Literal["accepted", "completed", "waiting", "failed"]
    version: UInt
    updated_at: Time


class AdminServiceView(DesignModel):
    release_id: Id
    state: Text
    dispatch: DispatchResult
    maintenance: dict[str, JsonValue] = Field(description="Maintenance observation; V1 lifecycle schema is separately staged.")
    operations: list[OperationSummary]


class AdminSnapshot(DesignModel):
    service: AdminServiceView
    projects: list[ProjectView]
    workers: list[WorkerView]
    credential_sources: list[CredentialSourceView]
    role_bindings: list[BindingView]
    catalog: list[CatalogView]
    limits: Limits
    csrf_token: Text
    meta: Meta


# Every named design model is available to schema generation; generic typing
# aliases are represented by the named enclosing models. No production registry.
MODEL_REGISTRY: dict[str, type[BaseModel]] = {
    name: value for name, value in list(globals().items())
    if isinstance(value, type) and issubclass(value, BaseModel)
    and value.__module__ == __name__ and value is not DesignModel
}
REGISTRY = MODEL_REGISTRY

