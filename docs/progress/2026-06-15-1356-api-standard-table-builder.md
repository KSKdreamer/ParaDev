# 2026-06-15 13:56 API standard table builder

## Scope

- Added `API_SYMBOL_FIELDS`, `copy_api_symbol_row(...)`, and `api_standard_table(...)` as the private shared data helpers for API-standard symbol tables.
- Routed 16 standard facade `get_*_api_table()` functions through the shared table builder while preserving each facade's public table function, schema constant, row `TypedDict`, row generator, and Markdown renderer.
- Removed the per-module duplicate standard row-copy helpers from package, config, GUI, desktop, games, project, localization, SDK, surfaces, build, REST facade, LSP server, PDX core, HB, templates, and copy-root API table modules.
- Made the Markdown helper reuse the shared standard field ordering so data assembly and Markdown rendering use one canonical column contract.
- Added focused helper tests for canonical field order, detached row copies, schema/count/index assembly, and copied row payloads.
- Left unrelated desktop, skill, PIHC3, localization-loader, and project-test worktree edits untouched.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table.py src/paradev/_api_table_markdown.py src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/project/api.py src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py tests/test_api_table.py`
- Generated-reference parity check passed for 16 affected renderers against the tracked manual pages, modulo the tracked files' final newline.
- `rtk bash scripts/test.bash tests/test_api_table.py tests/test_architecture.py::test_package_api_table_lists_root_facade tests/test_architecture.py::test_config_api_table_lists_public_config_facade tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade tests/test_architecture.py::test_desktop_api_table_lists_public_desktop_facade tests/test_architecture.py::test_games_api_table_lists_public_games_facade tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade tests/test_architecture.py::test_sdk_api_table_lists_facade_exports tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_build_api_table_lists_public_build_facade tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract -q`: 37 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py src/paradev/_api_table_markdown.py src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/project/api.py src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py tests/test_api_table.py`: OK, 19 files.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py src/paradev/_api_table_markdown.py src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/project/api.py src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py tests/test_api_table.py`: unchanged.
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the API-table helper, standard facade routing, helper tests, and this note.
- Do not stage `node_modules/`.
