# Frontend API Form Control Index Progress

Date: 2026-06-14 04:14 +0800

Linear: none

## Done

- Added generated Form Control Index tables to the frontend API reference renderer.
- The new table lists every frontend input's SDK-derived control kind, operation id, type, required state, option-source provider, and static choices.
- Aligned `get_frontend_api_form(...)` with the TypeScript helper by exposing dynamic option-source fields as `combobox` controls instead of plain text/path controls.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the form-control audit table.
- Added targeted architecture and CLI assertions for combobox, select, textarea, json, number, checkbox, and path controls.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_form_contract_is_derived_from_operation_inputs tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_operation_form_contract_json`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, project-test, and progress-note changes from other workers.

## Next

- Continue consolidating frontend-facing API maintenance tables around generated contract metadata instead of duplicated hand-maintained lists.
