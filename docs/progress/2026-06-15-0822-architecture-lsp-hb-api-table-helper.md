# Architecture LSP HB API Table Helper Progress

Date: 2026-06-15 08:22 CST

Linear: none

## Done

- Migrated the architecture API reference renderer to the shared API-table Markdown helpers.
- Migrated the LSP server API reference renderer to the shared API-table Markdown helpers.
- Migrated the HeavenBase facade API reference renderer to the shared API-table Markdown helpers.
- Confirmed the PDX core API renderer was already migrated and left it unchanged.
- Preserved generated API schemas, row ordering, manual reference output, CLI JSON output, and CLI Markdown output.

## Verification

- `rtk uv run black src/paradev/sdk/architecture.py src/paradev/lsp/api.py src/paradev/hb/api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/architecture.py src/paradev/lsp/api.py src/paradev/hb/api.py`
- `rtk uv run pytest tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade tests/test_cli.py::test_architecture_cli_outputs_api_table_json tests/test_cli.py::test_architecture_cli_outputs_api_table_markdown tests/test_cli.py::test_lsp_server_api_cli_outputs_table_json tests/test_cli.py::test_lsp_server_api_cli_outputs_reference_markdown tests/test_cli.py::test_hb_api_cli_outputs_table_json tests/test_cli.py::test_hb_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/architecture.py src/paradev/lsp/api.py src/paradev/hb/api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/architecture.py src/paradev/lsp/api.py src/paradev/hb/api.py`
- `rtk git diff --check -- src/paradev/sdk/architecture.py src/paradev/lsp/api.py src/paradev/hb/api.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated Heaven-style skill, desktop app, PIHC3, logo, loader, and `node_modules/` changes from other workers.

## Next

- Continue migrating remaining generated-reference renderers with local Markdown helper copies.
- Keep avoiding build loader, HoI4 package internals, desktop app files, and PIHC3 progress files while those slices remain active elsewhere.
