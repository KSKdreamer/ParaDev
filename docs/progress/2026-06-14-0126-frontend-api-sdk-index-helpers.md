# Frontend API SDK Index Helper Progress

Date: 2026-06-14 01:26 +0800

Linear: none

## Done

- Added public Python SDK helpers for frontend API surface, payload, and workspace-section operation-id indexes.
- Exported the helpers from `paradev.sdk` and documented them in the SDK manual, frontend API guide, developer manual, architecture interface map, and generated frontend API reference.
- Regenerated the checked-in frontend API Markdown reference and desktop TypeScript contract after the SDK renderer changes.
- Preserved existing frontend behavior; the change only adds maintained lookup paths over indexes that were already present in the contract.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_lookup_helpers_return_canonical_rows tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_contract_indexes_every_surface_binding_and_openapi_annotation tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_architecture.py::test_desktop_frontend_api_helper_consumes_generated_contract tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_typescript_contract`
- `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiBindingIndex.test.ts src/data/frontendApiSummary.test.ts`
- `rtk npm --prefix apps/desktop exec tsc -- --noEmit -p apps/desktop/tsconfig.json`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run in this slice to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, PIHC3, loader, and progress-note changes owned by other workers.

## Next

- Continue consolidating frontend-facing APIs around SDK-owned lookup helpers and generated reference tables.
- Consider adding typed Python metadata accessors for operation groups and statuses if more callers start reading raw `contract["index"]` maps directly.
