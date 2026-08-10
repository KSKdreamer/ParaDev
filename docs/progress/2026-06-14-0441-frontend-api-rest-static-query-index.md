# Frontend API REST Static Query Index Progress

Date: 2026-06-14 04:41 +0800

Linear: none

## Done

- Added generated REST Static Query Index tables to the frontend API reference renderer.
- The new table expands fixed REST binding query parameters into one row per parameter, including rendered value, canonical operation id, method, path, and JSON value type.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the REST static-query audit table.
- Added targeted architecture and CLI assertions for inspection selectors, build emit flags, and PDX parse toggles.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md docs/progress/2026-06-14-0441-frontend-api-rest-static-query-index.md`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, project-test, and progress-note changes from other workers.

## Next

- Continue consolidating REST, SDK, CLI, MCP, and frontend-facing API maintenance tables around generated contract metadata.
