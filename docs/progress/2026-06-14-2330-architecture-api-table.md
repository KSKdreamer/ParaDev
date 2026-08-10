# 2026-06-14 23:30 - Architecture API Table

Linear: TAL-299

## Done

- Added an SDK-owned architecture API-standard table through `ARCHITECTURE_API_TABLE_ROWS`, `ARCHITECTURE_API_TABLE_SCHEMA`, `get_architecture_api_table()`, and `render_architecture_api_reference_markdown()`.
- Added CLI projections `paradev architecture --api-table` and `paradev architecture --api-table-markdown`.
- Generated `docs/user-manual/architecture-api-reference.md` and linked it from the user manual.
- Updated architecture and developer docs so SDK, CLI, REST, and MCP architecture entry points point at the generated table instead of hand-maintained symbol lists.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/architecture.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/architecture.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/architecture.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface tests/test_architecture.py::test_architecture_surfaces_cover_requested_paths tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_cli.py::test_architecture_cli_outputs_api_table_json tests/test_cli.py::test_architecture_cli_outputs_api_table_markdown tests/test_cli.py::test_architecture_cli_rejects_api_table_markdown_json_combo tests/test_cli.py::test_architecture_cli_outputs_one_surface_contract_json -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_architecture_cli_rejects_surface_contract_markdown_json_combo tests/test_cli.py::test_architecture_cli_outputs_surface_contract_reference_markdown tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries -q`
- `rtk bash -lc 'uv run paradev architecture --api-table-markdown | diff -u docs/user-manual/architecture-api-reference.md -'`

## Notes

- Full-suite tests were deferred to keep CPU free while PIHC3 migration work is active in the shared tree.
- `node_modules/`, desktop generated output, and PIHC3 migration files remain outside this slice.
