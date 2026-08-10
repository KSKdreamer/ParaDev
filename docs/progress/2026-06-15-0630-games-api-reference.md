# Games API Reference

## Scope

- Added a generated `paradev.games` facade API table for the game profile registry surface.
- Wired `games-api` into the API catalog, CLI contract, user manual index, architecture interface map, developer manual, and SDK guide.
- Generated `docs/user-manual/games-api-reference.md` and refreshed the dependent API catalog, CLI API, and surfaces API references.
- Left PIHC3 migration, desktop frontend, skill updates, and `node_modules/` untouched.

## Verification

- `rtk uv run python -m py_compile src/paradev/games/__init__.py src/paradev/games/api.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk uv run pytest tests/test_architecture.py::test_games_api_table_lists_public_games_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_games_api_cli_outputs_table_json tests/test_cli.py::test_games_api_cli_outputs_reference_markdown tests/test_cli.py::test_games_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/games/__init__.py src/paradev/games/api.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/games/__init__.py src/paradev/games/api.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
