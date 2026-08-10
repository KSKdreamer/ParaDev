# API Name Guards Progress

Date: 2026-06-16 12:41

Linear: none

## Done

- Added shared API table helpers that distinguish list-like collections from required string field names.
- Routed API table index fields, value fields, row field lists, list-field markers, skip-empty markers, and indexed-table spec entries through explicit string-name validation.
- Added focused error-path tests for non-string field names so invalid API table specs fail with contextual `TypeError`s instead of falling through to row lookup failures.

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
