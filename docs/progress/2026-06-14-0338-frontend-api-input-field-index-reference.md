# Frontend API Input Field Index Reference Progress

Date: 2026-06-14 03:38 +0800

Linear: none

## Done

- Added generated Input Field Index tables to the frontend API reference renderer.
- The new table lists every `operation.inputs[*]` row with field name, operation id, type, required/default state, finite choices, frontend-to-SDK alias, and option-source provider.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the input-field audit table.
- Added targeted architecture and CLI assertions for module creation, build artifact aliasing, diagnostic severity choices, and LSP position fields.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, project-test, and progress-note changes from other workers.

## Next

- Continue consolidating frontend-facing API maintenance tables around generated contract metadata instead of duplicated hand-maintained lists.
