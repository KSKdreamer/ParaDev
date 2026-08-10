# API Table Lines Helper Progress

Date: 2026-06-15 16:29

Linear: Not updated

## Done

- Added `api_table_lines` to `src/paradev/_api_table_markdown.py` for untitled API table blocks.
- Updated `api_table_section` to delegate header-and-row rendering to the new helper.
- Converted the frontend API English/Chinese summary tables and compact SDK/CLI feature summary table in `src/paradev/sdk/frontend_api.py` to `api_table_lines`.
- Added focused coverage for header escaping and row pass-through in `tests/test_api_table.py`.
- Confirmed no manual Markdown table-header patterns remain in `src/paradev/sdk/frontend_api.py`.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py src/paradev/sdk/frontend_api.py tests/test_api_table.py`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py src/paradev/sdk/frontend_api.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py::test_api_table_lines_returns_header_and_rows tests/test_api_table.py::test_api_table_section_returns_custom_table_section -q`
- `rtk uv run python - <<'PY' ...` checked all 29 generated API references against checked-in docs.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py src/paradev/sdk/frontend_api.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py src/paradev/sdk/frontend_api.py tests/test_api_table.py`

## Risks Or Blockers

- Full-suite tests were deferred to keep CPU available for concurrent PIHC migration work.
- Existing unrelated workspace changes were left untouched.

## Next

- Continue scanning generated API reference renderers for duplicated Markdown table assembly that can use the shared table helpers.
