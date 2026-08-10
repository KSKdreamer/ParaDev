# Frontend API REST Dynamic Query Field Index Progress

Date: 2026-06-14 04:46 +0800

Linear: none

## Done

- Added generated REST Dynamic Query Field Index tables to the frontend API reference renderer.
- The new table lists frontend inputs that become REST query parameters at request-plan time, excluding REST path parameters and JSON body fields.
- The table also shows static defaults for query fields that can override a fixed REST binding query when explicitly submitted.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the dynamic query-field audit table.
- Added targeted architecture and CLI assertions for project creation, module list filters, build emit flags, and PDX parse toggles.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md docs/progress/2026-06-14-0446-frontend-api-rest-dynamic-query-field-index.md`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, project-test, and progress-note changes from other workers.

## Next

- Continue consolidating REST, SDK, CLI, MCP, and frontend-facing API maintenance tables around generated contract metadata.
