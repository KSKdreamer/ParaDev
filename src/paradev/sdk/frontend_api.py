"""Frontend-facing API capability contract."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import NoReturn
from urllib.parse import quote

from heavenbase.utils import dumps_json
from typing_extensions import TypedDict

from paradev._api_table import (
    api_value_indexes,
    append_api_index_entry,
    append_api_nested_index_entry,
    append_index_entry,
)
from paradev._api_table_markdown import api_table_lines as _frontend_api_table_lines
from paradev._api_table_markdown import api_table_section as _frontend_api_table_section
from paradev._api_table_markdown import code_cell as _code_cell
from paradev._api_table_markdown import code_list_cell
from paradev._api_table_markdown import markdown_cell as _markdown_cell
from paradev._api_table_markdown import table_rows as _frontend_api_table_rows
from paradev._catalog import (
    CATALOG_QUERY_DEFAULT_INCLUDE_DATA,
    CATALOG_QUERY_DEFAULT_LIMIT,
    CATALOG_QUERY_MAX_LIMIT,
    normalize_catalog_query_filters,
)

from ._module_diagram_api import (
    MAX_MODULE_DIAGRAM_EDGE_INTENTS,
    MAX_MODULE_DIAGRAM_NODE_INTENTS,
    MAX_MODULE_DIAGRAM_POSITION_INTENTS,
)
from .project import Project, get_project_inspection_contract, open_project


class _FrontendApiOptionProviderRecord(TypedDict):
    consumer_fields: list[str]
    consumers: set[str]
    paths: set[str]
    requires: set[str]
    forward: set[str]
    filters: set[str]


_FrontendApiDetailRecord = tuple[str, Mapping[str, object], Mapping[str, object]]
_FrontendApiDetailCellBuilder = Callable[
    [str, Mapping[str, object], Mapping[str, object]],
    list[str],
]
_FrontendApiBindingInputRecord = tuple[
    dict[str, object],
    Mapping[str, object],
    Mapping[str, object],
]
_FrontendApiInputRecord = tuple[dict[str, object], Mapping[str, object]]
_FrontendApiOwnerOperationRecord = tuple[dict[str, object], list[dict[str, object]]]
_FrontendApiOwnerActionRecord = tuple[
    dict[str, object],
    list[dict[str, object]],
    list[dict[str, object]],
]
_FrontendApiRestOperationRecord = tuple[dict[str, object], Mapping[str, object]]
_FrontendApiRestQueryBodyContext = tuple[dict[str, object], dict[str, object], set[str], set[str]]
_FrontendApiOptionProviderInputs = tuple[Project, Mapping[str, object]]
_FrontendApiActionGroupMap = dict[str, list[dict[str, object]]]
_FrontendApiWorkspaceActionGroups = tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    _FrontendApiActionGroupMap,
]
_FrontendApiSummaryDeltaPair = tuple[int, int]
_FrontendApiSummaryDeltaTriple = tuple[int, int, int]
_FrontendApiSummaryDeltaQuad = tuple[int, int, int, int]
_FrontendApiCountMap = dict[str, int]
_FrontendApiGroupCountMap = dict[str, _FrontendApiCountMap]
_FrontendApiInputBuckets = dict[str, dict[str, object]]
_FrontendApiConfirmationCounts = tuple[
    list[str],
    _FrontendApiCountMap,
    _FrontendApiCountMap,
    _FrontendApiCountMap,
]
_FrontendApiStaticSummaryCellBuilder = Callable[[Mapping[str, object]], Sequence[str]]
_FrontendApiOwnerSummaryCellBuilder = Callable[[object, Sequence[Mapping[str, object]]], Sequence[str]]
_FrontendApiOwnerDetailCellBuilder = Callable[[Mapping[str, object], Sequence[Mapping[str, object]]], Sequence[str]]
_FrontendApiOwnerActionCellBuilder = Callable[
    [object, Sequence[Mapping[str, object]], Sequence[Mapping[str, object]]],
    Sequence[str],
]
_FrontendApiInputCellBuilder = Callable[[Mapping[str, object], Mapping[str, object]], Sequence[str]]
_FrontendApiInputPredicate = Callable[[Mapping[str, object]], bool]
_FrontendApiOperationCellBuilder = Callable[[Mapping[str, object]], Sequence[str]]


_FRONTEND_API_REFERENCE_TABLE_LABELS = (
    "Operation",
    "Group",
    "Status",
    "Mode",
    "SDK",
    "CLI",
    "REST",
    "MCP",
    "LSP",
    "Inputs",
    "Payload",
    "Summary",
)
_FRONTEND_API_SDK_CLI_TABLE_LABELS = (
    "Operation",
    "Group",
    "Mode",
    "Python SDK",
    "CLI",
    "Inputs",
    "Summary",
)
_FRONTEND_API_INPUT_BUCKET_NAMES = ("project", "parameters", "selectors", "projections")
FRONTEND_API_SCHEMA = "paradev.sdk.frontend-api.v1"
FRONTEND_API_ACTION_DETAIL_SCHEMA = "paradev.sdk.frontend-api.action-detail.v1"
FRONTEND_API_ACTION_SCHEMA = "paradev.sdk.frontend-api.action.v1"
FRONTEND_API_BINDING_LOOKUP_SCHEMA = "paradev.sdk.frontend-api.binding-lookup.v1"
FRONTEND_API_CONFIRMATION_SCHEMA = "paradev.sdk.frontend-api.confirmation.v1"
FRONTEND_API_FORM_SCHEMA = "paradev.sdk.frontend-api.form.v1"
FRONTEND_API_INPUTS_SCHEMA = "paradev.sdk.frontend-api.inputs.v1"
FRONTEND_API_OPTIONS_SCHEMA = "paradev.sdk.frontend-api.options.v1"
FRONTEND_API_OPTION_SOURCE_SCHEMA = "paradev.sdk.frontend-api.option-source.v1"
FRONTEND_API_REST_REQUEST_SCHEMA = "paradev.sdk.frontend-api.rest-request.v1"
FRONTEND_API_SUMMARY_SCHEMA = "paradev.sdk.frontend-api.summary.v1"
FRONTEND_API_WORKSPACE_SCHEMA = "paradev.sdk.frontend-api.workspace.v1"
FRONTEND_API_SELECTORS = ("operation_id", "group_id")
FRONTEND_API_BINDING_SURFACES = ("cli", "lsp", "mcp", "rest", "sdk")
FRONTEND_API_SURFACE_COVERAGE_COLUMNS = ("sdk", "cli", "rest", "mcp", "lsp")
_FRONTEND_API_SURFACE_INDEX_VALUES = (*FRONTEND_API_SURFACE_COVERAGE_COLUMNS, "unbound")
FRONTEND_API_INDEX_CATALOG = (
    {
        "id": "group",
        "contract_path": 'contract["index"]["group"][group_id]',
        "python_helper": "get_frontend_api_group_operation_ids(group_id)",
        "typescript_helper": "getFrontendApiGroupOperationIds(groupId)",
        "usage": "Group id to operation ids.",
    },
    {
        "id": "status",
        "contract_path": 'contract["index"]["status"][status]',
        "python_helper": "get_frontend_api_status_operation_ids(status)",
        "typescript_helper": "getFrontendApiStatusOperationIds(status)",
        "usage": "Implementation status to operation ids.",
    },
    {
        "id": "mode",
        "contract_path": 'contract["index"]["mode"][mode]',
        "python_helper": "get_frontend_api_mode_operation_ids(mode)",
        "typescript_helper": "getFrontendApiModeOperationIds(mode)",
        "usage": "Read/write mode to operation ids.",
    },
    {
        "id": "surface",
        "contract_path": 'contract["index"]["surface"][surface]',
        "python_helper": "get_frontend_api_surface_operation_ids(surface)",
        "typescript_helper": "getFrontendApiSurfaceOperationIds(surface)",
        "usage": "Callable surface to operation ids.",
    },
    {
        "id": "binding",
        "contract_path": 'contract["index"]["binding"][surface][key]',
        "python_helper": "get_frontend_api_binding_operation_ids(surface, key)",
        "typescript_helper": "getFrontendApiBindingOperationIds(surface, key)",
        "usage": "Surface call key to operation ids.",
    },
    {
        "id": "payload",
        "contract_path": 'contract["index"]["payload"][payload]',
        "python_helper": "get_frontend_api_payload_operation_ids(payload)",
        "typescript_helper": "getFrontendApiPayloadOperationIds(payload)",
        "usage": "Payload schema to operation ids.",
    },
    {
        "id": "workspace_section",
        "contract_path": 'contract["index"]["workspace_section"][section_id]',
        "python_helper": "get_frontend_api_workspace_section_operation_ids(section_id)",
        "typescript_helper": "getFrontendApiWorkspaceSectionOperationIds(sectionId)",
        "usage": "Workspace section id to operation ids.",
    },
)
PROJECT_INPUT_GROUPS = frozenset({"modules", "collections", "build", "catalog"})
AUTHORING_KIND_CHOICES = ("module", "collection")
DIAGNOSTIC_SEVERITY_CHOICES = ("error", "warning")
INSPECTION_KIND_CHOICES = tuple(str(row["kind"]) for row in get_project_inspection_contract()["inspections"] if isinstance(row, Mapping))
OWNER_KIND_CHOICES = ("module", "collection")
PROJECT_BROWSER_KIND_CHOICES = ("module", "collection")
SOURCE_SLOT_STATUS_CHOICES = ("satisfied", "missing", "empty", "diagnostic")
SOURCE_STATUS_CHOICES = ("loaded", "diagnostic")
TARGET_ROOT_CHOICES = ("output", "build")
CONFIRMATION_FIELD_NAMES = frozenset({"create", "emit_artifacts", "emit_manifests", "force", "write"})
DESTRUCTIVE_ACTIONS = frozenset({"remove", "delete"})
REST_BODY_INPUTS = {
    "lsp.diagnostics": ("text", "uri", "path"),
    "lsp.symbols": ("text", "uri", "path"),
    "lsp.hover": ("text", "line", "character", "uri", "path"),
    "lsp.formatting": ("text", "uri", "path", "indent", "comments"),
    "lsp.completion": (
        "text",
        "line",
        "character",
        "offset",
        "uri",
        "path",
        "project_path",
        "database",
        "game_root",
        "limit",
    ),
    "lsp.semantic_tokens": ("text", "uri", "path"),
    "module.create": ("values",),
    "module.create_batch": (
        "project_id",
        "project_root",
        "modules",
        "source_root",
        "write",
        "plan_hash",
    ),
    "module.duplicate": (
        "project_root",
        "module_id",
        "object_id",
        "source_root",
        "destination_source_root",
        "write",
        "plan_hash",
    ),
    "module.metadata.clean": (
        "project_root",
        "family",
        "module_id",
        "source_root",
        "write",
        "plan_hash",
    ),
    "module.collection.set": (
        "project_root",
        "module_id",
        "collection_id",
        "source_root",
        "write",
        "plan_hash",
    ),
    "module.activity.set": (
        "project_root",
        "module_id",
        "active",
        "source_root",
        "write",
        "plan_hash",
    ),
    "module.diagram.edit": (
        "project_root",
        "family",
        "profile",
        "position_intents",
        "edge_intents",
        "node_intents",
        "write",
        "plan_hash",
    ),
    "module.draft": (
        "project_root",
        "template_id",
        "object_id",
        "values",
        "write",
        "force",
    ),
    "module.edit": ("text",),
    "localization.workspace": (
        "project_root",
        "target_kind",
        "target_id",
        "family",
        "source_root",
        "drafts",
        "limit",
    ),
    "localization.plan": (
        "project_root",
        "target_kind",
        "target_id",
        "family",
        "source_root",
        "drafts",
        "limit",
        "operation",
    ),
    "collection.scaffold": ("values",),
    "collection.create": ("metadata",),
    "collection.edit": ("text",),
    "project.source_form": ("project_root", "path", "text", "query"),
    "project.draft_apply": (
        "project_root",
        "source_edits",
        "source_removals",
        "source_replacements",
        "module_rename",
    ),
    "build.start": (
        "project_root",
        "mode",
        "profile",
        "strict_metadata",
        "parallelism",
        "target",
    ),
    "build.interrupt": ("run_id",),
    "ai.chat": (
        "provider",
        "model",
        "gateway",
        "preset",
        "key_env",
        "base_url",
        "prompt",
        "role",
        "project_root",
        "sources",
    ),
    "ai.profile.write": ("profile", "project_root"),
    "surface.frontend_api.action": (),
    "surface.frontend_api.normalize": ("values",),
    "surface.frontend_api.options": ("values",),
    "surface.frontend_api.rest_request": ("values",),
}
FRONTEND_API_LABEL_WORDS = {
    "api": "API",
    "cli": "CLI",
    "id": "ID",
    "json": "JSON",
    "lsp": "LSP",
    "mcp": "MCP",
    "pdx": "PDX",
    "rest": "REST",
    "sdk": "SDK",
    "uri": "URI",
    "url": "URL",
}
FRONTEND_API_FIELD_DESCRIPTIONS = {
    "artifact_path": "Artifact path filter relative to the selected target root.",
    "artifact_type": "Artifact type filter, such as PDX output, localization, or static asset.",
    "character": "Zero-based editor character for LSP position requests.",
    "code": "Diagnostic code filter.",
    "collection_id": "Stable collection identifier.",
    "collection_source_slot": "Collection source slot filter.",
    "comments": "Keep or emit PDX comments when formatting output.",
    "create": "Create the target source file when it does not already exist.",
    "database": "Optional HeavenBase catalog database path.",
    "drafts": "Current unsaved source texts keyed by their Registry-owned source paths.",
    "diagnostic_code": "Specific diagnostic code filter for source or authoring checks.",
    "edge_intents": ("Bounded array of reviewed dependency/path edge-presence intents from " "the current source-backed module diagram."),
    "edge_kind": "Dependency edge kind filter.",
    "emit_artifacts": "Write build artifacts after the build plan is not blocked.",
    "emit_manifests": "Write build manifests after the build plan is not blocked.",
    "encoding": "Text encoding used when reading or writing source files.",
    "entity": "HeavenBase entity type filter.",
    "family": "Compiler family filter, such as focus, idea, or modifier.",
    "file_format": "Static asset file-format filter.",
    "force": "Allow overwriting existing starter or scaffold files after confirmation.",
    "family_id": "Frontend browser family id, such as ideas, focuses, decisions, or modifiers.",
    "form": "Return the derived form contract for the selected frontend operation.",
    "game": "Game profile identifier, such as hoi4.",
    "game_root": "Hearts of Iron IV install path used for built-in keyword completion data.",
    "gateway": "HeavenBase gateway identifier used for AI model routing.",
    "group_id": "Frontend API group identifier.",
    "include_dump": "Include a parsed AST dump in the PDX response.",
    "include_tokens": "Include lexer token rows in the PDX response.",
    "indent": "Indent string used by the PDX formatter.",
    "key": "Exact localization key filter.",
    "key_prefix": "Localization key-prefix filter.",
    "kind": "Select a module or collection scope for shared browser and authoring operations.",
    "language": "Localization language filter.",
    "limit": "Maximum number of rows to return.",
    "line": "Zero-based editor line for LSP position requests.",
    "loader": "Source loader kind filter.",
    "metadata": "Collection metadata object to write into the descriptor.",
    "mode": "Artifact emission mode filter.",
    "model": "AI model identifier routed through HeavenBase.",
    "module_id": "Stable module identifier.",
    "modules": "Ordered module creation requests for one atomic batch.",
    "name": "Exact name filter.",
    "object_id": "Object identifier for a new or renamed module.",
    "operation": "Closed Registry-owned authoring operation to validate and plan.",
    "operation_id": "Stable frontend API operation identifier.",
    "owner": "Artifact owner filter.",
    "owner_kind": "Source owner kind filter.",
    "profile_id": "Stable ParaDev AI chat profile id to edit.",
    "profile": "Build or game profile name.",
    "parallelism": "Maximum build worker count.",
    "plan_hash": "Exact plan hash returned by a prior dry run when applying a guarded write.",
    "position_intents": ("Bounded array of reviewed absolute node-position intents from the " "current source-backed module diagram."),
    "prompt": "User prompt sent to the desktop AI chat route.",
    "project_id": "Stable project identifier.",
    "project_path": "Currently active project path for desktop project switchers.",
    "project_paths": "Known project paths for project switchers.",
    "project_root": "Explicit project root used when a project id is not registered in local state.",
    "provider": "HeavenBase AI provider identifier, such as deepseek.",
    "relative_path": "Source file path relative to the selected module or collection root.",
    "route": "REST route filter.",
    "role": "Stable ParaDev AI role identifier, such as chat or explain.",
    "run_id": "Desktop build run identifier.",
    "search_roots": "Filesystem roots scanned for local projects.",
    "severity": "Diagnostic severity filter.",
    "slot": "Source slot filter.",
    "source": "Source root or source kind filter.",
    "source_edits": (
        "Array of text edits with project-contained path and replacement text; optional paired expected_size and "
        "expected_mtime_ns fields reject writes when the source changed after it was read."
    ),
    "source_path": "Exact source file path filter.",
    "source_removals": (
        "Array of project-contained source file paths or removal objects; optional paired expected_size and " "expected_mtime_ns fields reject stale deletion."
    ),
    "source_replacements": (
        "Array of binary replacements with project-contained path and base64 content; optional content_format=png and target_format "
        "convert PNG uploads to DDS, TGA, JPEG, WebP, or BMP before atomic replacement. Optional paired expected_size and "
        "expected_mtime_ns fields reject writes when the source changed after it was read; expected_absent=true rejects a "
        "new-file write if its target appeared meanwhile."
    ),
    "module_rename": (
        "Optional module identity mapping committed after all source drafts " "succeed, with module_id, object_id, and optional source_root and title."
    ),
    "source_root": "Named source root or source root path for authoring operations.",
    "source_slot": "Declared source slot filter.",
    "sprite_slot": "Sprite slot filter.",
    "status": "Status filter for source, source-slot, or diagnostic rows.",
    "strict_metadata": "Treat unknown module or collection metadata keys as blocking diagnostics.",
    "tag": "HeavenBase catalog tag filter.",
    "target": "Target identifier filter.",
    "target_id": "Target object or collection identifier.",
    "target_root": "Artifact target root filter.",
    "template_id": "Authoring template identifier.",
    "text": "Submitted source file or editor-buffer text.",
    "title": "Human-readable project title.",
    "uri": "Optional document URI for editor-buffer operations.",
    "values": "Submitted frontend form values or scaffold template values.",
    "write": "Write files only after the user confirms the planned change.",
}
FRONTEND_API_PATH_DESCRIPTIONS = {
    "pdx": "Saved Paradox script file path.",
    "lsp": "Optional saved file path for editor diagnostics context.",
}

FRONTEND_API_GROUPS = [
    {
        "id": "projects",
        "title": "Projects",
        "summary": "Create, open, view, inspect, configure, and select projects.",
    },
    {
        "id": "modules",
        "title": "Modules",
        "summary": "List, create, inspect, and edit source modules.",
    },
    {
        "id": "collections",
        "title": "Collections",
        "summary": "List, inspect, and author collection descriptor sources.",
    },
    {
        "id": "localization",
        "title": "Localization",
        "summary": "Edit module and collection text through one guarded language workspace.",
    },
    {
        "id": "build",
        "title": "Build",
        "summary": "Plan builds, inspect manifests, trace sources, and explain diagnostics.",
    },
    {
        "id": "pdx",
        "title": "PDX",
        "summary": "Parse, tokenize, dump, and format Paradox script files.",
    },
    {
        "id": "lsp",
        "title": "LSP",
        "summary": "Language-server operations for editor-style diagnostics and navigation.",
    },
    {
        "id": "catalog",
        "title": "Catalog",
        "summary": "Preview, write, refresh, and query HeavenBase catalog rows.",
    },
    {
        "id": "ai",
        "title": "AI",
        "summary": "Route desktop AI chat prompts through the Python SDK.",
    },
    {
        "id": "surfaces",
        "title": "Surfaces",
        "summary": "Inspect SDK-owned CLI, MCP, REST, OpenAPI, and frontend contracts.",
    },
]
FRONTEND_API_WORKSPACE_SECTIONS = [
    {
        "id": "project-switcher",
        "title": "Project Switcher",
        "summary": "Create, find, open, configure, rename, and activate local projects.",
        "default_operation_id": "project.state",
        "operation_ids": (
            "project.state",
            "project.list",
            "project.find",
            "project.open",
            "project.create",
            "project.rename",
            "project.language",
            "project.activate",
        ),
    },
    {
        "id": "project-browser",
        "title": "Project Browser",
        "summary": "Browse modules, collections, source slots, and source inventories.",
        "default_operation_id": "project.browser",
        "operation_ids": (
            "project.browser",
            "module.list",
            "module.view",
            "collection.list",
            "collection.view",
            "module.source_slots",
            "module.sources",
            "collection.source_slots",
            "collection.sources",
        ),
    },
    {
        "id": "authoring",
        "title": "Authoring",
        "summary": "Resolve authoring destinations and perform guarded module or collection mutations.",
        "default_operation_id": "module.authoring_plan",
        "operation_ids": (
            "module.authoring_path",
            "module.authoring_plan",
            "module.templates",
            "module.diagram",
            "module.diagram.edit",
            "module.create",
            "module.create_batch",
            "module.draft",
            "module.rename",
            "module.collection.set",
            "module.activity.set",
            "module.metadata.clean",
            "module.remove",
            "collection.authoring_path",
            "collection.authoring_plan",
            "collection.scaffold",
            "collection.create",
            "collection.rename",
            "collection.remove",
            "localization.workspace",
            "localization.plan",
        ),
    },
    {
        "id": "source-editor",
        "title": "Source Editor",
        "summary": "Read, write, parse, format, diagnose, outline, and inspect source buffers.",
        "default_operation_id": "module.file",
        "operation_ids": (
            "project.source_text",
            "project.source_form",
            "module.file",
            "module.edit",
            "collection.file",
            "collection.edit",
            "project.draft_apply",
            "pdx.parse",
            "pdx.format",
            "lsp.diagnostics",
            "lsp.symbols",
            "lsp.hover",
            "lsp.formatting",
            "lsp.completion",
            "lsp.semantic_tokens",
            "lsp.keywords",
        ),
    },
    {
        "id": "build",
        "title": "Build",
        "summary": "Plan builds, emit artifacts, inspect outputs, and trace diagnostics.",
        "default_operation_id": "build.plan",
        "operation_ids": (
            "build.plan",
            "build.emit",
            "build.start",
            "build.runs",
            "build.status",
            "build.interrupt",
            "build.summary",
            "build.manifests",
            "build.artifacts",
            "build.localization",
            "build.assets",
            "build.sprites",
            "build.diagnostics",
            "build.source_map",
            "build.dependencies",
            "build.graph",
            "build.explain",
            "build.families",
        ),
    },
    {
        "id": "catalog",
        "title": "Catalog",
        "summary": "Preview, write, refresh, and query HeavenBase catalog rows.",
        "default_operation_id": "catalog.preview",
        "operation_ids": (
            "catalog.preview",
            "catalog.write",
            "catalog.refresh",
            "catalog.query",
        ),
    },
    {
        "id": "ai-chat",
        "title": "AI Chat",
        "summary": "Send desktop AI prompts through the SDK-owned HeavenBase route.",
        "default_operation_id": "ai.chat",
        "operation_ids": (
            "ai.profiles",
            "ai.profile.write",
            "ai.profile.reset",
            "ai.chat",
        ),
    },
    {
        "id": "surface-contracts",
        "title": "Surface Contracts",
        "summary": "Inspect SDK-owned API, adapter, REST, MCP, CLI, LSP, and architecture contracts.",
        "default_operation_id": "surface.frontend_api",
        "operation_ids": (
            "surface.frontend_api",
            "surface.frontend_api.workspace",
            "surface.frontend_api.action",
            "surface.frontend_api.normalize",
            "surface.frontend_api.rest_request",
            "surface.frontend_api.options",
            "surface.frontend_api.binding_lookup",
            "surface.architecture",
            "surface.openapi",
            "surface.cli_contract",
            "surface.mcp_contract",
            "surface.lsp_contract",
        ),
    },
]


def _option_source(
    operation_id: str,
    values_path: Sequence[str],
    value_field: str,
    label_field: str,
    *,
    detail_fields: Sequence[str] = (),
    requires: Sequence[str] = (),
    forward: Sequence[str] = (),
    filters: Mapping[str, object] | None = None,
) -> dict[str, object]:
    source: dict[str, object] = {
        "schema": FRONTEND_API_OPTION_SOURCE_SCHEMA,
        "operation_id": operation_id,
        "values_path": list(values_path),
        "value_field": value_field,
        "label_field": label_field,
    }
    if detail_fields:
        source["detail_fields"] = list(detail_fields)
    if requires:
        source["requires"] = list(requires)
    if forward:
        source["forward"] = list(forward)
    if filters:
        source["filters"] = dict(filters)
    return source


TEMPLATE_OPTION_SOURCE = _option_source(
    "module.templates",
    ("templates",),
    "id",
    "title",
    detail_fields=("family", "source"),
    requires=("path",),
    forward=("path",),
    filters={"authoring_ready": True},
)
SOURCE_ROOT_OPTION_SOURCE = _option_source(
    "module.templates",
    ("source_roots",),
    "relative_path",
    "relative_path",
    detail_fields=("path",),
    requires=("path",),
    forward=("path",),
)
FAMILY_OPTION_SOURCE = _option_source(
    "build.families",
    ("families",),
    "family",
    "family",
    detail_fields=("kind",),
    requires=("path",),
    forward=("path", "profile"),
)
MODULE_ID_OPTION_SOURCE = _option_source(
    "module.list",
    ("modules",),
    "module_id",
    "module_id",
    detail_fields=("family", "collection_id"),
    requires=("path",),
    forward=("path", "profile", "family", "collection_id"),
)
COLLECTION_ID_OPTION_SOURCE = _option_source(
    "collection.list",
    ("collections",),
    "collection_id",
    "collection_id",
    detail_fields=("family",),
    requires=("path",),
    forward=("path", "profile", "family", "module_id"),
)
MODULE_RELATIVE_PATH_OPTION_SOURCE = _option_source(
    "module.sources",
    ("sources",),
    "relative_path",
    "relative_path",
    detail_fields=("slot", "loader", "status"),
    requires=("path", "module_id"),
    forward=(
        "path",
        "profile",
        "module_id",
        "family",
        "collection_id",
        "slot",
        "loader",
        "status",
    ),
)
COLLECTION_RELATIVE_PATH_OPTION_SOURCE = _option_source(
    "collection.sources",
    ("sources",),
    "relative_path",
    "relative_path",
    detail_fields=("slot", "loader", "status"),
    requires=("path", "collection_id"),
    forward=("path", "profile", "collection_id", "family", "slot", "loader", "status"),
)
SOURCE_PATH_OPTION_SOURCE = _option_source(
    "module.sources",
    ("sources",),
    "path",
    "relative_path",
    detail_fields=("module_id", "slot", "loader", "status"),
    requires=("path",),
    forward=(
        "path",
        "profile",
        "module_id",
        "family",
        "collection_id",
        "slot",
        "loader",
        "status",
    ),
)
ARTIFACT_PATH_OPTION_SOURCE = _option_source(
    "build.artifacts",
    ("artifacts",),
    "path",
    "path",
    detail_fields=("type", "target_root", "owner"),
    requires=("path",),
    forward=(
        "path",
        "profile",
        "artifact_type",
        "target_root",
        "owner",
        "mode",
        "module_id",
        "collection_id",
    ),
)
ARTIFACT_TYPE_OPTION_SOURCE = _option_source(
    "build.artifacts",
    ("artifacts",),
    "type",
    "type",
    detail_fields=("target_root", "owner"),
    requires=("path",),
    forward=(
        "path",
        "profile",
        "target_root",
        "owner",
        "mode",
        "module_id",
        "collection_id",
    ),
)
DIAGNOSTIC_CODE_OPTION_SOURCE = _option_source(
    "build.diagnostics",
    ("diagnostics",),
    "code",
    "code",
    detail_fields=("severity", "message"),
    requires=("path",),
    forward=(
        "path",
        "profile",
        "severity",
        "family",
        "module_id",
        "collection_id",
        "source_path",
        "slot",
        "strict_metadata",
    ),
)


def get_frontend_api_contract() -> dict[str, object]:
    """Return the canonical frontend-facing API operation list.

    Returns:
        JSON-safe operation contract for GUI, REST, MCP, importer, VS Code,
        and desktop clients. Implemented rows point at the current SDK, CLI,
        REST, MCP, or LSP surface. Planned rows are explicit placeholders for
        APIs that the frontend may need but that are not stable behavior yet.
    """

    operations = _frontend_api_operations()
    workspace = _frontend_api_workspace(operations)
    groups = _frontend_api_groups(operations)
    return {
        "schema": FRONTEND_API_SCHEMA,
        "status": "alpha",
        "sdk_owned": True,
        "summary": _frontend_api_summary(operations, groups, workspace),
        "groups": groups,
        "operations": operations,
        "workspace": workspace,
        "index": _frontend_api_index(operations, workspace),
        "inspection_contract": get_project_inspection_contract(),
        "maintenance": {
            "rule": "Add or update a row whenever a frontend-visible SDK, CLI, REST, MCP, or LSP capability changes.",
            "manual": "docs/user-manual/frontend-api.md",
            "reference_manual": "docs/user-manual/frontend-api-reference.md",
            "architecture": "docs/architecture/interfaces.md",
        },
    }


def get_frontend_api_selection(
    operation_id: str | None = None,
    group_id: str | None = None,
    *,
    form: bool = False,
    index_name: str | None = None,
    key: str | None = None,
) -> dict[str, object] | list[str]:
    """Return the frontend API table or one selector projection.

    Args:
        operation_id: Optional stable operation id. When `form` is true, the
            selected operation's derived form contract is returned.
        group_id: Optional stable operation group id.
        form: Return the selected operation's form contract instead of the
            operation row.
        index_name: Optional flat index dimension such as `status`, `mode`,
            `surface`, `payload`, or `workspace_section`.
        key: Optional concrete index key used with `index_name`.

    Returns:
        The full frontend API contract, one operation row, one group slice, or
        one operation form contract, or one ordered operation id list for
        `index_name` and `key`.

    Raises:
        ValueError: If selectors are ambiguous, incomplete, or unknown.
    """

    index_lookup = index_name is not None or key is not None
    if form and (not operation_id or group_id or index_lookup):
        raise ValueError("form requires operation_id and cannot be combined with group_id or index_name/key.")
    if index_lookup and (index_name is None or key is None):
        raise ValueError("index_name requires key, and key requires index_name.")
    if index_lookup and (operation_id or group_id):
        raise ValueError("Pass only one frontend API selector: operation_id, group_id, or index_name/key.")
    if not form and operation_id and group_id:
        raise ValueError("Pass only one frontend API selector: operation_id or group_id.")
    if index_name is not None and key is not None:
        return _frontend_api_selection_index_operation_ids(index_name, key)
    if form and operation_id:
        return get_frontend_api_form(operation_id)
    if operation_id:
        return get_frontend_api_operation(operation_id)
    if group_id:
        return get_frontend_api_group(group_id)
    return get_frontend_api_contract()


def get_frontend_api_index_catalog() -> list[dict[str, str]]:
    """Return the documented frontend API index dimensions.

    Returns:
        Copied rows describing the canonical contract index path, Python SDK
        helper, TypeScript helper, and intended lookup use for each index
        dimension.
    """

    return [dict(row) for row in FRONTEND_API_INDEX_CATALOG]


def get_frontend_api_workspace() -> dict[str, object]:
    """Return the SDK-owned workspace projection for GUI navigation.

    Returns:
        JSON-safe workspace sections derived from canonical frontend API
        operation ids. Sections are intended for GUI, importer, desktop,
        VS Code, MCP, and REST clients that need a maintained action layout
        without inventing frontend-only operation names. Action rows include
        derived execution hints, default surface selection, callable bindings,
        form schema, and normalization or REST-planner schema references.
    """

    return _frontend_api_workspace(_frontend_api_operations())


def get_frontend_api_action(operation_id: str) -> dict[str, object]:
    """Return the frontend-ready detail payload for one operation.

    Args:
        operation_id: Stable operation id such as `module.create` or
            `pdx.format`.

    Returns:
        JSON-safe action detail that combines the canonical operation row, the
        matching workspace action row, the derived form contract when the
        operation has inputs, section membership, bindings, execution hints,
        and option-source field names.

    Raises:
        ValueError: If `operation_id` is not listed in the frontend contract.
    """

    operation = get_frontend_api_operation(operation_id)
    workspace = get_frontend_api_workspace()
    sections = _frontend_api_action_sections(workspace, operation_id)
    action = _frontend_api_action_workspace_row(workspace, operation)
    form = _frontend_api_action_form(operation_id, operation)
    return _frontend_api_action_detail_payload(operation_id, operation, sections, action, form)


def _frontend_api_action_workspace_row(workspace: Mapping[str, object], operation: dict[str, object]) -> dict[str, object]:
    operation_id = str(operation["id"])
    action = _frontend_api_workspace_action(workspace, operation_id)
    if action:
        return action
    return _workspace_action(operation)


def _frontend_api_action_form(operation_id: str, operation: Mapping[str, object]) -> dict[str, object] | None:
    if not _frontend_api_operation_has_form(operation):
        return None
    return get_frontend_api_form(operation_id)


def _frontend_api_action_detail_payload(
    operation_id: str,
    operation: Mapping[str, object],
    sections: Sequence[str],
    action: Mapping[str, object],
    form: Mapping[str, object] | None,
) -> dict[str, object]:
    option_sources = _frontend_api_action_option_sources(form)
    return {
        "schema": FRONTEND_API_ACTION_DETAIL_SCHEMA,
        "operation_id": operation_id,
        "sections": list(sections),
        "operation": operation,
        "action": action,
        "form": form,
        "option_fields": list(option_sources),
        "option_sources": option_sources,
        "bindings": _copy_bindings(operation.get("bindings", {})),
        "execution": _copy_binding(action.get("execution", {})),
    }


def render_frontend_api_reference_markdown() -> str:
    """Render the canonical frontend API operation list as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/frontend-api-reference.md`. The content is generated
        from `get_frontend_api_contract()` so docs and SDK operation rows stay
        aligned.
    """

    contract = get_frontend_api_contract()
    operations = _frontend_api_operation_rows(contract)
    lines = [
        "# Frontend API Reference",
        "",
        *_frontend_api_reference_language_sections(
            contract,
            "## English",
            _frontend_api_reference_english_intro_lines(),
            _frontend_api_reference_english_lookup_sections(contract),
            _frontend_api_reference_english_detail_sections(contract),
        ),
        *_frontend_api_reference_language_sections(
            contract,
            "## 中文",
            _frontend_api_reference_chinese_intro_lines(),
            _frontend_api_reference_chinese_lookup_sections(contract),
            _frontend_api_reference_chinese_detail_sections(contract),
        ),
        "## Operations / 操作清单",
        "",
    ]
    lines.extend(_frontend_api_reference_operation_sections(contract, operations))
    return "\n".join(lines)


def _frontend_api_reference_language_sections(
    contract: Mapping[str, object],
    heading: str,
    intro_lines: Sequence[str],
    lookup_sections: Sequence[str],
    detail_sections: Sequence[str],
) -> list[str]:
    return [
        heading,
        "",
        *intro_lines,
        "",
        *_frontend_api_reference_summary_section(contract["summary"]),
        "",
        *lookup_sections,
        *detail_sections,
    ]


def _frontend_api_reference_english_intro_lines() -> list[str]:
    return [
        "Generated from `paradev.sdk.get_frontend_api_contract()`.",
        "Do not maintain a second frontend API list by hand; update `src/paradev/sdk/frontend_api.py`, then regenerate this page with `rtk uv run paradev frontend-api --markdown`.",
        "For TypeScript clients, regenerate `apps/desktop/src/generated/frontendApi.ts` with `rtk uv run paradev frontend-api --typescript`; the file exports operation id unions plus the full contract.",
        "The operation ids, surface names, payload schemas, and input names below are the stable contract for GUI, importer, REST, MCP, VS Code, and desktop clients.",
        "Use `get_frontend_api_workspace()` for SDK-owned workspace sections and action grouping.",
        "Workspace action rows use `paradev.sdk.frontend-api.action.v1` and expose derived `execution.default_surface`, `execution.available_surfaces`, `execution.confirmation`, callable `bindings`, `form_schema`, `normalizer_schema`, and `rest_request_schema` hints.",
        "`execution.confirmation` uses `paradev.sdk.frontend-api.confirmation.v1`; GUI shells must honor `required`, `scope`, `style`, and `confirm_fields` before executing a planned REST request.",
        "Use `get_frontend_api_group_operation_ids(group_id)` / TypeScript `getFrontendApiGroupOperationIds(groupId)` and `get_frontend_api_status_operation_ids(status)` / TypeScript `getFrontendApiStatusOperationIds(status)` when a client needs a grouped operation id list without reading raw indexes.",
        "Use `get_frontend_api_mode_operation_ids(mode)` / TypeScript `getFrontendApiModeOperationIds(mode)` when a client needs a read/write operation id list without scanning rows.",
        "Use `get_frontend_api_selection(index_name=..., key=...)`, CLI `frontend-api --index ... --key ...`, REST `GET /frontend-api?index_name=...&key=...`, or MCP `frontend_api` when a surface needs one shared selector path for a flat operation-id index.",
        "Use `get_frontend_api_action(operation_id)` for a one-operation detail payload that combines the operation row, workspace action, form, bindings, and option-source field names.",
        "Use `get_frontend_api_form(operation_id)` for SDK-owned field labels, descriptions, controls, choices, bounds, aliases, option sources, and JSON Schema.",
        "Field `option_source` rows use `paradev.sdk.frontend-api.option-source.v1` and point to another canonical operation id plus a list path and display fields.",
        "Use `resolve_frontend_api_options(operation_id, field_name, values)` or `paradev frontend-api --option-field` to execute those option sources through the SDK.",
        "Use `get_frontend_api_binding_lookup(surface, key)`, `get_frontend_api_binding_operation_ids(surface, key)`, `get_frontend_api_binding_index(surface)`, `get_frontend_api_rest_operation_ids(method, path, query)`, or CLI `frontend-api --binding-surface ... --binding-key ...` when a surface call key or whole adapter surface must map back to stable operation ids.",
        "The summary publishes overall and per-group surface binding coverage as `surface_counts` and `group_surface_counts`; the table below renders those same fields.",
        'Use `get_frontend_api_surface_operation_ids(surface)` or `contract["index"]["surface"]` when a client needs every operation id backed by one surface without scanning rows.',
        'Use `get_frontend_api_payload_operation_ids(payload)` or `contract["index"]["payload"]` when a renderer needs every operation id returning one payload schema; rows without a declared payload are grouped under `untyped`.',
        'Use `get_frontend_api_workspace_section_operation_ids(section_id)` or `contract["index"]["workspace_section"]` when a shell needs every operation id in one workspace section without scanning workspace rows.',
    ]


def _frontend_api_reference_english_lookup_sections(
    contract: Mapping[str, object],
) -> list[str]:
    return [
        *_frontend_api_index_catalog_section(
            body=(
                "Rows document which SDK-owned index backs each lookup helper; clients should prefer helper APIs and use raw contract paths only for generated clients.",
            ),
        ),
        "",
        *_frontend_api_group_index_section(
            contract,
            body=("Rows group canonical operation ids by SDK-owned operation group.",),
        ),
        "",
        *_frontend_api_status_index_section(
            contract,
            body=("Rows group canonical operation ids by implementation status.",),
        ),
        "",
        *_frontend_api_mode_index_section(
            contract,
            body=("Rows group canonical operation ids by whether the operation mutates project or app state.",),
        ),
        "",
        *_frontend_api_surface_index_section(
            contract,
            body=("Rows group canonical operation ids by callable surface; `unbound` rows are frontend-local or contract-only operations.",),
        ),
        "",
        *_frontend_api_surface_coverage_section(
            contract["summary"],
            body=(
                "Counts show operation rows with an explicit binding for each surface; `Unbound` is frontend-local or contract-only rows without a callable surface.",
            ),
        ),
        "",
        *_frontend_api_rest_route_index_section(
            contract,
            body=(
                "Rows group canonical operation ids by structured REST method, path, and query values. Use this table for GUI REST clients and OpenAPI audits instead of parsing display strings.",
            ),
        ),
        "",
        *_frontend_api_rest_request_planner_index_section(
            contract,
            body=(
                "Rows list REST planner inputs for each REST-bound operation, including static query defaults, path parameters, and fields routed to the JSON body.",
            ),
        ),
        "",
        *_frontend_api_workspace_section_rest_summary_index_section(
            contract,
            body=(
                "Rows summarize REST planner coverage by SDK-owned workspace section, including method distribution, static query defaults, path parameters, JSON body fields, and dynamic query fields.",
            ),
        ),
        "",
        *_frontend_api_group_rest_summary_index_section(
            contract,
            body=(
                "Rows summarize REST planner coverage by operation group, including method distribution, static query defaults, path parameters, JSON body fields, and dynamic query fields.",
            ),
        ),
        "",
        *_frontend_api_rest_static_query_index_section(
            contract,
            body=(
                "Rows list fixed query parameters declared by REST bindings, including canonical operation id, method, path, rendered value, and JSON value type.",
            ),
        ),
        "",
        *_frontend_api_rest_dynamic_query_field_index_section(
            contract,
            body=(
                "Rows list frontend inputs routed to REST query parameters at request-plan time, excluding REST path parameters and JSON body fields; `Static Default` shows fields that can override a fixed binding query when explicitly submitted.",
            ),
        ),
        "",
        *_frontend_api_rest_path_parameter_index_section(
            contract,
            body=(
                "Rows list each frontend input routed to a REST path parameter, including alias-aware parameter names, source field names, types, required state, and normalizer target bucket.",
            ),
        ),
        "",
        *_frontend_api_rest_body_field_index_section(
            contract,
            body=(
                "Rows list each frontend input routed to a REST JSON body field, including alias-aware body names, source field names, types, required state, and normalizer target bucket.",
            ),
        ),
        "",
        *_frontend_api_sdk_call_index_section(
            contract,
            body=(
                "Rows group canonical operation ids by SDK call string. Use this table for Python SDK audits instead of filtering the generic binding table by hand.",
            ),
        ),
        "",
        *_frontend_api_sdk_call_input_index_section(
            contract,
            body=(
                "Rows list declared frontend inputs for SDK-bound operations, including SDK call string, operation id, input type, required/default state, normalizer target bucket, and adapter-side alias.",
            ),
        ),
        "",
        *_frontend_api_mcp_tool_index_section(
            contract,
            body=(
                "Rows group canonical operation ids by MCP tool name. Use this table for MCP adapter audits instead of filtering the generic binding table by hand.",
            ),
        ),
        "",
        *_frontend_api_mcp_tool_input_index_section(
            contract,
            body=(
                "Rows list declared frontend inputs for MCP-bound operations, including tool name, operation id, input type, required/default state, normalizer target bucket, and adapter-side alias.",
            ),
        ),
        "",
        *_frontend_api_cli_command_index_section(
            contract,
            body=(
                "Rows group canonical operation ids by CLI command string. Use this table for CLI adapter audits instead of filtering the generic binding table by hand.",
            ),
        ),
        "",
        *_frontend_api_cli_command_input_index_section(
            contract,
            body=(
                "Rows list declared frontend inputs for CLI-bound operations, including command string, operation id, input type, required/default state, normalizer target bucket, and adapter-side alias.",
            ),
        ),
        "",
        *_frontend_api_lsp_method_index_section(
            contract,
            body=(
                "Rows group canonical operation ids by LSP method string. Use this table for VS Code and language-server audits instead of filtering the generic binding table by hand.",
            ),
        ),
        "",
        *_frontend_api_lsp_method_input_index_section(
            contract,
            body=(
                "Rows list declared frontend inputs for LSP-bound operations, including LSP method string, operation id, input type, required/default state, normalizer target bucket, and adapter-side alias.",
            ),
        ),
        "",
        *_frontend_api_binding_index_section(
            contract,
            body=(
                "Rows map surface-specific call keys back to canonical operation ids. Use these rows for generated clients, audits, and shared REST routes instead of parsing display strings.",
            ),
        ),
        "",
        *_frontend_api_group_binding_summary_index_section(
            contract,
            body=(
                "Rows summarize concrete surface binding keys by operation group, including SDK calls, CLI commands, REST routes, MCP tools, LSP methods, and unbound operations.",
            ),
        ),
        "",
    ]


def _frontend_api_reference_english_detail_sections(
    contract: Mapping[str, object],
) -> list[str]:
    return [
        *_frontend_api_payload_index_section(
            contract,
            body=(
                "Rows group canonical operation ids by declared payload schema; `untyped` rows are contract or side-effect operations without a typed response payload.",
            ),
        ),
        "",
        *_frontend_api_workspace_section_index_section(
            contract,
            body=("Rows group canonical operation ids by SDK-owned workspace section; the default action is the section's first-render target.",),
        ),
        "",
        *_frontend_api_workspace_section_mode_status_section(
            contract,
            body=("Rows summarize read/write mode and implementation status coverage by SDK-owned workspace section.",),
        ),
        "",
        *_frontend_api_group_mode_status_section(
            contract,
            body=("Rows summarize read/write mode and implementation status coverage by operation group.",),
        ),
        "",
        *_frontend_api_workspace_section_payload_coverage_section(
            contract,
            body=(
                "Rows summarize response payload schemas by SDK-owned workspace section; actions without a declared response payload are counted as `untyped`.",
            ),
        ),
        "",
        *_frontend_api_group_payload_coverage_section(
            contract,
            body=("Rows summarize response payload schemas by operation group; operations without a declared response payload are counted as `untyped`.",),
        ),
        "",
        *_frontend_api_workspace_section_surface_coverage_section(
            contract,
            body=(
                "Rows summarize callable surface coverage by SDK-owned workspace section, including frontend-local actions, unbound actions, and default-surface distribution.",
            ),
        ),
        "",
        *_frontend_api_workspace_section_binding_summary_section(
            contract,
            body=(
                "Rows summarize concrete surface binding keys by SDK-owned workspace section, including SDK calls, CLI commands, REST routes, MCP tools, LSP methods, and unbound actions.",
            ),
        ),
        "",
        *_frontend_api_workspace_section_form_summary_section(
            contract,
            body=(
                "Rows summarize each SDK-owned workspace section's action form footprint: action count, input count, required fields, defaults, aliases, dynamic option sources, validation constraints, and control-kind counts.",
            ),
        ),
        "",
        *_frontend_api_workspace_section_control_summary_section(
            contract,
            body=(
                "Rows summarize SDK-derived form control kinds by workspace section, including dynamic option-backed controls, static-choice controls, and textarea fields.",
            ),
        ),
        "",
        *_frontend_api_group_control_summary_section(
            contract,
            body=(
                "Rows summarize SDK-derived form control kinds by operation group, including dynamic option-backed controls, static-choice controls, and textarea fields.",
            ),
        ),
        "",
        *_frontend_api_workspace_section_option_source_summary_section(
            contract,
            body=(
                "Rows summarize dynamic option-source dependencies by SDK-owned workspace section, including provider operations, payload paths, required context, forwarded fields, and fixed filters.",
            ),
        ),
        "",
        *_frontend_api_workspace_section_input_target_summary_section(
            contract,
            body=(
                "Rows summarize frontend input target buckets by SDK-owned workspace section, including parameter, project-context, selector, projection, and alias fields.",
            ),
        ),
        "",
        *_frontend_api_group_input_target_summary_section(
            contract,
            body=(
                "Rows summarize input target buckets by operation group, including parameter fields, project-context fields, selectors, projections, and aliases.",
            ),
        ),
        "",
        *_frontend_api_workspace_section_validation_summary_section(
            contract,
            body=(
                "Rows summarize frontend input validation constraints by SDK-owned workspace section, including constrained operation ids and choice/bound field names.",
            ),
        ),
        "",
        *_frontend_api_group_validation_summary_section(
            contract,
            body=(
                "Rows summarize frontend input validation constraints by operation group, including constrained operation ids and choice/bound field names.",
            ),
        ),
        "",
        *_frontend_api_workspace_section_default_summary_section(
            contract,
            body=(
                "Rows summarize defaulted frontend inputs by SDK-owned workspace section, including defaulted operation ids, field names, and literal default values.",
            ),
        ),
        "",
        *_frontend_api_group_default_summary_section(
            contract,
            body=("Rows summarize defaulted frontend inputs by operation group, including defaulted operation ids, field names, and literal default values.",),
        ),
        "",
        *_frontend_api_workspace_section_required_summary_section(
            contract,
            body=(
                "Rows summarize required frontend inputs by SDK-owned workspace section, including required operation ids, field names, target buckets, option providers, and aliases.",
            ),
        ),
        "",
        *_frontend_api_group_required_summary_section(
            contract,
            body=(
                "Rows summarize required frontend inputs by operation group, including required operation ids, field names, target buckets, option providers, and aliases.",
            ),
        ),
        "",
        *_frontend_api_workspace_section_alias_summary_section(
            contract,
            body=(
                "Rows summarize frontend-to-SDK input aliases by SDK-owned workspace section, including aliased operation ids, frontend fields, target buckets, option providers, and alias mappings.",
            ),
        ),
        "",
        *_frontend_api_group_alias_summary_section(
            contract,
            body=(
                "Rows summarize frontend-to-SDK input aliases by operation group, including aliased operation ids, frontend fields, target buckets, option providers, and alias mappings.",
            ),
        ),
        "",
        *_frontend_api_group_execution_summary_section(
            contract,
            body=(
                "Rows summarize workspace action execution policy by operation group, including execution kinds, default surfaces, available surfaces, value requirements, confirmations, state scopes, and planner schema coverage.",
            ),
        ),
        "",
        *_frontend_api_workspace_section_execution_summary_section(
            contract,
            body=(
                "Rows summarize SDK-owned workspace action execution policy by workspace section, including execution kinds, default surfaces, available surfaces, value requirements, confirmations, state scopes, and planner schema coverage.",
            ),
        ),
        "",
        *_frontend_api_workspace_action_execution_section(
            contract,
            body=(
                "Rows list SDK-owned workspace action execution hints for GUI shells, including default call surface, available surfaces, value requirements, frontend state scope, normalizer schema, and REST planner schema.",
            ),
        ),
        "",
        *_frontend_api_group_confirmation_summary_section(
            contract,
            body=("Rows summarize confirmation-gated workspace actions by operation group, including confirmation scopes, styles, fields, and operation ids.",),
        ),
        "",
        *_frontend_api_workspace_section_confirmation_summary_section(
            contract,
            body=(
                "Rows summarize confirmation-gated actions by SDK-owned workspace section, including confirmation scopes, styles, fields, and operation ids.",
            ),
        ),
        "",
        *_frontend_api_confirmation_index_section(
            contract,
            body=(
                "Rows list workspace actions whose execution requires explicit confirmation before mutating project files, catalog state, or configuration.",
            ),
        ),
        "",
        *_frontend_api_group_option_source_summary_section(
            contract,
            body=(
                "Rows summarize dynamic option-source dependencies by operation group, including provider operations, values paths, required context, forwarded fields, and fixed filters.",
            ),
        ),
        "",
        *_frontend_api_option_source_index_section(
            contract,
            body=(
                "Rows list form fields with SDK-owned dynamic options, including provider operation ids, payload paths, required context, forwarded fields, and fixed filters.",
            ),
        ),
        "",
        *_frontend_api_option_provider_index_section(
            contract,
            body=(
                "Rows group dynamic option-source consumers by provider operation, so GUI and SDK maintainers can audit provider APIs, dependent fields, required context, forwarded values, and fixed filters.",
            ),
        ),
        "",
        *_frontend_api_input_field_index_section(
            contract,
            body=(
                "Rows list every declared frontend operation input with type, required/default state, finite choices, frontend-to-SDK alias, and option-source provider.",
            ),
        ),
        "",
        *_frontend_api_group_form_summary_section(
            contract,
            body=(
                "Rows summarize each operation group's form footprint: operation count, input count, required fields, defaults, aliases, dynamic option sources, validation constraints, and control-kind counts.",
            ),
        ),
        "",
        *_frontend_api_operation_form_summary_section(
            contract,
            body=(
                "Rows summarize each operation's form footprint: input count, required fields, defaults, aliases, dynamic option sources, validation constraints, and control kinds.",
            ),
        ),
        "",
        *_frontend_api_form_control_index_section(
            contract,
            body=("Rows list SDK-derived form control kinds for frontend inputs, including dynamic option providers and static choices.",),
        ),
        "",
        *_frontend_api_required_input_index_section(
            contract,
            body=(
                "Rows list fields that must be supplied before action execution, including the normalizer target bucket, adapter-side alias, and option-source provider.",
            ),
        ),
        "",
        *_frontend_api_input_default_index_section(
            contract,
            body=(
                "Rows list fields that initialize frontend form state from SDK-owned defaults, including the normalizer target bucket and adapter-side alias.",
            ),
        ),
        "",
        *_frontend_api_input_constraint_index_section(
            contract,
            body=("Rows list fields with finite choices or numeric lower bounds enforced by the frontend API normalizer.",),
        ),
        "",
        *_frontend_api_input_target_index_section(
            contract,
            body=("Rows list the normalizer target bucket for every declared input field; `Maps To` is the adapter-side name used inside that bucket.",),
        ),
        "",
        *_frontend_api_input_alias_index_section(
            contract,
            body=(
                "Rows list only frontend inputs whose submitted name is remapped before adapter execution, including the normalizer target bucket and option-source provider.",
            ),
        ),
        "",
    ]


def _frontend_api_reference_chinese_intro_lines() -> list[str]:
    return [
        "由 `paradev.sdk.get_frontend_api_contract()` 生成。",
        "不要手工维护第二份前端 API 清单；请先更新 `src/paradev/sdk/frontend_api.py`，再用 `rtk uv run paradev frontend-api --markdown` 重新生成本页。",
        "TypeScript client 应用 `rtk uv run paradev frontend-api --typescript` 重新生成 `apps/desktop/src/generated/frontendApi.ts`；该文件导出 operation id union 和完整 contract。",
        "下方的 operation id、surface 名称、payload schema 和 input 名称，是 GUI、导入器、REST、MCP、VS Code 与桌面端客户端应使用的稳定 contract。",
        "workspace section 和 action 分组应通过 `get_frontend_api_workspace()` 获取，由 SDK 统一维护。",
        "workspace action row 使用 `paradev.sdk.frontend-api.action.v1`，并暴露派生的 `execution.default_surface`、`execution.available_surfaces`、`execution.confirmation`、可调用 `bindings`、`form_schema`、`normalizer_schema` 和 `rest_request_schema` 提示。",
        "`execution.confirmation` 使用 `paradev.sdk.frontend-api.confirmation.v1`；GUI shell 执行 planned REST request 前必须遵守 `required`、`scope`、`style` 和 `confirm_fields`。",
        "client 需要按 group 或 status 获取 operation id list 时，应使用 `get_frontend_api_group_operation_ids(group_id)` / TypeScript `getFrontendApiGroupOperationIds(groupId)` 和 `get_frontend_api_status_operation_ids(status)` / TypeScript `getFrontendApiStatusOperationIds(status)`，不要直接读取 raw index。",
        "client 需要按 read/write mode 获取 operation id list 时，应使用 `get_frontend_api_mode_operation_ids(mode)` / TypeScript `getFrontendApiModeOperationIds(mode)`，不要扫描 rows。",
        "surface 需要通过统一 selector 查询 flat operation-id index 时，应使用 `get_frontend_api_selection(index_name=..., key=...)`、CLI `frontend-api --index ... --key ...`、REST `GET /frontend-api?index_name=...&key=...` 或 MCP `frontend_api`。",
        "单个 operation 的详情应通过 `get_frontend_api_action(operation_id)` 获取，payload 会合并 operation row、workspace action、form、bindings 和 option-source 字段名。",
        "字段 label、description、控件、choices、边界、alias、option source 和 JSON Schema 应通过 `get_frontend_api_form(operation_id)` 获取，由 SDK 统一维护。",
        "字段 `option_source` 行使用 `paradev.sdk.frontend-api.option-source.v1`，并指向另一个 canonical operation id、列表路径和展示字段。",
        "动态选项应通过 `resolve_frontend_api_options(operation_id, field_name, values)` 或 `paradev frontend-api --option-field` 执行，由 SDK 调用对应 provider。",
        "surface call key 或整个 adapter surface 需要反查稳定 operation id 时，使用 `get_frontend_api_binding_lookup(surface, key)`、`get_frontend_api_binding_operation_ids(surface, key)`、`get_frontend_api_binding_index(surface)`、`get_frontend_api_rest_operation_ids(method, path, query)`，或 CLI `frontend-api --binding-surface ... --binding-key ...`。",
        "summary 通过 `surface_counts` 和 `group_surface_counts` 发布整体和按分组的 surface binding 覆盖；下方表格渲染的就是这些字段。",
        'client 需要列出某个 surface 支持的全部 operation id 时，应使用 `get_frontend_api_surface_operation_ids(surface)` 或 `contract["index"]["surface"]`，不要扫描 operation rows。',
        'renderer 需要列出返回同一 payload schema 的全部 operation id 时，应使用 `get_frontend_api_payload_operation_ids(payload)` 或 `contract["index"]["payload"]`；未声明 payload 的行归入 `untyped`。',
        'shell 需要列出某个 workspace section 中的全部 operation id 时，应使用 `get_frontend_api_workspace_section_operation_ids(section_id)` 或 `contract["index"]["workspace_section"]`，不要扫描 workspace rows。',
    ]


def _frontend_api_reference_chinese_lookup_sections(
    contract: Mapping[str, object],
) -> list[str]:
    return [
        *_frontend_api_index_catalog_section(
            body=("这些行说明每类 SDK-owned index 对应的 lookup helper；client 应优先使用 helper API，生成客户端才直接读取 raw contract path。",),
        ),
        "",
        *_frontend_api_group_index_section(
            contract,
            body=("按 SDK-owned operation group 汇总 canonical operation id。",),
        ),
        "",
        *_frontend_api_status_index_section(
            contract,
            body=("按 implementation status 汇总 canonical operation id。",),
        ),
        "",
        *_frontend_api_mode_index_section(
            contract,
            body=("按 operation 是否会修改项目或应用状态汇总 canonical operation id。",),
        ),
        "",
        *_frontend_api_surface_index_section(
            contract,
            body=("按 callable surface 汇总 canonical operation id；`unbound` 表示 frontend-local 或只有 contract、没有可调用 surface 的 operation。",),
        ),
        "",
        *_frontend_api_surface_coverage_section(
            contract["summary"],
            body=("计数表示每个分组中声明了对应 surface binding 的 operation row；`Unbound` 表示 frontend-local 或没有可调用 surface 的 contract row。",),
        ),
        "",
        *_frontend_api_rest_route_index_section(
            contract,
            body=(
                "按结构化 REST method、path 和 query value 汇总 canonical operation id；GUI REST client 和 OpenAPI 审计应使用这张表，不要解析 display string。",
            ),
        ),
        "",
        *_frontend_api_rest_request_planner_index_section(
            contract,
            body=("这些行列出每个 REST-bound operation 的 REST planner 输入，包括 static query defaults、path parameters 和会进入 JSON body 的字段。",),
        ),
        "",
        *_frontend_api_workspace_section_rest_summary_index_section(
            contract,
            body=(
                "这些行按 SDK-owned workspace section 汇总 REST planner coverage，包括 method distribution、static query defaults、path parameters、JSON body fields 和 dynamic query fields。",
            ),
        ),
        "",
        *_frontend_api_group_rest_summary_index_section(
            contract,
            body=(
                "这些行按 operation group 汇总 REST planner coverage，包括 method distribution、static query defaults、path parameters、JSON body fields 和 dynamic query fields。",
            ),
        ),
        "",
        *_frontend_api_rest_static_query_index_section(
            contract,
            body=("这些行列出 REST binding 声明的 fixed query parameter，包括 canonical operation id、method、path、rendered value 和 JSON value type。",),
        ),
        "",
        *_frontend_api_rest_dynamic_query_field_index_section(
            contract,
            body=(
                "这些行列出 request-plan time 会进入 REST query parameter 的 frontend input，不包括 REST path parameter 和 JSON body field；`Static Default` 表示显式提交时可覆盖 fixed binding query 的字段。",
            ),
        ),
        "",
        *_frontend_api_rest_path_parameter_index_section(
            contract,
            body=(
                "这些行列出每个会进入 REST path parameter 的 frontend input，包括 alias-aware parameter name、source field name、type、required state 和 normalizer target bucket。",
            ),
        ),
        "",
        *_frontend_api_rest_body_field_index_section(
            contract,
            body=(
                "这些行列出每个会进入 REST JSON body 的 frontend input，包括 alias-aware body name、source field name、type、required state 和 normalizer target bucket。",
            ),
        ),
        "",
        *_frontend_api_sdk_call_index_section(
            contract,
            body=("按 SDK call string 汇总 canonical operation id；Python SDK 审计应使用这张表，不要手工过滤 generic binding table。",),
        ),
        "",
        *_frontend_api_sdk_call_input_index_section(
            contract,
            body=(
                "这些行列出 SDK-bound operation 声明的 frontend input，包括 SDK call string、operation id、input type、required/default state、normalizer target bucket 和 adapter-side alias。",
            ),
        ),
        "",
        *_frontend_api_mcp_tool_index_section(
            contract,
            body=("按 MCP tool name 汇总 canonical operation id；MCP adapter 审计应使用这张表，不要手工过滤 generic binding table。",),
        ),
        "",
        *_frontend_api_mcp_tool_input_index_section(
            contract,
            body=(
                "这些行列出 MCP-bound operation 声明的 frontend input，包括 tool name、operation id、input type、required/default state、normalizer target bucket 和 adapter-side alias。",
            ),
        ),
        "",
        *_frontend_api_cli_command_index_section(
            contract,
            body=("按 CLI command string 汇总 canonical operation id；CLI adapter 审计应使用这张表，不要手工过滤 generic binding table。",),
        ),
        "",
        *_frontend_api_cli_command_input_index_section(
            contract,
            body=(
                "这些行列出 CLI-bound operation 声明的 frontend input，包括 command string、operation id、input type、required/default state、normalizer target bucket 和 adapter-side alias。",
            ),
        ),
        "",
        *_frontend_api_lsp_method_index_section(
            contract,
            body=("按 LSP method string 汇总 canonical operation id；VS Code 和 language-server 审计应使用这张表，不要手工过滤 generic binding table。",),
        ),
        "",
        *_frontend_api_lsp_method_input_index_section(
            contract,
            body=(
                "这些行列出 LSP-bound operation 声明的 frontend input，包括 LSP method string、operation id、input type、required/default state、normalizer target bucket 和 adapter-side alias。",
            ),
        ),
        "",
        *_frontend_api_binding_index_section(
            contract,
            body=("按 surface-specific call key 反查 canonical operation id；生成客户端、审计和共享 REST route 应使用这些行，不要解析 display string。",),
        ),
        "",
        *_frontend_api_group_binding_summary_index_section(
            contract,
            body=(
                "这些行按 operation group 汇总 concrete surface binding key，包括 SDK call、CLI command、REST route、MCP tool、LSP method 和 unbound operation。",
            ),
        ),
        "",
    ]


def _frontend_api_reference_chinese_detail_sections(
    contract: Mapping[str, object],
) -> list[str]:
    return [
        *_frontend_api_payload_index_section(
            contract,
            body=("按声明的 payload schema 分组 canonical operation id；`untyped` 表示 contract row 或只有 side effect、没有 typed response payload 的行。",),
        ),
        "",
        *_frontend_api_workspace_section_index_section(
            contract,
            body=("按 SDK-owned workspace section 分组 canonical operation id；default action 是该 section 的首屏目标。",),
        ),
        "",
        *_frontend_api_workspace_section_mode_status_section(
            contract,
            body=("这些行按 SDK-owned workspace section 汇总 read/write mode 和 implementation status coverage。",),
        ),
        "",
        *_frontend_api_group_mode_status_section(
            contract,
            body=("这些行按 operation group 汇总 read/write mode 和 implementation status coverage。",),
        ),
        "",
        *_frontend_api_workspace_section_payload_coverage_section(
            contract,
            body=("这些行按 SDK-owned workspace section 汇总 response payload schema；未声明 response payload 的 action 会计入 `untyped`。",),
        ),
        "",
        *_frontend_api_group_payload_coverage_section(
            contract,
            body=("这些行按 operation group 汇总 response payload schema；未声明 response payload 的 operation 会计入 `untyped`。",),
        ),
        "",
        *_frontend_api_workspace_section_surface_coverage_section(
            contract,
            body=(
                "这些行按 SDK-owned workspace section 汇总 callable surface coverage，包括 frontend-local actions、unbound actions 和 default-surface distribution。",
            ),
        ),
        "",
        *_frontend_api_workspace_section_binding_summary_section(
            contract,
            body=(
                "这些行按 SDK-owned workspace section 汇总 concrete surface binding key，包括 SDK call、CLI command、REST route、MCP tool、LSP method 和 unbound action。",
            ),
        ),
        "",
        *_frontend_api_workspace_section_form_summary_section(
            contract,
            body=(
                "这些行按 SDK-owned workspace section 汇总 action form footprint，包括 action count、input count、required fields、defaults、aliases、dynamic option sources、validation constraints 和 control-kind counts。",
            ),
        ),
        "",
        *_frontend_api_workspace_section_control_summary_section(
            contract,
            body=(
                "这些行按 workspace section 汇总 SDK-derived form control kind，包括 dynamic option-backed controls、static-choice controls 和 textarea fields。",
            ),
        ),
        "",
        *_frontend_api_group_control_summary_section(
            contract,
            body=(
                "这些行按 operation group 汇总 SDK-derived form control kind，包括 dynamic option-backed controls、static-choice controls 和 textarea fields。",
            ),
        ),
        "",
        *_frontend_api_workspace_section_option_source_summary_section(
            contract,
            body=(
                "这些行按 SDK-owned workspace section 汇总 dynamic option-source dependency，包括 provider operation、payload path、required context、forwarded field 和 fixed filter。",
            ),
        ),
        "",
        *_frontend_api_workspace_section_input_target_summary_section(
            contract,
            body=(
                "这些行按 SDK-owned workspace section 汇总 frontend input target bucket，包括 parameter、project-context、selector、projection 和 alias field。",
            ),
        ),
        "",
        *_frontend_api_group_input_target_summary_section(
            contract,
            body=("这些行按 operation group 汇总 input target bucket，包括 parameter fields、project-context fields、selectors、projections 和 aliases。",),
        ),
        "",
        *_frontend_api_workspace_section_validation_summary_section(
            contract,
            body=(
                "这些行按 SDK-owned workspace section 汇总 frontend input validation constraint，包括 constrained operation id、choice field 和 bound field。",
            ),
        ),
        "",
        *_frontend_api_group_validation_summary_section(
            contract,
            body=("这些行按 operation group 汇总 frontend input validation constraint，包括 constrained operation id、choice field 和 bound field。",),
        ),
        "",
        *_frontend_api_workspace_section_default_summary_section(
            contract,
            body=("这些行按 SDK-owned workspace section 汇总带 default 的 frontend input，包括 operation id、field name 和 literal default value。",),
        ),
        "",
        *_frontend_api_group_default_summary_section(
            contract,
            body=("这些行按 operation group 汇总带 default 的 frontend input，包括 operation id、field name 和 literal default value。",),
        ),
        "",
        *_frontend_api_workspace_section_required_summary_section(
            contract,
            body=(
                "这些行按 SDK-owned workspace section 汇总 required frontend input，包括 required operation id、field name、target bucket、option provider 和 alias。",
            ),
        ),
        "",
        *_frontend_api_group_required_summary_section(
            contract,
            body=("这些行按 operation group 汇总 required frontend input，包括 required operation id、field name、target bucket、option provider 和 alias。",),
        ),
        "",
        *_frontend_api_workspace_section_alias_summary_section(
            contract,
            body=(
                "这些行按 SDK-owned workspace section 汇总 frontend-to-SDK input alias，包括 aliased operation id、frontend field、target bucket、option provider 和 alias mapping。",
            ),
        ),
        "",
        *_frontend_api_group_alias_summary_section(
            contract,
            body=(
                "这些行按 operation group 汇总 frontend-to-SDK input alias，包括 aliased operation id、frontend field、target bucket、option provider 和 alias mapping。",
            ),
        ),
        "",
        *_frontend_api_group_execution_summary_section(
            contract,
            body=(
                "这些行按 operation group 汇总 workspace action execution policy，包括 execution kind、default surface、available surfaces、value requirements、confirmation、state scope 和 planner schema coverage。",
            ),
        ),
        "",
        *_frontend_api_workspace_section_execution_summary_section(
            contract,
            body=(
                "这些行按 SDK-owned workspace section 汇总 workspace action execution policy，包括 execution kind、default surface、available surfaces、value requirements、confirmation、state scope 和 planner schema coverage。",
            ),
        ),
        "",
        *_frontend_api_workspace_action_execution_section(
            contract,
            body=(
                "这些行列出 SDK-owned workspace action 的 execution hints，供 GUI shell 审计 default call surface、available surfaces、value requirements、frontend state scope、normalizer schema 和 REST planner schema。",
            ),
        ),
        "",
        *_frontend_api_group_confirmation_summary_section(
            contract,
            body=("这些行按 operation group 汇总需要 confirmation 的 workspace action，包括 confirmation scope、style、field 和 operation id。",),
        ),
        "",
        *_frontend_api_workspace_section_confirmation_summary_section(
            contract,
            body=("这些行按 SDK-owned workspace section 汇总需要 confirmation 的 action，包括 confirmation scope、style、field 和 operation id。",),
        ),
        "",
        *_frontend_api_confirmation_index_section(
            contract,
            body=("这些行列出执行前需要显式确认的 workspace action，用于保护 project files、catalog state 或 configuration mutation。",),
        ),
        "",
        *_frontend_api_group_option_source_summary_section(
            contract,
            body=(
                "这些行按 operation group 汇总 dynamic option-source dependency，包括 provider operation、values path、required context、forwarded fields 和 fixed filters。",
            ),
        ),
        "",
        *_frontend_api_option_source_index_section(
            contract,
            body=(
                "这些行列出带 SDK-owned dynamic option 的 form field，包括 provider operation id、payload path、required context、forwarded fields 和 fixed filters。",
            ),
        ),
        "",
        *_frontend_api_option_provider_index_section(
            contract,
            body=(
                "这些行按 provider operation 汇总 dynamic option-source consumer，方便 GUI 和 SDK 维护者审计 provider API、dependent fields、required context、forwarded values 和 fixed filters。",
            ),
        ),
        "",
        *_frontend_api_input_field_index_section(
            contract,
            body=(
                "这些行列出每个 frontend operation 声明的 input field，包括 type、required/default 状态、有限 choices、frontend-to-SDK alias 和 option-source provider。",
            ),
        ),
        "",
        *_frontend_api_group_form_summary_section(
            contract,
            body=(
                "这些行按 operation group 汇总 form footprint，包括 operation count、input count、required fields、defaults、aliases、dynamic option sources、validation constraints 和 control-kind counts。",
            ),
        ),
        "",
        *_frontend_api_operation_form_summary_section(
            contract,
            body=(
                "这些行汇总每个 operation 的 form footprint，包括 input 数、required fields、defaults、aliases、dynamic option sources、validation constraints 和 control kinds。",
            ),
        ),
        "",
        *_frontend_api_form_control_index_section(
            contract,
            body=("这些行列出 frontend input 的 SDK-derived form control kind，包括 dynamic option providers 和 static choices。",),
        ),
        "",
        *_frontend_api_required_input_index_section(
            contract,
            body=("这些行列出 action execution 前必须提交的字段，并包含 normalizer target bucket、adapter-side alias 和 option-source provider。",),
        ),
        "",
        *_frontend_api_input_default_index_section(
            contract,
            body=("这些行列出由 SDK-owned defaults 初始化 frontend form state 的字段，并包含 normalizer target bucket 与 adapter-side alias。",),
        ),
        "",
        *_frontend_api_input_constraint_index_section(
            contract,
            body=("这些行列出 frontend API normalizer 会执行校验的有限 choices 或 numeric lower bounds 字段。",),
        ),
        "",
        *_frontend_api_input_target_index_section(
            contract,
            body=("这些行列出每个 input field 的 normalizer target bucket；`Maps To` 是该 bucket 内使用的 adapter-side 名称。",),
        ),
        "",
        *_frontend_api_input_alias_index_section(
            contract,
            body=("这些行只列出 adapter execution 前需要重映射提交名称的 frontend input，并包含 normalizer target bucket 和 option-source provider。",),
        ),
        "",
    ]


def _frontend_api_reference_operation_sections(contract: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    return _frontend_api_operation_group_sections(
        contract,
        operations,
        _FRONTEND_API_REFERENCE_TABLE_LABELS,
        _frontend_api_reference_cells,
    )


def _frontend_api_sdk_cli_operation_sections(contract: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    return _frontend_api_operation_group_sections(
        contract,
        operations,
        _FRONTEND_API_SDK_CLI_TABLE_LABELS,
        _frontend_api_sdk_cli_cells,
    )


def _frontend_api_operation_group_sections(
    contract: object,
    operations: Sequence[Mapping[str, object]],
    table_labels: Sequence[str],
    cell_builder: _FrontendApiOperationCellBuilder,
) -> list[str]:
    lines: list[str] = []
    for group in _frontend_api_group_rows(contract):
        lines.extend(_frontend_api_operation_group_section(group, operations, table_labels, cell_builder))
    return lines


def _frontend_api_operation_group_section(
    group: Mapping[str, object],
    operations: Sequence[Mapping[str, object]],
    table_labels: Sequence[str],
    cell_builder: _FrontendApiOperationCellBuilder,
) -> list[str]:
    group_id = str(group["id"])
    return [
        f"### {_markdown_cell(group['title'])} (`{_markdown_cell(group_id)}`, {group['operation_count']} operations)",
        "",
        *_frontend_api_table_lines(
            table_labels,
            _frontend_api_table_rows(cell_builder(operation) for operation in operations if operation["group"] == group_id),
        ),
        "",
    ]


def _frontend_api_sdk_cli_intro_section() -> list[str]:
    return [
        "# SDK And CLI API Reference",
        "",
        "Generated from `paradev.sdk.get_frontend_api_contract()`.",
        "",
        *_frontend_api_sdk_cli_language_intro_section(
            "## English",
            "This page is the compact HoI4 modder and automation entry map. Use it when you need to know which Python SDK call or CLI command backs a project, module, collection, build, PDX, LSP, catalog, or surface operation. For REST, MCP, LSP method, payload, and binding details, read [Frontend API Reference](frontend-api-reference.md).",
            "Regenerate this file whenever the frontend API operation list changes:",
        ),
        *_frontend_api_sdk_cli_language_intro_section(
            "## 中文",
            "本页是面向 HoI4 Mod 作者和自动化脚本的紧凑入口表。需要确认某个 project、module、collection、build、PDX、LSP、catalog 或 surface 操作对应哪个 Python SDK 调用或 CLI 命令时，优先看这里。REST、MCP、LSP method、payload 和 binding 细节见 [前端 API Reference](frontend-api-reference.md)。",
            "每次 frontend API operation list 变化后，用下面的命令重新生成本文件：",
        ),
    ]


def _frontend_api_sdk_cli_language_intro_section(heading: str, body: str, regenerate_text: str) -> list[str]:
    return [
        heading,
        "",
        body,
        "",
        regenerate_text,
        "",
        "```bash",
        "rtk uv run paradev frontend-api --sdk-cli-markdown > docs/user-manual/sdk-cli-reference.md",
        "```",
        "",
    ]


def _frontend_api_sdk_cli_summary_section(summary: Mapping[str, object]) -> list[str]:
    status_counts = summary["status_counts"]
    return [
        "## Summary / 汇总",
        "",
        f"- Operations / 操作数: {summary['operation_count']}",
        f"- Implemented / 已实现: {status_counts.get('implemented', 0)}",
        f"- Frontend-local / 前端本地: {status_counts.get('frontend-local', 0)}",
        "",
    ]


def _frontend_api_sdk_cli_feature_summary_section(contract: object) -> list[str]:
    return [
        "## Feature Summary / 功能汇总",
        "",
        "Counts show how many operations each feature group exposes through Python SDK calls and CLI commands.",
        "",
        *_frontend_api_table_lines(
            ("Group", "Title", "Operations", "Python SDK", "CLI", "Read", "Write"),
            _frontend_api_sdk_cli_summary_rows(contract),
        ),
        "",
    ]


def render_frontend_api_sdk_cli_markdown() -> str:
    """Render the frontend API contract as a Python SDK and CLI matrix.

    Returns:
        Deterministic Markdown focused on Python SDK calls, CLI commands,
        frontend input names, and operation summaries.
    """

    contract = get_frontend_api_contract()
    operations = _frontend_api_operation_rows(contract)
    lines = [
        *_frontend_api_sdk_cli_intro_section(),
        *_frontend_api_sdk_cli_summary_section(contract["summary"]),
        *_frontend_api_sdk_cli_feature_summary_section(contract),
        "## Operation Matrix / 操作矩阵",
        "",
    ]
    lines.extend(_frontend_api_sdk_cli_operation_sections(contract, operations))
    return "\n".join(lines)


def _frontend_api_typescript_identifier_array_section(
    contract: Mapping[str, object],
) -> list[str]:
    operation_rows = _frontend_api_operation_rows(contract)
    group_rows = _frontend_api_group_rows(contract)
    section_rows = _frontend_api_workspace_section_rows(contract)
    return [
        f'export const PARADEV_FRONTEND_API_SCHEMA = "{FRONTEND_API_SCHEMA}" as const;',
        "",
        _typescript_const_array("PARADEV_FRONTEND_API_OPERATION_IDS", _frontend_api_row_ids(operation_rows)),
        "",
        _typescript_const_array("PARADEV_FRONTEND_API_GROUP_IDS", _frontend_api_row_ids(group_rows)),
        "",
        _typescript_const_array(
            "PARADEV_FRONTEND_API_STATUS_VALUES",
            sorted(str(status) for status in contract["index"]["status"]),
        ),
        "",
        _typescript_const_array("PARADEV_FRONTEND_API_MODE_VALUES", ["read", "write"]),
        "",
        _typescript_const_array(
            "PARADEV_FRONTEND_API_WORKSPACE_SECTION_IDS",
            _frontend_api_row_ids(section_rows),
        ),
        "",
    ]


def _frontend_api_typescript_type_section() -> list[str]:
    return [
        "export type ParaDevJsonPrimitive = string | number | boolean | null;",
        "export type ParaDevJsonValue = ParaDevJsonPrimitive | readonly ParaDevJsonValue[] | { readonly [key: string]: ParaDevJsonValue };",
        "export type ParaDevJsonObject = { readonly [key: string]: ParaDevJsonValue };",
        "",
        "export type ParaDevFrontendApiOperationId = (typeof PARADEV_FRONTEND_API_OPERATION_IDS)[number];",
        "export type ParaDevFrontendApiGroupId = (typeof PARADEV_FRONTEND_API_GROUP_IDS)[number];",
        "export type ParaDevFrontendApiStatus = (typeof PARADEV_FRONTEND_API_STATUS_VALUES)[number];",
        "export type ParaDevFrontendApiMode = (typeof PARADEV_FRONTEND_API_MODE_VALUES)[number];",
        "export type ParaDevFrontendApiWorkspaceSectionId = (typeof PARADEV_FRONTEND_API_WORKSPACE_SECTION_IDS)[number];",
        "",
        "export type ParaDevFrontendApiContract = {",
        "  readonly schema: typeof PARADEV_FRONTEND_API_SCHEMA;",
        "  readonly summary: ParaDevJsonObject;",
        "  readonly groups: readonly ParaDevJsonObject[];",
        "  readonly operations: readonly ParaDevJsonObject[];",
        "  readonly index: ParaDevJsonObject;",
        "  readonly inspection_contract: ParaDevJsonObject;",
        "  readonly workspace: ParaDevJsonObject;",
        "  readonly [key: string]: ParaDevJsonValue;",
        "};",
        "",
    ]


def _frontend_api_typescript_contract_section(
    contract: Mapping[str, object],
) -> list[str]:
    contract_source = dumps_json(contract, indent=2).rstrip()
    return [
        f"export const PARADEV_FRONTEND_API_CONTRACT = {contract_source} as const satisfies ParaDevFrontendApiContract;",
        "",
    ]


def render_frontend_api_typescript() -> str:
    """Render the frontend API contract as a generated TypeScript module.

    Returns:
        Deterministic TypeScript source for desktop and generated clients. The
        module exports operation/group/status/section id unions plus the full
        JSON contract as `PARADEV_FRONTEND_API_CONTRACT`.
    """

    contract = get_frontend_api_contract()
    lines = [
        "/* Generated by `rtk uv run paradev frontend-api --typescript`; do not edit by hand. */",
        "",
        *_frontend_api_typescript_identifier_array_section(contract),
        *_frontend_api_typescript_type_section(),
        *_frontend_api_typescript_contract_section(contract),
    ]
    return "\n".join(lines)


def get_frontend_api_operation(operation_id: str) -> dict[str, object]:
    """Return one canonical frontend operation row by id.

    Args:
        operation_id: Stable operation id such as `project.create` or
            `module.list`.

    Returns:
        JSON-safe operation row copied from `get_frontend_api_contract()`.

    Raises:
        ValueError: If `operation_id` is not listed in the frontend contract.
    """

    return _frontend_api_operation_row(operation_id, _frontend_api_operations())


def _frontend_api_operation_row(operation_id: str, operations: Sequence[dict[str, object]]) -> dict[str, object]:
    rows = _frontend_api_operation_row_map(operations)
    try:
        return dict(rows[operation_id])
    except KeyError as error:
        _raise_unknown_frontend_api_key("operation", operation_id, "operations", sorted(rows), cause=error)


def _frontend_api_operation_row_map(
    operations: Sequence[dict[str, object]],
) -> dict[str, dict[str, object]]:
    return {str(row["id"]): row for row in operations}


def get_frontend_api_group(group_id: str) -> dict[str, object]:
    """Return one frontend API group and its operation rows.

    Args:
        group_id: Stable group id such as `projects`, `modules`, or `lsp`.

    Returns:
        JSON-safe group slice with copied group metadata, operation ids,
        operation rows, and indexes scoped to that group.

    Raises:
        ValueError: If `group_id` is not listed in the frontend contract.
    """

    all_operations = _frontend_api_operations()
    group = _frontend_api_group_row(group_id, all_operations)
    operations = _frontend_api_group_operations(group_id, all_operations)
    return _frontend_api_group_payload(group, operations)


def _frontend_api_group_row(group_id: str, operations: Sequence[dict[str, object]]) -> dict[str, object]:
    groups = {str(group["id"]): group for group in _frontend_api_groups(operations)}
    try:
        return dict(groups[group_id])
    except KeyError as error:
        _raise_unknown_frontend_api_key("group", group_id, "groups", sorted(groups), cause=error)


def _frontend_api_group_operations(group_id: str, operations: Sequence[dict[str, object]]) -> list[dict[str, object]]:
    return [row for row in operations if row["group"] == group_id]


def _frontend_api_group_payload(group: Mapping[str, object], operations: Sequence[dict[str, object]]) -> dict[str, object]:
    return {
        "schema": FRONTEND_API_SCHEMA,
        "status": "alpha",
        "sdk_owned": True,
        "group": dict(group),
        "operation_ids": [str(row["id"]) for row in operations],
        "operations": [dict(row) for row in operations],
        "index": _frontend_api_index(operations),
    }


def get_frontend_api_group_operation_ids(group_id: str) -> list[str]:
    """Return frontend operation ids assigned to one operation group.

    Args:
        group_id: Stable group id such as `projects`, `modules`, or `lsp`.

    Returns:
        Copied list of stable frontend API operation ids in that group.

    Raises:
        ValueError: If `group_id` is not listed in the frontend contract.
    """

    return _frontend_api_index_operation_ids(
        "group",
        group_id,
        key_label="group",
        choices_label="groups",
    )


def _frontend_api_selection_index_operation_ids(index_name: str, key: str) -> list[str]:
    if index_name == "group":
        return get_frontend_api_group_operation_ids(key)
    if index_name == "status":
        return get_frontend_api_status_operation_ids(key)
    if index_name == "mode":
        return get_frontend_api_mode_operation_ids(key)
    if index_name == "surface":
        return get_frontend_api_surface_operation_ids(key)
    if index_name == "payload":
        return get_frontend_api_payload_operation_ids(key)
    if index_name == "workspace_section":
        return get_frontend_api_workspace_section_operation_ids(key)
    _raise_unsupported_frontend_api_key(
        "index",
        index_name,
        "indexes",
        ("group", "status", "mode", "surface", "payload", "workspace_section"),
    )


def _frontend_api_operation_id_list(operation_ids: object) -> list[str]:
    if not _is_frontend_api_operation_id_sequence(operation_ids):
        return []
    return [str(operation_id) for operation_id in operation_ids]


def _is_frontend_api_operation_id_sequence(operation_ids: object) -> bool:
    return isinstance(operation_ids, Sequence) and not isinstance(operation_ids, (str, bytes))


def _frontend_api_index_map(index_name: str) -> Mapping[str, object] | None:
    index = get_frontend_api_contract()["index"]
    index_map = index.get(index_name) if isinstance(index, Mapping) else None
    if not isinstance(index_map, Mapping):
        return None
    return index_map


def _frontend_api_operation_id_index(
    rows: Mapping[str, object],
) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for key, operation_ids in rows.items():
        if _is_frontend_api_operation_id_sequence(operation_ids):
            index[str(key)] = _frontend_api_operation_id_list(operation_ids)
    return index


def _frontend_api_choices(values: Iterable[object]) -> str:
    return ", ".join(str(value) for value in values)


def _raise_unknown_frontend_api_key(
    key_label: str,
    key: str,
    choices_label: str,
    choices: Iterable[object],
    *,
    cause: BaseException | None = None,
) -> NoReturn:
    choices_text = _frontend_api_choices(choices)
    raise ValueError(f"Unknown frontend API {key_label}: {key}. Available {choices_label}: {choices_text}.") from cause


def _raise_unsupported_frontend_api_key(
    key_label: str,
    key: str,
    choices_label: str,
    choices: Iterable[object],
) -> NoReturn:
    choices_text = _frontend_api_choices(choices)
    raise ValueError(f"Unsupported frontend API {key_label}: {key}. Available {choices_label}: {choices_text}.")


def _frontend_api_index_operation_ids(
    index_name: str,
    key: str,
    *,
    key_label: str,
    choices_label: str,
    supported_values: Sequence[str] | None = None,
    allow_unknown: bool = False,
) -> list[str]:
    operation_index = _frontend_api_index_map(index_name)
    if operation_index is None:
        return []
    _validate_frontend_api_supported_index_key(
        key_label,
        key,
        choices_label,
        supported_values,
    )
    if not _frontend_api_index_contains_key(
        operation_index,
        key,
        key_label=key_label,
        choices_label=choices_label,
        allow_unknown=allow_unknown,
    ):
        return []
    return _frontend_api_operation_id_list(operation_index.get(key, []))


def _validate_frontend_api_supported_index_key(
    key_label: str,
    key: str,
    choices_label: str,
    supported_values: Sequence[str] | None,
) -> None:
    if supported_values is None or key in supported_values:
        return
    _raise_unsupported_frontend_api_key(key_label, key, choices_label, supported_values)


def _frontend_api_index_contains_key(
    operation_index: Mapping[str, object],
    key: str,
    *,
    key_label: str,
    choices_label: str,
    allow_unknown: bool,
) -> bool:
    if key in operation_index:
        return True
    if allow_unknown:
        return False
    _raise_unknown_frontend_api_key(key_label, key, choices_label, operation_index)


def get_frontend_api_status_operation_ids(status: str) -> list[str]:
    """Return frontend operation ids assigned to one implementation status.

    Args:
        status: Operation status such as `implemented`, `planned`, or
            `frontend-local`.

    Returns:
        Copied list of stable frontend API operation ids with that status.

    Raises:
        ValueError: If `status` is not listed in the frontend contract.
    """

    return _frontend_api_index_operation_ids(
        "status",
        status,
        key_label="status",
        choices_label="statuses",
    )


def get_frontend_api_mode_operation_ids(mode: str) -> list[str]:
    """Return frontend operation ids assigned to one read/write mode.

    Args:
        mode: Operation mode, either `read` for non-mutating rows or `write`
            for mutating rows.

    Returns:
        Copied list of stable frontend API operation ids with that mode.

    Raises:
        ValueError: If `mode` is not listed in the frontend contract.
    """

    return _frontend_api_index_operation_ids(
        "mode",
        mode,
        key_label="mode",
        choices_label="modes",
    )


def build_frontend_api_rest_index_key(method: str, path: str, query: Mapping[str, object] | None = None) -> str:
    """Return the stable reverse-index key for a REST frontend API binding.

    Args:
        method: HTTP method such as `GET` or `POST`.
        path: REST path such as `/projects/inspect`.
        query: Optional query values. Keys are sorted, and `None` values are
            ignored so callers can pass partially filled request plans.

    Returns:
        Stable key used by `get_frontend_api_contract()["index"]["binding"]["rest"]`.
    """

    return _rest_index_key(_frontend_api_rest_index_binding(method, path, query))


def _frontend_api_rest_index_binding(
    method: str,
    path: str,
    query: Mapping[str, object] | None,
) -> dict[str, object]:
    return {
        "method": method,
        "path": path,
        "query": _frontend_api_rest_index_query(query),
    }


def _frontend_api_rest_index_query(
    query: Mapping[str, object] | None,
) -> dict[str, object]:
    filtered_query: dict[str, object] = {}
    for key, value in dict(query or {}).items():
        if value is not None:
            filtered_query[str(key)] = value
    return filtered_query


def get_frontend_api_binding_operation_ids(surface: str, key: str) -> list[str]:
    """Return frontend operation ids for a surface call key.

    Args:
        surface: Binding surface, one of `cli`, `lsp`, `mcp`, `rest`, or `sdk`.
        key: Surface-specific call key, such as `project`, `project_inspect`,
            `textDocument/hover`, or `GET /projects`.

    Returns:
        Copied list of stable frontend API operation ids. Unknown keys return
        an empty list so callers can probe shared routes without exception
        handling.

    Raises:
        ValueError: If `surface` is not a supported frontend API binding surface.
    """

    surface_index = _frontend_api_binding_surface_index(surface)
    if surface_index is None:
        return []
    return _frontend_api_operation_id_list(surface_index.get(key, []))


def get_frontend_api_binding_index(surface: str) -> dict[str, list[str]]:
    """Return the reverse binding index for one callable surface.

    Args:
        surface: Binding surface, one of `cli`, `lsp`, `mcp`, `rest`, or `sdk`.

    Returns:
        Copied map from surface-specific call keys to stable frontend API
        operation ids. Unknown call keys are omitted.

    Raises:
        ValueError: If `surface` is not a supported frontend API binding surface.
    """

    surface_index = _frontend_api_binding_surface_index(surface)
    if surface_index is None:
        return {}
    return _frontend_api_operation_id_index(surface_index)


def _frontend_api_binding_surface_index(surface: str) -> Mapping[str, object] | None:
    _validate_frontend_api_supported_index_key(
        "binding surface",
        surface,
        "surfaces",
        FRONTEND_API_BINDING_SURFACES,
    )

    binding_index = _frontend_api_index_map("binding")
    surface_index = binding_index.get(surface) if binding_index is not None else None
    if not isinstance(surface_index, Mapping):
        return None
    return surface_index


def get_frontend_api_binding_lookup(surface: str, key: str) -> dict[str, object]:
    """Return a JSON-safe binding reverse-lookup payload.

    Args:
        surface: Binding surface, one of `cli`, `lsp`, `mcp`, `rest`, or `sdk`.
        key: Surface-specific call key, such as `project`, `project_inspect`,
            `textDocument/hover`, or `GET /projects`.

    Returns:
        JSON-safe payload with the surface, key, matching operation ids, and
        count. Unknown keys return an empty operation list.

    Raises:
        ValueError: If `surface` is not a supported frontend API binding surface.
    """

    operation_ids = get_frontend_api_binding_operation_ids(surface, key)
    return _frontend_api_binding_lookup_payload(surface, key, operation_ids)


def _frontend_api_binding_lookup_payload(
    surface: str,
    key: str,
    operation_ids: Sequence[str],
) -> dict[str, object]:
    return {
        "schema": FRONTEND_API_BINDING_LOOKUP_SCHEMA,
        "surface": surface,
        "key": key,
        "operation_ids": operation_ids,
        "count": len(operation_ids),
    }


def get_frontend_api_rest_operation_ids(
    method: str,
    path: str,
    query: Mapping[str, object] | None = None,
) -> list[str]:
    """Return frontend operation ids for a REST method, path, and query.

    Args:
        method: HTTP method such as `GET` or `POST`.
        path: REST path such as `/projects/inspect`.
        query: Optional query values used to disambiguate shared routes.

    Returns:
        Copied list of stable frontend API operation ids for the REST binding.
    """

    return get_frontend_api_binding_operation_ids("rest", build_frontend_api_rest_index_key(method, path, query))


def get_frontend_api_surface_operation_ids(surface: str) -> list[str]:
    """Return frontend operation ids exposed by one callable surface.

    Args:
        surface: Callable surface, one of `cli`, `lsp`, `mcp`, `rest`, `sdk`,
            or `unbound` for frontend-local or contract-only rows.

    Returns:
        Copied list of stable frontend API operation ids backed by that
        surface.

    Raises:
        ValueError: If `surface` is not a supported frontend API surface.
    """

    return _frontend_api_index_operation_ids(
        "surface",
        surface,
        key_label="surface",
        choices_label="surfaces",
        supported_values=_FRONTEND_API_SURFACE_INDEX_VALUES,
        allow_unknown=True,
    )


def get_frontend_api_payload_operation_ids(payload: str) -> list[str]:
    """Return frontend operation ids that declare one payload schema.

    Args:
        payload: Payload schema name such as `Project.to_view`; use `untyped`
            for rows without a declared response payload.

    Returns:
        Copied list of stable frontend API operation ids. Unknown payload
        names return an empty list so renderers can probe optional payload
        handlers without exception handling.
    """

    return _frontend_api_index_operation_ids(
        "payload",
        payload,
        key_label="payload",
        choices_label="payloads",
        allow_unknown=True,
    )


def get_frontend_api_workspace_section_operation_ids(section_id: str) -> list[str]:
    """Return frontend operation ids assigned to one workspace section.

    Args:
        section_id: SDK-owned workspace section id such as `project-switcher`,
            `authoring`, `catalog`, or `surface-contracts`.

    Returns:
        Copied list of stable frontend API operation ids in that section.

    Raises:
        ValueError: If `section_id` is not a supported workspace section.
    """

    return _frontend_api_index_operation_ids(
        "workspace_section",
        section_id,
        key_label="workspace section",
        choices_label="sections",
    )


def get_frontend_api_form(operation_id: str) -> dict[str, object]:
    """Return the derived frontend form contract for one operation.

    Args:
        operation_id: Stable operation id such as `module.edit` or
            `build.artifacts`.

    Returns:
        JSON-safe form payload derived from the operation row `inputs`. The
        payload includes normalized fields, SDK-owned labels/descriptions,
        required field names, defaults, frontend-to-SDK aliases, finite
        choices, numeric bounds, and a small object JSON Schema.

    Raises:
        ValueError: If `operation_id` is not listed in the frontend contract.
    """

    operation = get_frontend_api_operation(operation_id)
    fields = _frontend_api_form_fields(operation)
    required = _frontend_api_form_required_names(fields)
    defaults = _frontend_api_form_defaults(fields)
    aliases = _frontend_api_form_aliases(fields)
    return _frontend_api_form_payload(operation, fields, required, defaults, aliases)


def _frontend_api_form_fields(operation: dict[str, object]) -> list[dict[str, object]]:
    return [_frontend_api_form_field(operation, field) for field in operation.get("inputs", []) if isinstance(field, dict)]


def _frontend_api_form_required_names(
    fields: Sequence[Mapping[str, object]],
) -> list[str]:
    return [str(field["name"]) for field in fields if field["required"]]


def _frontend_api_form_defaults(
    fields: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    return {str(field["name"]): field["default"] for field in fields if "default" in field}


def _frontend_api_form_aliases(
    fields: Sequence[Mapping[str, object]],
) -> dict[str, str]:
    return {str(field["name"]): str(field["maps_to"]) for field in fields if "maps_to" in field}


def _frontend_api_form_json_schema(
    fields: Sequence[Mapping[str, object]],
    required: Sequence[str],
) -> dict[str, object]:
    return {
        "type": "object",
        "properties": {str(field["name"]): field["schema"] for field in fields},
        "required": list(required),
        "additionalProperties": False,
    }


def _frontend_api_form_payload(
    operation: Mapping[str, object],
    fields: list[dict[str, object]],
    required: list[str],
    defaults: Mapping[str, object],
    aliases: Mapping[str, str],
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": FRONTEND_API_FORM_SCHEMA,
        "operation_id": operation["id"],
        "group": operation["group"],
        "action": operation["action"],
        "status": operation["status"],
        "read_only": operation["read_only"],
        "fields": fields,
        "required": required,
        "defaults": defaults,
        "aliases": aliases,
        "json_schema": _frontend_api_form_json_schema(fields, required),
        "operation": operation,
    }
    if operation.get("mutates"):
        payload["mutates"] = True
    return payload


def normalize_frontend_api_inputs(operation_id: str, values: Mapping[str, object] | None = None) -> dict[str, object]:
    """Normalize frontend form values into adapter input buckets.

    Args:
        operation_id: Stable operation id such as `module.edit`.
        values: Frontend-submitted values keyed by operation input name.

    Returns:
        JSON-safe payload with normalized frontend values plus separate
        `project`, `parameters`, `selectors`, and `projections` buckets. Field
        aliases such as `artifact_path -> path` are applied only inside the
        bucket targeted by the form field, so project path and artifact path do
        not collide.

    Raises:
        ValueError: If `operation_id` is unknown, a submitted value is not part
            of the form contract, a required field is missing, or two fields map
            to the same target in one bucket.
    """

    submitted = dict(values or {})
    form = get_frontend_api_form(operation_id)
    fields = _frontend_api_normalization_fields(form)
    _reject_unknown_frontend_api_inputs(operation_id, submitted, fields)

    normalized_values, buckets, missing = _frontend_api_collect_normalized_inputs(
        operation_id,
        form,
        fields,
        submitted,
    )
    if missing:
        _raise_missing_frontend_api_inputs(operation_id, missing)
    if operation_id == "catalog.query":
        normalize_catalog_query_filters(normalized_values)

    return _frontend_api_normalized_inputs_payload(form, normalized_values, buckets)


def _frontend_api_collect_normalized_inputs(
    operation_id: str,
    form: Mapping[str, object],
    fields: Sequence[Mapping[str, object]],
    submitted: Mapping[str, object],
) -> tuple[dict[str, object], _FrontendApiInputBuckets, list[str]]:
    normalized_values: dict[str, object] = {}
    buckets = _frontend_api_input_buckets()
    missing: list[str] = []
    for field in fields:
        has_value, value = _frontend_api_input_value(field, submitted, missing)
        if not has_value:
            continue
        _add_frontend_api_normalized_input(
            operation_id,
            form,
            field,
            value,
            normalized_values,
            buckets,
        )
    return normalized_values, buckets, missing


def _raise_missing_frontend_api_inputs(operation_id: str, missing: Sequence[str]) -> NoReturn:
    names = ", ".join(missing)
    raise ValueError(f"Missing required frontend API inputs for {operation_id}: {names}.")


def _frontend_api_normalization_fields(
    form: Mapping[str, object],
) -> list[dict[str, object]]:
    return [field for field in form["fields"] if isinstance(field, dict)]


def _reject_unknown_frontend_api_inputs(
    operation_id: str,
    submitted: Mapping[str, object],
    fields: Sequence[Mapping[str, object]],
) -> None:
    unknown = _frontend_api_unknown_input_names(submitted, fields)
    if unknown:
        _raise_unsupported_frontend_api_inputs(operation_id, unknown)


def _frontend_api_unknown_input_names(
    submitted: Mapping[str, object],
    fields: Sequence[Mapping[str, object]],
) -> list[str]:
    field_names = {str(field["name"]) for field in fields}
    return sorted(set(submitted) - field_names)


def _raise_unsupported_frontend_api_inputs(operation_id: str, unknown: Sequence[str]) -> NoReturn:
    names = ", ".join(unknown)
    raise ValueError(f"Unsupported frontend API inputs for {operation_id}: {names}.")


def _frontend_api_input_buckets() -> _FrontendApiInputBuckets:
    return {name: {} for name in _FRONTEND_API_INPUT_BUCKET_NAMES}


def _frontend_api_input_value(
    field: Mapping[str, object],
    submitted: Mapping[str, object],
    missing: list[str],
) -> tuple[bool, object]:
    name = str(field["name"])
    if name in submitted:
        value = submitted[name]
    elif "default" in field:
        value = field["default"]
    else:
        return _frontend_api_missing_input_value(name, field, missing)

    if value is None:
        return _frontend_api_missing_input_value(name, field, missing)
    return True, value


def _frontend_api_missing_input_value(
    name: str,
    field: Mapping[str, object],
    missing: list[str],
) -> tuple[bool, object]:
    if field.get("required"):
        missing.append(name)
    return False, None


def _add_frontend_api_normalized_input(
    operation_id: str,
    form: Mapping[str, object],
    field: Mapping[str, object],
    value: object,
    normalized_values: dict[str, object],
    buckets: _FrontendApiInputBuckets,
) -> None:
    _validate_frontend_api_input_value(str(form["operation_id"]), field, value)
    name = str(field["name"])
    normalized_values[name] = value
    target = str(field["target"])
    target_name = _frontend_api_mapped_input_name(field)
    _add_frontend_api_target_bucket_value(operation_id, buckets, target, target_name, value)


def _add_frontend_api_target_bucket_value(
    operation_id: str,
    buckets: _FrontendApiInputBuckets,
    target: str,
    target_name: str,
    value: object,
) -> None:
    bucket = buckets[target]
    if target_name in bucket:
        raise ValueError(f"Frontend API input mapping collision for {operation_id}: {target}.{target_name}.")
    bucket[target_name] = value


def _frontend_api_normalized_inputs_payload(
    form: Mapping[str, object],
    normalized_values: Mapping[str, object],
    buckets: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    payload = {
        "schema": FRONTEND_API_INPUTS_SCHEMA,
        "operation_id": form["operation_id"],
        "group": form["group"],
        "action": form["action"],
        "status": form["status"],
        "read_only": form["read_only"],
        "values": normalized_values,
    }
    payload.update(_frontend_api_normalized_input_bucket_payload(buckets))
    payload["aliases"] = form["aliases"]
    return payload


def _frontend_api_normalized_input_bucket_payload(
    buckets: Mapping[str, Mapping[str, object]],
) -> dict[str, Mapping[str, object]]:
    return {name: buckets[name] for name in _FRONTEND_API_INPUT_BUCKET_NAMES}


def plan_frontend_api_rest_request(operation_id: str, values: Mapping[str, object] | None = None) -> dict[str, object]:
    """Plan one REST request from frontend form values.

    Args:
        operation_id: Stable operation id such as `module.edit`.
        values: Frontend-submitted values keyed by operation input name.

    Returns:
        JSON-safe REST request plan with method, path, query parameters, JSON
        body, source binding, and the normalized frontend input buckets.

    Raises:
        ValueError: If the operation is frontend-local, unknown, has no REST
            binding, or the submitted values fail frontend input normalization.
    """

    submitted = dict(values or {})
    operation, rest_binding = _frontend_api_rest_operation_binding(operation_id)
    normalized = normalize_frontend_api_inputs(operation_id, submitted)
    path, query, body = _frontend_api_rest_request_parts(operation_id, operation, rest_binding, submitted, normalized)
    return _frontend_api_rest_request_payload(operation_id, rest_binding, path, query, body, normalized)


def _frontend_api_rest_operation_binding(
    operation_id: str,
) -> tuple[dict[str, object], dict[str, object]]:
    operation = get_frontend_api_operation(operation_id)
    if operation["status"] == "frontend-local":
        raise ValueError(f"Cannot plan REST request for frontend-local operation: {operation_id}.")
    bindings = operation.get("bindings")
    rest_binding = bindings.get("rest") if isinstance(bindings, dict) else None
    if not isinstance(rest_binding, dict):
        raise ValueError(f"Frontend API operation does not expose a REST binding: {operation_id}.")
    return operation, rest_binding


def _frontend_api_rest_request_parts(
    operation_id: str,
    operation: dict[str, object],
    rest_binding: Mapping[str, object],
    submitted: Mapping[str, object],
    normalized: dict[str, object],
) -> tuple[str, dict[str, object], dict[str, object]]:
    candidates = _rest_request_candidates(normalized)
    path = _fill_rest_path_parameters(str(rest_binding["path"]), candidates)
    query, body = _frontend_api_rest_query_body(operation_id, operation, rest_binding, submitted, candidates)
    return path, query, body


def _frontend_api_rest_query_body(
    operation_id: str,
    operation: dict[str, object],
    rest_binding: Mapping[str, object],
    submitted: Mapping[str, object],
    candidates: Mapping[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    query, body, body_names, explicit_query_names = _frontend_api_rest_query_body_context(
        operation_id,
        operation,
        rest_binding,
        submitted,
    )
    for name, value in candidates.items():
        _add_frontend_api_rest_candidate(name, value, query, body, body_names, explicit_query_names)
    return query, body


def _frontend_api_rest_query_body_context(
    operation_id: str,
    operation: dict[str, object],
    rest_binding: Mapping[str, object],
    submitted: Mapping[str, object],
) -> _FrontendApiRestQueryBodyContext:
    query = dict(rest_binding.get("query", {}))
    body: dict[str, object] = {}
    body_names = _rest_body_inputs(operation_id, operation)
    explicit_query_names = _submitted_target_names(operation_id, submitted) - body_names
    return query, body, body_names, explicit_query_names


def _add_frontend_api_rest_candidate(
    name: str,
    value: object,
    query: dict[str, object],
    body: dict[str, object],
    body_names: set[str],
    explicit_query_names: set[str],
) -> None:
    if name in body_names:
        body[name] = value
    elif name in query and name not in explicit_query_names:
        return
    else:
        query[name] = value


def _frontend_api_rest_request_payload(
    operation_id: str,
    rest_binding: Mapping[str, object],
    path: str,
    query: Mapping[str, object],
    body: Mapping[str, object],
    normalized: Mapping[str, object],
) -> dict[str, object]:
    return {
        "schema": FRONTEND_API_REST_REQUEST_SCHEMA,
        "operation_id": operation_id,
        "method": rest_binding["method"],
        "path": path,
        "query": query,
        "body": body,
        "binding": dict(rest_binding),
        "normalized": normalized,
    }


def resolve_frontend_api_options(operation_id: str, field_name: str, values: Mapping[str, object] | None = None) -> dict[str, object]:
    """Resolve dynamic frontend options for one form field.

    Args:
        operation_id: Stable consumer operation id such as `module.create`.
        field_name: Field in that operation's form whose `option_source`
            should be executed.
        values: Current frontend form values. Defaults from the consumer form
            are applied before checking option-source requirements.

    Returns:
        JSON-safe option payload with `value`, `label`, `details`, and source
        row data for each option. If a required upstream field is absent, the
        payload has `available=False`, `missing_requirements`, and no options
        instead of raising.

    Raises:
        ValueError: If the consumer operation or field is unknown, the field
            has no `option_source`, the provider is not a supported SDK-owned
            option provider, or provider input normalization fails.
    """

    submitted = dict(values or {})
    form = get_frontend_api_form(operation_id)
    field = _frontend_api_form_field_by_name(form, field_name)
    option_source = _frontend_api_required_field_option_source(operation_id, field_name, field)

    consumer_values = _frontend_api_option_consumer_values(form, submitted)
    provider_id = _frontend_api_option_source_required_operation_id(option_source)
    provider_values = _frontend_api_option_provider_values(option_source, consumer_values)
    missing_requirements = _frontend_api_missing_option_requirements(option_source, consumer_values)
    base_payload = _frontend_api_options_base_payload(
        operation_id,
        field_name,
        option_source,
        provider_id,
        provider_values,
        missing_requirements,
    )
    if missing_requirements:
        return base_payload

    provider_payload = _execute_frontend_api_option_provider(provider_id, provider_values)
    return _frontend_api_options_resolved_payload(base_payload, provider_payload, option_source)


def _frontend_api_options_resolved_payload(
    base_payload: dict[str, object],
    provider_payload: Mapping[str, object],
    option_source: Mapping[str, object],
) -> dict[str, object]:
    _set_frontend_api_option_provider_schema(base_payload, provider_payload)
    _set_frontend_api_option_rows(base_payload, provider_payload, option_source)
    return base_payload


def _set_frontend_api_option_provider_schema(
    payload: dict[str, object],
    provider_payload: Mapping[str, object],
) -> None:
    provider_schema = provider_payload.get("schema")
    if isinstance(provider_schema, str):
        payload["provider_payload_schema"] = provider_schema


def _set_frontend_api_option_rows(
    payload: dict[str, object],
    provider_payload: Mapping[str, object],
    option_source: Mapping[str, object],
) -> None:
    rows = _frontend_api_values_path(
        provider_payload,
        _frontend_api_option_source_required_values_path(option_source),
    )
    options = _frontend_api_option_rows(rows, option_source)
    payload["options"] = options
    payload["count"] = len(options)


def _frontend_api_options_base_payload(
    operation_id: str,
    field_name: str,
    option_source: Mapping[str, object],
    provider_id: str,
    provider_values: Mapping[str, object],
    missing_requirements: Sequence[str],
) -> dict[str, object]:
    return {
        "schema": FRONTEND_API_OPTIONS_SCHEMA,
        "operation_id": operation_id,
        "field_name": field_name,
        "available": not missing_requirements,
        "missing_requirements": missing_requirements,
        "option_source": _copy_option_source(option_source),
        "provider_operation_id": provider_id,
        "provider_values": provider_values,
        "provider_payload_schema": "",
        "options": [],
        "count": 0,
    }


def _frontend_api_form_field_by_name(form: Mapping[str, object], field_name: str) -> dict[str, object]:
    fields = form.get("fields")
    if isinstance(fields, Sequence) and not isinstance(fields, (str, bytes)):
        for field in fields:
            if isinstance(field, dict) and field.get("name") == field_name:
                return dict(field)
    operation_id = str(form.get("operation_id", "unknown"))
    raise ValueError(f"Unknown frontend API field for {operation_id}: {field_name}.")


def _frontend_api_required_field_option_source(
    operation_id: str,
    field_name: str,
    field: Mapping[str, object],
) -> Mapping[str, object]:
    option_source = _frontend_api_field_option_source(field)
    if option_source is not None:
        return option_source
    raise ValueError(f"Frontend API field {operation_id}.{field_name} does not expose option_source.")


def _frontend_api_option_consumer_values(form: Mapping[str, object], submitted: Mapping[str, object]) -> dict[str, object]:
    defaults = form.get("defaults")
    values = dict(defaults) if isinstance(defaults, Mapping) else {}
    values.update(submitted)
    return values


def _frontend_api_missing_option_requirements(option_source: Mapping[str, object], values: Mapping[str, object]) -> list[str]:
    missing: list[str] = []
    for name in _frontend_api_option_source_requires(option_source):
        key = str(name)
        if key not in values or values[key] is None:
            missing.append(key)
    return missing


def _frontend_api_option_provider_values(option_source: Mapping[str, object], values: Mapping[str, object]) -> dict[str, object]:
    filters = _frontend_api_option_source_filters(option_source)
    provider_values = dict(filters) if isinstance(filters, Mapping) else {}
    for name in _frontend_api_option_source_forward(option_source):
        _add_frontend_api_option_provider_forward_value(provider_values, values, name)
    return provider_values


def _add_frontend_api_option_provider_forward_value(
    provider_values: dict[str, object],
    values: Mapping[str, object],
    name: object,
) -> None:
    key = str(name)
    if key not in values or values[key] is None or key in provider_values:
        return
    provider_values[key] = values[key]


def _execute_frontend_api_option_provider(provider_id: str, provider_values: Mapping[str, object]) -> dict[str, object]:
    project, parameters = _frontend_api_option_provider_inputs(provider_id, provider_values)

    if provider_id == "module.templates":
        return project.templates(**parameters)

    provider_operation = get_frontend_api_operation(provider_id)
    inspection_kind = _frontend_api_inspection_provider_kind(provider_operation)
    if inspection_kind:
        return project.inspect(inspection_kind, **parameters)

    raise ValueError(f"Frontend API option provider is not supported by the SDK resolver: {provider_id}.")


def _frontend_api_option_provider_inputs(
    provider_id: str,
    provider_values: Mapping[str, object],
) -> _FrontendApiOptionProviderInputs:
    normalized = normalize_frontend_api_inputs(provider_id, provider_values)
    project_values = normalized["project"]
    parameters = normalized["parameters"]
    if not isinstance(project_values, Mapping) or not isinstance(parameters, Mapping):
        raise ValueError(f"Frontend API option provider produced invalid normalized buckets: {provider_id}.")
    return open_project(str(project_values.get("path", "."))), parameters


def _frontend_api_inspection_provider_kind(operation: Mapping[str, object]) -> str:
    bindings = operation.get("bindings")
    rest_binding = bindings.get("rest") if isinstance(bindings, Mapping) else None
    query = rest_binding.get("query") if isinstance(rest_binding, Mapping) else None
    kind = query.get("kind") if isinstance(query, Mapping) else None
    return str(kind) if isinstance(kind, str) and kind else ""


def _frontend_api_values_path(payload: Mapping[str, object], values_path: object) -> list[object]:
    segments = _frontend_api_values_path_segments(values_path)
    path = _frontend_api_values_path_label(segments)
    current = _frontend_api_values_path_value(payload, segments, path)
    return _frontend_api_values_path_list(current, path)


def _frontend_api_values_path_value(
    payload: Mapping[str, object],
    segments: Sequence[object],
    path: str,
) -> object:
    current: object = payload
    for segment in segments:
        current = _frontend_api_values_path_step(current, segment, path)
    return current


def _frontend_api_values_path_step(current: object, segment: object, path: str) -> object:
    key = str(segment)
    if not isinstance(current, Mapping) or key not in current:
        raise ValueError(f"Frontend API option provider payload does not contain values_path {path}.")
    return current[key]


def _frontend_api_values_path_list(current: object, path: str) -> list[object]:
    if not isinstance(current, Sequence) or isinstance(current, (str, bytes)):
        raise ValueError(f"Frontend API option provider values_path is not a list: {path}.")
    return list(current)


def _frontend_api_values_path_segments(values_path: object) -> list[object]:
    return _input_choices(values_path)


def _frontend_api_values_path_label(segments: Sequence[object]) -> str:
    return ".".join(str(part) for part in segments)


def _frontend_api_option_rows(rows: Sequence[object], option_source: Mapping[str, object]) -> list[dict[str, object]]:
    value_field = _frontend_api_option_source_value_field(option_source)
    label_field = _frontend_api_option_source_label_field(option_source)
    detail_fields = _frontend_api_option_source_detail_fields(option_source)
    options: list[dict[str, object]] = []
    seen: set[str] = set()
    for row in rows:
        option = _frontend_api_option_row(row, value_field, label_field, detail_fields, seen)
        if option is not None:
            options.append(option)
    return options


def _frontend_api_option_row(
    row: object,
    value_field: str,
    label_field: str,
    detail_fields: Sequence[str],
    seen: set[str],
) -> dict[str, object] | None:
    if not isinstance(row, Mapping) or value_field not in row:
        return None
    value = row[value_field]
    if _frontend_api_option_value_seen(value, seen):
        return None
    label = row.get(label_field, value)
    option: dict[str, object] = {
        "value": value,
        "label": str(label),
        "row": dict(row),
    }
    details = _frontend_api_option_details(row, detail_fields)
    if details:
        option["details"] = details
    return option


def _frontend_api_option_value_seen(value: object, seen: set[str]) -> bool:
    key = repr(value)
    if key in seen:
        return True
    seen.add(key)
    return False


def _frontend_api_option_details(row: Mapping[str, object], detail_fields: Sequence[str]) -> dict[str, object]:
    return {name: row[name] for name in detail_fields if name in row}


def _frontend_api_groups(
    operations: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    group_counts = _frontend_api_group_counts(operations)
    groups: list[dict[str, object]] = []
    for group in FRONTEND_API_GROUPS:
        group_row: dict[str, object] = dict(group)
        group_row["operation_count"] = group_counts.get(str(group["id"]), {}).get("operation_count", 0)
        groups.append(group_row)
    return groups


def _frontend_api_summary(
    operations: Sequence[Mapping[str, object]],
    groups: Sequence[Mapping[str, object]],
    workspace: Mapping[str, object],
) -> dict[str, object]:
    group_counts = _frontend_api_group_counts(operations)
    return {
        "schema": FRONTEND_API_SUMMARY_SCHEMA,
        "operation_count": len(operations),
        "group_count": len(groups),
        "workspace_section_count": _frontend_api_workspace_section_count(workspace),
        "status_counts": _frontend_api_field_counts(operations, "status"),
        "mode_counts": _frontend_api_mode_counts(operations),
        "surface_counts": _frontend_api_surface_counts(operations),
        "group_counts": group_counts,
        "group_surface_counts": _frontend_api_group_surface_counts(operations),
    }


def _frontend_api_workspace_section_count(workspace: Mapping[str, object]) -> int:
    sections = workspace.get("sections", ())
    if isinstance(sections, Sequence) and not isinstance(sections, (str, bytes)):
        return len(sections)
    return 0


def _frontend_api_group_counts(
    operations: Sequence[Mapping[str, object]],
) -> _FrontendApiGroupCountMap:
    counts: _FrontendApiGroupCountMap = {}
    for operation in operations:
        group_id = str(operation["group"])
        bucket = counts.setdefault(group_id, {"operation_count": 0, "read": 0, "write": 0})
        bucket["operation_count"] += 1
        mode = _frontend_api_operation_mode(operation)
        bucket[mode] += 1
        status = str(operation["status"])
        _frontend_api_increment_count(bucket, status)
    return counts


def _frontend_api_field_counts(operations: Sequence[Mapping[str, object]], field_name: str) -> _FrontendApiCountMap:
    counts: _FrontendApiCountMap = {}
    for operation in operations:
        value = str(operation[field_name])
        _frontend_api_increment_count(counts, value)
    return counts


def _frontend_api_increment_count(counts: _FrontendApiCountMap, name: str) -> None:
    counts[name] = counts.get(name, 0) + 1


def _frontend_api_mode_counts(
    operations: Sequence[Mapping[str, object]],
) -> _FrontendApiCountMap:
    counts: _FrontendApiCountMap = {"read": 0, "write": 0}
    for operation in operations:
        counts[_frontend_api_operation_mode(operation)] += 1
    return counts


def _frontend_api_surface_counts(
    operations: Sequence[Mapping[str, object]],
) -> _FrontendApiCountMap:
    counts: _FrontendApiCountMap = {
        "operation_count": len(operations),
        **{surface: 0 for surface in FRONTEND_API_SURFACE_COVERAGE_COLUMNS},
        "unbound": 0,
    }
    for operation in operations:
        bindings = _frontend_api_operation_bindings(operation)
        if not bindings:
            counts["unbound"] += 1
            continue
        for surface in FRONTEND_API_SURFACE_COVERAGE_COLUMNS:
            if surface in bindings:
                counts[surface] += 1
    return counts


def _frontend_api_group_surface_counts(
    operations: Sequence[Mapping[str, object]],
) -> _FrontendApiGroupCountMap:
    by_group = _frontend_api_operations_by_group(operations)
    return {str(group["id"]): _frontend_api_surface_counts(_frontend_api_summary_group_operations(by_group, group)) for group in FRONTEND_API_GROUPS}


def _frontend_api_operations_by_group(
    operations: Sequence[Mapping[str, object]],
) -> dict[str, list[Mapping[str, object]]]:
    by_group: dict[str, list[Mapping[str, object]]] = {}
    for operation in operations:
        append_index_entry(by_group, str(operation["group"]), operation)
    return by_group


def _frontend_api_summary_group_operations(
    by_group: Mapping[str, Sequence[Mapping[str, object]]],
    group: Mapping[str, object],
) -> Sequence[Mapping[str, object]]:
    return by_group.get(str(group["id"]), [])


def _frontend_api_operations() -> list[dict[str, object]]:
    return [
        _op(
            "project.create",
            "projects",
            "create",
            "Create a starter project.",
            mutates=True,
            sdk="Project.create",
            cli="new",
            rest="POST /projects",
            mcp="project_create",
            payload="paradev.project.create.v1",
            inputs=[
                _input("path", "path", required=True),
                _input("project_id", "string"),
                _input("title", "string"),
                _input("game", "string", default="hoi4"),
                _input("force", "boolean", default=False),
            ],
        ),
        _op(
            "project.find",
            "projects",
            "find",
            "Find a project from a root or nested path without raising for missing manifests.",
            sdk="Project.find",
            cli="project-find",
            rest="GET /projects/find",
            mcp="project_find",
            payload="paradev.project.find.v1",
            inputs=[_input("path", "path", default=".")],
        ),
        _op(
            "project.open",
            "projects",
            "open",
            "Discover and load a project from a root or nested path.",
            sdk="Project.load",
            cli="project",
            rest="GET /projects",
            mcp="project_open",
            payload="Project.to_view",
            inputs=[
                _input("path", "path", default="."),
                _input("game", "string"),
                _input("title", "string"),
            ],
        ),
        _op(
            "project.view",
            "projects",
            "view",
            "Return the loaded project view model.",
            sdk="Project.to_view",
            cli="project",
            rest="GET /projects",
            mcp="project_view",
            payload="Project.to_view",
            inputs=[
                _input("path", "path", default="."),
                _input("game", "string"),
                _input("title", "string"),
            ],
        ),
        _op(
            "project.list",
            "projects",
            "list",
            "List registered local ParaDev projects.",
            sdk="registered_projects",
            cli="projects",
            rest="GET /projects/list",
            payload="paradev.sdk.projects.v1",
            inputs=[
                _input("project_paths", "array", default=[]),
                _input("search_roots", "array", default=[]),
            ],
        ),
        _op(
            "project.inspect",
            "projects",
            "inspect",
            "Run one SDK-owned read-only inspection by kind and filters.",
            sdk="Project.inspect",
            cli="inspections and inspection commands",
            rest="GET /projects/inspect",
            mcp="project_inspect",
            payload="Project inspection payload",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "kind",
                    "string",
                    default="summary",
                    choices=INSPECTION_KIND_CHOICES,
                    description="SDK project inspection kind.",
                ),
            ],
        ),
        _op(
            "project.config",
            "projects",
            "config",
            "Read and write stored ParaDev config scopes.",
            mutates=True,
            sdk="CM_PARADEV",
            cli="config",
            inputs=[],
        ),
        _op(
            "project.rename",
            "projects",
            "rename",
            "Rename the project display title without moving source folders.",
            mutates=True,
            sdk="Project.rename",
            cli="project-rename",
            rest="PATCH /projects/rename",
            mcp="project_rename",
            payload="paradev.project.rename.v1",
            inputs=[
                _input("title", "string", required=True),
                _input("path", "path", default="."),
            ],
        ),
        _op(
            "project.language",
            "projects",
            "configure",
            "Plan or apply the project-wide module-authoring language.",
            mutates=True,
            sdk="Project.set_preferred_language",
            cli="project-language",
            rest="PATCH /projects/language",
            mcp="project_preferred_language",
            payload="paradev.project.preferred-language.v1",
            inputs=[
                _input(
                    "preferred_language",
                    "string",
                    required=True,
                    choices=(
                        "en",
                        "fr",
                        "de",
                        "ru",
                        "es",
                        "pl",
                        "pt_br",
                        "zh",
                        "ja",
                        "ko",
                    ),
                ),
                _input("path", "path", default="."),
                _input("write", "boolean", default=False),
                _input("plan_hash", "string"),
            ],
        ),
        _op(
            "project.activate",
            "projects",
            "activate",
            "Select the active project in a frontend workspace.",
            status="frontend-local",
            mutates=True,
            inputs=[_input("project_id", "string", required=True)],
        ),
        _op(
            "project.state",
            "projects",
            "state",
            "Return SDK-owned project switcher state for a desktop workspace.",
            sdk="desktop_state",
            cli="desktop-state",
            rest="GET /desktop/state",
            payload="paradev.desktop.state.v1",
            inputs=[
                _input("project_path", "path"),
                _input("project_paths", "array", default=[]),
                _input("search_roots", "array", default=[]),
            ],
        ),
        _op(
            "project.browser",
            "projects",
            "browser",
            "Return the read-only project browser tree and indexes for frontend clients.",
            sdk="Project.browser",
            cli="project-browser",
            rest="GET /projects/browser",
            mcp="project_browser",
            payload="paradev.sdk.project-browser.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("kind", "string", choices=PROJECT_BROWSER_KIND_CHOICES),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
            ],
        ),
        _op(
            "project.source_text",
            "projects",
            "source-text",
            "Read one project-contained source file from a browser row path.",
            sdk="Project.read_source_text",
            rest="GET /projects/{project_id}/sources",
            payload="paradev.rest.source_text.v1",
            inputs=[
                _input("project_id", "string", required=True),
                _input("path", "path", default=".", maps_to="project_root"),
                _input(
                    "source_path",
                    "path",
                    required=True,
                    maps_to="path",
                    option_source=SOURCE_PATH_OPTION_SOURCE,
                ),
            ],
        ),
        _op(
            "project.source_form",
            "projects",
            "source-form",
            "Return an optional guided form for current canonical JSON or PDX source text.",
            sdk="Project.source_form",
            rest="POST /projects/{project_id}/sources/form",
            payload="paradev.source-form.v1",
            inputs=[
                _input("project_id", "string", required=True),
                _input("path", "path", default=".", maps_to="project_root"),
                _input(
                    "source_path",
                    "path",
                    required=True,
                    maps_to="path",
                    option_source=SOURCE_PATH_OPTION_SOURCE,
                ),
                _input("text", "text", required=True),
                _input(
                    "query",
                    "string",
                    description="Optional bounded field search for large guided forms.",
                ),
            ],
        ),
        _op(
            "project.draft_apply",
            "projects",
            "draft-apply",
            "Apply validated source edits and an optional module-folder rename inside one project transaction.",
            mutates=True,
            sdk="Project.apply_source_draft",
            cli="draft-apply",
            rest="POST /projects/{project_id}/drafts/apply",
            mcp="project_draft_apply",
            payload="paradev.rest.draft_apply.v1",
            inputs=[
                _input("project_id", "string", required=True),
                _input("path", "path", default=".", maps_to="project_root"),
                _input("source_edits", "array"),
                _input("source_removals", "array"),
                _input("source_replacements", "array"),
                _input("module_rename", "object"),
            ],
        ),
        _op(
            "module.list",
            "modules",
            "list",
            "List discovered build modules with filters.",
            sdk="Project.inspect('modules')",
            cli="modules",
            rest="GET /projects/inspect?kind=modules",
            mcp="project_inspect",
            payload="paradev.build.modules.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
                _input("source_slot", "string"),
            ],
        ),
        _op(
            "module.view",
            "modules",
            "view",
            "Explain one module with source, artifact, dependency, and diagnostic context.",
            sdk="Project.inspect('build-explain')",
            cli="build-explain --module",
            rest="GET /projects/inspect?kind=build-explain",
            mcp="project_inspect",
            payload="paradev.build.explain.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "module_id",
                    "string",
                    required=True,
                    option_source=MODULE_ID_OPTION_SOURCE,
                ),
                _input("profile", "string"),
            ],
        ),
        _op(
            "module.templates",
            "modules",
            "templates",
            "List authoring templates and source roots available to module creation.",
            sdk="Project.templates",
            cli="templates",
            rest="GET /projects/templates",
            mcp="project_templates",
            payload="paradev.sdk.templates.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("template_id", "string", option_source=TEMPLATE_OPTION_SOURCE),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input(
                    "kind",
                    "string",
                    choices=("module", "collection"),
                ),
                _input("source", "string"),
                _input("authoring_ready", "boolean"),
                _input(
                    "diagnostic_code",
                    "string",
                    option_source=DIAGNOSTIC_CODE_OPTION_SOURCE,
                ),
            ],
        ),
        _op(
            "module.create",
            "modules",
            "create",
            "Plan or write a source module from an authoring template.",
            mutates=True,
            sdk="Project.scaffold_module",
            cli="scaffold",
            rest="POST /projects/scaffold",
            mcp="project_scaffold",
            payload="paradev.sdk.module_scaffold.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "template_id",
                    "string",
                    required=True,
                    option_source=TEMPLATE_OPTION_SOURCE,
                ),
                _input("object_id", "string", required=True),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("values", "object"),
                _input("write", "boolean", default=False),
                _input("force", "boolean", default=False),
            ],
        ),
        _op(
            "module.create_batch",
            "modules",
            "create-batch",
            "Plan or atomically create several source modules from one guarded plan.",
            mutates=True,
            sdk="Project.create_modules",
            cli="module-batch-create",
            rest="POST /projects/modules/create-batch",
            mcp="project_create_modules",
            payload="paradev.sdk.module_batch.v1",
            inputs=[
                _input("project_id", "string", required=True),
                _input("path", "path", default=".", maps_to="project_root"),
                _input("modules", "array", required=True),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("write", "boolean", default=False),
                _input("plan_hash", "string"),
            ],
        ),
        _op(
            "module.draft",
            "modules",
            "draft",
            "Plan or write a source-module draft from a frontend browser family id.",
            mutates=True,
            sdk="Project.create_module_draft",
            rest="POST /projects/{project_id}/modules/{family_id}/drafts",
            payload="paradev.rest.module_draft.v1",
            inputs=[
                _input("project_id", "string", required=True),
                _input(
                    "family_id",
                    "string",
                    required=True,
                    option_source=FAMILY_OPTION_SOURCE,
                ),
                _input("path", "path", default=".", maps_to="project_root"),
                _input("template_id", "string", option_source=TEMPLATE_OPTION_SOURCE),
                _input("object_id", "string", required=True),
                _input("values", "object"),
                _input("write", "boolean", default=False),
                _input("force", "boolean", default=False),
            ],
        ),
        _op(
            "module.authoring_path",
            "modules",
            "authoring-path",
            "Resolve one canonical module folder without writing files.",
            sdk="Project.authoring_path",
            cli="authoring-path",
            rest="GET /projects/authoring-path",
            mcp="project_authoring_path",
            payload="paradev.sdk.authoring_path.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("kind", "string", default="module", choices=AUTHORING_KIND_CHOICES),
                _input(
                    "family",
                    "string",
                    required=True,
                    option_source=FAMILY_OPTION_SOURCE,
                ),
                _input("target_id", "string", required=True),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
            ],
        ),
        _op(
            "module.authoring_plan",
            "modules",
            "authoring-plan",
            "Resolve a module folder plus expected source-slot status.",
            sdk="Project.authoring_plan",
            cli="authoring-plan",
            rest="GET /projects/authoring-plan",
            mcp="project_authoring_plan",
            payload="paradev.sdk.authoring_plan.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("kind", "string", default="module", choices=AUTHORING_KIND_CHOICES),
                _input(
                    "family",
                    "string",
                    required=True,
                    option_source=FAMILY_OPTION_SOURCE,
                ),
                _input("target_id", "string", required=True),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("profile", "string"),
            ],
        ),
        _op(
            "module.source_slots",
            "modules",
            "source-slots",
            "Show expected-versus-found source slots for modules.",
            sdk="Project.inspect('source-slots')",
            cli="source-slots",
            rest="GET /projects/inspect?kind=source-slots",
            mcp="project_inspect",
            payload="paradev.build.source-slots.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
                _input("slot", "string"),
                _input("status", "string", choices=SOURCE_SLOT_STATUS_CHOICES),
            ],
        ),
        _op(
            "module.sources",
            "modules",
            "sources",
            "Show compiler input source files for modules.",
            sdk="Project.inspect('sources')",
            cli="sources",
            rest="GET /projects/inspect?kind=sources",
            mcp="project_inspect",
            payload="paradev.build.sources.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
                _input("slot", "string"),
                _input("loader", "string"),
                _input("status", "string", choices=SOURCE_STATUS_CHOICES),
            ],
        ),
        _op(
            "module.diagram",
            "modules",
            "diagram",
            "Project one authoritative module family into a source-backed diagram.",
            sdk="Project.module_diagram",
            cli="module-diagram",
            rest="GET /projects/modules/diagram",
            mcp="module_diagram",
            payload="paradev.sdk.module_diagram.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "family",
                    "string",
                    required=True,
                    option_source=FAMILY_OPTION_SOURCE,
                ),
                _input("profile", "string"),
            ],
        ),
        _op(
            "module.diagram.edit",
            "modules",
            "diagram-edit",
            "Plan or apply bounded source-backed module diagram intents.",
            mutates=True,
            sdk="Project.edit_module_diagram",
            cli="module-diagram-edit",
            rest="POST /projects/modules/diagram/edit",
            mcp="module_diagram_edit",
            payload="paradev.sdk.module_diagram_edit.v1",
            inputs=[
                _input("path", "path", default=".", maps_to="project_root"),
                _input(
                    "family",
                    "string",
                    required=True,
                    option_source=FAMILY_OPTION_SOURCE,
                ),
                _input("profile", "string"),
                _input(
                    "position_intents",
                    "array",
                    default=[],
                    item_type="object",
                    max_items=MAX_MODULE_DIAGRAM_POSITION_INTENTS,
                ),
                _input(
                    "edge_intents",
                    "array",
                    default=[],
                    item_type="object",
                    max_items=MAX_MODULE_DIAGRAM_EDGE_INTENTS,
                ),
                _input(
                    "node_intents",
                    "array",
                    default=[],
                    item_type="object",
                    max_items=MAX_MODULE_DIAGRAM_NODE_INTENTS,
                ),
                _input("write", "boolean", default=False),
                _input("plan_hash", "string"),
            ],
        ),
        _op(
            "module.file",
            "modules",
            "file",
            "Read one text source file from a module.",
            sdk="Project.read_module_file",
            cli="module-file",
            rest="GET /projects/modules/file",
            mcp="module_file",
            payload="paradev.module.file.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "module_id",
                    "string",
                    required=True,
                    option_source=MODULE_ID_OPTION_SOURCE,
                ),
                _input(
                    "relative_path",
                    "path",
                    required=True,
                    option_source=MODULE_RELATIVE_PATH_OPTION_SOURCE,
                ),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("encoding", "string", default="utf-8"),
            ],
        ),
        _op(
            "module.edit",
            "modules",
            "edit",
            "Write one text source file inside a module.",
            mutates=True,
            sdk="Project.write_module_file",
            cli="module-edit",
            rest="PATCH /projects/modules/file",
            mcp="module_edit",
            payload="paradev.module.file.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "module_id",
                    "string",
                    required=True,
                    option_source=MODULE_ID_OPTION_SOURCE,
                ),
                _input(
                    "relative_path",
                    "path",
                    required=True,
                    option_source=MODULE_RELATIVE_PATH_OPTION_SOURCE,
                ),
                _input("text", "text", required=True),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("create", "boolean", default=False),
                _input("encoding", "string", default="utf-8"),
            ],
        ),
        _op(
            "localization.workspace",
            "localization",
            "localization-workspace",
            "Return one Registry-owned cross-language localization workspace for a module or collection.",
            sdk="Project.localization_workspace",
            rest="POST /projects/{project_id}/localization/workspace",
            mcp="localization_workspace",
            payload="paradev.localization-workspace.v2",
            inputs=[
                _input("project_id", "string", required=True),
                _input("path", "path", default=".", maps_to="project_root"),
                _input(
                    "target_kind",
                    "string",
                    required=True,
                    choices=("module", "collection"),
                ),
                _input("target_id", "string", required=True),
                _input("family", "string"),
                _input("source_root", "string"),
                _input("drafts", "array"),
                _input("limit", "integer", default=512),
            ],
        ),
        _op(
            "localization.plan",
            "localization",
            "localization-plan",
            "Plan one lossless Registry-owned localization edit without writing source files.",
            sdk="Project.plan_localization_update",
            rest="POST /projects/{project_id}/localization/plan",
            mcp="localization_plan",
            payload="paradev.localization-update-plan.v2",
            inputs=[
                _input("project_id", "string", required=True),
                _input("path", "path", default=".", maps_to="project_root"),
                _input(
                    "target_kind",
                    "string",
                    required=True,
                    choices=("module", "collection"),
                ),
                _input("target_id", "string", required=True),
                _input("family", "string"),
                _input("source_root", "string"),
                _input("drafts", "array"),
                _input("limit", "integer", default=512),
                _input("operation", "object", required=True),
            ],
        ),
        _op(
            "module.rename",
            "modules",
            "rename",
            "Rename a source module folder or synchronize its readable title without rewriting PDX content.",
            mutates=True,
            sdk="Project.rename_module",
            cli="module-rename",
            rest="PATCH /projects/modules/rename",
            mcp="module_rename",
            payload="paradev.module.rename.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "module_id",
                    "string",
                    required=True,
                    option_source=MODULE_ID_OPTION_SOURCE,
                ),
                _input("object_id", "string", required=True),
                _input("title", "string"),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
            ],
        ),
        _op(
            "module.duplicate",
            "modules",
            "duplicate",
            "Plan or atomically create an independent module copy through its family identity rewriter.",
            mutates=True,
            sdk="Project.duplicate_module",
            cli="module-duplicate",
            rest="POST /projects/modules/duplicate",
            mcp="module_duplicate",
            payload="paradev.sdk.module_duplicate.v1",
            inputs=[
                _input("path", "path", default=".", maps_to="project_root"),
                _input(
                    "module_id",
                    "string",
                    required=True,
                    option_source=MODULE_ID_OPTION_SOURCE,
                ),
                _input("object_id", "string", required=True),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input(
                    "destination_source_root",
                    "path",
                    option_source=SOURCE_ROOT_OPTION_SOURCE,
                ),
                _input(
                    "identity",
                    "choice",
                    default="rewrite",
                    choices=["rewrite", "preserve"],
                ),
                _input("write", "boolean", default=False),
                _input("plan_hash", "string"),
            ],
        ),
        _op(
            "module.collection.set",
            "modules",
            "collection",
            "Plan or atomically move a module into a same-family collection, or clear its membership.",
            mutates=True,
            sdk="Project.set_module_collection",
            cli="module-collection-set",
            rest="POST /projects/modules/collection",
            mcp="module_collection_set",
            payload="paradev.sdk.module_collection_update.v1",
            inputs=[
                _input("path", "path", default=".", maps_to="project_root"),
                _input(
                    "module_id",
                    "string",
                    required=True,
                    option_source=MODULE_ID_OPTION_SOURCE,
                ),
                _input(
                    "collection_id",
                    "string",
                    option_source=COLLECTION_ID_OPTION_SOURCE,
                    description="Target same-family collection; omit to clear membership.",
                ),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("write", "boolean", default=False),
                _input("plan_hash", "string"),
            ],
        ),
        _op(
            "module.activity.set",
            "modules",
            "activity",
            "Plan or atomically include or omit one module in every compilation mode.",
            mutates=True,
            sdk="Project.set_module_active",
            cli="module-activity-set",
            rest="POST /projects/modules/activity",
            mcp="module_activity_set",
            payload="paradev.sdk.module_activity_update.v1",
            inputs=[
                _input("path", "path", default=".", maps_to="project_root"),
                _input(
                    "module_id",
                    "string",
                    required=True,
                    option_source=MODULE_ID_OPTION_SOURCE,
                ),
                _input("active", "boolean", required=True),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("write", "boolean", default=False),
                _input("plan_hash", "string"),
            ],
        ),
        _op(
            "module.metadata.clean",
            "modules",
            "clean",
            "Plan or atomically remove redundant path-derived module metadata.",
            mutates=True,
            sdk="Project.clean_module_metadata",
            cli="module-metadata-clean",
            rest="POST /projects/modules/metadata/clean",
            mcp="module_metadata_clean",
            payload="paradev.sdk.module_metadata_cleanup.v1",
            inputs=[
                _input("path", "path", default=".", maps_to="project_root"),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input(
                    "module_id",
                    "string",
                    option_source=MODULE_ID_OPTION_SOURCE,
                ),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("write", "boolean", default=False),
                _input("plan_hash", "string"),
            ],
        ),
        _op(
            "module.remove",
            "modules",
            "remove",
            "Plan or remove a source module folder.",
            mutates=True,
            sdk="Project.remove_module",
            cli="module-remove",
            rest="DELETE /projects/modules/remove",
            mcp="module_remove",
            payload="paradev.module.remove.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "module_id",
                    "string",
                    required=True,
                    option_source=MODULE_ID_OPTION_SOURCE,
                ),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("write", "boolean", default=False),
            ],
        ),
        _op(
            "collection.list",
            "collections",
            "list",
            "List discovered build collections with filters.",
            sdk="Project.inspect('collections')",
            cli="collections",
            rest="GET /projects/inspect?kind=collections",
            mcp="project_inspect",
            payload="paradev.build.collections.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("source_slot", "string"),
            ],
        ),
        _op(
            "collection.view",
            "collections",
            "view",
            "Explain one collection with source, artifact, dependency, and diagnostic context.",
            sdk="Project.inspect('collections')",
            cli="collections --collection",
            rest="GET /projects/inspect?kind=collections",
            mcp="project_inspect",
            payload="paradev.build.collections.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "collection_id",
                    "string",
                    required=True,
                    option_source=COLLECTION_ID_OPTION_SOURCE,
                ),
                _input("profile", "string"),
            ],
        ),
        _op(
            "collection.authoring_path",
            "collections",
            "authoring-path",
            "Resolve one canonical collection descriptor folder without writing files.",
            sdk="Project.authoring_path",
            cli="authoring-path",
            rest="GET /projects/authoring-path",
            mcp="project_authoring_path",
            payload="paradev.sdk.authoring_path.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "kind",
                    "string",
                    default="collection",
                    choices=AUTHORING_KIND_CHOICES,
                ),
                _input(
                    "family",
                    "string",
                    required=True,
                    option_source=FAMILY_OPTION_SOURCE,
                ),
                _input("target_id", "string", required=True),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
            ],
        ),
        _op(
            "collection.authoring_plan",
            "collections",
            "authoring-plan",
            "Resolve a collection descriptor folder plus expected source-slot status.",
            sdk="Project.authoring_plan",
            cli="authoring-plan",
            rest="GET /projects/authoring-plan",
            mcp="project_authoring_plan",
            payload="paradev.sdk.authoring_plan.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "kind",
                    "string",
                    default="collection",
                    choices=AUTHORING_KIND_CHOICES,
                ),
                _input(
                    "family",
                    "string",
                    required=True,
                    option_source=FAMILY_OPTION_SOURCE,
                ),
                _input("target_id", "string", required=True),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("profile", "string"),
            ],
        ),
        _op(
            "collection.source_slots",
            "collections",
            "source-slots",
            "Show expected-versus-found source slots for collection descriptors.",
            sdk="Project.inspect('source-slots')",
            cli="source-slots",
            rest="GET /projects/inspect?kind=source-slots",
            mcp="project_inspect",
            payload="paradev.build.source-slots.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
                _input("slot", "string"),
                _input("status", "string", choices=SOURCE_SLOT_STATUS_CHOICES),
            ],
        ),
        _op(
            "collection.sources",
            "collections",
            "sources",
            "Show compiler input source files owned by collection descriptors.",
            sdk="Project.inspect('sources')",
            cli="sources --owner-kind collection",
            rest="GET /projects/inspect?kind=sources",
            mcp="project_inspect",
            payload="paradev.build.sources.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
                _input("slot", "string"),
                _input("loader", "string"),
                _input("status", "string", choices=SOURCE_STATUS_CHOICES),
                _input(
                    "owner_kind",
                    "string",
                    default="collection",
                    choices=OWNER_KIND_CHOICES,
                ),
            ],
        ),
        _op(
            "collection.file",
            "collections",
            "file",
            "Read one text source file from a collection descriptor.",
            sdk="Project.read_collection_file",
            cli="collection-file",
            rest="GET /projects/collections/file",
            mcp="collection_file",
            payload="paradev.collection.file.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "collection_id",
                    "string",
                    required=True,
                    option_source=COLLECTION_ID_OPTION_SOURCE,
                ),
                _input(
                    "relative_path",
                    "path",
                    required=True,
                    option_source=COLLECTION_RELATIVE_PATH_OPTION_SOURCE,
                ),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("encoding", "string", default="utf-8"),
            ],
        ),
        _op(
            "collection.scaffold",
            "collections",
            "scaffold",
            "Plan or transactionally write a collection from a Registry-backed template.",
            mutates=True,
            sdk="Project.scaffold_collection",
            cli="collection-scaffold",
            rest="POST /projects/collections/scaffold",
            mcp="collection_scaffold",
            payload="paradev.sdk.collection_scaffold.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "template_id",
                    "string",
                    required=True,
                    option_source=TEMPLATE_OPTION_SOURCE,
                ),
                _input("collection_id", "string", required=True),
                _input(
                    "source_root",
                    "path",
                    option_source=SOURCE_ROOT_OPTION_SOURCE,
                ),
                _input("values", "object"),
                _input("write", "boolean", default=False),
                _input("force", "boolean", default=False),
                _input("plan_hash", "string"),
            ],
        ),
        _op(
            "collection.create",
            "collections",
            "create",
            "Plan or write a collection descriptor metadata scaffold.",
            mutates=True,
            sdk="Project.create_collection",
            cli="collection-create",
            rest="POST /projects/collections",
            mcp="collection_create",
            payload="paradev.collection.create.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "family",
                    "string",
                    required=True,
                    option_source=FAMILY_OPTION_SOURCE,
                ),
                _input("collection_id", "string", required=True),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("metadata", "object"),
                _input("write", "boolean", default=False),
                _input("force", "boolean", default=False),
            ],
        ),
        _op(
            "collection.edit",
            "collections",
            "edit",
            "Write one text source file inside a collection descriptor.",
            mutates=True,
            sdk="Project.write_collection_file",
            cli="collection-edit",
            rest="PATCH /projects/collections/file",
            mcp="collection_edit",
            payload="paradev.collection.file.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "collection_id",
                    "string",
                    required=True,
                    option_source=COLLECTION_ID_OPTION_SOURCE,
                ),
                _input(
                    "relative_path",
                    "path",
                    required=True,
                    option_source=COLLECTION_RELATIVE_PATH_OPTION_SOURCE,
                ),
                _input("text", "text", required=True),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("create", "boolean", default=False),
                _input("encoding", "string", default="utf-8"),
            ],
        ),
        _op(
            "collection.rename",
            "collections",
            "rename",
            "Rename a collection descriptor folder within its current family without rewriting authored content.",
            mutates=True,
            sdk="Project.rename_collection",
            cli="collection-rename",
            rest="PATCH /projects/collections/rename",
            mcp="collection_rename",
            payload="paradev.collection.rename.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "collection_id",
                    "string",
                    required=True,
                    option_source=COLLECTION_ID_OPTION_SOURCE,
                ),
                _input("target_id", "string", required=True),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
            ],
        ),
        _op(
            "collection.remove",
            "collections",
            "remove",
            "Plan or remove a collection while preserving and ungrouping its modules.",
            mutates=True,
            sdk="Project.remove_collection",
            cli="collection-remove",
            rest="DELETE /projects/collections",
            mcp="collection_remove",
            payload="paradev.collection.remove.v1",
            inputs=[
                _input("path", "path", default="."),
                _input(
                    "collection_id",
                    "string",
                    required=True,
                    option_source=COLLECTION_ID_OPTION_SOURCE,
                ),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("source_root", "path", option_source=SOURCE_ROOT_OPTION_SOURCE),
                _input("write", "boolean", default=False),
                _input("plan_hash", "string"),
            ],
        ),
        _op(
            "build.plan",
            "build",
            "plan",
            "Run a dry build plan.",
            sdk="Project.build",
            cli="build",
            rest="POST /projects/build",
            payload="BuildResult.to_dict",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("strict_metadata", "boolean"),
            ],
        ),
        _op(
            "build.emit",
            "build",
            "emit",
            "Plan once, write only when diagnostics pass, and return the blocked dry result otherwise.",
            mutates=True,
            sdk="Project.build",
            cli="build --emit-artifacts/--emit-manifests",
            rest="POST /projects/build?emit_artifacts=true&emit_manifests=true",
            payload="BuildResult.to_dict",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("strict_metadata", "boolean"),
                _input("emit_artifacts", "boolean", default=False),
                _input("emit_manifests", "boolean", default=False),
            ],
        ),
        _op(
            "build.start",
            "build",
            "start",
            "Start one desktop build run through the Python desktop facade.",
            mutates=True,
            sdk="desktop_start_build",
            rest="POST /desktop/builds",
            payload="paradev.desktop.build-run.v1",
            inputs=[
                _input("project_root", "path", required=True),
                _input("mode", "string", default="cached", choices=("cached", "full")),
                _input("profile", "string"),
                _input("strict_metadata", "boolean"),
                _input("parallelism", "integer", minimum=1),
                _input(
                    "target",
                    "object",
                    description="Optional build target with kind, id, and optional family fields.",
                ),
            ],
        ),
        _op(
            "build.runs",
            "build",
            "status",
            "List active and retained terminal desktop build runs.",
            sdk="desktop_build_runs",
            rest="GET /desktop/builds",
            payload="paradev.desktop.build-runs.v1",
            inputs=[_input("project_root", "path")],
        ),
        _op(
            "build.status",
            "build",
            "status",
            "Return active or retained terminal status for one exact desktop build run.",
            sdk="desktop_build_status",
            rest="GET /desktop/builds/status",
            payload="paradev.desktop.build-run.v1",
            inputs=[
                _input(
                    "run_id",
                    "string",
                    required=True,
                    nonblank=True,
                    description="Exact run identifier returned by build.start or build.runs.",
                )
            ],
        ),
        _op(
            "build.interrupt",
            "build",
            "interrupt",
            "Interrupt one exact active desktop build run or return its retained terminal status.",
            mutates=True,
            sdk="desktop_interrupt_build",
            rest="POST /desktop/builds/interrupt",
            payload="paradev.desktop.build-run.v1",
            inputs=[
                _input(
                    "run_id",
                    "string",
                    required=True,
                    nonblank=True,
                    description="Exact run identifier returned by build.start or build.runs.",
                )
            ],
        ),
        _op(
            "build.summary",
            "build",
            "summary",
            "Read the build summary.",
            sdk="Project.inspect('summary')",
            cli="summary",
            rest="GET /projects/inspect?kind=summary",
            mcp="project_inspect",
            payload="paradev.build.summary.v1",
            inputs=[_input("path", "path", default="."), _input("profile", "string")],
        ),
        _op(
            "build.manifests",
            "build",
            "manifests",
            "Read all build manifest payloads.",
            sdk="Project.inspect('manifests')",
            cli="manifests",
            rest="GET /projects/inspect?kind=manifests",
            mcp="project_inspect",
            payload="paradev.build.manifests.v1",
            inputs=[_input("path", "path", default="."), _input("profile", "string")],
        ),
        _op(
            "build.artifacts",
            "build",
            "artifacts",
            "List planned artifacts.",
            sdk="Project.inspect('artifacts')",
            cli="artifacts",
            rest="GET /projects/inspect?kind=artifacts",
            mcp="project_inspect",
            payload="paradev.build.artifacts.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("artifact_type", "string", option_source=ARTIFACT_TYPE_OPTION_SOURCE),
                _input("target_root", "string", choices=TARGET_ROOT_CHOICES),
                _input("owner", "string"),
                _input(
                    "artifact_path",
                    "path",
                    maps_to="path",
                    option_source=ARTIFACT_PATH_OPTION_SOURCE,
                ),
                _input("mode", "string"),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
            ],
        ),
        _op(
            "build.localization",
            "build",
            "localization",
            "List loaded localization rows.",
            sdk="Project.inspect('localization')",
            cli="localization",
            rest="GET /projects/inspect?kind=localization",
            mcp="project_inspect",
            payload="paradev.build.localization.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("language", "string"),
                _input("key", "string"),
                _input("key_prefix", "string"),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
            ],
        ),
        _op(
            "build.assets",
            "build",
            "assets",
            "List loaded static copy assets.",
            sdk="Project.inspect('assets')",
            cli="assets",
            rest="GET /projects/inspect?kind=assets",
            mcp="project_inspect",
            payload="paradev.build.assets.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("slot", "string"),
                _input("file_format", "string"),
            ],
        ),
        _op(
            "build.sprites",
            "build",
            "sprites",
            "List planned interface sprite declarations.",
            sdk="Project.inspect('sprites')",
            cli="sprites",
            rest="GET /projects/inspect?kind=sprites",
            mcp="project_inspect",
            payload="paradev.build.sprites.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("slot", "string"),
                _input("name", "string"),
            ],
        ),
        _op(
            "build.diagnostics",
            "build",
            "diagnostics",
            "List build diagnostics.",
            sdk="Project.inspect('diagnostics')",
            cli="diagnostics",
            rest="GET /projects/inspect?kind=diagnostics",
            mcp="project_inspect",
            payload="paradev.build.diagnostics.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("severity", "string", choices=DIAGNOSTIC_SEVERITY_CHOICES),
                _input("code", "string", option_source=DIAGNOSTIC_CODE_OPTION_SOURCE),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("owner", "string"),
                _input("target_root", "string", choices=TARGET_ROOT_CHOICES),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
                _input("source_path", "path", option_source=SOURCE_PATH_OPTION_SOURCE),
                _input("slot", "string"),
                _input("strict_metadata", "boolean"),
                _input("published", "boolean", default=False),
            ],
        ),
        _op(
            "build.source_map",
            "build",
            "source-map",
            "Trace artifacts back to source rows.",
            sdk="Project.inspect('source-map')",
            cli="source-map",
            rest="GET /projects/inspect?kind=source-map",
            mcp="project_inspect",
            payload="paradev.build.source-map.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("slot", "string"),
                _input("artifact_type", "string", option_source=ARTIFACT_TYPE_OPTION_SOURCE),
                _input("target_root", "string", choices=TARGET_ROOT_CHOICES),
            ],
        ),
        _op(
            "build.dependencies",
            "build",
            "dependencies",
            "List build dependency edges.",
            sdk="Project.inspect('dependencies')",
            cli="dependencies",
            rest="GET /projects/inspect?kind=dependencies",
            mcp="project_inspect",
            payload="paradev.build.dependencies.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("source", "string"),
                _input("target", "string"),
                _input("kind", "string"),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
            ],
        ),
        _op(
            "build.graph",
            "build",
            "graph",
            "Return grouped source, artifact, and dependency graph nodes and edges.",
            sdk="Project.inspect('build-graph')",
            cli="build-graph",
            rest="GET /projects/inspect?kind=build-graph",
            mcp="project_inspect",
            payload="paradev.build.graph.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("slot", "string"),
                _input("artifact_type", "string", option_source=ARTIFACT_TYPE_OPTION_SOURCE),
                _input("target_root", "string", choices=TARGET_ROOT_CHOICES),
                _input("edge_kind", "string"),
            ],
        ),
        _op(
            "build.explain",
            "build",
            "explain",
            "Explain one module, collection, source, artifact, or diagnostic.",
            sdk="Project.inspect('build-explain')",
            cli="build-explain",
            rest="GET /projects/inspect?kind=build-explain",
            mcp="project_inspect",
            payload="paradev.build.explain.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("module_id", "string", option_source=MODULE_ID_OPTION_SOURCE),
                _input("collection_id", "string", option_source=COLLECTION_ID_OPTION_SOURCE),
                _input("source_path", "path", option_source=SOURCE_PATH_OPTION_SOURCE),
                _input("artifact_path", "path", option_source=ARTIFACT_PATH_OPTION_SOURCE),
                _input(
                    "diagnostic_code",
                    "string",
                    option_source=DIAGNOSTIC_CODE_OPTION_SOURCE,
                ),
                _input("target_root", "string", choices=TARGET_ROOT_CHOICES),
                _input("profile", "string"),
            ],
        ),
        _op(
            "build.families",
            "build",
            "families",
            "List compiler family and authoring contracts.",
            sdk="Project.inspect('families')",
            cli="families",
            rest="GET /projects/inspect?kind=families",
            mcp="project_inspect",
            payload="paradev.build.families.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("family", "string", option_source=FAMILY_OPTION_SOURCE),
                _input("kind", "string"),
                _input("source_slot", "string"),
                _input("collection_source_slot", "string"),
                _input("sprite_slot", "string"),
                _input("route", "string"),
                _input("artifact_type", "string", option_source=ARTIFACT_TYPE_OPTION_SOURCE),
            ],
        ),
        _op(
            "pdx.parse",
            "pdx",
            "parse",
            "Parse one PDX file.",
            sdk="parse_pdx_file",
            cli="parse",
            rest="GET /pdx/parse",
            mcp="pdx_parse",
            payload="paradev.pdx.parse.v1",
            inputs=[
                _input("path", "path", required=True),
                _input("include_dump", "boolean", default=False),
                _input("include_tokens", "boolean", default=False),
            ],
        ),
        _op(
            "pdx.tokens",
            "pdx",
            "tokens",
            "Parse one PDX file and include lexer token rows.",
            sdk="parse_pdx_file(..., include_tokens=True)",
            cli="parse --tokens",
            rest="GET /pdx/parse?include_tokens=true",
            inputs=[
                _input("path", "path", required=True),
                _input("include_tokens", "boolean", default=True),
            ],
        ),
        _op(
            "pdx.dump",
            "pdx",
            "dump",
            "Parse one PDX file and include the lossless AST dump.",
            sdk="parse_pdx_file(..., include_dump=True)",
            cli="parse --dump",
            rest="GET /pdx/parse?include_dump=true",
            inputs=[
                _input("path", "path", required=True),
                _input("include_dump", "boolean", default=True),
            ],
        ),
        _op(
            "pdx.format",
            "pdx",
            "format",
            "Format PDX text through the SDK formatter.",
            mutates=True,
            sdk="format_pdx_file",
            cli="format",
            rest="POST /pdx/format",
            mcp="pdx_format",
            payload="paradev.pdx.format.v1",
            inputs=[
                _input("path", "path", required=True),
                _input("indent", "string", default="\t"),
                _input("comments", "boolean", default=True),
                _input("write", "boolean", default=False),
            ],
        ),
        _op(
            "lsp.diagnostics",
            "lsp",
            "diagnostics",
            "Publish document diagnostics.",
            sdk="diagnose_pdx_lsp_text",
            rest="POST /lsp/diagnostics",
            lsp="textDocument/publishDiagnostics",
            payload="paradev.lsp.diagnostics.v1",
            inputs=[
                _input("text", "text", required=True),
                _input("uri", "string"),
                _input("path", "path"),
            ],
        ),
        _op(
            "lsp.symbols",
            "lsp",
            "symbols",
            "Return document symbols.",
            sdk="document_symbols_pdx_lsp_text",
            rest="POST /lsp/symbols",
            lsp="textDocument/documentSymbol",
            payload="paradev.lsp.symbols.v1",
            inputs=[
                _input("text", "text", required=True),
                _input("uri", "string"),
                _input("path", "path"),
            ],
        ),
        _op(
            "lsp.hover",
            "lsp",
            "hover",
            "Return hover details for a document position.",
            sdk="hover_pdx_lsp_text",
            rest="POST /lsp/hover",
            lsp="textDocument/hover",
            payload="paradev.lsp.hover.v1",
            inputs=[
                _input("text", "text", required=True),
                _input("line", "integer", required=True, minimum=0),
                _input("character", "integer", required=True, minimum=0),
                _input("uri", "string"),
                _input("path", "path"),
            ],
        ),
        _op(
            "lsp.formatting",
            "lsp",
            "formatting",
            "Return text edits for PDX formatting.",
            mutates=True,
            sdk="format_pdx_lsp_text",
            rest="POST /lsp/formatting",
            lsp="textDocument/formatting",
            payload="paradev.lsp.formatting.v1",
            inputs=[
                _input("text", "text", required=True),
                _input("uri", "string"),
                _input("path", "path"),
                _input("indent", "string", default="\t"),
                _input("comments", "boolean", default=True),
            ],
        ),
        _op(
            "lsp.completion",
            "lsp",
            "completion",
            "Return catalog-backed completion items for a document position.",
            sdk="complete_pdx_lsp_text",
            rest="POST /lsp/completion",
            lsp="textDocument/completion",
            payload="paradev.lsp.completion.v1",
            inputs=[
                _input("text", "text", required=True),
                _input("line", "integer", required=True, minimum=0),
                _input("character", "integer", required=True, minimum=0),
                _input("offset", "integer", minimum=0),
                _input("uri", "string"),
                _input("path", "path"),
                _input("project_path", "path"),
                _input("database", "path"),
                _input("game_root", "path"),
                _input("limit", "integer", default=100, minimum=1),
            ],
        ),
        _op(
            "lsp.semantic_tokens",
            "lsp",
            "semantic tokens",
            "Return semantic tokens for PDX highlighting.",
            sdk="semantic_tokens_pdx_lsp_text",
            rest="POST /lsp/semantic-tokens",
            lsp="textDocument/semanticTokens/full",
            payload="paradev.lsp.semantic-tokens.v1",
            inputs=[
                _input("text", "text", required=True),
                _input("uri", "string"),
                _input("path", "path"),
            ],
        ),
        _op(
            "lsp.keywords",
            "lsp",
            "keywords",
            "Return the HOI4 keyword dataset used by editor completion.",
            sdk="hoi4_keyword_dataset",
            cli="lsp keywords",
            rest="GET /lsp/keywords",
            payload="paradev.hoi4.keyword-dataset.v1",
            inputs=[_input("game_root", "path")],
        ),
        _op(
            "catalog.preview",
            "catalog",
            "preview",
            "Return deterministic HeavenBase-ready catalog rows.",
            sdk="Project.inspect('catalog-preview')",
            cli="hb catalog-preview",
            rest="GET /projects/inspect?kind=catalog-preview",
            mcp="project_inspect",
            payload="paradev.hb.catalog-preview.v1",
            inputs=[_input("path", "path", default="."), _input("profile", "string")],
        ),
        _op(
            "catalog.write",
            "catalog",
            "write",
            "Write preview rows to a local HeavenBase catalog database.",
            mutates=True,
            sdk="paradev.hb.catalog_write",
            cli="hb catalog-write",
            rest="POST /projects/catalog",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("database", "path"),
            ],
        ),
        _op(
            "catalog.refresh",
            "catalog",
            "refresh",
            "Replace the local HeavenBase catalog database.",
            mutates=True,
            sdk="paradev.hb.catalog_refresh",
            cli="hb catalog-refresh",
            rest="PUT /projects/catalog",
            inputs=[
                _input("path", "path", default="."),
                _input("profile", "string"),
                _input("database", "path"),
            ],
        ),
        _op(
            "catalog.query",
            "catalog",
            "query",
            "Query written HeavenBase catalog rows.",
            sdk="Project.inspect('catalog-query')",
            cli="hb catalog-query",
            rest="GET /projects/inspect?kind=catalog-query",
            mcp="project_inspect",
            payload="paradev.hb.catalog-query.v1",
            inputs=[
                _input("path", "path", default="."),
                _input("database", "path"),
                _input("entity", "string"),
                _input("target_id", "string"),
                _input("name", "string"),
                _input("tag", "string"),
                _input(
                    "limit",
                    "integer",
                    default=CATALOG_QUERY_DEFAULT_LIMIT,
                    minimum=1,
                    maximum=CATALOG_QUERY_MAX_LIMIT,
                    description="Return 1-200 rows. Set this to 1 before enabling hydrated target data.",
                ),
                _input("offset", "integer", default=0, minimum=0),
                _input(
                    "include_data",
                    "boolean",
                    default=CATALOG_QUERY_DEFAULT_INCLUDE_DATA,
                    description="Hydrate target payload data. This requires limit 1 and is off by default.",
                ),
            ],
        ),
        _op(
            "ai.profiles",
            "ai",
            "profiles",
            "Return SDK-owned desktop AI chat role profiles.",
            sdk="desktop_chat_profiles",
            rest="GET /desktop/ai/profiles",
            payload="paradev.desktop.ai-chat-profiles.v1",
            inputs=[_input("project_root", "path")],
        ),
        _op(
            "ai.profile.write",
            "ai",
            "profiles",
            "Write one SDK-owned desktop AI chat role profile override.",
            sdk="desktop_write_chat_profile",
            rest="PUT /desktop/ai/profiles/{profile_id}",
            mutates=True,
            payload="paradev.desktop.ai-chat-profiles.v1",
            inputs=[
                _input("profile_id", "string", required=True),
                _input(
                    "profile",
                    "object",
                    required=True,
                    description="AI chat profile fields to override, including prompt, label, detail, and sourceKinds.",
                ),
                _input("project_root", "path"),
            ],
        ),
        _op(
            "ai.profile.reset",
            "ai",
            "profiles",
            "Reset one SDK-owned desktop AI chat role profile override to built-in defaults.",
            sdk="desktop_reset_chat_profile",
            rest="DELETE /desktop/ai/profiles/{profile_id}",
            mutates=True,
            payload="paradev.desktop.ai-chat-profiles.v1",
            inputs=[
                _input("profile_id", "string", required=True),
                _input("project_root", "path"),
            ],
        ),
        _op(
            "ai.chat",
            "ai",
            "chat",
            "Send one desktop AI chat prompt through the Python SDK and HeavenBase.",
            sdk="desktop_chat",
            rest="POST /desktop/ai/chat",
            payload="paradev.desktop.ai-chat.v1",
            inputs=[
                _input("provider", "string", required=True, default="deepseek"),
                _input("model", "string", required=True, default="deepseek-v4-flash"),
                _input("gateway", "string", required=True, default="openai"),
                _input(
                    "preset",
                    "string",
                    default="chat",
                    choices=["system", "chat", "reason", "coder"],
                    description="Optional HeavenBase route preset for this chat request.",
                ),
                _input(
                    "key_env",
                    "string",
                    description="Optional API-key environment variable name for this chat request.",
                ),
                _input(
                    "base_url",
                    "string",
                    description="Optional LLM base URL override for this chat request.",
                ),
                _input("prompt", "string", required=True),
                _input("role", "string", default="chat"),
                _input("project_root", "path"),
                _input(
                    "sources",
                    "array",
                    description="Optional AI chat source/context descriptors resolved by the Python desktop SDK.",
                ),
            ],
        ),
        _op(
            "surface.frontend_api",
            "surfaces",
            "frontend-api",
            "Return this frontend API contract.",
            sdk="get_frontend_api_selection",
            cli="frontend-api",
            rest="GET /frontend-api",
            mcp="frontend_api",
            payload=FRONTEND_API_SCHEMA,
            selectors=FRONTEND_API_SELECTORS,
            inputs=[
                _input("operation_id", "string"),
                _input("group_id", "string"),
                _input("form", "boolean", default=False),
            ],
        ),
        _op(
            "surface.frontend_api.workspace",
            "surfaces",
            "frontend-api-workspace",
            "Return the SDK-owned frontend workspace action projection.",
            sdk="get_frontend_api_workspace",
            cli="frontend-api --workspace",
            rest="GET /frontend-api/workspace",
            payload=FRONTEND_API_WORKSPACE_SCHEMA,
            inputs=[],
        ),
        _op(
            "surface.frontend_api.action",
            "surfaces",
            "frontend-api-action",
            "Return one frontend operation's workspace action, form, bindings, and option-source summary.",
            sdk="get_frontend_api_action",
            cli="frontend-api --operation --action",
            rest="GET /frontend-api/action",
            payload=FRONTEND_API_ACTION_DETAIL_SCHEMA,
            inputs=[_input("operation_id", "string", required=True)],
        ),
        _op(
            "surface.frontend_api.normalize",
            "surfaces",
            "frontend-api-normalize",
            "Normalize submitted frontend API form values into adapter buckets.",
            sdk="normalize_frontend_api_inputs",
            cli="frontend-api --operation --values-json",
            rest="POST /frontend-api/normalize",
            payload=FRONTEND_API_INPUTS_SCHEMA,
            inputs=[
                _input("operation_id", "string", required=True),
                _input("values", "object", default={}),
            ],
        ),
        _op(
            "surface.frontend_api.rest_request",
            "surfaces",
            "frontend-api-rest-request",
            "Plan the REST request for submitted frontend API form values.",
            sdk="plan_frontend_api_rest_request",
            cli="frontend-api --operation --values-json --rest-request",
            rest="POST /frontend-api/rest-request",
            payload=FRONTEND_API_REST_REQUEST_SCHEMA,
            inputs=[
                _input("operation_id", "string", required=True),
                _input("values", "object", default={}),
            ],
        ),
        _op(
            "surface.frontend_api.options",
            "surfaces",
            "frontend-api-options",
            "Resolve dynamic form field options from SDK-owned option-source providers.",
            sdk="resolve_frontend_api_options",
            cli="frontend-api --operation --option-field --values-json",
            rest="POST /frontend-api/options",
            payload=FRONTEND_API_OPTIONS_SCHEMA,
            inputs=[
                _input("operation_id", "string", required=True),
                _input("field_name", "string", required=True),
                _input("values", "object", default={}),
            ],
        ),
        _op(
            "surface.frontend_api.binding_lookup",
            "surfaces",
            "frontend-api-binding-lookup",
            "Map one SDK, CLI, REST, MCP, or LSP surface call key back to frontend operation ids.",
            sdk="get_frontend_api_binding_lookup",
            cli="frontend-api --binding-surface --binding-key",
            rest="GET /frontend-api/binding",
            payload=FRONTEND_API_BINDING_LOOKUP_SCHEMA,
            inputs=[
                _input(
                    "binding_surface",
                    "string",
                    required=True,
                    choices=FRONTEND_API_BINDING_SURFACES,
                ),
                _input("binding_key", "string", required=True),
            ],
        ),
        _op(
            "surface.architecture",
            "surfaces",
            "architecture",
            "Return the SDK-owned architecture graph.",
            sdk="get_architecture_spec",
            cli="architecture",
            rest="GET /architecture",
            mcp="list_surfaces",
            inputs=[],
        ),
        _op(
            "surface.openapi",
            "surfaces",
            "openapi",
            "Return the local REST/OpenAPI seed.",
            sdk="get_openapi_seed",
            inputs=[],
        ),
        _op(
            "surface.cli_contract",
            "surfaces",
            "cli-contract",
            "Return the CLI adapter contract.",
            sdk="get_cli_contract",
            inputs=[],
        ),
        _op(
            "surface.mcp_contract",
            "surfaces",
            "mcp-contract",
            "Return the MCP toolkit contract.",
            sdk="get_mcp_contract",
            inputs=[],
        ),
        _op(
            "surface.lsp_contract",
            "surfaces",
            "lsp-contract",
            "Return the LSP capability contract.",
            sdk="get_lsp_contract",
            inputs=[],
        ),
    ]


def _frontend_api_workspace(
    operations: Sequence[dict[str, object]],
) -> dict[str, object]:
    rows = {str(row["id"]): row for row in operations}
    sections = [_workspace_section(section, rows) for section in FRONTEND_API_WORKSPACE_SECTIONS]
    return {
        "schema": FRONTEND_API_WORKSPACE_SCHEMA,
        "contract_schema": FRONTEND_API_SCHEMA,
        "status": "alpha",
        "sdk_owned": True,
        "sections": sections,
        "index": _workspace_index(sections),
    }


def _frontend_api_action_sections(workspace: Mapping[str, object], operation_id: str) -> list[str]:
    index = workspace.get("index")
    operation_index = index.get("operation_id") if isinstance(index, Mapping) else None
    sections = operation_index.get(operation_id, []) if isinstance(operation_index, Mapping) else []
    return [str(section_id) for section_id in sections] if isinstance(sections, Sequence) and not isinstance(sections, (str, bytes)) else []


def _frontend_api_workspace_action(workspace: Mapping[str, object], operation_id: str) -> dict[str, object]:
    sections = workspace.get("sections")
    if not isinstance(sections, Sequence) or isinstance(sections, (str, bytes)):
        return {}
    for section in sections:
        if not isinstance(section, Mapping):
            continue
        actions = section.get("actions")
        if not isinstance(actions, Sequence) or isinstance(actions, (str, bytes)):
            continue
        for action in actions:
            if isinstance(action, dict) and action.get("operation_id") == operation_id:
                return dict(action)
    return {}


def _frontend_api_operation_has_form(operation: Mapping[str, object]) -> bool:
    inputs = operation.get("inputs")
    return isinstance(inputs, Sequence) and not isinstance(inputs, (str, bytes)) and bool(inputs)


def _frontend_api_action_option_sources(
    form: Mapping[str, object] | None,
) -> dict[str, object]:
    if form is None:
        return {}
    fields = form.get("fields")
    if not isinstance(fields, Sequence) or isinstance(fields, (str, bytes)):
        return {}
    sources: dict[str, object] = {}
    for field in fields:
        if not isinstance(field, Mapping):
            continue
        name = field.get("name")
        option_source = field.get("option_source")
        if isinstance(name, str) and isinstance(option_source, Mapping):
            sources[name] = _copy_option_source(option_source)
    return sources


def _workspace_section(section: Mapping[str, object], rows: Mapping[str, dict[str, object]]) -> dict[str, object]:
    operation_ids = [str(operation_id) for operation_id in section["operation_ids"]]
    actions = [_workspace_action(rows[operation_id]) for operation_id in operation_ids]
    return {
        "id": section["id"],
        "title": section["title"],
        "summary": section["summary"],
        "default_operation_id": section["default_operation_id"],
        "operation_ids": operation_ids,
        "actions": actions,
    }


def _workspace_action(operation: Mapping[str, object]) -> dict[str, object]:
    inputs = operation.get("inputs")
    has_form = isinstance(inputs, Sequence) and not isinstance(inputs, (str, bytes)) and bool(inputs)
    action = {
        "schema": FRONTEND_API_ACTION_SCHEMA,
        "operation_id": operation["id"],
        "title": _operation_title(str(operation["id"])),
        "group": operation["group"],
        "status": operation["status"],
        "read_only": operation["read_only"],
        "mutates": bool(operation.get("mutates", False)),
        "form": has_form,
        "summary": operation["summary"],
        "execution": _workspace_action_execution(operation, has_form),
    }
    if "payload" in operation:
        action["payload"] = operation["payload"]
    if has_form:
        action["form_schema"] = FRONTEND_API_FORM_SCHEMA
    bindings = operation.get("bindings")
    if isinstance(bindings, Mapping):
        action["bindings"] = _copy_bindings(bindings)
    return action


def _workspace_action_execution(operation: Mapping[str, object], has_form: bool) -> dict[str, object]:
    if operation["status"] == "frontend-local":
        execution: dict[str, object] = {
            "kind": "frontend-local",
            "default_surface": "frontend-local",
            "available_surfaces": [],
            "binding": {},
            "requires_values": has_form,
            "state_scope": "workspace",
            "confirmation": _action_confirmation(operation),
        }
        if has_form:
            execution["normalizer_schema"] = FRONTEND_API_INPUTS_SCHEMA
        return execution

    bindings = operation.get("bindings")
    binding_rows = bindings if isinstance(bindings, Mapping) else {}
    default_surface = _default_action_surface(binding_rows)
    execution = {
        "kind": "adapter" if default_surface else "unavailable",
        "default_surface": default_surface or "none",
        "available_surfaces": list(binding_rows),
        "binding": _copy_binding(binding_rows.get(default_surface, {})) if default_surface else {},
        "requires_values": has_form,
        "confirmation": _action_confirmation(operation),
    }
    if has_form:
        execution["normalizer_schema"] = FRONTEND_API_INPUTS_SCHEMA
    if "rest" in binding_rows:
        execution["rest_request_schema"] = FRONTEND_API_REST_REQUEST_SCHEMA
    return execution


def _action_confirmation(operation: Mapping[str, object]) -> dict[str, object]:
    required = bool(operation.get("mutates", False)) and operation["status"] != "frontend-local"
    return {
        "schema": FRONTEND_API_CONFIRMATION_SCHEMA,
        "required": required,
        "scope": _confirmation_scope(operation),
        "style": _confirmation_style(operation, required),
        "title": _confirmation_title(operation),
        "summary": operation["summary"],
        "confirm_fields": _confirmation_fields(operation),
        "default_confirmed": not required,
    }


def _confirmation_scope(operation: Mapping[str, object]) -> str:
    if not operation.get("mutates", False):
        return "none"
    if operation["status"] == "frontend-local":
        return "workspace-state"
    group = str(operation["group"])
    if group == "catalog":
        return "catalog"
    if group == "projects" and operation["id"] == "project.config":
        return "configuration"
    return "project-files"


def _confirmation_style(operation: Mapping[str, object], required: bool) -> str:
    if not required:
        return "state" if operation["status"] == "frontend-local" and operation.get("mutates", False) else "none"
    action = str(operation["action"])
    operation_id = str(operation["id"])
    if action in DESTRUCTIVE_ACTIONS or operation_id.endswith(".remove"):
        return "destructive"
    return "write"


def _confirmation_title(operation: Mapping[str, object]) -> str:
    title = _operation_title(str(operation["id"]))
    return f"Confirm {title}" if bool(operation.get("mutates", False)) and operation["status"] != "frontend-local" else title


def _confirmation_fields(operation: Mapping[str, object]) -> list[str]:
    inputs = operation.get("inputs", ())
    if not isinstance(inputs, Sequence) or isinstance(inputs, (str, bytes)):
        return []
    return [
        str(field["name"])
        for field in inputs
        if isinstance(field, Mapping) and str(field.get("name", "")) in CONFIRMATION_FIELD_NAMES and field.get("default") is False
    ]


def _default_action_surface(bindings: Mapping[str, object]) -> str:
    for surface in ("rest", "sdk", "lsp", "mcp", "cli"):
        if surface in bindings:
            return surface
    return ""


def _copy_bindings(bindings: Mapping[str, object]) -> dict[str, object]:
    return {str(surface): _copy_binding(binding) for surface, binding in bindings.items()}


def _copy_binding(binding: object) -> dict[str, object]:
    if not isinstance(binding, Mapping):
        return {}
    copied: dict[str, object] = {}
    for key, value in binding.items():
        if isinstance(value, Mapping):
            copied[str(key)] = dict(value)
        else:
            copied[str(key)] = value
    return copied


def _operation_title(operation_id: str) -> str:
    parts = operation_id.replace(".", "_").replace("-", "_").split("_")
    return " ".join(_input_label_part(part) for part in parts if part)


def _workspace_index(sections: Sequence[dict[str, object]]) -> dict[str, object]:
    section_index: dict[str, list[str]] = {}
    operation_rows: list[dict[str, str]] = []
    for section in sections:
        section_id = str(section["id"])
        operation_ids = [str(operation_id) for operation_id in section["operation_ids"]]
        section_index[section_id] = operation_ids
        operation_rows.extend({"operation_id": operation_id, "section_id": section_id} for operation_id in operation_ids)
    (operation_index,) = api_value_indexes(operation_rows, "operation_id", value_field="section_id")
    return {"section": section_index, "operation_id": operation_index}


def _op(
    identifier: str,
    group: str,
    action: str,
    summary: str,
    *,
    status: str = "implemented",
    mutates: bool = False,
    sdk: str | None = None,
    cli: str | None = None,
    rest: str | None = None,
    mcp: str | None = None,
    lsp: str | None = None,
    payload: str | None = None,
    selectors: Sequence[str] | None = None,
    inputs: Sequence[dict[str, object]] | None = None,
) -> dict[str, object]:
    row: dict[str, object] = {
        "id": identifier,
        "group": group,
        "action": action,
        "summary": summary,
        "status": status,
        "read_only": not mutates,
    }
    if mutates:
        row["mutates"] = True
    if selectors:
        row["selectors"] = list(selectors)
    if inputs is not None:
        row["inputs"] = [dict(field) for field in inputs]
    for key, value in (
        ("sdk", sdk),
        ("cli", cli),
        ("rest", rest),
        ("mcp", mcp),
        ("lsp", lsp),
        ("payload", payload),
    ):
        if value:
            row[key] = value
    bindings = _surface_bindings(sdk=sdk, cli=cli, rest=rest, mcp=mcp, lsp=lsp)
    if bindings:
        row["bindings"] = bindings
    return row


def _surface_bindings(
    *,
    sdk: str | None = None,
    cli: str | None = None,
    rest: str | None = None,
    mcp: str | None = None,
    lsp: str | None = None,
) -> dict[str, dict[str, object]]:
    bindings: dict[str, dict[str, object]] = {}
    if sdk:
        bindings["sdk"] = {"call": sdk}
    if cli:
        bindings["cli"] = {"command": cli}
    if rest:
        bindings["rest"] = _rest_binding(rest)
    if mcp:
        bindings["mcp"] = {"tool": mcp}
    if lsp:
        bindings["lsp"] = {"method": lsp}
    return bindings


def _rest_binding(binding: str) -> dict[str, object]:
    method, target = binding.split(" ", maxsplit=1)
    path, _, query_string = target.partition("?")
    return {"method": method, "path": path, "query": _rest_query(query_string)}


def _rest_query(query_string: str) -> dict[str, object]:
    query: dict[str, object] = {}
    if not query_string:
        return query
    for part in query_string.split("&"):
        key, _, value = part.partition("=")
        if key:
            query[key] = _rest_query_value(value)
    return query


def _rest_query_value(value: str) -> object:
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def _input(
    name: str,
    value_type: str,
    *,
    required: bool = False,
    default: object = None,
    maps_to: str | None = None,
    choices: Sequence[object] = (),
    minimum: int | None = None,
    maximum: int | None = None,
    item_type: str | None = None,
    max_items: int | None = None,
    nonblank: bool = False,
    label: str | None = None,
    description: str | None = None,
    option_source: Mapping[str, object] | None = None,
) -> dict[str, object]:
    field: dict[str, object] = {"name": name, "type": value_type, "required": required}
    if default is not None:
        field["default"] = default
    if maps_to is not None:
        field["maps_to"] = maps_to
    if choices:
        field["choices"] = list(choices)
    if minimum is not None:
        field["minimum"] = minimum
    if maximum is not None:
        field["maximum"] = maximum
    if item_type is not None:
        field["item_type"] = item_type
    if max_items is not None:
        field["max_items"] = max_items
    if nonblank:
        field["nonblank"] = True
    if label is not None:
        field["label"] = label
    if description is not None:
        field["description"] = description
    if option_source is not None:
        field["option_source"] = _copy_option_source(option_source)
    return field


def _frontend_api_form_field(operation: dict[str, object], field: dict[str, object]) -> dict[str, object]:
    name = str(field["name"])
    value_type = str(field["type"])
    schema = _input_json_schema(value_type)
    normalized: dict[str, object] = {
        "name": name,
        "label": _input_label(name, field),
        "description": _input_description(operation, name, field),
        "type": value_type,
        "required": bool(field.get("required", False)),
        "control": _input_control(value_type, field.get("choices"), field.get("option_source")),
        "target": _input_target(operation, name),
        "schema": schema,
    }
    if "default" in field:
        default = field["default"]
        normalized["default"] = default
        schema["default"] = default
    if "maps_to" in field:
        normalized["maps_to"] = str(field["maps_to"])
    option_source = field.get("option_source")
    if isinstance(option_source, Mapping):
        copied_source = _copy_option_source(option_source)
        normalized["option_source"] = copied_source
        schema["x-paradev-option-source"] = _copy_option_source(copied_source)
    if "choices" in field:
        choices = _input_choices(field["choices"])
        normalized["choices"] = choices
        schema["enum"] = choices
    if "minimum" in field:
        minimum = field["minimum"]
        if isinstance(minimum, int):
            normalized["minimum"] = minimum
            schema["minimum"] = minimum
    if "maximum" in field:
        maximum = field["maximum"]
        if isinstance(maximum, int):
            normalized["maximum"] = maximum
            schema["maximum"] = maximum
    if "item_type" in field:
        item_type = field["item_type"]
        if isinstance(item_type, str) and value_type == "array":
            normalized["item_type"] = item_type
            schema["items"] = _input_json_schema(item_type)
    if "max_items" in field:
        max_items = field["max_items"]
        if isinstance(max_items, int) and value_type == "array":
            normalized["max_items"] = max_items
            schema["maxItems"] = max_items
    if field.get("nonblank") is True:
        normalized["nonblank"] = True
        schema["minLength"] = 1
        schema["pattern"] = r".*\S.*"
    return normalized


def _copy_option_source(option_source: Mapping[str, object]) -> dict[str, object]:
    copied: dict[str, object] = {}
    for key, value in option_source.items():
        if isinstance(value, Mapping):
            copied[str(key)] = dict(value)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            copied[str(key)] = list(value)
        else:
            copied[str(key)] = value
    return copied


def _input_label(name: str, field: Mapping[str, object]) -> str:
    label = field.get("label")
    if isinstance(label, str) and label.strip():
        return label.strip()
    return " ".join(_input_label_part(part) for part in name.split("_"))


def _input_label_part(part: str) -> str:
    return FRONTEND_API_LABEL_WORDS.get(part, part.capitalize())


def _input_description(operation: Mapping[str, object], name: str, field: Mapping[str, object]) -> str:
    description = field.get("description")
    if isinstance(description, str) and description.strip():
        return description.strip()
    if name == "path":
        return _path_input_description(operation)
    if name in FRONTEND_API_FIELD_DESCRIPTIONS:
        return FRONTEND_API_FIELD_DESCRIPTIONS[name]
    return f"{_input_label(name, field)} value for {operation['id']}."


def _path_input_description(operation: Mapping[str, object]) -> str:
    group = str(operation["group"])
    if group in FRONTEND_API_PATH_DESCRIPTIONS:
        return FRONTEND_API_PATH_DESCRIPTIONS[group]
    if group in PROJECT_INPUT_GROUPS or group == "projects":
        return "Project root, project destination, or nested path used to find the project."
    return "Filesystem path used by the operation."


def _validate_frontend_api_input_value(operation_id: str, field: Mapping[str, object], value: object) -> None:
    choices = _input_choices(field.get("choices"))
    if choices and value not in choices:
        names = ", ".join(str(choice) for choice in choices)
        raise ValueError(f"Invalid frontend API input for {operation_id}: {field['name']} must be one of {names}.")

    minimum = field.get("minimum")
    if isinstance(minimum, int):
        if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
            raise ValueError(f"Invalid frontend API input for {operation_id}: {field['name']} must be >= {minimum}.")
    maximum = field.get("maximum")
    if isinstance(maximum, int):
        if not isinstance(value, int) or isinstance(value, bool) or value > maximum:
            raise ValueError(f"Invalid frontend API input for {operation_id}: {field['name']} must be <= {maximum}.")
    max_items = field.get("max_items")
    if isinstance(max_items, int):
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise ValueError(f"Invalid frontend API input for {operation_id}: {field['name']} must be an array.")
        if len(value) > max_items:
            raise ValueError(f"Invalid frontend API input for {operation_id}: {field['name']} cannot contain more than {max_items} items.")
        if field.get("item_type") == "object" and any(not isinstance(item, Mapping) for item in value):
            raise ValueError(f"Invalid frontend API input for {operation_id}: {field['name']} items must be objects.")
    if field.get("nonblank") is True and (not isinstance(value, str) or not value.strip()):
        raise ValueError(f"Invalid frontend API input for {operation_id}: {field['name']} must be a nonblank string.")


def _input_choices(value: object) -> list[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return list(value)


def _input_target(operation: dict[str, object], name: str) -> str:
    if operation["id"] in {
        "surface.frontend_api",
        "surface.frontend_api.action",
        "surface.frontend_api.normalize",
        "surface.frontend_api.rest_request",
        "surface.frontend_api.options",
        "surface.frontend_api.binding_lookup",
    }:
        if name in FRONTEND_API_SELECTORS or name in {
            "field_name",
            "binding_surface",
            "binding_key",
        }:
            return "selectors"
    if operation["id"] == "surface.frontend_api":
        if name == "form":
            return "projections"
    if name == "path" and operation["group"] in PROJECT_INPUT_GROUPS:
        return "project"
    return "parameters"


def _input_json_schema(value_type: str) -> dict[str, object]:
    if value_type == "array":
        return {"type": "array", "items": {"type": "string"}}
    if value_type == "boolean":
        return {"type": "boolean"}
    if value_type == "integer":
        return {"type": "integer"}
    if value_type == "object":
        return {"type": "object"}
    if value_type == "path":
        return {"type": "string", "format": "path"}
    if value_type == "text":
        return {"type": "string", "format": "text"}
    return {"type": "string"}


def _input_control(value_type: str, choices: object = None, option_source: object = None) -> str:
    if _input_choices(choices):
        return "select"
    if isinstance(option_source, Mapping):
        return "combobox"
    return {
        "array": "json",
        "boolean": "checkbox",
        "integer": "number",
        "object": "json",
        "path": "path",
        "text": "textarea",
    }.get(value_type, "text")


def _frontend_api_index(operations: list[dict[str, object]], workspace: Mapping[str, object] | None = None) -> dict[str, object]:
    index = _frontend_api_empty_index(workspace or {})
    for row in operations:
        _add_frontend_api_index_row_entries(index, row)
    return index


def _frontend_api_empty_index(workspace: Mapping[str, object]) -> dict[str, object]:
    return {
        "id": {},
        "group": {},
        "status": {},
        "mode": _frontend_api_empty_mode_index(),
        "action": {},
        "binding": {},
        "payload": {},
        "workspace_section": _frontend_api_workspace_section_index(workspace or {}),
        "surface": _frontend_api_empty_surface_index(),
    }


def _frontend_api_empty_mode_index() -> dict[str, list[str]]:
    return {"read": [], "write": []}


def _frontend_api_empty_surface_index() -> dict[str, list[str]]:
    return {
        **{surface: [] for surface in FRONTEND_API_SURFACE_COVERAGE_COLUMNS},
        "unbound": [],
    }


def _add_frontend_api_index_row_entries(index: dict[str, object], row: Mapping[str, object]) -> None:
    identifier = str(row["id"])
    _add_frontend_api_primary_index_entries(index, identifier, row)
    _add_frontend_api_payload_index_entry(index["payload"], identifier, row)
    _add_frontend_api_mode_index_entry(index["mode"], identifier, row)
    _add_frontend_api_surface_binding_index_entries(index, identifier, row.get("bindings", {}))


def _add_frontend_api_primary_index_entries(
    index: dict[str, object],
    identifier: str,
    row: Mapping[str, object],
) -> None:
    for field in ("id", "group", "status", "action"):
        bucket = index[field]
        if isinstance(bucket, dict):
            append_api_index_entry(bucket, row[field], identifier)


def _add_frontend_api_payload_index_entry(
    payload_index: object,
    identifier: str,
    row: Mapping[str, object],
) -> None:
    if isinstance(payload_index, dict):
        payload = str(row["payload"]) if row.get("payload") else "untyped"
        append_api_index_entry(payload_index, payload, identifier)


def _add_frontend_api_mode_index_entry(
    mode_index: object,
    identifier: str,
    row: Mapping[str, object],
) -> None:
    if isinstance(mode_index, dict):
        mode_index["write" if row.get("mutates") else "read"].append(identifier)


def _add_frontend_api_surface_binding_index_entries(
    index: dict[str, object],
    identifier: str,
    bindings: object,
) -> None:
    surface_index = index["surface"]
    if isinstance(bindings, dict) and bindings:
        _add_frontend_api_surface_index_entries(surface_index, identifier, bindings)
        _add_frontend_api_binding_index_entries(index["binding"], identifier, bindings)
        return
    if isinstance(surface_index, dict):
        surface_index["unbound"].append(identifier)


def _add_frontend_api_surface_index_entries(
    surface_index: object,
    identifier: str,
    bindings: dict[object, object],
) -> None:
    if not isinstance(surface_index, dict):
        return
    for surface in FRONTEND_API_SURFACE_COVERAGE_COLUMNS:
        if surface in bindings:
            surface_index[surface].append(identifier)


def _add_frontend_api_binding_index_entries(
    binding_index: object,
    identifier: str,
    bindings: dict[object, object],
) -> None:
    if not isinstance(binding_index, dict):
        return
    for surface, binding in bindings.items():
        key = _binding_index_key(str(surface), binding)
        if key is not None:
            append_api_nested_index_entry(binding_index, surface, key, identifier)


def _frontend_api_workspace_section_index(
    workspace: Mapping[str, object],
) -> dict[str, list[str]]:
    section_index = _frontend_api_workspace_section_source_index(workspace)
    if section_index is None:
        return {}
    return {
        str(section_id): _frontend_api_operation_id_list(operation_ids)
        for section_id, operation_ids in section_index.items()
        if _is_frontend_api_operation_id_sequence(operation_ids)
    }


def _frontend_api_workspace_section_source_index(
    workspace: Mapping[str, object],
) -> Mapping[str, object] | None:
    workspace_index = workspace.get("index", {})
    section_index = workspace_index.get("section", {}) if isinstance(workspace_index, Mapping) else {}
    return section_index if isinstance(section_index, Mapping) else None


def _binding_index_key(surface: str, binding: object) -> str | None:
    if not isinstance(binding, dict):
        return None
    if surface == "sdk":
        return str(binding["call"])
    if surface == "cli":
        return str(binding["command"])
    if surface == "mcp":
        return str(binding["tool"])
    if surface == "lsp":
        return str(binding["method"])
    if surface == "rest":
        return _rest_index_key(binding)
    return None


def _rest_index_key(binding: dict[str, object]) -> str:
    method = str(binding["method"])
    path = str(binding["path"])
    query = binding.get("query", {})
    if not isinstance(query, dict) or not query:
        return f"{method} {path}"
    query_string = _rest_query_string(query)
    return f"{method} {path}?{query_string}"


def _rest_query_string(query: object) -> str:
    if not isinstance(query, Mapping) or not query:
        return ""
    return "&".join(f"{key}={_rest_index_value(query[key])}" for key in sorted(query))


def _rest_index_value(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def _typescript_const_array(name: str, values: Sequence[str]) -> str:
    rendered = dumps_json(list(values), indent=2).rstrip()
    return f"export const {name} = {rendered} as const;"


def _frontend_api_sdk_cli_summary_rows(contract: object) -> list[str]:
    summary_counts = _frontend_api_sdk_cli_summary_count_maps(contract)
    if summary_counts is None:
        return []
    group_counts, group_surface_counts = summary_counts
    return _frontend_api_table_rows(
        _frontend_api_sdk_cli_summary_cells(
            group,
            _frontend_api_mapping_or_empty(group_counts.get(str(group["id"]), {})),
            _frontend_api_mapping_or_empty(group_surface_counts.get(str(group["id"]), {})),
        )
        for group in _frontend_api_group_rows(contract)
    )


def _frontend_api_sdk_cli_summary_count_maps(
    contract: object,
) -> tuple[Mapping[str, object], Mapping[str, object]] | None:
    if not isinstance(contract, Mapping):
        return None
    summary = contract.get("summary", {})
    if not isinstance(summary, Mapping):
        return None
    group_counts = summary.get("group_counts", {})
    group_surface_counts = summary.get("group_surface_counts", {})
    if not isinstance(group_counts, Mapping) or not isinstance(group_surface_counts, Mapping):
        return None
    return group_counts, group_surface_counts


def _frontend_api_sdk_cli_summary_cells(
    group: Mapping[str, object],
    counts: Mapping[str, object],
    surface_counts: Mapping[str, object],
) -> list[str]:
    return [
        _code_cell(group["id"]),
        _markdown_cell(group.get("title", "")),
        *_frontend_api_summary_count_cells(counts, "operation_count"),
        *_frontend_api_summary_count_cells(surface_counts, "sdk", "cli"),
        *_frontend_api_summary_count_cells(counts, "read", "write"),
    ]


def _frontend_api_reference_summary_section(summary: Mapping[str, object]) -> list[str]:
    return [
        "## Summary / 汇总",
        "",
        f"- Operations / 操作数: {summary['operation_count']}",
        f"- Groups / 分组数: {summary['group_count']}",
        f"- Workspace sections / 工作区分区数: {summary['workspace_section_count']}",
        "",
        *_frontend_api_table_lines(
            (
                "Group",
                "Operations",
                "Read",
                "Write",
                "Implemented",
                "Planned",
                "Frontend-local",
            ),
            _frontend_api_reference_summary_rows(summary),
        ),
    ]


def _frontend_api_reference_summary_rows(summary: object) -> list[str]:
    return _frontend_api_static_group_summary_rows(
        summary,
        "group_counts",
        lambda counts: _frontend_api_summary_count_cells(
            counts,
            "operation_count",
            "read",
            "write",
            "implemented",
            "planned",
            "frontend-local",
        ),
    )


def _frontend_api_surface_coverage_rows(summary: object) -> list[str]:
    return _frontend_api_static_group_summary_rows(
        summary,
        "group_surface_counts",
        lambda counts: _frontend_api_summary_count_cells(
            counts,
            "operation_count",
            "sdk",
            "cli",
            "rest",
            "mcp",
            "lsp",
            "unbound",
        ),
    )


def _frontend_api_static_group_summary_rows(
    summary: object,
    summary_key: str,
    cells_for_counts: _FrontendApiStaticSummaryCellBuilder,
) -> list[str]:
    group_counts = _frontend_api_static_group_summary_counts(summary, summary_key)
    if group_counts is None:
        return []
    return _frontend_api_table_rows(
        _frontend_api_static_group_summary_cells(
            str(group["id"]),
            _frontend_api_mapping_or_empty(group_counts.get(str(group["id"]), {})),
            cells_for_counts,
        )
        for group in FRONTEND_API_GROUPS
    )


def _frontend_api_static_group_summary_counts(summary: object, summary_key: str) -> Mapping[str, object] | None:
    if not isinstance(summary, Mapping):
        return None
    group_counts = summary.get(summary_key, {})
    return group_counts if isinstance(group_counts, Mapping) else None


def _frontend_api_static_group_summary_cells(
    group_id: object,
    counts: Mapping[str, object],
    cells_for_counts: _FrontendApiStaticSummaryCellBuilder,
) -> list[str]:
    return [_code_cell(group_id), *cells_for_counts(counts)]


def _frontend_api_mapping_or_empty(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _frontend_api_summary_count_cells(counts: Mapping[str, object], *names: str) -> list[str]:
    return [_markdown_cell(counts.get(name, 0)) for name in names]


def _frontend_api_index_catalog_rows() -> list[str]:
    return _frontend_api_table_rows(_frontend_api_index_catalog_cells(row) for row in get_frontend_api_index_catalog())


def _frontend_api_index_catalog_section(body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Index Catalog / Index 目录",
        ("Index", "Contract Path", "Python Helper", "TypeScript Helper", "Use"),
        _frontend_api_index_catalog_rows(),
        level=3,
        body=body,
    )


def _frontend_api_index_catalog_cells(row: Mapping[str, object]) -> list[str]:
    return [
        _code_cell(row["id"]),
        _code_cell(row["contract_path"]),
        _code_cell(row["python_helper"]),
        _code_cell(row["typescript_helper"]),
        _markdown_cell(row["usage"]),
    ]


def _frontend_api_group_index_rows(contract: object) -> list[str]:
    if not isinstance(contract, Mapping):
        return []
    group_index = _frontend_api_contract_index_mapping(contract, "group")
    if group_index is None:
        return []
    return _frontend_api_table_rows(
        _frontend_api_operation_id_detail_cells(
            [
                _code_cell(group["id"]),
                _markdown_cell(group.get("title", "")),
            ],
            group_index.get(str(group["id"]), []),
        )
        for group in _frontend_api_group_rows(contract)
    )


def _frontend_api_group_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Index / Group 索引",
        ("Group", "Title", "Operations", "Operation IDs"),
        _frontend_api_group_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_status_index_rows(contract: object) -> list[str]:
    status_index = _frontend_api_contract_index_mapping(contract, "status")
    if status_index is None:
        return []
    return _frontend_api_operation_id_index_rows(status_index)


def _frontend_api_status_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Status Index / Status 索引",
        ("Status", "Operations", "Operation IDs"),
        _frontend_api_status_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_mode_index_rows(contract: object) -> list[str]:
    mode_index = _frontend_api_contract_index_mapping(contract, "mode")
    if mode_index is None:
        return []
    return _frontend_api_operation_id_index_rows(mode_index, ("read", "write"))


def _frontend_api_mode_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Read/Write Mode Index / Read Write 模式索引",
        ("Mode", "Operations", "Operation IDs"),
        _frontend_api_mode_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_surface_index_rows(contract: object) -> list[str]:
    surface_index = _frontend_api_contract_index_mapping(contract, "surface")
    if surface_index is None:
        return []
    return _frontend_api_operation_id_index_rows(
        surface_index,
        (*FRONTEND_API_SURFACE_COVERAGE_COLUMNS, "unbound"),
    )


def _frontend_api_surface_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Surface Index / Surface 索引",
        ("Surface", "Operations", "Operation IDs"),
        _frontend_api_surface_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_surface_coverage_section(summary: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Surface Coverage / Surface 覆盖",
        ("Group", "Operations", "SDK", "CLI", "REST", "MCP", "LSP", "Unbound"),
        _frontend_api_surface_coverage_rows(summary),
        level=3,
        body=body,
    )


def _frontend_api_operation_id_index_rows(
    index: Mapping[str, object],
    keys: Sequence[object] | None = None,
) -> list[str]:
    if keys is None:
        return _frontend_api_table_rows(_frontend_api_operation_id_detail_cells([_code_cell(key)], operation_ids) for key, operation_ids in index.items())
    return _frontend_api_table_rows(_frontend_api_operation_id_detail_cells([_code_cell(key)], index.get(key, [])) for key in keys)


def _frontend_api_operation_id_detail_cells(prefix_cells: Sequence[str], operation_ids: object) -> list[str]:
    return [
        *prefix_cells,
        *_frontend_api_operation_id_cells(operation_ids),
    ]


def _frontend_api_rest_route_index_rows(contract: object) -> list[str]:
    routes: dict[str, dict[str, object]] = {}
    order: list[str] = []
    for operation_row, rest in _frontend_api_contract_rest_operation_rows(contract):
        route_key = _rest_index_key(dict(rest))
        if route_key not in routes:
            routes[route_key] = {
                "method": str(rest["method"]),
                "path": str(rest["path"]),
                "query": _rest_query_string(rest.get("query", {})),
                "operation_ids": [],
            }
            order.append(route_key)
        operation_ids = routes[route_key]["operation_ids"]
        if isinstance(operation_ids, list):
            operation_ids.append(str(operation_row["id"]))
    return _frontend_api_table_rows(_frontend_api_rest_route_index_cells(routes[route_key]) for route_key in order)


def _frontend_api_rest_route_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "REST Route Index / REST Route 索引",
        ("Method", "Path", "Query", "Operations", "Operation IDs"),
        _frontend_api_rest_route_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_rest_route_index_cells(route: Mapping[str, object]) -> list[str]:
    return _frontend_api_operation_id_detail_cells(
        [
            _code_cell(route["method"]),
            _code_cell(route["path"]),
            _code_cell(route["query"]),
        ],
        route["operation_ids"],
    )


def _frontend_api_rest_request_planner_cells(operation: dict[str, object], rest: Mapping[str, object]) -> list[str]:
    path = str(rest.get("path", ""))
    operation_id = _frontend_api_operation_id(operation)
    return [
        _code_cell(rest.get("method", "")),
        _code_cell(path),
        _code_cell(_rest_query_string(rest.get("query", {}))),
        _frontend_api_code_list_cell(_rest_path_parameter_names(path)),
        _frontend_api_sorted_code_list_cell(_rest_body_inputs(operation_id, operation)),
        _code_cell(operation_id),
    ]


def _frontend_api_rest_request_planner_index_rows(contract: object) -> list[str]:
    return _frontend_api_table_rows(
        _frontend_api_rest_request_planner_cells(operation_row, rest) for operation_row, rest in _frontend_api_contract_rest_operation_rows(contract)
    )


def _frontend_api_rest_request_planner_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "REST Request Planner Index / REST Request Planner 索引",
        (
            "Method",
            "Path",
            "Static Query",
            "Path Params",
            "Body Fields",
            "Operation ID",
        ),
        _frontend_api_rest_request_planner_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_workspace_section_rest_summary_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_operation_summary_rows(contract, _frontend_api_rest_summary_cells)


def _frontend_api_workspace_section_rest_summary_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section REST Summary Index / Workspace Section REST Summary 索引",
        (
            "Workspace Section",
            "Actions",
            "REST Actions",
            "Routes",
            "Methods",
            "Static Queries",
            "Path Params",
            "Body Fields",
            "Dynamic Query Fields",
        ),
        _frontend_api_workspace_section_rest_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_group_rest_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_operation_summary_rows(contract, _frontend_api_rest_summary_cells)


def _frontend_api_group_rest_summary_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group REST Summary Index / Group REST Summary 索引",
        (
            "Group",
            "Operations",
            "REST Operations",
            "Routes",
            "Methods",
            "Static Queries",
            "Path Params",
            "Body Fields",
            "Dynamic Query Fields",
        ),
        _frontend_api_group_rest_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_rest_summary_cells(owner_id: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    rest_count = 0
    routes: set[str] = set()
    method_counts: _FrontendApiCountMap = {}
    static_queries: set[str] = set()
    path_params: set[str] = set()
    body_fields: set[str] = set()
    query_fields: set[str] = set()
    for operation_row, rest in _frontend_api_rest_operation_rows(operations):
        operation_id = _frontend_api_operation_id(operation_row)
        rest_count += 1
        routes.add(_rest_index_key(dict(rest)))
        method = str(rest.get("method", ""))
        _frontend_api_increment_count(method_counts, method)
        query = rest.get("query", {})
        if isinstance(query, Mapping):
            static_queries.update(f"{key}={_rest_index_value(value)}" for key, value in query.items())
        path_names = set(_rest_path_parameter_names(str(rest.get("path", ""))))
        body_names = set(_rest_body_inputs(operation_id, operation_row))
        path_params.update(path_names)
        body_fields.update(body_names)
        for field in _frontend_api_input_rows(operation_row):
            query_name = _frontend_api_mapped_input_name(field)
            if query_name not in path_names and query_name not in body_names:
                query_fields.add(query_name)
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        _markdown_cell(rest_count),
        _markdown_cell(len(routes)),
        _frontend_api_count_list_cell(method_counts),
        _frontend_api_sorted_code_list_cell(static_queries),
        _frontend_api_sorted_code_list_cell(path_params),
        _frontend_api_sorted_code_list_cell(body_fields),
        _frontend_api_sorted_code_list_cell(query_fields),
    ]


def _frontend_api_rest_static_query_index_rows(contract: object) -> list[str]:
    cell_rows: list[list[str]] = []
    for operation_row, rest in _frontend_api_contract_rest_operation_rows(contract):
        query = rest.get("query") if isinstance(rest, Mapping) else None
        if not isinstance(rest, Mapping) or not isinstance(query, Mapping):
            continue
        for key, value in sorted(query.items(), key=lambda item: str(item[0])):
            cell_rows.append(_frontend_api_rest_static_query_cells(operation_row, rest, key, value))
    return _frontend_api_table_rows(cell_rows)


def _frontend_api_rest_static_query_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "REST Static Query Index / REST Static Query 索引",
        ("Query Parameter", "Value", "Operation ID", "Method", "Path", "Type"),
        _frontend_api_rest_static_query_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_rest_static_query_cells(
    operation: dict[str, object],
    rest: Mapping[str, object],
    key: object,
    value: object,
) -> list[str]:
    return [
        _code_cell(str(key)),
        _code_cell(_rest_index_value(value)),
        _code_cell(_frontend_api_operation_id(operation)),
        _code_cell(rest.get("method", "")),
        _code_cell(rest.get("path", "")),
        _code_cell(_rest_static_query_type(value)),
    ]


def _rest_static_query_type(value: object) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if value is None:
        return "null"
    return "string"


def _frontend_api_rest_dynamic_query_field_index_rows(contract: object) -> list[str]:
    cell_rows: list[list[str]] = []
    for operation_row, rest in _frontend_api_contract_rest_operation_rows(contract):
        operation_id = _frontend_api_operation_id(operation_row)
        path_names = set(_rest_path_parameter_names(str(rest.get("path", ""))))
        body_names = _rest_body_inputs(operation_id, operation_row)
        query = rest.get("query", {})
        static_query = {str(key): value for key, value in query.items()} if isinstance(query, Mapping) else {}
        for field in _frontend_api_input_rows(operation_row):
            query_name = _frontend_api_mapped_input_name(field)
            if query_name in path_names or query_name in body_names:
                continue
            cell_rows.append(_frontend_api_rest_dynamic_query_field_cells(operation_row, rest, field, query_name, static_query))
    return _frontend_api_table_rows(cell_rows)


def _frontend_api_rest_dynamic_query_field_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "REST Dynamic Query Field Index / REST Dynamic Query Field 索引",
        (
            "Query Parameter",
            "Operation ID",
            "Method",
            "Path",
            "Source Field",
            "Type",
            "Required",
            "Target",
            "Static Default",
        ),
        _frontend_api_rest_dynamic_query_field_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_rest_dynamic_query_field_cells(
    operation: dict[str, object],
    rest: Mapping[str, object],
    field: Mapping[str, object],
    query_name: str,
    static_query: Mapping[str, object],
) -> list[str]:
    return [
        *_frontend_api_rest_input_route_cells(operation, rest, field, query_name),
        _code_cell(_rest_index_value(static_query[query_name])) if query_name in static_query else _markdown_cell(""),
    ]


def _frontend_api_rest_path_parameter_index_rows(contract: object) -> list[str]:
    return _frontend_api_rest_routed_input_index_rows(
        contract,
        lambda _operation_id, _operation, rest: _rest_path_parameter_names(str(rest.get("path", ""))),
    )


def _frontend_api_rest_path_parameter_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "REST Path Parameter Index / REST Path Parameter 索引",
        (
            "Path Parameter",
            "Operation ID",
            "Method",
            "Path",
            "Source Field",
            "Type",
            "Required",
            "Target",
        ),
        _frontend_api_rest_path_parameter_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_rest_body_field_index_rows(contract: object) -> list[str]:
    return _frontend_api_rest_routed_input_index_rows(
        contract,
        lambda operation_id, operation, _rest: _rest_body_inputs(operation_id, operation),
    )


def _frontend_api_rest_body_field_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "REST Body Field Index / REST Body Field 索引",
        (
            "Body Field",
            "Operation ID",
            "Method",
            "Path",
            "Source Field",
            "Type",
            "Required",
            "Target",
        ),
        _frontend_api_rest_body_field_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_rest_routed_input_index_rows(
    contract: object,
    routed_names_for_operation: Callable[[str, dict[str, object], Mapping[str, object]], Sequence[str] | set[str]],
) -> list[str]:
    cell_rows: list[list[str]] = []
    for operation_row, rest in _frontend_api_contract_rest_operation_rows(contract):
        operation_id = _frontend_api_operation_id(operation_row)
        routed_names = routed_names_for_operation(operation_id, operation_row, rest)
        if not routed_names:
            continue
        for field in _frontend_api_input_rows(operation_row):
            routed_name = _frontend_api_mapped_input_name(field)
            if routed_name not in routed_names:
                continue
            cell_rows.append(_frontend_api_rest_input_route_cells(operation_row, rest, field, routed_name))
    return _frontend_api_table_rows(cell_rows)


def _frontend_api_rest_input_route_cells(
    operation: dict[str, object],
    rest: Mapping[str, object],
    field: Mapping[str, object],
    route_name: object,
) -> list[str]:
    return [
        _code_cell(route_name),
        _code_cell(_frontend_api_operation_id(operation)),
        _code_cell(rest.get("method", "")),
        _code_cell(rest.get("path", "")),
        _code_cell(_frontend_api_input_name(field)),
        _code_cell(field.get("type", "")),
        _frontend_api_required_cell(field),
        _frontend_api_input_target_cell(operation, field),
    ]


def _frontend_api_binding_surface_index_rows(contract: object, surface: str) -> list[str]:
    binding_index = _frontend_api_contract_index_mapping(contract, "binding")
    if binding_index is None:
        return []
    return _frontend_api_table_rows(
        _frontend_api_operation_id_detail_cells([_code_cell(key)], operation_ids)
        for key, operation_ids in _frontend_api_binding_surface_entries(binding_index, surface)
    )


def _frontend_api_binding_surface_entries(binding_index: Mapping[str, object], surface: str) -> list[tuple[str, object]]:
    surface_index = binding_index.get(surface, {})
    if not isinstance(surface_index, Mapping):
        return []
    return [(key, surface_index.get(key, [])) for key in sorted(str(value) for value in surface_index)]


def _frontend_api_group_binding_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_operation_summary_rows(contract, _frontend_api_binding_summary_cells)


def _frontend_api_group_binding_summary_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Binding Summary Index / Group Binding Summary 索引",
        (
            "Group",
            "Operations",
            "Bound Operations",
            "SDK Calls",
            "CLI Commands",
            "REST Routes",
            "MCP Tools",
            "LSP Methods",
            "Unbound Operations",
        ),
        _frontend_api_group_binding_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_binding_summary_cells(owner_id: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    surface_keys: dict[str, set[str]] = {surface: set() for surface in FRONTEND_API_SURFACE_COVERAGE_COLUMNS}
    unbound_operations: set[str] = set()
    bound_count = 0
    for operation in operations:
        operation_id = _frontend_api_operation_id(operation)
        bindings = _frontend_api_operation_bindings(operation)
        if not bindings:
            unbound_operations.add(operation_id)
            continue
        bound_count += 1
        for surface in FRONTEND_API_SURFACE_COVERAGE_COLUMNS:
            key = _binding_index_key(surface, bindings.get(surface))
            if key:
                surface_keys[surface].add(key)
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        _markdown_cell(bound_count),
        _frontend_api_sorted_code_list_cell(surface_keys["sdk"]),
        _frontend_api_sorted_code_list_cell(surface_keys["cli"]),
        _frontend_api_sorted_code_list_cell(surface_keys["rest"]),
        _frontend_api_sorted_code_list_cell(surface_keys["mcp"]),
        _frontend_api_sorted_code_list_cell(surface_keys["lsp"]),
        _frontend_api_sorted_code_list_cell(unbound_operations),
    ]


def _frontend_api_sdk_call_index_rows(contract: object) -> list[str]:
    return _frontend_api_binding_surface_index_rows(contract, "sdk")


def _frontend_api_sdk_call_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "SDK Call Index / SDK Call 索引",
        ("SDK Call", "Operations", "Operation IDs"),
        _frontend_api_sdk_call_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_sdk_call_input_index_rows(contract: object) -> list[str]:
    return _frontend_api_binding_input_index_rows(contract, "sdk", "call")


def _frontend_api_sdk_call_input_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "SDK Call Input Index / SDK Call Input 索引",
        (
            "SDK Call",
            "Operation ID",
            "Field",
            "Type",
            "Required",
            "Default",
            "Target",
            "Maps To",
        ),
        _frontend_api_sdk_call_input_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_mcp_tool_index_rows(contract: object) -> list[str]:
    return _frontend_api_binding_surface_index_rows(contract, "mcp")


def _frontend_api_mcp_tool_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "MCP Tool Index / MCP Tool 索引",
        ("Tool", "Operations", "Operation IDs"),
        _frontend_api_mcp_tool_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_mcp_tool_input_index_rows(contract: object) -> list[str]:
    return _frontend_api_binding_input_index_rows(contract, "mcp", "tool")


def _frontend_api_mcp_tool_input_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "MCP Tool Input Index / MCP Tool Input 索引",
        (
            "Tool",
            "Operation ID",
            "Field",
            "Type",
            "Required",
            "Default",
            "Target",
            "Maps To",
        ),
        _frontend_api_mcp_tool_input_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_cli_command_input_index_rows(contract: object) -> list[str]:
    return _frontend_api_binding_input_index_rows(contract, "cli", "command")


def _frontend_api_cli_command_input_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "CLI Command Input Index / CLI Command Input 索引",
        (
            "Command",
            "Operation ID",
            "Field",
            "Type",
            "Required",
            "Default",
            "Target",
            "Maps To",
        ),
        _frontend_api_cli_command_input_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_binding_input_cells(
    binding: Mapping[str, object],
    key: str,
    operation: dict[str, object],
    field: Mapping[str, object],
) -> list[str]:
    return [
        _code_cell(binding.get(key, "")),
        _code_cell(_frontend_api_operation_id(operation)),
        _code_cell(_frontend_api_input_name(field)),
        _code_cell(field.get("type", "")),
        _frontend_api_required_cell(field),
        _frontend_api_default_value_cell(field),
        _frontend_api_input_target_cell(operation, field),
        _frontend_api_input_alias_cell(field),
    ]


def _frontend_api_binding_input_index_rows(contract: object, surface: str, key: str) -> list[str]:
    return _frontend_api_table_rows(
        _frontend_api_binding_input_cells(binding, key, operation_row, field)
        for operation_row, binding, field in _frontend_api_binding_input_rows(contract, surface)
    )


def _frontend_api_binding_input_rows(
    contract: object,
    surface: str,
) -> list[_FrontendApiBindingInputRecord]:
    rows: list[_FrontendApiBindingInputRecord] = []
    for operation_row in _frontend_api_operation_rows(contract):
        bindings = _frontend_api_operation_bindings(operation_row)
        binding = bindings.get(surface)
        if not isinstance(binding, Mapping):
            continue
        for field in _frontend_api_input_rows(operation_row):
            rows.append((operation_row, binding, field))
    return rows


def _frontend_api_cli_command_index_rows(contract: object) -> list[str]:
    return _frontend_api_binding_surface_index_rows(contract, "cli")


def _frontend_api_cli_command_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "CLI Command Index / CLI Command 索引",
        ("Command", "Operations", "Operation IDs"),
        _frontend_api_cli_command_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_lsp_method_index_rows(contract: object) -> list[str]:
    return _frontend_api_binding_surface_index_rows(contract, "lsp")


def _frontend_api_lsp_method_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "LSP Method Index / LSP Method 索引",
        ("Method", "Operations", "Operation IDs"),
        _frontend_api_lsp_method_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_lsp_method_input_index_rows(contract: object) -> list[str]:
    return _frontend_api_binding_input_index_rows(contract, "lsp", "method")


def _frontend_api_lsp_method_input_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "LSP Method Input Index / LSP Method Input 索引",
        (
            "Method",
            "Operation ID",
            "Field",
            "Type",
            "Required",
            "Default",
            "Target",
            "Maps To",
        ),
        _frontend_api_lsp_method_input_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_binding_index_rows(contract: object) -> list[str]:
    binding_index = _frontend_api_contract_index_mapping(contract, "binding")
    if binding_index is None:
        return []
    return _frontend_api_table_rows(
        _frontend_api_binding_index_cells(surface, key, operation_ids)
        for surface in FRONTEND_API_BINDING_SURFACES
        for key, operation_ids in _frontend_api_binding_surface_entries(binding_index, surface)
    )


def _frontend_api_binding_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Binding Index / Binding 索引",
        ("Surface", "Binding Key", "Operations", "Operation IDs"),
        _frontend_api_binding_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_binding_index_cells(surface: object, key: object, operation_ids: object) -> list[str]:
    return _frontend_api_operation_id_detail_cells([_code_cell(surface), _code_cell(key)], operation_ids)


def _frontend_api_payload_index_rows(contract: object) -> list[str]:
    payload_index = _frontend_api_contract_index_mapping(contract, "payload")
    if payload_index is None:
        return []
    return _frontend_api_operation_id_index_rows(payload_index, _frontend_api_payload_index_keys(payload_index))


def _frontend_api_payload_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Payload Index / Payload 索引",
        ("Payload", "Operations", "Operation IDs"),
        _frontend_api_payload_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_payload_index_keys(payload_index: Mapping[str, object]) -> list[str]:
    payload_keys = [str(payload) for payload in payload_index if str(payload) != "untyped"]
    if "untyped" in payload_index:
        payload_keys.append("untyped")
    return payload_keys


def _frontend_api_workspace_section_index_rows(contract: object) -> list[str]:
    section_index = _frontend_api_contract_index_mapping(contract, "workspace_section")
    if section_index is None:
        return []
    return _frontend_api_table_rows(
        _frontend_api_workspace_section_index_cells(section, str(section["id"]), section_index.get(str(section["id"]), []))
        for section in _frontend_api_workspace_section_rows(contract)
    )


def _frontend_api_workspace_section_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Index / Workspace Section 索引",
        ("Workspace Section", "Operations", "Default Operation", "Operation IDs"),
        _frontend_api_workspace_section_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_workspace_section_index_cells(section: Mapping[str, object], section_id: str, operation_ids: object) -> list[str]:
    operation_id_cells = _frontend_api_operation_id_cells(operation_ids)
    return [
        _code_cell(section_id),
        operation_id_cells[0],
        _code_cell(section.get("default_operation_id", "")),
        operation_id_cells[1],
    ]


def _frontend_api_contract_index_mapping(contract: object, name: str) -> Mapping[str, object] | None:
    index = _frontend_api_contract_index(contract)
    if index is None:
        return None
    value = index.get(name, {})
    return value if isinstance(value, Mapping) else None


def _frontend_api_contract_index(contract: object) -> Mapping[str, object] | None:
    if not isinstance(contract, Mapping):
        return None
    index = contract.get("index", {})
    return index if isinstance(index, Mapping) else None


def _frontend_api_operation_rows(contract: object) -> list[dict[str, object]]:
    if not isinstance(contract, Mapping):
        return []
    return _frontend_api_dict_rows(contract.get("operations", []))


def _frontend_api_operation_input_rows(
    operations: Sequence[Mapping[str, object]],
) -> list[_FrontendApiInputRecord]:
    rows: list[_FrontendApiInputRecord] = []
    for operation in operations:
        operation_row = dict(operation)
        rows.extend((operation_row, field) for field in _frontend_api_input_rows(operation_row))
    return rows


def _frontend_api_input_rows(
    operation: Mapping[str, object],
) -> list[Mapping[str, object]]:
    return _frontend_api_mapping_rows(operation.get("inputs", []))


def _frontend_api_operation_bindings(
    operation: Mapping[str, object],
) -> Mapping[str, object]:
    bindings = operation.get("bindings", {})
    return bindings if isinstance(bindings, Mapping) else {}


def _frontend_api_contract_input_rows(
    contract: object,
) -> list[_FrontendApiInputRecord]:
    return _frontend_api_operation_input_rows(_frontend_api_operation_rows(contract))


def _frontend_api_rest_operation_rows(
    operations: Sequence[Mapping[str, object]],
) -> list[_FrontendApiRestOperationRecord]:
    rows: list[_FrontendApiRestOperationRecord] = []
    for operation in operations:
        operation_row = dict(operation)
        bindings = _frontend_api_operation_bindings(operation_row)
        rest = bindings.get("rest")
        if isinstance(rest, Mapping):
            rows.append((operation_row, rest))
    return rows


def _frontend_api_contract_rest_operation_rows(
    contract: object,
) -> list[_FrontendApiRestOperationRecord]:
    return _frontend_api_rest_operation_rows(_frontend_api_operation_rows(contract))


def _frontend_api_group_operation_rows(
    contract: object,
) -> list[_FrontendApiOwnerOperationRecord]:
    operation_rows = _frontend_api_operation_rows(contract)
    rows: list[_FrontendApiOwnerOperationRecord] = []
    for group_row in _frontend_api_group_rows(contract):
        group_id = _frontend_api_row_id(group_row)
        group_operations = [operation for operation in operation_rows if _frontend_api_operation_group_id(operation) == group_id]
        rows.append((group_row, group_operations))
    return rows


def _frontend_api_workspace_section_action_rows(
    contract: object,
) -> list[_FrontendApiOwnerActionRecord]:
    operation_rows = _frontend_api_operation_rows(contract)
    operation_by_id = _frontend_api_operation_by_id(operation_rows)
    rows: list[_FrontendApiOwnerActionRecord] = []
    for section_row in _frontend_api_workspace_section_rows(contract):
        section_actions = _frontend_api_dict_rows(section_row.get("actions", []))
        section_operations: list[dict[str, object]] = []
        for action in section_actions:
            operation = operation_by_id.get(_frontend_api_action_operation_id(action))
            if operation is not None:
                section_operations.append(operation)
        rows.append((section_row, section_operations, section_actions))
    return rows


def _frontend_api_workspace_section_operation_rows(
    contract: object,
) -> list[_FrontendApiOwnerOperationRecord]:
    return [(section, section_operations) for section, section_operations, _section_actions in _frontend_api_workspace_section_action_rows(contract)]


def _frontend_api_owner_operation_summary_rows(
    owner_rows: Sequence[_FrontendApiOwnerOperationRecord],
    cells_for_owner: _FrontendApiOwnerSummaryCellBuilder,
) -> list[str]:
    return _frontend_api_table_rows(cells_for_owner(_frontend_api_row_id(owner), owner_operations) for owner, owner_operations in owner_rows)


def _frontend_api_workspace_section_operation_summary_rows(
    contract: object,
    cells_for_owner: _FrontendApiOwnerSummaryCellBuilder,
) -> list[str]:
    return _frontend_api_owner_operation_summary_rows(
        _frontend_api_workspace_section_operation_rows(contract),
        cells_for_owner,
    )


def _frontend_api_group_operation_summary_rows(
    contract: object,
    cells_for_owner: _FrontendApiOwnerSummaryCellBuilder,
) -> list[str]:
    return _frontend_api_owner_operation_summary_rows(
        _frontend_api_group_operation_rows(contract),
        cells_for_owner,
    )


def _frontend_api_owner_operation_detail_rows(
    owner_rows: Sequence[_FrontendApiOwnerOperationRecord],
    cells_for_owner: _FrontendApiOwnerDetailCellBuilder,
) -> list[str]:
    return _frontend_api_table_rows(cells_for_owner(owner, owner_operations) for owner, owner_operations in owner_rows)


def _frontend_api_workspace_section_operation_detail_rows(
    contract: object,
    cells_for_owner: _FrontendApiOwnerDetailCellBuilder,
) -> list[str]:
    return _frontend_api_owner_operation_detail_rows(
        _frontend_api_workspace_section_operation_rows(contract),
        cells_for_owner,
    )


def _frontend_api_group_operation_detail_rows(
    contract: object,
    cells_for_owner: _FrontendApiOwnerDetailCellBuilder,
) -> list[str]:
    return _frontend_api_owner_operation_detail_rows(
        _frontend_api_group_operation_rows(contract),
        cells_for_owner,
    )


def _frontend_api_owner_action_summary_rows(
    owner_rows: Sequence[_FrontendApiOwnerActionRecord],
    cells_for_owner: _FrontendApiOwnerActionCellBuilder,
) -> list[str]:
    return _frontend_api_table_rows(
        cells_for_owner(_frontend_api_row_id(owner), owner_operations, owner_actions) for owner, owner_operations, owner_actions in owner_rows
    )


def _frontend_api_workspace_section_action_summary_rows(
    contract: object,
    cells_for_owner: _FrontendApiOwnerActionCellBuilder,
) -> list[str]:
    return _frontend_api_owner_action_summary_rows(
        _frontend_api_workspace_section_action_rows(contract),
        cells_for_owner,
    )


def _frontend_api_group_action_summary_rows(
    contract: object,
    cells_for_owner: _FrontendApiOwnerActionCellBuilder,
) -> list[str]:
    return _frontend_api_owner_action_summary_rows(
        _frontend_api_group_action_rows(contract),
        cells_for_owner,
    )


def _frontend_api_owner_operation_count_cells(owner_id: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    return [
        _code_cell(owner_id),
        _markdown_cell(len(operations)),
    ]


def _frontend_api_action_execution(
    action: Mapping[str, object],
) -> Mapping[str, object] | None:
    execution = action.get("execution", {})
    return execution if isinstance(execution, Mapping) else None


def _frontend_api_required_confirmation(value: object) -> Mapping[str, object] | None:
    return value if isinstance(value, Mapping) and bool(value.get("required", False)) else None


def _frontend_api_action_confirmation(
    action: Mapping[str, object],
) -> Mapping[str, object] | None:
    execution = _frontend_api_action_execution(action)
    if execution is None:
        return None
    return _frontend_api_required_confirmation(execution.get("confirmation", {}))


def _frontend_api_mode_status_cells(owner_id: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    counts = {
        "read": 0,
        "write": 0,
        "implemented": 0,
        "planned": 0,
        "frontend-local": 0,
    }
    for operation in operations:
        counts[_frontend_api_operation_mode(operation)] += 1
        status = _frontend_api_operation_status(operation)
        if status in counts:
            counts[status] += 1
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        _markdown_cell(counts["read"]),
        _markdown_cell(counts["write"]),
        _markdown_cell(counts["implemented"]),
        _markdown_cell(counts["planned"]),
        _markdown_cell(counts["frontend-local"]),
    ]


def _frontend_api_workspace_section_mode_status_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Mode Status Index / Workspace Section Mode Status 索引",
        (
            "Workspace Section",
            "Actions",
            "Read",
            "Write",
            "Implemented",
            "Planned",
            "Frontend Local",
        ),
        _frontend_api_workspace_section_mode_status_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_group_mode_status_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Mode Status Index / Group Mode Status 索引",
        (
            "Group",
            "Operations",
            "Read",
            "Write",
            "Implemented",
            "Planned",
            "Frontend Local",
        ),
        _frontend_api_group_mode_status_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_workspace_section_mode_status_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_operation_summary_rows(contract, _frontend_api_mode_status_cells)


def _frontend_api_group_mode_status_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_operation_summary_rows(contract, _frontend_api_mode_status_cells)


def _frontend_api_payload_coverage_cells(owner_id: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    payload_counts: _FrontendApiCountMap = {}
    for operation in operations:
        payload = _frontend_api_operation_payload(operation)
        _frontend_api_increment_count(payload_counts, payload)
    payloads = _frontend_api_count_list(payload_counts, exclude=("untyped",))
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        _markdown_cell(len(payloads)),
        _markdown_cell(payload_counts.get("untyped", 0)),
        _frontend_api_code_list_cell(payloads),
    ]


def _frontend_api_workspace_section_payload_coverage_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Payload Coverage Index / Workspace Section Payload Coverage 索引",
        ("Workspace Section", "Actions", "Payload Schemas", "Untyped", "Payloads"),
        _frontend_api_workspace_section_payload_coverage_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_group_payload_coverage_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Payload Coverage Index / Group Payload Coverage 索引",
        ("Group", "Operations", "Payload Schemas", "Untyped", "Payloads"),
        _frontend_api_group_payload_coverage_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_workspace_section_payload_coverage_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_operation_summary_rows(contract, _frontend_api_payload_coverage_cells)


def _frontend_api_group_payload_coverage_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_operation_summary_rows(contract, _frontend_api_payload_coverage_cells)


def _frontend_api_workspace_section_surface_coverage_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_action_summary_rows(contract, _frontend_api_workspace_section_surface_coverage_cells)


def _frontend_api_workspace_section_surface_coverage_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Surface Coverage Index / Workspace Section Surface Coverage 索引",
        (
            "Workspace Section",
            "Actions",
            "SDK",
            "CLI",
            "REST",
            "MCP",
            "LSP",
            "Frontend Local",
            "Unbound",
            "Default Surfaces",
        ),
        _frontend_api_workspace_section_surface_coverage_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_workspace_section_surface_coverage_cells(
    owner_id: object,
    _operations: Sequence[Mapping[str, object]],
    actions: Sequence[Mapping[str, object]],
) -> list[str]:
    surface_counts: _FrontendApiCountMap = {surface: 0 for surface in FRONTEND_API_SURFACE_COVERAGE_COLUMNS}
    default_counts: _FrontendApiCountMap = {}
    frontend_local_count = 0
    unbound_count = 0
    action_count = 0
    for action in actions:
        action_delta, frontend_local_delta, unbound_delta = _frontend_api_workspace_section_surface_action_counts(
            action,
            surface_counts,
            default_counts,
        )
        action_count += action_delta
        frontend_local_count += frontend_local_delta
        unbound_count += unbound_delta
    return [
        _code_cell(owner_id),
        _markdown_cell(action_count),
        _markdown_cell(surface_counts["sdk"]),
        _markdown_cell(surface_counts["cli"]),
        _markdown_cell(surface_counts["rest"]),
        _markdown_cell(surface_counts["mcp"]),
        _markdown_cell(surface_counts["lsp"]),
        _markdown_cell(frontend_local_count),
        _markdown_cell(unbound_count),
        _frontend_api_count_list_cell(default_counts),
    ]


def _frontend_api_workspace_section_surface_action_counts(
    action: Mapping[str, object],
    surface_counts: _FrontendApiCountMap,
    default_counts: _FrontendApiCountMap,
) -> _FrontendApiSummaryDeltaTriple:
    execution = _frontend_api_action_execution(action)
    if execution is None:
        return 0, 0, 0

    available_surfaces = _frontend_api_sequence_items(execution.get("available_surfaces", []))
    for surface in FRONTEND_API_SURFACE_COVERAGE_COLUMNS:
        surface_counts[surface] += int(surface in available_surfaces)
    default_surface = str(execution.get("default_surface", ""))
    if default_surface:
        _frontend_api_increment_count(default_counts, default_surface)
    frontend_local_count = int(default_surface == "frontend-local" or execution.get("kind") == "frontend-local")
    unbound_count = int(not available_surfaces and default_surface != "frontend-local")
    return 1, frontend_local_count, unbound_count


def _frontend_api_workspace_section_binding_summary_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_operation_summary_rows(contract, _frontend_api_binding_summary_cells)


def _frontend_api_workspace_section_binding_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Binding Summary Index / Workspace Section Binding Summary 索引",
        (
            "Workspace Section",
            "Actions",
            "Bound Actions",
            "SDK Calls",
            "CLI Commands",
            "REST Routes",
            "MCP Tools",
            "LSP Methods",
            "Unbound Actions",
        ),
        _frontend_api_workspace_section_binding_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_workspace_section_form_summary_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_operation_detail_rows(contract, _frontend_api_form_summary_cells)


def _frontend_api_workspace_section_form_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Form Summary Index / Workspace Section Form Summary 索引",
        (
            "Workspace Section",
            "Title",
            "Actions",
            "Inputs",
            "Required",
            "Defaults",
            "Aliases",
            "Option Sources",
            "Constraints",
            "Controls",
        ),
        _frontend_api_workspace_section_form_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_control_summary_cells(owner_id: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    input_count = 0
    dynamic_count = 0
    choice_count = 0
    control_counts: _FrontendApiCountMap = {}
    dynamic_fields: set[str] = set()
    choice_fields: set[str] = set()
    textarea_fields: set[str] = set()
    for operation, field in _frontend_api_operation_input_rows(operations):
        input_delta, dynamic_delta, choice_delta = _frontend_api_control_summary_input_counts(
            operation,
            field,
            control_counts,
            dynamic_fields,
            choice_fields,
            textarea_fields,
        )
        input_count += input_delta
        dynamic_count += dynamic_delta
        choice_count += choice_delta
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        _markdown_cell(input_count),
        _markdown_cell(len(control_counts)),
        _markdown_cell(dynamic_count),
        _markdown_cell(choice_count),
        _frontend_api_count_list_cell(control_counts),
        _frontend_api_sorted_code_list_cell(dynamic_fields),
        _frontend_api_sorted_code_list_cell(choice_fields),
        _frontend_api_sorted_code_list_cell(textarea_fields),
    ]


def _frontend_api_control_summary_input_counts(
    operation: dict[str, object],
    field: Mapping[str, object],
    control_counts: _FrontendApiCountMap,
    dynamic_fields: set[str],
    choice_fields: set[str],
    textarea_fields: set[str],
) -> _FrontendApiSummaryDeltaTriple:
    form_field = _frontend_api_form_field(operation, dict(field))
    control = str(form_field.get("control", ""))
    name = str(form_field.get("name", ""))
    _frontend_api_increment_count(control_counts, control)
    dynamic_count = int(isinstance(form_field.get("option_source"), Mapping))
    if dynamic_count:
        dynamic_fields.add(name)
    choice_count = int(bool(form_field.get("choices")))
    if choice_count:
        choice_fields.add(name)
    if control == "textarea":
        textarea_fields.add(name)
    return 1, dynamic_count, choice_count


def _frontend_api_workspace_section_control_summary_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_operation_summary_rows(contract, _frontend_api_control_summary_cells)


def _frontend_api_workspace_section_control_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Control Summary Index / Workspace Section Control Summary 索引",
        (
            "Workspace Section",
            "Actions",
            "Inputs",
            "Control Kinds",
            "Dynamic Controls",
            "Choice Controls",
            "Controls",
            "Dynamic Fields",
            "Choice Fields",
            "Textarea Fields",
        ),
        _frontend_api_workspace_section_control_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_group_control_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_operation_summary_rows(contract, _frontend_api_control_summary_cells)


def _frontend_api_group_control_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Control Summary Index / Group Control Summary 索引",
        (
            "Group",
            "Operations",
            "Inputs",
            "Control Kinds",
            "Dynamic Controls",
            "Choice Controls",
            "Controls",
            "Dynamic Fields",
            "Choice Fields",
            "Textarea Fields",
        ),
        _frontend_api_group_control_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_workspace_section_option_source_summary_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_operation_summary_rows(contract, _frontend_api_option_source_summary_cells)


def _frontend_api_workspace_section_option_source_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Option Source Summary Index / Workspace Section Option Source Summary 索引",
        (
            "Workspace Section",
            "Actions",
            "Option Fields",
            "Consumer Actions",
            "Providers",
            "Provider Operations",
            "Values Paths",
            "Requires",
            "Forward",
            "Filters",
        ),
        _frontend_api_workspace_section_option_source_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_group_option_source_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_operation_summary_rows(contract, _frontend_api_option_source_summary_cells)


def _frontend_api_group_option_source_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Option Source Summary Index / Group Option Source Summary 索引",
        (
            "Group",
            "Operations",
            "Option Fields",
            "Consumers",
            "Providers",
            "Provider Operations",
            "Values Paths",
            "Requires",
            "Forward",
            "Filters",
        ),
        _frontend_api_group_option_source_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_option_source_summary_cells(owner_id: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    option_field_count = 0
    consumer_actions: set[str] = set()
    providers: set[str] = set()
    values_paths: set[str] = set()
    requires: set[str] = set()
    forward: set[str] = set()
    filters: set[str] = set()
    for operation, field in _frontend_api_operation_input_rows(operations):
        option_field_count += _frontend_api_option_source_summary_input_count(
            operation,
            field,
            consumer_actions,
            providers,
            values_paths,
            requires,
            forward,
            filters,
        )
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        _markdown_cell(option_field_count),
        _markdown_cell(len(consumer_actions)),
        _markdown_cell(len(providers)),
        _frontend_api_sorted_code_list_cell(providers),
        _frontend_api_sorted_code_list_cell(values_paths),
        _frontend_api_sorted_code_list_cell(requires),
        _frontend_api_sorted_code_list_cell(forward),
        _frontend_api_sorted_code_list_cell(filters),
    ]


def _frontend_api_option_source_summary_input_count(
    operation: Mapping[str, object],
    field: Mapping[str, object],
    consumer_actions: set[str],
    providers: set[str],
    values_paths: set[str],
    requires: set[str],
    forward: set[str],
    filters: set[str],
) -> int:
    option_source = _frontend_api_field_option_source(field)
    if option_source is None:
        return 0

    consumer_actions.add(_frontend_api_operation_id(operation))
    providers.add(_frontend_api_option_source_operation_id(option_source))
    values_paths.add(_frontend_api_option_source_values_path(option_source))
    requires.update(str(value) for value in _frontend_api_option_source_requires(option_source))
    forward.update(str(value) for value in _frontend_api_option_source_forward(option_source))
    filters.update(_frontend_api_option_source_filter_parts(_frontend_api_option_source_filters(option_source)))
    return 1


def _frontend_api_input_target_summary_cells(owner_id: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    input_count = 0
    required_count = 0
    target_counts: _FrontendApiCountMap = {}
    fields_by_target: dict[str, set[str]] = {
        "parameters": set(),
        "project": set(),
        "selectors": set(),
        "projections": set(),
    }
    aliases: set[str] = set()
    for operation, field in _frontend_api_operation_input_rows(operations):
        input_delta, required_delta = _frontend_api_input_target_summary_input_counts(
            operation,
            field,
            target_counts,
            fields_by_target,
            aliases,
        )
        input_count += input_delta
        required_count += required_delta
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        _markdown_cell(input_count),
        _markdown_cell(required_count),
        _frontend_api_count_list_cell(target_counts),
        _frontend_api_sorted_code_list_cell(fields_by_target["parameters"]),
        _frontend_api_sorted_code_list_cell(fields_by_target["project"]),
        _frontend_api_sorted_code_list_cell(fields_by_target["selectors"]),
        _frontend_api_sorted_code_list_cell(fields_by_target["projections"]),
        _frontend_api_sorted_code_list_cell(aliases),
    ]


def _frontend_api_input_target_summary_input_counts(
    operation: dict[str, object],
    field: Mapping[str, object],
    target_counts: _FrontendApiCountMap,
    fields_by_target: dict[str, set[str]],
    aliases: set[str],
) -> _FrontendApiSummaryDeltaPair:
    name = _frontend_api_input_name(field)
    target = _frontend_api_input_target(operation, field)
    _frontend_api_increment_count(target_counts, target)
    fields_by_target.setdefault(target, set()).add(name)
    if "maps_to" in field:
        aliases.add(_frontend_api_input_alias_entry(name, field))
    return 1, int(bool(field.get("required", False)))


def _frontend_api_workspace_section_input_target_summary_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_operation_summary_rows(contract, _frontend_api_input_target_summary_cells)


def _frontend_api_workspace_section_input_target_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Input Target Summary Index / Workspace Section Input Target Summary 索引",
        (
            "Workspace Section",
            "Actions",
            "Inputs",
            "Required",
            "Targets",
            "Parameter Fields",
            "Project Fields",
            "Selector Fields",
            "Projection Fields",
            "Aliases",
        ),
        _frontend_api_workspace_section_input_target_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_group_input_target_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_operation_summary_rows(contract, _frontend_api_input_target_summary_cells)


def _frontend_api_group_input_target_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Input Target Summary Index / Group Input Target Summary 索引",
        (
            "Group",
            "Operations",
            "Inputs",
            "Required",
            "Targets",
            "Parameter Fields",
            "Project Fields",
            "Selector Fields",
            "Projection Fields",
            "Aliases",
        ),
        _frontend_api_group_input_target_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_validation_summary_cells(owner_id: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    input_count = 0
    constraint_count = 0
    choice_count = 0
    bound_count = 0
    constrained_operations: set[str] = set()
    choice_fields: set[str] = set()
    bound_fields: set[str] = set()
    for operation, field in _frontend_api_operation_input_rows(operations):
        input_delta, constraint_delta, choice_delta, bound_delta = _frontend_api_validation_summary_input_counts(
            operation,
            field,
            constrained_operations,
            choice_fields,
            bound_fields,
        )
        input_count += input_delta
        constraint_count += constraint_delta
        choice_count += choice_delta
        bound_count += bound_delta
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        _markdown_cell(input_count),
        _markdown_cell(constraint_count),
        _markdown_cell(choice_count),
        _markdown_cell(bound_count),
        _frontend_api_sorted_code_list_cell(constrained_operations),
        _frontend_api_sorted_code_list_cell(choice_fields),
        _frontend_api_sorted_code_list_cell(bound_fields),
    ]


def _frontend_api_validation_summary_input_counts(
    operation: Mapping[str, object],
    field: Mapping[str, object],
    constrained_operations: set[str],
    choice_fields: set[str],
    bound_fields: set[str],
) -> _FrontendApiSummaryDeltaQuad:
    has_choices = "choices" in field
    has_bound = "minimum" in field or "maximum" in field
    if not has_choices and not has_bound:
        return 1, 0, 0, 0

    name = _frontend_api_input_name(field)
    constrained_operations.add(_frontend_api_operation_id(operation))
    if has_choices:
        choice_fields.add(name)
    if has_bound:
        bound_fields.add(name)
    return 1, 1, int(has_choices), int(has_bound)


def _frontend_api_workspace_section_validation_summary_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_operation_summary_rows(contract, _frontend_api_validation_summary_cells)


def _frontend_api_workspace_section_validation_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Validation Summary Index / Workspace Section Validation Summary 索引",
        (
            "Workspace Section",
            "Actions",
            "Inputs",
            "Constraints",
            "Choices",
            "Bounds",
            "Operations",
            "Choice Fields",
            "Bound Fields",
        ),
        _frontend_api_workspace_section_validation_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_group_validation_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_operation_summary_rows(contract, _frontend_api_validation_summary_cells)


def _frontend_api_group_validation_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Validation Summary Index / Group Validation Summary 索引",
        (
            "Group",
            "Operations",
            "Inputs",
            "Constraints",
            "Choices",
            "Bounds",
            "Operations",
            "Choice Fields",
            "Bound Fields",
        ),
        _frontend_api_group_validation_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_default_summary_cells(owner_id: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    input_count = 0
    default_count = 0
    required_default_count = 0
    default_operations: set[str] = set()
    default_fields: set[str] = set()
    default_values: set[str] = set()
    for operation, field in _frontend_api_operation_input_rows(operations):
        input_delta, default_delta, required_default_delta = _frontend_api_default_summary_input_counts(
            operation,
            field,
            default_operations,
            default_fields,
            default_values,
        )
        input_count += input_delta
        default_count += default_delta
        required_default_count += required_default_delta
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        _markdown_cell(input_count),
        _markdown_cell(default_count),
        _markdown_cell(required_default_count),
        _frontend_api_sorted_code_list_cell(default_operations),
        _frontend_api_sorted_code_list_cell(default_fields),
        _frontend_api_sorted_code_list_cell(default_values),
    ]


def _frontend_api_default_summary_input_counts(
    operation: Mapping[str, object],
    field: Mapping[str, object],
    default_operations: set[str],
    default_fields: set[str],
    default_values: set[str],
) -> _FrontendApiSummaryDeltaTriple:
    if "default" not in field:
        return 1, 0, 0

    name = _frontend_api_input_name(field)
    default_operations.add(_frontend_api_operation_id(operation))
    default_fields.add(name)
    default_values.add(f"{name}={dumps_json(field.get('default'))}")
    return 1, 1, int(bool(field.get("required", False)))


def _frontend_api_workspace_section_default_summary_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_operation_summary_rows(contract, _frontend_api_default_summary_cells)


def _frontend_api_workspace_section_default_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Default Summary Index / Workspace Section Default Summary 索引",
        (
            "Workspace Section",
            "Actions",
            "Inputs",
            "Defaults",
            "Required Defaults",
            "Operations",
            "Fields",
            "Defaults",
        ),
        _frontend_api_workspace_section_default_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_group_default_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_operation_summary_rows(contract, _frontend_api_default_summary_cells)


def _frontend_api_group_default_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Default Summary Index / Group Default Summary 索引",
        (
            "Group",
            "Operations",
            "Inputs",
            "Defaults",
            "Required Defaults",
            "Operations",
            "Fields",
            "Defaults",
        ),
        _frontend_api_group_default_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_required_summary_cells(owner_id: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    input_count = 0
    required_count = 0
    required_operations: set[str] = set()
    required_fields: set[str] = set()
    target_counts: _FrontendApiCountMap = {}
    providers: set[str] = set()
    aliases: set[str] = set()
    for operation, field in _frontend_api_operation_input_rows(operations):
        input_delta, required_delta = _frontend_api_required_summary_input_counts(
            operation,
            field,
            required_operations,
            required_fields,
            target_counts,
            providers,
            aliases,
        )
        input_count += input_delta
        required_count += required_delta
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        _markdown_cell(input_count),
        _markdown_cell(required_count),
        _frontend_api_sorted_code_list_cell(required_operations),
        _frontend_api_sorted_code_list_cell(required_fields),
        _frontend_api_count_list_cell(target_counts),
        _frontend_api_sorted_code_list_cell(providers),
        _frontend_api_sorted_code_list_cell(aliases),
    ]


def _frontend_api_required_summary_input_counts(
    operation: dict[str, object],
    field: Mapping[str, object],
    required_operations: set[str],
    required_fields: set[str],
    target_counts: _FrontendApiCountMap,
    providers: set[str],
    aliases: set[str],
) -> _FrontendApiSummaryDeltaPair:
    if not bool(field.get("required", False)):
        return 1, 0

    name = _frontend_api_input_name(field)
    required_operations.add(_frontend_api_operation_id(operation))
    required_fields.add(name)
    target = _frontend_api_input_target(operation, field)
    _frontend_api_increment_count(target_counts, target)
    option_source = _frontend_api_field_option_source(field)
    if option_source is not None:
        providers.add(_frontend_api_option_source_operation_id(option_source))
    if "maps_to" in field:
        aliases.add(_frontend_api_input_alias_entry(name, field))
    return 1, 1


def _frontend_api_workspace_section_required_summary_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_operation_summary_rows(contract, _frontend_api_required_summary_cells)


def _frontend_api_workspace_section_required_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Required Summary Index / Workspace Section Required Summary 索引",
        (
            "Workspace Section",
            "Actions",
            "Inputs",
            "Required",
            "Operations",
            "Fields",
            "Targets",
            "Providers",
            "Aliases",
        ),
        _frontend_api_workspace_section_required_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_group_required_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_operation_summary_rows(contract, _frontend_api_required_summary_cells)


def _frontend_api_group_required_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Required Summary Index / Group Required Summary 索引",
        (
            "Group",
            "Operations",
            "Inputs",
            "Required",
            "Operations",
            "Fields",
            "Targets",
            "Providers",
            "Aliases",
        ),
        _frontend_api_group_required_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_alias_summary_cells(owner_id: object, operations: Sequence[Mapping[str, object]]) -> list[str]:
    input_count = 0
    alias_count = 0
    alias_operations: set[str] = set()
    alias_fields: set[str] = set()
    targets: set[str] = set()
    providers: set[str] = set()
    aliases: set[str] = set()
    for operation, field in _frontend_api_operation_input_rows(operations):
        input_delta, alias_delta = _frontend_api_alias_summary_input_counts(
            operation,
            field,
            alias_operations,
            alias_fields,
            targets,
            providers,
            aliases,
        )
        input_count += input_delta
        alias_count += alias_delta
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        _markdown_cell(input_count),
        _markdown_cell(alias_count),
        _frontend_api_sorted_code_list_cell(alias_operations),
        _frontend_api_sorted_code_list_cell(alias_fields),
        _frontend_api_sorted_code_list_cell(targets),
        _frontend_api_sorted_code_list_cell(providers),
        _frontend_api_sorted_code_list_cell(aliases),
    ]


def _frontend_api_alias_summary_input_counts(
    operation: dict[str, object],
    field: Mapping[str, object],
    alias_operations: set[str],
    alias_fields: set[str],
    targets: set[str],
    providers: set[str],
    aliases: set[str],
) -> _FrontendApiSummaryDeltaPair:
    if "maps_to" not in field:
        return 1, 0

    name = _frontend_api_input_name(field)
    alias_operations.add(_frontend_api_operation_id(operation))
    alias_fields.add(name)
    targets.add(_frontend_api_input_target(operation, field))
    aliases.add(_frontend_api_input_alias_entry(name, field))
    option_source = _frontend_api_field_option_source(field)
    if option_source is not None:
        providers.add(_frontend_api_option_source_operation_id(option_source))
    return 1, 1


def _frontend_api_workspace_section_alias_summary_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_operation_summary_rows(contract, _frontend_api_alias_summary_cells)


def _frontend_api_workspace_section_alias_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Alias Summary Index / Workspace Section Alias Summary 索引",
        (
            "Workspace Section",
            "Actions",
            "Inputs",
            "Aliases",
            "Operations",
            "Fields",
            "Targets",
            "Providers",
            "Alias Mappings",
        ),
        _frontend_api_workspace_section_alias_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_group_alias_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_operation_summary_rows(contract, _frontend_api_alias_summary_cells)


def _frontend_api_group_alias_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Alias Summary Index / Group Alias Summary 索引",
        (
            "Group",
            "Operations",
            "Inputs",
            "Aliases",
            "Operations",
            "Fields",
            "Targets",
            "Providers",
            "Alias Mappings",
        ),
        _frontend_api_group_alias_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_workspace_action_execution_index_rows(contract: object) -> list[str]:
    return _frontend_api_detail_record_index_rows(
        _frontend_api_workspace_action_execution_records(contract),
        _frontend_api_action_execution_cells,
    )


def _frontend_api_workspace_action_execution_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Action Execution Index / Workspace Action Execution 索引",
        (
            "Workspace Section",
            "Operation ID",
            "Kind",
            "Default Surface",
            "Available Surfaces",
            "Requires Values",
            "State Scope",
            "Normalizer",
            "REST Planner",
        ),
        _frontend_api_workspace_action_execution_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_workspace_action_execution_records(
    contract: object,
) -> list[_FrontendApiDetailRecord]:
    records: list[_FrontendApiDetailRecord] = []
    for (
        section,
        _section_operations,
        section_actions,
    ) in _frontend_api_workspace_section_action_rows(contract):
        section_id = _frontend_api_row_id(section)
        for action in section_actions:
            execution = _frontend_api_action_execution(action)
            if execution is None:
                continue
            records.append((section_id, action, execution))
    return records


def _frontend_api_detail_record_index_rows(
    records: Sequence[_FrontendApiDetailRecord],
    cells: _FrontendApiDetailCellBuilder,
) -> list[str]:
    return _frontend_api_table_rows(cells(owner_id, source, detail) for owner_id, source, detail in records)


def _frontend_api_action_execution_cells(
    section_id: str,
    action: Mapping[str, object],
    execution: Mapping[str, object],
) -> list[str]:
    return [
        _code_cell(section_id),
        _code_cell(_frontend_api_action_operation_id(action)),
        _code_cell(execution.get("kind", "")),
        _code_cell(execution.get("default_surface", "")),
        _frontend_api_code_list_cell(execution.get("available_surfaces", [])),
        _frontend_api_yes_no_cell(execution.get("requires_values", False)),
        _code_cell(execution.get("state_scope", "")),
        _code_cell(execution.get("normalizer_schema", "")),
        _code_cell(execution.get("rest_request_schema", "")),
    ]


def _frontend_api_group_execution_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_action_summary_rows(contract, _frontend_api_execution_summary_cells)


def _frontend_api_group_execution_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Execution Summary Index / Group Execution Summary 索引",
        (
            "Group",
            "Operations",
            "Workspace Actions",
            "Kinds",
            "Default Surfaces",
            "Available Surfaces",
            "Requires Values",
            "Confirmations",
            "State Scopes",
            "Normalizers",
            "REST Planners",
        ),
        _frontend_api_group_execution_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_workspace_section_execution_summary_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_action_summary_rows(contract, _frontend_api_execution_summary_cells)


def _frontend_api_workspace_section_execution_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Execution Summary Index / Workspace Section Execution Summary 索引",
        (
            "Workspace Section",
            "Operations",
            "Workspace Actions",
            "Kinds",
            "Default Surfaces",
            "Available Surfaces",
            "Requires Values",
            "Confirmations",
            "State Scopes",
            "Normalizers",
            "REST Planners",
        ),
        _frontend_api_workspace_section_execution_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_group_confirmation_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_action_summary_rows(contract, _frontend_api_confirmation_summary_cells)


def _frontend_api_group_confirmation_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Confirmation Summary Index / Group Confirmation Summary 索引",
        (
            "Group",
            "Operations",
            "Workspace Actions",
            "Confirmations",
            "Scopes",
            "Styles",
            "Confirm Fields",
            "Operations",
        ),
        _frontend_api_group_confirmation_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_group_action_rows(
    contract: object,
) -> list[_FrontendApiOwnerActionRecord]:
    groups, operation_rows, actions_by_group = _frontend_api_workspace_actions_by_group(contract)
    rows: list[_FrontendApiOwnerActionRecord] = []
    for group in groups:
        group_id = _frontend_api_row_id(group)
        group_operations = [operation for operation in operation_rows if _frontend_api_operation_group_id(operation) == group_id]
        rows.append((group, group_operations, actions_by_group.get(group_id, [])))
    return rows


def _frontend_api_workspace_actions_by_group(
    contract: object,
) -> _FrontendApiWorkspaceActionGroups:
    if not isinstance(contract, Mapping):
        return [], [], {}
    groups = contract.get("groups", [])
    operations = contract.get("operations", [])
    workspace = contract.get("workspace", {})
    if not isinstance(groups, Sequence) or isinstance(groups, (str, bytes)):
        return [], [], {}
    if not isinstance(operations, Sequence) or isinstance(operations, (str, bytes)):
        operations = []
    if not isinstance(workspace, Mapping):
        return [], [], {}
    group_rows = _frontend_api_group_rows(contract)
    operation_rows = _frontend_api_dict_rows(operations)
    operation_by_id = _frontend_api_operation_by_id(operation_rows)
    actions_by_group: _FrontendApiActionGroupMap = {}
    for section in _frontend_api_workspace_section_rows(contract):
        for action in _frontend_api_mapping_rows(section.get("actions", [])):
            operation = operation_by_id.get(_frontend_api_action_operation_id(action))
            if not operation:
                continue
            group_id = _frontend_api_operation_group_id(operation)
            append_index_entry(actions_by_group, group_id, dict(action))
    return group_rows, operation_rows, actions_by_group


def _frontend_api_execution_summary_cells(
    owner_id: object,
    operations: Sequence[Mapping[str, object]],
    actions: Sequence[Mapping[str, object]],
) -> list[str]:
    kind_counts: _FrontendApiCountMap = {}
    default_counts: _FrontendApiCountMap = {}
    available_counts: _FrontendApiCountMap = {}
    state_counts: _FrontendApiCountMap = {}
    values_required = 0
    confirmations = 0
    normalizers = 0
    rest_planners = 0
    for action in actions:
        values_delta, confirmation_delta, normalizer_delta, rest_planner_delta = _frontend_api_execution_summary_action_counts(
            action,
            kind_counts,
            default_counts,
            available_counts,
            state_counts,
        )
        values_required += values_delta
        confirmations += confirmation_delta
        normalizers += normalizer_delta
        rest_planners += rest_planner_delta
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        _markdown_cell(len(actions)),
        _frontend_api_count_list_cell(kind_counts),
        _frontend_api_count_list_cell(default_counts),
        _frontend_api_count_list_cell(available_counts),
        _markdown_cell(values_required),
        _markdown_cell(confirmations),
        _frontend_api_count_list_cell(state_counts),
        _markdown_cell(normalizers),
        _markdown_cell(rest_planners),
    ]


def _frontend_api_execution_summary_action_counts(
    action: Mapping[str, object],
    kind_counts: _FrontendApiCountMap,
    default_counts: _FrontendApiCountMap,
    available_counts: _FrontendApiCountMap,
    state_counts: _FrontendApiCountMap,
) -> _FrontendApiSummaryDeltaQuad:
    execution = _frontend_api_action_execution(action)
    if execution is None:
        return 0, 0, 0, 0

    kind = str(execution.get("kind", ""))
    if kind:
        _frontend_api_increment_count(kind_counts, kind)
    default_surface = str(execution.get("default_surface", ""))
    if default_surface:
        _frontend_api_increment_count(default_counts, default_surface)
    for surface in _frontend_api_sequence_items(execution.get("available_surfaces", [])):
        surface_name = str(surface)
        _frontend_api_increment_count(available_counts, surface_name)
    state_scope = str(execution.get("state_scope", ""))
    if state_scope:
        _frontend_api_increment_count(state_counts, state_scope)

    confirmation = _frontend_api_required_confirmation(execution.get("confirmation", {}))
    return (
        int(bool(execution.get("requires_values", False))),
        int(confirmation is not None),
        int(bool(execution.get("normalizer_schema", ""))),
        int(bool(execution.get("rest_request_schema", ""))),
    )


def _frontend_api_confirmation_summary_cells(
    owner_id: object,
    operations: Sequence[Mapping[str, object]],
    actions: Sequence[Mapping[str, object]],
) -> list[str]:
    return [
        *_frontend_api_owner_operation_count_cells(owner_id, operations),
        *_frontend_api_confirmation_metric_cells(actions),
    ]


def _frontend_api_confirmation_metric_cells(
    actions: Sequence[Mapping[str, object]],
) -> list[str]:
    confirmed_operations, scope_counts, style_counts, field_counts = _frontend_api_confirmation_counts(actions)
    return [
        _markdown_cell(len(actions)),
        _markdown_cell(len(confirmed_operations)),
        _frontend_api_count_list_cell(scope_counts),
        _frontend_api_count_list_cell(style_counts),
        _frontend_api_count_list_cell(field_counts),
        _frontend_api_code_list_cell(confirmed_operations),
    ]


def _frontend_api_confirmation_counts(
    actions: Sequence[Mapping[str, object]],
) -> _FrontendApiConfirmationCounts:
    confirmed_operations: list[str] = []
    scope_counts: _FrontendApiCountMap = {}
    style_counts: _FrontendApiCountMap = {}
    field_counts: _FrontendApiCountMap = {}
    for action in actions:
        confirmation = _frontend_api_action_confirmation(action)
        if confirmation is None:
            continue
        confirmed_operations.append(_frontend_api_action_operation_id(action))
        scope = str(confirmation.get("scope", ""))
        style = str(confirmation.get("style", ""))
        _frontend_api_increment_count(scope_counts, scope)
        _frontend_api_increment_count(style_counts, style)
        for field in _frontend_api_sequence_items(confirmation.get("confirm_fields", [])):
            field_name = str(field)
            _frontend_api_increment_count(field_counts, field_name)
    return confirmed_operations, scope_counts, style_counts, field_counts


def _frontend_api_count_list(counts: Mapping[str, int], *, exclude: Sequence[str] = ()) -> list[str]:
    return [f"{name}:{counts[name]}" for name in sorted(counts) if name not in exclude]


def _frontend_api_count_list_cell(counts: Mapping[str, int]) -> str:
    return _frontend_api_code_list_cell(_frontend_api_count_list(counts))


def _frontend_api_workspace_section_confirmation_summary_index_rows(
    contract: object,
) -> list[str]:
    return _frontend_api_workspace_section_action_summary_rows(contract, _frontend_api_workspace_section_confirmation_summary_cells)


def _frontend_api_workspace_section_confirmation_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Workspace Section Confirmation Summary Index / Workspace Section Confirmation Summary 索引",
        (
            "Workspace Section",
            "Actions",
            "Confirmations",
            "Scopes",
            "Styles",
            "Confirm Fields",
            "Operations",
        ),
        _frontend_api_workspace_section_confirmation_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_workspace_section_confirmation_summary_cells(
    owner_id: object,
    _operations: Sequence[Mapping[str, object]],
    actions: Sequence[Mapping[str, object]],
) -> list[str]:
    return [
        _code_cell(owner_id),
        *_frontend_api_confirmation_metric_cells(actions),
    ]


def _frontend_api_confirmation_index_rows(contract: object) -> list[str]:
    return _frontend_api_detail_record_index_rows(
        _frontend_api_confirmation_records(contract),
        _frontend_api_confirmation_cells,
    )


def _frontend_api_confirmation_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Confirmation Index / Confirmation 索引",
        (
            "Workspace Section",
            "Scope",
            "Style",
            "Confirm Fields",
            "Operation ID",
            "Title",
        ),
        _frontend_api_confirmation_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_confirmation_records(
    contract: object,
) -> list[_FrontendApiDetailRecord]:
    records: list[_FrontendApiDetailRecord] = []
    for (
        section,
        _section_operations,
        section_actions,
    ) in _frontend_api_workspace_section_action_rows(contract):
        section_id = _frontend_api_row_id(section)
        for action in section_actions:
            confirmation = _frontend_api_action_confirmation(action)
            if confirmation is None:
                continue
            records.append((section_id, action, confirmation))
    return records


def _frontend_api_confirmation_cells(
    section_id: str,
    action: Mapping[str, object],
    confirmation: Mapping[str, object],
) -> list[str]:
    confirm_fields = _frontend_api_sequence_items(confirmation.get("confirm_fields", []))
    return [
        _code_cell(section_id),
        _code_cell(confirmation.get("scope", "")),
        _code_cell(confirmation.get("style", "")),
        _markdown_cell(", ".join(f"`{field}`" for field in confirm_fields)),
        _code_cell(_frontend_api_action_operation_id(action)),
        _markdown_cell(confirmation.get("title", "")),
    ]


def _frontend_api_option_source_index_rows(contract: object) -> list[str]:
    return _frontend_api_detail_record_index_rows(
        _frontend_api_option_source_records(contract),
        _frontend_api_option_source_cells,
    )


def _frontend_api_option_source_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Option Source Index / Option Source 索引",
        (
            "Operation ID",
            "Field",
            "Values Path",
            "Provider Operation",
            "Requires",
            "Forward",
            "Filters",
        ),
        _frontend_api_option_source_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_option_source_records(
    contract: object,
) -> list[_FrontendApiDetailRecord]:
    records: list[_FrontendApiDetailRecord] = []
    for operation, field in _frontend_api_contract_input_rows(contract):
        option_source = _frontend_api_field_option_source(field)
        if option_source is None:
            continue
        records.append((_frontend_api_operation_id(operation), field, option_source))
    return records


def _frontend_api_option_source_cells(
    operation_id: str,
    field: Mapping[str, object],
    option_source: Mapping[str, object],
) -> list[str]:
    return [
        _code_cell(operation_id),
        _code_cell(field.get("name", "")),
        _code_cell(_frontend_api_option_source_values_path(option_source)),
        _code_cell(_frontend_api_option_source_operation_id(option_source)),
        _frontend_api_code_list_cell(_frontend_api_option_source_requires(option_source)),
        _frontend_api_code_list_cell(_frontend_api_option_source_forward(option_source)),
        _frontend_api_option_source_filter_cell(_frontend_api_option_source_filters(option_source)),
    ]


def _frontend_api_option_provider_index_rows(contract: object) -> list[str]:
    providers = _frontend_api_option_provider_records(contract)
    return _frontend_api_table_rows(_frontend_api_option_provider_cells(provider_id, providers[provider_id]) for provider_id in sorted(providers))


def _frontend_api_option_provider_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Option Provider Index / Option Provider 索引",
        (
            "Provider Operation",
            "Fields",
            "Consumer Fields",
            "Consumers",
            "Values Paths",
            "Requires",
            "Forward",
            "Filters",
        ),
        _frontend_api_option_provider_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_option_provider_records(
    contract: object,
) -> dict[str, _FrontendApiOptionProviderRecord]:
    providers: dict[str, _FrontendApiOptionProviderRecord] = {}
    for operation, field in _frontend_api_contract_input_rows(contract):
        option_source = _frontend_api_field_option_source(field)
        if option_source is None:
            continue
        _frontend_api_update_option_provider_record(providers, operation, field, option_source)
    return providers


def _frontend_api_update_option_provider_record(
    providers: dict[str, _FrontendApiOptionProviderRecord],
    operation: Mapping[str, object],
    field: Mapping[str, object],
    option_source: Mapping[str, object],
) -> None:
    operation_id = _frontend_api_operation_id(operation)
    provider_id = _frontend_api_option_source_operation_id(option_source)
    provider = providers.setdefault(provider_id, _frontend_api_option_provider_record())
    provider["consumer_fields"].append(f"{operation_id}.{field.get('name', '')}")
    provider["consumers"].add(operation_id)
    provider["paths"].add(
        _frontend_api_option_source_values_path(option_source),
    )
    provider["requires"].update(str(value) for value in _frontend_api_option_source_requires(option_source))
    provider["forward"].update(str(value) for value in _frontend_api_option_source_forward(option_source))
    provider["filters"].update(
        _frontend_api_option_source_filter_parts(_frontend_api_option_source_filters(option_source)),
    )


def _frontend_api_option_provider_cells(provider_id: str, provider: _FrontendApiOptionProviderRecord) -> list[str]:
    return [
        _code_cell(provider_id),
        _markdown_cell(len(provider["consumer_fields"])),
        _frontend_api_code_list_cell(provider["consumer_fields"]),
        _frontend_api_sorted_code_list_cell(provider["consumers"]),
        _frontend_api_sorted_code_list_cell(provider["paths"]),
        _frontend_api_sorted_code_list_cell(provider["requires"]),
        _frontend_api_sorted_code_list_cell(provider["forward"]),
        _frontend_api_sorted_code_list_cell(provider["filters"]),
    ]


def _frontend_api_option_provider_record() -> _FrontendApiOptionProviderRecord:
    return {
        "consumer_fields": [],
        "consumers": set(),
        "paths": set(),
        "requires": set(),
        "forward": set(),
        "filters": set(),
    }


def _frontend_api_option_source_path(path: object) -> str:
    path_items = _frontend_api_sequence_or_none(path)
    if path_items is not None:
        return ".".join(str(part) for part in path_items)
    return str(path)


def _frontend_api_option_source_values_path(option_source: Mapping[str, object]) -> str:
    return _frontend_api_option_source_path(option_source.get("values_path", []))


def _frontend_api_option_source_required_values_path(
    option_source: Mapping[str, object],
) -> object:
    return option_source["values_path"]


def _frontend_api_option_source_requires(
    option_source: Mapping[str, object],
) -> list[object]:
    return _frontend_api_sequence_items(option_source.get("requires", []))


def _frontend_api_option_source_forward(
    option_source: Mapping[str, object],
) -> list[object]:
    return _frontend_api_sequence_items(option_source.get("forward", []))


def _frontend_api_option_source_filters(option_source: Mapping[str, object]) -> object:
    return option_source.get("filters", {})


def _frontend_api_option_source_value_field(option_source: Mapping[str, object]) -> str:
    return str(option_source["value_field"])


def _frontend_api_option_source_label_field(option_source: Mapping[str, object]) -> str:
    return str(option_source["label_field"])


def _frontend_api_option_source_detail_fields(
    option_source: Mapping[str, object],
) -> list[str]:
    return [str(value) for value in _frontend_api_sequence_items(option_source.get("detail_fields", []))]


def _frontend_api_code_list_cell(values: object) -> str:
    value_items = _frontend_api_sequence_items(values)
    if not value_items:
        return _markdown_cell("")
    if all(_markdown_cell(value) for value in value_items):
        return code_list_cell(value_items)
    return _markdown_cell(", ".join(f"`{value}`" for value in value_items))


def _frontend_api_sorted_code_list_cell(values: object) -> str:
    if isinstance(values, set):
        return _frontend_api_code_list_cell(sorted(values))
    value_items = _frontend_api_sequence_items(values)
    if value_items:
        return _frontend_api_code_list_cell(sorted(value_items))
    return _markdown_cell("")


def _frontend_api_sequence_items(values: object) -> list[object]:
    return _frontend_api_sequence_or_none(values) or []


def _frontend_api_mapping_rows(values: object) -> list[Mapping[str, object]]:
    return [value for value in _frontend_api_sequence_items(values) if isinstance(value, Mapping)]


def _frontend_api_dict_rows(values: object) -> list[dict[str, object]]:
    return [dict(value) for value in _frontend_api_mapping_rows(values)]


def _frontend_api_workspace_section_rows(contract: object) -> list[dict[str, object]]:
    if not isinstance(contract, Mapping):
        return []
    workspace = contract.get("workspace", {})
    if not isinstance(workspace, Mapping):
        return []
    return _frontend_api_dict_rows(workspace.get("sections", []))


def _frontend_api_group_rows(contract: object) -> list[dict[str, object]]:
    if not isinstance(contract, Mapping):
        return []
    return _frontend_api_dict_rows(contract.get("groups", []))


def _frontend_api_operation_by_id(
    operations: Sequence[dict[str, object]],
) -> dict[str, dict[str, object]]:
    return {_frontend_api_operation_id(operation): operation for operation in operations}


def _frontend_api_operation_id(operation: Mapping[str, object]) -> str:
    return str(operation.get("id", ""))


def _frontend_api_operation_group_id(operation: Mapping[str, object]) -> str:
    return str(operation.get("group", ""))


def _frontend_api_operation_mode(operation: Mapping[str, object]) -> str:
    return "write" if operation.get("mutates") else "read"


def _frontend_api_operation_payload(operation: Mapping[str, object]) -> str:
    return str(operation.get("payload") or "untyped")


def _frontend_api_operation_payload_cell(operation: Mapping[str, object]) -> str:
    return str(operation.get("payload", ""))


def _frontend_api_operation_status(operation: Mapping[str, object]) -> str:
    return str(operation.get("status", ""))


def _frontend_api_action_operation_id(action: Mapping[str, object]) -> str:
    return str(action.get("operation_id", ""))


def _frontend_api_row_id(row: Mapping[str, object]) -> str:
    return str(row.get("id", ""))


def _frontend_api_row_ids(values: object) -> list[str]:
    return [str(row["id"]) for row in _frontend_api_mapping_rows(values)]


def _frontend_api_sequence_or_none(values: object) -> list[object] | None:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return None
    return list(values)


def _frontend_api_operation_id_cells(operation_ids: object) -> list[str]:
    operation_id_list = _frontend_api_operation_id_list(operation_ids)
    return [
        _markdown_cell(len(operation_id_list)),
        _frontend_api_code_list_cell(operation_id_list),
    ]


def _frontend_api_option_source_filter_cell(filters: object) -> str:
    return _frontend_api_code_list_cell(_frontend_api_option_source_filter_parts(filters))


def _frontend_api_option_source_filter_parts(filters: object) -> list[str]:
    if not isinstance(filters, Mapping):
        return []
    return [f"{key}={dumps_json(value)}" for key, value in sorted(filters.items())]


def _frontend_api_option_source_provider_id(field: Mapping[str, object]) -> str:
    option_source = _frontend_api_field_option_source(field)
    if option_source is None:
        return ""
    return _frontend_api_option_source_operation_id(option_source)


def _frontend_api_option_source_provider_cell(field: Mapping[str, object]) -> str:
    return _code_cell(_frontend_api_option_source_provider_id(field))


def _frontend_api_option_source_required_operation_id(
    option_source: Mapping[str, object],
) -> str:
    return str(option_source["operation_id"])


def _frontend_api_option_source_operation_id(
    option_source: Mapping[str, object],
) -> str:
    return str(option_source.get("operation_id", ""))


def _frontend_api_field_option_source(
    field: Mapping[str, object],
) -> Mapping[str, object] | None:
    option_source = field.get("option_source")
    return option_source if isinstance(option_source, Mapping) else None


def _frontend_api_required_cell(field: Mapping[str, object]) -> str:
    return _frontend_api_yes_no_cell(field.get("required", False))


def _frontend_api_yes_no_cell(value: object) -> str:
    return _markdown_cell("yes" if bool(value) else "no")


def _frontend_api_input_name(field: Mapping[str, object]) -> str:
    return str(field.get("name", ""))


def _frontend_api_mapped_input_name(field: Mapping[str, object]) -> str:
    return str(field.get("maps_to", _frontend_api_input_name(field)))


def _frontend_api_input_target(operation: dict[str, object], field: Mapping[str, object]) -> str:
    return _input_target(operation, _frontend_api_input_name(field))


def _frontend_api_input_target_cell(operation: dict[str, object], field: Mapping[str, object]) -> str:
    return _code_cell(_frontend_api_input_target(operation, field))


def _frontend_api_input_alias(field: Mapping[str, object]) -> str:
    return str(field.get("maps_to", ""))


def _frontend_api_input_alias_entry(name: str, field: Mapping[str, object]) -> str:
    return f"{name}->{_frontend_api_input_alias(field)}"


def _frontend_api_input_alias_cell(field: Mapping[str, object]) -> str:
    return _code_cell(_frontend_api_input_alias(field))


def _frontend_api_input_identity_cells(operation: Mapping[str, object], field: Mapping[str, object]) -> list[str]:
    return [
        _code_cell(_frontend_api_input_name(field)),
        _code_cell(_frontend_api_operation_id(operation)),
        _code_cell(field.get("type", "")),
    ]


def _frontend_api_input_field_index_rows(contract: object) -> list[str]:
    return _frontend_api_input_index_rows(contract, _frontend_api_input_field_cells)


def _frontend_api_input_field_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Input Field Index / Input Field 索引",
        (
            "Field",
            "Operation ID",
            "Type",
            "Required",
            "Default",
            "Choices",
            "Maps To",
            "Option Source",
        ),
        _frontend_api_input_field_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_input_index_rows(
    contract: object,
    cells_for_input: _FrontendApiInputCellBuilder,
    *,
    include: _FrontendApiInputPredicate | None = None,
) -> list[str]:
    return _frontend_api_table_rows(
        cells_for_input(operation, field) for operation, field in _frontend_api_contract_input_rows(contract) if include is None or include(field)
    )


def _frontend_api_has_required_input(field: Mapping[str, object]) -> bool:
    return bool(field.get("required", False))


def _frontend_api_has_input_default(field: Mapping[str, object]) -> bool:
    return "default" in field


def _frontend_api_has_input_constraint(field: Mapping[str, object]) -> bool:
    return "choices" in field or "minimum" in field or "maximum" in field or field.get("nonblank") is True


def _frontend_api_has_input_alias(field: Mapping[str, object]) -> bool:
    return "maps_to" in field


def _frontend_api_input_field_cells(operation: Mapping[str, object], field: Mapping[str, object]) -> list[str]:
    return [
        *_frontend_api_input_identity_cells(operation, field),
        _frontend_api_required_cell(field),
        _frontend_api_default_value_cell(field),
        _frontend_api_code_list_cell(field.get("choices", [])),
        _frontend_api_input_alias_cell(field),
        _frontend_api_option_source_provider_cell(field),
    ]


def _frontend_api_group_form_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_group_operation_detail_rows(contract, _frontend_api_form_summary_cells)


def _frontend_api_group_form_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Group Form Summary Index / Group Form Summary 索引",
        (
            "Group",
            "Title",
            "Operations",
            "Inputs",
            "Required",
            "Defaults",
            "Aliases",
            "Option Sources",
            "Constraints",
            "Controls",
        ),
        _frontend_api_group_form_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_form_summary_cells(owner: Mapping[str, object], operations: Sequence[Mapping[str, object]]) -> list[str]:
    footprint = _frontend_api_form_footprint(operations)
    return [
        _code_cell(_frontend_api_row_id(owner)),
        _markdown_cell(owner.get("title", "")),
        _markdown_cell(len(operations)),
        *_frontend_api_form_footprint_metric_cells(footprint, footprint["controls"]),
    ]


def _frontend_api_form_footprint_metric_cells(footprint: Mapping[str, object], controls: object) -> list[str]:
    return [
        _markdown_cell(footprint["inputs"]),
        _markdown_cell(footprint["required"]),
        _markdown_cell(footprint["defaults"]),
        _markdown_cell(footprint["aliases"]),
        _markdown_cell(footprint["option_sources"]),
        _markdown_cell(footprint["constraints"]),
        _frontend_api_code_list_cell(controls),
    ]


def _frontend_api_form_footprint(
    operations: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    input_count = 0
    required_count = 0
    default_count = 0
    alias_count = 0
    option_source_count = 0
    constraint_count = 0
    control_counts: _FrontendApiCountMap = {}
    control_names: set[str] = set()
    for operation_row, field in _frontend_api_operation_input_rows(operations):
        field_row = dict(field)
        input_count += 1
        required_count += int(bool(field_row.get("required", False)))
        default_count += int("default" in field_row)
        alias_count += int("maps_to" in field_row)
        option_source_count += int(isinstance(field_row.get("option_source"), Mapping))
        constraint_count += int("choices" in field_row or "minimum" in field_row or "maximum" in field_row or field_row.get("nonblank") is True)
        control = str(_frontend_api_form_field(operation_row, field_row).get("control", ""))
        control_names.add(control)
        if control:
            _frontend_api_increment_count(control_counts, control)
    return {
        "inputs": input_count,
        "required": required_count,
        "defaults": default_count,
        "aliases": alias_count,
        "option_sources": option_source_count,
        "constraints": constraint_count,
        "controls": _frontend_api_count_list(control_counts),
        "control_names": sorted(control_names),
    }


def _frontend_api_operation_form_summary_index_rows(contract: object) -> list[str]:
    return _frontend_api_table_rows(_frontend_api_operation_form_summary_cells(operation_row) for operation_row in _frontend_api_operation_rows(contract))


def _frontend_api_operation_form_summary_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Operation Form Summary Index / Operation Form Summary 索引",
        (
            "Operation ID",
            "Inputs",
            "Required",
            "Defaults",
            "Aliases",
            "Option Sources",
            "Constraints",
            "Controls",
        ),
        _frontend_api_operation_form_summary_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_operation_form_summary_cells(
    operation: Mapping[str, object],
) -> list[str]:
    footprint = _frontend_api_form_footprint([operation])
    return [
        _code_cell(_frontend_api_operation_id(operation)),
        *_frontend_api_form_footprint_metric_cells(footprint, footprint["control_names"]),
    ]


def _frontend_api_form_control_index_rows(contract: object) -> list[str]:
    return _frontend_api_input_index_rows(contract, _frontend_api_form_control_input_cells)


def _frontend_api_form_control_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Form Control Index / Form Control 索引",
        (
            "Field",
            "Operation ID",
            "Control",
            "Type",
            "Required",
            "Option Source",
            "Choices",
        ),
        _frontend_api_form_control_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_form_control_input_cells(operation: Mapping[str, object], field: Mapping[str, object]) -> list[str]:
    form_field = _frontend_api_form_field(dict(operation), dict(field))
    return _frontend_api_form_control_cells(operation, form_field)


def _frontend_api_form_control_cells(operation: Mapping[str, object], form_field: Mapping[str, object]) -> list[str]:
    name_cell, operation_id_cell, type_cell = _frontend_api_input_identity_cells(operation, form_field)
    return [
        name_cell,
        operation_id_cell,
        _code_cell(form_field.get("control", "")),
        type_cell,
        _frontend_api_required_cell(form_field),
        _frontend_api_option_source_provider_cell(form_field),
        _frontend_api_code_list_cell(form_field.get("choices", [])),
    ]


def _frontend_api_required_input_index_rows(contract: object) -> list[str]:
    return _frontend_api_input_index_rows(
        contract,
        _frontend_api_required_input_cells,
        include=_frontend_api_has_required_input,
    )


def _frontend_api_required_input_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Required Input Index / Required Input 索引",
        ("Field", "Operation ID", "Type", "Target", "Maps To", "Option Source"),
        _frontend_api_required_input_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_required_input_cells(operation: Mapping[str, object], field: Mapping[str, object]) -> list[str]:
    return [
        *_frontend_api_input_identity_cells(operation, field),
        _frontend_api_input_target_cell(operation, field),
        _frontend_api_input_alias_cell(field),
        _frontend_api_option_source_provider_cell(field),
    ]


def _frontend_api_input_default_index_rows(contract: object) -> list[str]:
    return _frontend_api_input_index_rows(
        contract,
        _frontend_api_input_default_cells,
        include=_frontend_api_has_input_default,
    )


def _frontend_api_input_default_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Input Default Index / Input Default 索引",
        ("Field", "Operation ID", "Type", "Default", "Target", "Maps To", "Required"),
        _frontend_api_input_default_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_input_default_cells(operation: Mapping[str, object], field: Mapping[str, object]) -> list[str]:
    return [
        *_frontend_api_input_identity_cells(operation, field),
        _frontend_api_default_value_cell(field),
        _frontend_api_input_target_cell(operation, field),
        _frontend_api_input_alias_cell(field),
        _frontend_api_required_cell(field),
    ]


def _frontend_api_input_constraint_index_rows(contract: object) -> list[str]:
    return _frontend_api_input_index_rows(
        contract,
        _frontend_api_input_constraint_cells,
        include=_frontend_api_has_input_constraint,
    )


def _frontend_api_input_constraint_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Input Constraint Index / Input Constraint 索引",
        (
            "Field",
            "Operation ID",
            "Type",
            "Choices",
            "Minimum",
            "Maximum",
            "Nonblank",
            "Required",
        ),
        _frontend_api_input_constraint_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_input_constraint_cells(operation: Mapping[str, object], field: Mapping[str, object]) -> list[str]:
    return [
        *_frontend_api_input_identity_cells(operation, field),
        _frontend_api_code_list_cell(field.get("choices", [])),
        _code_cell(field.get("minimum", "")),
        _code_cell(field.get("maximum", "")),
        _frontend_api_yes_no_cell(field.get("nonblank") is True),
        _frontend_api_required_cell(field),
    ]


def _frontend_api_input_target_index_rows(contract: object) -> list[str]:
    return _frontend_api_input_index_rows(contract, _frontend_api_input_target_cells)


def _frontend_api_input_target_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Input Target Index / Input Target 索引",
        ("Target", "Field", "Operation ID", "Maps To", "Type", "Required"),
        _frontend_api_input_target_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_input_target_cells(operation: Mapping[str, object], field: Mapping[str, object]) -> list[str]:
    name_cell, operation_id_cell, type_cell = _frontend_api_input_identity_cells(operation, field)
    return [
        _frontend_api_input_target_cell(operation, field),
        name_cell,
        operation_id_cell,
        _frontend_api_input_alias_cell(field),
        type_cell,
        _frontend_api_required_cell(field),
    ]


def _frontend_api_input_alias_index_rows(contract: object) -> list[str]:
    return _frontend_api_input_index_rows(contract, _frontend_api_input_alias_cells, include=_frontend_api_has_input_alias)


def _frontend_api_input_alias_index_section(contract: object, body: Sequence[str]) -> list[str]:
    return _frontend_api_table_section(
        "Input Alias Index / Input Alias 索引",
        (
            "Field",
            "Operation ID",
            "Type",
            "Target",
            "Maps To",
            "Required",
            "Option Source",
        ),
        _frontend_api_input_alias_index_rows(contract),
        level=3,
        body=body,
    )


def _frontend_api_input_alias_cells(operation: Mapping[str, object], field: Mapping[str, object]) -> list[str]:
    return [
        *_frontend_api_input_identity_cells(operation, field),
        _frontend_api_input_target_cell(operation, field),
        _frontend_api_input_alias_cell(field),
        _frontend_api_required_cell(field),
        _frontend_api_option_source_provider_cell(field),
    ]


def _frontend_api_default_value_cell(field: Mapping[str, object]) -> str:
    if "default" not in field:
        return _markdown_cell("")
    value = field["default"]
    if isinstance(value, bool):
        return _code_cell("true" if value else "false")
    if isinstance(value, str | int | float):
        return _code_cell(value)
    return _code_cell(dumps_json(value))


def _frontend_api_reference_cells(operation: Mapping[str, object]) -> list[str]:
    return [
        *_frontend_api_operation_identity_cells(operation, include_status=True),
        _code_cell(_frontend_api_operation_mode(operation)),
        *_frontend_api_operation_surface_cells(operation, "sdk", "cli", "rest", "mcp", "lsp"),
        _frontend_api_operation_inputs_cell(operation),
        _code_cell(_frontend_api_operation_payload_cell(operation)),
        _markdown_cell(operation["summary"]),
    ]


def _frontend_api_sdk_cli_cells(operation: Mapping[str, object]) -> list[str]:
    return [
        *_frontend_api_operation_identity_cells(operation),
        _code_cell(_frontend_api_operation_mode(operation)),
        *_frontend_api_operation_surface_cells(operation, "sdk", "cli"),
        _frontend_api_operation_inputs_cell(operation),
        _markdown_cell(operation["summary"]),
    ]


def _inputs_cell(inputs: object) -> str:
    if not isinstance(inputs, Sequence) or isinstance(inputs, (str, bytes)):
        return ""
    names: list[str] = []
    for field in inputs:
        if isinstance(field, dict) and "name" in field:
            names.append(f"`{_markdown_cell(field['name'])}`")
    return ", ".join(names)


def _frontend_api_operation_inputs_cell(operation: Mapping[str, object]) -> str:
    return _inputs_cell(operation.get("inputs", []))


def _frontend_api_operation_identity_cells(operation: Mapping[str, object], *, include_status: bool = False) -> list[str]:
    cells = [
        _code_cell(operation["id"]),
        _code_cell(operation["group"]),
    ]
    if include_status:
        cells.append(_code_cell(operation["status"]))
    return cells


def _frontend_api_operation_surface_cells(operation: Mapping[str, object], *surfaces: str) -> list[str]:
    return [_code_cell(operation.get(surface, "")) for surface in surfaces]


def _rest_request_candidates(normalized: dict[str, object]) -> dict[str, object]:
    candidates: dict[str, object] = {}
    for bucket_name in _FRONTEND_API_INPUT_BUCKET_NAMES:
        bucket = normalized[bucket_name]
        if isinstance(bucket, dict):
            candidates.update(bucket)
    return candidates


def _fill_rest_path_parameters(path: str, candidates: dict[str, object]) -> str:
    planned_path = path
    for name in _rest_path_parameter_names(path):
        if name not in candidates:
            raise ValueError(f"Missing REST path parameter for frontend API request: {name}.")
        value = candidates.pop(name)
        planned_path = planned_path.replace("{" + name + "}", quote(str(value), safe=""))
    return planned_path


def _rest_path_parameter_names(path: str) -> list[str]:
    names: list[str] = []
    index = 0
    while index < len(path):
        start = path.find("{", index)
        if start == -1:
            break
        end = path.find("}", start + 1)
        if end == -1:
            break
        name = path[start + 1 : end].strip()
        if name:
            names.append(name)
        index = end + 1
    return names


def _rest_body_inputs(operation_id: str, operation: dict[str, object]) -> set[str]:
    return set(REST_BODY_INPUTS.get(operation_id, ()))


def _submitted_target_names(operation_id: str, submitted: Mapping[str, object]) -> set[str]:
    form = get_frontend_api_form(operation_id)
    names: set[str] = set()
    for field in form["fields"]:
        if isinstance(field, dict) and field["name"] in submitted:
            names.add(_frontend_api_mapped_input_name(field))
    return names
