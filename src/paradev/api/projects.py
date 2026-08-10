"""Transport-neutral project authoring operations shared by app surfaces."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from paradev.api._requests import (
    bool_value,
    module_create_batch_requests,
    optional_string,
    request_text,
    required_string,
    scalar_values,
    validate_request_fields,
)
from paradev.sdk.project import Project, open_project, registered_projects

_SOURCE_FORM_REQUEST_FIELDS = frozenset({"project_root", "path", "text", "query"})
_SOURCE_FORM_UPDATE_BATCH_REQUEST_FIELDS = frozenset({"project_root", "updates"})
_SOURCE_FORM_UPDATE_FIELDS = frozenset({"source_path", "values", "text", "query"})
_LOCALIZATION_WORKSPACE_REQUEST_FIELDS = frozenset(
    {
        "project_root",
        "target_kind",
        "target_id",
        "family",
        "source_root",
        "drafts",
        "limit",
    }
)
_LOCALIZATION_UPDATE_REQUEST_FIELDS = _LOCALIZATION_WORKSPACE_REQUEST_FIELDS | {"operation"}
_LOCALIZATION_DRAFT_FIELDS = frozenset({"source_path", "text"})
_MODULE_CREATE_BATCH_REQUEST_FIELDS = frozenset(
    {
        "project_id",
        "project_root",
        "modules",
        "source_root",
        "write",
        "plan_hash",
    }
)

__all__ = [
    "apply_project_draft",
    "create_module_batch",
    "create_module_draft",
    "normalize_project_draft_mutations",
    "plan_project_localization_update",
    "plan_project_source_form_updates",
    "read_project_localization_workspace",
    "read_project_source_form",
    "read_project_source_text",
]


def apply_project_draft(*, project_id: str, request: Mapping[str, object]) -> dict[str, object]:
    """Apply project draft edits after validating every target path.

    Args:
        project_id: Project id selected by the calling interface.
        request: Request with optional project root and source mutations.

    Returns:
        JSON-safe apply payload with written file rows.

    Raises:
        ValueError: If the project or draft request is invalid.
        OSError: If the guarded source transaction cannot complete.
    """

    unknown_fields = sorted(
        set(request)
        - {
            "project_root",
            "source_edits",
            "source_removals",
            "source_replacements",
            "module_rename",
        }
    )
    if unknown_fields:
        raise ValueError("Draft apply request contains unsupported fields: " f"{', '.join(unknown_fields)}.")
    project = _project(project_id, optional_string(request.get("project_root"), "project_root"))
    return project.apply_source_draft(
        source_edits=request.get("source_edits"),
        source_removals=request.get("source_removals"),
        source_replacements=request.get("source_replacements"),
        module_rename=request.get("module_rename"),
    )


def create_module_batch(*, request: Mapping[str, object]) -> dict[str, object]:
    """Plan or atomically create several modules through one SDK transaction.

    Args:
        request: Request with project identity, module rows, and optional plan
            or apply fields.

    Returns:
        JSON-safe SDK module batch plan or apply payload.

    Raises:
        ValueError: If the project identity or module batch is invalid.
        OSError: If guarded module creation cannot complete.
    """

    validate_request_fields(request, _MODULE_CREATE_BATCH_REQUEST_FIELDS, "module create-batch request")
    project_id = required_string(request.get("project_id"), "project_id")
    project_root = optional_string(request.get("project_root"), "project_root")
    project = _project(project_id, project_root)
    return project.create_modules(
        module_create_batch_requests(request.get("modules")),
        source_root=optional_string(request.get("source_root"), "source_root"),
        write=bool_value(request.get("write", False), "write"),
        plan_hash=optional_string(request.get("plan_hash"), "plan_hash"),
    )


def create_module_draft(
    *,
    project_id: str,
    family_id: str,
    request: Mapping[str, object],
) -> dict[str, object]:
    """Plan or write a module draft through the SDK scaffold contract.

    Args:
        project_id: Project id selected by the calling interface.
        family_id: Browser family id, such as ``ideas``.
        request: Request with object id, optional project/template identity,
            scalar values, and write flags.

    Returns:
        JSON-safe module draft payload containing the SDK scaffold plan.

    Raises:
        ValueError: If the project, family, request, or template is invalid.
        OSError: If scaffold planning or writing cannot complete.
    """

    project = _project(project_id, optional_string(request.get("project_root"), "project_root"))
    return project.create_module_draft(
        family_id,
        required_string(request.get("object_id"), "object_id"),
        template_id=optional_string(request.get("template_id"), "template_id"),
        values=scalar_values(request.get("values")),
        write=bool_value(request.get("write", False), "write"),
        force=bool_value(request.get("force", False), "force"),
    )


def normalize_project_draft_mutations(
    *,
    source_edits: object = None,
    source_removals: object = None,
    source_replacements: object = None,
    module_rename: object = None,
    allow_snake_case: bool = True,
    label: str = "project draft",
) -> dict[str, object]:
    """Normalize draft mutation aliases into the SDK's snake-case shape.

    Args:
        source_edits: Optional text-edit rows.
        source_removals: Optional removal paths or guarded removal rows.
        source_replacements: Optional binary-replacement rows.
        module_rename: Optional canonical module-folder rename.
        allow_snake_case: Whether SDK-style field names are accepted with
            desktop camel-case aliases.
        label: Human-readable request label used in validation errors.

    Returns:
        JSON-safe mutation mapping accepted by ``Project.apply_source_draft``.

    Raises:
        ValueError: If an item, alias pair, or rename has an invalid shape.
    """

    edit_label = f"{label} sourceEdits" if not allow_snake_case else f"{label} source edits"
    removal_label = f"{label} sourceRemovals" if not allow_snake_case else f"{label} source removals"
    replacement_label = f"{label} sourceReplacements" if not allow_snake_case else f"{label} source replacements"
    edits = _normalize_project_draft_items(
        source_edits,
        aliases={
            "path": "path",
            "text": "text",
            "expectedSize": "expected_size",
            "expectedMtimeNs": "expected_mtime_ns",
        },
        label=edit_label,
        item_label=f"{label} source edit",
        allow_snake_case=allow_snake_case,
    )
    removals = _normalize_project_draft_items(
        source_removals,
        aliases={
            "path": "path",
            "expectedSize": "expected_size",
            "expectedMtimeNs": "expected_mtime_ns",
        },
        label=removal_label,
        item_label=f"{label} source removal",
        allow_snake_case=allow_snake_case,
    )
    replacements = _normalize_project_draft_items(
        source_replacements,
        aliases={
            "path": "path",
            "contentBase64": "content_base64",
            "contentFormat": "content_format",
            "targetFormat": "target_format",
            "expectedSize": "expected_size",
            "expectedMtimeNs": "expected_mtime_ns",
            "expectedAbsent": "expected_absent",
        },
        label=replacement_label,
        item_label=f"{label} source replacement",
        allow_snake_case=allow_snake_case,
    )
    rename = _normalize_project_draft_module_rename(
        module_rename,
        allow_snake_case=allow_snake_case,
        label=label,
    )
    normalized: dict[str, object] = {
        "source_edits": edits,
        "source_removals": removals,
        "source_replacements": replacements,
    }
    if rename is not None:
        normalized["module_rename"] = rename
    return normalized


def plan_project_localization_update(
    *,
    project_id: str,
    request: Mapping[str, object],
) -> dict[str, object]:
    """Plan one Registry-owned localization operation without writing.

    Args:
        project_id: Project id selected by the calling interface.
        request: Localization workspace request plus one closed operation.

    Returns:
        JSON-safe update plan accepted by :func:`apply_project_draft`.

    Raises:
        ValueError: If identity, ownership, drafts, or operation is invalid.
        OSError: If a stable source snapshot cannot be read.
    """

    validate_request_fields(request, _LOCALIZATION_UPDATE_REQUEST_FIELDS, "project localization update request")
    operation = request.get("operation")
    if not isinstance(operation, Mapping):
        raise ValueError("Request field 'operation' must be an object.")
    project, target_kind, target_id, family, source_root, drafts, limit = _localization_request(
        project_id,
        request,
    )
    return project.plan_localization_update(
        target_id,
        operation,
        target_kind=target_kind,
        family=family,
        source_root=source_root,
        drafts=drafts,
        limit=limit,
    )


def plan_project_source_form_updates(
    *,
    project_id: str,
    request: Mapping[str, object],
) -> dict[str, object]:
    """Plan several guided source updates without writing project files.

    Args:
        project_id: Project id selected by the calling interface.
        request: Request containing optional project root and update rows.

    Returns:
        JSON-safe Registry-owned source update plan.

    Raises:
        ValueError: If the project, request, source, or controls are invalid.
        OSError: If a stable source snapshot cannot be read.
    """

    validate_request_fields(
        request,
        _SOURCE_FORM_UPDATE_BATCH_REQUEST_FIELDS,
        "project source-form update-batch request",
    )
    project_root = optional_string(request.get("project_root"), "project_root")
    updates = request.get("updates")
    if not isinstance(updates, list):
        raise ValueError("Request field 'updates' must be an array.")
    planned_updates: list[dict[str, object]] = []
    for index, update in enumerate(updates):
        if not isinstance(update, Mapping):
            raise ValueError(f"Request field 'updates[{index}]' must be an object.")
        validate_request_fields(update, _SOURCE_FORM_UPDATE_FIELDS, f"project source-form update row {index}")
        source_path = request_text(update, "source_path")
        values = update.get("values")
        if not isinstance(values, Mapping):
            raise ValueError(f"Request field 'updates[{index}].values' must be an object.")
        text = update.get("text")
        if text is not None and not isinstance(text, str):
            raise ValueError(f"Request field 'updates[{index}].text' must be a string.")
        query = update.get("query")
        if query is not None and not isinstance(query, str):
            raise ValueError(f"Request field 'updates[{index}].query' must be a string.")
        planned_updates.append(
            {
                "source_path": source_path,
                "values": values,
                **({"text": text} if text is not None else {}),
                **({"query": query} if query is not None else {}),
            }
        )
    return _project(project_id, project_root).plan_source_form_updates(planned_updates)


def read_project_localization_workspace(
    *,
    project_id: str,
    request: Mapping[str, object],
) -> dict[str, object]:
    """Return one Registry-owned source-unit localization workspace.

    Args:
        project_id: Project id selected by the calling interface.
        request: Request containing target identity and optional projections.

    Returns:
        JSON-safe cross-language workspace with stable source revisions.

    Raises:
        ValueError: If identity, ownership, drafts, or row limit is invalid.
        OSError: If a stable source snapshot cannot be read.
    """

    validate_request_fields(
        request,
        _LOCALIZATION_WORKSPACE_REQUEST_FIELDS,
        "project localization workspace request",
    )
    project, target_kind, target_id, family, source_root, drafts, limit = _localization_request(
        project_id,
        request,
    )
    return project.localization_workspace(
        target_id,
        target_kind=target_kind,
        family=family,
        source_root=source_root,
        drafts=drafts,
        limit=limit,
    )


def read_project_source_form(
    *,
    project_id: str,
    request: Mapping[str, object],
) -> dict[str, object] | None:
    """Return an optional Registry-owned form for current JSON or PDX text.

    Args:
        project_id: Project id selected by the calling interface.
        request: Request with source path, current text, and optional query.

    Returns:
        Validated source-form payload, or ``None`` when unavailable.

    Raises:
        ValueError: If the project, request, source, or query is invalid.
        OSError: If a stable source snapshot cannot be read.
    """

    validate_request_fields(request, _SOURCE_FORM_REQUEST_FIELDS, "project source form request")
    source_path = request_text(request, "path")
    project_root = optional_string(request.get("project_root"), "project_root")
    text = request.get("text")
    if not isinstance(text, str):
        raise ValueError("Request field 'text' must be a string.")
    query = request.get("query")
    if query is not None and not isinstance(query, str):
        raise ValueError("Request field 'query' must be a string.")
    return _project(project_id, project_root).source_form(
        source_path,
        text=text,
        **({"query": query} if query is not None else {}),
    )


def read_project_source_text(
    *,
    project_id: str,
    source_path: str,
    project_root: str | None = None,
) -> dict[str, object]:
    """Read one project source file as UTF-8 text.

    Args:
        project_id: Project id selected by the calling interface.
        source_path: Absolute or project-relative source path.
        project_root: Optional explicit project root.

    Returns:
        JSON-safe source text payload.

    Raises:
        ValueError: If project identity or source path is invalid.
        OSError: If a stable source snapshot cannot be read.
    """

    return _project(project_id, project_root).read_source_text(source_path)


def _localization_drafts(value: object) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise ValueError("Request field 'drafts' must be an array.")
    drafts: dict[str, str] = {}
    for index, row in enumerate(value):
        if not isinstance(row, Mapping):
            raise ValueError(f"Request field 'drafts[{index}]' must be an object.")
        validate_request_fields(row, _LOCALIZATION_DRAFT_FIELDS, f"project localization draft {index}")
        source_path = request_text(row, "source_path")
        text = row.get("text")
        if not isinstance(text, str):
            raise ValueError(f"Request field 'drafts[{index}].text' must be a string.")
        if source_path in drafts:
            raise ValueError(f"Request field 'drafts' repeats source path {source_path!r}.")
        drafts[source_path] = text
    return drafts


def _localization_request(
    project_id: str,
    request: Mapping[str, object],
) -> tuple[Project, str, str, str | None, str | None, dict[str, str] | None, int]:
    project_root = optional_string(request.get("project_root"), "project_root")
    target_kind = required_string(request.get("target_kind"), "target_kind")
    if target_kind not in {"module", "collection"}:
        raise ValueError("Request field 'target_kind' must be 'module' or 'collection'.")
    target_id = required_string(request.get("target_id"), "target_id")
    family = optional_string(request.get("family"), "family")
    source_root = optional_string(request.get("source_root"), "source_root")
    limit = request.get("limit", 512)
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValueError("Request field 'limit' must be an integer.")
    return (
        _project(project_id, project_root),
        target_kind,
        target_id,
        family,
        source_root,
        _localization_drafts(request.get("drafts")),
        limit,
    )


def _normalize_project_draft_items(
    value: object,
    *,
    aliases: Mapping[str, str],
    label: str,
    item_label: str,
    allow_snake_case: bool,
) -> list[object] | None:
    if value is None:
        return None
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise ValueError(f"{label} must be a JSON array.")
    allowed = set(aliases)
    if allow_snake_case:
        allowed.update(aliases.values())
    normalized: list[object] = []
    for item in value:
        if not isinstance(item, Mapping):
            normalized.append(item)
            continue
        unknown = sorted(repr(key) for key in item if not isinstance(key, str) or key not in allowed)
        if unknown:
            raise ValueError(f"{item_label} contains unsupported fields: {', '.join(unknown)}.")
        planned: dict[str, object] = {}
        for source_name, target_name in aliases.items():
            has_source = source_name in item
            has_target = allow_snake_case and target_name in item
            if source_name != target_name and has_source and has_target:
                raise ValueError(f"{item_label} cannot provide both " f"{source_name!r} and {target_name!r}.")
            if has_source:
                planned[target_name] = item[source_name]
            elif has_target:
                planned[target_name] = item[target_name]
        normalized.append(planned)
    return normalized


def _normalize_project_draft_module_rename(
    value: object,
    *,
    allow_snake_case: bool,
    label: str,
) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} module rename must be a JSON object.")
    aliases = {
        "moduleId": "module_id",
        "objectId": "object_id",
        "sourceRoot": "source_root",
        "title": "title",
    }
    allowed = set(aliases)
    if allow_snake_case:
        allowed.update(aliases.values())
    unknown = sorted(repr(key) for key in value if not isinstance(key, str) or key not in allowed)
    if unknown:
        raise ValueError(f"{label} module rename contains unsupported fields: {', '.join(unknown)}.")
    normalized: dict[str, object] = {}
    for source_name, target_name in aliases.items():
        has_source = source_name in value
        has_target = allow_snake_case and target_name in value
        if source_name != target_name and has_source and has_target:
            raise ValueError(f"{label} module rename cannot provide both " f"{source_name!r} and {target_name!r}.")
        if has_source:
            normalized[target_name] = value[source_name]
        elif has_target:
            normalized[target_name] = value[target_name]
    return normalized


def _project(project_id: str, project_root: str | None) -> Project:
    if project_root:
        project = open_project(project_root)
        if project.project_id != project_id:
            raise ValueError(f"Project root {project_root!r} loaded project {project.project_id!r}, not {project_id!r}.")
        return project
    registry = registered_projects()
    projects = registry.get("projects", ())
    if isinstance(projects, list):
        for row in projects:
            if isinstance(row, dict) and row.get("project_id") == project_id and isinstance(row.get("root"), str):
                return open_project(row["root"])
    raise ValueError(f"Unknown project id: {project_id}")
