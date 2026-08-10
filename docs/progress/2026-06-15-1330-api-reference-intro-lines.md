# 2026-06-15 13:30 API reference intro lines

## Scope

- Added `api_reference_intro_lines(...)` as the shared renderer for generated API reference source and regeneration instructions.
- Routed 16 facade API Markdown renderers through the helper instead of repeating generated-from, regenerate-when, and fenced-command lines.
- Kept each facade title, source function, regenerate-when sentence, regeneration command, overview sections, API-standard table heading, and row renderer unchanged.
- Added a focused helper test that pins source formatting, blank-line spacing, and the nested fenced Bash regeneration command.
- Kept rendered Markdown text and API table payloads unchanged for all affected facade renderers.
- Left unrelated desktop, skill, PIHC3, localization, and logo worktree edits untouched.

## Verification

- Renderer/table comparison against `HEAD` passed for 16 facade API reference modules.
- `rtk bash scripts/test.bash tests/test_api_table.py tests/test_architecture.py::test_package_api_table_lists_root_facade tests/test_architecture.py::test_config_api_table_lists_public_config_facade tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade tests/test_architecture.py::test_desktop_api_table_lists_public_desktop_facade tests/test_architecture.py::test_games_api_table_lists_public_games_facade tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade tests/test_architecture.py::test_sdk_api_table_lists_facade_exports tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_build_api_table_lists_public_build_facade tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract -q`: 34 passed.
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/project/api.py src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/project/api.py src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/project/api.py src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py src/paradev/api/api.py src/paradev/lsp/api.py src/paradev/pdx/api.py src/paradev/hb/api.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py tests/test_api_table.py`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the shared Markdown helper, facade renderer intro cleanup, helper tests, and this note.
- Do not stage `node_modules/`.
