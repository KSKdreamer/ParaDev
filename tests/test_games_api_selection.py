import paradev.games as games
from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.games import (
    get_games_api_selection,
    get_games_api_table,
    render_games_api_reference_markdown,
)


def test_games_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_games_api_table()
    assert_api_selection_projection(
        get_games_api_selection,
        table,
        symbol="registry_for_profile",
        index_cases=(
            ("module_index", "games.api"),
            ("feature_index", "profiles"),
            ("kind_index", "function"),
        ),
    )


def test_games_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_games_api_selection,
        symbol="registry_for_profile",
        index_name="module_index",
        key="games.api",
    )


def test_games_api_table_lists_selection_helper() -> None:
    table = get_games_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(games.__all__)
    assert table["module_index"]["games.api"] == [
        "GAMES_API_TABLE_SCHEMA",
        "GamesApiRow",
        "GamesApiTable",
        "get_games_api_selection",
        "get_games_api_table",
        "render_games_api_reference_markdown",
    ]
    assert table["feature_index"]["games-api"] == table["module_index"]["games.api"]
    assert row_by_symbol["get_games_api_selection"]["returns"] == "GamesApiTable | GamesApiRow | list[str]"
    assert row_by_symbol["get_games_api_selection"]["registry_seam"] == "games facade API table"


def test_games_api_reference_documents_selection_helper() -> None:
    reference = render_games_api_reference_markdown()

    assert "`get_games_api_selection`" in reference
    assert load_txt("docs/user-manual/games-api-reference.md") == reference
