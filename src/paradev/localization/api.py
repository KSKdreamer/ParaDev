"""Generated facade API table for public localization package exports."""

from __future__ import annotations

import inspect
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

LOCALIZATION_API_TABLE_SCHEMA = "paradev.localization.api-table.v1"
_LOCALIZATION_API_REFERENCE_PAGE = "docs/user-manual/localization-api-reference.md"
_LOCALIZATION_API_TEST_ANCHOR = "tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade"
_LOCALIZATION_API_SYMBOLS = {
    "LOCALIZATION_API_TABLE_SCHEMA",
    "LocalizationApiRow",
    "LocalizationApiTable",
    "get_localization_api_selection",
    "get_localization_api_table",
    "render_localization_api_reference_markdown",
}
_LOCALIZATION_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")


class LocalizationApiRow(TypedDict):
    """One public `paradev.localization` facade API row."""

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


class LocalizationApiTable(TypedDict):
    """Generated API-standard table for the localization package facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[LocalizationApiRow]


def get_localization_api_table() -> LocalizationApiTable:
    """Return the API-standard table for the public localization facade.

    Returns:
        JSON-safe table derived from `paradev.localization.__all__`, with
        copied rows and indexes for localization module, feature, and
        symbol-kind audits.
    """

    return cast(LocalizationApiTable, api_standard_table(LOCALIZATION_API_TABLE_SCHEMA, _localization_api_rows()))


def get_localization_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> LocalizationApiTable | LocalizationApiRow | list[str]:
    """Return the localization facade table, one row, or one index projection.

    Args:
        symbol: Optional public facade symbol such as `canonical_language`.
        index_name: Optional index payload name such as `module_index`,
            `feature_index`, or `kind_index`.
        key: Optional concrete index key used with `index_name`.

    Returns:
        Full localization facade table, one facade row, or one ordered symbol list.

    Raises:
        ValueError: If selector arguments are ambiguous, incomplete, or use an
            unsupported index.
        KeyError: If `symbol` does not match a localization facade row.
    """

    return cast(
        LocalizationApiTable | LocalizationApiRow | list[str],
        api_table_selection(
            get_localization_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_LOCALIZATION_API_INDEX_NAMES,
        ),
    )


def render_localization_api_reference_markdown() -> str:
    """Render the public localization facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/localization-api-reference.md`. The content is
        generated from `get_localization_api_table()` so the language helper
        facade, CLI command, and manual page stay aligned.
    """

    table = get_localization_api_table()
    return api_standard_reference_markdown(
        title="Localization API Reference",
        source="paradev.localization.get_localization_api_table()",
        regenerate_when="Regenerate this file whenever the public `paradev.localization` facade changes:",
        command="rtk uv run paradev localization-api --markdown > docs/user-manual/localization-api-reference.md",
        table=table,
        module_label="Localization",
    )


def _localization_api_rows() -> list[LocalizationApiRow]:
    import paradev.localization as localization

    rows: list[LocalizationApiRow] = []
    for symbol in localization.__all__:
        value = getattr(localization, symbol)
        module = _localization_api_module(symbol, value)
        feature = _localization_api_feature(symbol, module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _localization_api_kind(symbol, value),
                "layer": "localization",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.localization.{symbol}",
                "returns": _localization_api_returns(symbol, value),
                "value": _localization_api_value(symbol, value),
                "registry_seam": _localization_api_registry_seam(feature),
                "surface": "sdk",
                "doc_page": _LOCALIZATION_API_REFERENCE_PAGE,
                "test_anchor": _LOCALIZATION_API_TEST_ANCHOR,
            }
        )
    return rows


def _localization_api_module(symbol: str, value: object) -> str:
    if symbol in _LOCALIZATION_API_SYMBOLS:
        return "api"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev."):
        return module.removeprefix("paradev.")
    return "localization"


def _localization_api_feature(symbol: str, module: str) -> str:
    if module == "api":
        return "localization-api"
    return "languages"


def _localization_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if is_typeddict(value):
        return "TypedDict"
    if inspect.isfunction(value):
        return "function"
    if isinstance(value, dict):
        return "dict constant"
    return type(value).__name__


def _localization_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if is_typeddict(value):
        return "TypedDict schema"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation, prefer_builtins_qualname=True, use_name=False)
    if isinstance(value, dict):
        return f"dict[{len(value)}]"
    return type(value).__name__


def _localization_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    return ""


def _localization_api_registry_seam(feature: str) -> str:
    if feature == "localization-api":
        return "localization facade API table"
    return "HOI4 language alias normalization"
