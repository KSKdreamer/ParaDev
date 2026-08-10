"""Typer and Rich CLI contract."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from typing_extensions import TypedDict

from paradev._api_table import api_indexed_table, api_table_selection
from paradev._api_table_markdown import (
    api_indexed_reference_sections,
    api_reference_markdown,
)
from paradev.sdk import FRONTEND_API_SELECTORS, get_frontend_api_binding_index, get_project_inspection_contract
from paradev.surfaces.api_catalog import API_CATALOG_SOURCE_ROWS

CLI_API_TABLE_SCHEMA = "paradev.cli.api-table.v1"
TEMPLATE_FILTERS = ["template_id", "family", "source", "authoring_ready", "diagnostic_code"]
_CLI_API_REFERENCE_PAGE = "docs/user-manual/cli-api-reference.md"
_CLI_API_TEST_ANCHOR = "tests/test_architecture.py::test_cli_api_table_lists_command_contract"
_CLI_COMMAND_GROUPS = {"config", "hb", "lsp", "mcp"}
_CLI_API_INDEX_NAMES = ("feature_index", "kind_index", "adapter_index", "frontend_operation_index")
_STANDARD_API_REFERENCE_FILTERS = ["symbol", "index_name", "key"]
_STANDARD_API_REFERENCE_PROJECTIONS = ["symbol", "index", "key", "markdown"]
_CLI_API_STANDARD_FIELDS = (
    "symbol",
    "kind",
    "layer",
    "feature",
    "command_key",
    "adapter",
    "filters",
    "projections",
    "returns",
    "raises",
    "frontend_operation_ids",
    "registry_seam",
    "doc_page",
    "test_anchor",
)


class CliApiRow(TypedDict):
    """One CLI command contract table row."""

    symbol: str
    kind: str
    layer: str
    feature: str
    command_key: str
    adapter: str
    filters: list[str]
    projections: list[str]
    returns: str
    raises: str
    registry_seam: str
    surface: str
    frontend_operation_ids: list[str]
    doc_page: str
    test_anchor: str


class CliApiTable(TypedDict):
    """Generated API-standard table for Typer CLI commands."""

    schema: str
    row_count: int
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    adapter_index: dict[str, list[str]]
    frontend_operation_index: dict[str, list[str]]
    rows: list[CliApiRow]


def get_cli_contract() -> dict[str, object]:
    """Return the CLI surface contract."""

    inspection_contract = get_project_inspection_contract()
    contract: dict[str, object] = {
        "identifier": "cli",
        "runtime": "python-typer-rich",
        "status": "scaffold",
        "commands": [
            "architecture",
            "frontend-api",
            "api-catalog",
            "package-api",
            "config-api",
            "gui-api",
            "desktop-api",
            "games-api",
            "surfaces-api",
            "sdk-api",
            "project-api",
            "templates-api",
            "copy-roots-api",
            "project-facade-api",
            "localization-api",
            "build-api",
            "pdx-api",
            "pdx-core-api",
            "lsp-api",
            "lsp-server-api",
            "catalog-api",
            "hb-api",
            "rest-api",
            "rest-facade-api",
            "mcp-api",
            "cli-api",
            "parse",
            "format",
            "new",
            "projects",
            "desktop-state",
            "project-browser",
            "project-find",
            "project-rename",
            "project-language",
            "module-rename",
            "module-duplicate",
            "module-collection-set",
            "module-activity-set",
            "module-metadata-clean",
            "module-diagram",
            "module-diagram-edit",
            "module-remove",
            "module-file",
            "module-edit",
            "module-batch-create",
            "module-batch-edit",
            "module-batch-request",
            "collection-file",
            "collection-edit",
            "collection-scaffold",
            "collection-create",
            "collection-rename",
            "collection-remove",
            "templates",
            "authoring-path",
            "authoring-plan",
            "scaffold",
            "draft-apply",
            "build",
            "summary",
            "manifests",
            "inspections",
            "modules",
            "collections",
            "artifacts",
            "localization",
            "sources",
            "source-slots",
            "assets",
            "sprites",
            "diagnostics",
            "source-map",
            "dependencies",
            "build-graph",
            "build-explain",
            "families",
            "project",
            "config",
            "config get",
            "config list",
            "config set",
            "config unset",
            "config scopes",
            "config history",
            "hb",
            "hb catalog-preview",
            "hb catalog-smoke",
            "hb catalog-write",
            "hb catalog-refresh",
            "hb catalog-query",
            "mcp",
            "mcp serve",
            "lsp",
            "lsp serve",
            "lsp diagnostics",
            "lsp formatting",
            "lsp symbols",
            "lsp hover",
            "lsp completion",
            "lsp keywords",
            "lsp semantic-tokens",
            "setup",
            "init",
            "pj",
        ],
        "adapters": {
            "architecture": "get_architecture_spec",
            "architecture --api-table": "get_architecture_api_selection",
            "architecture --api-table --symbol": "get_architecture_api_selection",
            "architecture --api-table --index --key": "get_architecture_api_selection",
            "architecture --api-table-markdown": "render_architecture_api_reference_markdown",
            "architecture --surface-contract": "get_surface_contract_selection",
            "architecture --surface-contracts": "get_surface_contract_selection",
            "architecture --surface-contracts-markdown": "render_surface_contract_reference_markdown",
            "frontend-api": "get_frontend_api_selection",
            "frontend-api --workspace": "get_frontend_api_workspace",
            "frontend-api --operation": "get_frontend_api_selection",
            "frontend-api --group": "get_frontend_api_selection",
            "frontend-api --operation --form": "get_frontend_api_selection",
            "frontend-api --index --key": "get_frontend_api_selection",
            "frontend-api --operation --action": "get_frontend_api_action",
            "frontend-api --operation --option-field --values-json": "resolve_frontend_api_options",
            "frontend-api --operation --values-json": "normalize_frontend_api_inputs",
            "frontend-api --operation --values-json --rest-request": "plan_frontend_api_rest_request",
            "frontend-api --binding-surface --binding-key": "get_frontend_api_binding_lookup",
            "frontend-api --markdown": "render_frontend_api_reference_markdown",
            "frontend-api --sdk-cli-markdown": "render_frontend_api_sdk_cli_markdown",
            "frontend-api --typescript": "render_frontend_api_typescript",
            "api-catalog": "get_api_catalog_selection",
            "api-catalog --reference": "get_api_catalog_selection",
            "api-catalog --index --key": "get_api_catalog_selection",
            "api-catalog --markdown": "render_api_catalog_reference_markdown",
            "package-api": "get_package_api_table",
            "package-api --markdown": "render_package_api_reference_markdown",
            "config-api": "get_config_api_table",
            "config-api --markdown": "render_config_api_reference_markdown",
            "gui-api": "get_gui_api_table",
            "gui-api --markdown": "render_gui_api_reference_markdown",
            "desktop-api": "get_desktop_api_table",
            "desktop-api --markdown": "render_desktop_api_reference_markdown",
            "desktop-api --typescript": "render_desktop_typescript",
            "games-api": "get_games_api_table",
            "games-api --markdown": "render_games_api_reference_markdown",
            "surfaces-api": "get_surfaces_api_table",
            "surfaces-api --markdown": "render_surfaces_api_reference_markdown",
            "sdk-api": "get_sdk_api_table",
            "sdk-api --markdown": "render_sdk_api_reference_markdown",
            "project-api": "get_project_api_table",
            "project-api --markdown": "render_project_api_reference_markdown",
            "templates-api": "get_templates_api_table",
            "templates-api --markdown": "render_templates_api_reference_markdown",
            "copy-roots-api": "get_copy_roots_api_table",
            "copy-roots-api --markdown": "render_copy_roots_api_reference_markdown",
            "project-facade-api": "get_project_facade_api_table",
            "project-facade-api --markdown": "render_project_facade_api_reference_markdown",
            "localization-api": "get_localization_api_table",
            "localization-api --markdown": "render_localization_api_reference_markdown",
            "build-api": "get_build_api_table",
            "build-api --markdown": "render_build_api_reference_markdown",
            "pdx-api": "get_pdx_api_table",
            "pdx-api --markdown": "render_pdx_api_reference_markdown",
            "pdx-core-api": "get_pdx_core_api_table",
            "pdx-core-api --markdown": "render_pdx_core_api_reference_markdown",
            "lsp-api": "get_lsp_api_table",
            "lsp-api --markdown": "render_lsp_api_reference_markdown",
            "lsp-server-api": "get_lsp_server_api_table",
            "lsp-server-api --markdown": "render_lsp_server_api_reference_markdown",
            "catalog-api": "get_catalog_api_table",
            "catalog-api --markdown": "render_catalog_api_reference_markdown",
            "hb-api": "get_hb_api_table",
            "hb-api --markdown": "render_hb_api_reference_markdown",
            "rest-api": "get_rest_api_table",
            "rest-api --markdown": "render_rest_api_reference_markdown",
            "rest-facade-api": "get_rest_facade_api_table",
            "rest-facade-api --markdown": "render_rest_facade_api_reference_markdown",
            "mcp-api": "get_mcp_api_table",
            "mcp-api --markdown": "render_mcp_api_reference_markdown",
            "cli-api": "get_cli_api_table",
            "cli-api --markdown": "render_cli_api_reference_markdown",
            "parse": "parse_pdx_file",
            "format": "format_pdx_file",
            "new": "Project.create",
            "projects": "registered_projects",
            "desktop-state": "desktop_state",
            "project-browser": "Project.browser",
            "project": "Project.to_view",
            "build": "Project.build",
            "project-find": "Project.find",
            "project-rename": "Project.rename",
            "project-language": "Project.set_preferred_language",
            "module-rename": "Project.rename_module",
            "module-duplicate": "Project.duplicate_module",
            "module-collection-set": "Project.set_module_collection",
            "module-activity-set": "Project.set_module_active",
            "module-metadata-clean": "Project.clean_module_metadata",
            "module-diagram": "Project.module_diagram",
            "module-diagram-edit": "Project.edit_module_diagram",
            "module-remove": "Project.remove_module",
            "module-file": "Project.read_module_file",
            "module-edit": "Project.write_module_file",
            "module-batch-create": "Project.create_modules",
            "module-batch-edit": "Project.write_module_files",
            "module-batch-request": "Project.module_batch_edit_request",
            "collection-file": "Project.read_collection_file",
            "collection-edit": "Project.write_collection_file",
            "collection-scaffold": "Project.scaffold_collection",
            "collection-create": "Project.create_collection",
            "collection-rename": "Project.rename_collection",
            "collection-remove": "Project.remove_collection",
            "templates": "Project.templates",
            "authoring-path": "Project.authoring_path",
            "authoring-plan": "Project.authoring_plan",
            "scaffold": "Project.scaffold_module",
            "draft-apply": "Project.apply_source_draft",
            "summary": "Project.inspect('summary')",
            "manifests": "Project.inspect('manifests')",
            "inspections": "get_project_inspection_selection",
            "inspections --kind": "get_project_inspection_selection",
            "inspections --index --key": "get_project_inspection_selection",
            "inspections --markdown": "render_project_inspection_reference_markdown",
            "modules": "Project.inspect('modules')",
            "collections": "Project.inspect('collections')",
            "artifacts": "Project.inspect('artifacts')",
            "localization": "Project.inspect('localization')",
            "sources": "Project.inspect('sources')",
            "source-slots": "Project.inspect('source-slots')",
            "assets": "Project.inspect('assets')",
            "sprites": "Project.inspect('sprites')",
            "diagnostics": "Project.inspect('diagnostics')",
            "source-map": "Project.inspect('source-map')",
            "dependencies": "Project.inspect('dependencies')",
            "build-graph": "Project.inspect('build-graph')",
            "build-explain": "Project.inspect('build-explain')",
            "families": "Project.inspect('families')",
            "hb catalog-preview": "Project.inspect('catalog-preview')",
            "hb catalog-smoke": "catalog_smoke",
            "hb catalog-write": "catalog_write",
            "hb catalog-refresh": "catalog_refresh",
            "hb catalog-query": "Project.inspect('catalog-query')",
            "mcp serve": "serve_authoring_mcp_stdio",
            "lsp serve": "serve_pdx_lsp_stdio",
            "lsp diagnostics": "diagnose_pdx_lsp_text",
            "lsp formatting": "format_pdx_lsp_text",
            "lsp symbols": "document_symbols_pdx_lsp_text",
            "lsp hover": "hover_pdx_lsp_text",
            "lsp completion": "complete_pdx_lsp_text",
            "lsp keywords": "hoi4_keyword_dataset",
            "lsp semantic-tokens": "semantic_tokens_pdx_lsp_text",
            "config get": "config_get",
            "config list": "config_list",
            "config set": "config_set",
            "config unset": "config_unset",
            "config scopes": "config_scopes",
            "config history": "config_history",
            "setup": "CM_PARADEV.setup",
            "init": "CM_PARADEV.init",
            "pj": "CM_PARADEV.pj",
        },
        "filters": {
            "architecture --api-table": ["symbol", "index_name", "key"],
            "api-catalog": ["reference_id", "index_name", "key"],
            "frontend-api": [*FRONTEND_API_SELECTORS, "index_name", "key"],
            "inspections": ["kind", "index_name", "key"],
            "templates": TEMPLATE_FILTERS,
            "module-metadata-clean": [
                "family",
                "module_id",
                "source_root",
                "write",
                "plan_hash",
            ],
            "module-collection-set": [
                "module_id",
                "collection_id",
                "source_root",
                "write",
                "plan_hash",
            ],
            "module-activity-set": [
                "module_id",
                "active",
                "source_root",
                "write",
                "plan_hash",
            ],
            "module-diagram": ["family", "profile"],
            "module-diagram-edit": [
                "family",
                "request",
                "request_json",
                "profile",
                "write",
                "plan_hash",
            ],
        },
        "projections": {
            "architecture": [
                "api-table",
                "api-table-markdown",
                "surface-contract",
                "surface-contracts",
                "surface-contracts-markdown",
            ],
            "architecture --api-table": [
                "symbol",
                "index",
                "key",
            ],
            "architecture --api-table --symbol": [
                "symbol",
            ],
            "architecture --api-table --index --key": [
                "index",
                "key",
            ],
            "frontend-api": [
                "form",
                "index",
                "key",
                "action",
                "values-json",
                "option-field",
                "binding-surface",
                "binding-key",
                "rest-request",
                "workspace",
                "markdown",
                "sdk-cli-markdown",
                "typescript",
            ],
            "api-catalog": [
                "reference",
                "index",
                "key",
                "markdown",
            ],
            "package-api": [
                "markdown",
            ],
            "config-api": [
                "markdown",
            ],
            "gui-api": [
                "markdown",
            ],
            "desktop-api": [
                "markdown",
                "typescript",
            ],
            "games-api": [
                "markdown",
            ],
            "surfaces-api": [
                "markdown",
            ],
            "sdk-api": [
                "markdown",
            ],
            "project-api": [
                "markdown",
            ],
            "templates-api": [
                "markdown",
            ],
            "copy-roots-api": [
                "markdown",
            ],
            "project-facade-api": [
                "markdown",
            ],
            "localization-api": [
                "markdown",
            ],
            "build-api": [
                "markdown",
            ],
            "pdx-api": [
                "markdown",
            ],
            "pdx-core-api": [
                "markdown",
            ],
            "lsp-api": [
                "markdown",
            ],
            "lsp-server-api": [
                "markdown",
            ],
            "catalog-api": [
                "markdown",
            ],
            "hb-api": [
                "markdown",
            ],
            "rest-api": [
                "markdown",
            ],
            "rest-facade-api": [
                "markdown",
            ],
            "mcp-api": [
                "markdown",
            ],
            "cli-api": [
                "markdown",
            ],
            "inspections": [
                "kind",
                "index",
                "key",
                "markdown",
            ],
        },
        "frontend_operation_ids": get_frontend_api_binding_index("cli"),
        "inspection_contract": inspection_contract,
        "sdk_owned": True,
    }
    _add_standard_api_reference_selectors(contract)
    return contract


def _add_standard_api_reference_selectors(contract: dict[str, object]) -> None:
    adapters = _contract_mapping(contract, "adapters")
    filters = _contract_mapping(contract, "filters")
    projections = _contract_mapping(contract, "projections")
    for row in API_CATALOG_SOURCE_ROWS:
        command = row["cli_command"]
        selector_helper = row["selector_helper"]
        if "cli" not in row["surfaces"] or command in {"api-catalog", "frontend-api"} or not command.endswith("-api") or not selector_helper:
            continue
        adapters[command] = selector_helper
        adapters[f"{command} --symbol"] = selector_helper
        adapters[f"{command} --index --key"] = selector_helper
        filters[command] = list(_STANDARD_API_REFERENCE_FILTERS)
        projections[command] = list(_STANDARD_API_REFERENCE_PROJECTIONS)


def _contract_mapping(contract: Mapping[str, object], key: str) -> dict[str, object]:
    value = contract.get(key)
    if not isinstance(value, dict):
        raise TypeError(f"CLI contract {key!r} must be a mapping")
    return value


def get_cli_api_table() -> CliApiTable:
    """Return the API-standard table for Typer CLI commands.

    Returns:
        JSON-safe table derived from `get_cli_contract()`, with command rows
        and indexes for feature, kind, adapter, and frontend operation audits.
    """

    return cast(
        CliApiTable,
        api_indexed_table(
            CLI_API_TABLE_SCHEMA,
            _cli_api_rows(get_cli_contract()),
            (
                ("feature_index", "feature"),
                ("kind_index", "kind"),
                ("adapter_index", "adapter"),
                ("frontend_operation_index", "frontend_operation_ids"),
            ),
            index_list_fields=("frontend_operation_ids",),
            index_skip_empty_fields=("adapter",),
            row_list_fields=("filters", "projections", "frontend_operation_ids"),
        ),
    )


def get_cli_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> CliApiTable | CliApiRow | list[str]:
    """Return the full CLI API table, one row, or one index bucket.

    Args:
        symbol: Optional CLI symbol to select from the table rows.
        index_name: Optional index name, such as `feature_index`,
            `kind_index`, `adapter_index`, or `frontend_operation_index`.
        key: Optional key inside the selected index.

    Returns:
        A detached table copy when no selector is passed, a detached row copy
        when `symbol` is passed, or a copied list of symbols for an index
        bucket when `index_name` and `key` are passed.

    Raises:
        ValueError: If selectors are ambiguous, incomplete, or name an
            unsupported index.
        KeyError: If the requested symbol or index key is not present.
    """

    return cast(
        CliApiTable | CliApiRow | list[str],
        api_table_selection(
            get_cli_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_CLI_API_INDEX_NAMES,
        ),
    )


def render_cli_api_reference_markdown() -> str:
    """Render the CLI command table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/cli-api-reference.md`. The content is generated
        from `get_cli_api_table()` so the static CLI contract, adapter map,
        frontend operation reverse index, and manual page stay aligned.
    """

    table = get_cli_api_table()
    return api_reference_markdown(
        title="CLI API Reference",
        source="paradev.surfaces.cli.get_cli_api_table()",
        regenerate_when="Regenerate this file whenever the CLI command contract changes:",
        command="rtk uv run paradev cli-api --markdown > docs/user-manual/cli-api-reference.md",
        sections=api_indexed_reference_sections(
            summary_lines=[
                f"- API rows / API 行数: {table['row_count']}",
                f"- Features / Feature 数: {len(table['feature_index'])}",
                f"- Row kinds / 行类型数: {len(table['kind_index'])}",
                f"- Adapters / Adapter 数: {len(table['adapter_index'])}",
                f"- Frontend-bound operations / 前端绑定操作数: {len(table['frontend_operation_index'])}",
            ],
            table=table,
            index_specs=(
                ("Kind Index / 行类型索引", "kind_index", "Kind", "Commands", "Symbols"),
                ("Feature Index / Feature 索引", "feature_index", "Feature", "Commands", "Symbols"),
                ("Adapter Index / Adapter 索引", "adapter_index", "Adapter", "Commands", "Symbols"),
                ("Frontend Operation Index / 前端操作索引", "frontend_operation_index", "Operation", "Commands", "Symbols"),
            ),
            fields=_CLI_API_STANDARD_FIELDS,
            list_fields=("filters", "projections", "frontend_operation_ids"),
        ),
    )


def _cli_api_rows(contract: Mapping[str, object]) -> list[CliApiRow]:
    commands = _string_list(contract.get("commands"))
    adapters = _string_mapping(contract.get("adapters"))
    filters = _string_list_mapping(contract.get("filters"))
    projections = _string_list_mapping(contract.get("projections"))
    frontend_operation_ids = _string_list_mapping(contract.get("frontend_operation_ids"))
    command_set = set(commands)
    adapter_set = set(adapters)
    rows: list[CliApiRow] = []
    for command_key in _cli_api_command_keys(commands, adapters, frontend_operation_ids):
        rows.append(
            {
                "symbol": _cli_api_symbol(command_key, command_set, adapter_set),
                "kind": _cli_api_kind(command_key, command_set, adapter_set),
                "layer": "cli",
                "feature": _cli_api_feature(command_key),
                "command_key": command_key,
                "adapter": adapters.get(command_key, ""),
                "filters": _cli_api_filters(command_key, filters),
                "projections": _cli_api_projections(command_key, projections),
                "returns": _cli_api_returns(command_key, adapters),
                "raises": _cli_api_raises(command_key),
                "registry_seam": "Typer command registry",
                "surface": "cli",
                "frontend_operation_ids": list(frontend_operation_ids.get(command_key, [])),
                "doc_page": _CLI_API_REFERENCE_PAGE,
                "test_anchor": _CLI_API_TEST_ANCHOR,
            }
        )
    return rows


def _cli_api_command_keys(commands: list[str], adapters: Mapping[str, str], frontend_operation_ids: Mapping[str, list[str]]) -> list[str]:
    command_keys = list(commands)
    seen = set(command_keys)
    for source in (adapters, frontend_operation_ids):
        for command_key in source:
            if command_key in seen:
                continue
            seen.add(command_key)
            command_keys.append(command_key)
    return command_keys


def _cli_api_kind(command_key: str, command_set: set[str], adapter_set: set[str]) -> str:
    if command_key in _CLI_COMMAND_GROUPS:
        return "command group"
    if command_key in command_set:
        return "command"
    if command_key in adapter_set:
        return "command projection"
    return "binding variant"


def _cli_api_symbol(command_key: str, command_set: set[str], adapter_set: set[str]) -> str:
    if command_key in command_set or command_key in adapter_set or _cli_api_base_command(command_key) in command_set:
        return f"paradev {command_key}"
    return f"CLI binding: {command_key}"


def _cli_api_feature(command_key: str) -> str:
    base = _cli_api_base_command(command_key)
    if base in {"setup", "init", "pj"} or base.startswith("config"):
        return "config"
    if base == "gui-api":
        return "gui"
    if base == "desktop-api":
        return "desktop"
    if base == "games-api":
        return "games"
    if base == "hb" or base.startswith("hb ") or base in {"catalog-api", "hb-api"}:
        return "catalog"
    if base == "mcp" or base.startswith("mcp ") or base == "mcp-api":
        return "mcp"
    if base.startswith("lsp") or base == "lsp-api":
        return "lsp"
    if base in {"parse", "format", "pdx-api", "pdx-core-api"}:
        return "pdx"
    if base in {"project-api", "project-facade-api"}:
        return "projects"
    if base == "localization-api":
        return "localization"
    if base == "build-api":
        return "build"
    if base == "copy-roots-api":
        return "copy-roots"
    if base == "api-catalog":
        return "api-catalog"
    if base == "package-api":
        return "package"
    if base == "surfaces-api":
        return "surfaces"
    if base.startswith("rest-") or base == "rest-api":
        return "rest"
    if base in {"sdk-api", "cli-api"}:
        return base.removesuffix("-api")
    if base == "architecture":
        return "architecture"
    if base == "frontend-api":
        return "frontend-api"
    if base in {"templates-api", "templates", "authoring-path", "authoring-plan", "scaffold", "module-batch-create"}:
        return "authoring"
    if base.startswith("module-"):
        return "modules"
    if base.startswith("collection-"):
        return "collections"
    if base in {"new", "project", "projects", "desktop-state", "project-browser", "project-find", "project-rename", "project-language", "draft-apply"}:
        return "projects"
    if base == "inspections":
        return "inspections"
    if command_key == "inspections and inspection commands":
        return "inspections"
    if base in {
        "build",
        "summary",
        "manifests",
        "modules",
        "collections",
        "artifacts",
        "localization",
        "sources",
        "source-slots",
        "assets",
        "sprites",
        "diagnostics",
        "source-map",
        "dependencies",
        "build-graph",
        "build-explain",
        "families",
    }:
        return "build"
    return "cli"


def _cli_api_base_command(command_key: str) -> str:
    parts = command_key.split()
    command_parts: list[str] = []
    for part in parts:
        if part.startswith("--"):
            break
        command_parts.append(part)
    return " ".join(command_parts)


def _cli_api_filters(command_key: str, filters: Mapping[str, list[str]]) -> list[str]:
    if command_key in filters:
        return list(filters[command_key])
    filter_key = _cli_api_longest_prefixed_key(command_key, filters)
    if filter_key:
        return list(filters[filter_key])
    return list(filters.get(_cli_api_base_command(command_key), []))


def _cli_api_projections(command_key: str, projections: Mapping[str, list[str]]) -> list[str]:
    if command_key in projections:
        return list(projections[command_key])
    option_projections = [part[2:] for part in command_key.split() if part.startswith("--")]
    if option_projections:
        return option_projections
    return []


def _cli_api_longest_prefixed_key(command_key: str, values: Mapping[str, object]) -> str:
    candidates = [key for key in values if command_key.startswith(f"{key} ")]
    return max(candidates, key=len, default="")


def _cli_api_returns(command_key: str, adapters: Mapping[str, str]) -> str:
    adapter = adapters.get(command_key)
    if adapter:
        return f"CLI output from {adapter}"
    if command_key in _CLI_COMMAND_GROUPS:
        return "Typer subcommand group"
    return "CLI output"


def _cli_api_raises(command_key: str) -> str:
    if command_key in _CLI_COMMAND_GROUPS:
        return ""
    return "Typer validation errors"


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _string_mapping(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): str(item) for key, item in value.items()}


def _string_list_mapping(value: object) -> dict[str, list[str]]:
    if not isinstance(value, Mapping):
        return {}
    rows: dict[str, list[str]] = {}
    for key, items in value.items():
        rows[str(key)] = _string_list(items)
    return rows
