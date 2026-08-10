# Frontend API Binding Index Helper Progress

Date: 2026-06-14 01:42 +0800

Linear: none

## Done

- Added `get_frontend_api_binding_index(surface)` as a public Python SDK helper for copied surface-specific binding maps.
- Routed `get_cli_contract()` and `get_mcp_contract()` through the helper instead of reading raw `contract["index"]["binding"]`.
- Updated SDK, frontend API, developer, architecture, and generated reference docs so adapter authors use the helper for whole CLI/MCP binding slices.
- Added targeted tests for helper copy semantics and CLI/MCP contract mirroring.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_architecture.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_architecture.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, and progress-note changes from other workers.

## Next

- Continue replacing raw frontend API index reads with explicit SDK helpers where callers need stable grouped views.
- Consider status/group operation-id helpers if Python clients keep reading `contract["index"]["group"]` or `contract["index"]["status"]` directly.
