import pytest
from heavenbase.utils import load_txt

from paradev.surfaces.mcp import get_mcp_api_table, get_mcp_contract, render_mcp_api_reference_markdown
from paradev.surfaces.rest import get_openapi_seed, get_rest_api_table, render_rest_api_reference_markdown


def test_rest_api_rest_route_outputs_selector_json() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())

    table_response = client.get("/rest-api")
    row_response = client.get("/rest-api", params={"symbol": "GET /rest-api"})
    index_response = client.get("/rest-api", params={"index_name": "feature_index", "key": "rest"})
    unknown_response = client.get("/rest-api", params={"symbol": "GET /missing"})

    assert table_response.status_code == 200, table_response.text
    assert table_response.json()["schema"] == "paradev.rest.api-table.v1"
    assert row_response.status_code == 200, row_response.text
    assert row_response.json()["symbol"] == "GET /rest-api"
    assert index_response.status_code == 200, index_response.text
    assert index_response.json() == ["GET /rest-api"]
    assert unknown_response.status_code == 400
    assert "unknown API table symbol 'GET /missing'" in unknown_response.json()["detail"]


def test_rest_api_openapi_and_route_row_advertise_self_selector() -> None:
    seed = get_openapi_seed()
    table = get_rest_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    rest_api = seed["paths"]["/rest-api"]["get"]
    assert [param["name"] for param in rest_api["parameters"]] == ["symbol", "index_name", "key"]
    assert rest_api["responses"]["200"]["description"] == "REST API table, row, or index lookup payload."
    assert rest_api["responses"]["400"]["description"] == "Invalid REST API selector."
    assert table["feature_index"]["rest"] == ["GET /rest-api"]
    assert row_by_symbol["GET /rest-api"]["inputs"] == "query:symbol, query:index_name, query:key"
    assert row_by_symbol["GET /rest-api"]["required_inputs"] == "none"
    assert row_by_symbol["GET /rest-api"]["returns"] == "200 REST API table, row, or index lookup payload."
    assert row_by_symbol["GET /rest-api"]["raises"] == "400 Invalid REST API selector."


def test_mcp_contract_exposes_mcp_api_self_selector_tool() -> None:
    contract = get_mcp_contract()
    table = get_mcp_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}
    tools = {tool["name"]: tool for tool in contract["tool_contracts"]}

    assert tools["mcp_api"] == {
        "name": "mcp_api",
        "sdk_method": "get_mcp_api_selection",
        "read_only": True,
        "selectors": ["symbol", "index_name", "key"],
    }
    assert table["feature_index"]["mcp"] == ["mcp_api"]
    assert row_by_symbol["mcp_api"]["mode"] == "read"
    assert row_by_symbol["mcp_api"]["inputs"] == "symbol, index_name, key"
    assert row_by_symbol["mcp_api"]["returns"] == "MCP API table, row, or index lookup payload"
    assert row_by_symbol["mcp_api"]["raises"] == "ValueError or KeyError on invalid MCP API selector"


def test_generated_references_document_rest_and_mcp_self_selectors() -> None:
    rest_reference = render_rest_api_reference_markdown()
    mcp_reference = render_mcp_api_reference_markdown()

    assert "| `GET` | 37 | `GET /health`, `GET /api-catalog`, `GET /rest-api`," in rest_reference
    assert "| `rest` | 1 | `GET /rest-api` |" in rest_reference
    assert "| `GET /rest-api` | `REST route` | `rest` | `rest` | `GET` | `/rest-api` |" in rest_reference
    assert ("| `read` | 31 | `project_inspections`, `project_inspect`, " "`project_templates`,") in mcp_reference
    assert "| `mcp` | 1 | `mcp_api` |" in mcp_reference
    assert "| `mcp_api` | `MCP tool` | `mcp` | `mcp` | `read` | `get_mcp_api_selection` |" in mcp_reference

    assert load_txt("docs/user-manual/rest-api-reference.md", encoding="utf-8") == rest_reference
    assert load_txt("docs/user-manual/mcp-api-reference.md", encoding="utf-8") == mcp_reference
