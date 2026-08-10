from __future__ import annotations

from heavenbase.utils import load_txt, loads_json
from typer.testing import CliRunner

from paradev.cli import build_app
from paradev.surfaces.cli import get_cli_api_table, get_cli_contract


def test_architecture_api_cli_outputs_one_symbol_json() -> None:
    result = CliRunner().invoke(build_app(), ["architecture", "--api-table", "--symbol", "get_architecture_api_selection", "--json"])

    assert result.exit_code == 0, result.output
    payload = loads_json(result.output)
    assert payload["symbol"] == "get_architecture_api_selection"
    assert payload["kind"] == "function"


def test_architecture_api_cli_outputs_one_index_bucket_json() -> None:
    result = CliRunner().invoke(build_app(), ["architecture", "--api-table", "--index", "surface_index", "--key", "cli", "--json"])

    assert result.exit_code == 0, result.output
    payload = loads_json(result.output)
    assert "paradev architecture --api-table" in payload
    assert "paradev architecture --api-table-markdown" in payload


def test_architecture_api_cli_requires_api_table_for_table_selectors() -> None:
    result = CliRunner().invoke(build_app(), ["architecture", "--symbol", "get_architecture_api_selection", "--json"])

    assert result.exit_code != 0
    assert "--symbol and --index/--key require --api-table" in result.output


def test_cli_contract_advertises_architecture_api_selectors() -> None:
    contract = get_cli_contract()
    adapters = contract["adapters"]
    filters = contract["filters"]
    projections = contract["projections"]

    assert adapters["architecture --api-table"] == "get_architecture_api_selection"
    assert adapters["architecture --api-table --symbol"] == "get_architecture_api_selection"
    assert adapters["architecture --api-table --index --key"] == "get_architecture_api_selection"
    assert filters["architecture --api-table"] == ["symbol", "index_name", "key"]
    assert projections["architecture --api-table"] == ["symbol", "index", "key"]

    rows = {row["command_key"]: row for row in get_cli_api_table()["rows"]}
    assert rows["architecture --api-table"]["filters"] == ["symbol", "index_name", "key"]
    assert rows["architecture --api-table --symbol"]["filters"] == ["symbol", "index_name", "key"]
    assert rows["architecture --api-table --index --key"]["filters"] == ["symbol", "index_name", "key"]
    assert rows["architecture --api-table --symbol"]["projections"] == ["symbol"]
    assert rows["architecture --api-table --index --key"]["projections"] == ["index", "key"]


def test_architecture_interface_docs_describe_architecture_api_selectors() -> None:
    content = load_txt("docs/architecture/interfaces.md", encoding="utf-8")

    assert "get_architecture_api_selection(symbol=..., index_name=..., key=...)" in content
    assert "paradev architecture --api-table --symbol" in content
    assert "paradev architecture --api-table --index ... --key ..." in content
