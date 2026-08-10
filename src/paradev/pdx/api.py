"""Generated facade API table for public PDX exports."""

from __future__ import annotations

import inspect
from dataclasses import is_dataclass
from enum import Enum
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

PDX_CORE_API_TABLE_SCHEMA = "paradev.pdx.core-api-table.v1"
_PDX_CORE_API_REFERENCE_PAGE = "docs/user-manual/pdx-core-api-reference.md"
_PDX_CORE_API_TEST_ANCHOR = "tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade"
_PDX_CORE_API_SYMBOLS = {
    "PDX_CORE_API_TABLE_SCHEMA",
    "PdxCoreApiRow",
    "PdxCoreApiTable",
    "get_pdx_core_api_selection",
    "get_pdx_core_api_table",
    "render_pdx_core_api_reference_markdown",
}
_PDX_CORE_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")
_SCALAR_SYMBOLS = {
    "SCALAR_BOOL",
    "SCALAR_COLOR",
    "SCALAR_ID",
    "SCALAR_NUM",
    "SCALAR_STR",
    "SCALAR_VAR",
}


class PdxCoreApiRow(TypedDict):
    """One public `paradev.pdx` facade API row."""

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


class PdxCoreApiTable(TypedDict):
    """Generated API-standard table for the PDX parser facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[PdxCoreApiRow]


def get_pdx_core_api_table() -> PdxCoreApiTable:
    """Return the API-standard table for the public PDX parser facade.

    Returns:
        JSON-safe table derived from `paradev.pdx.__all__`, with copied rows
        and indexes for parser module, feature, and symbol-kind audits.
    """

    return cast(PdxCoreApiTable, api_standard_table(PDX_CORE_API_TABLE_SCHEMA, _pdx_core_api_rows()))


def get_pdx_core_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> PdxCoreApiTable | PdxCoreApiRow | list[str]:
    """Return the full PDX core API table, one row, or one index bucket.

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
        PdxCoreApiTable | PdxCoreApiRow | list[str],
        api_table_selection(
            get_pdx_core_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_PDX_CORE_API_INDEX_NAMES,
        ),
    )


def render_pdx_core_api_reference_markdown() -> str:
    """Render the public PDX parser facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/pdx-core-api-reference.md`. The content is
        generated from `get_pdx_core_api_table()` so the tokenizer, AST,
        diagnostics, parser, and facade helper exports stay aligned.
    """

    table = get_pdx_core_api_table()
    return api_standard_reference_markdown(
        title="PDX Core API Reference",
        source="paradev.pdx.get_pdx_core_api_table()",
        regenerate_when="Regenerate this file whenever the public `paradev.pdx` facade changes:",
        command="rtk uv run paradev pdx-core-api --markdown > docs/user-manual/pdx-core-api-reference.md",
        table=table,
        module_label="PDX",
    )


def _pdx_core_api_rows() -> list[PdxCoreApiRow]:
    import paradev.pdx as pdx

    rows: list[PdxCoreApiRow] = []
    for symbol in pdx.__all__:
        value = getattr(pdx, symbol)
        module = _pdx_core_api_module(symbol, value)
        feature = _pdx_core_api_feature(symbol, module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _pdx_core_api_kind(symbol, value),
                "layer": "pdx",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.pdx.{symbol}",
                "returns": _pdx_core_api_returns(symbol, value),
                "value": _pdx_core_api_value(symbol, value),
                "registry_seam": _pdx_core_api_registry_seam(module),
                "surface": "sdk",
                "doc_page": _pdx_core_api_doc_page(module),
                "test_anchor": _PDX_CORE_API_TEST_ANCHOR,
            }
        )
    return rows


def _pdx_core_api_module(symbol: str, value: object) -> str:
    if symbol in _PDX_CORE_API_SYMBOLS:
        return "api"
    if symbol in _SCALAR_SYMBOLS:
        return "ast"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev.pdx."):
        return module.removeprefix("paradev.pdx.")
    return "pdx"


def _pdx_core_api_feature(symbol: str, module: str) -> str:
    if module == "api":
        return "pdx-core-api"
    if symbol in _SCALAR_SYMBOLS:
        return "scalars"
    if module == "ast":
        return "ast"
    if module == "diagnostics":
        return "diagnostics"
    if module == "parser":
        return "parser"
    if module == "token":
        return "tokens"
    return "pdx-core"


def _pdx_core_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if symbol in _SCALAR_SYMBOLS:
        return "scalar constant"
    if is_typeddict(value):
        return "TypedDict"
    if is_dataclass(value):
        return "dataclass"
    if inspect.isclass(value):
        if issubclass(value, Exception):
            return "exception"
        if issubclass(value, Enum):
            return "enum"
        return "class"
    if inspect.isfunction(value):
        return "function"
    return type(value).__name__


def _pdx_core_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if symbol in _SCALAR_SYMBOLS:
        return "str"
    if is_typeddict(value):
        return "TypedDict schema"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation, drop_collections_abc=True)
    if inspect.isclass(value):
        return f"{value.__name__} class"
    return type(value).__name__


def _pdx_core_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA") or symbol in _SCALAR_SYMBOLS:
        return str(value)
    return ""


def _pdx_core_api_registry_seam(module: str) -> str:
    if module == "api":
        return "PDX core facade API table"
    if module == "ast":
        return "PDX AST contract"
    if module == "diagnostics":
        return "PDX diagnostic contract"
    if module == "parser":
        return "PDX parser contract"
    if module == "token":
        return "PDX token stream contract"
    return "none"


def _pdx_core_api_doc_page(module: str) -> str:
    if module == "api":
        return _PDX_CORE_API_REFERENCE_PAGE
    return "docs/user-manual/pdx-core-api-reference.md"
