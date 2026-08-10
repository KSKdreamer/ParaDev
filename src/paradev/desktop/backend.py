"""Self-contained command protocol for the ParaDev desktop backend."""

from __future__ import annotations

import platform
import sys
from collections.abc import Callable, Mapping, Sequence
from contextlib import redirect_stdout
from types import MappingProxyType
from typing import TextIO, cast

from typing_extensions import TypedDict

import heavenbase
from heavenbase.utils import dumps_json, loads_json, snake

import paradev
from paradev.api.projects import (
    apply_project_draft,
    create_module_batch,
    create_module_draft,
    normalize_project_draft_mutations,
    plan_project_localization_update,
    plan_project_source_form_updates,
    read_project_localization_workspace,
    read_project_source_form,
)
from paradev._catalog import (
    CATALOG_QUERY_DEFAULT_INCLUDE_DATA,
    CATALOG_QUERY_DEFAULT_OFFSET,
    CATALOG_QUERY_MAX_HYDRATED_LIMIT,
    CATALOG_QUERY_MAX_LIMIT,
)
from paradev.desktop.local import (
    desktop_chat,
    desktop_chat_profiles,
    desktop_dependency_status,
    desktop_install_dependency,
    desktop_read_app_config,
    desktop_read_binary_source,
    desktop_read_config_value,
    desktop_read_text_source,
    desktop_read_thumbnail_cache,
    desktop_reset_chat_profile,
    desktop_test_llm_route,
    desktop_write_app_config,
    desktop_write_browser_cache,
    desktop_write_chat_profile,
    desktop_write_config_value,
    desktop_write_thumbnail_cache,
    read_project_browser_cache,
)
from paradev.desktop.project_packages import (
    desktop_install_project_package,
    desktop_project_package_catalog,
)
from paradev.desktop.shell import (
    desktop_hoi4_launch_readiness,
    desktop_open_path,
    desktop_path_status,
    desktop_project_build_command,
    desktop_run_hoi4,
)
from paradev.hb import catalog_refresh
from paradev.sdk import desktop_state, open_project
from paradev.sdk._module_diagram_api import (
    module_diagram_intents,
    module_diagram_node_intents,
)

DESKTOP_BACKEND_PROTOCOL = "paradev.desktop.backend.v1"
DESKTOP_BACKEND_INFO_SCHEMA = "paradev.desktop.backend-info.v1"
_BUILD_COMMAND_PREFIX = ("uv", "run", "paradev")


class _DesktopCallRequest(TypedDict):
    """Validated desktop-call request envelope."""

    protocol: str
    operation: str
    args: list[str]


class _DesktopStateRequest(TypedDict, total=False):
    """Validated desktop-state request payload."""

    projectRoot: str | None
    includeBrowser: bool | None


class _ProjectBrowserRootRequest(TypedDict):
    """Required project-browser request fields."""

    projectRoot: str


class _ProjectBrowserRequest(_ProjectBrowserRootRequest, total=False):
    """Validated project-browser request payload."""

    profile: str | None
    kind: str | None
    family: str | None
    moduleId: str | None
    collectionId: str | None
    summary: bool | None


class _ModuleDiagramRequired(TypedDict):
    """Required source-backed module diagram request fields."""

    projectRoot: str
    family: str


class _ModuleDiagramRequest(_ModuleDiagramRequired, total=False):
    """Validated source-backed module diagram projection request."""

    profile: str | None


class _ModuleDiagramEditRequest(_ModuleDiagramRequired, total=False):
    """Validated source-backed module diagram edit request."""

    profile: str | None
    positionIntents: list[dict[str, object]]
    edgeIntents: list[dict[str, object]]
    nodeIntents: list[dict[str, object]]
    write: bool | None
    planHash: str | None


class _ProjectCatalogQueryRequired(TypedDict):
    """Required project catalog query request fields."""

    projectRoot: str
    limit: int


class _ProjectCatalogQueryRequest(_ProjectCatalogQueryRequired, total=False):
    """Validated finite project catalog query request payload."""

    entity: str | None
    targetId: str | None
    name: str | None
    tag: str | None
    offset: int
    includeData: bool | None


class _ProjectCatalogStatusRequest(TypedDict):
    """Validated canonical project catalog status request payload."""

    projectRoot: str


class _ProjectCatalogRefreshRequired(TypedDict):
    """Required project catalog refresh request fields."""

    projectRoot: str


class _ProjectCatalogRefreshRequest(_ProjectCatalogRefreshRequired, total=False):
    """Validated canonical project catalog refresh request payload."""

    profile: str | None


class _ProjectSourceFormRequestRequired(TypedDict):
    """Validated project source-form projection request payload."""

    projectId: str
    projectRoot: str
    sourcePath: str
    text: str


class _ProjectSourceFormRequest(_ProjectSourceFormRequestRequired, total=False):
    """Project source-form request with optional bounded search."""

    query: str


class _ProjectSourceFormUpdateRequired(TypedDict):
    """Required fields for one guided source update."""

    sourcePath: str
    values: dict[str, object]


class _ProjectSourceFormUpdate(_ProjectSourceFormUpdateRequired, total=False):
    """One guided source update with an optional unsaved base text."""

    text: str
    query: str


class _ProjectSourceFormUpdateBatchRequest(TypedDict):
    """Validated guided source update-batch plan request."""

    projectId: str
    projectRoot: str
    updates: list[_ProjectSourceFormUpdate]


class _ProjectLocalizationDraft(TypedDict):
    """One unsaved localization source draft."""

    sourcePath: str
    text: str


class _ProjectLocalizationWorkspaceRequired(TypedDict):
    """Required localization workspace request fields."""

    projectId: str
    projectRoot: str
    targetKind: str
    targetId: str


class _ProjectLocalizationWorkspaceRequest(_ProjectLocalizationWorkspaceRequired, total=False):
    """Validated localization workspace request payload."""

    family: str
    sourceRoot: str
    drafts: list[_ProjectLocalizationDraft]
    limit: int


class _ProjectLocalizationUpdateRequest(_ProjectLocalizationWorkspaceRequest):
    """Validated localization update-plan request payload."""

    operation: dict[str, object]


class _ProjectDraftRequest(TypedDict, total=False):
    """Validated project source-draft request payload."""

    projectId: str
    projectRoot: str
    sourceEdits: list[object] | None
    sourceRemovals: list[object] | None
    sourceReplacements: list[object] | None
    moduleRename: dict[str, object] | None


class _ModuleRemoveRequired(TypedDict):
    """Required module-remove request fields."""

    projectRoot: str
    moduleId: str


class _ModuleRemoveRequest(_ModuleRemoveRequired, total=False):
    """Validated destructive module-remove request payload."""

    sourceRoot: str | None


class _ProjectPreferredLanguageRequired(TypedDict):
    """Required project-language request fields."""

    projectRoot: str
    preferredLanguage: str


class _ProjectPreferredLanguageRequest(
    _ProjectPreferredLanguageRequired,
    total=False,
):
    """Validated transactional project-language request payload."""

    write: bool | None
    planHash: str | None


class _ModuleDuplicateRequired(TypedDict):
    """Required transactional module-duplicate request fields."""

    projectRoot: str
    moduleId: str
    objectId: str


class _ModuleDuplicateRequest(_ModuleDuplicateRequired, total=False):
    """Validated plan/apply module-duplicate request payload."""

    sourceRoot: str | None
    destinationSourceRoot: str | None
    identity: str | None
    write: bool | None
    planHash: str | None


class _ModuleCollectionRequired(TypedDict):
    """Required transactional module-collection request fields."""

    projectRoot: str
    moduleId: str


class _ModuleCollectionRequest(_ModuleCollectionRequired, total=False):
    """Validated plan/apply module-collection request payload."""

    collectionId: str | None
    sourceRoot: str | None
    write: bool | None
    planHash: str | None


class _ModuleActivityRequired(TypedDict):
    """Required transactional module-activity request fields."""

    projectRoot: str
    moduleId: str
    active: bool


class _ModuleActivityRequest(_ModuleActivityRequired, total=False):
    """Validated plan/apply module-activity request payload."""

    sourceRoot: str | None
    write: bool | None
    planHash: str | None


class _ModuleCreateBatchRequired(TypedDict):
    """Required transactional module create-batch request fields."""

    projectId: str
    projectRoot: str
    modules: list[dict[str, object]]


class _ModuleCreateBatchRequest(_ModuleCreateBatchRequired, total=False):
    """Validated transactional module create-batch request payload."""

    sourceRoot: str | None
    write: bool | None
    planHash: str | None


class _CollectionScaffoldRequired(TypedDict):
    """Required transactional collection-scaffold request fields."""

    projectRoot: str
    templateId: str
    collectionId: str
    values: dict[str, object]


class _CollectionScaffoldRequest(_CollectionScaffoldRequired, total=False):
    """Validated collection scaffold plan/apply request."""

    sourceRoot: str | None
    write: bool | None
    force: bool | None
    planHash: str | None


class _CollectionRenameRequired(TypedDict):
    """Required collection-rename request fields."""

    projectRoot: str
    collectionId: str
    targetId: str


class _CollectionRenameRequest(_CollectionRenameRequired, total=False):
    """Validated collection-rename request payload."""

    family: str | None
    sourceRoot: str | None


class _CollectionRemoveRequired(TypedDict):
    """Required transactional collection-removal request fields."""

    projectRoot: str
    collectionId: str


class _CollectionRemoveRequest(_CollectionRemoveRequired, total=False):
    """Validated collection-removal plan/apply request payload."""

    family: str | None
    sourceRoot: str | None
    write: bool | None
    planHash: str | None


_DesktopHelper = Callable[..., object]


def _loads_object(value: str, label: str) -> dict[str, object]:
    payload = loads_json(value)
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return cast(dict[str, object], payload)


def _validate_request_fields(request: Mapping[str, object], request_type: type, label: str) -> None:
    unknown = sorted(set(request) - set(request_type.__annotations__))
    if unknown:
        raise ValueError(f"{label} contains unsupported fields: {', '.join(unknown)}.")


def _optional_request_text(request: Mapping[str, object], key: str, label: str) -> str | None:
    value = request.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a JSON string or null.")
    return value.strip() or None


def _optional_request_bool(request: Mapping[str, object], key: str, label: str) -> bool | None:
    value = request.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a JSON boolean or null.")
    return value


def _desktop_state(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "desktop state request")
    _validate_request_fields(request, _DesktopStateRequest, "desktop state request")
    project_root = _optional_request_text(request, "projectRoot", "desktop state projectRoot")
    include_browser = _optional_request_bool(request, "includeBrowser", "desktop state includeBrowser")
    if include_browser is None:
        return desktop_state(project_root)
    return desktop_state(project_root, include_browser=include_browser)


def _project_browser(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "project browser request")
    _validate_request_fields(request, _ProjectBrowserRequest, "project browser request")
    project_root = _optional_request_text(request, "projectRoot", "project browser projectRoot")
    if project_root is None:
        raise ValueError("project browser projectRoot cannot be empty.")
    profile = _optional_request_text(request, "profile", "project browser profile")
    kind = _optional_request_text(request, "kind", "project browser kind")
    family = _optional_request_text(request, "family", "project browser family")
    module_id = _optional_request_text(request, "moduleId", "project browser moduleId")
    collection_id = _optional_request_text(request, "collectionId", "project browser collectionId")
    summary = _optional_request_bool(request, "summary", "project browser summary") or False
    if summary and (module_id is not None or collection_id is not None):
        raise ValueError("project browser summary cannot be combined with moduleId or collectionId.")
    project = open_project(project_root)
    if summary:
        return project.browser_summary(profile=profile, kind=kind, family=family)
    return project.browser(
        profile=profile,
        kind=kind,
        family=family,
        module_id=module_id,
        collection_id=collection_id,
    )


def _module_diagram(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "module diagram request")
    _validate_request_fields(
        request,
        _ModuleDiagramRequest,
        "module diagram request",
    )
    project_root = _optional_request_text(
        request,
        "projectRoot",
        "module diagram projectRoot",
    )
    family = _optional_request_text(
        request,
        "family",
        "module diagram family",
    )
    if project_root is None:
        raise ValueError("module diagram projectRoot cannot be empty.")
    if family is None:
        raise ValueError("module diagram family cannot be empty.")
    profile = _optional_request_text(
        request,
        "profile",
        "module diagram profile",
    )
    return open_project(project_root).module_diagram(
        family,
        profile=profile,
    )


def _module_diagram_edit(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "module diagram edit request")
    _validate_request_fields(
        request,
        _ModuleDiagramEditRequest,
        "module diagram edit request",
    )
    project_root = _optional_request_text(
        request,
        "projectRoot",
        "module diagram edit projectRoot",
    )
    family = _optional_request_text(
        request,
        "family",
        "module diagram edit family",
    )
    if project_root is None:
        raise ValueError("module diagram edit projectRoot cannot be empty.")
    if family is None:
        raise ValueError("module diagram edit family cannot be empty.")
    positions, edges = module_diagram_intents(
        request.get("positionIntents"),
        request.get("edgeIntents"),
    )
    nodes = module_diagram_node_intents(request.get("nodeIntents"))
    profile = _optional_request_text(
        request,
        "profile",
        "module diagram edit profile",
    )
    write = (
        _optional_request_bool(
            request,
            "write",
            "module diagram edit write",
        )
        or False
    )
    plan_hash = _optional_request_text(
        request,
        "planHash",
        "module diagram edit planHash",
    )
    return open_project(project_root).edit_module_diagram(
        family,
        profile=profile,
        position_intents=positions,
        edge_intents=edges,
        node_intents=nodes,
        write=write,
        plan_hash=plan_hash,
    )


def _collection_scaffold(request_json: str) -> dict[str, object]:
    """Plan or apply one Registry-backed collection template."""

    request = _loads_object(request_json, "collection scaffold request")
    _validate_request_fields(
        request,
        _CollectionScaffoldRequest,
        "collection scaffold request",
    )

    def required_text(key: str) -> str:
        value = _optional_request_text(
            request,
            key,
            f"collection scaffold {key}",
        )
        if value is None:
            raise ValueError(f"collection scaffold {key} cannot be empty.")
        return value

    values = request.get("values")
    if not isinstance(values, dict) or not all(isinstance(key, str) and key for key in values):
        raise ValueError("collection scaffold values must be a JSON object with " "non-empty string keys.")
    return open_project(required_text("projectRoot")).scaffold_collection(
        required_text("templateId"),
        required_text("collectionId"),
        source_root=_optional_request_text(
            request,
            "sourceRoot",
            "collection scaffold sourceRoot",
        ),
        values=values,
        write=(
            _optional_request_bool(
                request,
                "write",
                "collection scaffold write",
            )
            or False
        ),
        force=(
            _optional_request_bool(
                request,
                "force",
                "collection scaffold force",
            )
            or False
        ),
        plan_hash=_optional_request_text(
            request,
            "planHash",
            "collection scaffold planHash",
        ),
    )


def _rename_collection(request_json: str) -> dict[str, object]:
    """Rename one Registry-owned collection descriptor."""

    request = _loads_object(request_json, "collection rename request")
    _validate_request_fields(
        request,
        _CollectionRenameRequest,
        "collection rename request",
    )
    project_root = _optional_request_text(
        request,
        "projectRoot",
        "collection rename projectRoot",
    )
    collection_id = _optional_request_text(
        request,
        "collectionId",
        "collection rename collectionId",
    )
    target_id = _optional_request_text(
        request,
        "targetId",
        "collection rename targetId",
    )
    if project_root is None:
        raise ValueError("collection rename projectRoot cannot be empty.")
    if collection_id is None:
        raise ValueError("collection rename collectionId cannot be empty.")
    if target_id is None:
        raise ValueError("collection rename targetId cannot be empty.")
    return open_project(project_root).rename_collection(
        collection_id,
        target_id,
        family=_optional_request_text(
            request,
            "family",
            "collection rename family",
        ),
        source_root=_optional_request_text(
            request,
            "sourceRoot",
            "collection rename sourceRoot",
        ),
    )


def _remove_collection(request_json: str) -> dict[str, object]:
    """Plan or apply one guarded collection removal."""

    request = _loads_object(request_json, "collection remove request")
    _validate_request_fields(
        request,
        _CollectionRemoveRequest,
        "collection remove request",
    )
    project_root = _optional_request_text(
        request,
        "projectRoot",
        "collection remove projectRoot",
    )
    collection_id = _optional_request_text(
        request,
        "collectionId",
        "collection remove collectionId",
    )
    if project_root is None:
        raise ValueError("collection remove projectRoot cannot be empty.")
    if collection_id is None:
        raise ValueError("collection remove collectionId cannot be empty.")
    return open_project(project_root).remove_collection(
        collection_id,
        family=_optional_request_text(
            request,
            "family",
            "collection remove family",
        ),
        source_root=_optional_request_text(
            request,
            "sourceRoot",
            "collection remove sourceRoot",
        ),
        write=(
            _optional_request_bool(
                request,
                "write",
                "collection remove write",
            )
            or False
        ),
        plan_hash=_optional_request_text(
            request,
            "planHash",
            "collection remove planHash",
        ),
    )


def _project_catalog_query(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "project catalog query request")
    _validate_request_fields(request, _ProjectCatalogQueryRequest, "project catalog query request")
    project_root = _optional_request_text(request, "projectRoot", "project catalog query projectRoot")
    if project_root is None:
        raise ValueError("project catalog query projectRoot cannot be empty.")
    limit = request.get("limit")
    if limit is None:
        raise ValueError("project catalog query limit is required.")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= CATALOG_QUERY_MAX_LIMIT:
        raise ValueError(f"project catalog query limit must be an integer from 1 to {CATALOG_QUERY_MAX_LIMIT}.")
    offset = request.get("offset", CATALOG_QUERY_DEFAULT_OFFSET)
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("project catalog query offset must be a non-negative integer.")
    include_data = _optional_request_bool(request, "includeData", "project catalog query includeData")
    if include_data is None:
        include_data = CATALOG_QUERY_DEFAULT_INCLUDE_DATA
    if include_data and limit != CATALOG_QUERY_MAX_HYDRATED_LIMIT:
        raise ValueError(f"project catalog query hydrated requests must have limit {CATALOG_QUERY_MAX_HYDRATED_LIMIT}.")
    return open_project(project_root).catalog_query(
        entity=_optional_request_text(request, "entity", "project catalog query entity"),
        target_id=_optional_request_text(request, "targetId", "project catalog query targetId"),
        name=_optional_request_text(request, "name", "project catalog query name"),
        tag=_optional_request_text(request, "tag", "project catalog query tag"),
        limit=limit,
        offset=offset,
        include_data=include_data,
    )


def _project_catalog_status(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "project catalog status request")
    _validate_request_fields(request, _ProjectCatalogStatusRequest, "project catalog status request")
    project_root = _optional_request_text(request, "projectRoot", "project catalog status projectRoot")
    if project_root is None:
        raise ValueError("project catalog status projectRoot cannot be empty.")
    return open_project(project_root).catalog_status()


def _project_catalog_refresh(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "project catalog refresh request")
    _validate_request_fields(request, _ProjectCatalogRefreshRequest, "project catalog refresh request")
    project_root = _optional_request_text(request, "projectRoot", "project catalog refresh projectRoot")
    if project_root is None:
        raise ValueError("project catalog refresh projectRoot cannot be empty.")
    profile = _optional_request_text(request, "profile", "project catalog refresh profile")
    return catalog_refresh(open_project(project_root), profile=profile)


def _desktop_write_config_value(key: str, value_json: str) -> dict[str, object]:
    return desktop_write_config_value(key, loads_json(value_json))


def _desktop_write_app_config(config_json: str) -> None:
    desktop_write_app_config(_loads_object(config_json, "desktop app config"))


def _desktop_write_thumbnail_cache(project_root: str, cache_key: str, bytes_json: str) -> dict[str, object]:
    content = loads_json(bytes_json)
    if not isinstance(content, list):
        raise ValueError("thumbnail cache bytes must be a JSON array.")
    return desktop_write_thumbnail_cache(project_root, cache_key, content)


def _desktop_write_browser_cache(project_root: str, payload_json: str) -> dict[str, object]:
    return desktop_write_browser_cache(project_root, _loads_object(payload_json, "project browser cache"))


def _desktop_chat(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "desktop chat request")
    return desktop_chat(
        request.get("provider", ""),
        request.get("model", ""),
        request.get("gateway", ""),
        request.get("prompt", ""),
        request.get("role") or "chat",
        request.get("projectRoot") or "",
        request.get("sources") or [],
        key_env=request.get("keyEnv") or request.get("key_env"),
        base_url=request.get("baseUrl") or request.get("base_url"),
        preset=request.get("preset"),
    )


def _desktop_test_llm_route(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "desktop LLM route request")
    return desktop_test_llm_route(
        request.get("provider", ""),
        request.get("model", ""),
        request.get("gateway", ""),
        key_env=request.get("keyEnv") or request.get("key_env"),
        base_url=request.get("baseUrl") or request.get("base_url"),
        preset=request.get("preset"),
    )


def _desktop_run_hoi4(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "HOI4 launch request")
    return desktop_run_hoi4(
        project_root=request.get("projectRoot"),
        game_root=request.get("gameRoot"),
        mode=request.get("mode"),
    )


def _desktop_open_path(path: str, target_json: str) -> list[str]:
    target = loads_json(target_json)
    if target is not None and not isinstance(target, str):
        raise ValueError("open path target must be a JSON string or null.")
    return desktop_open_path(path, target)


def _desktop_project_build_args(request_json: str, progress_jsonl: str) -> list[str]:
    request = _loads_object(request_json, "desktop build request")
    strict_metadata = request["strictMetadata"] if "strictMetadata" in request else request.get("strict_metadata")
    tokens = desktop_project_build_command(
        request.get("projectRoot"),
        mode=request.get("mode"),
        profile=request.get("profile"),
        strict_metadata=strict_metadata,
        parallelism=request.get("parallelism"),
        target=request.get("target"),
        progress_jsonl=progress_jsonl or None,
    )
    if tuple(tokens[: len(_BUILD_COMMAND_PREFIX)]) != _BUILD_COMMAND_PREFIX:
        raise RuntimeError("desktop build planner returned an unsupported runtime prefix.")
    return tokens[len(_BUILD_COMMAND_PREFIX) :]


def _project_inspect(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "project inspection request")
    project_root = request.get("projectRoot")
    if not isinstance(project_root, str) or not project_root.strip():
        raise ValueError("project root cannot be empty.")
    kind = request.get("kind")
    if not isinstance(kind, str) or not kind.strip():
        raise ValueError("project inspection kind cannot be empty.")
    source_filters = request.get("filters", {})
    if source_filters is None:
        source_filters = {}
    if not isinstance(source_filters, Mapping):
        raise ValueError("project inspection filters must be a JSON object.")
    filters: dict[str, object] = {}
    aliases: dict[str, str] = {}
    for source_name, value in source_filters.items():
        normalized_name = snake(source_name)
        if not normalized_name:
            raise ValueError(f"project inspection filter name {source_name!r} must normalize to non-empty snake_case.")
        if previous_name := aliases.get(normalized_name):
            raise ValueError(f"project inspection filter aliases collide: {previous_name!r} and {source_name!r} both normalize to {normalized_name!r}.")
        aliases[normalized_name] = str(source_name)
        filters[normalized_name] = value
    return open_project(project_root.strip()).inspect(kind.strip(), **filters)


def _create_module_draft(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "module draft request")
    project = open_project(request.get("projectRoot") or "")
    return create_module_draft(
        project_id=project.project_id,
        family_id=request.get("familyId") or "",
        request={
            "project_root": str(project.root),
            "template_id": request.get("templateId"),
            "object_id": request.get("objectId"),
            "values": request.get("values"),
            "write": bool(request.get("write")),
            "force": bool(request.get("force")),
        },
    )


def _create_module_batch(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "module create-batch request")
    _validate_request_fields(request, _ModuleCreateBatchRequest, "module create-batch request")
    project_id = _optional_request_text(request, "projectId", "module create-batch projectId")
    if project_id is None:
        raise ValueError("module create-batch projectId cannot be empty.")
    project_root = _optional_request_text(request, "projectRoot", "module create-batch projectRoot")
    if project_root is None:
        raise ValueError("module create-batch projectRoot cannot be empty.")
    modules = request.get("modules")
    if not isinstance(modules, list):
        raise ValueError("module create-batch modules must be a JSON array.")
    return create_module_batch(
        request={
            "project_id": project_id,
            "project_root": project_root,
            "modules": modules,
            "source_root": _optional_request_text(request, "sourceRoot", "module create-batch sourceRoot"),
            "write": _optional_request_bool(request, "write", "module create-batch write") or False,
            "plan_hash": _optional_request_text(request, "planHash", "module create-batch planHash"),
        }
    )


def _apply_project_draft(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "project draft request")
    _validate_request_fields(request, _ProjectDraftRequest, "project draft request")
    mutations = normalize_project_draft_mutations(
        source_edits=request.get("sourceEdits"),
        source_removals=request.get("sourceRemovals"),
        source_replacements=(request.get("sourceReplacements") if request.get("sourceReplacements") is not None else []),
        module_rename=request.get("moduleRename"),
        allow_snake_case=False,
    )
    return apply_project_draft(
        project_id=request.get("projectId") or "",
        request={
            "project_root": request.get("projectRoot") or "",
            **mutations,
        },
    )


def _project_source_form(request_json: str) -> dict[str, object] | None:
    request = _loads_object(request_json, "project source form request")
    _validate_request_fields(request, _ProjectSourceFormRequest, "project source form request")
    project_id = _optional_request_text(request, "projectId", "project source form projectId")
    if project_id is None:
        raise ValueError("project source form projectId cannot be empty.")
    project_root = _optional_request_text(request, "projectRoot", "project source form projectRoot")
    if project_root is None:
        raise ValueError("project source form projectRoot cannot be empty.")
    source_path = _optional_request_text(request, "sourcePath", "project source form sourcePath")
    if source_path is None:
        raise ValueError("project source form sourcePath cannot be empty.")
    text = request.get("text")
    if not isinstance(text, str):
        raise ValueError("project source form text must be a JSON string.")
    query = request.get("query")
    if query is not None and not isinstance(query, str):
        raise ValueError("project source form query must be a JSON string.")
    return read_project_source_form(
        project_id=project_id,
        request={
            "project_root": project_root,
            "path": source_path,
            "text": text,
            **({"query": query} if query is not None else {}),
        },
    )


def _project_source_form_update_batch(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "project source-form update-batch request")
    _validate_request_fields(
        request,
        _ProjectSourceFormUpdateBatchRequest,
        "project source-form update-batch request",
    )
    project_id = _optional_request_text(
        request,
        "projectId",
        "project source-form update-batch projectId",
    )
    if project_id is None:
        raise ValueError("project source-form update-batch projectId cannot be empty.")
    project_root = _optional_request_text(
        request,
        "projectRoot",
        "project source-form update-batch projectRoot",
    )
    if project_root is None:
        raise ValueError("project source-form update-batch projectRoot cannot be empty.")
    updates = request.get("updates")
    if not isinstance(updates, list):
        raise ValueError("project source-form update-batch updates must be a JSON array.")

    planned_updates: list[dict[str, object]] = []
    for index, update in enumerate(updates):
        if not isinstance(update, dict):
            raise ValueError(f"project source-form update-batch row {index} must be an object.")
        _validate_request_fields(
            update,
            _ProjectSourceFormUpdate,
            f"project source-form update-batch row {index}",
        )
        source_path = _optional_request_text(
            update,
            "sourcePath",
            f"project source-form update-batch row {index} sourcePath",
        )
        if source_path is None:
            raise ValueError(f"project source-form update-batch row {index} sourcePath " "cannot be empty.")
        values = update.get("values")
        if not isinstance(values, dict):
            raise ValueError(f"project source-form update-batch row {index} values must " "be a JSON object.")
        text = update.get("text")
        if text is not None and not isinstance(text, str):
            raise ValueError(f"project source-form update-batch row {index} text must be " "a JSON string.")
        query = update.get("query")
        if query is not None and not isinstance(query, str):
            raise ValueError(f"project source-form update-batch row {index} query must be " "a JSON string.")
        planned_updates.append(
            {
                "source_path": source_path,
                "values": values,
                **({"text": text} if text is not None else {}),
                **({"query": query} if query is not None else {}),
            }
        )

    return plan_project_source_form_updates(
        project_id=project_id,
        request={
            "project_root": project_root,
            "updates": planned_updates,
        },
    )


def _project_localization_workspace(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "project localization workspace request")
    _validate_request_fields(request, _ProjectLocalizationWorkspaceRequest, "project localization workspace request")
    project_id, normalized = _project_localization_request(request, include_operation=False)
    return read_project_localization_workspace(project_id=project_id, request=normalized)


def _project_localization_update(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "project localization update request")
    _validate_request_fields(request, _ProjectLocalizationUpdateRequest, "project localization update request")
    project_id, normalized = _project_localization_request(request, include_operation=True)
    return plan_project_localization_update(project_id=project_id, request=normalized)


def _project_localization_request(
    request: Mapping[str, object],
    *,
    include_operation: bool,
) -> tuple[str, dict[str, object]]:
    project_id = _optional_request_text(request, "projectId", "project localization projectId")
    project_root = _optional_request_text(request, "projectRoot", "project localization projectRoot")
    target_kind = _optional_request_text(
        request,
        "targetKind",
        "project localization targetKind",
    )
    target_id = _optional_request_text(
        request,
        "targetId",
        "project localization targetId",
    )
    if project_id is None or project_root is None or target_kind is None or target_id is None:
        raise ValueError("Project localization projectId, projectRoot, targetKind, and " "targetId cannot be empty.")
    if target_kind not in {"module", "collection"}:
        raise ValueError("Project localization targetKind must be 'module' or 'collection'.")
    drafts = request.get("drafts", [])
    if not isinstance(drafts, list):
        raise ValueError("Project localization drafts must be a JSON array.")
    normalized_drafts: list[dict[str, object]] = []
    for index, draft in enumerate(drafts):
        if not isinstance(draft, dict):
            raise ValueError(f"Project localization draft row {index} must be an object.")
        _validate_request_fields(draft, _ProjectLocalizationDraft, f"project localization draft row {index}")
        source_path = _optional_request_text(draft, "sourcePath", f"project localization draft row {index} sourcePath")
        text = draft.get("text")
        if source_path is None or not isinstance(text, str):
            raise ValueError(f"Project localization draft row {index} requires sourcePath and text.")
        normalized_drafts.append({"source_path": source_path, "text": text})
    normalized: dict[str, object] = {
        "project_root": project_root,
        "target_kind": target_kind,
        "target_id": target_id,
        "drafts": normalized_drafts,
    }
    family = _optional_request_text(request, "family", "project localization family")
    if family is not None:
        normalized["family"] = family
    source_root = _optional_request_text(request, "sourceRoot", "project localization sourceRoot")
    if source_root is not None:
        normalized["source_root"] = source_root
    limit = request.get("limit")
    if limit is not None:
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError("Project localization limit must be an integer.")
        normalized["limit"] = limit
    if include_operation:
        operation = request.get("operation")
        if not isinstance(operation, dict):
            raise ValueError("Project localization operation must be an object.")
        normalized["operation"] = operation
    return project_id, normalized


def _module_batch_request(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "module batch request")
    project = open_project(request.get("projectRoot") or "")
    encoding = request["encoding"] if request.get("encoding") is not None else "utf-8"
    return project.module_batch_edit_request(
        request.get("edits") or [],
        create=bool(request.get("create")),
        encoding=encoding,
    )


def _rename_module(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "module rename request")
    project_root = request.get("projectRoot")
    if not isinstance(project_root, str) or not project_root.strip():
        raise ValueError("project root cannot be empty.")
    module_id = request.get("moduleId")
    if not isinstance(module_id, str) or not module_id.strip():
        raise ValueError("module id cannot be empty.")
    object_id = request.get("objectId")
    if not isinstance(object_id, str) or not object_id.strip():
        raise ValueError("object id cannot be empty.")
    source_root = request.get("sourceRoot")
    if isinstance(source_root, str) and not source_root.strip():
        source_root = None
    title = request.get("title")
    if title is not None and (not isinstance(title, str) or not title.strip()):
        raise ValueError("module title must be a non-empty string when provided.")
    return open_project(project_root.strip()).rename_module(
        module_id.strip(),
        object_id.strip(),
        source_root=source_root,
        title=title,
    )


def _set_project_preferred_language(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "project preferred-language request")
    _validate_request_fields(
        request,
        _ProjectPreferredLanguageRequest,
        "project preferred-language request",
    )
    project_root = _optional_request_text(
        request,
        "projectRoot",
        "project preferred-language projectRoot",
    )
    if project_root is None:
        raise ValueError("project preferred-language projectRoot cannot be empty.")
    preferred_language = _optional_request_text(
        request,
        "preferredLanguage",
        "project preferred-language preferredLanguage",
    )
    if preferred_language is None:
        raise ValueError("project preferred-language preferredLanguage cannot be empty.")
    write = _optional_request_bool(
        request,
        "write",
        "project preferred-language write",
    )
    plan_hash = _optional_request_text(
        request,
        "planHash",
        "project preferred-language planHash",
    )
    return open_project(project_root).set_preferred_language(
        preferred_language,
        write=write or False,
        plan_hash=plan_hash,
    )


def _duplicate_module(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "module duplicate request")
    _validate_request_fields(request, _ModuleDuplicateRequest, "module duplicate request")
    project_root = _optional_request_text(request, "projectRoot", "module duplicate projectRoot")
    if project_root is None:
        raise ValueError("module duplicate projectRoot cannot be empty.")
    module_id = _optional_request_text(request, "moduleId", "module duplicate moduleId")
    if module_id is None:
        raise ValueError("module duplicate moduleId cannot be empty.")
    object_id = _optional_request_text(request, "objectId", "module duplicate objectId")
    if object_id is None:
        raise ValueError("module duplicate objectId cannot be empty.")
    source_root = _optional_request_text(request, "sourceRoot", "module duplicate sourceRoot")
    destination_source_root = _optional_request_text(
        request,
        "destinationSourceRoot",
        "module duplicate destinationSourceRoot",
    )
    identity = _optional_request_text(request, "identity", "module duplicate identity") or "rewrite"
    write = _optional_request_bool(request, "write", "module duplicate write") or False
    plan_hash = _optional_request_text(request, "planHash", "module duplicate planHash")
    return open_project(project_root).duplicate_module(
        module_id,
        object_id,
        source_root=source_root,
        destination_source_root=destination_source_root,
        identity=identity,
        write=write,
        plan_hash=plan_hash,
    )


def _set_module_collection(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "module collection request")
    _validate_request_fields(
        request,
        _ModuleCollectionRequest,
        "module collection request",
    )
    project_root = _optional_request_text(
        request,
        "projectRoot",
        "module collection projectRoot",
    )
    module_id = _optional_request_text(
        request,
        "moduleId",
        "module collection moduleId",
    )
    if project_root is None:
        raise ValueError("module collection projectRoot cannot be empty.")
    if module_id is None:
        raise ValueError("module collection moduleId cannot be empty.")
    collection_id = _optional_request_text(
        request,
        "collectionId",
        "module collection collectionId",
    )
    source_root = _optional_request_text(
        request,
        "sourceRoot",
        "module collection sourceRoot",
    )
    write = _optional_request_bool(
        request,
        "write",
        "module collection write",
    )
    plan_hash = _optional_request_text(
        request,
        "planHash",
        "module collection planHash",
    )
    return open_project(project_root).set_module_collection(
        module_id,
        collection_id,
        source_root=source_root,
        write=write or False,
        plan_hash=plan_hash,
    )


def _set_module_active(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "module activity request")
    _validate_request_fields(
        request,
        _ModuleActivityRequest,
        "module activity request",
    )
    project_root = _optional_request_text(
        request,
        "projectRoot",
        "module activity projectRoot",
    )
    module_id = _optional_request_text(
        request,
        "moduleId",
        "module activity moduleId",
    )
    active = _optional_request_bool(
        request,
        "active",
        "module activity active",
    )
    if project_root is None:
        raise ValueError("module activity projectRoot cannot be empty.")
    if module_id is None:
        raise ValueError("module activity moduleId cannot be empty.")
    if active is None:
        raise ValueError("module activity active must be a JSON boolean.")
    source_root = _optional_request_text(
        request,
        "sourceRoot",
        "module activity sourceRoot",
    )
    write = _optional_request_bool(
        request,
        "write",
        "module activity write",
    )
    plan_hash = _optional_request_text(
        request,
        "planHash",
        "module activity planHash",
    )
    return open_project(project_root).set_module_active(
        module_id,
        active,
        source_root=source_root,
        write=write or False,
        plan_hash=plan_hash,
    )


def _remove_module(request_json: str) -> dict[str, object]:
    request = _loads_object(request_json, "module remove request")
    _validate_request_fields(request, _ModuleRemoveRequest, "module remove request")
    project_root = _optional_request_text(request, "projectRoot", "module remove projectRoot")
    if project_root is None:
        raise ValueError("module remove projectRoot cannot be empty.")
    module_id = _optional_request_text(request, "moduleId", "module remove moduleId")
    if module_id is None:
        raise ValueError("module remove moduleId cannot be empty.")
    source_root = _optional_request_text(request, "sourceRoot", "module remove sourceRoot")
    return open_project(project_root).remove_module(module_id, source_root=source_root, write=True)


def _desktop_write_chat_profile(profile_id: str, profile_json: str, project_root: str) -> dict[str, object]:
    return desktop_write_chat_profile(profile_id, _loads_object(profile_json, "desktop chat profile"), project_root)


def _desktop_reset_chat_profile(profile_id: str, project_root: str) -> dict[str, object]:
    return desktop_reset_chat_profile(profile_id, project_root)


def _desktop_install_project_package(
    archive_path: str,
    destination_root: str,
    desktop_version: str,
) -> dict[str, object]:
    catalog = desktop_project_package_catalog()
    expected_version = catalog["desktop_version"]
    if desktop_version != expected_version:
        raise ValueError(
            f"Project-package catalog targets ParaDev Desktop {expected_version}, "
            f"but the running desktop is {desktop_version}. Reinstall a matching ParaDev release."
        )
    return desktop_install_project_package(archive_path, destination_root)


_HELPERS: Mapping[str, _DesktopHelper] = MappingProxyType(
    {
        "apply_project_draft": _apply_project_draft,
        "collection_remove": _remove_collection,
        "collection_rename": _rename_collection,
        "collection_scaffold": _collection_scaffold,
        "create_module_batch": _create_module_batch,
        "create_module_draft": _create_module_draft,
        "desktop_chat": _desktop_chat,
        "desktop_chat_profiles": desktop_chat_profiles,
        "desktop_dependency_status": desktop_dependency_status,
        "desktop_install_dependency": desktop_install_dependency,
        "desktop_install_project_package": _desktop_install_project_package,
        "desktop_hoi4_launch_readiness": desktop_hoi4_launch_readiness,
        "desktop_open_path": _desktop_open_path,
        "desktop_path_status": desktop_path_status,
        "desktop_project_build_command": _desktop_project_build_args,
        "desktop_read_app_config": desktop_read_app_config,
        "desktop_read_binary_source": desktop_read_binary_source,
        "desktop_read_config_value": desktop_read_config_value,
        "desktop_read_text_source": desktop_read_text_source,
        "desktop_read_thumbnail_cache": desktop_read_thumbnail_cache,
        "desktop_reset_chat_profile": _desktop_reset_chat_profile,
        "desktop_run_hoi4": _desktop_run_hoi4,
        "desktop_state": _desktop_state,
        "desktop_project_package_catalog": desktop_project_package_catalog,
        "desktop_test_llm_route": _desktop_test_llm_route,
        "desktop_write_app_config": _desktop_write_app_config,
        "desktop_write_browser_cache": _desktop_write_browser_cache,
        "desktop_write_chat_profile": _desktop_write_chat_profile,
        "desktop_write_config_value": _desktop_write_config_value,
        "desktop_write_thumbnail_cache": _desktop_write_thumbnail_cache,
        "module_batch_request": _module_batch_request,
        "module_diagram": _module_diagram,
        "module_diagram_edit": _module_diagram_edit,
        "duplicate_module": _duplicate_module,
        "module_collection_set": _set_module_collection,
        "module_activity_set": _set_module_active,
        "project_source_form": _project_source_form,
        "project_source_form_update_batch": _project_source_form_update_batch,
        "project_localization_workspace": _project_localization_workspace,
        "project_localization_update": _project_localization_update,
        "remove_module": _remove_module,
        "project_inspect": _project_inspect,
        "project_browser": _project_browser,
        "project_catalog_query": _project_catalog_query,
        "project_catalog_status": _project_catalog_status,
        "project_catalog_refresh": _project_catalog_refresh,
        "project_preferred_language": _set_project_preferred_language,
        "read_project_browser_cache": read_project_browser_cache,
        "rename_module": _rename_module,
    }
)


def _backend_info() -> dict[str, str]:
    return {
        "schema": DESKTOP_BACKEND_INFO_SCHEMA,
        "protocol": DESKTOP_BACKEND_PROTOCOL,
        "paradevVersion": paradev.__version__,
        "heavenbaseVersion": heavenbase.__version__,
        "pythonVersion": platform.python_version(),
        "platform": sys.platform,
        "platformVersion": platform.version(),
        "machine": platform.machine(),
    }


def _read_call(source: TextIO) -> _DesktopCallRequest:
    encoded = source.read()
    if not encoded.strip():
        raise ValueError("desktop-call requires a JSON request on stdin.")
    payload = loads_json(encoded)
    if not isinstance(payload, dict):
        raise ValueError("desktop-call request must be a JSON object.")
    unknown = sorted(set(payload) - _DesktopCallRequest.__required_keys__)
    if unknown:
        raise ValueError(f"desktop-call request contains unsupported fields: {', '.join(unknown)}.")
    missing = sorted(_DesktopCallRequest.__required_keys__ - set(payload))
    if missing:
        raise ValueError(f"desktop-call request is missing fields: {', '.join(missing)}.")
    protocol = payload["protocol"]
    if protocol != DESKTOP_BACKEND_PROTOCOL:
        raise ValueError(f"unsupported desktop backend protocol: {protocol!r}.")
    operation = payload["operation"]
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("desktop-call operation must be a non-empty string.")
    args = payload["args"]
    if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
        raise ValueError("desktop-call args must be a JSON array of strings.")
    return {"protocol": protocol, "operation": operation, "args": args}


def _desktop_call(source: TextIO) -> object:
    request = _read_call(source)
    helper = _HELPERS.get(request["operation"])
    if helper is None:
        raise ValueError(f"unsupported desktop operation: {request['operation']!r}.")
    with redirect_stdout(sys.stderr):
        return helper(*request["args"])


def _emit_json(value: object) -> None:
    sys.stdout.write(f"{dumps_json(value, compact=True)}\n")


def _emit_error(error: Exception) -> int:
    detail = str(error).strip() or type(error).__name__
    sys.stderr.write(f"{detail}\n")
    return 1


def _configure_protocol_stdio() -> None:
    """Use strict UTF-8 for every packaged backend stdin/stdout stream."""

    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="strict")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the packaged desktop backend or forward to the ParaDev CLI.

    Args:
        argv (Sequence[str] | None): Optional arguments without the executable
            name. `backend-info` reports the packaged runtime, `desktop-call`
            reads one versioned request from stdin, and every other argument
            list is forwarded unchanged to the normal ParaDev CLI.

    Returns:
        int: Process exit code. Desktop protocol failures return `1`; forwarded
        CLI commands retain their normal exit behavior.
    """

    args = list(sys.argv[1:] if argv is None else argv)
    command = args[0] if args else None
    _configure_protocol_stdio()
    if command not in {"backend-info", "desktop-call"}:
        from paradev.cli import main as cli_main

        return cli_main(args)
    if len(args) != 1:
        return _emit_error(ValueError(f"{command} does not accept command-line arguments."))
    try:
        payload = _backend_info() if command == "backend-info" else _desktop_call(sys.stdin)
        _emit_json(payload)
    except Exception as error:
        return _emit_error(error)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
