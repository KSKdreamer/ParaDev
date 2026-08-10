import paradev.sdk.copy_roots as copy_roots
from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.sdk.copy_roots import (
    get_copy_roots_api_selection,
    get_copy_roots_api_table,
    render_copy_roots_api_reference_markdown,
)


def test_copy_roots_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_copy_roots_api_table()
    assert_api_selection_projection(
        get_copy_roots_api_selection,
        table,
        symbol="copy_root_artifacts",
        index_cases=(
            ("module_index", "sdk.copy_roots"),
            ("feature_index", "copy-roots-api"),
            ("kind_index", "function"),
        ),
    )


def test_copy_roots_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_copy_roots_api_selection,
        symbol="copy_root_artifacts",
        index_name="module_index",
        key="sdk.copy_roots",
    )


def test_copy_roots_api_table_lists_selection_helper() -> None:
    table = get_copy_roots_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(copy_roots.__all__)
    assert table["feature_index"]["copy-roots-api"] == [
        "COPY_ROOTS_API_TABLE_SCHEMA",
        "CopyRootsApiRow",
        "CopyRootsApiTable",
        "get_copy_roots_api_selection",
        "get_copy_roots_api_table",
        "render_copy_roots_api_reference_markdown",
    ]
    assert table["module_index"]["sdk.copy_roots"][-6:] == table["feature_index"]["copy-roots-api"]
    assert row_by_symbol["get_copy_roots_api_selection"]["returns"] == "CopyRootsApiTable | CopyRootsApiRow | list[str]"
    assert row_by_symbol["get_copy_roots_api_selection"]["registry_seam"] == "copy roots API table"


def test_copy_roots_api_reference_documents_selection_helper() -> None:
    reference = render_copy_roots_api_reference_markdown()

    assert "`get_copy_roots_api_selection`" in reference
    assert load_txt("docs/user-manual/copy-roots-api-reference.md") == reference
