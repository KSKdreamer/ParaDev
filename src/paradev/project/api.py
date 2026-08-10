"""Generated facade API table for public project package exports."""

from __future__ import annotations

import inspect
from dataclasses import is_dataclass
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

PROJECT_FACADE_API_TABLE_SCHEMA = "paradev.project.facade-api-table.v1"
_PROJECT_FACADE_API_REFERENCE_PAGE = "docs/user-manual/project-facade-api-reference.md"
_PROJECT_FACADE_API_TEST_ANCHOR = "tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade"
_PROJECT_FACADE_API_SYMBOLS = {
    "PROJECT_FACADE_API_TABLE_SCHEMA",
    "ProjectFacadeApiRow",
    "ProjectFacadeApiTable",
    "get_project_facade_api_selection",
    "get_project_facade_api_table",
    "render_project_facade_api_reference_markdown",
}
_PROJECT_FACADE_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")


class ProjectFacadeApiRow(TypedDict):
    """One public `paradev.project` facade API row."""

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


class ProjectFacadeApiTable(TypedDict):
    """Generated API-standard table for the project package facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[ProjectFacadeApiRow]


def get_project_facade_api_table() -> ProjectFacadeApiTable:
    """Return the API-standard table for the public project package facade.

    Returns:
        JSON-safe table derived from `paradev.project.__all__`, with copied
        rows and indexes for project package module, feature, and symbol-kind
        audits.
    """

    return cast(ProjectFacadeApiTable, api_standard_table(PROJECT_FACADE_API_TABLE_SCHEMA, _project_facade_api_rows()))


def get_project_facade_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> ProjectFacadeApiTable | ProjectFacadeApiRow | list[str]:
    """Return the full project facade API table, one row, or one index bucket.

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
        ProjectFacadeApiTable | ProjectFacadeApiRow | list[str],
        api_table_selection(
            get_project_facade_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_PROJECT_FACADE_API_INDEX_NAMES,
        ),
    )


def render_project_facade_api_reference_markdown() -> str:
    """Render the public project package facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/project-facade-api-reference.md`. The content is
        generated from `get_project_facade_api_table()` so the compatibility
        project import facade stays aligned with the canonical SDK `Project`
        object reference.
    """

    table = get_project_facade_api_table()
    return api_standard_reference_markdown(
        title="Project Facade API Reference",
        source="paradev.project.get_project_facade_api_table()",
        regenerate_when="Regenerate this file whenever the public `paradev.project` facade changes:",
        command="rtk uv run paradev project-facade-api --markdown > docs/user-manual/project-facade-api-reference.md",
        table=table,
        module_label="Project",
    )


def _project_facade_api_rows() -> list[ProjectFacadeApiRow]:
    import paradev.project as project

    rows: list[ProjectFacadeApiRow] = []
    for symbol in project.__all__:
        value = getattr(project, symbol)
        module = _project_facade_api_module(symbol, value)
        feature = _project_facade_api_feature(symbol, module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _project_facade_api_kind(symbol, value),
                "layer": "project",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.project.{symbol}",
                "returns": _project_facade_api_returns(symbol, value),
                "value": _project_facade_api_value(symbol, value),
                "registry_seam": _project_facade_api_registry_seam(symbol, feature),
                "surface": "sdk",
                "doc_page": _project_facade_api_doc_page(feature),
                "test_anchor": _PROJECT_FACADE_API_TEST_ANCHOR,
            }
        )
    return rows


def _project_facade_api_module(symbol: str, value: object) -> str:
    if symbol in _PROJECT_FACADE_API_SYMBOLS:
        return "api"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev."):
        return module.removeprefix("paradev.")
    return "project"


def _project_facade_api_feature(symbol: str, module: str) -> str:
    if module == "api":
        return "project-facade-api"
    if symbol.endswith("Error"):
        return "errors"
    return "projects"


def _project_facade_api_kind(symbol: str, value: object) -> str:
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
    return type(value).__name__


def _project_facade_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if is_typeddict(value):
        return "TypedDict schema"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation, prefer_builtins_qualname=True, use_name=False)
    if inspect.isclass(value):
        return f"{value.__name__} class"
    return type(value).__name__


def _project_facade_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    return ""


def _project_facade_api_registry_seam(symbol: str, feature: str) -> str:
    if feature == "project-facade-api":
        return "project facade API table"
    if symbol == "Project":
        return "project family/template registry"
    if feature == "errors":
        return "project manifest validation"
    return "none"


def _project_facade_api_doc_page(feature: str) -> str:
    if feature == "project-facade-api":
        return _PROJECT_FACADE_API_REFERENCE_PAGE
    return "docs/user-manual/project-api-reference.md"
