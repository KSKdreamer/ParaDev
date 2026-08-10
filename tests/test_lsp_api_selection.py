from heavenbase.utils import load_txt

from api_selection_contracts import assert_api_selection_projection, assert_api_selection_rejects_invalid_selectors
from paradev.sdk.lsp import (
    LSP_API_TABLE_ROWS,
    get_lsp_api_selection,
    get_lsp_api_table,
    render_lsp_api_reference_markdown,
)


def test_lsp_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_lsp_api_table()
    assert_api_selection_projection(
        get_lsp_api_selection,
        table,
        symbol="complete_pdx_lsp_text",
        index_cases=(
            ("surface_index", "sdk"),
            ("feature_index", "completion"),
        ),
        mutation_field="raises",
    )


def test_lsp_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_lsp_api_selection,
        symbol="complete_pdx_lsp_text",
        index_name="surface_index",
        key="sdk",
    )


def test_lsp_api_table_lists_selection_helper() -> None:
    table = get_lsp_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(LSP_API_TABLE_ROWS)
    assert table["feature_index"]["api-table"] == [
        "LSP_API_TABLE_SCHEMA",
        "LSP_API_TABLE_ROWS",
        "LspApiRow",
        "LspApiTable",
        "get_lsp_api_selection",
        "get_lsp_api_table",
        "render_lsp_api_reference_markdown",
        "paradev lsp-api",
        "paradev lsp-api --markdown",
        "GET /lsp-api",
        "lsp_api",
    ]
    assert "get_lsp_api_selection" in table["surface_index"]["sdk"]
    assert table["surface_index"]["mcp"] == ["lsp_api"]
    assert row_by_symbol["get_lsp_api_selection"]["returns"] == "LspApiTable | LspApiRow | list[str]"
    assert row_by_symbol["get_lsp_api_selection"]["registry_seam"] == "none"


def test_lsp_api_reference_documents_selection_helper() -> None:
    reference = render_lsp_api_reference_markdown()

    assert "`get_lsp_api_selection`" in reference
    assert load_txt("docs/user-manual/lsp-api-reference.md", encoding="utf-8") == reference
