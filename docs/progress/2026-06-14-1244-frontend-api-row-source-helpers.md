# 2026-06-14 12:44 Frontend API Row Source Helpers

## Focus

- Continue reducing duplicate table-renderer plumbing in the SDK-owned frontend API reference.
- Keep rendered API tables stable while making row sources more reusable.

## Changes

- Reused `_frontend_api_operation_rows` inside `_frontend_api_binding_input_index_rows` instead of duplicating contract operation validation.
- Extracted `_frontend_api_payload_index_keys` for payload index ordering, including the existing rule that places the literal `untyped` payload last.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style-0.1.1.1/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- Full-suite tests are deferred to reduce CPU contention with active PIHC2-to-PIHC3 migration work.
- Staging remains limited to `src/paradev/sdk/frontend_api.py` and this progress note; desktop files, PIHC3 migration files, generated frontend assets, and `node_modules` are intentionally untouched.
