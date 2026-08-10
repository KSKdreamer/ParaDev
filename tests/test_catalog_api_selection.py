from heavenbase.utils import load_txt

from api_selection_contracts import assert_api_selection_projection, assert_api_selection_rejects_invalid_selectors
from paradev.hb import (
    CATALOG_API_TABLE_ROWS,
    get_catalog_api_selection,
    get_catalog_api_table,
    render_catalog_api_reference_markdown,
)


def test_catalog_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_catalog_api_table()
    assert_api_selection_projection(
        get_catalog_api_selection,
        table,
        symbol="catalog_query",
        index_cases=(
            ("surface_index", "sdk"),
            ("feature_index", "query"),
        ),
        mutation_field="raises",
    )


def test_catalog_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_catalog_api_selection,
        symbol="catalog_query",
        index_name="surface_index",
        key="sdk",
    )


def test_catalog_api_table_lists_selection_helper() -> None:
    table = get_catalog_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(CATALOG_API_TABLE_ROWS)
    assert table["feature_index"]["api-table"] == [
        "CATALOG_API_TABLE_SCHEMA",
        "CATALOG_API_TABLE_ROWS",
        "CatalogApiRow",
        "CatalogApiTable",
        "get_catalog_api_selection",
        "get_catalog_api_table",
        "render_catalog_api_reference_markdown",
        "paradev catalog-api",
        "paradev catalog-api --markdown",
        "GET /catalog-api",
        "catalog_api",
    ]
    assert "get_catalog_api_selection" in table["surface_index"]["sdk"]
    assert table["surface_index"]["mcp"][-1] == "catalog_api"
    assert row_by_symbol["get_catalog_api_selection"]["returns"] == "CatalogApiTable | CatalogApiRow | list[str]"
    assert row_by_symbol["get_catalog_api_selection"]["registry_seam"] == "none"


def test_catalog_api_reference_documents_selection_helper() -> None:
    reference = render_catalog_api_reference_markdown()

    assert "`get_catalog_api_selection`" in reference
    assert load_txt("docs/user-manual/catalog-api-reference.md", encoding="utf-8") == reference
