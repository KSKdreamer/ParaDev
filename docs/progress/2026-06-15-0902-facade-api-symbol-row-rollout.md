# Facade API Symbol Row Rollout Progress

Date: 2026-06-15 09:02 CST

Linear: none

## Done

- Migrated the REST facade, LSP server, PDX core, and HeavenBase facade API reference renderers to the shared `api_symbol_table_row()` helper.
- Preserved the generated Markdown for all four API references exactly.
- Kept the slice away from dirty PIHC3 migration, build loader internals, HoI4 package internals, and desktop app files.

## Verification

- `rtk uv run python - <<'PY' ... PY` old-vs-current renderer comparison for REST facade, LSP server, PDX core, and HB API references
- `rtk uv run black src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py`
- `rtk uv run python -m py_compile src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py`
- `rtk uv run pytest tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade tests/test_cli.py::test_rest_facade_api_cli_outputs_reference_markdown tests/test_cli.py::test_lsp_server_api_cli_outputs_reference_markdown tests/test_cli.py::test_pdx_core_api_cli_outputs_reference_markdown tests/test_cli.py::test_hb_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py`
- `rtk git diff --check -- src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated Heaven-style skill, desktop app, PIHC3, logo, loader, and `node_modules/` changes from other workers.

## Next

- Evaluate the remaining specialized API table renderers separately; some use plain Markdown cells for free-form values and should not be blindly routed through `api_symbol_table_row()`.
- Keep avoiding build loader internals, HoI4 package internals, desktop app files, and PIHC3 progress files while those slices remain active elsewhere.
