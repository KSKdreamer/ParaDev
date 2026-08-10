# 2026-06-14 12:35 Frontend API REST Route Index Row

## Focus

- Continue the frontend API reference renderer refactor in a small behavior-preserving slice.
- Keep SDK-owned API tables modular and easier to maintain while avoiding PIHC3 migration files, desktop work, generated frontend assets, and `node_modules`.

## Changes

- Extracted the REST route index markdown row construction into `_frontend_api_rest_route_index_row`.
- Left route grouping, ordering, query formatting, and operation-id detail behavior unchanged.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- Full-suite tests are deferred to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- Commit staging is limited to `src/paradev/sdk/frontend_api.py` and this progress note; `node_modules` remains unstaged.
