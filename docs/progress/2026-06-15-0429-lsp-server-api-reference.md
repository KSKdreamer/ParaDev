# 2026-06-15 04:29 - LSP Server API Reference

Slice: added a generated `paradev.lsp` facade API table so the public LSP server package exports are covered by the maintained API inventory.

Changes:

- Added `paradev.lsp.get_lsp_server_api_table()` and `render_lsp_server_api_reference_markdown()`.
- Added CLI `paradev lsp-server-api` with `--json` and `--markdown` output.
- Registered `lsp-server-api` in the overall API catalog and CLI API contract.
- Regenerated affected references: LSP server API, API catalog, CLI API, and surfaces API.
- Updated user/developer docs and architecture interface notes to route facade audits through the generated table.

Targeted checks:

- `rtk uv run python -m py_compile src/paradev/lsp/api.py src/paradev/lsp/__init__.py src/paradev/cli.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/lsp/api.py src/paradev/lsp/__init__.py src/paradev/cli.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/lsp/api.py src/paradev/lsp/__init__.py src/paradev/cli.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk uv run pytest tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_lsp_server_api_cli_outputs_table_json tests/test_cli.py::test_lsp_server_api_cli_outputs_reference_markdown tests/test_cli.py::test_lsp_server_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown`

Skipped full-suite tests to keep CPU free for concurrent PIHC3 migration work.
