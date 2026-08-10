# Frontend API Selector Progress

Date: 2026-06-20 02:07 +0800

Linear: none

## Done

- Added `get_frontend_api_selection(...)` as the shared SDK selector for the full frontend API contract, operation rows, group slices, and operation form projections.
- Routed CLI `frontend-api`, `--operation`, `--group`, and `--operation --form`, REST `GET /frontend-api`, and MCP `frontend_api` metadata through the shared selector.
- Regenerated SDK, CLI, MCP, frontend, SDK CLI, and API catalog reference docs.
- Updated architecture docs and tests to lock selector parity across SDK, CLI, REST, MCP, static API tables, and generated TypeScript metadata.

## Verification

- Red run: targeted SDK/CLI/MCP/frontend contract tests failed before implementation because `get_frontend_api_selection` was absent and surface metadata still referenced split selector helpers.
- Focused green run: `15 passed in 1.15s`.
- Affected module run: `tests/test_architecture.py tests/test_cli.py` passed with `222 passed in 14.41s`.
- Heaven-style scan passed for changed Python and test paths.
- `scripts/flake.bash --all --paths ...` and `scripts/flake.bash --ci --paths ...` both passed for changed Python and test paths.

## Risks Or Blockers

- Full suite intentionally not run for this small surface-table slice to preserve CPU for the parallel PIHC3 migration work.
- `apps/desktop/src/generated/frontendApi.ts` had unrelated pre-existing generated additions; this slice only stages the frontend selector string replacements.
- Unrelated dirty PIHC3, desktop, documentation, and skill changes remain untouched.

## Next

- Continue reducing split selector metadata in generated API tables, and keep isolating generated artifacts before staging.
