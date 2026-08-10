import paradev.localization as localization
from heavenbase.utils import load_txt

from api_selection_contracts import assert_api_selection_projection, assert_api_selection_rejects_invalid_selectors
from paradev.localization import (
    get_localization_api_selection,
    get_localization_api_table,
    render_localization_api_reference_markdown,
)


def test_localization_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_localization_api_table()
    assert_api_selection_projection(
        get_localization_api_selection,
        table,
        symbol="canonical_language",
        index_cases=(
            ("module_index", "api"),
            ("feature_index", "languages"),
            ("kind_index", "function"),
        ),
    )


def test_localization_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_localization_api_selection,
        symbol="canonical_language",
        index_name="module_index",
        key="api",
    )


def test_localization_api_table_lists_selection_helper() -> None:
    table = get_localization_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(localization.__all__)
    assert table["module_index"]["api"] == [
        "LOCALIZATION_API_TABLE_SCHEMA",
        "LocalizationApiRow",
        "LocalizationApiTable",
        "get_localization_api_selection",
        "get_localization_api_table",
        "render_localization_api_reference_markdown",
    ]
    assert table["feature_index"]["localization-api"] == table["module_index"]["api"]
    assert row_by_symbol["get_localization_api_selection"]["returns"] == ("LocalizationApiTable | LocalizationApiRow | list[str]")
    assert row_by_symbol["get_localization_api_selection"]["registry_seam"] == "localization facade API table"


def test_localization_api_reference_documents_selection_helper() -> None:
    reference = render_localization_api_reference_markdown()

    assert "`get_localization_api_selection`" in reference
    assert load_txt("docs/user-manual/localization-api-reference.md") == reference
