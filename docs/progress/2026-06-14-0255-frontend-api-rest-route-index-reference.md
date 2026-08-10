# Frontend API REST Route Index Reference Progress

Date: 2026-06-14 02:55 +0800

Linear: none

## Done

- Added generated REST Route Index tables to the frontend API reference renderer.
- The new table groups canonical frontend operation ids by structured REST method, path, and query values from each operation's machine-readable `bindings.rest` object.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the structured REST route table for GUI clients and OpenAPI audits.
- Added targeted architecture and CLI assertions for shared routes, query-disambiguated inspection routes, and boolean query values.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, and progress-note changes from other workers.

## Next

- Continue improving generated API references with structured per-surface tables where callers still need to parse display strings.
- Consider a similar structured MCP tool index if the generic binding table remains too broad for MCP adapter audits.
