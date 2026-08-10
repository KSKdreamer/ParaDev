# 2026-06-14 09:22 - Frontend API Index Operation Helper

## Scope

- Added a private `_frontend_api_index_operation_ids(...)` helper in `src/paradev/sdk/frontend_api.py`.
- Routed status, mode, surface, payload, and workspace-section operation-id lookup helpers through the shared index reader.
- Preserved public SDK helper names and error behavior while removing repeated index extraction and list-copy guards.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
  - 3 passed in 1.02s.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
  - OK: 1 file(s) - no banned imports.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`
  - All done; 1 file would be left unchanged.
