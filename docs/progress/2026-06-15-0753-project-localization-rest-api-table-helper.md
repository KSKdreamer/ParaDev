# Project Localization REST API Table Helper Progress

Date: 2026-06-15 07:53 +0800

Linear: none

## Done

- Migrated the public project package facade API reference renderer to the shared API-table Markdown helpers.
- Migrated the public localization facade API reference renderer to the shared API-table Markdown helpers.
- Migrated the public REST package facade API reference renderer to the shared API-table Markdown helpers.
- Preserved generated API schemas, row ordering, manual reference output, CLI JSON output, and CLI Markdown output.

## Verification

- `rtk uv run python -m py_compile src/paradev/project/api.py src/paradev/localization/api.py src/paradev/api/api.py`
- `rtk uv run pytest tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade tests/test_cli.py::test_project_facade_api_cli_outputs_table_json tests/test_cli.py::test_project_facade_api_cli_outputs_reference_markdown tests/test_cli.py::test_localization_api_cli_outputs_table_json tests/test_cli.py::test_localization_api_cli_outputs_reference_markdown tests/test_cli.py::test_rest_facade_api_cli_outputs_table_json tests/test_cli.py::test_rest_facade_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/project/api.py src/paradev/localization/api.py src/paradev/api/api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/project/api.py src/paradev/localization/api.py src/paradev/api/api.py`
- `rtk git diff --check -- src/paradev/project/api.py src/paradev/localization/api.py src/paradev/api/api.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated Heaven-style skill, desktop, PIHC3, logo, loader, and `node_modules/` changes from other workers.

## Next

- Continue migrating clean generated-reference renderers to `paradev._api_table_markdown`.
- Keep avoiding build loader, HoI4 package internals, desktop app files, and PIHC3 progress files while those slices remain active elsewhere.
