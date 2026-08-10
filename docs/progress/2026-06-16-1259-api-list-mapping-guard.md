# API List Mapping Guard Progress

Date: 2026-06-16 12:59

Linear: n/a

## Done

- Added an explicit mapping guard for API table fields declared as list-valued.
- Covered both API value index generation and copied API row list-field behavior.
- Preserved valid list-like iterable behavior while preventing dictionaries from being copied as their key lists.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table.py tests/test_api_table.py`
- `rtk uv run black src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_architecture_cli_outputs_api_table_markdown -q`
- API catalog parity probe: checked 29 docs, 0 mismatches, 0 missing.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py tests/test_api_table.py`

## Risks Or Blockers

- Full-suite tests were deferred to keep CPU available for parallel PIHC3 migration workers.
- No active PR reviews were available from `rtk gh pr status`.

## Next

- Continue tightening API table helpers and reference contracts in small, independently verifiable commits.
