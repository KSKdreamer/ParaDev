import paradev.lsp as lsp
from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.lsp import (
    get_lsp_server_api_selection,
    get_lsp_server_api_table,
    render_lsp_server_api_reference_markdown,
)


def test_lsp_server_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_lsp_server_api_table()
    assert_api_selection_projection(
        get_lsp_server_api_selection,
        table,
        symbol="PdxDocument",
        index_cases=(
            ("module_index", "api"),
            ("feature_index", "framing"),
            ("kind_index", "function"),
        ),
    )


def test_lsp_server_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_lsp_server_api_selection,
        symbol="PdxDocument",
        index_name="module_index",
        key="api",
    )


def test_lsp_server_api_table_lists_selection_helper() -> None:
    table = get_lsp_server_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(lsp.__all__)
    assert table["module_index"]["api"] == [
        "LSP_SERVER_API_TABLE_SCHEMA",
        "LspServerApiRow",
        "LspServerApiTable",
        "get_lsp_server_api_selection",
        "get_lsp_server_api_table",
        "render_lsp_server_api_reference_markdown",
    ]
    assert table["feature_index"]["lsp-server-api"] == table["module_index"]["api"]
    assert row_by_symbol["get_lsp_server_api_selection"]["returns"] == "LspServerApiTable | LspServerApiRow | list[str]"
    assert row_by_symbol["get_lsp_server_api_selection"]["registry_seam"] == "LSP server facade API table"


def test_lsp_server_api_reference_documents_selection_helper() -> None:
    reference = render_lsp_server_api_reference_markdown()

    assert "`get_lsp_server_api_selection`" in reference
    assert load_txt("docs/user-manual/lsp-server-api-reference.md") == reference
