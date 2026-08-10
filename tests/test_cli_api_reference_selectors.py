from __future__ import annotations

from heavenbase.utils import loads_json
from typer.testing import CliRunner

from paradev.cli import build_app
from paradev.surfaces.api_catalog import get_api_catalog_table
from paradev.surfaces.cli import get_cli_contract


def test_api_reference_cli_outputs_one_symbol_json() -> None:
    result = CliRunner().invoke(build_app(), ["sdk-api", "--symbol", "Project", "--json"])

    assert result.exit_code == 0, result.output
    payload = loads_json(result.output)
    assert payload["symbol"] == "Project"
    assert payload["feature"] == "projects"


def test_api_reference_cli_outputs_one_index_bucket_json() -> None:
    result = CliRunner().invoke(build_app(), ["sdk-api", "--index", "feature_index", "--key", "projects", "--json"])

    assert result.exit_code == 0, result.output
    payload = loads_json(result.output)
    assert "Project" in payload
    assert "open_project" in payload


def test_cli_contract_advertises_standard_api_reference_selectors() -> None:
    contract = get_cli_contract()
    adapters = contract["adapters"]
    filters = contract["filters"]
    projections = contract["projections"]
    catalog = get_api_catalog_table()["rows"]

    for row in catalog:
        command = row["cli_command"]
        if "cli" not in row["surfaces"] or command in {"api-catalog", "frontend-api"} or not command.endswith("-api"):
            continue

        selector_helper = row["selector_helper"]
        assert adapters[command] == selector_helper
        assert adapters[f"{command} --symbol"] == selector_helper
        assert adapters[f"{command} --index --key"] == selector_helper
        assert filters[command] == ["symbol", "index_name", "key"]
        assert projections[command] == ["symbol", "index", "key", "markdown"]


def test_cli_contract_advertises_project_inspection_selectors() -> None:
    contract = get_cli_contract()
    adapters = contract["adapters"]
    filters = contract["filters"]
    projections = contract["projections"]

    assert adapters["inspections --kind"] == "get_project_inspection_selection"
    assert adapters["inspections --index --key"] == "get_project_inspection_selection"
    assert filters["inspections"] == ["kind", "index_name", "key"]
    assert projections["inspections"] == ["kind", "index", "key", "markdown"]
