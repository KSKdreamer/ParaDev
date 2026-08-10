# API Symbol Index Helper

## Scope

- Added `api_symbol_indexes()` for generated API table data construction.
- Migrated the standard `module`, `feature`, and `kind` index builders for facade-style API tables to the shared helper.
- Left specialized REST, CLI, MCP, catalog, and list-valued indexes for a later focused slice.

## Verification

- `rtk uv run python - <<'PY' ...` exact `HEAD` renderer comparison for package, config, GUI, desktop, games, project facade, localization, SDK facade, surfaces facade, build facade, REST facade, LSP server, PDX core, and HB facade references: all matched.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_package_api_table_lists_root_facade tests/test_architecture.py::test_config_api_table_lists_public_config_facade tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade tests/test_architecture.py::test_desktop_api_table_lists_public_desktop_facade tests/test_architecture.py::test_games_api_table_lists_public_games_facade tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade tests/test_architecture.py::test_sdk_api_table_lists_facade_exports tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_build_api_table_lists_public_build_facade tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade -q`: 14 passed.
- `rtk uv run black src/paradev/_api_table.py src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/project/api.py src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py`: unchanged.
- `rtk uv run python -m py_compile src/paradev/_api_table.py src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/project/api.py src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/project/api.py src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py`.
- `rtk bash scripts/flake.bash --paths src/paradev/_api_table.py src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/project/api.py src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py`.
- `rtk git diff --check -- src/paradev/_api_table.py src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/project/api.py src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py`.

## Notes

- Full-suite tests were intentionally skipped to reduce CPU contention with active PIHC3 migration work.
- `rtk gh pr status` reported no current PRs, so there were no open GitHub review threads to address in this pass.
