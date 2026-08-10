"""Generated facade API table for public REST package exports."""

from __future__ import annotations

import inspect
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

REST_FACADE_API_TABLE_SCHEMA = "paradev.rest.facade-api-table.v1"
_REST_FACADE_API_REFERENCE_PAGE = "docs/user-manual/rest-facade-api-reference.md"
_REST_FACADE_API_TEST_ANCHOR = "tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade"
_REST_FACADE_API_SYMBOLS = {
    "REST_FACADE_API_TABLE_SCHEMA",
    "RestFacadeApiRow",
    "RestFacadeApiTable",
    "get_rest_facade_api_selection",
    "get_rest_facade_api_table",
    "render_rest_facade_api_reference_markdown",
}
_REST_PROJECT_COMPATIBILITY_SYMBOLS = {
    "apply_project_draft",
    "create_module_batch",
    "create_module_draft",
    "read_project_source",
    "read_project_source_form",
}
_REST_FACADE_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")


class RestFacadeApiRow(TypedDict):
    """One public `paradev.api` facade API row."""

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


class RestFacadeApiTable(TypedDict):
    """Generated API-standard table for the REST package facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[RestFacadeApiRow]


def get_rest_facade_api_table() -> RestFacadeApiTable:
    """Return the API-standard table for the public REST package facade.

    Returns:
        JSON-safe table derived from `paradev.api.__all__`, with copied rows
        and indexes for REST package module, feature, and symbol-kind audits.
    """

    return cast(RestFacadeApiTable, api_standard_table(REST_FACADE_API_TABLE_SCHEMA, _rest_facade_api_rows()))


def get_rest_facade_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> RestFacadeApiTable | RestFacadeApiRow | list[str]:
    """Return the full REST facade API table, one row, or one index bucket.

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
        RestFacadeApiTable | RestFacadeApiRow | list[str],
        api_table_selection(
            get_rest_facade_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_REST_FACADE_API_INDEX_NAMES,
        ),
    )


def render_rest_facade_api_reference_markdown() -> str:
    """Render the public REST package facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/rest-facade-api-reference.md`. The content is
        generated from `get_rest_facade_api_table()` so local API server,
        OpenAPI seed, project source, and draft helper exports stay aligned.
    """

    table = get_rest_facade_api_table()
    return api_standard_reference_markdown(
        title="REST Facade API Reference",
        source="paradev.api.get_rest_facade_api_table()",
        regenerate_when="Regenerate this file whenever the public `paradev.api` facade changes:",
        command="rtk uv run paradev rest-facade-api --markdown > docs/user-manual/rest-facade-api-reference.md",
        table=table,
        module_label="REST",
    )


def _rest_facade_api_rows() -> list[RestFacadeApiRow]:
    import paradev.api as api

    rows: list[RestFacadeApiRow] = []
    for symbol in api.__all__:
        value = getattr(api, symbol)
        module = _rest_facade_api_module(symbol, value)
        feature = _rest_facade_api_feature(symbol, module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _rest_facade_api_kind(symbol, value),
                "layer": "rest",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.api.{symbol}",
                "returns": _rest_facade_api_returns(symbol, value),
                "value": _rest_facade_api_value(symbol, value),
                "registry_seam": _rest_facade_api_registry_seam(symbol, feature),
                "surface": "rest",
                "doc_page": _REST_FACADE_API_REFERENCE_PAGE,
                "test_anchor": _REST_FACADE_API_TEST_ANCHOR,
            }
        )
    return rows


def _rest_facade_api_module(symbol: str, value: object) -> str:
    if symbol in _REST_FACADE_API_SYMBOLS:
        return "api"
    if symbol in _REST_PROJECT_COMPATIBILITY_SYMBOLS:
        return "rest"
    module = getattr(value, "__module__", "")
    if module == "paradev.surfaces.rest":
        return "rest"
    if module.startswith("paradev."):
        return module.removeprefix("paradev.")
    return "rest"


def _rest_facade_api_feature(symbol: str, module: str) -> str:
    if module == "api":
        return "rest-facade-api"
    if symbol == "get_openapi_seed":
        return "openapi"
    if symbol == "build_app":
        return "server"
    if symbol in {"read_project_source", "read_project_source_form"}:
        return "project-sources"
    if symbol == "apply_project_draft":
        return "project-drafts"
    if symbol == "create_module_batch":
        return "module-batches"
    if symbol == "create_module_draft":
        return "module-drafts"
    return "rest"


def _rest_facade_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if is_typeddict(value):
        return "TypedDict"
    if inspect.isfunction(value):
        return "function"
    return type(value).__name__


def _rest_facade_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if is_typeddict(value):
        return "TypedDict schema"
    if symbol == "build_app":
        return "FastAPI app"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation, prefer_builtins_qualname=True, use_name=False)
    return type(value).__name__


def _rest_facade_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    return ""


def _rest_facade_api_registry_seam(symbol: str, feature: str) -> str:
    if feature == "rest-facade-api":
        return "REST facade API table"
    if symbol == "get_openapi_seed":
        return "OpenAPI seed contract"
    if symbol == "build_app":
        return "FastAPI app factory"
    if symbol in {"read_project_source", "read_project_source_form"}:
        return "REST project source bridge"
    if symbol == "apply_project_draft":
        return "REST project draft bridge"
    if symbol == "create_module_batch":
        return "REST module batch bridge"
    if symbol == "create_module_draft":
        return "REST module draft bridge"
    return "REST package facade"
