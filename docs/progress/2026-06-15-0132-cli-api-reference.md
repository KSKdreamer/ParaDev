# CLI API Reference Progress

Date: 2026-06-15 01:32

Linear: unassigned

## Done

- Added the generated CLI command API-standard table from `paradev.surfaces.cli.get_cli_api_table()`.
- Added CLI `paradev cli-api` with JSON and Markdown projections.
- Tightened `get_cli_contract()` adapter coverage for existing inspection, config, catalog, LSP, and frontend API command variants.
- Generated `docs/user-manual/cli-api-reference.md` and linked it from the user/developer/interface docs.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/cli.py src/paradev/surfaces/__init__.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_cli_api_cli_rejects_markdown_json_combo -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/cli.py src/paradev/surfaces/__init__.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/cli.py src/paradev/surfaces/__init__.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full suite intentionally not run to preserve CPU while other PIHC2-to-PIHC3 workers are active.

## Next

- Continue moving remaining public surface inventories from prose-only docs into generated API tables.
