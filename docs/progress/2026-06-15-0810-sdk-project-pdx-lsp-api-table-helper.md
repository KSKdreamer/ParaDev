# SDK Project PDX LSP API Table Helper Progress

Date: 2026-06-15 08:10 CST

Linear: none

## Done

- Migrated the SDK Project object API reference renderer to the shared API-table Markdown helpers.
- Migrated the SDK PDX API reference renderer to the shared API-table Markdown helpers.
- Migrated the SDK LSP API reference renderer to the shared API-table Markdown helpers.
- Preserved generated API schemas, row ordering, manual reference output, CLI JSON output, and CLI Markdown output.

## Verification

- `rtk uv run black src/paradev/sdk/project_api.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py`
- `rtk uv run python -m py_compile src/paradev/sdk/project_api.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py`
- `rtk uv run pytest tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces tests/test_cli.py::test_project_api_cli_outputs_table_json tests/test_cli.py::test_project_api_cli_outputs_reference_markdown tests/test_cli.py::test_pdx_api_cli_outputs_table_json tests/test_cli.py::test_pdx_api_cli_outputs_reference_markdown tests/test_cli.py::test_lsp_api_cli_outputs_table_json tests/test_cli.py::test_lsp_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project_api.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project_api.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py`
- `rtk git diff --check -- src/paradev/sdk/project_api.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated Heaven-style skill, desktop app, PIHC3, logo, loader, and `node_modules/` changes from other workers.

## Next

- Continue migrating clean generated-reference renderers to `paradev._api_table_markdown`.
- Keep avoiding build loader, HoI4 package internals, desktop app files, and PIHC3 progress files while those slices remain active elsewhere.
