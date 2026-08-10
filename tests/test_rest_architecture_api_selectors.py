from __future__ import annotations

import pytest

from paradev.surfaces.rest import get_openapi_seed, get_rest_api_selection


def test_architecture_rest_route_outputs_api_table_selection_json() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())
    response = client.get(
        "/architecture",
        params={"api_table": "true", "symbol": "get_architecture_api_selection"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["symbol"] == "get_architecture_api_selection"
    assert payload["kind"] == "function"
    assert payload["surface"] == "sdk"


def test_architecture_rest_route_outputs_api_table_index_json() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())
    response = client.get(
        "/architecture",
        params={"api_table": "true", "index_name": "surface_index", "key": "rest"},
    )

    assert response.status_code == 200, response.text
    assert response.json() == ["GET /architecture"]


def test_architecture_rest_route_requires_api_table_for_table_selectors() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())
    response = client.get("/architecture", params={"symbol": "get_architecture_api_selection"})

    assert response.status_code == 400
    assert "architecture API table selectors require api_table=true" in response.json()["detail"]


def test_architecture_rest_openapi_and_route_row_advertise_api_table_selectors() -> None:
    operation = get_openapi_seed()["paths"]["/architecture"]["get"]
    parameters = {parameter["name"]: parameter for parameter in operation["parameters"]}

    assert list(parameters) == ["api_table", "symbol", "index_name", "key"]
    assert parameters["api_table"]["schema"]["type"] == "boolean"

    row = get_rest_api_selection(symbol="GET /architecture")
    assert row["inputs"] == "query:api_table, query:symbol, query:index_name, query:key"
    assert row["required_inputs"] == "none"
    assert row["returns"] == "200 ParaDev architecture graph or architecture API table selection."
    assert row["raises"] == "400 Invalid architecture API table selector."
