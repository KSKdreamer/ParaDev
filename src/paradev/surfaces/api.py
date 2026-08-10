"""Generated facade API table for public surface exports."""

from __future__ import annotations

import inspect
from dataclasses import is_dataclass
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

SURFACES_API_TABLE_SCHEMA = "paradev.surfaces.api-table.v1"
_SURFACES_API_REFERENCE_PAGE = "docs/user-manual/surfaces-api-reference.md"
_SURFACES_API_TEST_ANCHOR = "tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade"
_SURFACES_API_SYMBOLS = {
    "SURFACES_API_TABLE_SCHEMA",
    "SurfacesApiRow",
    "SurfacesApiTable",
    "get_surfaces_api_selection",
    "get_surfaces_api_table",
    "render_surfaces_api_reference_markdown",
}
_SURFACES_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")
_API_CATALOG_SYMBOLS = {
    "API_CATALOG_INDEX_CATALOG",
    "API_CATALOG_SCHEMA",
    "API_CATALOG_SOURCE_ROWS",
    "ApiCatalogIndexCatalogRow",
    "ApiCatalogReferenceGroupRow",
    "ApiCatalogRow",
    "ApiCatalogSourceRow",
    "ApiCatalogSummary",
    "ApiCatalogTable",
    "get_api_catalog_group_reference_ids",
    "get_api_catalog_reference_group",
    "get_api_catalog_reference_groups",
    "get_api_catalog_index_catalog",
    "get_api_catalog_reference",
    "get_api_catalog_reference_ids",
    "get_api_catalog_selection",
    "get_api_catalog_summary",
    "get_api_catalog_table",
    "render_api_catalog_reference_markdown",
}
_SURFACE_CONTRACT_SYMBOLS = {
    "SURFACE_CONTRACT_IDS",
    "SURFACE_CONTRACT_INDEX_CATALOG",
    "SURFACE_CONTRACT_SUMMARY_SCHEMA",
    "SurfaceContractIdentifier",
    "SurfaceContractIndexCatalogRow",
    "SurfaceContractPayload",
    "SurfaceContractSummary",
    "SurfaceContractSummaryRow",
    "get_surface_contract",
    "get_surface_contract_ids",
    "get_surface_contract_index_catalog",
    "get_surface_contract_selection",
    "get_surface_contract_summary",
    "get_surface_contract_summary_row",
    "get_surface_contract_status_ids",
    "get_surface_contracts",
    "render_surface_contract_reference_markdown",
}
_TYPE_ALIAS_SYMBOLS = {
    "SurfaceContractIdentifier",
    "SurfaceContractPayload",
}


class SurfacesApiRow(TypedDict):
    """One public `paradev.surfaces` facade API row."""

    symbol: str
    kind: str
    layer: str
    module: str
    feature: str
    import_path: str
    returns: str
    value: str
    registry_seam: str
    surface: str
    doc_page: str
    test_anchor: str


class SurfacesApiTable(TypedDict):
    """Generated API-standard table for the surface facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[SurfacesApiRow]


def get_surfaces_api_table() -> SurfacesApiTable:
    """Return the API-standard table for the public surface facade.

    Returns:
        JSON-safe table derived from `paradev.surfaces.__all__`, with copied
        rows and indexes for surface module, feature, and symbol-kind audits.
    """

    return cast(SurfacesApiTable, api_standard_table(SURFACES_API_TABLE_SCHEMA, _surfaces_api_rows()))


def get_surfaces_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> SurfacesApiTable | SurfacesApiRow | list[str]:
    """Return the surfaces facade table, one row, or one index projection.

    Args:
        symbol: Optional public facade symbol such as `get_rest_api_selection`.
        index_name: Optional index payload name such as `module_index`,
            `feature_index`, or `kind_index`.
        key: Optional concrete index key used with `index_name`.

    Returns:
        Full surfaces facade table, one facade row, or one ordered symbol list.

    Raises:
        ValueError: If selector arguments are ambiguous, incomplete, or use an
            unsupported index.
        KeyError: If `symbol` does not match a surfaces facade row.
    """

    return cast(
        SurfacesApiTable | SurfacesApiRow | list[str],
        api_table_selection(
            get_surfaces_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_SURFACES_API_INDEX_NAMES,
        ),
    )


def render_surfaces_api_reference_markdown() -> str:
    """Render the public surface facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/surfaces-api-reference.md`. The content is generated
        from `get_surfaces_api_table()` so the surface facade, CLI command,
        aggregate catalog, and tests stay aligned.
    """

    table = get_surfaces_api_table()
    return api_standard_reference_markdown(
        title="Surfaces API Reference",
        source="paradev.surfaces.get_surfaces_api_table()",
        regenerate_when="Regenerate this file whenever the public `paradev.surfaces` facade changes:",
        command="rtk uv run paradev surfaces-api --markdown > docs/user-manual/surfaces-api-reference.md",
        table=table,
        module_label="Surface",
    )


def _surfaces_api_rows() -> list[SurfacesApiRow]:
    import paradev.surfaces as surfaces

    rows: list[SurfacesApiRow] = []
    for symbol in surfaces.__all__:
        value = getattr(surfaces, symbol)
        module = _surfaces_api_module(symbol, value)
        feature = _surfaces_api_feature(symbol, module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _surfaces_api_kind(symbol, value),
                "layer": "surface",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.surfaces.{symbol}",
                "returns": _surfaces_api_returns(symbol, value),
                "value": _surfaces_api_value(symbol, value),
                "registry_seam": _surfaces_api_registry_seam(module),
                "surface": _surfaces_api_surface(module),
                "doc_page": _surfaces_api_doc_page(module),
                "test_anchor": _SURFACES_API_TEST_ANCHOR,
            }
        )
    return rows


def _surfaces_api_module(symbol: str, value: object) -> str:
    if symbol in _SURFACES_API_SYMBOLS:
        return "api"
    if symbol in _API_CATALOG_SYMBOLS:
        return "api_catalog"
    if symbol in _SURFACE_CONTRACT_SYMBOLS:
        return "surface_contracts"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev.surfaces."):
        return module.removeprefix("paradev.surfaces.")
    if module == "paradev.surfaces":
        return "surface_contracts"
    return "surfaces"


def _surfaces_api_feature(symbol: str, module: str) -> str:
    if module == "api":
        return "surfaces-api"
    if module == "api_catalog":
        return "api-catalog"
    if module == "surface_contracts":
        return "surface-contracts"
    if module == "rest" and symbol == "get_openapi_seed":
        return "openapi"
    if module in {"bundle", "cli", "lsp", "mcp", "rest", "vscode"}:
        return module
    return "surfaces"


def _surfaces_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if symbol in _TYPE_ALIAS_SYMBOLS:
        return "type alias"
    if is_typeddict(value):
        return "TypedDict"
    if is_dataclass(value):
        return "dataclass"
    if inspect.isclass(value):
        return "class"
    if inspect.isfunction(value):
        return "function"
    if isinstance(value, tuple):
        return "tuple constant"
    return type(value).__name__


def _surfaces_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if symbol in _TYPE_ALIAS_SYMBOLS:
        return "TypeAlias"
    if is_typeddict(value):
        return "TypedDict schema"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation)
    if inspect.isclass(value):
        return f"{value.__name__} class"
    if isinstance(value, tuple):
        return f"tuple[{len(value)}]"
    return type(value).__name__


def _surfaces_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if isinstance(value, tuple):
        return f"{len(value)} items"
    return ""


def _surfaces_api_registry_seam(module: str) -> str:
    if module == "api":
        return "surface facade API table"
    if module == "api_catalog":
        return "API reference catalog"
    if module == "surface_contracts":
        return "surface contract catalog"
    if module == "cli":
        return "Typer command registry"
    if module == "rest":
        return "REST/OpenAPI route contract"
    if module == "mcp":
        return "MCP tool contract"
    if module == "lsp":
        return "LSP stdio contract"
    if module == "bundle":
        return "desktop bundle contract"
    if module == "vscode":
        return "VS Code extension contract"
    return "none"


def _surfaces_api_surface(module: str) -> str:
    if module in {"bundle", "cli", "lsp", "mcp", "rest", "vscode"}:
        return module
    return "sdk"


def _surfaces_api_doc_page(module: str) -> str:
    if module == "api":
        return _SURFACES_API_REFERENCE_PAGE
    if module == "api_catalog":
        return "docs/user-manual/api-catalog-reference.md"
    if module == "surface_contracts":
        return "docs/user-manual/surface-contract-reference.md"
    if module == "cli":
        return "docs/user-manual/cli-api-reference.md"
    if module == "rest":
        return "docs/user-manual/rest-api-reference.md"
    if module == "mcp":
        return "docs/user-manual/mcp-api-reference.md"
    if module == "lsp":
        return "docs/user-manual/lsp-api-reference.md"
    if module in {"bundle", "vscode"}:
        return "docs/architecture/interfaces.md"
    return "docs/user-manual/sdk-python.md"
