# Frontend API Group Status Helper Progress

Date: 2026-06-14 01:53 +0800

Linear: none

## Done

- Added public Python SDK helpers `get_frontend_api_group_operation_ids(...)` and `get_frontend_api_status_operation_ids(...)`.
- Exported the helpers from `paradev.sdk` and documented them in the SDK manual, frontend API guide, developer manual, architecture boundary doc, and generated frontend API reference.
- Replaced SDK manual example reads of raw `api["index"]["group"]` and `api["index"]["status"]` with the new helpers.
- Added targeted tests for canonical order, copy semantics, and validation errors.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids tests/test_architecture.py::test_frontend_api_lookup_helpers_return_canonical_rows tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, and progress-note changes from other workers.

## Next

- Continue moving frontend API consumers from raw generated indexes toward named SDK and TypeScript helpers.
- Consider whether TypeScript needs a status-operation helper if GUI code starts grouping by implementation status.
