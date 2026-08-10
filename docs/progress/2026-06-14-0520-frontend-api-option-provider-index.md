# Frontend API Option Provider Index Progress

Date: 2026-06-14 05:20 +0800

Linear: none

## Done

- Added generated Option Provider Index tables to the frontend API reference renderer.
- The new table groups dynamic option-source consumers by provider operation, including field count, consumer fields, consumer operations, values paths, required context, forwarded values, and fixed filters.
- Reused the existing option-source metadata and path/filter rendering conventions.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the inverse option-provider audit table.
- Added targeted architecture and CLI assertions for `collection.sources`, `build.artifacts`, and filtered `module.templates` provider rows.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- ``rtk rg -n 'Option Provider Index|_frontend_api_option_provider_index_rows|\| `collection\.sources` \| 2|\| `build\.artifacts` \| 6|\| `module\.templates` \| 17|authoring_ready=true' src/paradev/sdk/frontend_api.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md tests/test_architecture.py tests/test_cli.py``
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md docs/progress/2026-06-14-0520-frontend-api-option-provider-index.md`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, project-test, and progress-note changes from other workers.

## Next

- Continue consolidating dynamic dependency, feature-level, surface-level, and input-level API maintenance tables around generated frontend contract metadata.
