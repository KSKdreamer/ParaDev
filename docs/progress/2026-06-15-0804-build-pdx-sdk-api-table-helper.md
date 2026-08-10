# Build PDX SDK API Table Helper Progress

Date: 2026-06-15 08:04 +0800

Linear: none

## Done

- Migrated the public build facade API reference renderer to the shared API-table Markdown helpers.
- Migrated the public PDX core facade API reference renderer to the shared API-table Markdown helpers.
- Migrated the public SDK facade API reference renderer to the shared API-table Markdown helpers.
- Preserved generated API schemas, row ordering, manual reference output, CLI JSON output, and CLI Markdown output.

## Verification

- `rtk uv run python -m py_compile src/paradev/build/api.py src/paradev/pdx/api.py src/paradev/sdk/api.py`
- `rtk uv run pytest tests/test_architecture.py::test_sdk_api_table_lists_facade_exports tests/test_architecture.py::test_build_api_table_lists_public_build_facade tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade tests/test_cli.py::test_sdk_api_cli_outputs_table_json tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_build_api_cli_outputs_table_json tests/test_cli.py::test_build_api_cli_outputs_reference_markdown tests/test_cli.py::test_pdx_core_api_cli_outputs_table_json tests/test_cli.py::test_pdx_core_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/api.py src/paradev/pdx/api.py src/paradev/sdk/api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/build/api.py src/paradev/pdx/api.py src/paradev/sdk/api.py`
- `rtk git diff --check -- src/paradev/build/api.py src/paradev/pdx/api.py src/paradev/sdk/api.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated Heaven-style skill, desktop app, PIHC3, logo, loader, and `node_modules/` changes from other workers.

## Next

- Continue migrating clean generated-reference renderers to `paradev._api_table_markdown`.
- Keep avoiding build loader, HoI4 package internals, desktop app files, and PIHC3 progress files while those slices remain active elsewhere.
