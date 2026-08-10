# Frontend API TypeScript Group Status Index Progress

Date: 2026-06-14 02:07 +0800

Linear: none

## Done

- Added typed desktop helpers `frontendApiGroupIndex`, `frontendApiStatusIndex`, `getFrontendApiGroupOperationIds(...)`, and `getFrontendApiStatusOperationIds(...)`.
- Routed `getFrontendApiGroupOperations(...)` through the generated group index so desktop group slices do not scan operation rows.
- Added generated Group Index and Status Index tables to the frontend API reference renderer.
- Updated frontend API, SDK, architecture, and developer docs to point Python and TypeScript clients at named group/status helpers.
- Added targeted Vitest and architecture guard coverage for the new TypeScript helper surface.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiBindingIndex.test.ts src/data/frontendApiSummary.test.ts`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_desktop_frontend_api_helper_consumes_generated_contract tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, and progress-note changes from other workers.

## Next

- Continue moving desktop/API-table consumers from operation-row scanning to named SDK or TypeScript index helpers.
- Consider adding focused API-reference tests for generated group/status index table content if the table grows more complex.
