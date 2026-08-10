# API Index Mapping Guards Progress

Date: 2026-06-16 11:37 CST

Linear: N/A

## Done

- Routed generated API index-section rendering through a shared mapping-shape validator.
- Replaced the table-spec index cast path with the same validator so malformed scalar indexes fail with contextual `TypeError`.
- Added focused error-path coverage for direct `api_index_section(...)` and table-driven `api_index_sections(...)`.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_sdk_api_table_lists_facade_exports -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_architecture_cli_outputs_api_table_markdown -q`
- Generated-reference parity over all 29 `API_CATALOG_SOURCE_ROWS`: `checked=29 mismatches=0 missing=0`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- Full suite intentionally deferred to keep CPU free for parallel PIHC3 migration workers.

## Risks Or Blockers

- None known for valid generated reference indexes; malformed scalar indexes now raise contextual `TypeError` instead of failing later with generic attribute errors.

## Next

- Continue hardening generated API table/reference infrastructure while preserving valid SDK, CLI, REST, MCP, LSP, frontend, and docs output.
