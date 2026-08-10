import paradev.build as build
from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.build import (
    get_build_api_selection,
    get_build_api_table,
    render_build_api_reference_markdown,
)


def test_build_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_build_api_table()
    assert_api_selection_projection(
        get_build_api_selection,
        table,
        symbol="BuildRegistry",
        index_cases=(
            ("module_index", "api"),
            ("feature_index", "families"),
            ("kind_index", "function"),
        ),
    )


def test_build_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_build_api_selection,
        symbol="BuildRegistry",
        index_name="module_index",
        key="api",
    )


def test_build_api_table_lists_selection_helper() -> None:
    table = get_build_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(build.__all__)
    assert table["module_index"]["api"] == [
        "BUILD_API_TABLE_SCHEMA",
        "BuildApiRow",
        "BuildApiTable",
        "get_build_api_selection",
        "get_build_api_table",
        "render_build_api_reference_markdown",
    ]
    assert table["feature_index"]["api-table"] == table["module_index"]["api"]
    assert row_by_symbol["get_build_api_selection"]["returns"] == "BuildApiTable | BuildApiRow | list[str]"
    assert row_by_symbol["get_build_api_selection"]["registry_seam"] == "none"


def test_build_api_reference_documents_selection_helper() -> None:
    reference = render_build_api_reference_markdown()

    assert "`get_build_api_selection`" in reference
    assert load_txt("docs/user-manual/build-api-reference.md") == reference
