# API Markdown Index Spec Guard Progress

Date: 2026-06-16 13:09

Linear: n/a

## Done

- Added runtime string validation for API Markdown index-section spec entries.
- Covered invalid non-string spec values with a focused regression test.
- Preserved valid generated-reference spec behavior while converting malformed specs into contextual `TypeError`s.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run black src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_architecture_cli_outputs_api_table_markdown -q`
- API catalog parity probe: checked 29 docs, 0 mismatches, 0 missing.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py tests/test_api_table.py`

## Risks Or Blockers

- Full-suite tests were deferred to avoid competing with parallel PIHC3 migration work.
- No active PR reviews were available from `rtk gh pr status`.

## Next

- Continue strengthening generated API reference helpers and table contracts in small verified slices.
