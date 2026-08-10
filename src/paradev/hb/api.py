"""Generated facade API table for public HeavenBase exports."""

from __future__ import annotations

import inspect
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

HB_API_TABLE_SCHEMA = "paradev.hb.api-table.v1"
_HB_API_REFERENCE_PAGE = "docs/user-manual/hb-api-reference.md"
_CATALOG_API_REFERENCE_PAGE = "docs/user-manual/catalog-api-reference.md"
_HB_API_TEST_ANCHOR = "tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade"
_HB_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")
_HB_API_SYMBOLS = {
    "HB_API_TABLE_SCHEMA",
    "HbApiRow",
    "HbApiTable",
    "get_hb_api_selection",
    "get_hb_api_table",
    "render_hb_api_reference_markdown",
}
_CATALOG_API_SYMBOLS = {
    "CATALOG_API_TABLE_ROWS",
    "CATALOG_API_TABLE_SCHEMA",
    "CATALOG_SCHEMA",
    "CatalogApiRow",
    "CatalogApiTable",
    "ENTITY_TYPES",
    "QUERY_SCHEMA",
    "REFRESH_SCHEMA",
    "SMOKE_SCHEMA",
    "STATUS_SCHEMA",
    "WRITE_SCHEMA",
    "catalog_completion_items",
    "catalog_preview",
    "catalog_query",
    "catalog_refresh",
    "catalog_smoke",
    "catalog_status",
    "catalog_write",
    "get_catalog_api_table",
    "render_catalog_api_reference_markdown",
}
_SCHEMA_FEATURES = {
    "CATALOG_API_TABLE_SCHEMA": "catalog-api",
    "CATALOG_SCHEMA": "preview",
    "QUERY_SCHEMA": "query",
    "REFRESH_SCHEMA": "refresh",
    "SMOKE_SCHEMA": "smoke",
    "STATUS_SCHEMA": "status",
    "WRITE_SCHEMA": "write",
}
_FUNCTION_FEATURES = {
    "catalog_completion_items": "completion",
    "catalog_preview": "preview",
    "catalog_query": "query",
    "catalog_refresh": "refresh",
    "catalog_smoke": "smoke",
    "catalog_status": "status",
    "catalog_write": "write",
    "get_catalog_api_table": "catalog-api",
    "render_catalog_api_reference_markdown": "catalog-api",
}


class HbApiRow(TypedDict):
    """One public `paradev.hb` facade API row."""

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


class HbApiTable(TypedDict):
    """Generated API-standard table for the HeavenBase facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[HbApiRow]


def get_hb_api_table() -> HbApiTable:
    """Return the API-standard table for the public HeavenBase facade.

    Returns:
        JSON-safe table derived from `paradev.hb.__all__`, with copied rows
        and indexes for HeavenBase module, feature, and symbol-kind audits.
    """

    return cast(HbApiTable, api_standard_table(HB_API_TABLE_SCHEMA, _hb_api_rows()))


def get_hb_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> HbApiTable | HbApiRow | list[str]:
    """Return the full HeavenBase facade API table, one row, or one index bucket.

    Args:
        symbol: Optional public symbol to select from the table rows.
        index_name: Optional index name, such as `module_index`,
            `feature_index`, or `kind_index`.
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
        HbApiTable | HbApiRow | list[str],
        api_table_selection(
            get_hb_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_HB_API_INDEX_NAMES,
        ),
    )


def render_hb_api_reference_markdown() -> str:
    """Render the public HeavenBase facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/hb-api-reference.md`. The content is generated
        from `get_hb_api_table()` so catalog helper exports and facade table
        helpers stay aligned with `paradev.hb.__all__`.
    """

    table = get_hb_api_table()
    return api_standard_reference_markdown(
        title="HeavenBase Facade API Reference",
        source="paradev.hb.get_hb_api_table()",
        regenerate_when="Regenerate this file whenever the public `paradev.hb` facade changes:",
        command="rtk uv run paradev hb-api --markdown > docs/user-manual/hb-api-reference.md",
        table=table,
        module_label="HeavenBase",
    )


def _hb_api_rows() -> list[HbApiRow]:
    import paradev.hb as hb

    rows: list[HbApiRow] = []
    for symbol in hb.__all__:
        value = getattr(hb, symbol)
        module = _hb_api_module(symbol, value)
        feature = _hb_api_feature(symbol, module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _hb_api_kind(symbol, value),
                "layer": "hb",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.hb.{symbol}",
                "returns": _hb_api_returns(symbol, value),
                "value": _hb_api_value(symbol, value),
                "registry_seam": _hb_api_registry_seam(symbol, feature),
                "surface": "sdk",
                "doc_page": _hb_api_doc_page(module),
                "test_anchor": _HB_API_TEST_ANCHOR,
            }
        )
    return rows


def _hb_api_module(symbol: str, value: object) -> str:
    if symbol in _HB_API_SYMBOLS:
        return "api"
    if symbol in _CATALOG_API_SYMBOLS:
        return "catalog"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev.hb."):
        return module.removeprefix("paradev.hb.")
    if module == "paradev.hb":
        return "catalog"
    return "hb"


def _hb_api_feature(symbol: str, module: str) -> str:
    if module == "api":
        return "hb-api"
    if symbol in {"CATALOG_API_TABLE_ROWS", "CatalogApiRow", "CatalogApiTable"}:
        return "catalog-api"
    if symbol in _SCHEMA_FEATURES:
        return _SCHEMA_FEATURES[symbol]
    if symbol in _FUNCTION_FEATURES:
        return _FUNCTION_FEATURES[symbol]
    if symbol == "ENTITY_TYPES":
        return "entities"
    return "catalog"


def _hb_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if symbol in {"CATALOG_API_TABLE_ROWS", "ENTITY_TYPES"}:
        return "tuple constant"
    if is_typeddict(value):
        return "TypedDict"
    if inspect.isfunction(value):
        return "function"
    return type(value).__name__


def _hb_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if symbol in {"CATALOG_API_TABLE_ROWS", "ENTITY_TYPES"}:
        try:
            return f"tuple[{len(value)}]"
        except TypeError:
            return "tuple"
    if is_typeddict(value):
        return "TypedDict schema"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation, drop_collections_abc=True)
    return type(value).__name__


def _hb_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if symbol == "CATALOG_API_TABLE_ROWS":
        return f"{len(value)} rows"
    if symbol == "ENTITY_TYPES":
        return f"{len(value)} entity types"
    return ""


def _hb_api_registry_seam(symbol: str, feature: str) -> str:
    if feature == "hb-api":
        return "HeavenBase facade API table"
    if symbol == "ENTITY_TYPES":
        return "HOI4 HeavenBase extension registry"
    if feature in {"write", "refresh"}:
        return "HeavenBase SQLite backend"
    if feature == "completion":
        return "LSP catalog completion"
    if feature in {"preview", "smoke", "query", "status"}:
        return "HeavenBase catalog integration"
    if feature == "catalog-api":
        return "catalog API reference table"
    return "none"


def _hb_api_doc_page(module: str) -> str:
    if module == "api":
        return _HB_API_REFERENCE_PAGE
    return _CATALOG_API_REFERENCE_PAGE
