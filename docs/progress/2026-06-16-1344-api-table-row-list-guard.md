# API Table Row List Guard Progress

Date: 2026-06-16 13:44

Linear: none

## Done

- Added a contextual row-collection guard so API table builders reject mappings as row lists before iterating keys.
- Added focused regression tests across `api_value_indexes`, `api_standard_table`, and `api_indexed_table`.
- Checked `gh pr status`; there are no active PR review opinions to address in this pass.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table.py tests/test_api_table.py`
- `rtk uv run black src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_architecture_cli_outputs_api_table_markdown -q`
- API catalog parity probe: `checked=29 mismatches=0 missing=0`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py tests/test_api_table.py`

## Risks Or Blockers

- Full-suite tests were deferred to avoid unnecessary CPU load during parallel PIHC3 work.
- The worktree contains unrelated desktop, PIHC3, skill, logo, and `node_modules` changes; this slice stages only the API table helper, its tests, and this note.

## Next

- Continue tightening generated API table payload validation around index specifications and copied row fields.
