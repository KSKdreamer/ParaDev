# Frontend API TypeScript ID Rows

Date: 2026-06-14 16:49 Asia/Shanghai

## Summary

- Added `_frontend_api_row_ids` beside the shared frontend API row extractors.
- Routed TypeScript operation, group, and workspace section ID arrays through the shared mapping-row extraction path.
- Kept generated TypeScript IDs, ordering, and contract serialization behavior unchanged for the current frontend API contract.

## Verification

- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_cli.py::test_frontend_api_cli_outputs_typescript_contract`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- This is a behavior-preserving maintainability slice scoped to frontend API TypeScript renderer row extraction.
- Full-suite tests were intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
