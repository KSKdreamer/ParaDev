"""Generated facade API table for public desktop package exports."""

from __future__ import annotations

import inspect
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

DESKTOP_API_TABLE_SCHEMA = "paradev.desktop.api-table.v1"
_DESKTOP_API_REFERENCE_PAGE = "docs/user-manual/desktop-api-reference.md"
_DESKTOP_API_TEST_ANCHOR = "tests/test_architecture.py::test_desktop_api_table_lists_public_desktop_facade"
_DESKTOP_API_SYMBOLS = {
    "DESKTOP_API_TABLE_SCHEMA",
    "DesktopApiRow",
    "DesktopApiTable",
    "get_desktop_api_selection",
    "get_desktop_api_table",
    "render_desktop_api_reference_markdown",
}
_DESKTOP_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")


class DesktopApiRow(TypedDict):
    """One public `paradev.desktop` facade API row."""

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


class DesktopApiTable(TypedDict):
    """Generated API-standard table for the desktop package facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[DesktopApiRow]


def get_desktop_api_table() -> DesktopApiTable:
    """Return the API-standard table for the public desktop facade.

    Returns:
        JSON-safe table derived from `paradev.desktop.__all__`, with copied
        rows and indexes for desktop state module, feature, and symbol-kind
        audits.
    """

    return cast(DesktopApiTable, api_standard_table(DESKTOP_API_TABLE_SCHEMA, _desktop_api_rows()))


def get_desktop_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> DesktopApiTable | DesktopApiRow | list[str]:
    """Return the full desktop API table, one row, or one index bucket.

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
        DesktopApiTable | DesktopApiRow | list[str],
        api_table_selection(
            get_desktop_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_DESKTOP_API_INDEX_NAMES,
        ),
    )


def render_desktop_api_reference_markdown() -> str:
    """Render the public desktop facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/desktop-api-reference.md`. The content is generated
        from `get_desktop_api_table()` so the desktop state facade, CLI
        command, and manual page stay aligned.
    """

    table = get_desktop_api_table()
    return api_standard_reference_markdown(
        title="Desktop API Reference",
        source="paradev.desktop.get_desktop_api_table()",
        regenerate_when="Regenerate this file whenever the public `paradev.desktop` facade changes:",
        command="rtk uv run paradev desktop-api --markdown > docs/user-manual/desktop-api-reference.md",
        table=table,
        module_label="Desktop",
        markdown_value=True,
    )


def _desktop_api_rows() -> list[DesktopApiRow]:
    import paradev.desktop as desktop

    rows: list[DesktopApiRow] = []
    for symbol in desktop.__all__:
        value = getattr(desktop, symbol)
        module = _desktop_api_module(symbol, value)
        feature = _desktop_api_feature(symbol, module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _desktop_api_kind(symbol, value),
                "layer": "desktop",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.desktop.{symbol}",
                "returns": _desktop_api_returns(symbol, value),
                "value": _desktop_api_value(symbol, value),
                "registry_seam": _desktop_api_registry_seam(feature),
                "surface": _desktop_api_surface(feature),
                "doc_page": _DESKTOP_API_REFERENCE_PAGE,
                "test_anchor": _DESKTOP_API_TEST_ANCHOR,
            }
        )
    return rows


def _desktop_api_module(symbol: str, value: object) -> str:
    if symbol in _DESKTOP_API_SYMBOLS:
        return "desktop.api"
    if symbol in {"DESKTOP_STATE_SCHEMA", "desktop_state"}:
        return "sdk.project"
    if symbol in {"BUILD_RUN_SCHEMA", "BUILD_RUNS_SCHEMA", "DesktopBuildRegistry"}:
        return "desktop.builds"
    if symbol in {
        "AI_CHAT_SCHEMA",
        "AI_CHAT_PROFILES_SCHEMA",
        "AI_CHAT_PROFILES_CONFIG_KEY",
        "AI_CHAT_PROFILES_CONFIG_SCHEMA",
        "BINARY_SOURCE_SCHEMA",
        "DESKTOP_CONFIG_KEYS",
        "DESKTOP_APP_CONFIG_KEY",
    }:
        return "desktop.local"
    if symbol in {
        "PROJECT_PACKAGE_CATALOG_SCHEMA",
        "PROJECT_PACKAGE_INSTALL_SCHEMA",
        "desktop_project_package_catalog",
        "desktop_install_project_package",
    }:
        return "desktop.project_packages"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev."):
        return module.removeprefix("paradev.")
    return "desktop"


def _desktop_api_feature(symbol: str, module: str) -> str:
    if module == "desktop.api":
        return "desktop-api"
    if symbol in {"DESKTOP_STATE_SCHEMA", "desktop_state"}:
        return "state"
    if symbol in {
        "AI_CHAT_SCHEMA",
        "AI_CHAT_PROFILES_SCHEMA",
        "AI_CHAT_PROFILES_CONFIG_KEY",
        "AI_CHAT_PROFILES_CONFIG_SCHEMA",
        "desktop_chat",
        "desktop_chat_profiles",
        "desktop_reset_chat_profile",
        "desktop_write_chat_profile",
        "desktop_test_llm_route",
    }:
        return "ai-chat"
    if symbol in {
        "desktop_source_path",
        "desktop_read_text_source",
        "desktop_read_binary_source",
        "desktop_binary_source",
        "desktop_mime_type",
        "BINARY_SOURCE_SCHEMA",
    }:
        return "sources"
    if symbol in {
        "desktop_browser_cache_path",
        "read_project_browser_cache",
        "desktop_write_browser_cache",
        "desktop_thumbnail_cache_path",
        "desktop_read_thumbnail_cache",
        "desktop_write_thumbnail_cache",
    }:
        return "cache"
    if symbol in {
        "DESKTOP_CONFIG_KEYS",
        "DESKTOP_APP_CONFIG_KEY",
        "desktop_config_rows",
        "render_desktop_typescript",
        "desktop_read_app_config",
        "desktop_write_app_config",
        "desktop_read_config_value",
        "desktop_write_config_value",
    }:
        return "config"
    if symbol in {"desktop_dependency_status", "desktop_install_dependency"}:
        return "dependencies"
    if symbol in {
        "PROJECT_PACKAGE_CATALOG_SCHEMA",
        "PROJECT_PACKAGE_INSTALL_SCHEMA",
        "desktop_project_package_catalog",
        "desktop_install_project_package",
    }:
        return "project-packages"
    if symbol in {
        "BUILD_RUN_SCHEMA",
        "BUILD_RUNS_SCHEMA",
        "DesktopBuildRegistry",
        "desktop_project_build_command",
        "desktop_start_build",
        "desktop_build_runs",
        "desktop_build_status",
        "desktop_interrupt_build",
    }:
        return "build"
    if symbol in {"desktop_hoi4_launch_command", "desktop_run_hoi4"}:
        return "game-launch"
    if symbol in {"desktop_open_path_command", "desktop_open_path", "desktop_open_path_targets", "desktop_path_status"}:
        return "open-path"
    return "desktop"


def _desktop_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if is_typeddict(value):
        return "TypedDict"
    if inspect.isclass(value):
        return "class"
    if inspect.isfunction(value):
        return "function"
    return type(value).__name__


def _desktop_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if is_typeddict(value):
        return "TypedDict schema"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation, strip_string_quotes=True)
    return type(value).__name__


def _desktop_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    return ""


def _desktop_api_registry_seam(feature: str) -> str:
    if feature == "desktop-api":
        return "desktop facade API table"
    if feature == "sources":
        return "project-contained desktop source files"
    if feature == "cache":
        return "project .paradev desktop cache"
    if feature == "config":
        return "CM_PARADEV desktop GUI config"
    if feature == "ai-chat":
        return "HeavenBase desktop AI chat"
    if feature == "dependencies":
        return "desktop dependency manager"
    if feature == "project-packages":
        return "publisher-verified project package catalog and installer"
    if feature == "build":
        return "desktop build lifecycle and CLI command planner"
    if feature == "game-launch":
        return "desktop HOI4 launcher command"
    if feature == "open-path":
        return "desktop local path opener"
    return "desktop state contract"


def _desktop_api_surface(feature: str) -> str:
    if feature == "desktop-api":
        return "sdk"
    if feature in {"cache", "config", "sources"}:
        return "desktop"
    return "desktop"
