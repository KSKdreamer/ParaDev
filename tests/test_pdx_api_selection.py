from heavenbase.utils import load_txt

from api_selection_contracts import assert_api_selection_projection, assert_api_selection_rejects_invalid_selectors
from paradev.sdk.pdx import (
    PDX_API_TABLE_ROWS,
    get_pdx_api_selection,
    get_pdx_api_table,
    render_pdx_api_reference_markdown,
)


def test_pdx_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_pdx_api_table()
    assert_api_selection_projection(
        get_pdx_api_selection,
        table,
        symbol="format_pdx_text",
        index_cases=(
            ("surface_index", "sdk"),
            ("feature_index", "format"),
        ),
        mutation_field="raises",
    )


def test_pdx_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_pdx_api_selection,
        symbol="format_pdx_text",
        index_name="surface_index",
        key="sdk",
    )


def test_pdx_api_table_lists_selection_helper() -> None:
    table = get_pdx_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(PDX_API_TABLE_ROWS)
    assert table["feature_index"]["api-table"] == [
        "PDX_API_TABLE_SCHEMA",
        "PDX_API_TABLE_ROWS",
        "PdxApiRow",
        "PdxApiTable",
        "get_pdx_api_selection",
        "get_pdx_api_table",
        "render_pdx_api_reference_markdown",
        "paradev pdx-api",
        "paradev pdx-api --markdown",
        "GET /pdx-api",
        "pdx_api",
    ]
    assert "get_pdx_api_selection" in table["surface_index"]["sdk"]
    assert row_by_symbol["get_pdx_api_selection"]["returns"] == "PdxApiTable | PdxApiRow | list[str]"
    assert row_by_symbol["get_pdx_api_selection"]["registry_seam"] == "none"


def test_pdx_api_reference_documents_selection_helper() -> None:
    reference = render_pdx_api_reference_markdown()

    assert "`get_pdx_api_selection`" in reference
    assert load_txt("docs/user-manual/pdx-api-reference.md", encoding="utf-8") == reference
