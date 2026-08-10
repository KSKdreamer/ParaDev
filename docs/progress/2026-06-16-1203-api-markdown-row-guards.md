# API Markdown Row Guards Progress

Date: 2026-06-16 12:03 CST

Linear: N/A

## Done

- Hardened generated API Markdown field-table rendering so scalar row collections, non-mapping rows, scalar table fields, and scalar field-mode lists fail with contextual `TypeError` messages.
- Added regression tests for malformed Markdown field-table inputs while preserving valid generated Markdown output.

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

- Continue tightening generated API reference helpers in small, reviewable slices.
