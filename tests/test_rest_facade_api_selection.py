import paradev.api as rest_facade
from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.api import (
    get_rest_facade_api_selection,
    get_rest_facade_api_table,
    render_rest_facade_api_reference_markdown,
)


def test_rest_facade_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_rest_facade_api_table()
    assert_api_selection_projection(
        get_rest_facade_api_selection,
        table,
        symbol="build_app",
        index_cases=(
            ("module_index", "api"),
            ("feature_index", "project-drafts"),
            ("kind_index", "function"),
        ),
    )


def test_rest_facade_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_rest_facade_api_selection,
        symbol="build_app",
        index_name="module_index",
        key="api",
    )


def test_rest_facade_api_table_lists_selection_helper() -> None:
    table = get_rest_facade_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(rest_facade.__all__)
    assert table["module_index"]["api"] == [
        "REST_FACADE_API_TABLE_SCHEMA",
        "RestFacadeApiRow",
        "RestFacadeApiTable",
        "get_rest_facade_api_selection",
        "get_rest_facade_api_table",
        "render_rest_facade_api_reference_markdown",
    ]
    assert table["feature_index"]["rest-facade-api"] == table["module_index"]["api"]
    assert row_by_symbol["get_rest_facade_api_selection"]["returns"] == ("RestFacadeApiTable | RestFacadeApiRow | list[str]")
    assert row_by_symbol["get_rest_facade_api_selection"]["registry_seam"] == "REST facade API table"


def test_rest_facade_api_reference_documents_selection_helper() -> None:
    reference = render_rest_facade_api_reference_markdown()

    assert "`get_rest_facade_api_selection`" in reference
    assert load_txt("docs/user-manual/rest-facade-api-reference.md") == reference
