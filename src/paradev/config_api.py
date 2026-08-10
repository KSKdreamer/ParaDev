"""Generated facade API table for public config module exports."""

from __future__ import annotations

import inspect
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

CONFIG_API_TABLE_SCHEMA = "paradev.config.api-table.v1"
_CONFIG_API_REFERENCE_PAGE = "docs/user-manual/config-api-reference.md"
_CONFIG_API_TEST_ANCHOR = "tests/test_architecture.py::test_config_api_table_lists_public_config_facade"
_CONFIG_API_SYMBOLS = {
    "CONFIG_API_TABLE_SCHEMA",
    "ConfigApiRow",
    "ConfigApiTable",
    "get_config_api_selection",
    "get_config_api_table",
    "render_config_api_reference_markdown",
}
_CONFIG_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")


class ConfigApiRow(TypedDict):
    """One public `paradev.config` facade API row."""

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


class ConfigApiTable(TypedDict):
    """Generated API-standard table for the config module facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[ConfigApiRow]


def get_config_api_table() -> ConfigApiTable:
    """Return the API-standard table for the public config facade.

    Returns:
        JSON-safe table derived from `paradev.config.__all__`, with copied
        rows and indexes for config module, feature, and symbol-kind audits.
    """

    return cast(ConfigApiTable, api_standard_table(CONFIG_API_TABLE_SCHEMA, _config_api_rows()))


def get_config_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> ConfigApiTable | ConfigApiRow | list[str]:
    """Return the full config API table, one row, or one index bucket.

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
        ConfigApiTable | ConfigApiRow | list[str],
        api_table_selection(
            get_config_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_CONFIG_API_INDEX_NAMES,
        ),
    )


def render_config_api_reference_markdown() -> str:
    """Render the public config facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/config-api-reference.md`. The content is generated
        from `get_config_api_table()` so the config defaults, ConfigManager
        instance, CLI command, and manual page stay aligned.
    """

    table = get_config_api_table()
    return api_standard_reference_markdown(
        title="Config API Reference",
        source="paradev.config.get_config_api_table()",
        regenerate_when="Regenerate this file whenever the public `paradev.config` facade changes:",
        command="rtk uv run paradev config-api --markdown > docs/user-manual/config-api-reference.md",
        table=table,
        module_label="Config",
    )


def _config_api_rows() -> list[ConfigApiRow]:
    import paradev.config as config

    rows: list[ConfigApiRow] = []
    for symbol in config.__all__:
        value = getattr(config, symbol)
        module = _config_api_module(symbol, value)
        feature = _config_api_feature(symbol, module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _config_api_kind(symbol, value),
                "layer": "config",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.config.{symbol}",
                "returns": _config_api_returns(symbol, value),
                "value": _config_api_value(symbol, value),
                "registry_seam": _config_api_registry_seam(symbol, feature),
                "surface": "sdk",
                "doc_page": _CONFIG_API_REFERENCE_PAGE,
                "test_anchor": _CONFIG_API_TEST_ANCHOR,
            }
        )
    return rows


def _config_api_module(symbol: str, value: object) -> str:
    if symbol in _CONFIG_API_SYMBOLS:
        return "config_api"
    if symbol in {"DEFAULT_CONFIG", "BOOTSTRAP_CONFIG", "CM_PARADEV"}:
        return "config"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev."):
        return module.removeprefix("paradev.")
    return "config"


def _config_api_feature(symbol: str, module: str) -> str:
    if module == "config_api":
        return "config-api"
    if symbol == "CM_PARADEV":
        return "config-manager"
    if symbol in {"DEFAULT_CONFIG", "BOOTSTRAP_CONFIG"}:
        return "defaults"
    return "config"


def _config_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if symbol == "CM_PARADEV":
        return "ConfigManager"
    if is_typeddict(value):
        return "TypedDict"
    if inspect.isfunction(value):
        return "function"
    if isinstance(value, dict):
        return "dict constant"
    return type(value).__name__


def _config_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if symbol == "CM_PARADEV":
        return "ConfigManager"
    if is_typeddict(value):
        return "TypedDict schema"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation)
    if isinstance(value, dict):
        return f"dict[{len(value)}]"
    return type(value).__name__


def _config_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    return ""


def _config_api_registry_seam(symbol: str, feature: str) -> str:
    if feature == "config-api":
        return "config facade API table"
    if symbol == "CM_PARADEV":
        return "HeavenBase ConfigManager"
    if feature == "config":
        return "HeavenBase ConfigManager"
    return "HeavenBase ConfigManager defaults"
