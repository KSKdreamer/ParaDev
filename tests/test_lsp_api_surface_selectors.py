from __future__ import annotations

import pytest
from heavenbase.utils import load_txt

from paradev.sdk import (
    LSP_API_TABLE_SCHEMA,
    get_lsp_api_selection,
    get_lsp_api_table,
    render_lsp_api_reference_markdown,
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


def test_lsp_api_table_lists_rest_and_mcp_selector_surfaces() -> None:
    table = get_lsp_api_table()
    rows = {row["symbol"]: row for row in table["rows"]}

    assert get_lsp_api_selection(index_name="surface_index", key="rest") == [
        "POST /lsp/diagnostics",
        "POST /lsp/symbols",
        "POST /lsp/hover",
        "POST /lsp/formatting",
        "POST /lsp/completion",
        "POST /lsp/semantic-tokens",
        "GET /lsp-api",
    ]
    assert get_lsp_api_selection(index_name="surface_index", key="mcp") == ["lsp_api"]
    assert "GET /lsp-api" in table["feature_index"]["api-table"]
    assert "lsp_api" in table["feature_index"]["api-table"]

    assert rows["GET /lsp-api"] == {
        "symbol": "GET /lsp-api",
        "kind": "REST route",
        "layer": "rest",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "LspApiTable | LspApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "OpenAPI path /lsp-api",
        "surface": "rest",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_lsp_api_surface_selectors.py::test_lsp_api_table_lists_rest_and_mcp_selector_surfaces",
    }
    assert rows["lsp_api"] == {
        "symbol": "lsp_api",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "LspApiTable | LspApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "MCP tool registry",
        "surface": "mcp",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_lsp_api_surface_selectors.py::test_lsp_api_table_lists_rest_and_mcp_selector_surfaces",
    }


def test_mcp_contract_exposes_lsp_api_selector_tool() -> None:
    contract = get_mcp_contract()
    tools = {tool["name"]: tool for tool in contract["tool_contracts"]}

    assert "lsp_api" in contract["tools"]
    assert tools["lsp_api"] == {
        "name": "lsp_api",
        "sdk_method": "get_lsp_api_selection",
        "read_only": True,
        "selectors": ["symbol", "index_name", "key"],
    }

    row = get_mcp_api_selection(symbol="lsp_api")
    assert row["feature"] == "lsp"
    assert row["mode"] == "read"
    assert row["sdk_method"] == "get_lsp_api_selection"
    assert row["inputs"] == "symbol, index_name, key"
    assert row["returns"] == "LSP API table, row, or index lookup payload"
    assert row["raises"] == "ValueError or KeyError on invalid LSP API selector"
    assert get_mcp_api_selection(index_name="feature_index", key="lsp") == ["lsp_api"]


def test_lsp_api_rest_route_outputs_selector_json() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())
    row_response = client.get("/lsp-api", params={"symbol": "get_lsp_api_selection"})
    index_response = client.get("/lsp-api", params={"index_name": "surface_index", "key": "mcp"})
    bad_response = client.get("/lsp-api", params={"symbol": "missing_symbol"})

    assert row_response.status_code == 200, row_response.text
    assert row_response.json()["symbol"] == "get_lsp_api_selection"
    assert index_response.status_code == 200, index_response.text
    assert index_response.json() == ["lsp_api"]
    assert bad_response.status_code == 400
    assert "unknown API table symbol" in bad_response.json()["detail"]


def test_lsp_api_rest_openapi_and_route_row_advertise_selectors() -> None:
    operation = get_openapi_seed()["paths"]["/lsp-api"]["get"]
    parameters = {parameter["name"]: parameter for parameter in operation["parameters"]}

    assert list(parameters) == ["symbol", "index_name", "key"]
    assert all(not parameter["required"] for parameter in parameters.values())

    row = get_rest_api_selection(symbol="GET /lsp-api")
    assert row["feature"] == "lsp"
    assert row["inputs"] == "query:symbol, query:index_name, query:key"
    assert row["required_inputs"] == "none"
    assert row["returns"] == "200 LSP API table, row, or index lookup payload."
    assert row["raises"] == "400 Invalid LSP API selector."


def test_generated_references_document_lsp_api_surface_selectors() -> None:
    lsp_reference = render_lsp_api_reference_markdown()
    mcp_reference = render_mcp_api_reference_markdown()
    rest_reference = render_rest_api_reference_markdown()

    assert "| `rest` | 7 | `POST /lsp/diagnostics`, `POST /lsp/symbols`, `POST /lsp/hover`," in lsp_reference
    assert "| `mcp` | 1 | `lsp_api` |" in lsp_reference
    assert "| `lsp` | 1 | `lsp_api` |" in mcp_reference
    assert "| `GET /lsp-api` | `REST route` | `rest` | `lsp` | `GET` | `/lsp-api` |" in rest_reference

    assert load_txt("docs/user-manual/lsp-api-reference.md", encoding="utf-8") == lsp_reference
    assert load_txt("docs/user-manual/mcp-api-reference.md", encoding="utf-8") == mcp_reference
    assert load_txt("docs/user-manual/rest-api-reference.md", encoding="utf-8") == rest_reference
