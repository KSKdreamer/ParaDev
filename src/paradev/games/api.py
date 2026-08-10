"""Generated facade API table for public game package exports."""

from __future__ import annotations

import inspect
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

GAMES_API_TABLE_SCHEMA = "paradev.games.api-table.v1"
_GAMES_API_REFERENCE_PAGE = "docs/user-manual/games-api-reference.md"
_GAMES_API_TEST_ANCHOR = "tests/test_architecture.py::test_games_api_table_lists_public_games_facade"
_GAMES_API_SYMBOLS = {
    "GAMES_API_TABLE_SCHEMA",
    "GamesApiRow",
    "GamesApiTable",
    "get_games_api_selection",
    "get_games_api_table",
    "render_games_api_reference_markdown",
}
_GAMES_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")


class GamesApiRow(TypedDict):
    """One public `paradev.games` facade API row."""

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


class GamesApiTable(TypedDict):
    """Generated API-standard table for the game package facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[GamesApiRow]


def get_games_api_table() -> GamesApiTable:
    """Return the API-standard table for the public games facade.

    Returns:
        JSON-safe table derived from `paradev.games.__all__`, with copied rows
        and indexes for game profile module, feature, and symbol-kind audits.
    """

    return cast(GamesApiTable, api_standard_table(GAMES_API_TABLE_SCHEMA, _games_api_rows()))


def get_games_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> GamesApiTable | GamesApiRow | list[str]:
    """Return the full games API table, one row, or one index bucket.

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
        GamesApiTable | GamesApiRow | list[str],
        api_table_selection(
            get_games_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_GAMES_API_INDEX_NAMES,
        ),
    )


def render_games_api_reference_markdown() -> str:
    """Render the public games facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/games-api-reference.md`. The content is generated
        from `get_games_api_table()` so profile registry helpers, CLI command,
        and manual page stay aligned.
    """

    table = get_games_api_table()
    return api_standard_reference_markdown(
        title="Games API Reference",
        source="paradev.games.get_games_api_table()",
        regenerate_when="Regenerate this file whenever the public `paradev.games` facade changes:",
        command="rtk uv run paradev games-api --markdown > docs/user-manual/games-api-reference.md",
        table=table,
        module_label="Games",
        markdown_value=True,
    )


def _games_api_rows() -> list[GamesApiRow]:
    import paradev.games as games

    rows: list[GamesApiRow] = []
    for symbol in games.__all__:
        value = getattr(games, symbol)
        module = _games_api_module(symbol, value)
        feature = _games_api_feature(symbol, module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _games_api_kind(symbol, value),
                "layer": "games",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.games.{symbol}",
                "returns": _games_api_returns(symbol, value),
                "value": _games_api_value(symbol, value),
                "registry_seam": _games_api_registry_seam(feature),
                "surface": "sdk",
                "doc_page": _GAMES_API_REFERENCE_PAGE,
                "test_anchor": _GAMES_API_TEST_ANCHOR,
            }
        )
    return rows


def _games_api_module(symbol: str, value: object) -> str:
    if symbol in _GAMES_API_SYMBOLS:
        return "games.api"
    if symbol in {"PROFILE_REGISTRIES", "registry_for_profile"}:
        return "games"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev."):
        return module.removeprefix("paradev.")
    return "games"


def _games_api_feature(symbol: str, module: str) -> str:
    if module == "games.api":
        return "games-api"
    if symbol in {"PROFILE_REGISTRIES", "registry_for_profile"}:
        return "profiles"
    return "games"


def _games_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if is_typeddict(value):
        return "TypedDict"
    if inspect.isfunction(value):
        return "function"
    if isinstance(value, dict):
        return "dict constant"
    return type(value).__name__


def _games_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if is_typeddict(value):
        return "TypedDict schema"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation, strip_string_quotes=True)
    if isinstance(value, dict):
        return f"dict[{len(value)}]"
    return type(value).__name__


def _games_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if symbol == "PROFILE_REGISTRIES" and isinstance(value, dict):
        return ", ".join(sorted(str(key) for key in value))
    return ""


def _games_api_registry_seam(feature: str) -> str:
    if feature == "games-api":
        return "games facade API table"
    return "game profile registry"
