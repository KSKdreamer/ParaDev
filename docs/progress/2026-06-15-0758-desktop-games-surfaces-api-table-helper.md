# Desktop Games Surfaces API Table Helper Progress

Date: 2026-06-15 07:58 +0800

Linear: none

## Done

- Migrated the public desktop package facade API reference renderer to the shared API-table Markdown helpers.
- Migrated the public games package facade API reference renderer to the shared API-table Markdown helpers.
- Migrated the public surfaces facade API reference renderer to the shared API-table Markdown helpers.
- Preserved generated API schemas, row ordering, manual reference output, CLI JSON output, and CLI Markdown output.

## Verification

- `rtk uv run python -m py_compile src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/surfaces/api.py`
- `rtk uv run pytest tests/test_architecture.py::test_desktop_api_table_lists_public_desktop_facade tests/test_architecture.py::test_games_api_table_lists_public_games_facade tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_cli.py::test_desktop_api_cli_outputs_table_json tests/test_cli.py::test_desktop_api_cli_outputs_reference_markdown tests/test_cli.py::test_games_api_cli_outputs_table_json tests/test_cli.py::test_games_api_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_outputs_table_json tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/surfaces/api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/surfaces/api.py`
- `rtk git diff --check -- src/paradev/desktop/api.py src/paradev/games/api.py src/paradev/surfaces/api.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated Heaven-style skill, desktop app, PIHC3, logo, loader, and `node_modules/` changes from other workers.

## Next

- Continue migrating clean generated-reference renderers to `paradev._api_table_markdown`.
- Avoid build loader, HoI4 package internals, desktop app files, and PIHC3 progress files while those slices remain active elsewhere.
