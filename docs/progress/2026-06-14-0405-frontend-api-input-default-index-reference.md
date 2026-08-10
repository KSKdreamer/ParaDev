# Frontend API Input Default Index Progress

Date: 2026-06-14 04:05 +0800

Linear: none

## Done

- Added generated Input Default Index tables to the frontend API reference renderer.
- The new table lists every input field with an SDK-owned default, including operation id, type, default value, normalizer target bucket, adapter-side alias, and required state.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the default-value audit table.
- Added targeted architecture and CLI assertions for project path defaults, safe boolean defaults, empty-list defaults, alias routing, and projection defaults.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, project-test, and progress-note changes from other workers.

## Next

- Continue consolidating frontend-facing API maintenance tables around generated contract metadata instead of duplicated hand-maintained lists.
