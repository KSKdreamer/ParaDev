"""Generated facade API table for public SDK exports."""

from __future__ import annotations

import inspect
from dataclasses import is_dataclass
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

SDK_API_TABLE_SCHEMA = "paradev.sdk.api-table.v1"
_SDK_API_REFERENCE_PAGE = "docs/user-manual/sdk-api-reference.md"
_SDK_API_TEST_ANCHOR = "tests/test_architecture.py::test_sdk_api_table_lists_facade_exports"
_SDK_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")


class SdkApiRow(TypedDict):
    """One public `paradev.sdk` facade API row."""

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


class SdkApiTable(TypedDict):
    """Generated API-standard table for the Python SDK facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[SdkApiRow]


def get_sdk_api_table() -> SdkApiTable:
    """Return the API-standard table for the public Python SDK facade.

    Returns:
        JSON-safe table derived from `paradev.sdk.__all__`, with copied rows
        and indexes for module, feature, and symbol-kind audits.
    """

    return cast(SdkApiTable, api_standard_table(SDK_API_TABLE_SCHEMA, _sdk_api_rows()))


def get_sdk_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> SdkApiTable | SdkApiRow | list[str]:
    """Return the full SDK API table, one row, or one index bucket.

    Args:
        symbol: Optional public SDK symbol to select from the table rows.
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
        SdkApiTable | SdkApiRow | list[str],
        api_table_selection(
            get_sdk_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_SDK_API_INDEX_NAMES,
        ),
    )


def render_sdk_api_reference_markdown() -> str:
    """Render the public SDK facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/sdk-api-reference.md`. The content is generated
        from `get_sdk_api_table()` so the import facade, docs, CLI command,
        and tests stay aligned.
    """

    table = get_sdk_api_table()
    return api_standard_reference_markdown(
        title="SDK API Reference",
        source="paradev.sdk.get_sdk_api_table()",
        regenerate_when="Regenerate this file whenever the public Python SDK facade changes:",
        command="rtk uv run paradev sdk-api --markdown > docs/user-manual/sdk-api-reference.md",
        table=table,
        module_label="SDK",
    )


def _sdk_api_rows() -> list[SdkApiRow]:
    import paradev.sdk as sdk

    rows: list[SdkApiRow] = []
    for symbol in sdk.__all__:
        value = getattr(sdk, symbol)
        module = _sdk_api_module(symbol, value)
        feature = _sdk_api_feature(symbol, module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _sdk_api_kind(symbol, value),
                "layer": "sdk",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.sdk.{symbol}",
                "returns": _sdk_api_returns(symbol, value),
                "value": _sdk_api_value(symbol, value),
                "registry_seam": _sdk_api_registry_seam(symbol, module),
                "surface": "sdk",
                "doc_page": _sdk_api_doc_page(module, feature),
                "test_anchor": _SDK_API_TEST_ANCHOR,
            }
        )
    return rows


def _sdk_api_module(symbol: str, value: object) -> str:
    if symbol.startswith("SDK_API") or symbol in {"SdkApiRow", "SdkApiTable", "get_sdk_api_table", "render_sdk_api_reference_markdown"}:
        return "api"
    if symbol.startswith("PROJECT_API") or symbol in {"ProjectApiRow", "ProjectApiTable", "get_project_api_table", "render_project_api_reference_markdown"}:
        return "project_api"
    if symbol.startswith("ARCHITECTURE") or symbol in {
        "ArchitectureApiRow",
        "ArchitectureApiTable",
        "ArchitectureSpec",
        "SurfaceSpec",
        "get_architecture_api_table",
        "get_architecture_spec",
        "render_architecture_api_reference_markdown",
    }:
        return "architecture"
    if symbol.startswith("FRONTEND_API") or symbol.startswith(
        ("build_frontend_", "get_frontend_", "normalize_frontend_", "plan_frontend_", "render_frontend_", "resolve_frontend_")
    ):
        return "frontend_api"
    if (
        symbol.startswith("LSP")
        or symbol.startswith("Lsp")
        or symbol.endswith("_pdx_lsp_text")
        or symbol
        in {
            "complete_pdx_lsp_text",
            "document_symbols_pdx_lsp_text",
            "hover_pdx_lsp_text",
            "semantic_tokens_pdx_lsp_text",
        }
    ):
        return "lsp"
    if (
        symbol.startswith("PDX")
        or symbol.startswith("Pdx")
        or symbol
        in {
            "format_pdx_file",
            "format_pdx_text",
            "get_pdx_api_table",
            "parse_pdx_file",
            "render_pdx_api_reference_markdown",
        }
    ):
        return "pdx"
    if symbol.startswith("HOI4_KEYWORD") or symbol == "hoi4_keyword_dataset":
        return "games.hoi4.keywords"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev.sdk."):
        return module.removeprefix("paradev.sdk.")
    if module.startswith("paradev."):
        return module.removeprefix("paradev.")
    return "project"


def _sdk_api_feature(symbol: str, module: str) -> str:
    upper_symbol = symbol.upper()
    if module == "api":
        return "api-table"
    if module == "desktop.local" and symbol in {"desktop_chat", "desktop_chat_profiles", "desktop_reset_chat_profile", "desktop_write_chat_profile"}:
        return "ai-chat"
    if module == "architecture":
        return "architecture"
    if module == "frontend_api":
        return "frontend-api"
    if module == "project_api":
        return "project-api"
    if module == "pdx":
        if "PARSE" in symbol or symbol == "parse_pdx_file":
            return "parse"
        if "FORMAT" in symbol or symbol.startswith("format_pdx"):
            return "format"
        return "pdx-api"
    if module == "lsp":
        return _sdk_api_lsp_feature(symbol)
    if module == "games.hoi4.keywords":
        return "hoi4-keywords"
    if "INSPECTION" in upper_symbol or symbol.startswith("get_project_inspection") or symbol.startswith("render_project_inspection"):
        return "inspections"
    if symbol.startswith("MODULE") or "module" in symbol.lower():
        return "modules"
    if symbol.startswith("COLLECTION") or "collection" in symbol.lower():
        return "collections"
    if symbol.startswith("DESKTOP") or symbol == "desktop_state":
        return "desktop"
    return "projects"


def _sdk_api_lsp_feature(symbol: str) -> str:
    text = symbol.lower()
    if "diagnostics" in text or "diagnose" in text:
        return "diagnostics"
    if "symbol" in text:
        return "symbols"
    if "hover" in text:
        return "hover"
    if "format" in text:
        return "formatting"
    if "completion" in text or "complete" in text:
        return "completion"
    if "semantic" in text:
        return "semantic-tokens"
    return "lsp-api"


def _sdk_api_kind(symbol: str, value: object) -> str:
    if inspect.isfunction(value):
        return "function"
    if is_typeddict(value):
        return "TypedDict"
    if inspect.isclass(value):
        if issubclass(value, ValueError):
            return "exception"
        if is_dataclass(value):
            return "dataclass"
        return "class"
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if isinstance(value, tuple):
        return "tuple constant"
    return "constant"


def _sdk_api_returns(symbol: str, value: object) -> str:
    if inspect.isfunction(value):
        return _sdk_api_return_annotation(value)
    if is_typeddict(value):
        return "TypedDict schema"
    if inspect.isclass(value):
        return f"{value.__name__} class"
    if symbol.endswith("_SCHEMA") and isinstance(value, str):
        return value
    if isinstance(value, tuple):
        return f"tuple[{len(value)}]"
    return type(value).__name__


def _sdk_api_return_annotation(value: object) -> str:
    try:
        annotation = inspect.signature(value).return_annotation
    except (TypeError, ValueError):
        return ""
    if annotation is inspect.Signature.empty:
        return ""
    return api_annotation_text(annotation)


def _sdk_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA") and isinstance(value, str):
        return value
    if isinstance(value, tuple):
        return f"tuple[{len(value)}]"
    return ""


def _sdk_api_registry_seam(symbol: str, module: str) -> str:
    if module == "desktop.local" and symbol in {"desktop_chat", "desktop_chat_profiles", "desktop_reset_chat_profile", "desktop_write_chat_profile"}:
        return "HeavenBase desktop AI chat"
    if module == "frontend_api":
        return "frontend API operation registry"
    if module == "project" and ("MODULE" in symbol or "COLLECTION" in symbol or symbol == "Project"):
        return "project family/template registry"
    if module == "games.hoi4.keywords":
        return "HOI4 keyword sources"
    return "none"


def _sdk_api_doc_page(module: str, feature: str) -> str:
    if module == "api":
        return _SDK_API_REFERENCE_PAGE
    if module == "desktop.local":
        return "docs/user-manual/desktop-api-reference.md"
    if module == "project_api":
        return "docs/user-manual/project-api-reference.md"
    if module == "architecture":
        return "docs/user-manual/architecture-api-reference.md"
    if module == "frontend_api":
        return "docs/user-manual/frontend-api-reference.md"
    if module == "pdx":
        return "docs/user-manual/pdx-api-reference.md"
    if module == "lsp" or module == "games.hoi4.keywords":
        return "docs/user-manual/lsp-api-reference.md"
    if feature == "inspections":
        return "docs/user-manual/project-inspection-reference.md"
    return "docs/user-manual/sdk-python.md"
