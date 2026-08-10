# API Table List Value Validation

## Done

- Tightened declared API table list fields so row copies and index expansion reject non-string list items instead of silently stringifying them.
- Added regression coverage for list-valued API index keys and copied API row fields.
- Kept the change outside PIHC3 migration and desktop surfaces.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table.py tests/test_api_table.py`
- `rtk uv run black src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_table_json -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py tests/test_api_table.py`

## Risks

- Full-suite tests were intentionally deferred to keep CPU free while other workers handle PIHC2 to PIHC3 migration.
- Existing dirty worktree changes, including desktop and PIHC3 files, were left untouched.

## Next

- Continue tightening generated API-reference helpers around explicit string/list contracts.
