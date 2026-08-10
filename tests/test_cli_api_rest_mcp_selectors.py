import pytest
from heavenbase.utils import load_txt


def test_cli_api_rest_route_outputs_selector_json() -> None:
    from fastapi.testclient import TestClient

    from paradev.api import build_app
    from paradev.surfaces.cli import get_cli_api_table

    client = TestClient(build_app())
    cli_table = get_cli_api_table()
    table_response = client.get("/cli-api")
    row_response = client.get("/cli-api", params={"symbol": "paradev cli-api"})
    index_response = client.get("/cli-api", params={"index_name": "feature_index", "key": "cli"})
    unknown_response = client.get("/cli-api", params={"symbol": "missing"})

    assert table_response.status_code == 200
    assert table_response.json()["schema"] == "paradev.cli.api-table.v1"
    assert table_response.json()["row_count"] == cli_table["row_count"]
    assert row_response.status_code == 200
    assert row_response.json()["symbol"] == "paradev cli-api"
    assert index_response.status_code == 200
    assert "paradev cli-api" in index_response.json()
    assert unknown_response.status_code == 400
    assert "unknown API table symbol 'missing'" in unknown_response.json()["detail"]


def test_cli_api_openapi_and_rest_api_row_advertise_selector() -> None:
    from paradev.surfaces.rest import get_openapi_seed, get_rest_api_table, render_rest_api_reference_markdown

    seed = get_openapi_seed()
    operation = seed["paths"]["/cli-api"]["get"]
    params = {param["name"]: param for param in operation["parameters"]}
    table = get_rest_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}
    reference = render_rest_api_reference_markdown()

    assert params["symbol"]["required"] is False
    assert params["index_name"]["required"] is False
    assert params["key"]["required"] is False
    assert operation["responses"]["200"]["description"] == "CLI API table, row, or index lookup payload."
    assert operation["responses"]["400"]["description"] == "Invalid CLI API selector."
    assert table["row_count"] == len(table["rows"])
    assert len(table["method_index"]["GET"]) == 37
    assert table["feature_index"]["cli"] == ["GET /cli-api"]
    assert row_by_symbol["GET /cli-api"]["feature"] == "cli"
    assert row_by_symbol["GET /cli-api"]["inputs"] == "query:symbol, query:index_name, query:key"
    assert row_by_symbol["GET /cli-api"]["required_inputs"] == "none"
    assert row_by_symbol["GET /cli-api"]["returns"] == "200 CLI API table, row, or index lookup payload."
    assert row_by_symbol["GET /cli-api"]["raises"] == "400 Invalid CLI API selector."
    assert "| `GET` | 37 | `GET /health`, `GET /api-catalog`, `GET /rest-api`, `GET /cli-api`," in reference
    assert "| `cli` | 1 | `GET /cli-api` |" in reference
    assert (
        "| `GET /cli-api` | `REST route` | `rest` | `cli` | `GET` | `/cli-api` | "
        "`query:symbol, query:index_name, query:key` | `none` | "
        "`200 CLI API table, row, or index lookup payload.` | `400 Invalid CLI API selector.` |"
    ) in reference
    assert load_txt("docs/user-manual/rest-api-reference.md") == reference


def test_mcp_contract_exposes_cli_api_selector_tool() -> None:
    from paradev.surfaces.mcp import get_mcp_api_table, get_mcp_contract, render_mcp_api_reference_markdown

    contract = get_mcp_contract()
    tools = {tool["name"]: tool for tool in contract["tool_contracts"]}
    table = get_mcp_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}
    reference = render_mcp_api_reference_markdown()

    assert tools["cli_api"] == {
        "name": "cli_api",
        "sdk_method": "get_cli_api_selection",
        "read_only": True,
        "selectors": ["symbol", "index_name", "key"],
    }
    assert table["row_count"] == len(table["rows"])
    assert len(table["mode_index"]["read"]) == 31
    assert table["feature_index"]["cli"] == ["cli_api"]
    assert row_by_symbol["cli_api"]["mode"] == "read"
    assert row_by_symbol["cli_api"]["inputs"] == "symbol, index_name, key"
    assert row_by_symbol["cli_api"]["returns"] == "CLI API table, row, or index lookup payload"
    assert row_by_symbol["cli_api"]["raises"] == "ValueError or KeyError on invalid CLI API selector"
    assert ("| `read` | 31 | `project_inspections`, `project_inspect`, " "`project_templates`,") in reference
    assert "| `cli` | 1 | `cli_api` |" in reference
    assert (
        "| `cli_api` | `MCP tool` | `mcp` | `cli` | `read` | `get_cli_api_selection` | "
        "`symbol, index_name, key` | `CLI API table, row, or index lookup payload` | "
        "`ValueError or KeyError on invalid CLI API selector` |"
    ) in reference
    assert load_txt("docs/user-manual/mcp-api-reference.md") == reference


def test_api_catalog_tracks_cli_api_rest_mcp_surfaces() -> None:
    from paradev.surfaces import get_api_catalog_table, render_api_catalog_reference_markdown
    from paradev.surfaces.cli import get_cli_api_table
    from paradev.surfaces.mcp import get_mcp_api_table
    from paradev.surfaces.rest import get_rest_api_table

    cli_row_count = get_cli_api_table()["row_count"]
    rest_row_count = get_rest_api_table()["row_count"]
    mcp_row_count = get_mcp_api_table()["row_count"]
    table = get_api_catalog_table()
    row_by_id = {row["id"]: row for row in table["rows"]}
    reference = render_api_catalog_reference_markdown()

    assert row_by_id["cli-api"]["surfaces"] == ["cli", "rest", "mcp", "frontend", "docs"]
    assert row_by_id["cli-api"]["row_count"] == cli_row_count
    assert row_by_id["rest-api"]["row_count"] == rest_row_count
    assert row_by_id["mcp-api"]["row_count"] == mcp_row_count
    assert len(table["surface_index"]["rest"]) == 12
    assert len(table["surface_index"]["mcp"]) == 11
    assert "cli-api" in table["surface_index"]["rest"]
    assert "cli-api" in table["surface_index"]["mcp"]
    assert "| `rest` | 12 | `api-catalog`, `surfaces-api`, `frontend-api`," in reference
    assert "| `mcp` | 11 | `api-catalog`, `surfaces-api`, `frontend-api`," in reference
    assert (
        f"| `cli-api` | CLI API Reference | `command-table` | `cli` | `cli` | `paradev.cli.api-table.v1` | {cli_row_count} | "
        "`get_cli_api_table` | `get_cli_api_selection` | `render_cli_api_reference_markdown` | "
        "`cli-api` | `cli-api --markdown` | `adapter_index`, `feature_index`, `frontend_operation_index`, "
        "`kind_index` | `cli`, `rest`, `mcp`, `frontend`, `docs` |"
    ) in reference
    assert load_txt("docs/user-manual/api-catalog-reference.md") == reference


@pytest.mark.parametrize(
    ("index_name", "key"),
    [
        ("surface", "rest"),
        ("surface", "mcp"),
    ],
)
def test_api_catalog_surface_indexes_include_cli_api(index_name: str, key: str) -> None:
    from paradev.surfaces import get_api_catalog_selection

    assert "cli-api" in get_api_catalog_selection(index_name=index_name, key=key)
