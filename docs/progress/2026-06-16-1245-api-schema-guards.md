# API Schema Guards Progress

Date: 2026-06-16 12:45

Linear: none

## Done

- Routed `api_standard_table(...)` and `api_indexed_table(...)` schema values through the shared API table string-name guard.
- Preserved valid API table payload behavior while making invalid non-string schema values fail with a contextual `TypeError`.
- Added focused tests for non-string schema values on both shared table builders.

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
