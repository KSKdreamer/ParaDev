# Frontend API Binding Index Reference Progress

Date: 2026-06-14 02:26 +0800

Linear: none

## Done

- Added generated Binding Index tables to the frontend API reference renderer.
- The new table maps SDK/CLI/REST/MCP/LSP surface call keys back to canonical frontend operation ids from `contract["index"]["binding"]`.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention that the generated reference now renders both surface coverage and the reverse binding table.
- Added targeted architecture and CLI assertions for representative CLI, REST, and MCP binding rows.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_contract_indexes_every_surface_binding_and_openapi_annotation tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, and progress-note changes from other workers.

## Next

- Continue consolidating API-reference tables around SDK-owned contract indexes instead of row scans or hand-maintained surface maps.
- Consider a compact index-dimension summary table if downstream readers need one overview of available group/status/mode/surface/binding/payload/workspace-section projections.
