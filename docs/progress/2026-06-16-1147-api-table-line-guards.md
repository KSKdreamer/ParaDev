# API Table Line Guards Progress

Date: 2026-06-16 11:47 CST

Linear: N/A

## Done

- Hardened API Markdown table assembly so scalar table-row collections fail with a contextual `TypeError` instead of being expanded character by character.
- Hardened optional API table section body lines with the same shared list guard.
- Added regression tests for both invalid input shapes while preserving existing Markdown output behavior.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_architecture_cli_outputs_api_table_markdown -q`
- `rtk uv run python - <<'PY' ... PY` API catalog parity probe: checked 29 references, 0 mismatches, 0 missing.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`

## Risks Or Blockers

- Full-suite testing deferred to reduce CPU use during the active multi-agent migration window.
- Existing unrelated PIHC3, desktop, skill, and `node_modules/` worktree changes were left untouched.

## Next

- Continue tightening generated API reference helper input validation in small, reviewable slices.
