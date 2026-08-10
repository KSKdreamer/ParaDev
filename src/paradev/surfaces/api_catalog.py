"""Aggregate catalog for ParaDev API reference tables."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from importlib import import_module
from typing import Literal, NoReturn, cast

from typing_extensions import TypedDict

from paradev._api_table import api_indexed_table
from paradev._api_table_markdown import (
    api_indexed_reference_sections,
    api_reference_markdown,
    api_table_section,
    code_cell,
    code_list_cell,
    markdown_cell,
)

API_CATALOG_SCHEMA = "paradev.api-catalog.v1"
_API_CATALOG_REFERENCE_PAGE = "docs/user-manual/api-catalog-reference.md"
_API_CATALOG_REGENERATE_WHEN = "Regenerate this file whenever an API reference table or generated contract is added, removed, or renamed:"
_API_CATALOG_TEST_ANCHOR = "tests/test_architecture.py::test_api_catalog_lists_generated_references"
_API_CATALOG_STANDARD_FIELDS = (
    "id",
    "title",
    "kind",
    "layer",
    "feature",
    "schema",
    "row_count",
    "table_helper",
    "selector_helper",
    "markdown_helper",
    "cli_command",
    "markdown_cli_command",
    "index_names",
    "surfaces",
    "doc_page",
    "test_anchor",
)
_API_CATALOG_SOURCE_TEXT_FIELDS = (
    "id",
    "title",
    "kind",
    "layer",
    "feature",
    "owner_module",
    "table_helper",
    "markdown_helper",
    "cli_command",
    "markdown_cli_command",
    "doc_page",
)
_API_CATALOG_INDEX_SPECS = (
    ("Layer Index / Layer 索引", "layer_index", "Layer", "References", "IDs"),
    ("Feature Index / Feature 索引", "feature_index", "Feature", "References", "IDs"),
    ("Kind Index / 类型索引", "kind_index", "Kind", "References", "IDs"),
    ("Reference Group Index / Reference 分组索引", "group_index", "Group", "References", "IDs"),
    ("Owner Module Index / Owner Module 索引", "owner_module_index", "Owner Module", "References", "IDs"),
    ("Surface Index / Surface 索引", "surface_index", "Surface", "References", "IDs"),
    ("Regeneration Index / 重新生成索引", "cli_command_index", "CLI Command", "References", "IDs"),
    ("Selector Helper Index / Selector Helper 索引", "selector_helper_index", "Selector Helper", "References", "IDs"),
    ("Doc Page Index / Doc Page 索引", "doc_page_index", "Doc Page", "References", "IDs"),
)
_API_CATALOG_TABLE_INDEX_SPECS = (
    ("layer_index", "layer"),
    ("feature_index", "feature"),
    ("kind_index", "kind"),
    ("owner_module_index", "owner_module"),
    ("surface_index", "surfaces"),
    ("cli_command_index", "cli_command"),
    ("selector_helper_index", "selector_helper"),
    ("doc_page_index", "doc_page"),
)
API_CATALOG_INDEX_CATALOG: tuple["ApiCatalogIndexCatalogRow", ...] = (
    {
        "id": "id",
        "table_path": 'table["rows"][*]["id"]',
        "python_helper": "get_api_catalog_reference(reference_id)",
        "usage": "Reference id to one aggregate API catalog row.",
    },
    {
        "id": "layer",
        "table_path": 'table["layer_index"][layer]',
        "python_helper": "get_api_catalog_reference_ids('layer', layer)",
        "usage": "Architecture layer to generated reference ids.",
    },
    {
        "id": "feature",
        "table_path": 'table["feature_index"][feature]',
        "python_helper": "get_api_catalog_reference_ids('feature', feature)",
        "usage": "Feature area to generated reference ids.",
    },
    {
        "id": "kind",
        "table_path": 'table["kind_index"][kind]',
        "python_helper": "get_api_catalog_reference_ids('kind', kind)",
        "usage": "Reference kind to generated reference ids.",
    },
    {
        "id": "group",
        "table_path": 'table["group_index"][group]',
        "python_helper": "get_api_catalog_group_reference_ids(group)",
        "usage": "Reader-oriented reference group to generated reference ids.",
    },
    {
        "id": "reference_group",
        "table_path": 'table["reference_groups"][*]["id"]',
        "python_helper": "get_api_catalog_reference_group(group)",
        "usage": "Reference group id to one reader-oriented reference group row.",
    },
    {
        "id": "owner_module",
        "table_path": 'table["owner_module_index"][owner_module]',
        "python_helper": "get_api_catalog_reference_ids('owner_module', owner_module)",
        "usage": "Owner module import path to generated reference ids.",
    },
    {
        "id": "surface",
        "table_path": 'table["surface_index"][surface]',
        "python_helper": "get_api_catalog_reference_ids('surface', surface)",
        "usage": "Surface id to generated reference ids.",
    },
    {
        "id": "cli_command",
        "table_path": 'table["cli_command_index"][cli_command]',
        "python_helper": "get_api_catalog_reference_ids('cli_command', cli_command)",
        "usage": "CLI command stem to generated reference ids.",
    },
    {
        "id": "selector_helper",
        "table_path": 'table["selector_helper_index"][selector_helper]',
        "python_helper": "get_api_catalog_reference_ids('selector_helper', selector_helper)",
        "usage": "Shared selector helper to generated reference ids.",
    },
    {
        "id": "doc_page",
        "table_path": 'table["doc_page_index"][doc_page]',
        "python_helper": "get_api_catalog_reference_ids('doc_page', doc_page)",
        "usage": "Manual page path to generated reference ids.",
    },
)
_API_CATALOG_REFERENCE_INDEX_FIELDS = {
    "layer": "layer_index",
    "feature": "feature_index",
    "kind": "kind_index",
    "group": "group_index",
    "owner_module": "owner_module_index",
    "surface": "surface_index",
    "cli_command": "cli_command_index",
    "selector_helper": "selector_helper_index",
    "doc_page": "doc_page_index",
}
_API_CATALOG_TABLE_INDEX_LIST_FIELDS = ("surfaces",)
_API_CATALOG_TABLE_INDEX_SKIP_EMPTY_FIELDS = ("selector_helper",)
_API_CATALOG_DERIVED_INDEX_NAMES = ("group_index",)
_API_CATALOG_TABLE_ROW_LIST_FIELDS = ("surfaces", "index_names")
_API_CATALOG_REFERENCE_LIST_FIELDS = ("index_names", "surfaces")
_API_CATALOG_REFERENCE_MARKDOWN_FIELDS = ("title", "row_count")
_API_CATALOG_UNIQUE_SOURCE_FIELDS = ("doc_page", "markdown_cli_command")
_API_CATALOG_ROW_COUNT_FALLBACK_FIELDS = {
    "surface-contract-reference": "surface_count",
    "project-inspection-reference": "inspections",
}
_API_CATALOG_REFERENCE_GROUP_SPECS: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "overall",
        "Overall Catalog",
        ("api-catalog",),
        "Start here for the complete generated reference inventory and selector map.",
    ),
    (
        "facades",
        "Facade API Tables",
        ("facade-table",),
        "Stable package and layer import surfaces exposed to SDK users and developers.",
    ),
    (
        "modules",
        "Object and Module Tables",
        ("object-table", "module-table"),
        "Concrete SDK object and module contracts for project, template, and copy-root work.",
    ),
    (
        "workflows",
        "Workflow Contracts",
        ("operation-contract", "operation-matrix", "inspection-contract"),
        "Generated operation, CLI workflow, and inspection contracts shared by GUIs and agents.",
    ),
    (
        "surfaces",
        "Surface API Tables",
        ("api-table", "route-table", "tool-table", "command-table"),
        "Callable SDK, REST, MCP, and CLI surface tables with selector helpers.",
    ),
    (
        "adapters",
        "Adapter Contracts",
        ("surface-contract",),
        "Cross-surface adapter status and ownership contracts.",
    ),
)


class ApiCatalogSourceRow(TypedDict):
    """Static source metadata for one generated API reference."""

    id: str
    title: str
    kind: str
    layer: str
    feature: str
    owner_module: str
    table_helper: str
    selector_helper: str
    markdown_helper: str
    cli_command: str
    markdown_cli_command: str
    doc_page: str
    surfaces: list[str]


class ApiCatalogIndexCatalogRow(TypedDict):
    """Documented index dimension for the aggregate API catalog."""

    id: str
    table_path: str
    python_helper: str
    usage: str


class ApiCatalogReferenceGroupRow(TypedDict):
    """Reader-oriented reference group row for the aggregate API catalog."""

    id: str
    title: str
    reference_count: int
    kinds: list[str]
    reference_ids: list[str]
    usage: str


class ApiCatalogSummary(TypedDict):
    """Compact counts for the aggregate API catalog payload."""

    reference_count: int
    layer_count: int
    feature_count: int
    kind_count: int
    reference_group_count: int
    index_count: int
    owner_module_count: int
    surface_count: int
    cli_command_count: int
    selector_helper_count: int
    doc_page_count: int


class ApiCatalogRow(ApiCatalogSourceRow):
    """One aggregate API catalog table row."""

    schema: str
    row_count: int
    index_names: list[str]
    test_anchor: str


class ApiCatalogTable(TypedDict):
    """Generated catalog for API reference tables and contracts."""

    schema: str
    row_count: int
    summary: ApiCatalogSummary
    layer_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    group_index: dict[str, list[str]]
    index_catalog: list[ApiCatalogIndexCatalogRow]
    reference_groups: list[ApiCatalogReferenceGroupRow]
    owner_module_index: dict[str, list[str]]
    surface_index: dict[str, list[str]]
    cli_command_index: dict[str, list[str]]
    selector_helper_index: dict[str, list[str]]
    doc_page_index: dict[str, list[str]]
    rows: list[ApiCatalogRow]


API_CATALOG_SOURCE_ROWS: tuple[ApiCatalogSourceRow, ...] = (
    {
        "id": "api-catalog",
        "title": "API Catalog Reference",
        "kind": "api-catalog",
        "layer": "surface",
        "feature": "overall",
        "owner_module": "paradev.surfaces",
        "table_helper": "get_api_catalog_table",
        "selector_helper": "get_api_catalog_selection",
        "markdown_helper": "render_api_catalog_reference_markdown",
        "cli_command": "api-catalog",
        "markdown_cli_command": "api-catalog --markdown",
        "doc_page": _API_CATALOG_REFERENCE_PAGE,
        "surfaces": ["sdk", "cli", "rest", "mcp", "docs"],
    },
    {
        "id": "sdk-api",
        "title": "SDK API Reference",
        "kind": "facade-table",
        "layer": "sdk",
        "feature": "facade",
        "owner_module": "paradev.sdk",
        "table_helper": "get_sdk_api_table",
        "selector_helper": "get_sdk_api_selection",
        "markdown_helper": "render_sdk_api_reference_markdown",
        "cli_command": "sdk-api",
        "markdown_cli_command": "sdk-api --markdown",
        "doc_page": "docs/user-manual/sdk-api-reference.md",
        "surfaces": ["sdk", "cli", "docs"],
    },
    {
        "id": "package-api",
        "title": "Package API Reference",
        "kind": "facade-table",
        "layer": "package",
        "feature": "facade",
        "owner_module": "paradev",
        "table_helper": "get_package_api_table",
        "selector_helper": "get_package_api_selection",
        "markdown_helper": "render_package_api_reference_markdown",
        "cli_command": "package-api",
        "markdown_cli_command": "package-api --markdown",
        "doc_page": "docs/user-manual/package-api-reference.md",
        "surfaces": ["sdk", "cli", "docs"],
    },
    {
        "id": "config-api",
        "title": "Config API Reference",
        "kind": "facade-table",
        "layer": "config",
        "feature": "config",
        "owner_module": "paradev.config",
        "table_helper": "get_config_api_table",
        "selector_helper": "get_config_api_selection",
        "markdown_helper": "render_config_api_reference_markdown",
        "cli_command": "config-api",
        "markdown_cli_command": "config-api --markdown",
        "doc_page": "docs/user-manual/config-api-reference.md",
        "surfaces": ["sdk", "cli", "docs"],
    },
    {
        "id": "gui-api",
        "title": "GUI API Reference",
        "kind": "facade-table",
        "layer": "gui",
        "feature": "launcher",
        "owner_module": "paradev.gui",
        "table_helper": "get_gui_api_table",
        "selector_helper": "get_gui_api_selection",
        "markdown_helper": "render_gui_api_reference_markdown",
        "cli_command": "gui-api",
        "markdown_cli_command": "gui-api --markdown",
        "doc_page": "docs/user-manual/gui-api-reference.md",
        "surfaces": ["sdk", "cli", "desktop", "docs"],
    },
    {
        "id": "desktop-api",
        "title": "Desktop API Reference",
        "kind": "facade-table",
        "layer": "desktop",
        "feature": "state",
        "owner_module": "paradev.desktop",
        "table_helper": "get_desktop_api_table",
        "selector_helper": "get_desktop_api_selection",
        "markdown_helper": "render_desktop_api_reference_markdown",
        "cli_command": "desktop-api",
        "markdown_cli_command": "desktop-api --markdown",
        "doc_page": "docs/user-manual/desktop-api-reference.md",
        "surfaces": ["sdk", "cli", "desktop", "docs"],
    },
    {
        "id": "games-api",
        "title": "Games API Reference",
        "kind": "facade-table",
        "layer": "games",
        "feature": "profiles",
        "owner_module": "paradev.games",
        "table_helper": "get_games_api_table",
        "selector_helper": "get_games_api_selection",
        "markdown_helper": "render_games_api_reference_markdown",
        "cli_command": "games-api",
        "markdown_cli_command": "games-api --markdown",
        "doc_page": "docs/user-manual/games-api-reference.md",
        "surfaces": ["sdk", "cli", "docs"],
    },
    {
        "id": "surfaces-api",
        "title": "Surfaces API Reference",
        "kind": "facade-table",
        "layer": "surface",
        "feature": "surfaces",
        "owner_module": "paradev.surfaces",
        "table_helper": "get_surfaces_api_table",
        "selector_helper": "get_surfaces_api_selection",
        "markdown_helper": "render_surfaces_api_reference_markdown",
        "cli_command": "surfaces-api",
        "markdown_cli_command": "surfaces-api --markdown",
        "doc_page": "docs/user-manual/surfaces-api-reference.md",
        "surfaces": ["sdk", "cli", "rest", "mcp", "lsp", "docs"],
    },
    {
        "id": "project-api",
        "title": "Project API Reference",
        "kind": "object-table",
        "layer": "sdk",
        "feature": "projects",
        "owner_module": "paradev.sdk",
        "table_helper": "get_project_api_table",
        "selector_helper": "get_project_api_selection",
        "markdown_helper": "render_project_api_reference_markdown",
        "cli_command": "project-api",
        "markdown_cli_command": "project-api --markdown",
        "doc_page": "docs/user-manual/project-api-reference.md",
        "surfaces": ["sdk", "cli", "frontend", "docs"],
    },
    {
        "id": "templates-api",
        "title": "Authoring Templates API Reference",
        "kind": "module-table",
        "layer": "sdk",
        "feature": "authoring",
        "owner_module": "paradev.sdk.templates",
        "table_helper": "get_templates_api_table",
        "selector_helper": "get_templates_api_selection",
        "markdown_helper": "render_templates_api_reference_markdown",
        "cli_command": "templates-api",
        "markdown_cli_command": "templates-api --markdown",
        "doc_page": "docs/user-manual/templates-api-reference.md",
        "surfaces": ["sdk", "cli", "frontend", "docs"],
    },
    {
        "id": "copy-roots-api",
        "title": "Copy Roots API Reference",
        "kind": "module-table",
        "layer": "sdk",
        "feature": "copy-roots",
        "owner_module": "paradev.sdk.copy_roots",
        "table_helper": "get_copy_roots_api_table",
        "selector_helper": "get_copy_roots_api_selection",
        "markdown_helper": "render_copy_roots_api_reference_markdown",
        "cli_command": "copy-roots-api",
        "markdown_cli_command": "copy-roots-api --markdown",
        "doc_page": "docs/user-manual/copy-roots-api-reference.md",
        "surfaces": ["sdk", "cli", "docs"],
    },
    {
        "id": "project-facade-api",
        "title": "Project Facade API Reference",
        "kind": "facade-table",
        "layer": "project",
        "feature": "project-facade",
        "owner_module": "paradev.project",
        "table_helper": "get_project_facade_api_table",
        "selector_helper": "get_project_facade_api_selection",
        "markdown_helper": "render_project_facade_api_reference_markdown",
        "cli_command": "project-facade-api",
        "markdown_cli_command": "project-facade-api --markdown",
        "doc_page": "docs/user-manual/project-facade-api-reference.md",
        "surfaces": ["sdk", "cli", "docs"],
    },
    {
        "id": "localization-api",
        "title": "Localization API Reference",
        "kind": "facade-table",
        "layer": "localization",
        "feature": "localization",
        "owner_module": "paradev.localization",
        "table_helper": "get_localization_api_table",
        "selector_helper": "get_localization_api_selection",
        "markdown_helper": "render_localization_api_reference_markdown",
        "cli_command": "localization-api",
        "markdown_cli_command": "localization-api --markdown",
        "doc_page": "docs/user-manual/localization-api-reference.md",
        "surfaces": ["sdk", "cli", "docs"],
    },
    {
        "id": "build-api",
        "title": "Build API Reference",
        "kind": "facade-table",
        "layer": "build",
        "feature": "compiler",
        "owner_module": "paradev.build",
        "table_helper": "get_build_api_table",
        "selector_helper": "get_build_api_selection",
        "markdown_helper": "render_build_api_reference_markdown",
        "cli_command": "build-api",
        "markdown_cli_command": "build-api --markdown",
        "doc_page": "docs/user-manual/build-api-reference.md",
        "surfaces": ["sdk", "cli", "docs"],
    },
    {
        "id": "frontend-api",
        "title": "Frontend API Reference",
        "kind": "operation-contract",
        "layer": "sdk",
        "feature": "frontend",
        "owner_module": "paradev.sdk",
        "table_helper": "get_frontend_api_contract",
        "selector_helper": "get_frontend_api_selection",
        "markdown_helper": "render_frontend_api_reference_markdown",
        "cli_command": "frontend-api",
        "markdown_cli_command": "frontend-api --markdown",
        "doc_page": "docs/user-manual/frontend-api-reference.md",
        "surfaces": ["sdk", "cli", "rest", "mcp", "lsp", "frontend", "typescript", "docs"],
    },
    {
        "id": "sdk-cli-reference",
        "title": "SDK And CLI API Reference",
        "kind": "operation-matrix",
        "layer": "sdk",
        "feature": "sdk-cli",
        "owner_module": "paradev.sdk",
        "table_helper": "get_frontend_api_contract",
        "selector_helper": "get_frontend_api_selection",
        "markdown_helper": "render_frontend_api_sdk_cli_markdown",
        "cli_command": "frontend-api",
        "markdown_cli_command": "frontend-api --sdk-cli-markdown",
        "doc_page": "docs/user-manual/sdk-cli-reference.md",
        "surfaces": ["sdk", "cli", "docs"],
    },
    {
        "id": "project-inspection-reference",
        "title": "Project Inspection Reference",
        "kind": "inspection-contract",
        "layer": "sdk",
        "feature": "inspections",
        "owner_module": "paradev.sdk",
        "table_helper": "get_project_inspection_contract",
        "selector_helper": "get_project_inspection_selection",
        "markdown_helper": "render_project_inspection_reference_markdown",
        "cli_command": "inspections",
        "markdown_cli_command": "inspections --markdown",
        "doc_page": "docs/user-manual/project-inspection-reference.md",
        "surfaces": ["sdk", "cli", "rest", "mcp", "frontend", "docs"],
    },
    {
        "id": "architecture-api",
        "title": "Architecture API Reference",
        "kind": "api-table",
        "layer": "sdk",
        "feature": "architecture",
        "owner_module": "paradev.sdk",
        "table_helper": "get_architecture_api_table",
        "selector_helper": "get_architecture_api_selection",
        "markdown_helper": "render_architecture_api_reference_markdown",
        "cli_command": "architecture --api-table",
        "markdown_cli_command": "architecture --api-table-markdown",
        "doc_page": "docs/user-manual/architecture-api-reference.md",
        "surfaces": ["sdk", "cli", "rest", "mcp", "docs"],
    },
    {
        "id": "pdx-api",
        "title": "PDX API Reference",
        "kind": "api-table",
        "layer": "sdk",
        "feature": "pdx",
        "owner_module": "paradev.sdk",
        "table_helper": "get_pdx_api_table",
        "selector_helper": "get_pdx_api_selection",
        "markdown_helper": "render_pdx_api_reference_markdown",
        "cli_command": "pdx-api",
        "markdown_cli_command": "pdx-api --markdown",
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "surfaces": ["sdk", "cli", "rest", "mcp", "docs"],
    },
    {
        "id": "pdx-core-api",
        "title": "PDX Core API Reference",
        "kind": "facade-table",
        "layer": "pdx",
        "feature": "pdx-core",
        "owner_module": "paradev.pdx",
        "table_helper": "get_pdx_core_api_table",
        "selector_helper": "get_pdx_core_api_selection",
        "markdown_helper": "render_pdx_core_api_reference_markdown",
        "cli_command": "pdx-core-api",
        "markdown_cli_command": "pdx-core-api --markdown",
        "doc_page": "docs/user-manual/pdx-core-api-reference.md",
        "surfaces": ["sdk", "cli", "docs"],
    },
    {
        "id": "lsp-api",
        "title": "LSP API Reference",
        "kind": "api-table",
        "layer": "sdk",
        "feature": "lsp",
        "owner_module": "paradev.sdk",
        "table_helper": "get_lsp_api_table",
        "selector_helper": "get_lsp_api_selection",
        "markdown_helper": "render_lsp_api_reference_markdown",
        "cli_command": "lsp-api",
        "markdown_cli_command": "lsp-api --markdown",
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "surfaces": ["sdk", "cli", "rest", "mcp", "lsp", "docs"],
    },
    {
        "id": "lsp-server-api",
        "title": "LSP Server API Reference",
        "kind": "facade-table",
        "layer": "lsp",
        "feature": "lsp-server",
        "owner_module": "paradev.lsp",
        "table_helper": "get_lsp_server_api_table",
        "selector_helper": "get_lsp_server_api_selection",
        "markdown_helper": "render_lsp_server_api_reference_markdown",
        "cli_command": "lsp-server-api",
        "markdown_cli_command": "lsp-server-api --markdown",
        "doc_page": "docs/user-manual/lsp-server-api-reference.md",
        "surfaces": ["sdk", "cli", "lsp", "docs"],
    },
    {
        "id": "catalog-api",
        "title": "Catalog API Reference",
        "kind": "api-table",
        "layer": "hb",
        "feature": "catalog",
        "owner_module": "paradev.hb",
        "table_helper": "get_catalog_api_table",
        "selector_helper": "get_catalog_api_selection",
        "markdown_helper": "render_catalog_api_reference_markdown",
        "cli_command": "catalog-api",
        "markdown_cli_command": "catalog-api --markdown",
        "doc_page": "docs/user-manual/catalog-api-reference.md",
        "surfaces": ["sdk", "cli", "rest", "mcp", "lsp", "docs"],
    },
    {
        "id": "hb-api",
        "title": "HeavenBase Facade API Reference",
        "kind": "facade-table",
        "layer": "hb",
        "feature": "facade",
        "owner_module": "paradev.hb",
        "table_helper": "get_hb_api_table",
        "selector_helper": "get_hb_api_selection",
        "markdown_helper": "render_hb_api_reference_markdown",
        "cli_command": "hb-api",
        "markdown_cli_command": "hb-api --markdown",
        "doc_page": "docs/user-manual/hb-api-reference.md",
        "surfaces": ["sdk", "cli", "docs"],
    },
    {
        "id": "rest-api",
        "title": "REST API Reference",
        "kind": "route-table",
        "layer": "rest",
        "feature": "rest",
        "owner_module": "paradev.surfaces.rest",
        "table_helper": "get_rest_api_table",
        "selector_helper": "get_rest_api_selection",
        "markdown_helper": "render_rest_api_reference_markdown",
        "cli_command": "rest-api",
        "markdown_cli_command": "rest-api --markdown",
        "doc_page": "docs/user-manual/rest-api-reference.md",
        "surfaces": ["rest", "cli", "frontend", "docs"],
    },
    {
        "id": "rest-facade-api",
        "title": "REST Facade API Reference",
        "kind": "facade-table",
        "layer": "rest",
        "feature": "rest-facade",
        "owner_module": "paradev.api",
        "table_helper": "get_rest_facade_api_table",
        "selector_helper": "get_rest_facade_api_selection",
        "markdown_helper": "render_rest_facade_api_reference_markdown",
        "cli_command": "rest-facade-api",
        "markdown_cli_command": "rest-facade-api --markdown",
        "doc_page": "docs/user-manual/rest-facade-api-reference.md",
        "surfaces": ["sdk", "cli", "rest", "docs"],
    },
    {
        "id": "mcp-api",
        "title": "MCP API Reference",
        "kind": "tool-table",
        "layer": "mcp",
        "feature": "mcp",
        "owner_module": "paradev.surfaces.mcp",
        "table_helper": "get_mcp_api_table",
        "selector_helper": "get_mcp_api_selection",
        "markdown_helper": "render_mcp_api_reference_markdown",
        "cli_command": "mcp-api",
        "markdown_cli_command": "mcp-api --markdown",
        "doc_page": "docs/user-manual/mcp-api-reference.md",
        "surfaces": ["mcp", "cli", "frontend", "docs"],
    },
    {
        "id": "cli-api",
        "title": "CLI API Reference",
        "kind": "command-table",
        "layer": "cli",
        "feature": "cli",
        "owner_module": "paradev.surfaces.cli",
        "table_helper": "get_cli_api_table",
        "selector_helper": "get_cli_api_selection",
        "markdown_helper": "render_cli_api_reference_markdown",
        "cli_command": "cli-api",
        "markdown_cli_command": "cli-api --markdown",
        "doc_page": "docs/user-manual/cli-api-reference.md",
        "surfaces": ["cli", "rest", "mcp", "frontend", "docs"],
    },
    {
        "id": "surface-contract-reference",
        "title": "Surface Contract Reference",
        "kind": "surface-contract",
        "layer": "surface",
        "feature": "adapters",
        "owner_module": "paradev.surfaces",
        "table_helper": "get_surface_contract_summary",
        "selector_helper": "get_surface_contract_selection",
        "markdown_helper": "render_surface_contract_reference_markdown",
        "cli_command": "architecture --surface-contracts",
        "markdown_cli_command": "architecture --surface-contracts-markdown",
        "doc_page": "docs/user-manual/surface-contract-reference.md",
        "surfaces": ["cli", "rest", "mcp", "lsp", "vscode", "bundle", "docs"],
    },
)


def _api_catalog_source_index(rows: tuple[ApiCatalogSourceRow, ...]) -> dict[str, ApiCatalogSourceRow]:
    index: dict[str, ApiCatalogSourceRow] = {}
    identity_indexes = _api_catalog_identity_indexes()
    for row in rows:
        _api_catalog_validate_source_text_fields(row)
        _api_catalog_validate_source_selector_helper_text(row)
        source_id = _api_catalog_source_text(row, "id")
        if source_id in index:
            raise ValueError(f"duplicate ParaDev API catalog source id {source_id!r}")
        index[source_id] = row
        _api_catalog_validate_source_surfaces(row)
        _api_catalog_add_unique_source_fields(identity_indexes, row, source_id)
    return index


def _api_catalog_identity_indexes() -> dict[str, dict[str, str]]:
    return {field: {} for field in _API_CATALOG_UNIQUE_SOURCE_FIELDS}


def _api_catalog_add_unique_source_fields(
    indexes: dict[str, dict[str, str]],
    source: Mapping[str, object],
    source_id: str,
) -> None:
    for field in _API_CATALOG_UNIQUE_SOURCE_FIELDS:
        _api_catalog_add_unique_source_value(
            indexes[field],
            field=field,
            value=_api_catalog_source_text(source, field),
            source_id=source_id,
        )


def _api_catalog_validate_source_text_fields(source: Mapping[str, object]) -> None:
    for field in _API_CATALOG_SOURCE_TEXT_FIELDS:
        _api_catalog_source_text(source, field)


def _api_catalog_validate_source_selector_helper_text(source: Mapping[str, object]) -> None:
    try:
        value = source["selector_helper"]
    except KeyError as error:
        raise KeyError("ParaDev API catalog source missing 'selector_helper'") from error
    if not isinstance(value, str):
        source_id = source.get("id", "<unknown>")
        raise TypeError(f"ParaDev API catalog source {source_id!r} selector_helper must be a string value, not {type(value).__name__}")


def _api_catalog_source_text(source: Mapping[str, object], field: str) -> str:
    try:
        value = source[field]
    except KeyError as error:
        raise KeyError(f"ParaDev API catalog source missing {field!r}") from error
    if not isinstance(value, str):
        source_id = source.get("id", "<unknown>")
        raise TypeError(f"ParaDev API catalog source {source_id!r} {field} must be a string value, not {type(value).__name__}")
    if not value:
        source_id = source.get("id", "<unknown>")
        raise ValueError(f"ParaDev API catalog source {source_id!r} {field} must not be empty")
    return value


def _api_catalog_validate_source_surfaces(source: ApiCatalogSourceRow) -> None:
    source_id = source["id"]
    surfaces = _api_catalog_source_surface_list(source)
    if not surfaces:
        raise ValueError(f"ParaDev API catalog source {source_id!r} must expose at least one surface")
    seen: set[str] = set()
    for surface in surfaces:
        if not surface:
            raise ValueError(f"ParaDev API catalog source {source_id!r} surface value must not be empty")
        if surface in seen:
            raise ValueError(f"duplicate ParaDev API catalog source surface {surface!r} for {source_id!r}")
        seen.add(surface)


def _api_catalog_source_surface_list(source: ApiCatalogSourceRow) -> list[str]:
    value = source["surfaces"]
    if isinstance(value, (str, bytes)):
        raise TypeError(f"ParaDev API catalog source {source['id']!r} surfaces must be a list-like value, not {type(value).__name__}")
    if isinstance(value, Mapping):
        raise TypeError(f"ParaDev API catalog source {source['id']!r} surfaces must be a list-like value, not {type(value).__name__}")
    if not isinstance(value, Iterable):
        raise TypeError(f"ParaDev API catalog source {source['id']!r} surfaces must be a list-like value, not {type(value).__name__}")
    surfaces: list[str] = []
    for surface in value:
        if not isinstance(surface, str):
            raise TypeError(f"ParaDev API catalog source {source['id']!r} surface values must be strings, not {type(surface).__name__}")
        surfaces.append(surface)
    return surfaces


def _api_catalog_add_unique_source_value(index: dict[str, str], *, field: str, value: str, source_id: str) -> None:
    previous_id = index.get(value)
    if previous_id is not None:
        raise ValueError(f"duplicate ParaDev API catalog source {field} {value!r} for {previous_id!r} and {source_id!r}")
    index[value] = source_id


_API_CATALOG_SOURCE_IDS = tuple(row["id"] for row in API_CATALOG_SOURCE_ROWS)
_API_CATALOG_SOURCE_BY_ID = _api_catalog_source_index(API_CATALOG_SOURCE_ROWS)


def get_api_catalog_index_catalog() -> list[ApiCatalogIndexCatalogRow]:
    """Return documented index dimensions for the aggregate API catalog.

    Returns:
        Copied rows describing the table path, Python helper, and intended
        lookup use for each aggregate API catalog index dimension.
    """

    return [_api_catalog_copy_index_catalog_row(row) for row in get_api_catalog_table()["index_catalog"]]


def get_api_catalog_summary() -> ApiCatalogSummary:
    """Return compact counts for the aggregate API catalog.

    Returns:
        Detached summary payload with counts for references, groups, indexes,
        modules, surfaces, commands, selector helpers, and generated docs.
    """

    return _api_catalog_copy_summary(get_api_catalog_table()["summary"])


def get_api_catalog_table() -> ApiCatalogTable:
    """Return the aggregate catalog of generated API references.

    Returns:
        JSON-safe table with one row per generated API reference or public
        contract, including schema, summary counts, regeneration command,
        grouped indexes, documented index dimensions, and reader-oriented
        reference groups for overall API-surface audits.
    """

    table = api_indexed_table(
        API_CATALOG_SCHEMA,
        (_api_catalog_row(source) for source in API_CATALOG_SOURCE_ROWS),
        _API_CATALOG_TABLE_INDEX_SPECS,
        value_field="id",
        index_list_fields=_API_CATALOG_TABLE_INDEX_LIST_FIELDS,
        index_skip_empty_fields=_API_CATALOG_TABLE_INDEX_SKIP_EMPTY_FIELDS,
        row_list_fields=_API_CATALOG_TABLE_ROW_LIST_FIELDS,
    )
    rows = table.pop("rows")
    table["group_index"] = _api_catalog_reference_group_index(table)
    table["index_catalog"] = _api_catalog_index_catalog_rows()
    table["reference_groups"] = _api_catalog_reference_groups(table)
    table["summary"] = _api_catalog_summary(table)
    table["rows"] = rows
    return cast(ApiCatalogTable, table)


def get_api_catalog_reference(reference_id: str) -> ApiCatalogRow:
    """Return one aggregate API catalog row by stable reference id.

    Args:
        reference_id: Stable API reference id such as `frontend-api` or
            `mcp-api`.

    Returns:
        Detached row for the requested generated reference or public contract.

    Raises:
        KeyError: If `reference_id` is not listed in the aggregate API catalog.
    """

    for row in get_api_catalog_table()["rows"]:
        if row["id"] == reference_id:
            return _api_catalog_copy_row(row)
    raise KeyError(f"unknown ParaDev API catalog reference {reference_id!r}; " f"expected one of: {_api_catalog_known_source_ids()}")


def get_api_catalog_reference_ids(index_name: str, key: str) -> list[str]:
    """Return API reference ids assigned to one aggregate catalog index key.

    Args:
        index_name: Index dimension such as `layer`, `feature`, `owner_module`,
            or `surface`.
        key: Concrete index key to look up.

    Returns:
        Copied ordered list of stable API reference ids for that key.

    Raises:
        ValueError: If `index_name` is unsupported or `key` is absent from the
            selected index.
    """

    index = _api_catalog_reference_index(index_name)
    try:
        return list(index[key])
    except KeyError as error:
        _raise_unknown_api_catalog_key(
            _api_catalog_index_label(index_name),
            key,
            _api_catalog_index_choice_label(index_name),
            index,
            cause=error,
        )


def get_api_catalog_group_reference_ids(group: str) -> list[str]:
    """Return API reference ids assigned to one reader-oriented group.

    Args:
        group: API catalog group id such as `surfaces`, `modules`, or
            `facades`.

    Returns:
        Copied ordered list of stable API reference ids for that group.

    Raises:
        ValueError: If `group` is not listed in the aggregate API catalog.
    """

    return get_api_catalog_reference_ids("group", group)


def get_api_catalog_reference_group(group: str) -> ApiCatalogReferenceGroupRow:
    """Return one reader-oriented API reference group.

    Args:
        group: API catalog group id such as `surfaces`, `modules`, or
            `facades`.

    Returns:
        Detached reference group row for that group.

    Raises:
        ValueError: If `group` is not listed in the aggregate API catalog.
    """

    table = get_api_catalog_table()
    for row in table["reference_groups"]:
        if row["id"] == group:
            return _api_catalog_copy_reference_group(row)
    _raise_unknown_api_catalog_key(
        "reference group",
        group,
        "reference groups",
        table["group_index"],
    )


def get_api_catalog_reference_groups() -> list[ApiCatalogReferenceGroupRow]:
    """Return reader-oriented API reference groups.

    Returns:
        Copied rows describing each reference group, the reference kinds it
        owns, the ordered reference ids in that group, and reader-facing usage
        guidance.
    """

    return [_api_catalog_copy_reference_group(row) for row in get_api_catalog_table()["reference_groups"]]


def get_api_catalog_selection(
    reference_id: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> ApiCatalogTable | ApiCatalogRow | list[str]:
    """Return an API catalog payload for one optional selector shape.

    Args:
        reference_id: Optional stable API reference id such as `mcp-api`.
        index_name: Optional index dimension such as `surface` or
            `owner_module`.
        key: Optional concrete index key used with `index_name`.

    Returns:
        Full API catalog table when no selector is passed, one reference row
        for `reference_id`, or one ordered id list for `index_name` and `key`.

    Raises:
        ValueError: If selector arguments are ambiguous or incomplete, or if
            `index_name`/`key` does not identify a supported index value.
        KeyError: If `reference_id` is not listed in the aggregate API catalog.
    """

    index_lookup = index_name is not None or key is not None
    if reference_id is not None and index_lookup:
        raise ValueError("Pass only one API catalog selector: reference_id or index_name/key.")
    if index_lookup and (index_name is None or key is None):
        raise ValueError("index_name requires key, and key requires index_name.")
    if reference_id is not None:
        return get_api_catalog_reference(reference_id)
    if index_name is not None and key is not None:
        return get_api_catalog_reference_ids(index_name, key)
    return get_api_catalog_table()


def render_api_catalog_reference_markdown() -> str:
    """Render the aggregate API catalog as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/api-catalog-reference.md`. The content is generated
        from `get_api_catalog_table()` so the overall API index stays aligned
        with SDK, CLI, REST, MCP, frontend, and generated manual contracts.
    """

    table = get_api_catalog_table()
    sections = api_indexed_reference_sections(
        summary_lines=_api_catalog_summary_lines(table),
        table=table,
        index_specs=_API_CATALOG_INDEX_SPECS,
        fields=_API_CATALOG_STANDARD_FIELDS,
        table_title="API Catalog Table / API Catalog 表",
        list_fields=_API_CATALOG_REFERENCE_LIST_FIELDS,
        markdown_fields=_API_CATALOG_REFERENCE_MARKDOWN_FIELDS,
    )
    return api_reference_markdown(
        title="API Catalog Reference",
        source="paradev.surfaces.get_api_catalog_table()",
        regenerate_when=_API_CATALOG_REGENERATE_WHEN,
        command="rtk uv run paradev api-catalog --markdown > docs/user-manual/api-catalog-reference.md",
        sections=[
            sections[0],
            _api_catalog_reference_group_section(table),
            _api_catalog_index_catalog_section(table),
            *sections[1:],
        ],
    )


def _api_catalog_copy_row(row: Mapping[str, object]) -> ApiCatalogRow:
    copied = dict(row)
    for field in _API_CATALOG_TABLE_ROW_LIST_FIELDS:
        value = copied.get(field)
        if isinstance(value, list):
            copied[field] = [str(item) for item in value]
    return cast(ApiCatalogRow, copied)


def _api_catalog_copy_index_catalog_row(row: ApiCatalogIndexCatalogRow) -> ApiCatalogIndexCatalogRow:
    return {
        "id": row["id"],
        "table_path": row["table_path"],
        "python_helper": row["python_helper"],
        "usage": row["usage"],
    }


def _api_catalog_copy_reference_group(row: ApiCatalogReferenceGroupRow) -> ApiCatalogReferenceGroupRow:
    return {
        "id": row["id"],
        "title": row["title"],
        "reference_count": row["reference_count"],
        "kinds": list(row["kinds"]),
        "reference_ids": list(row["reference_ids"]),
        "usage": row["usage"],
    }


def _api_catalog_copy_summary(summary: ApiCatalogSummary) -> ApiCatalogSummary:
    return {
        "reference_count": summary["reference_count"],
        "layer_count": summary["layer_count"],
        "feature_count": summary["feature_count"],
        "kind_count": summary["kind_count"],
        "reference_group_count": summary["reference_group_count"],
        "index_count": summary["index_count"],
        "owner_module_count": summary["owner_module_count"],
        "surface_count": summary["surface_count"],
        "cli_command_count": summary["cli_command_count"],
        "selector_helper_count": summary["selector_helper_count"],
        "doc_page_count": summary["doc_page_count"],
    }


def _api_catalog_reference_index(index_name: str) -> Mapping[str, list[str]]:
    field = _API_CATALOG_REFERENCE_INDEX_FIELDS.get(index_name)
    if field is None:
        _raise_unknown_api_catalog_key(
            "index",
            index_name,
            "indexes",
            _API_CATALOG_REFERENCE_INDEX_FIELDS,
        )
    index = get_api_catalog_table()[field]
    return cast(Mapping[str, list[str]], index)


def _api_catalog_index_label(index_name: str) -> str:
    return index_name.replace("_", " ")


def _api_catalog_index_choice_label(index_name: str) -> str:
    return f"{_api_catalog_index_label(index_name)}s"


def _raise_unknown_api_catalog_key(
    key_label: str,
    key: str,
    choices_label: str,
    choices: Iterable[object],
    *,
    cause: BaseException | None = None,
) -> NoReturn:
    choices_text = ", ".join(str(choice) for choice in choices)
    raise ValueError(f"Unknown ParaDev API catalog {key_label}: {key}. " f"Available {choices_label}: {choices_text}.") from cause


def _api_catalog_index_catalog_section(table: ApiCatalogTable) -> list[str]:
    return api_table_section(
        "Index Catalog / Index 目录",
        ("Index", "Table Path", "Python Helper", "Use"),
        _api_catalog_index_catalog_table_rows(table),
    )


def _api_catalog_reference_group_section(table: ApiCatalogTable) -> list[str]:
    return api_table_section(
        "Reference Groups / Reference 分组",
        ("Group", "Title", "References", "Kinds", "IDs", "Use"),
        _api_catalog_reference_group_table_rows(table),
        body=("Reader-oriented group map derived from the generated kind index.",),
    )


def _api_catalog_reference_group_table_rows(table: ApiCatalogTable) -> list[str]:
    rows: list[str] = []
    for row in table["reference_groups"]:
        rows.append(
            "| "
            + " | ".join(
                [
                    code_cell(row["id"]),
                    markdown_cell(row["title"]),
                    markdown_cell(row["reference_count"]),
                    code_list_cell(row["kinds"]),
                    code_list_cell(row["reference_ids"]),
                    markdown_cell(row["usage"]),
                ]
            )
            + " |"
        )
    return rows


def _api_catalog_reference_groups(table: Mapping[str, object]) -> list[ApiCatalogReferenceGroupRow]:
    group_index = cast(Mapping[str, list[str]], table["group_index"])
    return [
        {
            "id": group_id,
            "title": title,
            "reference_count": len(group_index[group_id]),
            "kinds": list(kinds),
            "reference_ids": list(group_index[group_id]),
            "usage": usage,
        }
        for group_id, title, kinds, usage in _API_CATALOG_REFERENCE_GROUP_SPECS
    ]


def _api_catalog_reference_group_index(table: Mapping[str, object]) -> dict[str, list[str]]:
    kind_index = cast(Mapping[str, list[str]], table["kind_index"])
    _api_catalog_validate_reference_group_kinds(kind_index)
    return {group_id: _api_catalog_reference_group_ids(kind_index, kinds) for group_id, _, kinds, _ in _API_CATALOG_REFERENCE_GROUP_SPECS}


def _api_catalog_reference_group_ids(kind_index: Mapping[str, list[str]], kinds: Iterable[str]) -> list[str]:
    reference_ids: list[str] = []
    for kind in kinds:
        reference_ids.extend(kind_index.get(kind, []))
    return reference_ids


def _api_catalog_validate_reference_group_kinds(kind_index: Mapping[str, list[str]]) -> None:
    grouped_kinds = [kind for _, _, kinds, _ in _API_CATALOG_REFERENCE_GROUP_SPECS for kind in kinds]
    duplicate_kinds = sorted({kind for kind in grouped_kinds if grouped_kinds.count(kind) > 1})
    if duplicate_kinds:
        raise ValueError(f"duplicate ParaDev API catalog reference group kinds: {', '.join(duplicate_kinds)}")
    kind_names = set(kind_index)
    grouped_kind_names = set(grouped_kinds)
    missing_kinds = sorted(kind_names - grouped_kind_names)
    if missing_kinds:
        raise ValueError(f"missing ParaDev API catalog reference group kinds: {', '.join(missing_kinds)}")
    unused_kinds = sorted(grouped_kind_names - kind_names)
    if unused_kinds:
        raise ValueError(f"unused ParaDev API catalog reference group kinds: {', '.join(unused_kinds)}")


def _api_catalog_index_catalog_rows() -> list[ApiCatalogIndexCatalogRow]:
    return [_api_catalog_copy_index_catalog_row(row) for row in API_CATALOG_INDEX_CATALOG]


def _api_catalog_index_catalog_table_rows(table: ApiCatalogTable) -> list[str]:
    return [
        "| "
        + " | ".join(
            [
                code_cell(row["id"]),
                code_cell(row["table_path"]),
                code_cell(row["python_helper"]),
                markdown_cell(row["usage"]),
            ]
        )
        + " |"
        for row in table["index_catalog"]
    ]


def _api_catalog_summary(table: Mapping[str, object]) -> ApiCatalogSummary:
    return {
        "reference_count": _api_catalog_int_table_field(table, "row_count"),
        "layer_count": _api_catalog_mapping_size(table, "layer_index"),
        "feature_count": _api_catalog_mapping_size(table, "feature_index"),
        "kind_count": _api_catalog_mapping_size(table, "kind_index"),
        "reference_group_count": _api_catalog_list_size(table, "reference_groups"),
        "index_count": _api_catalog_list_size(table, "index_catalog"),
        "owner_module_count": _api_catalog_mapping_size(table, "owner_module_index"),
        "surface_count": _api_catalog_mapping_size(table, "surface_index"),
        "cli_command_count": _api_catalog_mapping_size(table, "cli_command_index"),
        "selector_helper_count": _api_catalog_mapping_size(table, "selector_helper_index"),
        "doc_page_count": _api_catalog_mapping_size(table, "doc_page_index"),
    }


def _api_catalog_int_table_field(table: Mapping[str, object], field: str) -> int:
    value = table[field]
    if isinstance(value, int):
        return value
    raise TypeError(f"ParaDev API catalog table {field} must be an int, not {type(value).__name__}")


def _api_catalog_mapping_size(table: Mapping[str, object], field: str) -> int:
    value = table[field]
    if isinstance(value, Mapping):
        return len(value)
    raise TypeError(f"ParaDev API catalog table {field} must be a mapping, not {type(value).__name__}")


def _api_catalog_list_size(table: Mapping[str, object], field: str) -> int:
    value = table[field]
    if isinstance(value, list):
        return len(value)
    raise TypeError(f"ParaDev API catalog table {field} must be a list, not {type(value).__name__}")


def _api_catalog_summary_lines(table: ApiCatalogTable) -> list[str]:
    summary = table["summary"]
    return [
        f"- References / Reference 数: {summary['reference_count']}",
        f"- Layers / Layer 数: {summary['layer_count']}",
        f"- Features / Feature 数: {summary['feature_count']}",
        f"- Kinds / 类型数: {summary['kind_count']}",
        f"- Reference groups / Reference 分组数: {summary['reference_group_count']}",
        f"- Index dimensions / Index 维度数: {summary['index_count']}",
        f"- Owner modules / Owner Module 数: {summary['owner_module_count']}",
        f"- Surfaces / Surface 数: {summary['surface_count']}",
        f"- CLI commands / CLI 命令数: {summary['cli_command_count']}",
        f"- Selector helpers / Selector helper 数: {summary['selector_helper_count']}",
        f"- Doc pages / Doc page 数: {summary['doc_page_count']}",
    ]


def _api_catalog_row(source: ApiCatalogSourceRow) -> ApiCatalogRow:
    payload = _api_catalog_source_payload(source)
    row: ApiCatalogRow = {
        **source,
        "schema": _api_catalog_payload_schema(payload),
        "row_count": _api_catalog_payload_row_count(source["id"], payload),
        "index_names": _api_catalog_payload_index_names(payload),
        "test_anchor": _API_CATALOG_TEST_ANCHOR,
    }
    return row


def _api_catalog_payload(source_id: str) -> Mapping[str, object]:
    try:
        source = _API_CATALOG_SOURCE_BY_ID[source_id]
    except KeyError as error:
        raise KeyError(f"unknown ParaDev API catalog source {source_id!r}; expected one of: {_api_catalog_known_source_ids()}") from error
    return _api_catalog_source_payload(source)


def _api_catalog_source_payload(source: ApiCatalogSourceRow) -> Mapping[str, object]:
    if source["id"] == "api-catalog":
        _api_catalog_validate_source_helpers(source)
        return _api_catalog_self_payload()
    return _api_catalog_load_payload(source)


def _api_catalog_self_payload() -> Mapping[str, object]:
    return {
        "schema": API_CATALOG_SCHEMA,
        "row_count": len(API_CATALOG_SOURCE_ROWS),
        **_api_catalog_empty_index_payload(),
    }


def _api_catalog_empty_index_payload() -> dict[str, object]:
    return {
        **{index_name: {} for index_name, _ in _API_CATALOG_TABLE_INDEX_SPECS},
        **{index_name: {} for index_name in _API_CATALOG_DERIVED_INDEX_NAMES},
    }


def _api_catalog_load_payload(source: ApiCatalogSourceRow) -> Mapping[str, object]:
    helper = _api_catalog_source_helper(source, "table_helper")
    _api_catalog_source_helper(source, "markdown_helper")
    _api_catalog_source_selector_helper(source)
    payload = helper()
    if isinstance(payload, Mapping):
        return payload
    helper_path = f"{source['owner_module']}.{source['table_helper']}"
    raise TypeError(f"ParaDev API catalog helper {helper_path} returned {type(payload).__name__}; " "expected mapping payload")


def _api_catalog_validate_source_helpers(source: ApiCatalogSourceRow) -> None:
    _api_catalog_source_helper(source, "table_helper")
    _api_catalog_source_helper(source, "markdown_helper")
    _api_catalog_source_selector_helper(source)


def _api_catalog_source_selector_helper(source: ApiCatalogSourceRow) -> Callable[..., object] | None:
    if not source["selector_helper"]:
        return None
    return _api_catalog_source_helper(source, "selector_helper")


def _api_catalog_source_helper(
    source: ApiCatalogSourceRow,
    field: Literal["table_helper", "selector_helper", "markdown_helper"],
) -> Callable[..., object]:
    helper_name = source[field]
    helper_path = f"{source['owner_module']}.{helper_name}"
    try:
        helper = getattr(import_module(source["owner_module"]), helper_name)
    except AttributeError as error:
        raise AttributeError(f"ParaDev API catalog source {source['id']!r} {field} {helper_path} is missing") from error
    if callable(helper):
        return cast(Callable[..., object], helper)
    raise TypeError(f"ParaDev API catalog source {source['id']!r} {field} {helper_path} " f"must be callable, got {type(helper).__name__}")


def _api_catalog_known_source_ids() -> str:
    return ", ".join(_API_CATALOG_SOURCE_IDS)


def _api_catalog_payload_schema(payload: Mapping[str, object]) -> str:
    schema = payload.get("schema")
    return schema if isinstance(schema, str) else ""


def _api_catalog_payload_row_count(source_id: str, payload: Mapping[str, object]) -> int:
    for count in (_api_catalog_int_payload_field(payload, "row_count"), _api_catalog_summary_operation_count(payload)):
        if count is not None:
            return count
    return _api_catalog_source_row_count(source_id, payload)


def _api_catalog_int_payload_field(payload: Mapping[str, object], field: str) -> int | None:
    value = payload.get(field)
    return value if isinstance(value, int) else None


def _api_catalog_summary_operation_count(payload: Mapping[str, object]) -> int | None:
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        return None
    return _api_catalog_int_payload_field(summary, "operation_count")


def _api_catalog_source_row_count(source_id: str, payload: Mapping[str, object]) -> int:
    field = _API_CATALOG_ROW_COUNT_FALLBACK_FIELDS.get(source_id)
    return _api_catalog_payload_field_count(payload, field) if field is not None else 0


def _api_catalog_payload_field_count(payload: Mapping[str, object], field: str) -> int:
    value = payload.get(field)
    if isinstance(value, int):
        return value
    return len(value) if isinstance(value, list) else 0


def _api_catalog_payload_index_names(payload: Mapping[str, object]) -> list[str]:
    names = _api_catalog_top_level_index_names(payload)
    index = payload.get("index")
    if isinstance(index, Mapping):
        if _api_catalog_flat_index(index):
            names.append("index")
        else:
            names.extend(_api_catalog_nested_index_names(index))
    return names


def _api_catalog_top_level_index_names(payload: Mapping[str, object]) -> list[str]:
    return sorted(key for key, value in payload.items() if key.endswith("_index") and isinstance(value, Mapping))


def _api_catalog_flat_index(index: Mapping[str, object]) -> bool:
    return all(not isinstance(value, (Mapping, list, tuple, set)) for value in index.values())


def _api_catalog_nested_index_names(index: Mapping[str, object]) -> list[str]:
    return [f"index.{key}" for key in sorted(str(key) for key in index)]
