# Frontend API Mode Index Progress

Date: 2026-06-14 02:21 +0800

Linear: none

## Done

- Added `index["mode"]` to the canonical frontend API contract with stable `read` and `write` operation-id lists.
- Added public Python SDK helper `get_frontend_api_mode_operation_ids(...)` and exported it from `paradev.sdk`.
- Added generated TypeScript `PARADEV_FRONTEND_API_MODE_VALUES` / `ParaDevFrontendApiMode` plus desktop helper exports `frontendApiModeValues`, `frontendApiModeIndex`, and `getFrontendApiModeOperationIds(...)`.
- Added generated Read/Write Mode Index tables to the frontend API reference.
- Updated SDK, frontend API, architecture, and developer docs to steer clients toward named read/write helpers instead of filtering operation rows by `mutates`.
- Added targeted Python and Vitest coverage for mode ordering, copy semantics, validation, generated TypeScript symbols, and helper alignment.

## Verification

- `rtk uv run python - <<'PY' ... get_frontend_api_mode_operation_ids(...) ... PY`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_architecture.py::test_desktop_frontend_api_helper_consumes_generated_contract tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiBindingIndex.test.ts src/data/frontendApiSummary.test.ts`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py tests/test_cli.py`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- Desktop build still reports the existing Vite chunk-size warning.
- The worktree still contains unrelated desktop, loader, PIHC3, and progress-note changes from other workers.

## Next

- Continue moving API-table and dashboard consumers from row scans toward named SDK/TypeScript index helpers.
- Consider adding a compact machine-readable index summary table if downstream docs need one place to enumerate all available index dimensions.
