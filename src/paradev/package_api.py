"""Generated facade API table for root `paradev` exports."""

from __future__ import annotations

import inspect
from dataclasses import is_dataclass
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

PACKAGE_API_TABLE_SCHEMA = "paradev.package.api-table.v1"
_PACKAGE_API_REFERENCE_PAGE = "docs/user-manual/package-api-reference.md"
_PACKAGE_API_TEST_ANCHOR = "tests/test_architecture.py::test_package_api_table_lists_root_facade"
_PACKAGE_API_SYMBOLS = {
    "PackageApiRow",
    "PackageApiTable",
    "get_package_api_selection",
    "get_package_api_table",
    "render_package_api_reference_markdown",
}
_PACKAGE_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")


class PackageApiRow(TypedDict):
    """One public root `paradev` facade API row."""

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


class PackageApiTable(TypedDict):
    """Generated API-standard table for the root package facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[PackageApiRow]


def get_package_api_table() -> PackageApiTable:
    """Return the API-standard table for the root `paradev` facade.

    Returns:
        JSON-safe table derived from `paradev.__all__`, with copied rows and
        indexes for module, feature, and symbol-kind audits.
    """

    return cast(PackageApiTable, api_standard_table(PACKAGE_API_TABLE_SCHEMA, _package_api_rows()))


def get_package_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> PackageApiTable | PackageApiRow | list[str]:
    """Return the full package API table, one row, or one index bucket.

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
        PackageApiTable | PackageApiRow | list[str],
        api_table_selection(
            get_package_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_PACKAGE_API_INDEX_NAMES,
        ),
    )


def render_package_api_reference_markdown() -> str:
    """Render the root package facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/package-api-reference.md`. The content is generated
        from `get_package_api_table()` so the import facade, docs, CLI
        command, and tests stay aligned.
    """

    table = get_package_api_table()
    return api_standard_reference_markdown(
        title="Package API Reference",
        source="paradev.get_package_api_table()",
        regenerate_when="Regenerate this file whenever the root `paradev` facade changes:",
        command="rtk uv run paradev package-api --markdown > docs/user-manual/package-api-reference.md",
        table=table,
        module_label="Package",
    )


def _package_api_rows() -> list[PackageApiRow]:
    import paradev

    rows: list[PackageApiRow] = []
    for symbol in paradev.__all__:
        value = getattr(paradev, symbol)
        module = _package_api_module(symbol, value)
        feature = _package_api_feature(symbol, module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _package_api_kind(symbol, value),
                "layer": "package",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.{symbol}",
                "returns": _package_api_returns(symbol, value),
                "value": _package_api_value(symbol, value),
                "registry_seam": _package_api_registry_seam(symbol, module),
                "surface": "sdk",
                "doc_page": _package_api_doc_page(symbol, feature),
                "test_anchor": _PACKAGE_API_TEST_ANCHOR,
            }
        )
    return rows


def _package_api_module(symbol: str, value: object) -> str:
    if symbol.startswith("PACKAGE_API") or symbol in _PACKAGE_API_SYMBOLS:
        return "package_api"
    if symbol == "CM_PARADEV":
        return "config"
    if symbol == "__version__":
        return "version"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev."):
        return module.removeprefix("paradev.")
    return "package"


def _package_api_feature(symbol: str, module: str) -> str:
    if module == "package_api":
        return "package-api"
    if module == "config":
        return "config"
    if module == "version":
        return "version"
    if module == "sdk.architecture":
        return "architecture"
    if module == "sdk.project":
        if symbol.endswith("Error"):
            return "errors"
        return "projects"
    return "package"


def _package_api_kind(symbol: str, value: object) -> str:
    if symbol == "CM_PARADEV":
        return "ConfigManager"
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if is_typeddict(value):
        return "TypedDict"
    if inspect.isclass(value):
        if issubclass(value, ValueError):
            return "exception"
        if is_dataclass(value):
            return "dataclass"
        return "class"
    if inspect.isfunction(value):
        return "function"
    if symbol == "__version__":
        return "version constant"
    return type(value).__name__


def _package_api_returns(symbol: str, value: object) -> str:
    if symbol == "CM_PARADEV":
        return "ConfigManager"
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if is_typeddict(value):
        return "TypedDict schema"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation)
    if inspect.isclass(value):
        return f"{value.__name__} class"
    if symbol == "__version__":
        return "str"
    return type(value).__name__


def _package_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA") or symbol == "__version__":
        return str(value)
    return ""


def _package_api_registry_seam(symbol: str, module: str) -> str:
    if module == "config":
        return "HeavenBase ConfigManager"
    if module == "sdk.project" and symbol in {"Project", "ParaDevProject"}:
        return "project family/template registry"
    if module == "sdk.architecture":
        return "surface architecture registry"
    return "none"


def _package_api_doc_page(symbol: str, feature: str) -> str:
    if feature == "package-api":
        return _PACKAGE_API_REFERENCE_PAGE
    if feature == "architecture":
        return "docs/user-manual/architecture-api-reference.md"
    if feature in {"projects", "errors"}:
        return "docs/user-manual/project-api-reference.md"
    if feature == "config":
        return "docs/user-manual/troubleshooting.md"
    if symbol == "__version__":
        return "docs/user-manual/getting-started.md"
    return "docs/user-manual/sdk-python.md"
