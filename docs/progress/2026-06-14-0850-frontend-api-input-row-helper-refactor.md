# Frontend API Input Row Helper Refactor

## Scope

- Continued the behavior-preserving frontend API renderer cleanup stream.
- Added private operation/input traversal helpers for contract and grouped-operation table builders.
- Routed option source/provider rows and form/input detail indexes through the shared traversal helper.
- Routed the legacy reference and SDK/CLI summary rows through `_frontend_api_table_row` so table row formatting has one private implementation.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Notes

- Full-suite tests were intentionally skipped to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- No PIHC migration files were edited in this slice.
