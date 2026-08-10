from __future__ import annotations

import pytest
from heavenbase.utils import load_txt

from paradev.sdk import (
    PDX_API_TABLE_SCHEMA,
    get_pdx_api_selection,
    get_pdx_api_table,
    render_pdx_api_reference_markdown,
)
from paradev.surfaces.mcp import (
    get_mcp_api_selection,
    get_mcp_contract,
    render_mcp_api_reference_markdown,
)
from paradev.surfaces.rest import (
    get_openapi_seed,
    get_rest_api_selection,
    render_rest_api_reference_markdown,
)


def test_pdx_api_table_lists_rest_and_mcp_selector_surfaces() -> None:
    table = get_pdx_api_table()
    rows = {row["symbol"]: row for row in table["rows"]}

    assert get_pdx_api_selection(index_name="surface_index", key="rest") == [
        "GET /pdx/parse",
        "POST /pdx/format",
        "GET /pdx-api",
    ]
    assert get_pdx_api_selection(index_name="surface_index", key="mcp") == [
        "pdx_parse",
        "pdx_format",
        "pdx_api",
    ]
    assert "GET /pdx-api" in table["feature_index"]["api-table"]
    assert "pdx_api" in table["feature_index"]["api-table"]

    assert rows["GET /pdx-api"] == {
        "symbol": "GET /pdx-api",
        "kind": "REST route",
        "layer": "rest",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "PdxApiTable | PdxApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "OpenAPI path /pdx-api",
        "surface": "rest",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_pdx_api_surface_selectors.py::test_pdx_api_table_lists_rest_and_mcp_selector_surfaces",
    }
    assert rows["pdx_api"] == {
        "symbol": "pdx_api",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "PdxApiTable | PdxApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "MCP tool registry",
        "surface": "mcp",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_pdx_api_surface_selectors.py::test_pdx_api_table_lists_rest_and_mcp_selector_surfaces",
    }


def test_mcp_contract_exposes_pdx_api_selector_tool() -> None:
    contract = get_mcp_contract()
    tools = {tool["name"]: tool for tool in contract["tool_contracts"]}

    assert "pdx_api" in contract["tools"]
    assert tools["pdx_api"] == {
        "name": "pdx_api",
        "sdk_method": "get_pdx_api_selection",
        "read_only": True,
        "selectors": ["symbol", "index_name", "key"],
    }

    row = get_mcp_api_selection(symbol="pdx_api")
    assert row["feature"] == "pdx"
    assert row["mode"] == "read"
    assert row["sdk_method"] == "get_pdx_api_selection"
    assert row["inputs"] == "symbol, index_name, key"
    assert row["returns"] == "PDX API table, row, or index lookup payload"
    assert row["raises"] == "ValueError or KeyError on invalid PDX API selector"
    assert get_mcp_api_selection(index_name="feature_index", key="pdx") == [
        "pdx_parse",
        "pdx_format",
        "pdx_api",
    ]


def test_pdx_api_rest_route_outputs_selector_json() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())
    row_response = client.get("/pdx-api", params={"symbol": "get_pdx_api_selection"})
    index_response = client.get("/pdx-api", params={"index_name": "surface_index", "key": "mcp"})
    bad_response = client.get("/pdx-api", params={"symbol": "missing_symbol"})

    assert row_response.status_code == 200, row_response.text
    assert row_response.json()["symbol"] == "get_pdx_api_selection"
    assert index_response.status_code == 200, index_response.text
    assert index_response.json() == ["pdx_parse", "pdx_format", "pdx_api"]
    assert bad_response.status_code == 400
    assert "unknown API table symbol" in bad_response.json()["detail"]


def test_pdx_api_rest_openapi_and_route_row_advertise_selectors() -> None:
    operation = get_openapi_seed()["paths"]["/pdx-api"]["get"]
    parameters = {parameter["name"]: parameter for parameter in operation["parameters"]}

    assert list(parameters) == ["symbol", "index_name", "key"]
    assert all(not parameter["required"] for parameter in parameters.values())

    row = get_rest_api_selection(symbol="GET /pdx-api")
    assert row["feature"] == "pdx"
    assert row["inputs"] == "query:symbol, query:index_name, query:key"
    assert row["required_inputs"] == "none"
    assert row["returns"] == "200 PDX API table, row, or index lookup payload."
    assert row["raises"] == "400 Invalid PDX API selector."


def test_generated_references_document_pdx_api_surface_selectors() -> None:
    pdx_reference = render_pdx_api_reference_markdown()
    mcp_reference = render_mcp_api_reference_markdown()
    rest_reference = render_rest_api_reference_markdown()

    assert "| `rest` | 3 | `GET /pdx/parse`, `POST /pdx/format`, `GET /pdx-api` |" in pdx_reference
    assert "| `mcp` | 3 | `pdx_parse`, `pdx_format`, `pdx_api` |" in pdx_reference
    assert "| `pdx` | 3 | `pdx_parse`, `pdx_format`, `pdx_api` |" in mcp_reference
    assert "| `GET /pdx-api` | `REST route` | `rest` | `pdx` | `GET` | `/pdx-api` |" in rest_reference

    assert load_txt("docs/user-manual/pdx-api-reference.md", encoding="utf-8") == pdx_reference
    assert load_txt("docs/user-manual/mcp-api-reference.md", encoding="utf-8") == mcp_reference
    assert load_txt("docs/user-manual/rest-api-reference.md", encoding="utf-8") == rest_reference
