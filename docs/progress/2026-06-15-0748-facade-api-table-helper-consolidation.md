# Facade API Table Helper Consolidation Progress

Date: 2026-06-15 07:48 +0800

Linear: none

## Done

- Migrated the root package API reference renderer to the shared API-table Markdown helpers.
- Migrated the public config facade API reference renderer to the shared API-table Markdown helpers.
- Migrated the public GUI launcher facade API reference renderer to the shared API-table Markdown helpers.
- Kept generated API schemas, row ordering, manual reference output, CLI JSON output, and CLI Markdown output unchanged.

## Verification

- `rtk uv run python -m py_compile src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py`
- `rtk uv run pytest tests/test_architecture.py::test_package_api_table_lists_root_facade tests/test_architecture.py::test_config_api_table_lists_public_config_facade tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade tests/test_cli.py::test_package_api_cli_outputs_table_json tests/test_cli.py::test_package_api_cli_outputs_reference_markdown tests/test_cli.py::test_config_api_cli_outputs_table_json tests/test_cli.py::test_config_api_cli_outputs_reference_markdown tests/test_cli.py::test_gui_api_cli_outputs_table_json tests/test_cli.py::test_gui_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py`
- `rtk git diff --check -- src/paradev/package_api.py src/paradev/config_api.py src/paradev/gui_api.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated Heaven-style skill, desktop, PIHC3, logo, loader, and `node_modules/` changes from other workers.

## Next

- Continue migrating clean generated-reference renderers to `paradev._api_table_markdown`.
- Avoid build loader, HoI4, desktop app, and PIHC3 progress files while those slices remain active elsewhere.
