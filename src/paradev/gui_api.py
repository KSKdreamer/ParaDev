"""Generated facade API table for public GUI launcher exports."""

from __future__ import annotations

import inspect
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

GUI_API_TABLE_SCHEMA = "paradev.gui.api-table.v1"
_GUI_API_REFERENCE_PAGE = "docs/user-manual/gui-api-reference.md"
_GUI_API_TEST_ANCHOR = "tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade"
_GUI_API_SYMBOLS = {
    "GUI_API_TABLE_SCHEMA",
    "GuiApiRow",
    "GuiApiTable",
    "get_gui_api_selection",
    "get_gui_api_table",
    "render_gui_api_reference_markdown",
}
_GUI_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")


class GuiApiRow(TypedDict):
    """One public `paradev.gui` launcher API row."""

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


class GuiApiTable(TypedDict):
    """Generated API-standard table for the GUI launcher facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[GuiApiRow]


def get_gui_api_table() -> GuiApiTable:
    """Return the API-standard table for the public GUI launcher facade.

    Returns:
        JSON-safe table derived from `paradev.gui.__all__`, with copied rows
        and indexes for launcher module, feature, and symbol-kind audits.
    """

    return cast(GuiApiTable, api_standard_table(GUI_API_TABLE_SCHEMA, _gui_api_rows()))


def get_gui_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> GuiApiTable | GuiApiRow | list[str]:
    """Return the full GUI API table, one row, or one index bucket.

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
        GuiApiTable | GuiApiRow | list[str],
        api_table_selection(
            get_gui_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_GUI_API_INDEX_NAMES,
        ),
    )


def render_gui_api_reference_markdown() -> str:
    """Render the public GUI launcher facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/gui-api-reference.md`. The content is generated
        from `get_gui_api_table()` so the installed GUI script, parser helper,
        CLI command, and manual page stay aligned.
    """

    table = get_gui_api_table()
    return api_standard_reference_markdown(
        title="GUI API Reference",
        source="paradev.gui.get_gui_api_table()",
        regenerate_when="Regenerate this file whenever the public `paradev.gui` launcher facade changes:",
        command="rtk uv run paradev gui-api --markdown > docs/user-manual/gui-api-reference.md",
        table=table,
        module_label="GUI",
    )


def _gui_api_rows() -> list[GuiApiRow]:
    import paradev.gui as gui

    rows: list[GuiApiRow] = []
    for symbol in gui.__all__:
        value = getattr(gui, symbol)
        module = _gui_api_module(symbol, value)
        feature = _gui_api_feature(module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _gui_api_kind(symbol, value),
                "layer": "gui",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.gui.{symbol}",
                "returns": _gui_api_returns(symbol, value),
                "value": _gui_api_value(symbol, value),
                "registry_seam": _gui_api_registry_seam(feature),
                "surface": "desktop" if feature == "launcher" else "sdk",
                "doc_page": _GUI_API_REFERENCE_PAGE,
                "test_anchor": _GUI_API_TEST_ANCHOR,
            }
        )
    return rows


def _gui_api_module(symbol: str, value: object) -> str:
    if symbol in _GUI_API_SYMBOLS:
        return "gui_api"
    if symbol in {"build_parser", "main"}:
        return "gui"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev."):
        return module.removeprefix("paradev.")
    return "gui"


def _gui_api_feature(module: str) -> str:
    if module == "gui_api":
        return "gui-api"
    return "launcher"


def _gui_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if is_typeddict(value):
        return "TypedDict"
    if inspect.isfunction(value):
        return "function"
    return type(value).__name__


def _gui_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if is_typeddict(value):
        return "TypedDict schema"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation)
    return type(value).__name__


def _gui_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    return ""


def _gui_api_registry_seam(feature: str) -> str:
    if feature == "gui-api":
        return "GUI facade API table"
    return "Python GUI script entry point"
