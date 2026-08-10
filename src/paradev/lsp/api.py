"""Generated facade API table for public LSP server exports."""

from __future__ import annotations

import inspect
from dataclasses import is_dataclass
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

LSP_SERVER_API_TABLE_SCHEMA = "paradev.lsp.server-api-table.v1"
_LSP_SERVER_API_REFERENCE_PAGE = "docs/user-manual/lsp-server-api-reference.md"
_LSP_SERVER_API_TEST_ANCHOR = "tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade"
_LSP_SERVER_API_SYMBOLS = {
    "LSP_SERVER_API_TABLE_SCHEMA",
    "LspServerApiRow",
    "LspServerApiTable",
    "get_lsp_server_api_selection",
    "get_lsp_server_api_table",
    "render_lsp_server_api_reference_markdown",
}
_LSP_SERVER_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")


class LspServerApiRow(TypedDict):
    """One public `paradev.lsp` facade API row."""

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


class LspServerApiTable(TypedDict):
    """Generated API-standard table for the LSP server facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[LspServerApiRow]


def get_lsp_server_api_table() -> LspServerApiTable:
    """Return the API-standard table for the public LSP server facade.

    Returns:
        JSON-safe table derived from `paradev.lsp.__all__`, with copied rows
        and indexes for LSP server module, feature, and symbol-kind audits.
    """

    return cast(LspServerApiTable, api_standard_table(LSP_SERVER_API_TABLE_SCHEMA, _lsp_server_api_rows()))


def get_lsp_server_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> LspServerApiTable | LspServerApiRow | list[str]:
    """Return the full LSP server API table, one row, or one index bucket.

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
        LspServerApiTable | LspServerApiRow | list[str],
        api_table_selection(
            get_lsp_server_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_LSP_SERVER_API_INDEX_NAMES,
        ),
    )


def render_lsp_server_api_reference_markdown() -> str:
    """Render the public LSP server facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/lsp-server-api-reference.md`. The content is
        generated from `get_lsp_server_api_table()` so stdio, JSON-RPC server,
        document, and facade helper exports stay aligned.
    """

    table = get_lsp_server_api_table()
    return api_standard_reference_markdown(
        title="LSP Server API Reference",
        source="paradev.lsp.get_lsp_server_api_table()",
        regenerate_when="Regenerate this file whenever the public `paradev.lsp` facade changes:",
        command="rtk uv run paradev lsp-server-api --markdown > docs/user-manual/lsp-server-api-reference.md",
        table=table,
        module_label="LSP",
    )


def _lsp_server_api_rows() -> list[LspServerApiRow]:
    import paradev.lsp as lsp

    rows: list[LspServerApiRow] = []
    for symbol in lsp.__all__:
        value = getattr(lsp, symbol)
        module = _lsp_server_api_module(symbol, value)
        feature = _lsp_server_api_feature(symbol, module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _lsp_server_api_kind(symbol, value),
                "layer": "lsp",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.lsp.{symbol}",
                "returns": _lsp_server_api_returns(symbol, value),
                "value": _lsp_server_api_value(symbol, value),
                "registry_seam": _lsp_server_api_registry_seam(symbol, feature),
                "surface": "lsp",
                "doc_page": _LSP_SERVER_API_REFERENCE_PAGE,
                "test_anchor": _LSP_SERVER_API_TEST_ANCHOR,
            }
        )
    return rows


def _lsp_server_api_module(symbol: str, value: object) -> str:
    if symbol in _LSP_SERVER_API_SYMBOLS:
        return "api"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev.lsp."):
        return module.removeprefix("paradev.lsp.")
    if module == "paradev.lsp":
        return "server"
    return "lsp"


def _lsp_server_api_feature(symbol: str, module: str) -> str:
    if module == "api":
        return "lsp-server-api"
    if symbol == "PdxDocument":
        return "documents"
    if symbol == "PdxLanguageServer":
        return "server"
    if symbol == "serve_pdx_lsp_stdio":
        return "stdio"
    if symbol in {"read_lsp_message", "write_lsp_message"}:
        return "framing"
    return "server"


def _lsp_server_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if is_typeddict(value):
        return "TypedDict"
    if is_dataclass(value):
        return "dataclass"
    if inspect.isclass(value):
        return "class"
    if inspect.isfunction(value):
        return "function"
    return type(value).__name__


def _lsp_server_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if is_typeddict(value):
        return "TypedDict schema"
    if is_dataclass(value) or inspect.isclass(value):
        return "class"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation, drop_collections_abc=True)
    return type(value).__name__


def _lsp_server_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    return ""


def _lsp_server_api_registry_seam(symbol: str, feature: str) -> str:
    if feature == "lsp-server-api":
        return "LSP server facade API table"
    if symbol == "PdxDocument":
        return "LSP document cache"
    if symbol == "PdxLanguageServer":
        return "LSP JSON-RPC dispatcher"
    if feature == "stdio":
        return "LSP stdio server"
    if feature == "framing":
        return "LSP stdio framing"
    return "none"
