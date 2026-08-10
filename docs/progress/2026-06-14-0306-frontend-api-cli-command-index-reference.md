# Frontend API CLI Command Index Reference Progress

Date: 2026-06-14 03:06 +0800

Linear: none

## Done

- Added generated CLI Command Index tables to the frontend API reference renderer.
- The new table maps CLI command strings back to canonical frontend operation ids from `contract["index"]["binding"]["cli"]`.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the CLI command-to-operation table for adapter audits.
- Added targeted architecture and CLI assertions for representative one-operation and shared-command CLI rows.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, and progress-note changes from other workers.

## Next

- Continue replacing display-string parsing needs with structured generated per-surface tables.
