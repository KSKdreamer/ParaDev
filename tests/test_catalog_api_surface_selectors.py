import pytest
from heavenbase.utils import load_txt

from paradev.hb import (
    CATALOG_API_TABLE_SCHEMA,
    get_catalog_api_selection,
    get_catalog_api_table,
    render_catalog_api_reference_markdown,
)
from paradev.surfaces.mcp import get_mcp_api_table, get_mcp_contract, render_mcp_api_reference_markdown
from paradev.surfaces.rest import get_openapi_seed, get_rest_api_table, render_rest_api_reference_markdown


def test_catalog_api_table_lists_rest_and_mcp_selector_surfaces() -> None:
    table = get_catalog_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["surface_index"]["rest"] == [
        "GET /projects/inspect?kind=catalog-preview",
        "GET /projects/inspect?kind=catalog-query",
        "GET /projects/catalog",
        "POST /projects/catalog",
        "PUT /projects/catalog",
        "GET /catalog-api",
    ]
    assert table["surface_index"]["mcp"] == [
        "project_inspect kind=catalog-preview",
        "project_inspect kind=catalog-query",
        "catalog_api",
    ]
    assert table["feature_index"]["api-table"][-2:] == ["GET /catalog-api", "catalog_api"]
    assert get_catalog_api_selection(index_name="surface_index", key="mcp") == table["surface_index"]["mcp"]

    expected_common = {
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "CatalogApiTable | CatalogApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "payload_schema": CATALOG_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/catalog-api-reference.md",
        "test_anchor": "tests/test_catalog_api_surface_selectors.py::test_catalog_api_table_lists_rest_and_mcp_selector_surfaces",
    }
    assert row_by_symbol["GET /catalog-api"] == {
        "symbol": "GET /catalog-api",
        "kind": "REST route",
        "layer": "rest",
        "registry_seam": "OpenAPI path /catalog-api",
        "surface": "rest",
        **expected_common,
    }
    assert row_by_symbol["catalog_api"] == {
        "symbol": "catalog_api",
        "kind": "MCP tool",
        "layer": "mcp",
        "registry_seam": "MCP tool registry",
        "surface": "mcp",
        **expected_common,
    }


def test_mcp_contract_exposes_catalog_api_selector_tool() -> None:
    contract = get_mcp_contract()
    table = get_mcp_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}
    tools = {tool["name"]: tool for tool in contract["tool_contracts"]}

    assert tools["catalog_api"] == {
        "name": "catalog_api",
        "sdk_method": "get_catalog_api_selection",
        "read_only": True,
        "selectors": ["symbol", "index_name", "key"],
    }
    assert table["feature_index"]["catalog"] == ["catalog_api"]
    assert row_by_symbol["catalog_api"]["mode"] == "read"
    assert row_by_symbol["catalog_api"]["inputs"] == "symbol, index_name, key"
    assert row_by_symbol["catalog_api"]["returns"] == "Catalog API table, row, or index lookup payload"
    assert row_by_symbol["catalog_api"]["raises"] == "ValueError or KeyError on invalid catalog API selector"


def test_catalog_api_rest_route_outputs_selector_json() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())

    table_response = client.get("/catalog-api")
    row_response = client.get("/catalog-api", params={"symbol": "catalog_query"})
    index_response = client.get("/catalog-api", params={"index_name": "surface_index", "key": "mcp"})
    unknown_response = client.get("/catalog-api", params={"symbol": "missing"})

    assert table_response.status_code == 200, table_response.text
    assert table_response.json()["schema"] == CATALOG_API_TABLE_SCHEMA
    assert row_response.status_code == 200, row_response.text
    assert row_response.json()["symbol"] == "catalog_query"
    assert index_response.status_code == 200, index_response.text
    assert index_response.json() == ["project_inspect kind=catalog-preview", "project_inspect kind=catalog-query", "catalog_api"]
    assert unknown_response.status_code == 400
    assert "unknown API table symbol 'missing'" in unknown_response.json()["detail"]


def test_catalog_api_rest_openapi_and_route_row_advertise_selectors() -> None:
    seed = get_openapi_seed()
    rest_table = get_rest_api_table()
    row_by_symbol = {row["symbol"]: row for row in rest_table["rows"]}

    catalog_api = seed["paths"]["/catalog-api"]["get"]
    assert [param["name"] for param in catalog_api["parameters"]] == ["symbol", "index_name", "key"]
    assert catalog_api["responses"]["200"]["description"] == "Catalog API table, row, or index lookup payload."
    assert catalog_api["responses"]["400"]["description"] == "Invalid catalog API selector."
    assert row_by_symbol["GET /catalog-api"]["feature"] == "catalog"
    assert row_by_symbol["GET /catalog-api"]["inputs"] == "query:symbol, query:index_name, query:key"
    assert row_by_symbol["GET /catalog-api"]["returns"] == "200 Catalog API table, row, or index lookup payload."
    assert row_by_symbol["GET /catalog-api"]["raises"] == "400 Invalid catalog API selector."


def test_generated_references_document_catalog_api_surface_selectors() -> None:
    catalog_reference = render_catalog_api_reference_markdown()
    mcp_reference = render_mcp_api_reference_markdown()
    rest_reference = render_rest_api_reference_markdown()

    assert "| `api-table` | 11 | `CATALOG_API_TABLE_SCHEMA`, `CATALOG_API_TABLE_ROWS`, `CatalogApiRow`," in catalog_reference
    assert "| `mcp` | 3 | `project_inspect kind=catalog-preview`, `project_inspect kind=catalog-query`, `catalog_api` |" in catalog_reference
    assert "| `catalog` | 1 | `catalog_api` |" in mcp_reference
    assert "| `GET /catalog-api` | `REST route` | `rest` | `catalog` | `GET` | `/catalog-api` |" in rest_reference

    assert load_txt("docs/user-manual/catalog-api-reference.md", encoding="utf-8") == catalog_reference
    assert load_txt("docs/user-manual/mcp-api-reference.md", encoding="utf-8") == mcp_reference
    assert load_txt("docs/user-manual/rest-api-reference.md", encoding="utf-8") == rest_reference
