import paradev.hb as hb
from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.hb import (
    get_hb_api_selection,
    get_hb_api_table,
    render_hb_api_reference_markdown,
)


def test_hb_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_hb_api_table()
    assert_api_selection_projection(
        get_hb_api_selection,
        table,
        symbol="catalog_preview",
        index_cases=(
            ("module_index", "api"),
            ("feature_index", "hb-api"),
            ("kind_index", "function"),
        ),
    )


def test_hb_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_hb_api_selection,
        symbol="catalog_preview",
        index_name="module_index",
        key="api",
    )


def test_hb_api_table_lists_selection_helper() -> None:
    table = get_hb_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(hb.__all__)
    assert table["module_index"]["api"] == [
        "HB_API_TABLE_SCHEMA",
        "HbApiRow",
        "HbApiTable",
        "get_hb_api_selection",
        "get_hb_api_table",
        "render_hb_api_reference_markdown",
    ]
    assert table["feature_index"]["hb-api"] == table["module_index"]["api"]
    assert row_by_symbol["get_hb_api_selection"]["returns"] == "HbApiTable | HbApiRow | list[str]"
    assert row_by_symbol["get_hb_api_selection"]["registry_seam"] == "HeavenBase facade API table"


def test_hb_api_reference_documents_selection_helper() -> None:
    reference = render_hb_api_reference_markdown()

    assert "`get_hb_api_selection`" in reference
    assert load_txt("docs/user-manual/hb-api-reference.md") == reference
