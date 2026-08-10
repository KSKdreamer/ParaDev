# API Reference Newline Parity Progress

Date: 2026-06-16 11:32 CST

Linear: N/A

## Done

- Normalized the shared generated API reference renderer to return newline-terminated Markdown.
- Strengthened checked-in manual parity tests to compare exact file contents instead of trimming final newlines.
- Verified every cataloged API reference render helper now matches its `docs/user-manual/*-reference.md` file exactly.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py tests/test_api_table.py tests/test_architecture.py`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py tests/test_architecture.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_architecture_cli_outputs_api_table_markdown -q`
- Generated-reference parity over all 29 `API_CATALOG_SOURCE_ROWS`: `checked=29 mismatches=0 missing=0`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py tests/test_architecture.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py tests/test_architecture.py`
- Full suite intentionally deferred to keep CPU free for parallel PIHC3 migration workers.

## Risks Or Blockers

- Public `render_*_reference_markdown()` helpers that use the shared renderer now return a final newline; CLI output stays stable because markdown commands already print `render(...).rstrip()`.

## Next

- Continue hardening generated API table/reference infrastructure while preserving valid SDK, CLI, REST, MCP, LSP, frontend, and docs output.
