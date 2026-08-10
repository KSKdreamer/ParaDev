# API Index Reserved Guards Progress

Date: 2026-06-16 12:49

Linear: none

## Done

- Added a reserved payload-field guard for custom `api_indexed_table(...)` index names.
- Prevented index specs from colliding with `schema`, `row_count`, or `rows`, preserving the fixed generated API table payload shape.
- Added focused tests for all reserved index names.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table.py tests/test_api_table.py`
- `rtk uv run black src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_architecture_cli_outputs_api_table_markdown -q`
- `rtk uv run python - <<'PY' ... PY` API catalog generated-vs-checked-in parity probe: `checked=29 mismatches=0 missing=0`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py tests/test_api_table.py`

## Risks Or Blockers

- Full-suite tests deferred to avoid competing with ongoing PIHC3 migration work.
- Existing unrelated dirty files remain untouched.

## Next

- Run diff checks, then commit and push the narrow slice.
