import paradev.surfaces as surfaces
from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.surfaces import (
    get_mcp_api_selection,
    get_rest_api_selection,
    get_surfaces_api_selection,
    get_surfaces_api_table,
    render_surfaces_api_reference_markdown,
)


def test_surfaces_facade_exports_rest_and_mcp_selection_helpers() -> None:
    assert "get_rest_api_selection" in surfaces.__all__
    assert "get_mcp_api_selection" in surfaces.__all__
    assert surfaces.get_rest_api_selection is get_rest_api_selection
    assert surfaces.get_mcp_api_selection is get_mcp_api_selection

    assert get_rest_api_selection(symbol="GET /health")["path"] == "/health"
    assert get_mcp_api_selection(symbol="api_catalog")["sdk_method"] == "get_api_catalog_selection"


def test_surfaces_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_surfaces_api_table()
    assert_api_selection_projection(
        get_surfaces_api_selection,
        table,
        symbol="get_rest_api_selection",
        index_cases=(
            ("module_index", "rest"),
            ("feature_index", "mcp"),
            ("kind_index", "function"),
        ),
        mutation_symbol="get_mcp_api_selection",
    )


def test_surfaces_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_surfaces_api_selection,
        symbol="get_surfaces_api_table",
        index_name="module_index",
        key="api",
    )


def test_surfaces_api_table_lists_rest_and_mcp_selection_helpers() -> None:
    table = get_surfaces_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(surfaces.__all__)
    assert "get_surfaces_api_selection" in surfaces.__all__
    assert surfaces.get_surfaces_api_selection is get_surfaces_api_selection
    assert "get_surfaces_api_selection" in table["module_index"]["api"]
    assert "get_rest_api_selection" in table["module_index"]["rest"]
    assert "get_mcp_api_selection" in table["module_index"]["mcp"]
    assert table["feature_index"]["surfaces-api"] == [
        "SURFACES_API_TABLE_SCHEMA",
        "SurfacesApiRow",
        "SurfacesApiTable",
        "get_surfaces_api_selection",
        "get_surfaces_api_table",
        "render_surfaces_api_reference_markdown",
    ]
    assert table["feature_index"]["rest"] == [
        "get_rest_api_selection",
        "get_rest_api_table",
        "render_rest_api_reference_markdown",
    ]
    assert table["feature_index"]["mcp"] == [
        "get_mcp_api_selection",
        "get_mcp_api_table",
        "get_mcp_contract",
        "render_mcp_api_reference_markdown",
    ]

    assert row_by_symbol["get_rest_api_selection"]["returns"] == "RestApiTable | RestApiRow | list[str]"
    assert row_by_symbol["get_rest_api_selection"]["registry_seam"] == "REST/OpenAPI route contract"
    assert row_by_symbol["get_mcp_api_selection"]["returns"] == "McpApiTable | McpApiRow | list[str]"
    assert row_by_symbol["get_mcp_api_selection"]["registry_seam"] == "MCP tool contract"
    assert row_by_symbol["get_surfaces_api_selection"]["returns"] == "SurfacesApiTable | SurfacesApiRow | list[str]"
    assert row_by_symbol["get_surfaces_api_selection"]["registry_seam"] == "surface facade API table"


def test_surfaces_api_reference_documents_selection_helpers() -> None:
    reference = render_surfaces_api_reference_markdown()

    assert "`get_surfaces_api_selection`" in reference
    assert "`get_rest_api_selection`" in reference
    assert "`get_mcp_api_selection`" in reference
    assert load_txt("docs/user-manual/surfaces-api-reference.md") == reference
