# Frontend API SDK Call Index Reference Progress

Date: 2026-06-14 03:11 +0800

Linear: none

## Done

- Added generated SDK Call Index tables to the frontend API reference renderer.
- The new table maps SDK call strings back to canonical frontend operation ids from `contract["index"]["binding"]["sdk"]`.
- Reused one surface-binding row renderer for SDK, MCP, and CLI audit tables.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the SDK-call-to-operation table for Python SDK audits.
- Added targeted architecture and CLI assertions for representative one-operation and shared SDK call rows.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, and progress-note changes from other workers.

## Next

- Consider whether LSP method rows need their own generated audit table or whether the Surface and Binding indexes are enough for the smaller LSP surface.
