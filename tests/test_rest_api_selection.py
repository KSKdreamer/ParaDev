from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.surfaces.rest import (
    get_rest_api_selection,
    get_rest_api_table,
    render_rest_api_reference_markdown,
)


def test_rest_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_rest_api_table()
    assert_api_selection_projection(
        get_rest_api_selection,
        table,
        symbol="GET /api-catalog",
        index_cases=(
            ("method_index", "GET"),
            ("feature_index", "frontend-api"),
            ("frontend_operation_index", "catalog.write"),
        ),
        mutation_symbol="GET /frontend-api",
        mutation_field="frontend_operation_ids",
        mutation_mode="append",
    )


def test_rest_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_rest_api_selection,
        symbol="GET /health",
        index_name="method_index",
        key="GET",
        unknown_symbol="GET /missing",
    )


def test_rest_api_reference_documents_selection_helper() -> None:
    reference = render_rest_api_reference_markdown()

    assert "Use `get_rest_api_selection(symbol=..., index_name=..., key=...)`" in reference
    assert load_txt("docs/user-manual/rest-api-reference.md") == reference
