# Frontend API SDK Call Input Index Progress

Date: 2026-06-14 05:01 +0800

Linear: none

## Done

- Added generated SDK Call Input Index tables to the frontend API reference renderer.
- The new table lists SDK-bound operation inputs with SDK call string, operation id, field, type, required/default state, normalizer target bucket, and adapter-side alias.
- Reused the shared binding-input helper through the SDK surface and `call` binding key.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the SDK input audit table.
- Added targeted architecture and CLI assertions for project creation, module listing, build emit, and PDX parse SDK input rows.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- ``rtk rg -n 'SDK Call Input Index|_frontend_api_sdk_call_input_index_rows|\| `Project\.create` \| `project\.create` \| `path`|\| `Project\.inspect\('''modules'''\)` \| `module\.list` \| `profile`|\| `Project\.build` \| `build\.emit` \| `emit_artifacts`|\| `parse_pdx_file` \| `pdx\.parse` \| `include_tokens`' src/paradev/sdk/frontend_api.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md tests/test_architecture.py tests/test_cli.py``
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md docs/progress/2026-06-14-0501-frontend-api-sdk-call-input-index.md`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, project-test, and progress-note changes from other workers.

## Next

- Continue consolidating REST, SDK, CLI, MCP, and frontend-facing API maintenance tables around generated contract metadata.
