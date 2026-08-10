# 2026-06-16 12:20 API table row guards

## Scope

- Hardened `table_rows(...)` so scalar top-level table row collections fail with a contextual list-like error before character iteration.
- Added direct `table_rows(...)` regression coverage for normal row rendering, scalar row collections, and scalar nested rows.
- Kept generated API reference output unchanged.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_architecture_cli_outputs_api_table_markdown -q`
- `rtk uv run python - <<'PY' ... PY` API catalog generated-vs-checked-in parity probe: `checked=29 mismatches=0 missing=0`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`

Full suite deferred to avoid competing with active PIHC3 and desktop work.
