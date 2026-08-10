import paradev.pdx as pdx
from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.pdx import (
    get_pdx_core_api_selection,
    get_pdx_core_api_table,
    render_pdx_core_api_reference_markdown,
)


def test_pdx_core_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_pdx_core_api_table()
    assert_api_selection_projection(
        get_pdx_core_api_selection,
        table,
        symbol="PDXBlock",
        index_cases=(
            ("module_index", "api"),
            ("feature_index", "parser"),
            ("kind_index", "function"),
        ),
    )


def test_pdx_core_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_pdx_core_api_selection,
        symbol="PDXBlock",
        index_name="module_index",
        key="api",
    )


def test_pdx_core_api_table_lists_selection_helper() -> None:
    table = get_pdx_core_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(pdx.__all__)
    assert table["module_index"]["api"] == [
        "PDX_CORE_API_TABLE_SCHEMA",
        "PdxCoreApiRow",
        "PdxCoreApiTable",
        "get_pdx_core_api_selection",
        "get_pdx_core_api_table",
        "render_pdx_core_api_reference_markdown",
    ]
    assert table["feature_index"]["pdx-core-api"] == table["module_index"]["api"]
    assert row_by_symbol["get_pdx_core_api_selection"]["returns"] == "PdxCoreApiTable | PdxCoreApiRow | list[str]"
    assert row_by_symbol["get_pdx_core_api_selection"]["registry_seam"] == "PDX core facade API table"


def test_pdx_core_api_reference_documents_selection_helper() -> None:
    reference = render_pdx_core_api_reference_markdown()

    assert "`get_pdx_core_api_selection`" in reference
    assert load_txt("docs/user-manual/pdx-core-api-reference.md") == reference
