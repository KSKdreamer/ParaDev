from __future__ import annotations

import json
import os
from importlib import import_module
from pathlib import Path

import pytest
from heavenbase.utils import copy_dir
from typer.testing import CliRunner

from paradev.cli import build_app
from paradev.config import CM_PARADEV
from paradev.hb import catalog_write
from paradev.pdx import PDXBlock
from paradev.sdk import Project, format_pdx_file, parse_pdx_file

PROJECT_ROOT = Path("demos/assets/projects/minimal").resolve()


def assert_cli_table_output(command: str, module_name: str, helper_name: str) -> dict[str, object]:
    result = CliRunner().invoke(build_app(), [command, "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload == getattr(import_module(module_name), helper_name)()
    return payload


def assert_cli_markdown_output(command: str, module_name: str, helper_name: str) -> str:
    result = CliRunner().invoke(build_app(), [command, "--markdown"])

    assert result.exit_code == 0, result.output
    assert result.output == getattr(import_module(module_name), helper_name)()
    return result.output


def test_explicit_json_output_does_not_read_global_config(monkeypatch) -> None:
    cli_module = import_module("paradev.cli")

    def fail_config_read(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise AssertionError("explicit JSON output read global config")

    monkeypatch.setattr(cli_module.CM_PARADEV, "get", fail_config_read)

    result = CliRunner().invoke(build_app(), ["architecture", "--surface-contracts", "--json"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["schema"] == "paradev.surface-contract-summary.v1"


def test_dashboard_command_forwards_launcher_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: dict[str, object] = {}

    def fake_main(argv: list[str], *, prog: str) -> int:
        observed.update(argv=argv, prog=prog)
        return 0

    monkeypatch.setattr("paradev.gui.main", fake_main)

    result = CliRunner().invoke(build_app(), ["dashboard", "--install-app", "--yes"])

    assert result.exit_code == 0, result.output
    assert observed == {
        "argv": ["--install-app", "--yes"],
        "prog": "paradev dashboard",
    }


def test_dashboard_command_propagates_launcher_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("paradev.gui.main", lambda _argv, *, prog: 7)

    result = CliRunner().invoke(build_app(), ["dashboard", "--no-open"])

    assert result.exit_code == 7


def test_catalog_query_cli_defaults_to_bounded_unhydrated_page(monkeypatch) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    class FakeProject:
        def inspect(self, kind: str, **filters: object) -> dict[str, object]:
            calls.append((kind, filters))
            return {"schema": "fake.catalog-query", "rows": []}

    monkeypatch.setattr("paradev.cli.open_project", lambda _path: FakeProject())

    result = CliRunner().invoke(build_app(), ["hb", "catalog-query", "demo", "--json"])

    assert result.exit_code == 0, result.output
    assert calls == [
        (
            "catalog-query",
            {
                "database": None,
                "entity": None,
                "target_id": None,
                "name": None,
                "tag": None,
                "limit": 100,
                "offset": 0,
                "include_data": False,
            },
        )
    ]


def test_catalog_query_cli_rejects_oversized_and_bulk_hydrated_pages() -> None:
    runner = CliRunner()
    oversized = runner.invoke(
        build_app(),
        ["hb", "catalog-query", "demo", "--limit", "201", "--json"],
        terminal_width=200,
    )
    hydrated = runner.invoke(
        build_app(),
        ["hb", "catalog-query", "demo", "--data", "--json"],
        terminal_width=200,
    )

    assert oversized.exit_code != 0
    assert "200" in oversized.output
    assert hydrated.exit_code != 0
    assert "hydrated requests" in hydrated.output
    assert "limit 1" in hydrated.output


def test_build_cli_writes_progress_jsonl_for_desktop_bridge(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "progress_cli", project_id="progress_cli", title="Progress CLI")
    progress_path = tmp_path / "progress.jsonl"

    result = CliRunner().invoke(
        build_app(),
        [
            "build",
            str(project.root),
            "--emit-manifests",
            "--progress-jsonl",
            str(progress_path),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    events = [json.loads(line) for line in progress_path.read_text(encoding="utf-8").splitlines()]
    assert events[0]["schema"] == "paradev.build.progress.v1"
    assert events[0]["phase"] == "load_project"
    phases = [event["phase"] for event in events]
    assert "discover_modules" in phases
    assert "discover_collections" in phases
    assert "basic_copy" in phases
    assert events[-1]["phase"] == "complete"
    assert events[-1]["percent"] == 100


def test_build_cli_accepts_bare_module_id_with_family_and_hides_tracebacks(
    tmp_path: Path,
) -> None:
    project = Project.create(
        tmp_path / "target_cli",
        project_id="target_cli",
        title="Target CLI",
    )
    module = project.discover_modules().modules[0]
    family, object_id = module.module_id.split("/", 1)
    runner = CliRunner()

    accepted = runner.invoke(
        build_app(),
        [
            "build",
            str(project.root),
            "--family",
            family,
            "--module",
            object_id,
            "--json",
        ],
    )
    rejected = runner.invoke(
        build_app(),
        [
            "build",
            str(project.root),
            "--family",
            "focus",
            "--module",
            module.module_id,
            "--json",
        ],
        terminal_width=200,
    )

    assert accepted.exit_code == 0, accepted.output
    assert json.loads(accepted.output)["modules"][0]["module_id"] == module.module_id
    assert rejected.exit_code != 0
    assert "Invalid value" in rejected.output
    assert "Traceback" not in rejected.output


def test_diagnostics_cli_honors_strict_metadata(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    metadata_path = project_root / "src/modules/focus/GER_sample/meta.yaml"
    metadata_path.write_text(metadata_path.read_text(encoding="utf-8") + "\nlegacy_hint: yes\n", encoding="utf-8")

    result = CliRunner().invoke(build_app(), ["diagnostics", str(project_root), "--strict-metadata", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.build.diagnostics.v1"
    assert payload["diagnostics"][0]["code"] == "metadata.unknown_key"
    assert payload["diagnostics"][0]["severity"] == "error"


def test_architecture_cli_outputs_surface_contract_summary_json() -> None:
    result = CliRunner().invoke(build_app(), ["architecture", "--surface-contracts", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.surface-contract-summary.v1"
    assert payload["status_index"]["implemented"] == ["bundle", "lsp", "openapi"]
    assert payload["status_index"]["scaffold"] == ["cli", "mcp", "vscode"]


def test_architecture_cli_outputs_one_surface_contract_json() -> None:
    result = CliRunner().invoke(build_app(), ["architecture", "--surface-contract", "cli", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["identifier"] == "cli"
    assert payload["adapters"]["architecture --surface-contract"] == "get_surface_contract_selection"
    assert payload["adapters"]["architecture --surface-contracts"] == "get_surface_contract_selection"
    assert payload["projections"]["architecture"] == [
        "api-table",
        "api-table-markdown",
        "surface-contract",
        "surface-contracts",
        "surface-contracts-markdown",
    ]


def test_architecture_cli_outputs_surface_contract_reference_markdown() -> None:
    result = CliRunner().invoke(build_app(), ["architecture", "--surface-contracts-markdown"])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("# Surface Contract Reference\n")
    assert "Generated from `paradev.surfaces.get_surface_contract_summary()`." in result.output
    assert "| `implemented` | 3 | `bundle`, `lsp`, `openapi` |" in result.output
    assert "| `openapi` | `implemented` | `openapi-3.1.0` | yes |" in result.output


def test_architecture_cli_outputs_api_table_json() -> None:
    result = CliRunner().invoke(build_app(), ["architecture", "--api-table", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.sdk.architecture-api-table.v1"
    assert payload["row_count"] == len(payload["rows"])
    assert payload["surface_index"]["cli"] == [
        "paradev architecture",
        "paradev architecture --api-table",
        "paradev architecture --api-table-markdown",
    ]
    assert payload["surface_index"]["rest"] == ["GET /architecture"]


def test_architecture_cli_outputs_api_table_markdown() -> None:
    result = CliRunner().invoke(build_app(), ["architecture", "--api-table-markdown"])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("# Architecture API Reference\n")
    assert "Generated from `paradev.sdk.get_architecture_api_table()`." in result.output
    assert "| `rest` | 1 | `GET /architecture` |" in result.output
    assert "| `get_architecture_api_table` | `function` | `sdk` | `sdk` | `none` | `ArchitectureApiTable` |" in result.output


def test_architecture_cli_rejects_api_table_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["architecture", "--api-table-markdown", "--json"])

    assert result.exit_code != 0
    assert "--api-table-markdown cannot be combined" in result.output


def test_architecture_cli_rejects_surface_contract_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["architecture", "--surface-contracts-markdown", "--json"])

    assert result.exit_code != 0
    assert "--surface-contracts-markdown cannot be combined" in result.output


def test_api_catalog_cli_outputs_table_json() -> None:
    result = CliRunner().invoke(build_app(), ["api-catalog", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.api-catalog.v1"
    assert payload["row_count"] == len(payload["rows"]) == 29
    assert payload["layer_index"]["sdk"] == [
        "sdk-api",
        "project-api",
        "templates-api",
        "copy-roots-api",
        "frontend-api",
        "sdk-cli-reference",
        "project-inspection-reference",
        "architecture-api",
        "pdx-api",
        "lsp-api",
    ]
    assert payload["layer_index"]["package"] == ["package-api"]
    assert payload["layer_index"]["config"] == ["config-api"]
    assert payload["layer_index"]["gui"] == ["gui-api"]
    assert payload["layer_index"]["desktop"] == ["desktop-api"]
    assert payload["layer_index"]["games"] == ["games-api"]
    assert payload["layer_index"]["project"] == ["project-facade-api"]
    assert payload["layer_index"]["localization"] == ["localization-api"]
    assert payload["layer_index"]["surface"] == ["api-catalog", "surfaces-api", "surface-contract-reference"]
    assert payload["layer_index"]["pdx"] == ["pdx-core-api"]
    assert payload["layer_index"]["lsp"] == ["lsp-server-api"]
    assert payload["layer_index"]["rest"] == ["rest-api", "rest-facade-api"]
    assert payload["kind_index"]["facade-table"] == [
        "sdk-api",
        "package-api",
        "config-api",
        "gui-api",
        "desktop-api",
        "games-api",
        "surfaces-api",
        "project-facade-api",
        "localization-api",
        "build-api",
        "pdx-core-api",
        "lsp-server-api",
        "hb-api",
        "rest-facade-api",
    ]
    assert payload["kind_index"]["api-table"] == ["architecture-api", "pdx-api", "lsp-api", "catalog-api"]
    assert payload["kind_index"]["module-table"] == ["templates-api", "copy-roots-api"]
    assert payload["owner_module_index"]["paradev.surfaces"] == ["api-catalog", "surfaces-api", "surface-contract-reference"]
    assert payload["owner_module_index"]["paradev.sdk"] == [
        "sdk-api",
        "project-api",
        "frontend-api",
        "sdk-cli-reference",
        "project-inspection-reference",
        "architecture-api",
        "pdx-api",
        "lsp-api",
    ]
    assert payload["owner_module_index"]["paradev.sdk.templates"] == ["templates-api"]
    assert payload["owner_module_index"]["paradev.sdk.copy_roots"] == ["copy-roots-api"]
    assert payload["owner_module_index"]["paradev.pdx"] == ["pdx-core-api"]
    assert payload["owner_module_index"]["paradev.lsp"] == ["lsp-server-api"]
    assert payload["owner_module_index"]["paradev.hb"] == ["catalog-api", "hb-api"]
    assert payload["owner_module_index"]["paradev.project"] == ["project-facade-api"]
    assert payload["owner_module_index"]["paradev.localization"] == ["localization-api"]
    assert payload["owner_module_index"]["paradev.config"] == ["config-api"]
    assert payload["owner_module_index"]["paradev.gui"] == ["gui-api"]
    assert payload["owner_module_index"]["paradev.desktop"] == ["desktop-api"]
    assert payload["owner_module_index"]["paradev.games"] == ["games-api"]
    assert payload["owner_module_index"]["paradev.api"] == ["rest-facade-api"]
    assert payload["surface_index"]["sdk"] == [
        "api-catalog",
        "sdk-api",
        "package-api",
        "config-api",
        "gui-api",
        "desktop-api",
        "games-api",
        "surfaces-api",
        "project-api",
        "templates-api",
        "copy-roots-api",
        "project-facade-api",
        "localization-api",
        "build-api",
        "frontend-api",
        "sdk-cli-reference",
        "project-inspection-reference",
        "architecture-api",
        "pdx-api",
        "pdx-core-api",
        "lsp-api",
        "lsp-server-api",
        "catalog-api",
        "hb-api",
        "rest-facade-api",
    ]
    assert payload["surface_index"]["docs"][-3:] == ["mcp-api", "cli-api", "surface-contract-reference"]
    assert payload["surface_index"]["frontend"] == [
        "project-api",
        "templates-api",
        "frontend-api",
        "project-inspection-reference",
        "rest-api",
        "mcp-api",
        "cli-api",
    ]
    assert payload["surface_index"]["typescript"] == ["frontend-api"]
    assert payload["surface_index"]["desktop"] == ["gui-api", "desktop-api"]
    assert payload["surface_index"]["rest"][0] == "api-catalog"
    assert payload["surface_index"]["mcp"] == [
        "api-catalog",
        "surfaces-api",
        "frontend-api",
        "project-inspection-reference",
        "architecture-api",
        "pdx-api",
        "lsp-api",
        "catalog-api",
        "mcp-api",
        "cli-api",
        "surface-contract-reference",
    ]
    selector_helper_index = payload["selector_helper_index"]
    assert selector_helper_index["get_api_catalog_selection"] == ["api-catalog"]
    assert selector_helper_index["get_frontend_api_selection"] == ["frontend-api", "sdk-cli-reference"]
    assert selector_helper_index["get_architecture_api_selection"] == ["architecture-api"]
    assert selector_helper_index["get_project_inspection_selection"] == ["project-inspection-reference"]
    assert selector_helper_index["get_mcp_api_selection"] == ["mcp-api"]
    assert selector_helper_index["get_cli_api_selection"] == ["cli-api"]
    assert selector_helper_index["get_surface_contract_selection"] == ["surface-contract-reference"]
    rows = {row["id"]: row for row in payload["rows"]}
    assert rows["api-catalog"]["row_count"] == 29
    assert rows["api-catalog"]["selector_helper"] == "get_api_catalog_selection"
    assert rows["api-catalog"]["index_names"] == [
        "cli_command_index",
        "doc_page_index",
        "feature_index",
        "group_index",
        "kind_index",
        "layer_index",
        "owner_module_index",
        "selector_helper_index",
        "surface_index",
    ]
    assert rows["package-api"]["schema"] == "paradev.package.api-table.v1"
    assert rows["package-api"]["row_count"] == 15
    assert rows["config-api"]["schema"] == "paradev.config.api-table.v1"
    assert rows["config-api"]["row_count"] == 15
    assert rows["config-api"]["index_names"] == ["feature_index", "kind_index", "module_index"]
    assert rows["gui-api"]["schema"] == "paradev.gui.api-table.v1"
    assert rows["gui-api"]["row_count"] == 8
    assert rows["gui-api"]["index_names"] == ["feature_index", "kind_index", "module_index"]
    assert rows["desktop-api"]["schema"] == "paradev.desktop.api-table.v1"
    assert rows["desktop-api"]["row_count"] == 57
    assert rows["desktop-api"]["index_names"] == ["feature_index", "kind_index", "module_index"]
    assert rows["games-api"]["schema"] == "paradev.games.api-table.v1"
    assert rows["games-api"]["row_count"] == 8
    assert rows["games-api"]["index_names"] == ["feature_index", "kind_index", "module_index"]
    assert rows["surfaces-api"]["schema"] == "paradev.surfaces.api-table.v1"
    assert rows["surfaces-api"]["row_count"] == 56
    assert rows["surfaces-api"]["selector_helper"] == "get_surfaces_api_selection"
    assert rows["templates-api"]["schema"] == "paradev.sdk.templates.api-table.v1"
    assert rows["templates-api"]["row_count"] == 18
    assert rows["templates-api"]["index_names"] == ["feature_index", "kind_index", "module_index"]
    assert rows["copy-roots-api"]["schema"] == "paradev.sdk.copy_roots.api-table.v1"
    assert rows["copy-roots-api"]["row_count"] == 12
    assert rows["copy-roots-api"]["index_names"] == ["feature_index", "kind_index", "module_index"]
    assert rows["project-facade-api"]["schema"] == "paradev.project.facade-api-table.v1"
    assert rows["project-facade-api"]["row_count"] == 8
    assert rows["project-facade-api"]["index_names"] == ["feature_index", "kind_index", "module_index"]
    assert rows["localization-api"]["schema"] == "paradev.localization.api-table.v1"
    assert rows["localization-api"]["row_count"] == 8
    assert rows["localization-api"]["index_names"] == ["feature_index", "kind_index", "module_index"]
    assert rows["architecture-api"]["row_count"] == 17
    assert rows["architecture-api"]["selector_helper"] == "get_architecture_api_selection"
    assert rows["pdx-core-api"]["schema"] == "paradev.pdx.core-api-table.v1"
    assert rows["pdx-core-api"]["row_count"] == 23
    assert rows["lsp-server-api"]["schema"] == "paradev.lsp.server-api-table.v1"
    assert rows["lsp-server-api"]["row_count"] == 11
    assert rows["lsp-server-api"]["index_names"] == ["feature_index", "kind_index", "module_index"]
    assert rows["lsp-api"]["row_count"] == 42
    assert rows["lsp-api"]["surfaces"] == ["sdk", "cli", "rest", "mcp", "lsp", "docs"]
    assert rows["catalog-api"]["row_count"] == 37
    assert rows["hb-api"]["schema"] == "paradev.hb.api-table.v1"
    assert rows["hb-api"]["row_count"] == 27
    assert rows["hb-api"]["index_names"] == ["feature_index", "kind_index", "module_index"]
    assert rows["rest-api"]["schema"] == "paradev.rest.api-table.v1"
    assert rows["rest-api"]["row_count"] == 84
    assert rows["rest-facade-api"]["schema"] == "paradev.rest.facade-api-table.v1"
    assert rows["rest-facade-api"]["row_count"] == 13
    assert rows["rest-facade-api"]["index_names"] == ["feature_index", "kind_index", "module_index"]
    assert rows["mcp-api"]["schema"] == "paradev.mcp.api-table.v1"
    assert rows["mcp-api"]["row_count"] == 51
    assert rows["mcp-api"]["selector_helper"] == "get_mcp_api_selection"
    assert rows["cli-api"]["row_count"] == 208
    assert rows["cli-api"]["selector_helper"] == "get_cli_api_selection"


def test_api_catalog_cli_outputs_reference_json() -> None:
    result = CliRunner().invoke(build_app(), ["api-catalog", "--reference", "frontend-api", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["id"] == "frontend-api"
    assert payload["schema"] == "paradev.sdk.frontend-api.v1"
    assert payload["surfaces"] == ["sdk", "cli", "rest", "mcp", "lsp", "frontend", "typescript", "docs"]
    assert payload["table_helper"] == "get_frontend_api_contract"
    assert payload["selector_helper"] == "get_frontend_api_selection"


def test_api_catalog_cli_outputs_index_ids_json() -> None:
    result = CliRunner().invoke(build_app(), ["api-catalog", "--index", "surface", "--key", "rest", "--json"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == [
        "api-catalog",
        "surfaces-api",
        "frontend-api",
        "project-inspection-reference",
        "architecture-api",
        "pdx-api",
        "lsp-api",
        "catalog-api",
        "rest-api",
        "rest-facade-api",
        "cli-api",
        "surface-contract-reference",
    ]


def test_api_catalog_cli_outputs_reference_markdown() -> None:
    result = CliRunner().invoke(build_app(), ["api-catalog", "--markdown"])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("# API Catalog Reference\n")
    assert "Generated from `paradev.surfaces.get_api_catalog_table()`." in result.output
    assert "| `frontend-api` | 2 | `frontend-api`, `sdk-cli-reference` |" in result.output
    assert "| `package` | 1 | `package-api` |" in result.output
    assert "| `config` | 1 | `config-api` |" in result.output
    assert "| `gui` | 1 | `gui-api` |" in result.output
    assert "| `desktop` | 1 | `desktop-api` |" in result.output
    assert "| `games` | 1 | `games-api` |" in result.output
    assert "| `project` | 1 | `project-facade-api` |" in result.output
    assert "| `authoring` | 1 | `templates-api` |" in result.output
    assert "| `copy-roots` | 1 | `copy-roots-api` |" in result.output
    assert "| `localization` | 1 | `localization-api` |" in result.output
    assert "| `module-table` | 2 | `templates-api`, `copy-roots-api` |" in result.output
    assert (
        "| `facade-table` | 14 | `sdk-api`, `package-api`, `config-api`, `gui-api`, `desktop-api`, `games-api`, `surfaces-api`, `project-facade-api`, `localization-api`, `build-api`, `pdx-core-api`, "
        "`lsp-server-api`, `hb-api`, `rest-facade-api` |"
    ) in result.output
    assert "| `paradev.surfaces` | 3 | `api-catalog`, `surfaces-api`, `surface-contract-reference` |" in result.output
    assert "| `paradev.pdx` | 1 | `pdx-core-api` |" in result.output
    assert "| `paradev.lsp` | 1 | `lsp-server-api` |" in result.output
    assert "| `paradev.hb` | 2 | `catalog-api`, `hb-api` |" in result.output
    assert "| `paradev.project` | 1 | `project-facade-api` |" in result.output
    assert "| `paradev.localization` | 1 | `localization-api` |" in result.output
    assert "| `paradev.config` | 1 | `config-api` |" in result.output
    assert "| `paradev.gui` | 1 | `gui-api` |" in result.output
    assert "| `paradev.desktop` | 1 | `desktop-api` |" in result.output
    assert "| `paradev.games` | 1 | `games-api` |" in result.output
    assert "| `paradev.sdk.templates` | 1 | `templates-api` |" in result.output
    assert "| `paradev.sdk.copy_roots` | 1 | `copy-roots-api` |" in result.output
    assert "| `paradev.api` | 1 | `rest-facade-api` |" in result.output
    assert "| `get_api_catalog_selection` | 1 | `api-catalog` |" in result.output
    assert "| `get_frontend_api_selection` | 2 | `frontend-api`, `sdk-cli-reference` |" in result.output
    assert "| `get_architecture_api_selection` | 1 | `architecture-api` |" in result.output
    assert "| `get_mcp_api_selection` | 1 | `mcp-api` |" in result.output
    assert "| `get_cli_api_selection` | 1 | `cli-api` |" in result.output
    assert "| `get_surface_contract_selection` | 1 | `surface-contract-reference` |" in result.output
    assert (
        "| `sdk` | 25 | `api-catalog`, `sdk-api`, `package-api`, `config-api`, `gui-api`, `desktop-api`, `games-api`, `surfaces-api`, `project-api`, `templates-api`, `copy-roots-api`, `project-facade-api`, `localization-api`, "
        "`build-api`, `frontend-api`, `sdk-cli-reference`, `project-inspection-reference`, `architecture-api`, `pdx-api`, "
        "`pdx-core-api`, `lsp-api`, `lsp-server-api`, `catalog-api`, `hb-api`, `rest-facade-api` |"
    ) in result.output
    assert (
        "| `mcp` | 11 | `api-catalog`, `surfaces-api`, `frontend-api`, `project-inspection-reference`, `architecture-api`, `pdx-api`, `lsp-api`,"
        in result.output
    )
    assert "| `desktop` | 2 | `gui-api`, `desktop-api` |" in result.output
    assert (
        "| `package-api` | Package API Reference | `facade-table` | `package` | `facade` | `paradev.package.api-table.v1` | 15 | "
        "`get_package_api_table` | `get_package_api_selection` | `render_package_api_reference_markdown` | `package-api` | `package-api --markdown` |"
    ) in result.output
    assert (
        "| `config-api` | Config API Reference | `facade-table` | `config` | `config` | `paradev.config.api-table.v1` | 15 | "
        "`get_config_api_table` | `get_config_api_selection` | `render_config_api_reference_markdown` | `config-api` | `config-api --markdown` |"
    ) in result.output
    assert (
        "| `gui-api` | GUI API Reference | `facade-table` | `gui` | `launcher` | `paradev.gui.api-table.v1` | 8 | "
        "`get_gui_api_table` | `get_gui_api_selection` | `render_gui_api_reference_markdown` | `gui-api` | `gui-api --markdown` |"
    ) in result.output
    assert (
        "| `desktop-api` | Desktop API Reference | `facade-table` | `desktop` | `state` | `paradev.desktop.api-table.v1` | 57 | "
        "`get_desktop_api_table` | `get_desktop_api_selection` | `render_desktop_api_reference_markdown` | `desktop-api` | `desktop-api --markdown` |"
    ) in result.output
    assert (
        "| `games-api` | Games API Reference | `facade-table` | `games` | `profiles` | `paradev.games.api-table.v1` | 8 | "
        "`get_games_api_table` | `get_games_api_selection` | `render_games_api_reference_markdown` | `games-api` | `games-api --markdown` |"
    ) in result.output
    assert (
        "| `templates-api` | Authoring Templates API Reference | `module-table` | `sdk` | `authoring` | "
        "`paradev.sdk.templates.api-table.v1` | 18 | `get_templates_api_table` | "
        "`get_templates_api_selection` | `render_templates_api_reference_markdown` | `templates-api` | `templates-api --markdown` |"
    ) in result.output
    assert (
        "| `copy-roots-api` | Copy Roots API Reference | `module-table` | `sdk` | `copy-roots` | "
        "`paradev.sdk.copy_roots.api-table.v1` | 12 | `get_copy_roots_api_table` | "
        "`get_copy_roots_api_selection` | `render_copy_roots_api_reference_markdown` | `copy-roots-api` | `copy-roots-api --markdown` |"
    ) in result.output
    assert (
        "| `project-facade-api` | Project Facade API Reference | `facade-table` | `project` | `project-facade` | "
        "`paradev.project.facade-api-table.v1` | 8 | `get_project_facade_api_table` | "
        "`get_project_facade_api_selection` | `render_project_facade_api_reference_markdown` | `project-facade-api` | `project-facade-api --markdown` |"
    ) in result.output
    assert (
        "| `localization-api` | Localization API Reference | `facade-table` | `localization` | `localization` | "
        "`paradev.localization.api-table.v1` | 8 | `get_localization_api_table` | "
        "`get_localization_api_selection` | `render_localization_api_reference_markdown` | `localization-api` | `localization-api --markdown` |"
    ) in result.output
    assert (
        "| `surfaces-api` | Surfaces API Reference | `facade-table` | `surface` | `surfaces` | `paradev.surfaces.api-table.v1` | 56 | "
        "`get_surfaces_api_table` | `get_surfaces_api_selection` | `render_surfaces_api_reference_markdown` | `surfaces-api` | `surfaces-api --markdown` |"
    ) in result.output
    assert (
        "| `architecture-api` | Architecture API Reference | `api-table` | `sdk` | `architecture` | `paradev.sdk.architecture-api-table.v1` | 17 | "
        "`get_architecture_api_table` | `get_architecture_api_selection` | `render_architecture_api_reference_markdown` | `architecture --api-table` | `architecture --api-table-markdown` |"
    ) in result.output
    assert (
        "| `pdx-core-api` | PDX Core API Reference | `facade-table` | `pdx` | `pdx-core` | `paradev.pdx.core-api-table.v1` | 23 | "
        "`get_pdx_core_api_table` | `get_pdx_core_api_selection` | `render_pdx_core_api_reference_markdown` | `pdx-core-api` | `pdx-core-api --markdown` |"
    ) in result.output
    assert (
        "| `lsp-server-api` | LSP Server API Reference | `facade-table` | `lsp` | `lsp-server` | `paradev.lsp.server-api-table.v1` | 11 | "
        "`get_lsp_server_api_table` | `get_lsp_server_api_selection` | `render_lsp_server_api_reference_markdown` | `lsp-server-api` | `lsp-server-api --markdown` |"
    ) in result.output
    assert (
        "| `rest-facade-api` | REST Facade API Reference | `facade-table` | `rest` | `rest-facade` | "
        "`paradev.rest.facade-api-table.v1` | 13 | `get_rest_facade_api_table` | "
        "`get_rest_facade_api_selection` | `render_rest_facade_api_reference_markdown` | `rest-facade-api` | `rest-facade-api --markdown` |"
    ) in result.output
    assert (
        "| `hb-api` | HeavenBase Facade API Reference | `facade-table` | `hb` | `facade` | `paradev.hb.api-table.v1` | 27 | "
        "`get_hb_api_table` | `get_hb_api_selection` | `render_hb_api_reference_markdown` | `hb-api` | `hb-api --markdown` |"
    ) in result.output
    assert (
        "| `catalog-api` | Catalog API Reference | `api-table` | `hb` | `catalog` | `paradev.hb.catalog-api-table.v1` | 37 | "
        "`get_catalog_api_table` | `get_catalog_api_selection` | `render_catalog_api_reference_markdown` | `catalog-api` | `catalog-api --markdown` |"
    ) in result.output
    assert (
        "| `mcp-api` | MCP API Reference | `tool-table` | `mcp` | `mcp` | `paradev.mcp.api-table.v1` | 51 | "
        "`get_mcp_api_table` | `get_mcp_api_selection` | `render_mcp_api_reference_markdown` | `mcp-api` | `mcp-api --markdown` |"
    ) in result.output
    assert (
        "| `frontend-api` | Frontend API Reference | `operation-contract` | `sdk` | `frontend` | `paradev.sdk.frontend-api.v1` | 98 | "
        "`get_frontend_api_contract` | `get_frontend_api_selection` | `render_frontend_api_reference_markdown` | `frontend-api` | `frontend-api --markdown` |"
    ) in result.output


def test_api_catalog_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["api-catalog", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_api_catalog_cli_rejects_markdown_selector_combo() -> None:
    result = CliRunner().invoke(build_app(), ["api-catalog", "--markdown", "--reference", "frontend-api"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with selectors" in result.output


def test_api_catalog_cli_rejects_ambiguous_selectors() -> None:
    result = CliRunner().invoke(
        build_app(),
        ["api-catalog", "--reference", "frontend-api", "--index", "surface", "--key", "rest"],
    )

    assert result.exit_code != 0
    assert "Pass only one api-catalog selector" in result.output


def test_api_catalog_cli_rejects_partial_index_selector() -> None:
    result = CliRunner().invoke(build_app(), ["api-catalog", "--index", "surface"])

    assert result.exit_code != 0
    assert "--index requires --key" in result.output


def test_api_catalog_cli_rejects_unknown_reference() -> None:
    result = CliRunner().invoke(build_app(), ["api-catalog", "--reference", "missing-api"])

    assert result.exit_code != 0
    assert "unknown ParaDev API catalog reference 'missing-api'" in result.output


def test_package_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("package-api", "paradev", "get_package_api_table")

    assert payload["schema"] == "paradev.package.api-table.v1"
    assert payload["module_index"]["package_api"] == [
        "PACKAGE_API_TABLE_SCHEMA",
        "PackageApiRow",
        "PackageApiTable",
        "get_package_api_selection",
        "get_package_api_table",
        "render_package_api_reference_markdown",
    ]
    assert payload["feature_index"]["projects"] == ["ParaDevProject", "Project", "open_project"]
    assert payload["kind_index"]["ConfigManager"] == ["CM_PARADEV"]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["PACKAGE_API_TABLE_SCHEMA"]["value"] == "paradev.package.api-table.v1"
    assert rows["Project"]["registry_seam"] == "project family/template registry"


def test_package_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("package-api", "paradev", "render_package_api_reference_markdown")

    assert (
        "| `package-api` | 6 | `PACKAGE_API_TABLE_SCHEMA`, `PackageApiRow`, `PackageApiTable`, "
        "`get_package_api_selection`, `get_package_api_table`, `render_package_api_reference_markdown` |" in output
    )
    assert "| `projects` | 3 | `ParaDevProject`, `Project`, `open_project` |" in output
    assert (
        "| `Project` | `dataclass` | `package` | `sdk.project` | `projects` | `paradev.Project` | " "`Project class` |  | `project family/template registry` |"
    ) in output


def test_package_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["package-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_config_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("config-api", "paradev.config", "get_config_api_table")
    config_facade_symbols = [
        "DEFAULT_CONFIG",
        "BOOTSTRAP_CONFIG",
        "CM_PARADEV",
        "config_get",
        "config_list",
        "config_set",
        "config_unset",
        "config_scopes",
        "config_history",
    ]
    config_helper_symbols = [
        "config_get",
        "config_list",
        "config_set",
        "config_unset",
        "config_scopes",
        "config_history",
    ]

    assert payload["schema"] == "paradev.config.api-table.v1"
    assert payload["module_index"]["config"] == config_facade_symbols
    assert payload["module_index"]["config_api"] == [
        "CONFIG_API_TABLE_SCHEMA",
        "ConfigApiRow",
        "ConfigApiTable",
        "get_config_api_selection",
        "get_config_api_table",
        "render_config_api_reference_markdown",
    ]
    assert payload["feature_index"]["defaults"] == ["DEFAULT_CONFIG", "BOOTSTRAP_CONFIG"]
    assert payload["feature_index"]["config-manager"] == ["CM_PARADEV"]
    assert payload["feature_index"]["config"] == config_helper_symbols
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["CONFIG_API_TABLE_SCHEMA"]["value"] == "paradev.config.api-table.v1"
    assert rows["DEFAULT_CONFIG"]["returns"] == "dict[1]"
    assert rows["BOOTSTRAP_CONFIG"]["returns"] == "dict[5]"
    assert rows["CM_PARADEV"]["registry_seam"] == "HeavenBase ConfigManager"
    assert rows["config_get"]["returns"] == "object"
    assert rows["config_list"]["returns"] == "list[dict[str, object]]"
    assert rows["config_set"]["returns"] == "bool"
    assert rows["config_get"]["registry_seam"] == "HeavenBase ConfigManager"
    assert rows["get_config_api_table"]["returns"] == "ConfigApiTable"


def test_config_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("config-api", "paradev.config", "render_config_api_reference_markdown")

    assert (
        "| `config` | 9 | `DEFAULT_CONFIG`, `BOOTSTRAP_CONFIG`, `CM_PARADEV`, `config_get`, `config_list`, "
        "`config_set`, `config_unset`, `config_scopes`, `config_history` |"
    ) in output
    assert ("| `config` | 6 | `config_get`, `config_list`, `config_set`, `config_unset`, `config_scopes`, " "`config_history` |") in output
    assert (
        "| `config-api` | 6 | `CONFIG_API_TABLE_SCHEMA`, `ConfigApiRow`, `ConfigApiTable`, "
        "`get_config_api_selection`, `get_config_api_table`, `render_config_api_reference_markdown` |"
    ) in output
    assert (
        "| `CM_PARADEV` | `ConfigManager` | `config` | `config` | `config-manager` | "
        "`paradev.config.CM_PARADEV` | `ConfigManager` |  | `HeavenBase ConfigManager` |"
    ) in output
    assert (
        "| `config_get` | `function` | `config` | `config` | `config` | `paradev.config.config_get` | " "`object` |  | `HeavenBase ConfigManager` |"
    ) in output


def test_config_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["config-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_gui_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("gui-api", "paradev.gui", "get_gui_api_table")

    assert payload["schema"] == "paradev.gui.api-table.v1"
    assert payload["module_index"]["gui"] == ["build_parser", "main"]
    assert payload["module_index"]["gui_api"] == [
        "GUI_API_TABLE_SCHEMA",
        "GuiApiRow",
        "GuiApiTable",
        "get_gui_api_selection",
        "get_gui_api_table",
        "render_gui_api_reference_markdown",
    ]
    assert payload["feature_index"]["launcher"] == ["build_parser", "main"]
    assert payload["feature_index"]["gui-api"] == [
        "GUI_API_TABLE_SCHEMA",
        "GuiApiRow",
        "GuiApiTable",
        "get_gui_api_selection",
        "get_gui_api_table",
        "render_gui_api_reference_markdown",
    ]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["GUI_API_TABLE_SCHEMA"]["value"] == "paradev.gui.api-table.v1"
    assert rows["build_parser"]["returns"] == "argparse.ArgumentParser"
    assert rows["main"]["registry_seam"] == "Python GUI script entry point"
    assert rows["main"]["surface"] == "desktop"
    assert rows["get_gui_api_table"]["returns"] == "GuiApiTable"


def test_gui_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("gui-api", "paradev.gui", "render_gui_api_reference_markdown")

    assert "| `gui` | 2 | `build_parser`, `main` |" in output
    assert (
        "| `gui-api` | 6 | `GUI_API_TABLE_SCHEMA`, `GuiApiRow`, `GuiApiTable`, "
        "`get_gui_api_selection`, `get_gui_api_table`, `render_gui_api_reference_markdown` |"
    ) in output
    assert ("| `main` | `function` | `gui` | `gui` | `launcher` | `paradev.gui.main` | `int` |  | " "`Python GUI script entry point` | `desktop` |") in output


def test_gui_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["gui-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_desktop_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("desktop-api", "paradev.desktop", "get_desktop_api_table")

    assert payload["schema"] == "paradev.desktop.api-table.v1"
    assert payload["module_index"]["sdk.project"] == ["DESKTOP_STATE_SCHEMA", "desktop_state"]
    assert payload["module_index"]["desktop.builds"] == [
        "BUILD_RUN_SCHEMA",
        "BUILD_RUNS_SCHEMA",
        "DesktopBuildRegistry",
        "desktop_start_build",
        "desktop_build_runs",
        "desktop_build_status",
        "desktop_interrupt_build",
    ]
    assert payload["module_index"]["desktop.local"] == [
        "AI_CHAT_SCHEMA",
        "AI_CHAT_PROFILES_SCHEMA",
        "AI_CHAT_PROFILES_CONFIG_KEY",
        "AI_CHAT_PROFILES_CONFIG_SCHEMA",
        "BINARY_SOURCE_SCHEMA",
        "DESKTOP_CONFIG_KEYS",
        "DESKTOP_APP_CONFIG_KEY",
        "desktop_chat",
        "desktop_chat_profiles",
        "desktop_config_rows",
        "desktop_reset_chat_profile",
        "desktop_write_chat_profile",
        "desktop_test_llm_route",
        "render_desktop_typescript",
        "desktop_source_path",
        "desktop_read_text_source",
        "desktop_read_binary_source",
        "desktop_binary_source",
        "desktop_browser_cache_path",
        "read_project_browser_cache",
        "desktop_write_browser_cache",
        "desktop_thumbnail_cache_path",
        "desktop_read_thumbnail_cache",
        "desktop_write_thumbnail_cache",
        "desktop_read_app_config",
        "desktop_write_app_config",
        "desktop_read_config_value",
        "desktop_write_config_value",
        "desktop_mime_type",
        "desktop_dependency_status",
        "desktop_install_dependency",
    ]
    assert payload["module_index"]["desktop.shell"] == [
        "desktop_project_build_command",
        "desktop_hoi4_launch_command",
        "desktop_run_hoi4",
        "desktop_open_path_command",
        "desktop_open_path",
        "desktop_open_path_targets",
        "desktop_path_status",
    ]
    assert payload["module_index"]["desktop.api"] == [
        "DESKTOP_API_TABLE_SCHEMA",
        "DesktopApiRow",
        "DesktopApiTable",
        "get_desktop_api_selection",
        "get_desktop_api_table",
        "render_desktop_api_reference_markdown",
    ]
    assert payload["feature_index"]["state"] == ["DESKTOP_STATE_SCHEMA", "desktop_state"]
    assert payload["feature_index"]["ai-chat"] == [
        "AI_CHAT_SCHEMA",
        "AI_CHAT_PROFILES_SCHEMA",
        "AI_CHAT_PROFILES_CONFIG_KEY",
        "AI_CHAT_PROFILES_CONFIG_SCHEMA",
        "desktop_chat",
        "desktop_chat_profiles",
        "desktop_reset_chat_profile",
        "desktop_write_chat_profile",
        "desktop_test_llm_route",
    ]
    assert payload["feature_index"]["sources"] == [
        "BINARY_SOURCE_SCHEMA",
        "desktop_source_path",
        "desktop_read_text_source",
        "desktop_read_binary_source",
        "desktop_binary_source",
        "desktop_mime_type",
    ]
    assert payload["feature_index"]["cache"] == [
        "desktop_browser_cache_path",
        "read_project_browser_cache",
        "desktop_write_browser_cache",
        "desktop_thumbnail_cache_path",
        "desktop_read_thumbnail_cache",
        "desktop_write_thumbnail_cache",
    ]
    assert payload["feature_index"]["dependencies"] == ["desktop_dependency_status", "desktop_install_dependency"]
    assert payload["feature_index"]["config"] == [
        "DESKTOP_CONFIG_KEYS",
        "DESKTOP_APP_CONFIG_KEY",
        "desktop_config_rows",
        "render_desktop_typescript",
        "desktop_read_app_config",
        "desktop_write_app_config",
        "desktop_read_config_value",
        "desktop_write_config_value",
    ]
    assert payload["feature_index"]["build"] == [
        "BUILD_RUN_SCHEMA",
        "BUILD_RUNS_SCHEMA",
        "DesktopBuildRegistry",
        "desktop_start_build",
        "desktop_build_runs",
        "desktop_build_status",
        "desktop_interrupt_build",
        "desktop_project_build_command",
    ]
    assert payload["feature_index"]["game-launch"] == ["desktop_hoi4_launch_command", "desktop_run_hoi4"]
    assert payload["feature_index"]["open-path"] == ["desktop_open_path_command", "desktop_open_path", "desktop_open_path_targets", "desktop_path_status"]
    assert payload["feature_index"]["desktop-api"] == [
        "DESKTOP_API_TABLE_SCHEMA",
        "DesktopApiRow",
        "DesktopApiTable",
        "get_desktop_api_selection",
        "get_desktop_api_table",
        "render_desktop_api_reference_markdown",
    ]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["DESKTOP_STATE_SCHEMA"]["value"] == "paradev.desktop.state.v1"
    assert rows["BUILD_RUN_SCHEMA"]["value"] == "paradev.desktop.build-run.v1"
    assert rows["BUILD_RUNS_SCHEMA"]["value"] == "paradev.desktop.build-runs.v1"
    assert rows["DesktopBuildRegistry"]["kind"] == "class"
    assert rows["desktop_start_build"]["returns"] == "dict[str, object]"
    assert rows["desktop_start_build"]["registry_seam"] == "desktop build lifecycle and CLI command planner"
    assert rows["desktop_build_runs"]["registry_seam"] == "desktop build lifecycle and CLI command planner"
    assert rows["desktop_build_status"]["registry_seam"] == "desktop build lifecycle and CLI command planner"
    assert rows["desktop_interrupt_build"]["registry_seam"] == "desktop build lifecycle and CLI command planner"
    assert rows["AI_CHAT_SCHEMA"]["value"] == "paradev.desktop.ai-chat.v1"
    assert rows["AI_CHAT_PROFILES_SCHEMA"]["value"] == "paradev.desktop.ai-chat-profiles.v1"
    assert rows["AI_CHAT_PROFILES_CONFIG_SCHEMA"]["value"] == "paradev.sdk.ai-chat-profile-overrides.v1"
    assert rows["desktop_state"]["returns"] == "dict[str, object]"
    assert rows["desktop_state"]["registry_seam"] == "desktop state contract"
    assert rows["desktop_state"]["surface"] == "desktop"
    assert rows["desktop_chat"]["returns"] == "dict[str, object]"
    assert rows["desktop_chat"]["registry_seam"] == "HeavenBase desktop AI chat"
    assert rows["desktop_chat_profiles"]["returns"] == "dict[str, object]"
    assert rows["desktop_chat_profiles"]["registry_seam"] == "HeavenBase desktop AI chat"
    assert rows["desktop_reset_chat_profile"]["returns"] == "dict[str, object]"
    assert rows["desktop_reset_chat_profile"]["registry_seam"] == "HeavenBase desktop AI chat"
    assert rows["desktop_write_chat_profile"]["returns"] == "dict[str, object]"
    assert rows["desktop_write_chat_profile"]["registry_seam"] == "HeavenBase desktop AI chat"
    assert rows["desktop_test_llm_route"]["registry_seam"] == "HeavenBase desktop AI chat"
    assert rows["desktop_read_binary_source"]["registry_seam"] == "project-contained desktop source files"
    assert rows["desktop_write_thumbnail_cache"]["registry_seam"] == "project .paradev desktop cache"
    assert rows["DESKTOP_CONFIG_KEYS"]["registry_seam"] == "CM_PARADEV desktop GUI config"
    assert rows["render_desktop_typescript"]["returns"] == "str"
    assert rows["desktop_write_app_config"]["registry_seam"] == "CM_PARADEV desktop GUI config"
    assert rows["desktop_read_config_value"]["returns"] == "dict[str, object]"
    assert rows["desktop_write_config_value"]["registry_seam"] == "CM_PARADEV desktop GUI config"
    assert rows["desktop_dependency_status"]["registry_seam"] == "desktop dependency manager"
    assert rows["desktop_install_dependency"]["registry_seam"] == "desktop dependency manager"
    assert rows["desktop_project_build_command"]["registry_seam"] == "desktop build lifecycle and CLI command planner"
    assert rows["desktop_run_hoi4"]["registry_seam"] == "desktop HOI4 launcher command"
    assert rows["desktop_open_path"]["registry_seam"] == "desktop local path opener"
    assert rows["desktop_open_path_targets"]["returns"] == "dict[str, object]"
    assert rows["desktop_open_path_targets"]["registry_seam"] == "desktop local path opener"
    assert rows["desktop_path_status"]["returns"] == "dict[str, object]"
    assert rows["desktop_path_status"]["registry_seam"] == "desktop local path opener"
    assert rows["get_desktop_api_table"]["returns"] == "DesktopApiTable"


def test_desktop_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("desktop-api", "paradev.desktop", "render_desktop_api_reference_markdown")

    assert "| `sdk.project` | 2 | `DESKTOP_STATE_SCHEMA`, `desktop_state` |" in output
    assert "| `desktop.builds` | 7 | `BUILD_RUN_SCHEMA`, `BUILD_RUNS_SCHEMA`, `DesktopBuildRegistry`, `desktop_start_build`," in output
    assert "| `desktop.local` | 31 | `AI_CHAT_SCHEMA`, `AI_CHAT_PROFILES_SCHEMA`, `AI_CHAT_PROFILES_CONFIG_KEY`," in output
    assert "| `ai-chat` | 9 | `AI_CHAT_SCHEMA`, `AI_CHAT_PROFILES_SCHEMA`, `AI_CHAT_PROFILES_CONFIG_KEY`," in output
    assert (
        "| `config` | 8 | `DESKTOP_CONFIG_KEYS`, `DESKTOP_APP_CONFIG_KEY`, `desktop_config_rows`, `render_desktop_typescript`, `desktop_read_app_config`, `desktop_write_app_config`, `desktop_read_config_value`, `desktop_write_config_value` |"
        in output
    )
    assert "| `desktop.shell` | 7 | `desktop_project_build_command`, `desktop_hoi4_launch_command`," in output
    assert "| `build` | 8 | `BUILD_RUN_SCHEMA`, `BUILD_RUNS_SCHEMA`, `DesktopBuildRegistry`, `desktop_start_build`," in output
    assert "| `dependencies` | 2 | `desktop_dependency_status`, `desktop_install_dependency` |" in output
    assert "| `game-launch` | 2 | `desktop_hoi4_launch_command`, `desktop_run_hoi4` |" in output
    assert "| `open-path` | 4 | `desktop_open_path_command`, `desktop_open_path`, `desktop_open_path_targets`, `desktop_path_status` |" in output
    assert (
        "| `desktop-api` | 6 | `DESKTOP_API_TABLE_SCHEMA`, `DesktopApiRow`, `DesktopApiTable`, "
        "`get_desktop_api_selection`, `get_desktop_api_table`, `render_desktop_api_reference_markdown` |"
    ) in output
    assert (
        "| `desktop_state` | `function` | `desktop` | `sdk.project` | `state` | "
        "`paradev.desktop.desktop_state` | `dict[str, object]` |  | `desktop state contract` |"
    ) in output
    assert "| `desktop_read_binary_source` | `function` | `desktop` | `desktop.local` | `sources` |" in output
    assert "| `desktop_start_build` | `function` | `desktop` | `desktop.builds` | `build` |" in output
    assert "| `desktop_run_hoi4` | `function` | `desktop` | `desktop.shell` | `game-launch` |" in output


def test_desktop_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["desktop-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_games_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("games-api", "paradev.games", "get_games_api_table")

    assert payload["schema"] == "paradev.games.api-table.v1"
    assert payload["module_index"]["games"] == ["PROFILE_REGISTRIES", "registry_for_profile"]
    assert payload["module_index"]["games.api"] == [
        "GAMES_API_TABLE_SCHEMA",
        "GamesApiRow",
        "GamesApiTable",
        "get_games_api_selection",
        "get_games_api_table",
        "render_games_api_reference_markdown",
    ]
    assert payload["feature_index"]["profiles"] == ["PROFILE_REGISTRIES", "registry_for_profile"]
    assert payload["feature_index"]["games-api"] == [
        "GAMES_API_TABLE_SCHEMA",
        "GamesApiRow",
        "GamesApiTable",
        "get_games_api_selection",
        "get_games_api_table",
        "render_games_api_reference_markdown",
    ]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["GAMES_API_TABLE_SCHEMA"]["value"] == "paradev.games.api-table.v1"
    assert rows["PROFILE_REGISTRIES"]["returns"] == "dict[1]"
    assert rows["PROFILE_REGISTRIES"]["value"] == "hoi4"
    assert rows["registry_for_profile"]["returns"] == "BuildRegistry"
    assert rows["registry_for_profile"]["registry_seam"] == "game profile registry"
    assert rows["get_games_api_table"]["returns"] == "GamesApiTable"


def test_games_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("games-api", "paradev.games", "render_games_api_reference_markdown")

    assert "| `games` | 2 | `PROFILE_REGISTRIES`, `registry_for_profile` |" in output
    assert (
        "| `games-api` | 6 | `GAMES_API_TABLE_SCHEMA`, `GamesApiRow`, `GamesApiTable`, "
        "`get_games_api_selection`, `get_games_api_table`, `render_games_api_reference_markdown` |"
    ) in output
    assert (
        "| `registry_for_profile` | `function` | `games` | `games` | `profiles` | "
        "`paradev.games.registry_for_profile` | `BuildRegistry` |  | `game profile registry` |"
    ) in output


def test_games_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["games-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_project_facade_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("project-facade-api", "paradev.project", "get_project_facade_api_table")

    assert payload["schema"] == "paradev.project.facade-api-table.v1"
    assert payload["module_index"]["sdk.project"] == ["Project", "ProjectManifestError"]
    assert payload["module_index"]["api"] == [
        "PROJECT_FACADE_API_TABLE_SCHEMA",
        "ProjectFacadeApiRow",
        "ProjectFacadeApiTable",
        "get_project_facade_api_selection",
        "get_project_facade_api_table",
        "render_project_facade_api_reference_markdown",
    ]
    assert payload["feature_index"]["projects"] == ["Project"]
    assert payload["feature_index"]["errors"] == ["ProjectManifestError"]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["PROJECT_FACADE_API_TABLE_SCHEMA"]["value"] == "paradev.project.facade-api-table.v1"
    assert rows["Project"]["registry_seam"] == "project family/template registry"
    assert rows["get_project_facade_api_table"]["returns"] == "ProjectFacadeApiTable"


def test_project_facade_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("project-facade-api", "paradev.project", "render_project_facade_api_reference_markdown")

    assert "| `sdk.project` | 2 | `Project`, `ProjectManifestError` |" in output
    assert (
        "| `project-facade-api` | 6 | `PROJECT_FACADE_API_TABLE_SCHEMA`, `ProjectFacadeApiRow`, `ProjectFacadeApiTable`, "
        "`get_project_facade_api_selection`, `get_project_facade_api_table`, `render_project_facade_api_reference_markdown` |"
    ) in output
    assert (
        "| `Project` | `dataclass` | `project` | `sdk.project` | `projects` | `paradev.project.Project` | "
        "`Project class` |  | `project family/template registry` |"
    ) in output


def test_project_facade_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["project-facade-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_localization_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("localization-api", "paradev.localization", "get_localization_api_table")

    assert payload["schema"] == "paradev.localization.api-table.v1"
    assert payload["module_index"]["localization"] == ["HOI4_LANGUAGE_ALIASES", "canonical_language"]
    assert payload["module_index"]["api"] == [
        "LOCALIZATION_API_TABLE_SCHEMA",
        "LocalizationApiRow",
        "LocalizationApiTable",
        "get_localization_api_selection",
        "get_localization_api_table",
        "render_localization_api_reference_markdown",
    ]
    assert payload["feature_index"]["languages"] == ["HOI4_LANGUAGE_ALIASES", "canonical_language"]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["LOCALIZATION_API_TABLE_SCHEMA"]["value"] == "paradev.localization.api-table.v1"
    assert rows["HOI4_LANGUAGE_ALIASES"]["returns"] == "dict[24]"
    assert rows["canonical_language"]["registry_seam"] == "HOI4 language alias normalization"
    assert rows["get_localization_api_table"]["returns"] == "LocalizationApiTable"


def test_localization_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("localization-api", "paradev.localization", "render_localization_api_reference_markdown")

    assert "| `localization` | 2 | `HOI4_LANGUAGE_ALIASES`, `canonical_language` |" in output
    assert (
        "| `localization-api` | 6 | `LOCALIZATION_API_TABLE_SCHEMA`, `LocalizationApiRow`, `LocalizationApiTable`, "
        "`get_localization_api_selection`, `get_localization_api_table`, `render_localization_api_reference_markdown` |"
    ) in output
    assert (
        "| `canonical_language` | `function` | `localization` | `localization` | `languages` | "
        "`paradev.localization.canonical_language` | `str` |  | `HOI4 language alias normalization` |"
    ) in output


def test_localization_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["localization-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_surfaces_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("surfaces-api", "paradev.surfaces", "get_surfaces_api_table")

    assert payload["schema"] == "paradev.surfaces.api-table.v1"
    assert payload["module_index"]["api"] == [
        "SURFACES_API_TABLE_SCHEMA",
        "SurfacesApiRow",
        "SurfacesApiTable",
        "get_surfaces_api_selection",
        "get_surfaces_api_table",
        "render_surfaces_api_reference_markdown",
    ]
    assert payload["feature_index"]["surface-contracts"] == payload["module_index"]["surface_contracts"]
    assert payload["feature_index"]["openapi"] == ["get_openapi_seed"]
    assert payload["kind_index"]["type alias"] == ["SurfaceContractIdentifier", "SurfaceContractPayload"]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["get_api_catalog_reference_ids"]["returns"] == "list[str]"
    assert rows["get_api_catalog_selection"]["returns"] == "ApiCatalogTable | ApiCatalogRow | list[str]"
    assert rows["get_surface_contract_selection"]["returns"] == "SurfaceContractSummary | SurfaceContractPayload | list[SurfaceContractIdentifier]"
    assert rows["SURFACES_API_TABLE_SCHEMA"]["value"] == "paradev.surfaces.api-table.v1"
    assert rows["get_surfaces_api_table"]["registry_seam"] == "surface facade API table"
    assert rows["get_rest_api_table"]["surface"] == "rest"


def test_surfaces_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("surfaces-api", "paradev.surfaces", "render_surfaces_api_reference_markdown")

    assert (
        "| `api` | 6 | `SURFACES_API_TABLE_SCHEMA`, `SurfacesApiRow`, `SurfacesApiTable`, "
        "`get_surfaces_api_selection`, `get_surfaces_api_table`, `render_surfaces_api_reference_markdown` |"
    ) in output
    assert "| `rest` | 4 | `get_openapi_seed`, `get_rest_api_selection`, `get_rest_api_table`, `render_rest_api_reference_markdown` |" in output
    assert (
        "| `get_surfaces_api_table` | `function` | `surface` | `api` | `surfaces-api` | "
        "`paradev.surfaces.get_surfaces_api_table` | `SurfacesApiTable` |  | `surface facade API table` |"
    ) in output


def test_surfaces_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["surfaces-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_sdk_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("sdk-api", "paradev.sdk", "get_sdk_api_table")

    assert payload["schema"] == "paradev.sdk.api-table.v1"
    assert payload["module_index"]["api"] == [
        "SDK_API_TABLE_SCHEMA",
        "SdkApiRow",
        "SdkApiTable",
        "get_sdk_api_selection",
        "get_sdk_api_table",
        "render_sdk_api_reference_markdown",
    ]
    assert payload["module_index"]["project_api"] == [
        "PROJECT_API_TABLE_SCHEMA",
        "ProjectApiRow",
        "ProjectApiTable",
        "get_project_api_selection",
        "get_project_api_table",
        "render_project_api_reference_markdown",
    ]
    assert payload["module_index"]["desktop.local"] == [
        "desktop_chat",
        "desktop_chat_profiles",
        "desktop_reset_chat_profile",
        "desktop_write_chat_profile",
    ]
    assert payload["feature_index"]["ai-chat"] == [
        "desktop_chat",
        "desktop_chat_profiles",
        "desktop_reset_chat_profile",
        "desktop_write_chat_profile",
    ]
    assert payload["feature_index"]["inspections"][2] == "ProjectInspectionContract"
    assert payload["feature_index"]["project-api"][-2:] == ["get_project_api_table", "render_project_api_reference_markdown"]
    assert len(payload["kind_index"]["function"]) == 68
    assert len(payload["kind_index"]["schema constant"]) == 43
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["MODULE_BATCH_EDIT_REQUEST_SCHEMA"]["value"] == "paradev.module.batch_edit_request.v1"
    assert rows["MODULE_BATCH_EDIT_SCHEMA"]["value"] == "paradev.module.batch_edit.v1"
    assert rows["get_frontend_api_selection"]["returns"] == "dict[str, object] | list[str]"
    assert rows["get_project_inspection_selection"]["returns"] == "ProjectInspectionProjectContract | ProjectInspectionRow | list[str]"
    assert "get_project_api_table" in payload["kind_index"]["function"]
    assert "get_project_inspection_selection" in payload["kind_index"]["function"]
    assert "render_project_api_reference_markdown" in payload["kind_index"]["function"]
    assert rows["desktop_chat"]["feature"] == "ai-chat"
    assert rows["desktop_chat"]["doc_page"] == "docs/user-manual/desktop-api-reference.md"


def test_sdk_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("sdk-api", "paradev.sdk", "render_sdk_api_reference_markdown")

    assert (
        "| `api-table` | 6 | `SDK_API_TABLE_SCHEMA`, `SdkApiRow`, `SdkApiTable`, `get_sdk_api_selection`, `get_sdk_api_table`, `render_sdk_api_reference_markdown` |"
        in output
    )
    assert (
        "| `get_sdk_api_table` | `function` | `sdk` | `api` | `api-table` | `paradev.sdk.get_sdk_api_table` | " "`SdkApiTable` |  | `none` | `sdk` |"
    ) in output


def test_sdk_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["sdk-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_project_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("project-api", "paradev.sdk", "get_project_api_table")

    assert payload["schema"] == "paradev.sdk.project-api-table.v1"
    assert payload["kind_index"]["field"][0] == "Project.root"
    assert payload["kind_index"]["classmethod"] == ["Project.find", "Project.create", "Project.load"]
    assert payload["feature_index"]["project-state"][0] == "Project.root"
    assert payload["cli_command_index"]["paradev new"] == ["Project.create"]
    assert payload["cli_command_index"]["paradev module-batch-edit"] == ["Project.write_module_files"]
    assert payload["cli_command_index"]["paradev module-batch-request"] == ["Project.module_batch_edit_request"]
    assert payload["frontend_operation_index"]["project.create"] == ["Project.create"]
    assert payload["inspection_kind_index"]["summary"] == ["Project.summary", "Project.inspect"]


def test_project_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("project-api", "paradev.sdk", "render_project_api_reference_markdown")

    assert "| `project-state` | 15 | `Project.root`, `Project.manifest_path`," in output
    assert "| `paradev module-batch-edit` | 1 | `Project.write_module_files` |" in output
    assert "| `paradev module-batch-request` | 1 | `Project.module_batch_edit_request` |" in output
    assert "| `Project.create` | `classmethod` | `sdk` | `projects` |" in output


def test_project_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["project-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_templates_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("templates-api", "paradev.sdk.templates", "get_templates_api_table")

    assert payload["schema"] == "paradev.sdk.templates.api-table.v1"
    assert payload["row_count"] == len(payload["rows"]) == 18
    assert payload["module_index"]["sdk.templates"] == [
        "TEMPLATES_SCHEMA",
        "MODULE_SCAFFOLD_SCHEMA",
        "COLLECTION_SCAFFOLD_SCHEMA",
        "ProjectTemplateSpecError",
        "TemplateArg",
        "TemplateFile",
        "ModuleTemplate",
        "builtin_module_templates",
        "project_module_templates",
        "template_index",
        "module_scaffold_plan",
        "collection_scaffold_plan",
        "TEMPLATES_API_TABLE_SCHEMA",
        "TemplatesApiRow",
        "TemplatesApiTable",
        "get_templates_api_selection",
        "get_templates_api_table",
        "render_templates_api_reference_markdown",
    ]
    assert payload["feature_index"]["registry"] == ["builtin_module_templates", "project_module_templates", "template_index"]
    assert payload["feature_index"]["templates-api"][-3:] == [
        "get_templates_api_selection",
        "get_templates_api_table",
        "render_templates_api_reference_markdown",
    ]
    assert payload["kind_index"]["dataclass"] == ["TemplateArg", "TemplateFile", "ModuleTemplate"]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["TEMPLATES_SCHEMA"]["value"] == "paradev.sdk.templates.v1"
    assert rows["MODULE_SCAFFOLD_SCHEMA"]["value"] == "paradev.sdk.module_scaffold.v1"
    assert rows["COLLECTION_SCAFFOLD_SCHEMA"]["value"] == ("paradev.sdk.collection_scaffold.v1")
    assert rows["module_scaffold_plan"]["returns"] == "dict[str, object]"
    assert rows["module_scaffold_plan"]["registry_seam"] == ("resource scaffold planner")
    assert rows["get_templates_api_table"]["returns"] == "TemplatesApiTable"


def test_templates_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("templates-api", "paradev.sdk.templates", "render_templates_api_reference_markdown")

    assert (
        "| `sdk.templates` | 18 | `TEMPLATES_SCHEMA`, `MODULE_SCAFFOLD_SCHEMA`, `COLLECTION_SCAFFOLD_SCHEMA`, `ProjectTemplateSpecError`, "
        "`TemplateArg`, `TemplateFile`, `ModuleTemplate`,"
    ) in output
    assert "| `registry` | 3 | `builtin_module_templates`, `project_module_templates`, `template_index` |" in output
    assert (
        "| `module_scaffold_plan` | `function` | `sdk` | `sdk.templates` | `scaffold` | "
        "`paradev.sdk.templates.module_scaffold_plan` | `dict[str, object]` |  | `resource scaffold planner` |"
    ) in output


def test_templates_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["templates-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_copy_roots_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("copy-roots-api", "paradev.sdk.copy_roots", "get_copy_roots_api_table")

    assert payload["schema"] == "paradev.sdk.copy_roots.api-table.v1"
    assert payload["module_index"]["sdk.copy_roots"] == [
        "ARTIFACT_TARGET_ROOTS",
        "ProjectCopyRootSpecError",
        "CopyRootSpec",
        "project_copy_roots",
        "copy_root_artifacts",
        "merge_copy_root_artifacts",
        "COPY_ROOTS_API_TABLE_SCHEMA",
        "CopyRootsApiRow",
        "CopyRootsApiTable",
        "get_copy_roots_api_selection",
        "get_copy_roots_api_table",
        "render_copy_roots_api_reference_markdown",
    ]
    assert payload["feature_index"]["target-roots"] == ["ARTIFACT_TARGET_ROOTS"]
    assert payload["feature_index"]["artifacts"] == ["copy_root_artifacts", "merge_copy_root_artifacts"]
    assert payload["kind_index"]["TypedDict"] == ["CopyRootsApiRow", "CopyRootsApiTable"]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["ARTIFACT_TARGET_ROOTS"]["value"] == "build, output"
    assert rows["ProjectCopyRootSpecError"]["registry_seam"] == "copy-root validation"
    assert rows["project_copy_roots"]["returns"] == "tuple[CopyRootSpec, ...]"
    assert rows["copy_root_artifacts"]["returns"] == "tuple[tuple[Artifact, ...], tuple[Diagnostic, ...]]"
    assert rows["merge_copy_root_artifacts"]["registry_seam"] == "copy-root artifact pipeline"
    assert rows["get_copy_roots_api_table"]["returns"] == "CopyRootsApiTable"


def test_copy_roots_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("copy-roots-api", "paradev.sdk.copy_roots", "render_copy_roots_api_reference_markdown")

    assert (
        "| `sdk.copy_roots` | 12 | `ARTIFACT_TARGET_ROOTS`, `ProjectCopyRootSpecError`, `CopyRootSpec`, " "`project_copy_roots`, `copy_root_artifacts`,"
    ) in output
    assert "| `artifacts` | 2 | `copy_root_artifacts`, `merge_copy_root_artifacts` |" in output
    assert "| `TypedDict` | 2 | `CopyRootsApiRow`, `CopyRootsApiTable` |" in output
    assert (
        "| `merge_copy_root_artifacts` | `function` | `sdk` | `sdk.copy_roots` | `artifacts` | "
        "`paradev.sdk.copy_roots.merge_copy_root_artifacts` | `tuple[tuple[Artifact, ...], tuple[Diagnostic, ...]]` |  | "
        "`copy-root artifact pipeline` |"
    ) in output


def test_copy_roots_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["copy-roots-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_build_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("build-api", "paradev.build", "get_build_api_table")

    assert payload["schema"] == "paradev.build.api-table.v1"
    assert payload["module_index"]["api"] == [
        "BUILD_API_TABLE_SCHEMA",
        "BuildApiRow",
        "BuildApiTable",
        "get_build_api_selection",
        "get_build_api_table",
        "render_build_api_reference_markdown",
    ]
    assert payload["feature_index"]["families"][:3] == [
        "DEFAULT_IDENTITY_REWRITER",
        "PROJECT_DIAGRAM_PROVIDER_KIND",
        "BuildRegistry",
    ]
    assert payload["feature_index"]["records"] == ["Artifact", "BuildResult", "Collection", "Dependency", "Diagnostic", "Module", "module_collections"]
    assert payload["kind_index"]["TypedDict"] == ["BuildApiRow", "BuildApiTable"]


def test_build_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("build-api", "paradev.build", "render_build_api_reference_markdown")

    assert (
        "| `api` | 6 | `BUILD_API_TABLE_SCHEMA`, `BuildApiRow`, `BuildApiTable`, "
        "`get_build_api_selection`, `get_build_api_table`, `render_build_api_reference_markdown` |" in output
    )
    assert "| `families` | 20 | `DEFAULT_IDENTITY_REWRITER`, `PROJECT_DIAGRAM_PROVIDER_KIND`," in output
    assert "`ModuleDiagramSelectionDefault`" in output
    assert "| `TypedDict` | 2 | `BuildApiRow`, `BuildApiTable` |" in output


def test_build_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["build-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_pdx_api_cli_outputs_table_json() -> None:
    result = CliRunner().invoke(build_app(), ["pdx-api", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.sdk.pdx-api-table.v1"
    assert payload["row_count"] == len(payload["rows"])
    assert payload["feature_index"]["parse"] == ["PDX_PARSE_SCHEMA", "parse_pdx_file", "paradev parse", "GET /pdx/parse", "pdx_parse"]
    assert payload["surface_index"]["cli"] == [
        "paradev pdx-api",
        "paradev pdx-api --markdown",
        "paradev parse",
        "paradev format",
    ]


def test_pdx_api_cli_outputs_reference_markdown() -> None:
    result = CliRunner().invoke(build_app(), ["pdx-api", "--markdown"])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("# PDX API Reference\n")
    assert "Generated from `paradev.sdk.get_pdx_api_table()`." in result.output
    assert "| `rest` | 3 | `GET /pdx/parse`, `POST /pdx/format`, `GET /pdx-api` |" in result.output
    assert (
        '| `format_pdx_file` | `function` | `sdk` | `format` | `sdk` | `path, indent="\\t", comments=True, write=False` | '
        "`PDX format payload` | `ValueError on non-string indent` |"
    ) in result.output


def test_pdx_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["pdx-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_pdx_api_markdown_ignores_configured_json_default(cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.cli.output", default=None)

    try:
        CM_PARADEV.set("paradev.cli.output", "json")
        result = CliRunner().invoke(build_app(), ["pdx-api", "--markdown"])

        assert result.exit_code == 0, result.output
        assert result.output.startswith("# PDX API Reference\n")
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.cli.output")
        else:
            CM_PARADEV.set("paradev.cli.output", previous)


def test_pdx_core_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("pdx-core-api", "paradev.pdx", "get_pdx_core_api_table")

    assert payload["schema"] == "paradev.pdx.core-api-table.v1"
    assert payload["module_index"]["api"] == [
        "PDX_CORE_API_TABLE_SCHEMA",
        "PdxCoreApiRow",
        "PdxCoreApiTable",
        "get_pdx_core_api_selection",
        "get_pdx_core_api_table",
        "render_pdx_core_api_reference_markdown",
    ]
    assert payload["feature_index"]["scalars"] == [
        "SCALAR_BOOL",
        "SCALAR_COLOR",
        "SCALAR_ID",
        "SCALAR_NUM",
        "SCALAR_STR",
        "SCALAR_VAR",
    ]
    assert payload["kind_index"]["enum"] == ["TokenType"]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["parse_pdx"]["returns"] == "PDXBlock"
    assert rows["PDXParseError"]["kind"] == "exception"


def test_pdx_core_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("pdx-core-api", "paradev.pdx", "render_pdx_core_api_reference_markdown")

    assert (
        "| `api` | 6 | `PDX_CORE_API_TABLE_SCHEMA`, `PdxCoreApiRow`, `PdxCoreApiTable`, "
        "`get_pdx_core_api_selection`, `get_pdx_core_api_table`, `render_pdx_core_api_reference_markdown` |"
    ) in output
    assert "| `scalars` | 6 | `SCALAR_BOOL`, `SCALAR_COLOR`, `SCALAR_ID`, `SCALAR_NUM`, `SCALAR_STR`, `SCALAR_VAR` |" in output
    assert ("| `parse_pdx` | `function` | `pdx` | `parser` | `parser` | `paradev.pdx.parse_pdx` | " "`PDXBlock` |  | `PDX parser contract` |") in output


def test_pdx_core_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["pdx-core-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_lsp_api_cli_outputs_table_json() -> None:
    result = CliRunner().invoke(build_app(), ["lsp-api", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.sdk.lsp-api-table.v1"
    assert payload["row_count"] == len(payload["rows"])
    assert payload["surface_index"]["mcp"] == ["lsp_api"]
    assert payload["feature_index"]["diagnostics"] == [
        "LSP_DIAGNOSTICS_SCHEMA",
        "diagnose_pdx_lsp_text",
        "paradev lsp diagnostics",
        "POST /lsp/diagnostics",
        "textDocument/publishDiagnostics",
    ]
    assert payload["surface_index"]["lsp"] == [
        "textDocument/publishDiagnostics",
        "textDocument/documentSymbol",
        "textDocument/hover",
        "textDocument/formatting",
        "textDocument/completion",
        "textDocument/semanticTokens/full",
    ]


def test_lsp_api_cli_outputs_reference_markdown() -> None:
    result = CliRunner().invoke(build_app(), ["lsp-api", "--markdown"])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("# LSP API Reference\n")
    assert "Generated from `paradev.sdk.get_lsp_api_table()`." in result.output
    assert "| `api-table` | 11 | `LSP_API_TABLE_SCHEMA`, `LSP_API_TABLE_ROWS`, `LspApiRow`," in result.output
    assert "| `mcp` | 1 | `lsp_api` |" in result.output
    assert "| `lsp` | 6 | `textDocument/publishDiagnostics`, `textDocument/documentSymbol`, `textDocument/hover`," in result.output
    assert (
        '| `format_pdx_lsp_text` | `function` | `sdk` | `formatting` | `sdk` | `text, uri=None, path=None, indent="\\t", comments=True` | '
        "`LSP formatting payload` | `ValueError on unsupported text, uri, path, or indent` |"
    ) in result.output


def test_lsp_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["lsp-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_lsp_server_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("lsp-server-api", "paradev.lsp", "get_lsp_server_api_table")

    assert payload["schema"] == "paradev.lsp.server-api-table.v1"
    assert payload["module_index"] == {
        "server": [
            "PdxDocument",
            "PdxLanguageServer",
            "read_lsp_message",
            "serve_pdx_lsp_stdio",
            "write_lsp_message",
        ],
        "api": [
            "LSP_SERVER_API_TABLE_SCHEMA",
            "LspServerApiRow",
            "LspServerApiTable",
            "get_lsp_server_api_selection",
            "get_lsp_server_api_table",
            "render_lsp_server_api_reference_markdown",
        ],
    }
    assert payload["feature_index"]["framing"] == ["read_lsp_message", "write_lsp_message"]
    assert payload["feature_index"]["lsp-server-api"] == payload["module_index"]["api"]
    assert payload["kind_index"]["function"] == [
        "read_lsp_message",
        "serve_pdx_lsp_stdio",
        "write_lsp_message",
        "get_lsp_server_api_selection",
        "get_lsp_server_api_table",
        "render_lsp_server_api_reference_markdown",
    ]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["PdxDocument"]["registry_seam"] == "LSP document cache"
    assert rows["PdxLanguageServer"]["registry_seam"] == "LSP JSON-RPC dispatcher"
    assert rows["read_lsp_message"]["returns"] == "dict[str, object] | None"
    assert rows["LSP_SERVER_API_TABLE_SCHEMA"]["value"] == "paradev.lsp.server-api-table.v1"


def test_lsp_server_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("lsp-server-api", "paradev.lsp", "render_lsp_server_api_reference_markdown")

    assert "| `server` | 5 | `PdxDocument`, `PdxLanguageServer`, `read_lsp_message`, `serve_pdx_lsp_stdio`, `write_lsp_message` |" in output
    assert (
        "| `lsp-server-api` | 6 | `LSP_SERVER_API_TABLE_SCHEMA`, `LspServerApiRow`, `LspServerApiTable`, "
        "`get_lsp_server_api_selection`, `get_lsp_server_api_table`, `render_lsp_server_api_reference_markdown` |"
    ) in output
    assert (
        "| `PdxLanguageServer` | `class` | `lsp` | `server` | `server` | `paradev.lsp.PdxLanguageServer` | " "`class` |  | `LSP JSON-RPC dispatcher` |"
    ) in output


def test_lsp_server_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["lsp-server-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_catalog_api_cli_outputs_table_json() -> None:
    result = CliRunner().invoke(build_app(), ["catalog-api", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.hb.catalog-api-table.v1"
    assert payload["row_count"] == len(payload["rows"])
    assert payload["feature_index"]["preview"] == [
        "CATALOG_SCHEMA",
        "catalog_preview",
        "paradev hb catalog-preview",
        "GET /projects/inspect?kind=catalog-preview",
        "project_inspect kind=catalog-preview",
    ]
    assert payload["surface_index"]["mcp"] == [
        "project_inspect kind=catalog-preview",
        "project_inspect kind=catalog-query",
        "catalog_api",
    ]
    assert payload["surface_index"]["rest"][-1] == "GET /catalog-api"
    assert payload["feature_index"]["api-table"][-2:] == ["GET /catalog-api", "catalog_api"]


def test_catalog_api_cli_outputs_reference_markdown() -> None:
    result = CliRunner().invoke(build_app(), ["catalog-api", "--markdown"])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("# Catalog API Reference\n")
    assert "Generated from `paradev.hb.get_catalog_api_table()`." in result.output
    assert "| `api-table` | 11 | `CATALOG_API_TABLE_SCHEMA`, `CATALOG_API_TABLE_ROWS`, `CatalogApiRow`," in result.output
    assert ("| `rest` | 6 | `GET /projects/inspect?kind=catalog-preview`, `GET /projects/inspect?kind=catalog-query`,") in result.output
    assert "| `mcp` | 3 | `project_inspect kind=catalog-preview`, `project_inspect kind=catalog-query`, `catalog_api` |" in result.output
    assert (
        "| `catalog_query` | `function` | `sdk` | `query` | `sdk` | "
        "`project, database=None, entity=None, target_id=None, name=None, tag=None, limit=None, offset=0, include_data=True` | "
        "`catalog query payload` | `FileNotFoundError on missing database; RuntimeError on stale database; "
        "ValueError on invalid paging arguments` |"
    ) in result.output


def test_catalog_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["catalog-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_hb_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("hb-api", "paradev.hb", "get_hb_api_table")

    assert payload["schema"] == "paradev.hb.api-table.v1"
    assert payload["module_index"] == {
        "catalog": [
            "CATALOG_API_TABLE_ROWS",
            "CATALOG_API_TABLE_SCHEMA",
            "CATALOG_SCHEMA",
            "CatalogApiRow",
            "CatalogApiTable",
            "ENTITY_TYPES",
            "QUERY_SCHEMA",
            "REFRESH_SCHEMA",
            "SMOKE_SCHEMA",
            "STATUS_SCHEMA",
            "WRITE_SCHEMA",
            "catalog_completion_items",
            "catalog_preview",
            "catalog_query",
            "catalog_refresh",
            "catalog_smoke",
            "catalog_status",
            "catalog_write",
            "get_catalog_api_selection",
            "get_catalog_api_table",
            "render_catalog_api_reference_markdown",
        ],
        "api": [
            "HB_API_TABLE_SCHEMA",
            "HbApiRow",
            "HbApiTable",
            "get_hb_api_selection",
            "get_hb_api_table",
            "render_hb_api_reference_markdown",
        ],
    }
    assert payload["feature_index"]["hb-api"] == payload["module_index"]["api"]
    assert payload["feature_index"]["catalog-api"] == [
        "CATALOG_API_TABLE_ROWS",
        "CATALOG_API_TABLE_SCHEMA",
        "CatalogApiRow",
        "CatalogApiTable",
        "get_catalog_api_table",
        "render_catalog_api_reference_markdown",
    ]
    assert payload["feature_index"]["preview"] == ["CATALOG_SCHEMA", "catalog_preview"]
    assert payload["feature_index"]["completion"] == ["catalog_completion_items"]
    assert payload["kind_index"]["TypedDict"] == ["CatalogApiRow", "CatalogApiTable", "HbApiRow", "HbApiTable"]
    assert len(payload["kind_index"]["function"]) == 13
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["HB_API_TABLE_SCHEMA"]["value"] == "paradev.hb.api-table.v1"
    assert rows["CATALOG_API_TABLE_ROWS"]["returns"] == "tuple[37]"
    assert rows["ENTITY_TYPES"]["value"] == "16 entity types"
    assert rows["catalog_completion_items"]["registry_seam"] == "LSP catalog completion"
    assert rows["catalog_write"]["registry_seam"] == "HeavenBase SQLite backend"
    assert rows["get_hb_api_table"]["returns"] == "HbApiTable"


def test_hb_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("hb-api", "paradev.hb", "render_hb_api_reference_markdown")

    assert (
        "| `api` | 6 | `HB_API_TABLE_SCHEMA`, `HbApiRow`, `HbApiTable`, `get_hb_api_selection`, `get_hb_api_table`, " "`render_hb_api_reference_markdown` |"
    ) in output
    assert (
        "| `catalog-api` | 6 | `CATALOG_API_TABLE_ROWS`, `CATALOG_API_TABLE_SCHEMA`, `CatalogApiRow`, "
        "`CatalogApiTable`, `get_catalog_api_table`, `render_catalog_api_reference_markdown` |"
    ) in output
    assert "| `function` | 13 | `catalog_completion_items`, `catalog_preview`," in output
    assert (
        "| `catalog_preview` | `function` | `hb` | `catalog` | `preview` | `paradev.hb.catalog_preview` | "
        "`dict[str, object]` |  | `HeavenBase catalog integration` |"
    ) in output


def test_hb_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["hb-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_rest_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("rest-api", "paradev.surfaces.rest", "get_rest_api_table")

    rows = {row["symbol"]: row for row in payload["rows"]}
    assert payload["schema"] == "paradev.rest.api-table.v1"
    assert payload["method_index"]["GET"][0] == "GET /health"
    assert "GET /api-catalog" in payload["method_index"]["GET"]
    assert "GET /rest-api" in payload["method_index"]["GET"]
    assert "GET /cli-api" in payload["method_index"]["GET"]
    assert "GET /surface-contracts" in payload["method_index"]["GET"]
    assert "GET /catalog-api" in payload["method_index"]["GET"]
    assert "GET /lsp-api" in payload["method_index"]["GET"]
    assert payload["feature_index"]["api-catalog"] == ["GET /api-catalog"]
    assert payload["feature_index"]["rest"] == ["GET /rest-api"]
    assert payload["feature_index"]["cli"] == ["GET /cli-api"]
    assert payload["feature_index"]["surface-contracts"] == ["GET /surface-contracts"]
    assert payload["frontend_operation_index"]["catalog.write"] == ["POST /projects/catalog"]
    assert payload["frontend_operation_index"]["build.start"] == ["POST /desktop/builds"]
    assert payload["frontend_operation_index"]["build.runs"] == ["GET /desktop/builds"]
    assert payload["frontend_operation_index"]["build.status"] == ["GET /desktop/builds/status"]
    assert payload["frontend_operation_index"]["build.interrupt"] == ["POST /desktop/builds/interrupt"]
    assert payload["frontend_operation_index"]["ai.chat"] == ["POST /desktop/ai/chat"]
    assert payload["frontend_operation_index"]["ai.profiles"] == ["GET /desktop/ai/profiles"]
    assert payload["frontend_operation_index"]["ai.profile.write"] == ["PUT /desktop/ai/profiles/{profile_id}"]
    assert payload["frontend_operation_index"]["ai.profile.reset"] == ["DELETE /desktop/ai/profiles/{profile_id}"]
    assert payload["feature_index"]["catalog"] == [
        "GET /catalog-api",
        "GET /projects/catalog",
        "POST /projects/catalog",
        "PUT /projects/catalog",
    ]
    assert payload["feature_index"]["desktop"] == [
        "GET /desktop/state",
        "GET /desktop/builds",
        "POST /desktop/builds",
        "GET /desktop/builds/status",
        "POST /desktop/builds/interrupt",
        "POST /desktop/open-path",
        "POST /desktop/select-project",
        "POST /desktop/import-project-package",
        "GET /desktop/path-status",
        "GET /desktop/hoi4-launch-readiness",
        "GET /desktop/app-config",
        "PUT /desktop/app-config",
        "GET /desktop/config-value",
        "PUT /desktop/config-value",
        "POST /desktop/llm/test",
        "POST /desktop/ai/chat",
        "GET /desktop/ai/profiles",
        "PUT /desktop/ai/profiles/{profile_id}",
        "DELETE /desktop/ai/profiles/{profile_id}",
    ]
    assert rows["GET /frontend-api"]["inputs"] == "query:operation_id, query:group_id, query:form, query:index_name, query:key"
    assert rows["GET /desktop/builds"]["inputs"] == "query:project_root"
    assert rows["GET /desktop/builds"]["required_inputs"] == "none"
    assert rows["GET /desktop/builds"]["returns"] == "200 Desktop build-runs payload."
    assert rows["GET /desktop/builds"]["frontend_operation_ids"] == ["build.runs"]
    assert rows["POST /desktop/builds"]["inputs"] == "body"
    assert rows["POST /desktop/builds"]["required_inputs"] == "body"
    assert rows["POST /desktop/builds"]["returns"] == "200 Desktop build run payload."
    assert rows["POST /desktop/builds"]["frontend_operation_ids"] == ["build.start"]
    assert rows["GET /desktop/builds/status"]["inputs"] == "query:run_id"
    assert rows["GET /desktop/builds/status"]["required_inputs"] == "query:run_id"
    assert rows["GET /desktop/builds/status"]["returns"] == "200 Desktop build run payload."
    assert rows["GET /desktop/builds/status"]["frontend_operation_ids"] == ["build.status"]
    assert rows["POST /desktop/builds/interrupt"]["inputs"] == "body"
    assert rows["POST /desktop/builds/interrupt"]["required_inputs"] == "body"
    assert rows["POST /desktop/builds/interrupt"]["returns"] == "200 Desktop build run payload."
    assert rows["POST /desktop/builds/interrupt"]["frontend_operation_ids"] == ["build.interrupt"]
    assert rows["POST /desktop/import-project-package"]["inputs"] == "none"
    assert rows["POST /desktop/import-project-package"]["required_inputs"] == "none"
    assert rows["POST /desktop/import-project-package"]["returns"] == ("200 Desktop project-package installation payload or null.")
    assert rows["GET /desktop/path-status"]["inputs"] == "query:path"
    assert rows["GET /desktop/path-status"]["required_inputs"] == "query:path"
    assert rows["GET /desktop/path-status"]["returns"] == "200 Desktop path status payload."
    assert rows["GET /desktop/hoi4-launch-readiness"]["inputs"] == "query:project_root"
    assert rows["GET /desktop/hoi4-launch-readiness"]["required_inputs"] == "query:project_root"
    assert rows["GET /desktop/hoi4-launch-readiness"]["returns"] == "200 Desktop HOI4 launch-readiness payload."
    assert rows["GET /projects/catalog"]["inputs"] == "query:path"
    assert rows["GET /projects/catalog"]["returns"] == "200 Catalog status payload."
    assert rows["GET /projects/catalog"]["frontend_operation_ids"] == []
    assert rows["GET /desktop/app-config"]["returns"] == "200 Desktop app config payload."
    assert rows["PUT /desktop/app-config"]["required_inputs"] == "body"
    assert rows["GET /desktop/config-value"]["required_inputs"] == "query:key"
    assert rows["PUT /desktop/config-value"]["returns"] == "200 Desktop config value payload."
    assert rows["POST /desktop/llm/test"]["returns"] == "200 Desktop LLM route test payload."
    assert rows["POST /desktop/ai/chat"]["frontend_operation_ids"] == ["ai.chat"]
    assert rows["POST /desktop/ai/chat"]["returns"] == "200 Desktop AI chat payload."
    assert rows["GET /desktop/ai/profiles"]["frontend_operation_ids"] == ["ai.profiles"]
    assert rows["GET /desktop/ai/profiles"]["returns"] == "200 Desktop AI chat profile payload."
    assert rows["PUT /desktop/ai/profiles/{profile_id}"]["frontend_operation_ids"] == ["ai.profile.write"]
    assert rows["PUT /desktop/ai/profiles/{profile_id}"]["required_inputs"] == "path:profile_id, body"
    assert rows["PUT /desktop/ai/profiles/{profile_id}"]["returns"] == "200 Desktop AI chat profile payload."
    assert rows["DELETE /desktop/ai/profiles/{profile_id}"]["frontend_operation_ids"] == ["ai.profile.reset"]
    assert rows["DELETE /desktop/ai/profiles/{profile_id}"]["required_inputs"] == "path:profile_id"
    assert rows["DELETE /desktop/ai/profiles/{profile_id}"]["returns"] == "200 Desktop AI chat profile payload."
    assert rows["GET /rest-api"]["returns"] == "200 REST API table, row, or index lookup payload."
    assert rows["GET /cli-api"]["returns"] == "200 CLI API table, row, or index lookup payload."
    assert rows["GET /catalog-api"]["returns"] == "200 Catalog API table, row, or index lookup payload."
    assert rows["GET /lsp-api"]["returns"] == "200 LSP API table, row, or index lookup payload."


def test_rest_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("rest-api", "paradev.surfaces.rest", "render_rest_api_reference_markdown")

    assert "| `GET` | 37 | `GET /health`, `GET /api-catalog`, `GET /rest-api`, `GET /cli-api`," in output
    assert "| `lsp` | 8 | `GET /lsp-api`, `POST /lsp/diagnostics`, `POST /lsp/symbols`," in output
    assert "| `api-catalog` | 1 | `GET /api-catalog` |" in output
    assert "| `rest` | 1 | `GET /rest-api` |" in output
    assert "| `cli` | 1 | `GET /cli-api` |" in output
    assert "| `surface-contracts` | 1 | `GET /surface-contracts` |" in output
    assert "| `catalog` | 4 | `GET /catalog-api`, `GET /projects/catalog`, `POST /projects/catalog`, `PUT /projects/catalog` |" in output
    assert "| `desktop` | 19 | `GET /desktop/state`, `GET /desktop/builds`, `POST /desktop/builds`, `GET /desktop/builds/status`," in output
    assert "| `catalog.write` | 1 | `POST /projects/catalog` |" in output
    assert "| `build.start` | 1 | `POST /desktop/builds` |" in output
    assert "| `build.runs` | 1 | `GET /desktop/builds` |" in output
    assert "| `build.status` | 1 | `GET /desktop/builds/status` |" in output
    assert "| `build.interrupt` | 1 | `POST /desktop/builds/interrupt` |" in output
    assert "| `ai.profiles` | 1 | `GET /desktop/ai/profiles` |" in output
    assert "| `ai.profile.write` | 1 | `PUT /desktop/ai/profiles/{profile_id}` |" in output
    assert "| `ai.profile.reset` | 1 | `DELETE /desktop/ai/profiles/{profile_id}` |" in output
    assert "| `ai.chat` | 1 | `POST /desktop/ai/chat` |" in output
    assert (
        "| `GET /api-catalog` | `REST route` | `rest` | `api-catalog` | `GET` | `/api-catalog` | "
        "`query:reference_id, query:index_name, query:key` | `none` | "
        "`200 API catalog table, row, or index lookup payload.` | `400 Invalid API catalog selector.` |"
    ) in output
    assert (
        "| `GET /rest-api` | `REST route` | `rest` | `rest` | `GET` | `/rest-api` | "
        "`query:symbol, query:index_name, query:key` | `none` | "
        "`200 REST API table, row, or index lookup payload.` | `400 Invalid REST API selector.` |"
    ) in output
    assert (
        "| `GET /cli-api` | `REST route` | `rest` | `cli` | `GET` | `/cli-api` | "
        "`query:symbol, query:index_name, query:key` | `none` | "
        "`200 CLI API table, row, or index lookup payload.` | `400 Invalid CLI API selector.` |"
    ) in output
    assert (
        "| `GET /catalog-api` | `REST route` | `rest` | `catalog` | `GET` | `/catalog-api` | "
        "`query:symbol, query:index_name, query:key` | `none` | "
        "`200 Catalog API table, row, or index lookup payload.` | `400 Invalid catalog API selector.` |"
    ) in output
    assert (
        "| `GET /surface-contracts` | `REST route` | `rest` | `surface-contracts` | `GET` | `/surface-contracts` | "
        "`query:identifier, query:status` | `none` | "
        "`200 Surface contract summary, contract payload, or status id list.` | `400 Invalid surface contract selector.` |"
    ) in output
    assert (
        "| `GET /frontend-api` | `REST route` | `rest` | `frontend-api` | `GET` | `/frontend-api` | "
        "`query:operation_id, query:group_id, query:form, query:index_name, query:key` | `none` | "
        "`200 Frontend API contract or selected projection.` | `400 Invalid frontend API selector.` |"
    ) in output
    assert (
        "| `POST /projects/catalog` | `REST route` | `rest` | `catalog` | `POST` | `/projects/catalog` | "
        "`query:path, query:profile, query:database` | `none` | `200 Catalog write payload.` |  | "
        "`catalog.write` |"
    ) in output
    assert (
        "| `POST /desktop/ai/chat` | `REST route` | `rest` | `desktop` | `POST` | `/desktop/ai/chat` | "
        "`body` | `body` | `200 Desktop AI chat payload.` |  | `ai.chat` |"
    ) in output


def test_rest_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["rest-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_rest_facade_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("rest-facade-api", "paradev.api", "get_rest_facade_api_table")

    assert payload["schema"] == "paradev.rest.facade-api-table.v1"
    assert payload["module_index"] == {
        "rest": [
            "apply_project_draft",
            "build_app",
            "create_module_batch",
            "create_module_draft",
            "get_openapi_seed",
            "read_project_source",
            "read_project_source_form",
        ],
        "api": [
            "REST_FACADE_API_TABLE_SCHEMA",
            "RestFacadeApiRow",
            "RestFacadeApiTable",
            "get_rest_facade_api_selection",
            "get_rest_facade_api_table",
            "render_rest_facade_api_reference_markdown",
        ],
    }
    assert payload["feature_index"]["server"] == ["build_app"]
    assert payload["feature_index"]["rest-facade-api"] == payload["module_index"]["api"]
    assert payload["kind_index"]["TypedDict"] == ["RestFacadeApiRow", "RestFacadeApiTable"]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["apply_project_draft"]["registry_seam"] == "REST project draft bridge"
    assert rows["build_app"]["returns"] == "FastAPI app"
    assert rows["create_module_batch"]["registry_seam"] == "REST module batch bridge"
    assert rows["get_openapi_seed"]["registry_seam"] == "OpenAPI seed contract"
    assert rows["REST_FACADE_API_TABLE_SCHEMA"]["value"] == "paradev.rest.facade-api-table.v1"


def test_rest_facade_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("rest-facade-api", "paradev.api", "render_rest_facade_api_reference_markdown")

    assert (
        "| `rest` | 7 | `apply_project_draft`, `build_app`, `create_module_batch`, `create_module_draft`, `get_openapi_seed`, "
        "`read_project_source`, `read_project_source_form` |"
    ) in output
    assert (
        "| `rest-facade-api` | 6 | `REST_FACADE_API_TABLE_SCHEMA`, `RestFacadeApiRow`, `RestFacadeApiTable`, "
        "`get_rest_facade_api_selection`, `get_rest_facade_api_table`, `render_rest_facade_api_reference_markdown` |"
    ) in output
    assert ("| `build_app` | `function` | `rest` | `rest` | `server` | `paradev.api.build_app` | " "`FastAPI app` |  | `FastAPI app factory` |") in output


def test_rest_facade_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["rest-facade-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_mcp_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("mcp-api", "paradev.surfaces.mcp", "get_mcp_api_table")

    assert payload["schema"] == "paradev.mcp.api-table.v1"
    assert len(payload["mode_index"]["read"]) == 31
    assert payload["frontend_operation_index"]["catalog.query"] == ["project_inspect"]
    assert payload["feature_index"]["api-catalog"] == ["api_catalog"]
    assert payload["feature_index"]["catalog"] == ["catalog_api"]
    assert payload["feature_index"]["mcp"] == ["mcp_api"]
    assert payload["feature_index"]["cli"] == ["cli_api"]
    assert payload["feature_index"]["surface-contracts"] == ["surface_contracts"]
    assert payload["feature_index"]["lsp"] == ["lsp_api"]
    assert payload["feature_index"]["authoring"] == [
        "project_templates",
        "project_authoring_path",
        "project_authoring_plan",
        "project_scaffold",
        "project_create_modules",
        "project_draft_apply",
        "collection_scaffold",
        "localization_workspace",
        "localization_plan",
    ]
    rows = {row["symbol"]: row for row in payload["rows"]}
    assert rows["frontend_api"]["sdk_method"] == "get_frontend_api_selection"
    assert rows["catalog_api"]["sdk_method"] == "get_catalog_api_selection"
    assert rows["mcp_api"]["sdk_method"] == "get_mcp_api_selection"
    assert rows["cli_api"]["sdk_method"] == "get_cli_api_selection"
    assert rows["lsp_api"]["sdk_method"] == "get_lsp_api_selection"
    assert rows["project_create_modules"]["sdk_method"] == "Project.create_modules"
    assert rows["project_draft_apply"]["sdk_method"] == ("Project.apply_source_draft")
    assert rows["collection_scaffold"]["sdk_method"] == ("Project.scaffold_collection")


def test_mcp_api_cli_outputs_reference_markdown() -> None:
    output = assert_cli_markdown_output("mcp-api", "paradev.surfaces.mcp", "render_mcp_api_reference_markdown")

    assert "| `pdx` | 3 | `pdx_parse`, `pdx_format`, `pdx_api` |" in output
    assert "| `lsp` | 1 | `lsp_api` |" in output
    assert "| `catalog` | 1 | `catalog_api` |" in output
    assert "| `mcp` | 1 | `mcp_api` |" in output
    assert "| `cli` | 1 | `cli_api` |" in output
    assert "| `api-catalog` | 1 | `api_catalog` |" in output
    assert "| `surface-contracts` | 1 | `surface_contracts` |" in output
    assert "| `catalog.query` | 1 | `project_inspect` |" in output
    assert (
        "| `frontend_api` | `MCP tool` | `mcp` | `frontend-api` | `read` | `get_frontend_api_selection` | "
        "`operation_id, group_id, index_name, key` | `Frontend API contract or selected projection` | `ValueError on invalid frontend API selector` |"
    ) in output
    assert (
        "| `api_catalog` | `MCP tool` | `mcp` | `api-catalog` | `read` | `get_api_catalog_selection` | "
        "`reference_id, index_name, key` | `API catalog table, row, or index lookup payload` | "
        "`ValueError or KeyError on invalid API catalog selector` |"
    ) in output
    assert (
        "| `catalog_api` | `MCP tool` | `mcp` | `catalog` | `read` | `get_catalog_api_selection` | "
        "`symbol, index_name, key` | `Catalog API table, row, or index lookup payload` | "
        "`ValueError or KeyError on invalid catalog API selector` |"
    ) in output
    assert (
        "| `mcp_api` | `MCP tool` | `mcp` | `mcp` | `read` | `get_mcp_api_selection` | "
        "`symbol, index_name, key` | `MCP API table, row, or index lookup payload` | "
        "`ValueError or KeyError on invalid MCP API selector` |"
    ) in output
    assert (
        "| `cli_api` | `MCP tool` | `mcp` | `cli` | `read` | `get_cli_api_selection` | "
        "`symbol, index_name, key` | `CLI API table, row, or index lookup payload` | "
        "`ValueError or KeyError on invalid CLI API selector` |"
    ) in output
    assert (
        "| `surface_contracts` | `MCP tool` | `mcp` | `surface-contracts` | `read` | "
        "`get_surface_contract_selection` | `identifier, status` | "
        "`Surface contract summary, contract payload, or status id list` | "
        "`ValueError or KeyError on invalid surface contract selector` |"
    ) in output
    assert (
        "| `project_scaffold` | `MCP tool` | `mcp` | `authoring` | `write` | `Project.scaffold_module` | "
        "`path, template_id, object_id, source_root, values, write, force` | `SDK scaffold draft plan` |  | "
        "`module.create` |"
    ) in output
    assert (
        "| `project_create_modules` | `MCP tool` | `mcp` | `authoring` | `write` | `Project.create_modules` | "
        "`path, modules, source_root, write, plan_hash` | `SDK atomic module batch plan or apply payload` | "
        "`ProjectManifestError, OSError, or ValueError on invalid module batch` |"
    ) in output
    assert (
        "| `collection_scaffold` | `MCP tool` | `mcp` | `authoring` | `write` | "
        "`Project.scaffold_collection` | `path, template_id, collection_id, "
        "values, source_root, write, force, plan_hash` | "
        "`SDK guarded collection scaffold plan or apply payload` | "
        "`ProjectManifestError, OSError, or ValueError on invalid collection scaffold` |"
    ) in output


def test_mcp_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["mcp-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_cli_api_cli_outputs_table_json() -> None:
    payload = assert_cli_table_output("cli-api", "paradev.surfaces.cli", "get_cli_api_table")

    assert payload["schema"] == "paradev.cli.api-table.v1"
    assert len(payload["kind_index"]["command"]) == 101
    assert len(payload["kind_index"]["command projection"]) == 96
    assert len(payload["kind_index"]["binding variant"]) == 7
    assert payload["feature_index"]["api-catalog"] == [
        "paradev api-catalog",
        "paradev api-catalog --reference",
        "paradev api-catalog --index --key",
        "paradev api-catalog --markdown",
    ]
    assert payload["feature_index"]["package"] == [
        "paradev package-api",
        "paradev package-api --markdown",
        "paradev package-api --symbol",
        "paradev package-api --index --key",
    ]
    assert payload["feature_index"]["surfaces"] == [
        "paradev surfaces-api",
        "paradev surfaces-api --markdown",
        "paradev surfaces-api --symbol",
        "paradev surfaces-api --index --key",
    ]
    assert payload["feature_index"]["cli"] == ["paradev cli-api", "paradev cli-api --markdown", "paradev cli-api --symbol", "paradev cli-api --index --key"]
    assert payload["feature_index"]["sdk"] == ["paradev sdk-api", "paradev sdk-api --markdown", "paradev sdk-api --symbol", "paradev sdk-api --index --key"]
    assert payload["feature_index"]["gui"] == ["paradev gui-api", "paradev gui-api --markdown", "paradev gui-api --symbol", "paradev gui-api --index --key"]
    assert payload["feature_index"]["desktop"] == [
        "paradev desktop-api",
        "paradev desktop-api --markdown",
        "paradev desktop-api --typescript",
        "paradev desktop-api --symbol",
        "paradev desktop-api --index --key",
    ]
    assert payload["feature_index"]["games"] == [
        "paradev games-api",
        "paradev games-api --markdown",
        "paradev games-api --symbol",
        "paradev games-api --index --key",
    ]
    assert payload["feature_index"]["localization"] == [
        "paradev localization-api",
        "paradev localization-api --markdown",
        "paradev localization-api --symbol",
        "paradev localization-api --index --key",
    ]
    assert payload["feature_index"]["authoring"] == [
        "paradev templates-api",
        "paradev module-batch-create",
        "paradev templates",
        "paradev authoring-path",
        "paradev authoring-plan",
        "paradev scaffold",
        "paradev templates-api --markdown",
        "paradev templates-api --symbol",
        "paradev templates-api --index --key",
    ]
    assert payload["feature_index"]["copy-roots"] == [
        "paradev copy-roots-api",
        "paradev copy-roots-api --markdown",
        "paradev copy-roots-api --symbol",
        "paradev copy-roots-api --index --key",
    ]
    assert payload["feature_index"]["config"] == [
        "paradev config-api",
        "paradev config",
        "paradev config get",
        "paradev config list",
        "paradev config set",
        "paradev config unset",
        "paradev config scopes",
        "paradev config history",
        "paradev setup",
        "paradev init",
        "paradev pj",
        "paradev config-api --markdown",
        "paradev config-api --symbol",
        "paradev config-api --index --key",
    ]
    assert payload["feature_index"]["lsp"][:3] == ["paradev lsp-api", "paradev lsp-server-api", "paradev lsp"]
    assert payload["feature_index"]["rest"] == [
        "paradev rest-api",
        "paradev rest-facade-api",
        "paradev rest-api --markdown",
        "paradev rest-facade-api --markdown",
        "paradev rest-api --symbol",
        "paradev rest-api --index --key",
        "paradev rest-facade-api --symbol",
        "paradev rest-facade-api --index --key",
    ]
    assert payload["feature_index"]["catalog"][:3] == ["paradev catalog-api", "paradev hb-api", "paradev hb"]
    assert "paradev hb-api --markdown" in payload["feature_index"]["catalog"]
    assert "paradev hb-api --symbol" in payload["feature_index"]["catalog"]
    assert "paradev project-api" in payload["feature_index"]["projects"]
    assert "paradev project-api --markdown" in payload["feature_index"]["projects"]
    assert "paradev project-api --symbol" in payload["feature_index"]["projects"]
    assert "paradev project-facade-api" in payload["feature_index"]["projects"]
    assert "paradev project-facade-api --markdown" in payload["feature_index"]["projects"]
    assert "paradev project-facade-api --symbol" in payload["feature_index"]["projects"]
    assert "paradev build-api" in payload["feature_index"]["build"]
    assert "paradev build-api --markdown" in payload["feature_index"]["build"]
    assert "paradev build-api --symbol" in payload["feature_index"]["build"]
    assert payload["adapter_index"]["get_api_catalog_selection"] == [
        "paradev api-catalog",
        "paradev api-catalog --reference",
        "paradev api-catalog --index --key",
    ]
    assert payload["adapter_index"]["render_api_catalog_reference_markdown"] == ["paradev api-catalog --markdown"]
    assert payload["adapter_index"]["get_surface_contract_selection"] == [
        "paradev architecture --surface-contract",
        "paradev architecture --surface-contracts",
    ]
    assert payload["adapter_index"]["get_frontend_api_selection"] == [
        "paradev frontend-api",
        "paradev frontend-api --operation",
        "paradev frontend-api --group",
        "paradev frontend-api --operation --form",
        "paradev frontend-api --index --key",
    ]
    assert payload["adapter_index"]["get_project_inspection_selection"] == [
        "paradev inspections",
        "paradev inspections --kind",
        "paradev inspections --index --key",
    ]
    assert payload["adapter_index"]["Project.module_batch_edit_request"] == ["paradev module-batch-request"]
    assert payload["adapter_index"]["get_package_api_selection"] == ["paradev package-api", "paradev package-api --symbol", "paradev package-api --index --key"]
    assert payload["adapter_index"]["render_package_api_reference_markdown"] == ["paradev package-api --markdown"]
    assert payload["adapter_index"]["get_config_api_selection"] == ["paradev config-api", "paradev config-api --symbol", "paradev config-api --index --key"]
    assert payload["adapter_index"]["render_config_api_reference_markdown"] == ["paradev config-api --markdown"]
    assert payload["adapter_index"]["get_gui_api_selection"] == ["paradev gui-api", "paradev gui-api --symbol", "paradev gui-api --index --key"]
    assert payload["adapter_index"]["render_gui_api_reference_markdown"] == ["paradev gui-api --markdown"]
    assert payload["adapter_index"]["get_desktop_api_selection"] == ["paradev desktop-api", "paradev desktop-api --symbol", "paradev desktop-api --index --key"]
    assert payload["adapter_index"]["render_desktop_api_reference_markdown"] == ["paradev desktop-api --markdown"]
    assert payload["adapter_index"]["render_desktop_typescript"] == ["paradev desktop-api --typescript"]
    assert payload["adapter_index"]["get_games_api_selection"] == ["paradev games-api", "paradev games-api --symbol", "paradev games-api --index --key"]
    assert payload["adapter_index"]["render_games_api_reference_markdown"] == ["paradev games-api --markdown"]
    assert payload["adapter_index"]["get_surfaces_api_selection"] == [
        "paradev surfaces-api",
        "paradev surfaces-api --symbol",
        "paradev surfaces-api --index --key",
    ]
    assert payload["adapter_index"]["render_surfaces_api_reference_markdown"] == ["paradev surfaces-api --markdown"]
    assert payload["adapter_index"]["get_cli_api_selection"] == ["paradev cli-api", "paradev cli-api --symbol", "paradev cli-api --index --key"]
    assert payload["adapter_index"]["get_sdk_api_selection"] == ["paradev sdk-api", "paradev sdk-api --symbol", "paradev sdk-api --index --key"]
    assert payload["adapter_index"]["get_project_api_selection"] == ["paradev project-api", "paradev project-api --symbol", "paradev project-api --index --key"]
    assert payload["adapter_index"]["render_project_api_reference_markdown"] == ["paradev project-api --markdown"]
    assert payload["adapter_index"]["get_templates_api_selection"] == [
        "paradev templates-api",
        "paradev templates-api --symbol",
        "paradev templates-api --index --key",
    ]
    assert payload["adapter_index"]["render_templates_api_reference_markdown"] == ["paradev templates-api --markdown"]
    assert payload["adapter_index"]["get_copy_roots_api_selection"] == [
        "paradev copy-roots-api",
        "paradev copy-roots-api --symbol",
        "paradev copy-roots-api --index --key",
    ]
    assert payload["adapter_index"]["render_copy_roots_api_reference_markdown"] == ["paradev copy-roots-api --markdown"]
    assert payload["adapter_index"]["get_project_facade_api_selection"] == [
        "paradev project-facade-api",
        "paradev project-facade-api --symbol",
        "paradev project-facade-api --index --key",
    ]
    assert payload["adapter_index"]["render_project_facade_api_reference_markdown"] == ["paradev project-facade-api --markdown"]
    assert payload["adapter_index"]["get_localization_api_selection"] == [
        "paradev localization-api",
        "paradev localization-api --symbol",
        "paradev localization-api --index --key",
    ]
    assert payload["adapter_index"]["render_localization_api_reference_markdown"] == ["paradev localization-api --markdown"]
    assert payload["adapter_index"]["get_build_api_selection"] == ["paradev build-api", "paradev build-api --symbol", "paradev build-api --index --key"]
    assert payload["adapter_index"]["render_build_api_reference_markdown"] == ["paradev build-api --markdown"]
    assert payload["adapter_index"]["get_pdx_core_api_selection"] == [
        "paradev pdx-core-api",
        "paradev pdx-core-api --symbol",
        "paradev pdx-core-api --index --key",
    ]
    assert payload["adapter_index"]["render_pdx_core_api_reference_markdown"] == ["paradev pdx-core-api --markdown"]
    assert payload["adapter_index"]["get_lsp_server_api_selection"] == [
        "paradev lsp-server-api",
        "paradev lsp-server-api --symbol",
        "paradev lsp-server-api --index --key",
    ]
    assert payload["adapter_index"]["render_lsp_server_api_reference_markdown"] == ["paradev lsp-server-api --markdown"]
    assert payload["adapter_index"]["get_rest_facade_api_selection"] == [
        "paradev rest-facade-api",
        "paradev rest-facade-api --symbol",
        "paradev rest-facade-api --index --key",
    ]
    assert payload["adapter_index"]["render_rest_facade_api_reference_markdown"] == ["paradev rest-facade-api --markdown"]
    assert payload["adapter_index"]["get_hb_api_selection"] == ["paradev hb-api", "paradev hb-api --symbol", "paradev hb-api --index --key"]
    assert payload["adapter_index"]["render_hb_api_reference_markdown"] == ["paradev hb-api --markdown"]
    assert payload["frontend_operation_index"]["catalog.write"] == ["paradev hb catalog-write"]


def test_cli_api_cli_outputs_reference_markdown() -> None:
    result_output = assert_cli_markdown_output("cli-api", "paradev.surfaces.cli", "render_cli_api_reference_markdown")

    assert "| `command group` | 4 | `paradev config`, `paradev hb`, `paradev mcp`, `paradev lsp` |" in result_output
    assert "| `surface.frontend_api.action` | 1 | `paradev frontend-api --operation --action` |" in result_output
    assert (
        "| `api-catalog` | 4 | `paradev api-catalog`, `paradev api-catalog --reference`, "
        "`paradev api-catalog --index --key`, `paradev api-catalog --markdown` |"
    ) in result_output
    assert "| `gui` | 4 | `paradev gui-api`, `paradev gui-api --markdown`, `paradev gui-api --symbol`, `paradev gui-api --index --key` |" in result_output
    assert (
        "| `desktop` | 5 | `paradev desktop-api`, `paradev desktop-api --markdown`, `paradev desktop-api --typescript`, `paradev desktop-api --symbol`, `paradev desktop-api --index --key` |"
        in result_output
    )
    assert (
        "| `games` | 4 | `paradev games-api`, `paradev games-api --markdown`, `paradev games-api --symbol`, `paradev games-api --index --key` |"
        in result_output
    )
    assert (
        "| `authoring` | 9 | `paradev templates-api`, `paradev module-batch-create`, `paradev templates`, `paradev authoring-path`, "
        "`paradev authoring-plan`, `paradev scaffold`, `paradev templates-api --markdown`, "
        "`paradev templates-api --symbol`, `paradev templates-api --index --key` |"
    ) in result_output
    assert (
        "| `copy-roots` | 4 | `paradev copy-roots-api`, `paradev copy-roots-api --markdown`, `paradev copy-roots-api --symbol`, `paradev copy-roots-api --index --key` |"
        in result_output
    )
    assert "| `config` | 14 | `paradev config-api`, `paradev config`, `paradev config get`," in result_output
    assert ("| `lsp` | 17 | `paradev lsp-api`, `paradev lsp-server-api`, `paradev lsp`, `paradev lsp serve`, " "`paradev lsp diagnostics`,") in result_output
    assert (
        "| `rest` | 8 | `paradev rest-api`, `paradev rest-facade-api`, `paradev rest-api --markdown`, "
        "`paradev rest-facade-api --markdown`, `paradev rest-api --symbol`, `paradev rest-api --index --key`, "
        "`paradev rest-facade-api --symbol`, `paradev rest-facade-api --index --key` |"
    ) in result_output
    assert "| `catalog` | 14 | `paradev catalog-api`, `paradev hb-api`, `paradev hb`," in result_output
    assert (
        "| `package` | 4 | `paradev package-api`, `paradev package-api --markdown`, `paradev package-api --symbol`, `paradev package-api --index --key` |"
        in result_output
    )
    assert (
        "| `surfaces` | 4 | `paradev surfaces-api`, `paradev surfaces-api --markdown`, `paradev surfaces-api --symbol`, `paradev surfaces-api --index --key` |"
        in result_output
    )
    assert "| `sdk` | 4 | `paradev sdk-api`, `paradev sdk-api --markdown`, `paradev sdk-api --symbol`, `paradev sdk-api --index --key` |" in result_output
    assert (
        "| `localization` | 4 | `paradev localization-api`, `paradev localization-api --markdown`, `paradev localization-api --symbol`, `paradev localization-api --index --key` |"
        in result_output
    )
    assert (
        "| `pdx` | 12 | `paradev pdx-api`, `paradev pdx-core-api`, `paradev parse`, `paradev format`, "
        "`paradev pdx-api --markdown`, `paradev pdx-core-api --markdown`, `paradev pdx-api --symbol`, "
        "`paradev pdx-api --index --key`, `paradev pdx-core-api --symbol`, `paradev pdx-core-api --index --key`, "
        "`paradev parse --tokens`, `paradev parse --dump` |"
    ) in result_output
    assert "| `projects` | 17 |" in result_output
    assert (
        "| `inspections` | 5 | `paradev inspections`, `paradev inspections --kind`, "
        "`paradev inspections --index --key`, `paradev inspections --markdown`, `CLI binding: inspections and inspection commands` |"
    ) in result_output
    assert "| `build` | 25 |" in result_output
    assert (
        "| `get_api_catalog_selection` | 3 | `paradev api-catalog`, `paradev api-catalog --reference`, " "`paradev api-catalog --index --key` |"
    ) in result_output
    assert (
        "| `get_surface_contract_selection` | 2 | `paradev architecture --surface-contract`, " "`paradev architecture --surface-contracts` |"
    ) in result_output
    assert (
        "| `get_frontend_api_selection` | 5 | `paradev frontend-api`, `paradev frontend-api --operation`, "
        "`paradev frontend-api --group`, `paradev frontend-api --operation --form`, `paradev frontend-api --index --key` |"
    ) in result_output
    assert (
        "| `get_project_inspection_selection` | 3 | `paradev inspections`, `paradev inspections --kind`, `paradev inspections --index --key` |" in result_output
    )
    assert "| `get_package_api_selection` | 3 | `paradev package-api`, `paradev package-api --symbol`, `paradev package-api --index --key` |" in result_output
    assert "| `get_config_api_selection` | 3 | `paradev config-api`, `paradev config-api --symbol`, `paradev config-api --index --key` |" in result_output
    assert "| `get_gui_api_selection` | 3 | `paradev gui-api`, `paradev gui-api --symbol`, `paradev gui-api --index --key` |" in result_output
    assert "| `get_desktop_api_selection` | 3 | `paradev desktop-api`, `paradev desktop-api --symbol`, `paradev desktop-api --index --key` |" in result_output
    assert "| `render_desktop_typescript` | 1 | `paradev desktop-api --typescript` |" in result_output
    assert "| `get_games_api_selection` | 3 | `paradev games-api`, `paradev games-api --symbol`, `paradev games-api --index --key` |" in result_output
    assert (
        "| `get_surfaces_api_selection` | 3 | `paradev surfaces-api`, `paradev surfaces-api --symbol`, `paradev surfaces-api --index --key` |" in result_output
    )
    assert "| `get_project_api_selection` | 3 | `paradev project-api`, `paradev project-api --symbol`, `paradev project-api --index --key` |" in result_output
    assert (
        "| `get_templates_api_selection` | 3 | `paradev templates-api`, `paradev templates-api --symbol`, `paradev templates-api --index --key` |"
        in result_output
    )
    assert (
        "| `get_copy_roots_api_selection` | 3 | `paradev copy-roots-api`, `paradev copy-roots-api --symbol`, `paradev copy-roots-api --index --key` |"
        in result_output
    )
    assert (
        "| `get_project_facade_api_selection` | 3 | `paradev project-facade-api`, `paradev project-facade-api --symbol`, `paradev project-facade-api --index --key` |"
        in result_output
    )
    assert (
        "| `get_localization_api_selection` | 3 | `paradev localization-api`, `paradev localization-api --symbol`, `paradev localization-api --index --key` |"
        in result_output
    )
    assert "| `get_build_api_selection` | 3 | `paradev build-api`, `paradev build-api --symbol`, `paradev build-api --index --key` |" in result_output
    assert (
        "| `get_pdx_core_api_selection` | 3 | `paradev pdx-core-api`, `paradev pdx-core-api --symbol`, `paradev pdx-core-api --index --key` |" in result_output
    )
    assert (
        "| `get_lsp_server_api_selection` | 3 | `paradev lsp-server-api`, `paradev lsp-server-api --symbol`, `paradev lsp-server-api --index --key` |"
        in result_output
    )
    assert (
        "| `get_rest_facade_api_selection` | 3 | `paradev rest-facade-api`, `paradev rest-facade-api --symbol`, `paradev rest-facade-api --index --key` |"
        in result_output
    )
    assert "| `get_hb_api_selection` | 3 | `paradev hb-api`, `paradev hb-api --symbol`, `paradev hb-api --index --key` |" in result_output
    assert (
        "| `paradev api-catalog` | `command` | `cli` | `api-catalog` | `api-catalog` | `get_api_catalog_selection` | "
        "`reference_id`, `index_name`, `key` | "
        "`reference`, `index`, `key`, `markdown` | `CLI output from get_api_catalog_selection` | `Typer validation errors` |"
    ) in result_output
    assert (
        "| `paradev api-catalog --reference` | `command projection` | `cli` | `api-catalog` | `api-catalog --reference` | "
        "`get_api_catalog_selection` | `reference_id`, `index_name`, `key` | `reference` | "
        "`CLI output from get_api_catalog_selection` | `Typer validation errors` |"
    ) in result_output
    assert (
        "| `paradev api-catalog --index --key` | `command projection` | `cli` | `api-catalog` | `api-catalog --index --key` | "
        "`get_api_catalog_selection` | `reference_id`, `index_name`, `key` | `index`, `key` | "
        "`CLI output from get_api_catalog_selection` | `Typer validation errors` |"
    ) in result_output
    assert (
        "| `paradev architecture --surface-contract` | `command projection` | `cli` | `architecture` | "
        "`architecture --surface-contract` | `get_surface_contract_selection` |  | `surface-contract` | "
        "`CLI output from get_surface_contract_selection` | `Typer validation errors` |"
    ) in result_output
    assert (
        "| `paradev architecture --surface-contracts` | `command projection` | `cli` | `architecture` | "
        "`architecture --surface-contracts` | `get_surface_contract_selection` |  | `surface-contracts` | "
        "`CLI output from get_surface_contract_selection` | `Typer validation errors` |"
    ) in result_output
    standard_api_commands = [
        ("package", "package-api", "get_package_api_selection"),
        ("config", "config-api", "get_config_api_selection"),
        ("gui", "gui-api", "get_gui_api_selection"),
        ("desktop", "desktop-api", "get_desktop_api_selection"),
        ("games", "games-api", "get_games_api_selection"),
        ("surfaces", "surfaces-api", "get_surfaces_api_selection"),
        ("cli", "cli-api", "get_cli_api_selection"),
        ("projects", "project-api", "get_project_api_selection"),
        ("authoring", "templates-api", "get_templates_api_selection"),
        ("copy-roots", "copy-roots-api", "get_copy_roots_api_selection"),
        ("projects", "project-facade-api", "get_project_facade_api_selection"),
        ("localization", "localization-api", "get_localization_api_selection"),
        ("build", "build-api", "get_build_api_selection"),
        ("pdx", "pdx-core-api", "get_pdx_core_api_selection"),
        ("lsp", "lsp-server-api", "get_lsp_server_api_selection"),
        ("rest", "rest-facade-api", "get_rest_facade_api_selection"),
        ("catalog", "hb-api", "get_hb_api_selection"),
    ]
    for feature, command, helper in standard_api_commands:
        assert (
            f"| `paradev {command}` | `command` | `cli` | `{feature}` | `{command}` | `{helper}` | "
            "`symbol`, `index_name`, `key` | `symbol`, `index`, `key`, `markdown` | "
            f"`CLI output from {helper}` | `Typer validation errors` |"
        ) in result_output
    assert (
        "| `paradev package-api --symbol` | `command projection` | `cli` | `package` | "
        "`package-api --symbol` | `get_package_api_selection` | `symbol`, `index_name`, `key` | "
        "`symbol` | `CLI output from get_package_api_selection` | `Typer validation errors` |"
    ) in result_output
    assert (
        "| `paradev cli-api --index --key` | `command projection` | `cli` | `cli` | "
        "`cli-api --index --key` | `get_cli_api_selection` | `symbol`, `index_name`, `key` | "
        "`index`, `key` | `CLI output from get_cli_api_selection` | `Typer validation errors` |"
    ) in result_output


def test_cli_api_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["cli-api", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_inspections_cli_outputs_reference_markdown() -> None:
    result = CliRunner().invoke(build_app(), ["inspections", "--markdown"])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("# Project Inspection Reference\n")
    assert "Generated from `paradev.sdk.get_project_inspection_contract()`." in result.output
    assert "| `modules` | `Project.modules` | `modules` | `profile`, `family`, `module_id`, `collection_id`, `source_slot` |" in result.output
    assert "| `owner_kind` | 1 | `sources` |" in result.output


def test_inspections_cli_outputs_kind_selector_json() -> None:
    result = CliRunner().invoke(build_app(), ["inspections", "--kind", "modules", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["kind"] == "modules"
    assert payload["method"] == "Project.modules"
    assert payload["filters"] == ["profile", "family", "module_id", "collection_id", "source_slot"]


def test_inspections_cli_outputs_filter_index_selector_json() -> None:
    result = CliRunner().invoke(build_app(), ["inspections", "--index", "filter", "--key", "module_id", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert "modules" in payload
    assert "sources" in payload


def test_inspections_cli_rejects_markdown_json_combo() -> None:
    result = CliRunner().invoke(build_app(), ["inspections", "--markdown", "--json"])

    assert result.exit_code != 0
    assert "--markdown cannot be combined with --json" in result.output


def test_inspections_cli_rejects_selector_conflicts() -> None:
    markdown_result = CliRunner().invoke(build_app(), ["inspections", "--markdown", "--kind", "modules"])
    mixed_result = CliRunner().invoke(build_app(), ["inspections", "--kind", "modules", "--index", "filter", "--key", "module_id"])
    incomplete_result = CliRunner().invoke(build_app(), ["inspections", "--index", "filter"])

    assert markdown_result.exit_code != 0
    assert "--markdown cannot be combined with selectors" in markdown_result.output
    assert mixed_result.exit_code != 0
    assert "Pass only one project inspection selector" in mixed_result.output
    assert incomplete_result.exit_code != 0
    assert "--index requires --key" in incomplete_result.output


def test_frontend_api_cli_outputs_sdk_contract_json() -> None:
    result = CliRunner().invoke(build_app(), ["frontend-api", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.sdk.frontend-api.v1"
    assert payload["index"]["group"]["projects"][:4] == ["project.create", "project.find", "project.open", "project.view"]
    assert "module.create" in payload["index"]["group"]["modules"]
    assert "module.metadata.clean" in payload["index"]["group"]["modules"]
    assert "module.metadata.clean" in payload["index"]["workspace_section"]["authoring"]
    assert "pdx.parse" in payload["index"]["status"]["implemented"]
    assert "lsp.diagnostics" in payload["index"]["group"]["lsp"]
    assert payload["index"]["surface"]["unbound"] == ["project.activate"]
    assert payload["index"]["surface"]["lsp"] == [
        "lsp.diagnostics",
        "lsp.symbols",
        "lsp.hover",
        "lsp.formatting",
        "lsp.completion",
        "lsp.semantic_tokens",
    ]
    assert payload["index"]["payload"]["Project.to_view"] == ["project.open", "project.view"]
    assert payload["index"]["payload"]["untyped"][:2] == ["project.config", "project.activate"]
    assert payload["index"]["workspace_section"]["catalog"] == [
        "catalog.preview",
        "catalog.write",
        "catalog.refresh",
        "catalog.query",
    ]
    assert payload["index"]["group"]["ai"] == ["ai.profiles", "ai.profile.write", "ai.profile.reset", "ai.chat"]
    assert payload["index"]["workspace_section"]["ai-chat"] == ["ai.profiles", "ai.profile.write", "ai.profile.reset", "ai.chat"]
    assert payload["index"]["payload"]["paradev.desktop.ai-chat-profiles.v1"] == ["ai.profiles", "ai.profile.write", "ai.profile.reset"]
    assert payload["index"]["payload"]["paradev.desktop.ai-chat.v1"] == ["ai.chat"]
    assert payload["index"]["group"]["build"][:6] == ["build.plan", "build.emit", "build.start", "build.runs", "build.status", "build.interrupt"]
    assert payload["index"]["workspace_section"]["build"][:6] == [
        "build.plan",
        "build.emit",
        "build.start",
        "build.runs",
        "build.status",
        "build.interrupt",
    ]
    assert payload["index"]["payload"]["paradev.desktop.build-runs.v1"] == ["build.runs"]
    assert payload["index"]["payload"]["paradev.desktop.build-run.v1"] == ["build.start", "build.status", "build.interrupt"]
    assert payload["summary"]["surface_counts"] == {
        "operation_count": 98,
        "sdk": 97,
        "cli": 74,
        "rest": 92,
        "mcp": 60,
        "lsp": 6,
        "unbound": 1,
    }


def test_frontend_api_cli_outputs_reference_markdown() -> None:
    result = CliRunner().invoke(build_app(), ["frontend-api", "--markdown"])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("# Frontend API Reference\n")
    assert "Generated from `paradev.sdk.get_frontend_api_contract()`." in result.output
    assert "由 `paradev.sdk.get_frontend_api_contract()` 生成。" in result.output
    assert "### Index Catalog / Index 目录" in result.output
    assert "### Surface Index / Surface 索引" in result.output
    assert "### Surface Coverage / Surface 覆盖" in result.output
    assert "### REST Route Index / REST Route 索引" in result.output
    assert "### REST Request Planner Index / REST Request Planner 索引" in result.output
    assert "### Workspace Section REST Summary Index / Workspace Section REST Summary 索引" in result.output
    assert "### Group REST Summary Index / Group REST Summary 索引" in result.output
    assert "### REST Static Query Index / REST Static Query 索引" in result.output
    assert "### REST Dynamic Query Field Index / REST Dynamic Query Field 索引" in result.output
    assert "### REST Path Parameter Index / REST Path Parameter 索引" in result.output
    assert "### REST Body Field Index / REST Body Field 索引" in result.output
    assert "### SDK Call Index / SDK Call 索引" in result.output
    assert "### SDK Call Input Index / SDK Call Input 索引" in result.output
    assert "### MCP Tool Index / MCP Tool 索引" in result.output
    assert "### MCP Tool Input Index / MCP Tool Input 索引" in result.output
    assert "### CLI Command Index / CLI Command 索引" in result.output
    assert "### CLI Command Input Index / CLI Command Input 索引" in result.output
    assert "### LSP Method Index / LSP Method 索引" in result.output
    assert "### LSP Method Input Index / LSP Method Input 索引" in result.output
    assert "### Binding Index / Binding 索引" in result.output
    assert "### Group Binding Summary Index / Group Binding Summary 索引" in result.output
    assert "### Payload Index / Payload 索引" in result.output
    assert "### Workspace Section Index / Workspace Section 索引" in result.output
    assert "### Workspace Section Mode Status Index / Workspace Section Mode Status 索引" in result.output
    assert "### Group Mode Status Index / Group Mode Status 索引" in result.output
    assert "### Workspace Section Payload Coverage Index / Workspace Section Payload Coverage 索引" in result.output
    assert "### Group Payload Coverage Index / Group Payload Coverage 索引" in result.output
    assert "### Workspace Section Surface Coverage Index / Workspace Section Surface Coverage 索引" in result.output
    assert "### Workspace Section Binding Summary Index / Workspace Section Binding Summary 索引" in result.output
    assert "### Workspace Section Form Summary Index / Workspace Section Form Summary 索引" in result.output
    assert "### Workspace Section Control Summary Index / Workspace Section Control Summary 索引" in result.output
    assert "### Group Control Summary Index / Group Control Summary 索引" in result.output
    assert "### Workspace Section Option Source Summary Index / Workspace Section Option Source Summary 索引" in result.output
    assert "### Workspace Section Input Target Summary Index / Workspace Section Input Target Summary 索引" in result.output
    assert "### Group Input Target Summary Index / Group Input Target Summary 索引" in result.output
    assert "### Workspace Section Validation Summary Index / Workspace Section Validation Summary 索引" in result.output
    assert "### Group Validation Summary Index / Group Validation Summary 索引" in result.output
    assert "### Workspace Section Default Summary Index / Workspace Section Default Summary 索引" in result.output
    assert "### Group Default Summary Index / Group Default Summary 索引" in result.output
    assert "### Workspace Section Required Summary Index / Workspace Section Required Summary 索引" in result.output
    assert "### Group Required Summary Index / Group Required Summary 索引" in result.output
    assert "### Workspace Section Alias Summary Index / Workspace Section Alias Summary 索引" in result.output
    assert "### Group Alias Summary Index / Group Alias Summary 索引" in result.output
    assert "### Group Execution Summary Index / Group Execution Summary 索引" in result.output
    assert "### Workspace Section Execution Summary Index / Workspace Section Execution Summary 索引" in result.output
    assert "### Workspace Action Execution Index / Workspace Action Execution 索引" in result.output
    assert "### Group Confirmation Summary Index / Group Confirmation Summary 索引" in result.output
    assert "### Workspace Section Confirmation Summary Index / Workspace Section Confirmation Summary 索引" in result.output
    assert "### Confirmation Index / Confirmation 索引" in result.output
    assert "### Group Option Source Summary Index / Group Option Source Summary 索引" in result.output
    assert "### Option Source Index / Option Source 索引" in result.output
    assert "### Option Provider Index / Option Provider 索引" in result.output
    assert "### Input Field Index / Input Field 索引" in result.output
    assert "### Group Form Summary Index / Group Form Summary 索引" in result.output
    assert "### Operation Form Summary Index / Operation Form Summary 索引" in result.output
    assert "### Form Control Index / Form Control 索引" in result.output
    assert "### Required Input Index / Required Input 索引" in result.output
    assert "### Input Default Index / Input Default 索引" in result.output
    assert "### Input Constraint Index / Input Constraint 索引" in result.output
    assert "### Input Target Index / Input Target 索引" in result.output
    assert "### Input Alias Index / Input Alias 索引" in result.output
    assert "| `projects` | 15 | 14 | 12 | 13 | 9 | 0 | 1 |" in result.output
    assert "| `lsp` | 7 | 7 | 1 | 7 | 0 | 6 | 0 |" in result.output
    assert "| `projects` | 15 | 9 | 6 | 14 | 0 | 1 |" in result.output
    assert "| `surfaces` | 12 | 12 | 0 | 12 | 0 | 0 |" in result.output
    assert (
        '| `binding` | `contract["index"]["binding"][surface][key]` | `get_frontend_api_binding_operation_ids(surface, key)` | `getFrontendApiBindingOperationIds(surface, key)` | Surface call key to operation ids. |'
        in result.output
    )
    assert "| `lsp` | 6 | `lsp.diagnostics`, `lsp.symbols`, `lsp.hover`, `lsp.formatting`, `lsp.completion`, `lsp.semantic_tokens` |" in result.output
    assert "| `unbound` | 1 | `project.activate` |" in result.output
    assert "| `GET` | `/projects` |  | 2 | `project.open`, `project.view` |" in result.output
    assert "| `GET` | `/projects/inspect` | `kind=modules` | 1 | `module.list` |" in result.output
    assert "| `POST` | `/projects/build` | `emit_artifacts=true&emit_manifests=true` |  |  | `build.emit` |" in result.output
    assert (
        "| `build` | 18 | 18 | 18 | `GET:14`, `POST:4` | `emit_artifacts=true`, `emit_manifests=true`, `kind=artifacts`, `kind=assets`, `kind=build-explain`, `kind=build-graph`, `kind=dependencies`, `kind=diagnostics`, `kind=families`, `kind=localization`, `kind=manifests`, `kind=source-map`, `kind=sprites`, `kind=summary` |  | `mode`, `parallelism`, `profile`, `project_root`, `run_id`, `strict_metadata`, `target` | `artifact_path`, `artifact_type`, `code`, `collection_id`, `collection_source_slot`, `diagnostic_code`, `edge_kind`, `emit_artifacts`, `emit_manifests`, `family`, `file_format`, `key`, `key_prefix`, `kind`, `language`, `mode`, `module_id`, `name`, `owner`, `path`, `profile`, `project_root`, `published`, `route`, `run_id`, `severity`, `slot`, `source`, `source_path`, `source_slot`, `sprite_slot`, `strict_metadata`, `target`, `target_root` |"
        in result.output
    )
    assert (
        "| `surface-contracts` | 12 | 8 | 8 | `GET:5`, `POST:3` |  |  | `values` | `binding_key`, `binding_surface`, `field_name`, `form`, `group_id`, `operation_id` |"
        in result.output
    )
    assert (
        "| `surfaces` | 12 | 8 | 8 | `GET:5`, `POST:3` |  |  | `values` | `binding_key`, `binding_surface`, `field_name`, `form`, `group_id`, `operation_id` |"
        in result.output
    )
    assert (
        "| `projects` | 15 | 12 | 2 | `Project inspection payload:1`, `Project.to_view:2`, `paradev.desktop.state.v1:1`, `paradev.project.create.v1:1`, `paradev.project.find.v1:1`, `paradev.project.preferred-language.v1:1`, `paradev.project.rename.v1:1`, `paradev.rest.draft_apply.v1:1`, `paradev.rest.source_text.v1:1`, `paradev.sdk.project-browser.v1:1`, `paradev.sdk.projects.v1:1`, `paradev.source-form.v1:1` |"
        in result.output
    )
    assert (
        "| `surfaces` | 12 | 7 | 5 | `paradev.sdk.frontend-api.action-detail.v1:1`, `paradev.sdk.frontend-api.binding-lookup.v1:1`, `paradev.sdk.frontend-api.inputs.v1:1`, `paradev.sdk.frontend-api.options.v1:1`, `paradev.sdk.frontend-api.rest-request.v1:1`, `paradev.sdk.frontend-api.v1:1`, `paradev.sdk.frontend-api.workspace.v1:1` |"
        in result.output
    )
    assert "| `kind` | `modules` | `module.list` | `GET` | `/projects/inspect` | `string` |" in result.output
    assert "| `emit_artifacts` | `true` | `build.emit` | `POST` | `/projects/build` | `boolean` |" in result.output
    assert "| `path` | `project.create` | `POST` | `/projects` | `path` | `path` | yes | `parameters` |  |" in result.output
    assert "| `emit_artifacts` | `build.emit` | `POST` | `/projects/build` | `emit_artifacts` | `boolean` | no | `parameters` | `true` |" in result.output
    assert (
        "| `POST` | `/projects/{project_id}/drafts/apply` |  | `project_id` | `module_rename`, `project_root`, `source_edits`, `source_removals`, `source_replacements` | `project.draft_apply` |"
        in result.output
    )
    assert "| `Project.build` | 2 | `build.plan`, `build.emit` |" in result.output
    assert "| `project_id` | `project.source_text` | `GET` | `/projects/{project_id}/sources` | `project_id` | `string` | yes | `parameters` |" in result.output
    assert (
        "| `family_id` | `module.draft` | `POST` | `/projects/{project_id}/modules/{family_id}/drafts` | `family_id` | `string` | yes | `parameters` |"
        in result.output
    )
    assert (
        "| `project_root` | `module.draft` | `POST` | `/projects/{project_id}/modules/{family_id}/drafts` | `path` | `path` | no | `project` |" in result.output
    )
    assert "| `text` | `lsp.hover` | `POST` | `/lsp/hover` | `text` | `text` | yes | `parameters` |" in result.output
    assert "| `get_frontend_api_selection` | 1 | `surface.frontend_api` |" in result.output
    assert "| `project_authoring_path` | 2 | `module.authoring_path`, `collection.authoring_path` |" in result.output
    assert "| `Project.create` | `project.create` | `path` | `path` | yes |  | `parameters` |  |" in result.output
    assert "| `Project.create` | `project.create` | `game` | `string` | no | `hoi4` | `parameters` |  |" in result.output
    assert "| `Project.inspect('modules')` | `module.list` | `profile` | `string` | no |  | `parameters` |  |" in result.output
    assert "| `project_create` | `project.create` | `path` | `path` | yes |  | `parameters` |  |" in result.output
    assert "| `project_create` | `project.create` | `game` | `string` | no | `hoi4` | `parameters` |  |" in result.output
    assert "| `project_inspect` | `module.list` | `profile` | `string` | no |  | `parameters` |  |" in result.output
    assert "| `frontend_api` | 1 | `surface.frontend_api` |" in result.output
    assert "| `frontend-api --binding-surface --binding-key` | 1 | `surface.frontend_api.binding_lookup` |" in result.output
    assert "| `new` | `project.create` | `path` | `path` | yes |  | `parameters` |  |" in result.output
    assert "| `new` | `project.create` | `game` | `string` | no | `hoi4` | `parameters` |  |" in result.output
    assert "| `modules` | `module.list` | `profile` | `string` | no |  | `parameters` |  |" in result.output
    assert "| `source-slots` | 2 | `module.source_slots`, `collection.source_slots` |" in result.output
    assert "| `textDocument/hover` | 1 | `lsp.hover` |" in result.output
    assert "| `textDocument/publishDiagnostics` | 1 | `lsp.diagnostics` |" in result.output
    assert "| `textDocument/hover` | `lsp.hover` | `line` | `integer` | yes |  | `parameters` |  |" in result.output
    assert "| `textDocument/completion` | `lsp.completion` | `limit` | `integer` | no | `100` | `parameters` |  |" in result.output
    assert "| `rest` | `GET /projects/inspect?kind=modules` | 1 | `module.list` |" in result.output
    assert (
        "| `surfaces` | 12 | 12 | `get_architecture_spec`, `get_cli_contract`, `get_frontend_api_action`, `get_frontend_api_binding_lookup`, `get_frontend_api_selection`, `get_frontend_api_workspace`, `get_lsp_contract`, `get_mcp_contract`, `get_openapi_seed`, `normalize_frontend_api_inputs`, `plan_frontend_api_rest_request`, `resolve_frontend_api_options` | `architecture`, `frontend-api`, `frontend-api --binding-surface --binding-key`, `frontend-api --operation --action`, `frontend-api --operation --option-field --values-json`, `frontend-api --operation --values-json`, `frontend-api --operation --values-json --rest-request`, `frontend-api --workspace` |"
        in result.output
    )
    assert "| `Project.to_view` | 2 | `project.open`, `project.view` |" in result.output
    assert "| `catalog` | 4 | `catalog.preview` | `catalog.preview`, `catalog.write`, `catalog.refresh`, `catalog.query` |" in result.output
    assert "| `source-editor` | 16 | 11 | 5 | 16 | 0 | 0 |" in result.output
    assert "| `build` | 18 | 15 | 3 | 18 | 0 | 0 |" in result.output
    assert "| `catalog` | 4 | 2 | 2 | 4 | 0 | 0 |" in result.output
    assert (
        "| `project-browser` | 9 | 6 | 0 | `paradev.build.collections.v1:2`, `paradev.build.explain.v1:1`, `paradev.build.modules.v1:1`, `paradev.build.source-slots.v1:2`, `paradev.build.sources.v1:2`, `paradev.sdk.project-browser.v1:1` |"
        in result.output
    )
    assert "| `surfaces` | 12 | 12 | `adapter:12` | `rest:8`, `sdk:4` | `cli:8`, `mcp:2`, `rest:8`, `sdk:12` | 6 | 0 |  | 6 | 8 |" in result.output
    assert "| `catalog` | 4 | 4 | 2 | `catalog:2` | `write:2` |  | `catalog.write`, `catalog.refresh` |" in result.output
    assert (
        "| `projects` | 15 | 5 | 3 | 4 | `build.families`, `collection.list`, `module.list`, `module.sources` | `collections`, `families`, `modules`, `sources` | `path` |"
        in result.output
    )
    assert (
        "| `surfaces` | 12 | 13 | 7 | `parameters:3`, `projections:1`, `selectors:9` | `values` |  | `binding_key`, `binding_surface`, `field_name`, `group_id`, `operation_id` | `form` |  |"
        in result.output
    )
    assert "| `lsp` | 7 | 30 | 6 | 0 | 6 | `lsp.completion`, `lsp.hover` |  | `character`, `limit`, `line`, `offset` |" in result.output
    assert "| `surfaces` | 12 | 13 | 1 | 1 | 0 | `surface.frontend_api.binding_lookup` | `binding_surface` |  |" in result.output
    assert (
        "| `catalog` | 4 | 17 | 7 | 0 | `catalog.preview`, `catalog.query`, `catalog.refresh`, `catalog.write` | "
        '`include_data`, `limit`, `offset`, `path` | `include_data=false`, `limit=100`, `offset=0`, `path="."` |' in result.output
    )
    assert (
        "| `surfaces` | 12 | 13 | 4 | 0 | `surface.frontend_api`, `surface.frontend_api.normalize`, `surface.frontend_api.options`, `surface.frontend_api.rest_request` | `form`, `values` | `form=false`, `values={}` |"
        in result.output
    )
    assert (
        "| `modules` | 20 | 121 | 27 | `module.activity.set`, `module.authoring_path`, `module.authoring_plan`, `module.collection.set`, `module.create`, `module.create_batch`, `module.diagram`, `module.diagram.edit`, `module.draft`, `module.duplicate`, `module.edit`, `module.file`, `module.remove`, `module.rename`, `module.view` | `active`, `family`, `family_id`, `module_id`, `modules`, `object_id`, `project_id`, `relative_path`, `target_id`, `template_id`, `text` | `parameters:27` | `build.families`, `module.list`, `module.sources`, `module.templates` |  |"
        in result.output
    )
    assert (
        "| `surfaces` | 12 | 13 | 7 | `surface.frontend_api.action`, `surface.frontend_api.binding_lookup`, `surface.frontend_api.normalize`, `surface.frontend_api.options`, `surface.frontend_api.rest_request` | `binding_key`, `binding_surface`, `field_name`, `operation_id` | `selectors:7` |  |  |"
        in result.output
    )
    assert (
        "| `projects` | 15 | 46 | 5 | `project.draft_apply`, `project.source_form`, `project.source_text` | `path`, `source_path` | `parameters` | `module.sources` | `path->project_root`, `source_path->path` |"
        in result.output
    )
    assert "| `build` | 18 | 104 | 1 | `build.artifacts` | `artifact_path` | `parameters` | `build.artifacts` | `artifact_path->path` |" in result.output
    assert "| `catalog` | 4 | 2 | 2 | `paradev.hb.catalog-preview.v1:1`, `paradev.hb.catalog-query.v1:1` |" in result.output
    assert "| `authoring` | 21 | 21 | 18 | 21 | 20 | 0 | 0 | 0 | `rest:21` |" in result.output
    assert "| `build` | 18 | 18 | 14 | 18 | 12 | 0 | 0 | 0 | `rest:18` |" in result.output
    assert "| `catalog` | 4 | 4 | 4 | 4 | 2 | 0 | 0 | 0 | `rest:4` |" in result.output
    assert (
        "| `surface-contracts` | 12 | 12 | `get_architecture_spec`, `get_cli_contract`, `get_frontend_api_action`, `get_frontend_api_binding_lookup`, `get_frontend_api_selection`, `get_frontend_api_workspace`, `get_lsp_contract`, `get_mcp_contract`, `get_openapi_seed`, `normalize_frontend_api_inputs`, `plan_frontend_api_rest_request`, `resolve_frontend_api_options` | `architecture`, `frontend-api`, `frontend-api --binding-surface --binding-key`, `frontend-api --operation --action`, `frontend-api --operation --option-field --values-json`, `frontend-api --operation --values-json`, `frontend-api --operation --values-json --rest-request`, `frontend-api --workspace` | `GET /architecture`, `GET /frontend-api`, `GET /frontend-api/action`, `GET /frontend-api/binding`, `GET /frontend-api/workspace`, `POST /frontend-api/normalize`, `POST /frontend-api/options`, `POST /frontend-api/rest-request` | `frontend_api`, `list_surfaces` |  |  |"
        in result.output
    )
    assert (
        "| `authoring` | Authoring | 21 | 131 | 37 | 45 | 8 | 40 | 7 | `checkbox:17`, `combobox:40`, `json:11`, `number:2`, `path:21`, `select:7`, `text:33` |"
        in result.output
    )
    assert (
        "| `build` | Build | 18 | 104 | 3 | 18 | 1 | 33 | 10 | `checkbox:7`, `combobox:33`, `json:1`, `number:1`, `path:16`, `select:7`, `text:39` |"
        in result.output
    )
    assert "| `catalog` | Catalog | 4 | 17 | 0 | 7 | 0 | 0 | 2 | `checkbox:1`, `number:2`, `path:7`, `text:7` |" in result.output
    assert (
        "| `projects` | 15 | 46 | 7 | 5 | 3 | `checkbox:2`, `combobox:5`, `json:8`, `path:12`, `select:3`, `text:15`, `textarea:1` | `collection_id`, `family`, `module_id`, `source_path` | `kind`, `preferred_language` | `text` |"
        in result.output
    )
    assert (
        "| `build` | 18 | 104 | 7 | 33 | 7 | `checkbox:7`, `combobox:33`, `json:1`, `number:1`, `path:16`, `select:7`, `text:39` | `artifact_path`, `artifact_type`, `code`, `collection_id`, `diagnostic_code`, `family`, `module_id`, `source_path` | `mode`, `severity`, `target_root` |  |"
        in result.output
    )
    assert "| `catalog` | 4 | 17 | 4 | 0 | 0 | `checkbox:1`, `number:2`, `path:7`, `text:7` |  |  |  |" in result.output
    assert (
        "| `build` | 18 | 33 | 10 | 6 | `build.artifacts`, `build.diagnostics`, `build.families`, `collection.list`, `module.list`, `module.sources` | `artifacts`, `collections`, `diagnostics`, `families`, `modules`, `sources` | `path` | `artifact_type`, `collection_id`, `family`, `loader`, `mode`, `module_id`, `owner`, `path`, `profile`, `severity`, `slot`, `source_path`, `status`, `strict_metadata`, `target_root` |  |"
        in result.output
    )
    assert "| `catalog` | 4 | 0 | 0 | 0 |  |  |  |  |  |" in result.output
    assert (
        "| `build` | 18 | 104 | 3 | `parameters:90`, `project:14` | `artifact_path`, `artifact_type`, `code`, `collection_id`, `collection_source_slot`, `diagnostic_code`, `edge_kind`, `emit_artifacts`, `emit_manifests`, `family`, `file_format`, `key`, `key_prefix`, `kind`, `language`, `mode`, `module_id`, `name`, `owner`, `parallelism`, `profile`, `project_root`, `published`, `route`, `run_id`, `severity`, `slot`, `source`, `source_path`, `source_slot`, `sprite_slot`, `strict_metadata`, `target`, `target_root` | `path` |  |  | `artifact_path->path` |"
        in result.output
    )
    assert (
        "| `catalog` | 4 | 17 | 0 | `parameters:13`, `project:4` | `database`, `entity`, `include_data`, `limit`, `name`, `offset`, `profile`, `tag`, `target_id` | `path` |  |  |  |"
        in result.output
    )
    assert (
        "| `surface-contracts` | 12 | 13 | 7 | `parameters:3`, `projections:1`, `selectors:9` | `values` |  | `binding_key`, `binding_surface`, `field_name`, `group_id`, `operation_id` | `form` |  |"
        in result.output
    )
    assert (
        "| `build` | 18 | 104 | 8 | 7 | 1 | `build.artifacts`, `build.diagnostics`, `build.explain`, `build.graph`, `build.source_map`, `build.start` | `mode`, `severity`, `target_root` | `parallelism` |"
        in result.output
    )
    assert "| `catalog` | 4 | 17 | 2 | 0 | 2 | `catalog.query` |  | `limit`, `offset` |" in result.output
    assert "| `surface-contracts` | 12 | 13 | 1 | 1 | 0 | `surface.frontend_api.binding_lookup` | `binding_surface` |  |" in result.output
    assert (
        '| `build` | 18 | 104 | 18 | 0 | `build.artifacts`, `build.assets`, `build.dependencies`, `build.diagnostics`, `build.emit`, `build.explain`, `build.families`, `build.graph`, `build.localization`, `build.manifests`, `build.plan`, `build.source_map`, `build.sprites`, `build.start`, `build.summary` | `emit_artifacts`, `emit_manifests`, `mode`, `path`, `published` | `emit_artifacts=false`, `emit_manifests=false`, `mode="cached"`, `path="."`, `published=false` |'
        in result.output
    )
    assert (
        "| `catalog` | 4 | 17 | 7 | 0 | `catalog.preview`, `catalog.query`, `catalog.refresh`, `catalog.write` | "
        '`include_data`, `limit`, `offset`, `path` | `include_data=false`, `limit=100`, `offset=0`, `path="."` |' in result.output
    )
    assert "| `build` | 18 | 104 | 3 | `build.interrupt`, `build.start`, `build.status` | `project_root`, `run_id` | `parameters:3` |  |  |" in result.output
    assert "| `catalog` | 4 | 17 | 0 |  |  |  |  |  |" in result.output
    assert "| `build` | 18 | 104 | 1 | `build.artifacts` | `artifact_path` | `parameters` | `build.artifacts` | `artifact_path->path` |" in result.output
    assert "| `catalog` | 4 | 17 | 0 |  |  |  |  |  |" in result.output
    assert (
        "| `surface-contracts` | 12 | 13 | 7 | `surface.frontend_api.action`, `surface.frontend_api.binding_lookup`, `surface.frontend_api.normalize`, `surface.frontend_api.options`, `surface.frontend_api.rest_request` | `binding_key`, `binding_surface`, `field_name`, `operation_id` | `selectors:7` |  |  |"
        in result.output
    )
    assert (
        "| `project-switcher` | 8 | 8 | `adapter:7`, `frontend-local:1` | `frontend-local:1`, `rest:7` | `cli:7`, `mcp:5`, `rest:7`, `sdk:7` | 8 | 3 | `workspace:1` | 8 | 7 |"
        in result.output
    )
    assert "| `source-editor` | 16 | 16 | `adapter:16` | `rest:16` | `cli:8`, `lsp:6`, `mcp:7`, `rest:16`, `sdk:16` | 16 | 5 |  | 16 | 16 |" in result.output
    assert (
        "| `project-switcher` | `project.state` | `adapter` | `rest` | `sdk`, `cli`, `rest` | yes |  | `paradev.sdk.frontend-api.inputs.v1` | `paradev.sdk.frontend-api.rest-request.v1` |"
        in result.output
    )
    assert (
        "| `project-switcher` | `project.activate` | `frontend-local` | `frontend-local` |  | yes | `workspace` | `paradev.sdk.frontend-api.inputs.v1` |  |"
        in result.output
    )
    assert (
        "| `build` | 18 | 3 | `project-files:3` | `write:3` | `emit_artifacts:1`, `emit_manifests:1` | `build.emit`, `build.start`, `build.interrupt` |"
        in result.output
    )
    assert "| `catalog` | 4 | 2 | `catalog:2` | `write:2` |  | `catalog.write`, `catalog.refresh` |" in result.output
    assert "| `project-switcher` | `project-files` | `write` | `force` | `project.create` | Confirm Project Create |" in result.output
    assert "| `authoring` | `project-files` | `destructive` | `write` | `module.remove` | Confirm Module Remove |" in result.output
    assert "| `build` | `project-files` | `write` | `emit_artifacts`, `emit_manifests` | `build.emit` | Confirm Build Emit |" in result.output
    assert "| `build` | `project-files` | `write` |  | `build.start` | Confirm Build Start |" in result.output
    assert "| `build` | `project-files` | `write` |  | `build.interrupt` | Confirm Build Interrupt |" in result.output
    assert "| `module.create` | `template_id` | `templates` | `module.templates` | `path` | `path` | `authoring_ready=true` |" in result.output
    assert (
        "| `collection.sources` | 2 | `collection.file.relative_path`, `collection.edit.relative_path` | `collection.edit`, `collection.file` | `sources` | `collection_id`, `path` | `collection_id`, `family`, `loader`, `path`, `profile`, `slot`, `status` |  |"
        in result.output
    )
    assert "| `module.templates` | 25 |" in result.output
    assert "`authoring_ready=true` |" in result.output
    assert (
        "| `build.explain` | `artifact_path` | `artifacts` | `build.artifacts` | `path` | `path`, `profile`, `artifact_type`, `target_root`, `owner`, `mode`, `module_id`, `collection_id` |  |"
        in result.output
    )
    assert "| `template_id` | `module.create` | `string` | yes |  |  |  | `module.templates` |" in result.output
    assert "| `artifact_path` | `build.artifacts` | `path` | no |  |  | `path` | `build.artifacts` |" in result.output
    assert "| `line` | `lsp.hover` | `integer` | yes |  |  |  |  |" in result.output
    assert (
        "| `modules` | Modules | 20 | 121 | 27 | 40 | 7 | 45 | 6 | `checkbox:14`, `combobox:45`, `json:6`, `path:20`, `select:6`, `text:29`, `textarea:1` |"
        in result.output
    )
    assert (
        "| `build` | Build | 18 | 104 | 3 | 18 | 1 | 33 | 10 | `checkbox:7`, `combobox:33`, `json:1`, `number:1`, `path:16`, `select:7`, `text:39` |"
        in result.output
    )
    assert "| `project.create` | 5 | 1 | 2 | 0 | 0 | 0 | `checkbox`, `path`, `text` |" in result.output
    assert "| `build.artifacts` | 9 | 0 | 1 | 1 | 4 | 1 | `combobox`, `path`, `select`, `text` |" in result.output
    assert "| `build.start` | 6 | 1 | 1 | 0 | 0 | 2 | `checkbox`, `json`, `number`, `path`, `select`, `text` |" in result.output
    assert "| `build.status` | 1 | 1 | 0 | 0 | 0 | 1 | `text` |" in result.output
    assert "| `build.interrupt` | 1 | 1 | 0 | 0 | 0 | 1 | `text` |" in result.output
    assert "| `template_id` | `module.create` | `combobox` | `string` | yes | `module.templates` |  |" in result.output
    assert "| `kind` | `project.browser` | `select` | `string` | no |  | `module`, `collection` |" in result.output
    assert "| `text` | `module.edit` | `textarea` | `text` | yes |  |  |" in result.output
    assert "| `line` | `lsp.hover` | `number` | `integer` | yes |  |  |" in result.output
    assert "| `project_root` | `build.start` | `path` | `path` | yes |  |  |" in result.output
    assert "| `mode` | `build.start` | `select` | `string` | no |  | `cached`, `full` |" in result.output
    assert "| `parallelism` | `build.start` | `number` | `integer` | no |  |  |" in result.output
    assert "| `template_id` | `module.create` | `string` | `parameters` |  | `module.templates` |" in result.output
    assert "| `source_path` | `project.source_text` | `path` | `parameters` | `path` | `module.sources` |" in result.output
    assert "| `operation_id` | `surface.frontend_api.action` | `string` | `selectors` |  |  |" in result.output
    assert "| `force` | `project.create` | `boolean` | `false` | `parameters` |  | no |" in result.output
    assert "| `path` | `project.source_text` | `path` | `.` | `parameters` | `project_root` | no |" in result.output
    assert "| `form` | `surface.frontend_api` | `boolean` | `false` | `projections` |  | no |" in result.output
    assert "| `target_root` | `build.artifacts` | `string` | `output`, `build` |  |  | no | no |" in result.output
    assert "| `line` | `lsp.hover` | `integer` |  | `0` |  | no | yes |" in result.output
    assert "| `project` | `path` | `module.create` |  | `path` | no |" in result.output
    assert "| `selectors` | `operation_id` | `surface.frontend_api` |  | `string` | no |" in result.output
    assert "| `projections` | `form` | `surface.frontend_api` |  | `boolean` | no |" in result.output
    assert "| `source_path` | `project.source_text` | `path` | `parameters` | `path` | yes | `module.sources` |" in result.output
    assert "| `artifact_path` | `build.artifacts` | `path` | `parameters` | `path` | no | `build.artifacts` |" in result.output
    assert (
        "| `project.create` | `projects` | `implemented` | `write` | `Project.create` | `new` | `POST /projects` | `project_create` |  | `path`, `project_id`, `title`, `game`, `force` | `paradev.project.create.v1` | Create a starter project. |"
        in result.output
    )
    assert (
        "| `lsp.hover` | `lsp` | `implemented` | `read` | `hover_pdx_lsp_text` |  | `POST /lsp/hover` |  | `textDocument/hover` | `text`, `line`, `character`, `uri`, `path` | `paradev.lsp.hover.v1` | Return hover details for a document position. |"
        in result.output
    )

    conflicting = CliRunner().invoke(build_app(), ["frontend-api", "--markdown", "--json"])

    assert conflicting.exit_code != 0
    assert "--markdown cannot be combined" in conflicting.output


def test_frontend_api_cli_outputs_sdk_cli_reference_markdown() -> None:
    result = CliRunner().invoke(build_app(), ["frontend-api", "--sdk-cli-markdown"])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("# SDK And CLI API Reference\n")
    assert "Generated from `paradev.sdk.get_frontend_api_contract()`." in result.output
    assert "本页是面向 HoI4 Mod 作者和自动化脚本的紧凑入口表。" in result.output
    assert "## Feature Summary / 功能汇总" in result.output
    assert "| `modules` | Modules | 20 | 20 | 19 | 9 | 11 |" in result.output
    assert "| `localization` | Localization | 2 | 2 | 0 | 2 | 0 |" in result.output
    assert "| `lsp` | LSP | 7 | 7 | 1 | 6 | 1 |" in result.output
    assert (
        "| `project.create` | `projects` | `write` | `Project.create` | `new` | `path`, `project_id`, `title`, `game`, `force` | Create a starter project. |"
        in result.output
    )
    assert (
        "| `lsp.hover` | `lsp` | `read` | `hover_pdx_lsp_text` |  | `text`, `line`, `character`, `uri`, `path` | Return hover details for a document position. |"
        in result.output
    )

    conflicting = CliRunner().invoke(build_app(), ["frontend-api", "--sdk-cli-markdown", "--json"])

    assert conflicting.exit_code != 0
    assert "--sdk-cli-markdown cannot be combined" in conflicting.output


def test_frontend_api_cli_outputs_typescript_contract() -> None:
    result = CliRunner().invoke(build_app(), ["frontend-api", "--typescript"])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("/* Generated by `rtk uv run paradev frontend-api --typescript`; do not edit by hand. */")
    assert 'export const PARADEV_FRONTEND_API_SCHEMA = "paradev.sdk.frontend-api.v1" as const;' in result.output
    assert "export type ParaDevFrontendApiOperationId = (typeof PARADEV_FRONTEND_API_OPERATION_IDS)[number];" in result.output
    assert "export const PARADEV_FRONTEND_API_CONTRACT = " in result.output
    assert '"project.create",' in result.output
    assert '"module.create",' in result.output
    assert '"pdx.format",' in result.output
    assert '"lsp.hover",' in result.output

    conflicting = CliRunner().invoke(build_app(), ["frontend-api", "--typescript", "--json"])

    assert conflicting.exit_code != 0
    assert "--typescript cannot be combined" in conflicting.output


def test_desktop_api_cli_outputs_typescript_config_keys() -> None:
    result = CliRunner().invoke(build_app(), ["desktop-api", "--typescript"])

    assert result.exit_code == 0, result.output
    assert result.output == Path("apps/desktop/src/generated/desktopContract.ts").read_text(encoding="utf-8")
    assert result.output.startswith("/* Generated by `rtk uv run paradev desktop-api --typescript`; do not edit by hand. */")
    assert "export type DesktopConfigKey = (typeof PARADEV_DESKTOP_CONFIG_KEYS)[number];" in result.output
    assert "export const PARADEV_DESKTOP_OPEN_PATH_TARGETS = " in result.output
    assert "export const PARADEV_DESKTOP_OPEN_PATH_DEFAULT_TARGETS = " in result.output

    conflicting = CliRunner().invoke(build_app(), ["desktop-api", "--typescript", "--json"])

    assert conflicting.exit_code != 0
    assert "--typescript cannot be combined" in conflicting.output


def test_lsp_diagnostics_cli_outputs_lsp_payload() -> None:
    result = CliRunner().invoke(build_app(), ["lsp", "diagnostics", "--text", "value = 0x", "--uri", "file:///broken.pdx", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.lsp.diagnostics.v1"
    assert payload["uri"] == "file:///broken.pdx"
    assert payload["ok"] is False
    assert payload["diagnostics"][0]["range"]["start"] == {"line": 0, "character": 8}


def test_lsp_formatting_cli_reads_text_file(tmp_path: Path) -> None:
    source = tmp_path / "focus.pdx"
    source.write_text("focus = { id = GER_test }", encoding="utf-8")

    result = CliRunner().invoke(build_app(), ["lsp", "formatting", "--text-file", str(source), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.lsp.formatting.v1"
    assert payload["path"] == str(source)
    assert payload["ok"] is True
    assert payload["edits"][0]["newText"].startswith("focus = {")


def test_lsp_completion_cli_reads_project_catalog(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    catalog_write(Project.load(project_root))

    result = CliRunner().invoke(
        build_app(),
        [
            "lsp",
            "completion",
            "--text",
            "focus = {\n\tid = GER\n}\n",
            "--line",
            "1",
            "--character",
            "9",
            "--project",
            str(project_root),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.lsp.completion.v1"
    assert payload["prefix"] == "GER"
    assert "GER_sample" in [item["label"] for item in payload["items"]]


def test_lsp_keywords_cli_uses_configured_game_root_when_omitted(tmp_path: Path, cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.hoi4.game_root", default=None)
    game_root = tmp_path / "configured-game"
    documentation = game_root / "documentation"
    documentation.mkdir(parents=True)
    (documentation / "modifiers_documentation.md").write_text(
        "# Modifiers\n\n" "## Modifiers for scope country\n\n" "* [cfg_cli_factor](#cfg_cli_factor)\n",
        encoding="utf-8",
    )

    try:
        CM_PARADEV.set("paradev.hoi4.game_root", f"  {game_root}  ")

        result = CliRunner().invoke(build_app(), ["lsp", "keywords", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        modifier_names = [row["name"] for row in payload["rows"] if row["kind"] == "modifier"]
        assert payload["game_root"] == str(game_root)
        assert "cfg_cli_factor" in modifier_names
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous)


def test_lsp_completion_cli_uses_configured_game_root_when_omitted(tmp_path: Path, cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.hoi4.game_root", default=None)
    game_root = tmp_path / "configured-game"
    documentation = game_root / "documentation"
    documentation.mkdir(parents=True)
    (documentation / "modifiers_documentation.md").write_text(
        "# Modifiers\n\n" "## Modifiers for scope country\n\n" "* [cfg_cli_completion_factor](#cfg_cli_completion_factor)\n",
        encoding="utf-8",
    )

    try:
        CM_PARADEV.set("paradev.hoi4.game_root", f"  {game_root}  ")

        result = CliRunner().invoke(
            build_app(),
            [
                "lsp",
                "completion",
                "--text",
                "idea = {\n\tmodifier = {\n\t\tcfg",
                "--line",
                "2",
                "--character",
                "5",
                "--path",
                "common/ideas/sample.txt",
                "--json",
            ],
        )

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert "cfg_cli_completion_factor" in [item["label"] for item in payload["items"]]
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous)


def test_lsp_semantic_tokens_cli_outputs_highlight_ranges() -> None:
    result = CliRunner().invoke(build_app(), ["lsp", "semantic-tokens", "--text", "focus = {\n\tid = GER_test\n}\n", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.lsp.semantic-tokens.v1"
    assert payload["method"] == "textDocument/semanticTokens/full"
    assert payload["tokens"][0] == {"line": 0, "character": 0, "length": 5, "token_type": "class", "token_modifiers": []}


def test_frontend_api_cli_outputs_selected_operation_and_group_json() -> None:
    operation = CliRunner().invoke(build_app(), ["frontend-api", "--operation", "module.list", "--json"])

    assert operation.exit_code == 0, operation.output
    operation_payload = json.loads(operation.output)
    assert operation_payload["id"] == "module.list"
    assert operation_payload["rest"] == "GET /projects/inspect?kind=modules"

    group = CliRunner().invoke(build_app(), ["frontend-api", "--group", "modules", "--json"])

    assert group.exit_code == 0, group.output
    group_payload = json.loads(group.output)
    assert group_payload["schema"] == "paradev.sdk.frontend-api.v1"
    assert group_payload["group"]["id"] == "modules"
    assert group_payload["operation_ids"][0] == "module.list"
    assert "module.edit" in group_payload["index"]["status"]["implemented"]

    conflicting = CliRunner().invoke(build_app(), ["frontend-api", "--operation", "module.list", "--group", "modules", "--json"])

    assert conflicting.exit_code != 0
    assert "Pass only one frontend API selector" in conflicting.output

    unknown = CliRunner().invoke(build_app(), ["frontend-api", "--operation", "nope", "--json"])

    assert unknown.exit_code != 0
    assert "Unknown frontend API operation: nope" in unknown.output
    assert "Traceback" not in unknown.output


def test_frontend_api_cli_outputs_index_lookup_json() -> None:
    result = CliRunner().invoke(build_app(), ["frontend-api", "--index", "workspace_section", "--key", "catalog", "--json"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == [
        "catalog.preview",
        "catalog.write",
        "catalog.refresh",
        "catalog.query",
    ]

    incomplete = CliRunner().invoke(build_app(), ["frontend-api", "--index", "mode", "--json"])

    assert incomplete.exit_code != 0
    assert "--index requires --key" in incomplete.output

    conflicting = CliRunner().invoke(build_app(), ["frontend-api", "--index", "mode", "--key", "write", "--group", "modules", "--json"])

    assert conflicting.exit_code != 0
    assert "--index cannot be combined" in conflicting.output


def test_frontend_api_cli_outputs_binding_lookup_json() -> None:
    binding = CliRunner().invoke(
        build_app(),
        ["frontend-api", "--binding-surface", "rest", "--binding-key", "GET /projects/inspect?kind=modules", "--json"],
    )

    assert binding.exit_code == 0, binding.output
    payload = json.loads(binding.output)
    assert payload == {
        "schema": "paradev.sdk.frontend-api.binding-lookup.v1",
        "surface": "rest",
        "key": "GET /projects/inspect?kind=modules",
        "operation_ids": ["module.list"],
        "count": 1,
    }

    missing = CliRunner().invoke(build_app(), ["frontend-api", "--binding-surface", "rest", "--binding-key", "GET /missing", "--json"])

    assert missing.exit_code == 0, missing.output
    assert json.loads(missing.output)["operation_ids"] == []

    incomplete = CliRunner().invoke(build_app(), ["frontend-api", "--binding-surface", "rest", "--json"])

    assert incomplete.exit_code != 0
    assert "--binding-surface requires --binding-key" in incomplete.output

    conflicting = CliRunner().invoke(
        build_app(),
        ["frontend-api", "--binding-surface", "cli", "--binding-key", "project", "--operation", "project.open", "--json"],
    )

    assert conflicting.exit_code != 0
    assert "--binding-surface cannot be combined" in conflicting.output


def test_frontend_api_cli_outputs_operation_form_contract_json() -> None:
    result = CliRunner().invoke(build_app(), ["frontend-api", "--operation", "module.edit", "--form", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.sdk.frontend-api.form.v1"
    assert payload["operation_id"] == "module.edit"
    assert payload["required"] == ["module_id", "relative_path", "text"]
    assert payload["defaults"] == {"path": ".", "create": False, "encoding": "utf-8"}
    assert payload["fields"][3]["name"] == "text"
    assert payload["fields"][3]["label"] == "Text"
    assert "source file" in payload["fields"][3]["description"]
    assert payload["fields"][3]["control"] == "textarea"

    module_create = CliRunner().invoke(build_app(), ["frontend-api", "--operation", "module.create", "--form", "--json"])

    assert module_create.exit_code == 0, module_create.output
    module_create_payload = json.loads(module_create.output)
    module_create_fields = {field["name"]: field for field in module_create_payload["fields"]}
    assert module_create_fields["template_id"]["control"] == "combobox"
    assert module_create_fields["template_id"]["option_source"]["operation_id"] == "module.templates"
    assert module_create_fields["source_root"]["option_source"]["values_path"] == ["source_roots"]

    missing_operation = CliRunner().invoke(build_app(), ["frontend-api", "--form", "--json"])

    assert missing_operation.exit_code != 0
    assert "--form requires --operation" in missing_operation.output

    group_form = CliRunner().invoke(build_app(), ["frontend-api", "--group", "modules", "--form", "--json"])

    assert group_form.exit_code != 0
    assert "--form requires --operation" in group_form.output


def test_frontend_api_cli_outputs_workspace_projection_json() -> None:
    result = CliRunner().invoke(build_app(), ["frontend-api", "--workspace", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.sdk.frontend-api.workspace.v1"
    assert payload["sections"][0]["id"] == "project-switcher"
    assert payload["sections"][0]["default_operation_id"] == "project.state"
    assert "module.edit" in payload["index"]["section"]["source-editor"]
    assert payload["index"]["operation_id"]["pdx.format"] == ["source-editor"]
    source_editor = next(section for section in payload["sections"] if section["id"] == "source-editor")
    module_edit = next(action for action in source_editor["actions"] if action["operation_id"] == "module.edit")
    assert module_edit["schema"] == "paradev.sdk.frontend-api.action.v1"
    assert module_edit["execution"]["default_surface"] == "rest"
    assert module_edit["execution"]["binding"] == {"method": "PATCH", "path": "/projects/modules/file", "query": {}}
    assert module_edit["form_schema"] == "paradev.sdk.frontend-api.form.v1"

    conflicting = CliRunner().invoke(build_app(), ["frontend-api", "--workspace", "--operation", "module.edit", "--json"])

    assert conflicting.exit_code != 0
    assert "--workspace cannot be combined" in conflicting.output


def test_frontend_api_cli_outputs_action_detail_json() -> None:
    result = CliRunner().invoke(build_app(), ["frontend-api", "--operation", "module.create", "--action", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.sdk.frontend-api.action-detail.v1"
    assert payload["operation_id"] == "module.create"
    assert payload["sections"] == ["authoring"]
    assert payload["form"]["required"] == ["template_id", "object_id"]
    assert payload["option_fields"] == ["template_id", "source_root"]

    missing_operation = CliRunner().invoke(build_app(), ["frontend-api", "--action", "--json"])

    assert missing_operation.exit_code != 0
    assert "--action requires --operation" in missing_operation.output


def test_frontend_api_cli_normalizes_operation_values_json() -> None:
    result = CliRunner().invoke(
        build_app(),
        [
            "frontend-api",
            "--operation",
            "build.artifacts",
            "--values-json",
            '{"path":"/workspace/mod","artifact_path":"common/modifiers/test.txt","module_id":"modifier/test"}',
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.sdk.frontend-api.inputs.v1"
    assert payload["project"] == {"path": "/workspace/mod"}
    assert payload["parameters"] == {"path": "common/modifiers/test.txt", "module_id": "modifier/test"}
    assert payload["aliases"] == {"artifact_path": "path"}

    missing_operation = CliRunner().invoke(build_app(), ["frontend-api", "--values-json", "{}", "--json"])

    assert missing_operation.exit_code != 0
    assert "--values-json requires --operation" in missing_operation.output
    assert "with --group or --form" in missing_operation.output

    not_object = CliRunner().invoke(build_app(), ["frontend-api", "--operation", "module.edit", "--values-json", "[]", "--json"])

    assert not_object.exit_code != 0
    assert "--values-json must be a JSON object" in not_object.output

    invalid_choice = CliRunner().invoke(
        build_app(),
        ["frontend-api", "--operation", "project.browser", "--values-json", '{"kind":"asset"}', "--json"],
    )

    assert invalid_choice.exit_code != 0
    assert "project.browser" in invalid_choice.output
    assert "one of module, collection" in invalid_choice.output


def test_frontend_api_cli_plans_operation_rest_request_json() -> None:
    result = CliRunner().invoke(
        build_app(),
        [
            "frontend-api",
            "--operation",
            "module.edit",
            "--values-json",
            '{"path":"/workspace/mod","module_id":"modifier/test","relative_path":"def.pdx","text":"modifier = { value = 1 }"}',
            "--rest-request",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.sdk.frontend-api.rest-request.v1"
    assert payload["method"] == "PATCH"
    assert payload["path"] == "/projects/modules/file"
    assert payload["query"]["path"] == "/workspace/mod"
    assert payload["query"]["module_id"] == "modifier/test"
    assert payload["body"] == {"text": "modifier = { value = 1 }"}

    catalog = CliRunner().invoke(
        build_app(),
        [
            "frontend-api",
            "--operation",
            "catalog.write",
            "--values-json",
            '{"path":"/workspace/mod","database":"/workspace/mod/.paradev/.cache/hb/catalog.sqlite"}',
            "--rest-request",
            "--json",
        ],
    )

    assert catalog.exit_code == 0, catalog.output
    catalog_payload = json.loads(catalog.output)
    assert catalog_payload["method"] == "POST"
    assert catalog_payload["path"] == "/projects/catalog"
    assert catalog_payload["query"] == {"path": "/workspace/mod", "database": "/workspace/mod/.paradev/.cache/hb/catalog.sqlite"}
    assert catalog_payload["body"] == {}

    build = CliRunner().invoke(
        build_app(),
        [
            "frontend-api",
            "--operation",
            "build.plan",
            "--values-json",
            '{"path":"/workspace/mod","strict_metadata":true}',
            "--rest-request",
            "--json",
        ],
    )

    assert build.exit_code == 0, build.output
    build_payload = json.loads(build.output)
    assert build_payload["method"] == "POST"
    assert build_payload["path"] == "/projects/build"
    assert build_payload["query"] == {"path": "/workspace/mod", "strict_metadata": True}
    assert build_payload["body"] == {}

    missing_values = CliRunner().invoke(build_app(), ["frontend-api", "--operation", "module.edit", "--rest-request", "--json"])

    assert missing_values.exit_code != 0
    assert "--rest-request requires --operation and --values-json" in missing_values.output


def test_frontend_api_cli_resolves_option_source_rows() -> None:
    project_path = "demos/assets/projects/minimal"

    result = CliRunner().invoke(
        build_app(),
        [
            "frontend-api",
            "--operation",
            "module.create",
            "--option-field",
            "template_id",
            "--values-json",
            f'{{"path":"{project_path}"}}',
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.sdk.frontend-api.options.v1"
    assert payload["operation_id"] == "module.create"
    assert payload["field_name"] == "template_id"
    assert payload["provider_operation_id"] == "module.templates"
    assert payload["options"][0]["value"] == "hoi4:idea/basic"

    missing_operation = CliRunner().invoke(build_app(), ["frontend-api", "--option-field", "template_id", "--json"])

    assert missing_operation.exit_code != 0
    assert "--option-field requires --operation" in missing_operation.output


def test_new_creates_buildable_starter_project(tmp_path: Path) -> None:
    project_root = tmp_path / "starter-mod"

    result = CliRunner().invoke(build_app(), ["new", str(project_root), "--title", "Starter Mod", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.project.create.v1"
    assert payload["project"]["project_id"] == "starter_mod"
    assert payload["starter_module"] == "modifier/starter_mod_starter_modifier"
    project = Project.load(project_root)
    build = project.build(emit_artifacts=True, emit_manifests=True)

    assert build.blocked is False
    assert (project_root / "paradev.yaml").is_file()
    assert (project_root / "src/modules/modifier/starter_mod_starter_modifier/def.txt").is_file()
    assert (project.output_root / "descriptor.mod").is_file()
    assert (project.build_root / "launcher/starter_mod.mod").is_file()
    assert (project.output_root / "common/modifiers/starter_mod_starter_modifier.txt").is_file()
    assert (project.output_root / "localisation/english/starter_mod_starter_modifier_l_english.yml").is_file()
    assert (project.build_root / "summary.json").is_file()


def test_project_rename_cli_updates_manifest_title(tmp_path: Path) -> None:
    project_root = tmp_path / "starter-mod"
    Project.create(project_root, title="Starter Mod")

    result = CliRunner().invoke(build_app(), ["project-rename", str(project_root), "Renamed Starter", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.project.rename.v1"
    assert payload["previous_title"] == "Starter Mod"
    assert payload["project"]["title"] == "Renamed Starter"
    assert Project.load(project_root).title == "Renamed Starter"


def test_project_language_cli_plans_then_applies_exact_manifest_update(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "starter-mod"
    Project.create(project_root, title="Starter Mod")
    runner = CliRunner()

    planned = runner.invoke(
        build_app(),
        ["project-language", str(project_root), "zh", "--json"],
    )
    assert planned.exit_code == 0, planned.output
    plan = json.loads(planned.output)
    assert plan["preferred_language"] == "zh"
    assert plan["written"] is False

    applied = runner.invoke(
        build_app(),
        [
            "project-language",
            str(project_root),
            "zh",
            "--write",
            "--plan-hash",
            plan["plan_hash"],
            "--json",
        ],
    )
    assert applied.exit_code == 0, applied.output
    payload = json.loads(applied.output)
    assert payload["blocked"] is False
    assert payload["written"] is True
    assert Project.load(project_root).preferred_language == "zh"


def test_project_find_cli_reports_found_and_missing_projects(tmp_path: Path) -> None:
    project_root = tmp_path / "starter-mod"
    Project.create(project_root, title="Starter Mod")

    found = CliRunner().invoke(build_app(), ["project-find", str(project_root / "src"), "--json"])

    assert found.exit_code == 0, found.output
    found_payload = json.loads(found.output)
    assert found_payload["schema"] == "paradev.project.find.v1"
    assert found_payload["found"] is True
    assert found_payload["project"]["project_id"] == "starter_mod"

    missing_root = tmp_path / "missing"
    missing_root.mkdir()
    missing = CliRunner().invoke(build_app(), ["project-find", str(missing_root), "--json"])

    assert missing.exit_code == 1, missing.output
    missing_payload = json.loads(missing.output)
    assert missing_payload["found"] is False
    assert missing_payload["diagnostics"][0]["code"] == "project.manifest_missing"


def test_projects_cli_lists_explicit_and_searched_projects(tmp_path: Path) -> None:
    explicit = Project.create(tmp_path / "explicit-mod", title="Explicit Mod")
    Project.create(tmp_path / "workspace/searched-mod", title="Searched Mod")

    result = CliRunner().invoke(
        build_app(),
        ["projects", "--project", str(explicit.root / "src"), "--root", str(tmp_path / "workspace"), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.sdk.projects.v1"
    assert [row["project_id"] for row in payload["projects"]] == ["explicit_mod", "searched_mod"]
    assert payload["diagnostics"] == []


def test_desktop_state_cli_returns_active_project_view(tmp_path: Path) -> None:
    active = Project.create(tmp_path / "active-mod", title="Active Mod")
    Project.create(tmp_path / "known-mod", title="Known Mod")

    result = CliRunner().invoke(
        build_app(),
        ["desktop-state", "--project", str(active.root / "src"), "--root", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.desktop.state.v1"
    assert payload["active_project"]["project_id"] == "active_mod"
    assert payload["active_view"]["title"] == "Active Mod"
    assert payload["browser"]["schema"] == "paradev.sdk.project-browser.v1"
    assert payload["templates"]["schema"] == "paradev.sdk.templates.v1"
    assert {row["project_id"] for row in payload["projects"]} == {"active_mod", "known_mod"}


def test_module_rename_cli_moves_source_module(tmp_path: Path) -> None:
    project_root = tmp_path / "starter-mod"
    Project.create(project_root, title="Starter Mod")

    result = CliRunner().invoke(
        build_app(),
        [
            "module-rename",
            str(project_root),
            "modifier/starter_mod_starter_modifier",
            "starter_mod_renamed_modifier",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.module.rename.v1"
    assert payload["previous_module_id"] == "modifier/starter_mod_starter_modifier"
    assert payload["module_id"] == "modifier/starter_mod_renamed_modifier"
    assert payload["content_rewritten"] is False
    assert not (project_root / "src/modules/modifier/starter_mod_starter_modifier").exists()
    assert (project_root / "src/modules/modifier/starter_mod_renamed_modifier/def.txt").is_file()


def test_module_rename_cli_synchronizes_readable_folder_title(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "starter-mod"
    Project.create(project_root, title="Starter Mod")

    result = CliRunner().invoke(
        build_app(),
        [
            "module-rename",
            str(project_root),
            "modifier/starter_mod_starter_modifier",
            "starter_mod_starter_modifier",
            "--title",
            "Friendly Modifier",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["module_id"] == "modifier/starter_mod_starter_modifier"
    assert payload["relative_path"].endswith("starter_mod_starter_modifier - Friendly Modifier")


def test_module_file_and_edit_cli_read_and_write_source_text(tmp_path: Path) -> None:
    project_root = tmp_path / "starter-mod"
    Project.create(project_root, title="Starter Mod")

    read = CliRunner().invoke(
        build_app(),
        [
            "module-file",
            str(project_root),
            "modifier/starter_mod_starter_modifier",
            "def.txt",
            "--json",
        ],
    )

    assert read.exit_code == 0, read.output
    read_payload = json.loads(read.output)
    assert read_payload["schema"] == "paradev.module.file.v1"
    assert read_payload["module_relative_path"] == "def.txt"
    assert "stability_factor" in read_payload["text"]

    text = "starter_mod_starter_modifier = {\n\tstability_factor = 0.10\n}\n"
    write = CliRunner().invoke(
        build_app(),
        [
            "module-edit",
            str(project_root),
            "modifier/starter_mod_starter_modifier",
            "def.txt",
            "--text",
            text,
            "--json",
        ],
    )

    assert write.exit_code == 0, write.output
    write_payload = json.loads(write.output)
    assert write_payload["written"] is True
    assert write_payload["text"] == text
    assert (project_root / "src/modules/modifier/starter_mod_starter_modifier/def.txt").read_text(encoding="utf-8") == text


def test_collection_file_and_edit_cli_read_and_write_descriptor_text(tmp_path: Path) -> None:
    project_root = tmp_path / "collection-project"
    collection_root = project_root / "src/collections/bulletin/germany"
    module_root = project_root / "src/modules/bulletin/GER_news"
    collection_root.mkdir(parents=True)
    module_root.mkdir(parents=True)
    (collection_root / "category.txt").write_text("add_namespace = germany", encoding="utf-8")
    (module_root / "meta.yaml").write_text("type: bulletin\ncollection: germany\n", encoding="utf-8")
    (module_root / "body.txt").write_text("news = { id = germany.1 }", encoding="utf-8")
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: collection_project",
                "title: Collection Project",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "families:",
                "  bulletin:",
                "    kind: collection_source",
                "    source_slots:",
                "      - name: body",
                "        match: body.txt",
                "        kind: pdx",
                "    collection_source_slots:",
                "      - name: category",
                "        match: category.txt",
                "        kind: pdx",
                "    templates:",
                "      pdx: events/{collection_id}.txt",
            ]
        ),
        encoding="utf-8",
    )

    read = CliRunner().invoke(build_app(), ["collection-file", str(project_root), "germany", "category.txt", "--json"])

    assert read.exit_code == 0, read.output
    read_payload = json.loads(read.output)
    assert read_payload["schema"] == "paradev.collection.file.v1"
    assert read_payload["collection_relative_path"] == "category.txt"
    assert read_payload["text"] == "add_namespace = germany"

    text = "add_namespace = germany_news\n"
    write = CliRunner().invoke(
        build_app(),
        ["collection-edit", str(project_root), "germany", "category.txt", "--text", text, "--json"],
    )

    assert write.exit_code == 0, write.output
    write_payload = json.loads(write.output)
    assert write_payload["written"] is True
    assert write_payload["text"] == text
    assert (collection_root / "category.txt").read_text(encoding="utf-8") == text


def test_collection_rename_cli_moves_descriptor_and_rewrites_member_metadata(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "collection-project"
    collection_root = project_root / "src/collections/bulletin/germany"
    module_root = project_root / "src/modules/bulletin/GER_news"
    collection_root.mkdir(parents=True)
    module_root.mkdir(parents=True)
    (collection_root / "category.txt").write_text("add_namespace = germany", encoding="utf-8")
    (module_root / "meta.yaml").write_text(
        "type: bulletin\ncollection: germany\n",
        encoding="utf-8",
    )
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: collection_project",
                "title: Collection Project",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "families:",
                "  bulletin:",
                "    kind: collection_source",
                "    collection_source_slots:",
                "      - name: category",
                "        match: category.txt",
                "        kind: pdx",
                "    templates:",
                "      pdx: events/{collection_id}.txt",
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "collection-rename",
            str(project_root),
            "germany",
            "france",
            "--family",
            "bulletin",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.collection.rename.v1"
    assert payload["previous_collection_id"] == "germany"
    assert payload["collection_id"] == "france"
    assert payload["content_rewritten"] is True
    assert payload["members"] == ["bulletin/GER_news"]
    assert not collection_root.exists()
    assert (project_root / "src/collections/bulletin/france/category.txt").read_text(encoding="utf-8") == "add_namespace = germany"
    assert (module_root / "meta.yaml").read_text(encoding="utf-8") == ("type: bulletin\ncollection: france\n")


def test_collection_remove_cli_plans_and_removes_descriptor(tmp_path: Path) -> None:
    project_root = tmp_path / "collection-project"
    collection_root = project_root / "src/collections/bulletin/germany"
    collection_root.mkdir(parents=True)
    (collection_root / "category.txt").write_text("add_namespace = germany", encoding="utf-8")
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: collection_project",
                "title: Collection Project",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "families:",
                "  bulletin:",
                "    kind: collection_source",
                "    collection_source_slots:",
                "      - name: category",
                "        match: category.txt",
                "        kind: pdx",
                "    templates:",
                "      pdx: events/{collection_id}.txt",
            ]
        ),
        encoding="utf-8",
    )

    dry = CliRunner().invoke(
        build_app(),
        [
            "collection-remove",
            str(project_root),
            "germany",
            "--family",
            "bulletin",
            "--json",
        ],
    )

    assert dry.exit_code == 0, dry.output
    dry_payload = json.loads(dry.output)
    assert dry_payload["schema"] == "paradev.collection.remove.v1"
    assert dry_payload["removed"] is False
    assert dry_payload["blocked"] is False
    assert collection_root.is_dir()

    write = CliRunner().invoke(
        build_app(),
        [
            "collection-remove",
            str(project_root),
            "germany",
            "--family",
            "bulletin",
            "--write",
            "--plan-hash",
            dry_payload["plan_hash"],
            "--json",
        ],
    )

    assert write.exit_code == 0, write.output
    write_payload = json.loads(write.output)
    assert write_payload["removed"] is True
    assert not collection_root.exists()


def test_module_remove_cli_plans_and_removes_source_module(tmp_path: Path) -> None:
    project_root = tmp_path / "starter-mod"
    Project.create(project_root, title="Starter Mod")
    module_root = project_root / "src/modules/modifier/starter_mod_starter_modifier"

    dry = CliRunner().invoke(
        build_app(),
        [
            "module-remove",
            str(project_root),
            "modifier/starter_mod_starter_modifier",
            "--json",
        ],
    )

    assert dry.exit_code == 0, dry.output
    dry_payload = json.loads(dry.output)
    assert dry_payload["schema"] == "paradev.module.remove.v1"
    assert dry_payload["removed"] is False
    assert dry_payload["blocked"] is False
    assert module_root.is_dir()

    write = CliRunner().invoke(
        build_app(),
        [
            "module-remove",
            str(project_root),
            "modifier/starter_mod_starter_modifier",
            "--write",
            "--json",
        ],
    )

    assert write.exit_code == 0, write.output
    write_payload = json.loads(write.output)
    assert write_payload["removed"] is True
    assert not module_root.exists()


@pytest.mark.skipif(os.name != "posix", reason="Descriptor-anchored duplicate publication is POSIX-only.")
def test_module_duplicate_cli_plans_and_applies_exact_hash(tmp_path: Path) -> None:
    project_root = tmp_path / "starter-mod"
    Project.create(project_root, title="Starter Mod")
    destination = project_root / "src/modules/modifier/starter_mod_copied_modifier"

    dry = CliRunner().invoke(
        build_app(),
        [
            "module-duplicate",
            str(project_root),
            "modifier/starter_mod_starter_modifier",
            "starter_mod_copied_modifier",
            "--json",
        ],
    )

    assert dry.exit_code == 0, dry.output
    dry_payload = json.loads(dry.output)
    assert dry_payload["schema"] == "paradev.sdk.module_duplicate.v1"
    assert dry_payload["status"] == "planned"
    assert dry_payload["applied"] is False
    assert not destination.exists()

    write = CliRunner().invoke(
        build_app(),
        [
            "module-duplicate",
            str(project_root),
            "modifier/starter_mod_starter_modifier",
            "starter_mod_copied_modifier",
            "--write",
            "--plan-hash",
            dry_payload["plan_hash"],
            "--json",
        ],
    )

    assert write.exit_code == 0, write.output
    write_payload = json.loads(write.output)
    assert write_payload["status"] == "duplicated"
    assert write_payload["identity_mode"] == "rewrite"
    assert write_payload["content_rewritten"] is True
    assert destination.is_dir()


def test_module_collection_set_cli_forwards_plan_apply_and_clear(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter-mod", title="Starter Mod")
    calls: list[dict[str, object]] = []

    def update_collection(
        self: Project,
        module_id: str,
        collection_id: str | None,
        *,
        source_root: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        calls.append(
            {
                "module_id": module_id,
                "collection_id": collection_id,
                "source_root": source_root,
                "write": write,
                "plan_hash": plan_hash,
            }
        )
        return {
            "schema": "paradev.sdk.module_collection_update.v1",
            "applied": write,
            "blocked": False,
            "plan_hash": "reviewed-plan",
        }

    monkeypatch.setattr(Project, "set_module_collection", update_collection)
    runner = CliRunner()
    planned = runner.invoke(
        build_app(),
        [
            "module-collection-set",
            str(project.root),
            "modifier/starter_mod_starter_modifier",
            "--collection",
            "starter_modifiers",
            "--source-root",
            "src",
            "--json",
        ],
    )
    applied = runner.invoke(
        build_app(),
        [
            "module-collection-set",
            str(project.root),
            "modifier/starter_mod_starter_modifier",
            "--write",
            "--plan-hash",
            "reviewed-plan",
            "--json",
        ],
    )

    assert planned.exit_code == 0, planned.output
    assert applied.exit_code == 0, applied.output
    assert json.loads(planned.output)["applied"] is False
    assert json.loads(applied.output)["applied"] is True
    assert calls == [
        {
            "module_id": "modifier/starter_mod_starter_modifier",
            "collection_id": "starter_modifiers",
            "source_root": "src",
            "write": False,
            "plan_hash": None,
        },
        {
            "module_id": "modifier/starter_mod_starter_modifier",
            "collection_id": None,
            "source_root": None,
            "write": True,
            "plan_hash": "reviewed-plan",
        },
    ]


def test_module_activity_set_cli_forwards_plan_and_exact_hash_apply(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter-mod", title="Starter Mod")
    calls: list[dict[str, object]] = []

    def update_activity(
        self: Project,
        module_id: str,
        active: bool,
        *,
        source_root: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        calls.append(
            {
                "module_id": module_id,
                "active": active,
                "source_root": source_root,
                "write": write,
                "plan_hash": plan_hash,
            }
        )
        return {
            "schema": "paradev.sdk.module_activity_update.v1",
            "applied": write,
            "blocked": False,
            "plan_hash": "reviewed-plan",
        }

    monkeypatch.setattr(Project, "set_module_active", update_activity)
    runner = CliRunner()
    planned = runner.invoke(
        build_app(),
        [
            "module-activity-set",
            str(project.root),
            "modifier/starter_mod_starter_modifier",
            "--inactive",
            "--source-root",
            "src",
            "--json",
        ],
    )
    applied = runner.invoke(
        build_app(),
        [
            "module-activity-set",
            str(project.root),
            "modifier/starter_mod_starter_modifier",
            "--active",
            "--write",
            "--plan-hash",
            "reviewed-plan",
            "--json",
        ],
    )

    assert planned.exit_code == 0, planned.output
    assert applied.exit_code == 0, applied.output
    assert json.loads(planned.output)["applied"] is False
    assert json.loads(applied.output)["applied"] is True
    assert calls == [
        {
            "module_id": "modifier/starter_mod_starter_modifier",
            "active": False,
            "source_root": "src",
            "write": False,
            "plan_hash": None,
        },
        {
            "module_id": "modifier/starter_mod_starter_modifier",
            "active": True,
            "source_root": None,
            "write": True,
            "plan_hash": "reviewed-plan",
        },
    ]


def test_module_metadata_clean_cli_defaults_to_plan_and_forwards_exact_hash(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter-mod", title="Starter Mod")
    calls: list[dict[str, object]] = []

    def clean_module_metadata(
        self: Project,
        *,
        family: str | None = None,
        module_id: str | None = None,
        source_root: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        calls.append(
            {
                "family": family,
                "module_id": module_id,
                "source_root": source_root,
                "write": write,
                "plan_hash": plan_hash,
            }
        )
        return {
            "schema": "paradev.sdk.module_metadata_cleanup.v1",
            "applied": write,
            "blocked": False,
            "plan_hash": "reviewed-plan",
        }

    monkeypatch.setattr(Project, "clean_module_metadata", clean_module_metadata)
    runner = CliRunner()
    dry = runner.invoke(
        build_app(),
        [
            "module-metadata-clean",
            str(project.root),
            "--family",
            "idea",
            "--module",
            "idea/sample",
            "--source-root",
            "src",
            "--json",
        ],
    )
    applied = runner.invoke(
        build_app(),
        [
            "module-metadata-clean",
            str(project.root),
            "--family",
            "idea",
            "--write",
            "--plan-hash",
            "reviewed-plan",
            "--json",
        ],
    )

    assert dry.exit_code == 0, dry.output
    assert applied.exit_code == 0, applied.output
    assert json.loads(dry.output)["applied"] is False
    assert json.loads(applied.output)["applied"] is True
    assert calls == [
        {
            "family": "idea",
            "module_id": "idea/sample",
            "source_root": "src",
            "write": False,
            "plan_hash": None,
        },
        {
            "family": "idea",
            "module_id": None,
            "source_root": None,
            "write": True,
            "plan_hash": "reviewed-plan",
        },
    ]


def test_module_metadata_clean_cli_applies_reviewed_cleanup_plan(
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "starter-mod", title="Starter Mod")
    metadata_path = project.root / "src/modules/modifier/starter_mod_starter_modifier/meta.yaml"
    metadata_path.write_text(
        "type: modifier\ntitle: Starter Modifier\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    dry = runner.invoke(
        build_app(),
        [
            "module-metadata-clean",
            str(project.root),
            "--module",
            "modifier/starter_mod_starter_modifier",
            "--json",
        ],
    )

    assert dry.exit_code == 0, dry.output
    plan = json.loads(dry.output)
    assert plan["status"] == "planned"
    assert plan["counts"]["changed"] == 1
    assert metadata_path.read_text(encoding="utf-8").startswith("type: modifier\n")

    missing_hash = runner.invoke(
        build_app(),
        [
            "module-metadata-clean",
            str(project.root),
            "--module",
            "modifier/starter_mod_starter_modifier",
            "--write",
            "--json",
        ],
    )

    assert missing_hash.exit_code != 0
    missing_payload = json.loads(missing_hash.output)
    assert missing_payload["status"] == "blocked"
    assert missing_payload["blocked"] is True
    assert missing_payload["applied"] is False
    assert metadata_path.read_text(encoding="utf-8").startswith("type: modifier\n")

    applied = runner.invoke(
        build_app(),
        [
            "module-metadata-clean",
            str(project.root),
            "--module",
            "modifier/starter_mod_starter_modifier",
            "--write",
            "--plan-hash",
            plan["plan_hash"],
            "--json",
        ],
    )

    assert applied.exit_code == 0, applied.output
    payload = json.loads(applied.output)
    assert payload["status"] == "cleaned"
    assert payload["applied"] is True
    assert payload["written"] is True
    assert metadata_path.read_text(encoding="utf-8") == "title: Starter Modifier\n"


def test_collection_create_cli_plans_and_writes_descriptor(tmp_path: Path) -> None:
    project_root = tmp_path / "collection-project"
    (project_root / "src").mkdir(parents=True)
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: collection_project",
                "title: Collection Project",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "families:",
                "  bulletin:",
                "    kind: collection_source",
                "    collection_source_slots:",
                "      - name: category",
                "        match: category.txt",
                "        kind: pdx",
                "    templates:",
                "      pdx: events/{collection_id}.txt",
            ]
        ),
        encoding="utf-8",
    )

    dry = CliRunner().invoke(
        build_app(),
        [
            "collection-create",
            str(project_root),
            "bulletin",
            "france",
            "--metadata",
            "title=France Bulletin",
            "--json",
        ],
    )

    assert dry.exit_code == 0, dry.output
    dry_payload = json.loads(dry.output)
    assert dry_payload["schema"] == "paradev.collection.create.v1"
    assert dry_payload["blocked"] is False
    assert dry_payload["written"] is False
    assert dry_payload["metadata"] == {"title": "France Bulletin"}
    assert not (project_root / "src/collections/bulletin/france/meta.yaml").exists()

    write = CliRunner().invoke(
        build_app(),
        [
            "collection-create",
            str(project_root),
            "bulletin",
            "france",
            "--metadata",
            "title=France Bulletin",
            "--write",
            "--json",
        ],
    )

    assert write.exit_code == 0, write.output
    write_payload = json.loads(write.output)
    assert write_payload["written"] is True
    assert (project_root / "src/collections/bulletin/france/meta.yaml").read_text(encoding="utf-8") == "title: France Bulletin\n"


def test_sources_cli_filters_collection_descriptor_owner_kind(tmp_path: Path) -> None:
    project_root = tmp_path / "collection-sources-project"
    collection_root = project_root / "src/collections/bulletin/germany"
    module_root = project_root / "src/modules/bulletin/GER_news"
    collection_root.mkdir(parents=True)
    module_root.mkdir(parents=True)
    (collection_root / "strings.yml").write_text("en:\n  germany: Germany Events\n", encoding="utf-8")
    (module_root / "body.txt").write_text("bulletin = { id = germany.1 }", encoding="utf-8")
    (module_root / "meta.yaml").write_text("type: bulletin\ncollection: germany\n", encoding="utf-8")
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: collection_sources_project",
                "title: Collection Sources Project",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "families:",
                "  bulletin:",
                "    kind: collection_source",
                "    source_slots:",
                "      - name: body",
                "        match: body.txt",
                "        kind: pdx",
                "    collection_source_slots:",
                "      - name: strings",
                "        match: strings.yml",
                "        kind: loc",
                "    templates:",
                "      pdx: events/{collection_id}.txt",
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "sources",
            str(project_root),
            "--collection",
            "germany",
            "--owner-kind",
            "collection",
            "--loader",
            "loc",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.build.sources.v1"
    assert payload["sources"] == [
        {
            "owner_kind": "collection",
            "collection_id": "germany",
            "family": "bulletin",
            "root": str(collection_root),
            "slot": "strings",
            "path": str(collection_root / "strings.yml"),
            "relative_path": "strings.yml",
            "loader": "loc",
            "status": "loaded",
            "localization_count": 1,
            "languages": ["l_english"],
        }
    ]
    assert payload["index"] == {"germany": {"strings": [0]}}


def test_templates_cli_lists_available_authoring_templates(tmp_path: Path) -> None:
    project_root = tmp_path / "starter-mod"
    Project.create(project_root, title="Starter Mod")

    result = CliRunner().invoke(build_app(), ["templates", str(project_root), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    templates = {row["id"]: row for row in payload["templates"]}
    assert payload["schema"] == "paradev.sdk.templates.v1"
    assert payload["project_id"] == "starter_mod"
    assert payload["source_roots"] == [
        {
            "path": str(project_root / "src"),
            "relative_path": "src",
            "default": True,
        }
    ]
    assert payload["index"]["id"] == {"hoi4:idea/basic": [0]}
    assert payload["index"]["authoring_ready"] == {"true": [0]}
    assert templates["hoi4:idea/basic"]["family"] == "idea"
    assert templates["hoi4:idea/basic"]["authoring_ready"] is True
    assert templates["hoi4:idea/basic"]["files"] == ["meta.yaml", "def.txt", "main.loc"]


def test_templates_cli_filters_authoring_templates(tmp_path: Path) -> None:
    project_root = tmp_path / "filtered-template-project"
    project_root.mkdir()
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: filtered_template_project",
                "title: Filtered Template Project",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "templates:",
                "  notice/custom:",
                "    title: Custom Notice",
                "    family: notice",
                "    files:",
                "      body.txt: notice = { id = {object_id} }",
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "templates",
            str(project_root),
            "--family",
            "notice",
            "--not-authoring-ready",
            "--diagnostic-code",
            "template.unknown_family",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert [row["id"] for row in payload["templates"]] == ["notice/custom"]
    assert payload["index"]["family"] == {"notice": [0]}
    assert payload["index"]["authoring_ready"] == {"false": [0]}
    assert payload["index"]["diagnostic_code"] == {"template.unknown_family": [0]}


def test_authoring_path_cli_resolves_configured_source_root(tmp_path: Path) -> None:
    project_root = tmp_path / "multi-root-project"
    (project_root / "src").mkdir(parents=True)
    (project_root / "imports").mkdir()
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: multi_root_project",
                "title: Multi Root Project",
                "game: hoi4",
                "source_roots: [src, imports]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "authoring-path",
            str(project_root),
            "module",
            "idea",
            "GER_imported_spirit",
            "--source-root",
            "imports",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload == {
        "schema": "paradev.sdk.authoring_path.v1",
        "project_id": "multi_root_project",
        "kind": "module",
        "family": "idea",
        "object_id": "GER_imported_spirit",
        "module_id": "idea/GER_imported_spirit",
        "source_root": str(project_root / "imports"),
        "source_root_relative_path": "imports",
        "root": str(project_root / "imports/modules/idea/GER_imported_spirit"),
        "relative_path": "imports/modules/idea/GER_imported_spirit",
        "template": "modules/{family}/{object_id}",
        "exists": False,
    }


def test_authoring_plan_cli_lists_expected_source_slots(tmp_path: Path) -> None:
    project_root = tmp_path / "starter-mod"
    Project.create(project_root, title="Starter Mod")

    result = CliRunner().invoke(
        build_app(),
        [
            "authoring-plan",
            str(project_root),
            "module",
            "idea",
            "GER_industry_spirit",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.sdk.authoring_plan.v1"
    assert payload["authoring_path"]["module_id"] == "idea/GER_industry_spirit"
    assert [row["slot"] for row in payload["source_slots"]] == ["def", "icon", "loc"]
    assert [row["status"] for row in payload["source_slots"]] == ["empty", "empty", "empty"]
    assert [row["source_count"] for row in payload["source_slots"]] == [0, 0, 0]
    assert [row["relative_paths"] for row in payload["source_slots"]] == [[], [], []]
    assert [row["paths"] for row in payload["source_slots"]] == [[], [], []]
    assert payload["source_slots"][0]["suggested_relative_paths"] == ["src/modules/idea/GER_industry_spirit/def.txt"]
    assert payload["source_slots"][1]["loader"] == "copy"
    assert payload["index"]["slot"] == {"def": [0], "icon": [1], "loc": [2]}
    assert payload["index"]["status"] == {"empty": [0, 1, 2]}


def test_scaffold_cli_plans_and_writes_authoring_template(tmp_path: Path) -> None:
    project_root = tmp_path / "starter-mod"
    Project.create(project_root, title="Starter Mod")

    dry = CliRunner().invoke(
        build_app(),
        [
            "scaffold",
            str(project_root),
            "hoi4:idea/basic",
            "GER_industry_spirit",
            "--value",
            "title=German Industry Spirit",
            "--value",
            "description=Industrial production spirit.",
            "--json",
        ],
    )

    assert dry.exit_code == 0, dry.output
    dry_payload = json.loads(dry.output)
    assert dry_payload["schema"] == "paradev.sdk.module_scaffold.v1"
    assert dry_payload["blocked"] is False
    assert dry_payload["written"] is False
    assert dry_payload["template_id"] == "hoi4:idea/basic"
    assert dry_payload["authoring_plan"]["schema"] == "paradev.sdk.authoring_plan.v1"
    assert dry_payload["authoring_plan"]["authoring_path"]["module_id"] == "idea/GER_industry_spirit"
    assert [row["status"] for row in dry_payload["authoring_plan"]["source_slots"]] == ["empty", "empty", "empty"]
    assert dry_payload["authoring_plan"]["index"]["status"] == {"empty": [0, 1, 2]}
    assert not (project_root / "src/modules/idea/GER_industry_spirit/def.txt").exists()

    write = CliRunner().invoke(
        build_app(),
        [
            "scaffold",
            str(project_root),
            "hoi4:idea/basic",
            "GER_industry_spirit",
            "--value",
            "title=German Industry Spirit",
            "--value",
            "description=Industrial production spirit.",
            "--write",
            "--json",
        ],
    )

    assert write.exit_code == 0, write.output
    write_payload = json.loads(write.output)
    assert write_payload["blocked"] is False
    assert write_payload["written"] is True
    assert write_payload["module_id"] == "idea/GER_industry_spirit"
    assert (project_root / "src/modules/idea/GER_industry_spirit/def.txt").is_file()


def test_draft_apply_cli_writes_validated_source_edits(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module("idea", "GER_industry_spirit", values={"title": "German Industry Spirit"}, write=True)
    source_path = project.root / "src/modules/idea/GER_industry_spirit/def.txt"
    request_path = tmp_path / "draft-request.json"
    edited = "ideas = {}\n"
    request_path.write_text(
        json.dumps({"source_edits": [{"path": str(source_path), "text": edited}]}),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "draft-apply",
            project.project_id,
            "--project-root",
            str(project.root),
            "--request",
            str(request_path),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.rest.draft_apply.v1"
    assert payload["project_id"] == "starter"
    assert payload["written"] is True
    assert payload["files"][0]["relative_path"] == "src/modules/idea/GER_industry_spirit/def.txt"
    assert source_path.read_text(encoding="utf-8") == edited


def test_draft_apply_cli_commits_source_and_module_rename(
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module(
        "idea",
        "IDEA_ALPHA",
        values={"title": "Alpha"},
        write=True,
    )
    previous_root = project.root / "src/modules/idea/IDEA_ALPHA"
    localization = previous_root / "main.loc"
    request_path = tmp_path / "draft-request.json"
    request_path.write_text(
        json.dumps(
            {
                "source_edits": [
                    {
                        "path": str(localization),
                        "text": "[en.IDEA_ALPHA]\nReadable Alpha\n",
                    }
                ],
                "module_rename": {
                    "module_id": "idea/IDEA_ALPHA",
                    "object_id": "IDEA_ALPHA",
                    "title": "Readable Alpha",
                },
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "draft-apply",
            project.project_id,
            "--project-root",
            str(project.root),
            "--request",
            str(request_path),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    renamed_root = project.root / "src/modules/idea/IDEA_ALPHA - Readable Alpha"
    assert payload["module_rename"]["root"] == str(renamed_root)
    assert not previous_root.exists()
    assert (renamed_root / "main.loc").read_text(encoding="utf-8") == ("[en.IDEA_ALPHA]\nReadable Alpha\n")


def test_module_batch_create_cli_plans_inline_and_applies_file(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    request = {"modules": [{"family": "idea", "object_id": object_id, "values": {"title": f"Idea {object_id}"}} for object_id in ("A", "B", "C", "D", "E")]}

    planned = CliRunner().invoke(
        build_app(),
        [
            "module-batch-create",
            str(project.root),
            "--request-json",
            json.dumps(request),
            "--json",
        ],
    )

    assert planned.exit_code == 0, planned.output
    plan = json.loads(planned.output)
    assert plan["schema"] == "paradev.sdk.module_batch.v1"
    assert plan["blocked"] is False
    assert plan["applied"] is False
    assert plan["counts"]["create"] == 5
    assert len(plan["plan_hash"]) == 64
    assert not (project.root / "src/modules/idea/A").exists()

    request_path = tmp_path / "module-batch-create.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    applied = CliRunner().invoke(
        build_app(),
        [
            "module-batch-create",
            str(project.root),
            "--request",
            str(request_path),
            "--apply",
            "--plan-hash",
            plan["plan_hash"],
            "--json",
        ],
    )

    assert applied.exit_code == 0, applied.output
    payload = json.loads(applied.output)
    assert payload["applied"] is True
    assert payload["counts"]["created"] == 5
    assert (project.root / "src/modules/idea/E/meta.yaml").is_file()


def test_module_batch_create_cli_reads_stdin_and_blocks_apply_without_hash(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    request = {
        "modules": [
            {"family": "idea", "object_id": "HASH_GUARD", "values": {"title": "Hash guard"}},
        ]
    }

    planned = CliRunner().invoke(
        build_app(),
        ["module-batch-create", str(project.root), "--request", "-", "--json"],
        input=json.dumps(request),
    )

    assert planned.exit_code == 0, planned.output
    assert len(json.loads(planned.output)["plan_hash"]) == 64

    blocked = CliRunner().invoke(
        build_app(),
        [
            "module-batch-create",
            str(project.root),
            "--request-json",
            json.dumps(request),
            "--write",
            "--json",
        ],
    )

    assert blocked.exit_code == 1, blocked.output
    payload = json.loads(blocked.output)
    assert payload["blocked"] is True
    assert {row["code"] for row in payload["diagnostics"]} == {"module_batch.plan_hash_required"}
    assert not (project.root / "src/modules/idea/HASH_GUARD").exists()


def test_module_batch_create_cli_exposes_apply_without_force() -> None:
    result = CliRunner().invoke(build_app(), ["module-batch-create", "--help"])

    assert result.exit_code == 0, result.output
    assert "--apply" in result.output
    assert "--plan-hash" in result.output
    assert "--force" not in result.output


def test_module_batch_create_cli_plain_block_and_source_root_errors_are_actionable(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    request = {"modules": [{"family": "idea", "object_id": "ACTIONABLE", "values": {"title": "Actionable"}}]}
    request_json = json.dumps(request)

    blocked = CliRunner().invoke(
        build_app(),
        [
            "module-batch-create",
            str(project.root),
            "--request-json",
            request_json,
            "--apply",
        ],
    )

    assert blocked.exit_code == 1, blocked.output
    assert "1 pending create" in blocked.output
    assert "module_batch.plan_hash_required" in blocked.output
    assert "Applying a module batch requires" in blocked.output
    assert "plan_hash returned by a dry plan." in blocked.output

    project.scaffold_module(
        "idea",
        "ACTIONABLE",
        values={"title": "Different existing module"},
        write=True,
    )
    conflict = CliRunner().invoke(
        build_app(),
        [
            "module-batch-create",
            str(project.root),
            "--request-json",
            request_json,
        ],
    )

    assert conflict.exit_code == 0, conflict.output
    assert "module_batch.module_conflict" in conflict.output
    assert "already exists" in conflict.output
    assert "exactly match" in conflict.output

    invalid_source_root = CliRunner().invoke(
        build_app(),
        [
            "module-batch-create",
            str(project.root),
            "--request-json",
            request_json,
            "--source-root",
            "missing-source-root",
        ],
    )

    assert invalid_source_root.exit_code == 2, invalid_source_root.output
    assert "--request/--source-root" in invalid_source_root.output
    assert "Unknown source root" in invalid_source_root.output


def test_module_batch_edit_cli_writes_json_request(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module("idea", "GER_industry_spirit", values={"title": "German Industry Spirit"}, write=True)
    def_path = project.root / "src/modules/idea/GER_industry_spirit/def.txt"
    loc_path = project.root / "src/modules/idea/GER_industry_spirit/main.loc"
    request_path = tmp_path / "module-batch.json"
    edited_def = "ideas = {\n  GER_industry_spirit = {}\n}\n"
    edited_loc = 'l_english:\n  GER_industry_spirit: "German Industry Spirit"\n'
    request_path.write_text(
        json.dumps(
            {
                "edits": [
                    {
                        "module_id": "idea/GER_industry_spirit",
                        "relative_path": "def.txt",
                        "text": edited_def,
                    },
                    {
                        "module_id": "idea/GER_industry_spirit",
                        "relative_path": "main.loc",
                        "text": edited_loc,
                    },
                    {
                        "module_id": "idea/GER_industry_spirit",
                        "relative_path": "migration/notes.txt",
                        "text": "script generated note\n",
                        "create": True,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-edit",
            str(project.root),
            "--request",
            str(request_path),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.module.batch_edit.v1"
    assert payload["project_id"] == "starter"
    assert payload["written"] is True
    assert payload["file_count"] == 3
    assert payload["created_count"] == 1
    assert payload["updated_count"] == 2
    assert payload["files"][0]["relative_path"] == "src/modules/idea/GER_industry_spirit/def.txt"
    assert [row["created"] for row in payload["files"]] == [False, False, True]
    assert def_path.read_text(encoding="utf-8") == edited_def
    assert loc_path.read_text(encoding="utf-8") == edited_loc
    assert (project.root / "src/modules/idea/GER_industry_spirit/migration/notes.txt").read_text(encoding="utf-8") == "script generated note\n"


def test_module_batch_request_cli_emits_canonical_json_request(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module("idea", "GER_industry_spirit", values={"title": "German Industry Spirit"}, write=True)
    note_text = "generated request note\n"
    edit = {
        "module_id": "idea/GER_industry_spirit",
        "relative_path": "migration/notes.txt",
        "text": note_text,
    }

    result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-request",
            str(project.root),
            "--create",
            "--edit-json",
            json.dumps(edit),
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.module.batch_edit_request.v1"
    assert payload["project_id"] == "starter"
    assert payload["create"] is True
    assert payload["encoding"] == "utf-8"
    assert payload["edit_count"] == 1
    assert payload["summary"] == {
        "edit_count": 1,
        "module_count": 1,
        "source_root_count": 0,
        "existing_target_count": 0,
        "missing_target_count": 1,
        "changed_target_count": 1,
        "unchanged_target_count": 0,
        "create_enabled_count": 1,
        "encoding_count": 1,
    }
    assert payload["edits"] == [edit]
    assert payload["index"]["module_id"] == {"idea/GER_industry_spirit": [0]}
    assert payload["targets"] == [
        {
            "edit_index": 0,
            "module_id": "idea/GER_industry_spirit",
            "family": "idea",
            "object_id": "GER_industry_spirit",
            "relative_path": "migration/notes.txt",
            "target_relative_path": "src/modules/idea/GER_industry_spirit/migration/notes.txt",
            "exists": False,
            "created": True,
            "changed": True,
            "create": True,
            "encoding": "utf-8",
            "size_bytes": len(note_text.encode("utf-8")),
        }
    ]
    assert payload["target_index"]["created"] == {"true": [0]}
    assert payload["target_index"]["target_relative_path"] == {"src/modules/idea/GER_industry_spirit/migration/notes.txt": [0]}


def test_module_batch_request_cli_rejects_missing_targets_without_create(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module("idea", "GER_industry_spirit", values={"title": "German Industry Spirit"}, write=True)
    edit = {
        "module_id": "idea/GER_industry_spirit",
        "relative_path": "migration/notes.txt",
        "text": "generated request note\n",
    }

    result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-request",
            str(project.root),
            "--edit-json",
            json.dumps(edit),
        ],
    )

    assert result.exit_code != 0
    assert "Module file does not exist" in result.output
    assert "migration/notes.txt" in result.output


def test_module_batch_request_cli_output_feeds_batch_edit_stdin(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module("idea", "GER_industry_spirit", values={"title": "German Industry Spirit"}, write=True)
    notes_path = project.root / "src/modules/idea/GER_industry_spirit/migration/notes.txt"
    edit = {
        "module_id": "idea/GER_industry_spirit",
        "relative_path": "migration/notes.txt",
        "text": "generated request pipeline\n",
    }
    request_result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-request",
            str(project.root),
            "--create",
            "--edit-json",
            json.dumps(edit),
        ],
    )
    assert request_result.exit_code == 0, request_result.output

    edit_result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-edit",
            str(project.root),
            "--request",
            "-",
            "--json",
        ],
        input=request_result.output,
    )

    assert edit_result.exit_code == 0, edit_result.output
    payload = json.loads(edit_result.output)
    assert payload["schema"] == "paradev.module.batch_edit.v1"
    assert payload["written"] is True
    assert payload["file_count"] == 1
    assert payload["created_count"] == 1
    assert notes_path.read_text(encoding="utf-8") == "generated request pipeline\n"


def test_module_batch_edit_cli_plain_summary_counts_created_and_updated_files(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module("idea", "GER_industry_spirit", values={"title": "German Industry Spirit"}, write=True)
    request_path = tmp_path / "module-batch.json"
    request_path.write_text(
        json.dumps(
            {
                "edits": [
                    {
                        "module_id": "idea/GER_industry_spirit",
                        "relative_path": "def.txt",
                        "text": "ideas = { GER_industry_spirit = {} }\n",
                    },
                    {
                        "module_id": "idea/GER_industry_spirit",
                        "relative_path": "migration/notes.txt",
                        "text": "script generated note\n",
                        "create": True,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-edit",
            str(project.root),
            "--request",
            str(request_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert result.output == "wrote 2 module file(s): 2 changed, 0 unchanged; 1 updated, 1 created\n"


def test_module_batch_edit_cli_plain_summary_reports_changed_and_unchanged_files(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module("idea", "GER_industry_spirit", values={"title": "German Industry Spirit"}, write=True)
    def_path = project.root / "src/modules/idea/GER_industry_spirit/def.txt"
    original_def = def_path.read_text(encoding="utf-8")
    request_body = json.dumps(
        {
            "edits": [
                {
                    "module_id": "idea/GER_industry_spirit",
                    "relative_path": "def.txt",
                    "text": original_def,
                },
                {
                    "module_id": "idea/GER_industry_spirit",
                    "relative_path": "migration/rerun-notes.txt",
                    "text": "generated rerun note\n",
                    "create": True,
                },
            ]
        }
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-edit",
            str(project.root),
            "--request-json",
            request_body,
            "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.output
    assert result.output == "planned 2 module file(s): 1 changed, 1 unchanged; 1 updated, 1 created\n"
    assert def_path.read_text(encoding="utf-8") == original_def
    notes_path = project.root / "src/modules/idea/GER_industry_spirit/migration/rerun-notes.txt"
    assert not notes_path.exists()


def test_module_batch_edit_cli_accepts_inline_json_request(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module("idea", "GER_industry_spirit", values={"title": "German Industry Spirit"}, write=True)
    notes_path = project.root / "src/modules/idea/GER_industry_spirit/migration/inline-notes.txt"
    request_body = json.dumps(
        {
            "edits": [
                {
                    "module_id": "idea/GER_industry_spirit",
                    "relative_path": "migration/inline-notes.txt",
                    "text": "generated inline request\n",
                    "create": True,
                }
            ]
        }
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-edit",
            str(project.root),
            "--request-json",
            request_body,
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.module.batch_edit.v1"
    assert payload["file_count"] == 1
    assert payload["created_count"] == 1
    assert payload["files"][0]["module_relative_path"] == "migration/inline-notes.txt"
    assert notes_path.read_text(encoding="utf-8") == "generated inline request\n"


def test_module_batch_edit_cli_rejects_multiple_json_request_sources(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    request_path = tmp_path / "module-batch.json"
    request_path.write_text('{"edits":[]}', encoding="utf-8")

    result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-edit",
            str(project.root),
            "--request",
            str(request_path),
            "--request-json",
            '{"edits":[]}',
        ],
    )

    assert result.exit_code != 0
    assert "Pass only one module batch edit request source" in result.output


def test_module_batch_edit_cli_rejects_request_without_edits_array(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")

    result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-edit",
            str(project.root),
            "--request-json",
            '{"create": true}',
        ],
    )

    assert result.exit_code != 0
    assert "Module batch edit request edits must be an" in result.output
    assert "array." in result.output


def test_module_batch_edit_cli_reads_json_request_from_stdin(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module("idea", "GER_industry_spirit", values={"title": "German Industry Spirit"}, write=True)
    def_path = project.root / "src/modules/idea/GER_industry_spirit/def.txt"
    edited_def = "ideas = {\n  GER_industry_spirit = { allowed = { always = yes } }\n}\n"
    request_body = json.dumps(
        {
            "edits": [
                {
                    "module_id": "idea/GER_industry_spirit",
                    "relative_path": "def.txt",
                    "text": edited_def,
                }
            ]
        }
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-edit",
            str(project.root),
            "--request",
            "-",
            "--json",
        ],
        input=request_body,
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.module.batch_edit.v1"
    assert payload["file_count"] == 1
    assert payload["files"][0]["module_relative_path"] == "def.txt"
    assert def_path.read_text(encoding="utf-8") == edited_def


def test_module_batch_edit_cli_can_preview_json_request(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module("idea", "GER_industry_spirit", values={"title": "German Industry Spirit"}, write=True)
    def_path = project.root / "src/modules/idea/GER_industry_spirit/def.txt"
    original_def = def_path.read_text(encoding="utf-8")
    notes_path = project.root / "src/modules/idea/GER_industry_spirit/migration/notes.txt"
    request_body = json.dumps(
        {
            "edits": [
                {
                    "module_id": "idea/GER_industry_spirit",
                    "relative_path": "def.txt",
                    "text": "ideas = { GER_industry_spirit = {} }\n",
                },
                {
                    "module_id": "idea/GER_industry_spirit",
                    "relative_path": "migration/notes.txt",
                    "text": "preview note\n",
                    "create": True,
                },
            ]
        }
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-edit",
            str(project.root),
            "--request",
            "-",
            "--dry-run",
            "--json",
        ],
        input=request_body,
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.module.batch_edit.v1"
    assert payload["written"] is False
    assert payload["file_count"] == 2
    assert [row["written"] for row in payload["files"]] == [False, False]
    assert def_path.read_text(encoding="utf-8") == original_def
    assert not notes_path.exists()


def test_module_batch_edit_cli_json_reports_changed_and_unchanged_files(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module("idea", "GER_industry_spirit", values={"title": "German Industry Spirit"}, write=True)
    def_path = project.root / "src/modules/idea/GER_industry_spirit/def.txt"
    original_def = def_path.read_text(encoding="utf-8")
    request_body = json.dumps(
        {
            "edits": [
                {
                    "module_id": "idea/GER_industry_spirit",
                    "relative_path": "def.txt",
                    "text": original_def,
                },
                {
                    "module_id": "idea/GER_industry_spirit",
                    "relative_path": "migration/rerun-notes.txt",
                    "text": "generated rerun note\n",
                    "create": True,
                },
            ]
        }
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-edit",
            str(project.root),
            "--request-json",
            request_body,
            "--dry-run",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.module.batch_edit.v1"
    assert payload["written"] is False
    assert payload["file_count"] == 2
    assert payload["created_count"] == 1
    assert payload["updated_count"] == 1
    assert payload["changed_count"] == 1
    assert payload["unchanged_count"] == 1
    assert [row["changed"] for row in payload["files"]] == [False, True]
    assert def_path.read_text(encoding="utf-8") == original_def
    notes_path = project.root / "src/modules/idea/GER_industry_spirit/migration/rerun-notes.txt"
    assert not notes_path.exists()


def test_module_batch_edit_cli_uses_json_request_defaults(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module("idea", "GER_industry_spirit", values={"title": "German Industry Spirit"}, write=True)
    notes_path = project.root / "src/modules/idea/GER_industry_spirit/migration/notes.txt"
    request_body = json.dumps(
        {
            "create": True,
            "encoding": "utf-8",
            "edits": [
                {
                    "module_id": "idea/GER_industry_spirit",
                    "relative_path": "migration/notes.txt",
                    "text": "generated request default\n",
                }
            ],
        }
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "module-batch-edit",
            str(project.root),
            "--request",
            "-",
            "--json",
        ],
        input=request_body,
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.module.batch_edit.v1"
    assert payload["written"] is True
    assert payload["file_count"] == 1
    assert payload["files"][0]["module_relative_path"] == "migration/notes.txt"
    assert notes_path.read_text(encoding="utf-8") == "generated request default\n"


def test_scaffold_cli_can_select_source_root(tmp_path: Path) -> None:
    project_root = tmp_path / "multi-root-project"
    (project_root / "src").mkdir(parents=True)
    (project_root / "imports").mkdir()
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: multi_root_project",
                "title: Multi Root Project",
                "game: hoi4",
                "source_roots: [src, imports]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        build_app(),
        [
            "scaffold",
            str(project_root),
            "hoi4:idea/basic",
            "GER_imported_spirit",
            "--source-root",
            "imports",
            "--write",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["source_root"] == str(project_root / "imports")
    assert payload["root"] == str(project_root / "imports/modules/idea/GER_imported_spirit")
    assert (project_root / "imports/modules/idea/GER_imported_spirit/def.txt").is_file()


def test_scaffold_cli_rejects_invalid_template_value(tmp_path: Path) -> None:
    project_root = tmp_path / "starter-mod"
    Project.create(project_root, title="Starter Mod")

    result = CliRunner().invoke(
        build_app(),
        [
            "scaffold",
            str(project_root),
            "hoi4:idea/basic",
            "GER_industry_spirit",
            "--value",
            "title",
            "--json",
        ],
    )

    assert result.exit_code == 2, result.output
    assert "must use KEY=VALUE" in result.output


def test_config_list_accepts_local_json_option(cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.project.name", default=None)

    try:
        CM_PARADEV.unset("paradev.project.name")
        result = CliRunner().invoke(build_app(), ["config", "list", "--json"])

        assert result.exit_code == 0, result.output
        rows = json.loads(result.output)

        assert {"key": "paradev.project.name", "value": "ParaDev"} in rows
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.project.name")
        else:
            CM_PARADEV.set("paradev.project.name", previous)


def test_config_get_serializes_scalar_json_option(cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.project.name", default=None)

    try:
        CM_PARADEV.unset("paradev.project.name")
        result = CliRunner().invoke(build_app(), ["cfg", "get", "paradev.project.name", "--json"])

        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == "ParaDev"
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.project.name")
        else:
            CM_PARADEV.set("paradev.project.name", previous)


def test_cli_output_config_enables_json_by_default(cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.cli.output", default=None)
    previous_project_name = CM_PARADEV.get("paradev.project.name", default=None)

    try:
        CM_PARADEV.unset("paradev.project.name")
        CM_PARADEV.set("paradev.cli.output", "json")
        result = CliRunner().invoke(build_app(), ["cfg", "get", "paradev.project.name"])

        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == "ParaDev"
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.cli.output")
        else:
            CM_PARADEV.set("paradev.cli.output", previous)
        if previous_project_name is None:
            CM_PARADEV.unset("paradev.project.name")
        else:
            CM_PARADEV.set("paradev.project.name", previous_project_name)


def test_parse_outputs_pdx_projection_json(tmp_path: Path) -> None:
    source = tmp_path / "focus.pdx"
    source.write_text("focus = { id = GER_test cost = 10 }", encoding="utf-8")

    result = CliRunner().invoke(build_app(), ["parse", str(source), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload == {
        "schema": "paradev.pdx.parse.v1",
        "path": str(source.resolve()),
        "file_ext": ".pdx",
        "ok": True,
        "data": {"focus": {"id": "GER_test", "cost": 10}},
        "diagnostics": [],
    }


def test_parse_can_include_lossless_dump_json(tmp_path: Path) -> None:
    source = tmp_path / "focus.pdx"
    source.write_text("# focus comment\nfocus = { id = GER_test cost = 10 cost = 20 }", encoding="utf-8")

    result = CliRunner().invoke(build_app(), ["parse", str(source), "--dump", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    restored = PDXBlock.load(payload["dump"])
    focus = restored.find("focus")
    assert payload["data"] == {"focus": {"id": "GER_test", "cost": 10, "cost__D1": 20}}
    assert payload["dump"]["anno"] == {"file_ext": ".pdx"}
    assert focus.comments == ["# focus comment"]
    assert focus.val.count("cost") == 2


def test_parse_can_include_token_rows_json(tmp_path: Path) -> None:
    source = tmp_path / "focus.pdx"
    source.write_text("focus = { id = GER_test }", encoding="utf-8")

    result = CliRunner().invoke(build_app(), ["parse", str(source), "--tokens", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["tokens"] == [
        {"type": "identifier", "value": "focus", "line": 1, "column": 1},
        {"type": "equals", "value": "=", "line": 1, "column": 7},
        {"type": "lbrace", "value": "{", "line": 1, "column": 9},
        {"type": "identifier", "value": "id", "line": 1, "column": 11},
        {"type": "equals", "value": "=", "line": 1, "column": 14},
        {"type": "identifier", "value": "GER_test", "line": 1, "column": 16},
        {"type": "rbrace", "value": "}", "line": 1, "column": 25},
    ]
    assert payload["data"] == {"focus": {"id": "GER_test"}}
    assert "dump" not in payload


def test_parse_cli_matches_sdk_payload(tmp_path: Path) -> None:
    source = tmp_path / "focus.pdx"
    source.write_text("focus = { id = GER_test }", encoding="utf-8")

    result = CliRunner().invoke(build_app(), ["parse", str(source), "--tokens", "--json"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == parse_pdx_file(source, include_tokens=True)


def test_format_cli_previews_and_writes_pdx_file(tmp_path: Path) -> None:
    source = tmp_path / "focus.pdx"
    source.write_text("focus={id=GER_test cost=10}", encoding="utf-8")

    dry = CliRunner().invoke(build_app(), ["format", str(source), "--json"])

    assert dry.exit_code == 0, dry.output
    dry_payload = json.loads(dry.output)
    assert dry_payload == format_pdx_file(source)
    assert dry_payload["formatted_text"] == "focus = {\n\tid = GER_test\n\tcost = 10\n}\n"
    assert dry_payload["written"] is False
    assert source.read_text(encoding="utf-8") == "focus={id=GER_test cost=10}"

    write = CliRunner().invoke(build_app(), ["format", str(source), "--write", "--json"])

    assert write.exit_code == 0, write.output
    write_payload = json.loads(write.output)
    assert write_payload["written"] is True
    assert source.read_text(encoding="utf-8") == "focus = {\n\tid = GER_test\n\tcost = 10\n}\n"


def test_parse_outputs_diagnostics_json_for_invalid_pdx(tmp_path: Path) -> None:
    source = tmp_path / "broken.pdx"
    source.write_text("value = 0x", encoding="utf-8")

    result = CliRunner().invoke(build_app(), ["parse", str(source), "--json"])

    assert result.exit_code == 1, result.output
    payload = json.loads(result.output)
    assert payload == {
        "schema": "paradev.pdx.parse.v1",
        "path": str(source.resolve()),
        "file_ext": ".pdx",
        "ok": False,
        "data": None,
        "diagnostics": [
            {
                "code": "pdx.invalid_hex_number",
                "message": "PDX hexadecimal number requires at least one digit.",
                "line": 1,
                "column": 9,
                "severity": "error",
            }
        ],
    }


def test_parse_outputs_diagnostics_json_for_missing_source(tmp_path: Path) -> None:
    source = tmp_path / "missing.pdx"

    result = CliRunner().invoke(build_app(), ["parse", str(source), "--json"])

    assert result.exit_code == 1, result.output
    payload = json.loads(result.output)
    assert payload == {
        "schema": "paradev.pdx.parse.v1",
        "path": str(source.resolve()),
        "file_ext": ".pdx",
        "ok": False,
        "data": None,
        "diagnostics": [
            {
                "code": "pdx.source_not_found",
                "message": f"PDX source file not found: {source.resolve()}.",
                "severity": "error",
            }
        ],
    }
