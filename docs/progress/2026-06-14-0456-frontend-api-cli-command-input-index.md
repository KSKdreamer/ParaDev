# Frontend API CLI Command Input Index Progress

Date: 2026-06-14 04:56 +0800

Linear: none

## Done

- Added generated CLI Command Input Index tables to the frontend API reference renderer.
- The new table lists CLI-bound operation inputs with command string, operation id, field, type, required/default state, normalizer target bucket, and adapter-side alias.
- Refactored MCP and CLI input-index rendering through a shared binding-input helper keyed by surface and binding field.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the CLI input audit table.
- Added targeted architecture and CLI assertions for project creation, module listing, build emit, and PDX parse CLI input rows.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- ``rtk rg -n 'CLI Command Input Index|_frontend_api_cli_command_input_index_rows|_frontend_api_binding_input_index_rows|\| `new` \| `project\.create` \| `path`|\| `modules` \| `module\.list` \| `profile`' src/paradev/sdk/frontend_api.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md tests/test_architecture.py tests/test_cli.py``
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md docs/progress/2026-06-14-0456-frontend-api-cli-command-input-index.md`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, project-test, and progress-note changes from other workers.

## Next

- Continue consolidating REST, SDK, CLI, MCP, and frontend-facing API maintenance tables around generated contract metadata.
