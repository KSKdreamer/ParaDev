# Module Batch Request Progress

Date: 2026-06-21 04:48

Linear: TAL-000

## Done

- Added `Project.module_batch_edit_request(...)` to normalize generated module edit rows into a canonical `paradev.module.batch_edit_request.v1` JSON request.
- Added `paradev module-batch-request` for CLI request generation from `--request`, `--request-json`, or repeated `--edit-json`, with JSON output ready for `module-batch-edit --request -`.
- Registered the new command in the CLI and Project API contracts, regenerated the Project API, CLI API, and API catalog references, and updated the modules manual examples.

## Verification

- `rtk uv run pytest tests/test_project.py -k "module_batch or module_files_batch_edit" -q`
- `rtk uv run pytest tests/test_cli.py -k "module_batch_request or module_batch_edit_cli" -q`
- `rtk uv run pytest tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_project_api_cli_outputs_table_json tests/test_cli.py::test_project_api_cli_outputs_reference_markdown -q`
- `rtk uv run paradev module-batch-edit projects/PIHC3 --request /tmp/paradev-pihc3-module-batch-request.json --dry-run --json`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
- `rtk git diff --check -- src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_project.py tests/test_cli.py tests/test_architecture.py docs/user-manual/modules-and-collections.md docs/user-manual/project-api-reference.md docs/user-manual/cli-api-reference.md docs/user-manual/api-catalog-reference.md`

## Risks Or Blockers

- The request builder validates JSON shape, module id syntax, relative paths, duplicate request targets, text type, and encoding. It deliberately leaves project target existence validation to `module-batch-edit --dry-run` or write mode.

## Next

- Continue reducing PIHC3 migration scripts toward SDK/CLI request generation instead of hand-authored JSON payloads.
