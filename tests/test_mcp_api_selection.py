from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.surfaces.mcp import (
    get_mcp_api_selection,
    get_mcp_api_table,
    render_mcp_api_reference_markdown,
)


def test_mcp_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_mcp_api_table()
    assert_api_selection_projection(
        get_mcp_api_selection,
        table,
        symbol="api_catalog",
        index_cases=(
            ("mode_index", "read"),
            ("feature_index", "projects"),
            ("frontend_operation_index", "project.create"),
        ),
        mutation_symbol="project_inspect",
        mutation_field="frontend_operation_ids",
        mutation_mode="append",
    )


def test_mcp_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_mcp_api_selection,
        symbol="frontend_api",
        index_name="mode_index",
        key="read",
        unknown_symbol="missing_tool",
    )


def test_mcp_api_reference_documents_selection_helper() -> None:
    reference = render_mcp_api_reference_markdown()

    assert "Use `get_mcp_api_selection(symbol=..., index_name=..., key=...)`" in reference
    assert load_txt("docs/user-manual/mcp-api-reference.md") == reference
