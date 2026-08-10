# Frontend Reference Table Sections Progress

## Scope

- Extended `api_table_section()` with optional heading level and body text for custom generated-reference tables.
- Routed the first Frontend API reference index cluster through the shared table-section helper.
- Kept frontend-specific row renderers local so generated rows and docs remain unchanged.
- Added focused helper coverage for level-3 table sections with descriptive body text.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py src/paradev/sdk/frontend_api.py tests/test_api_table.py`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py src/paradev/sdk/frontend_api.py tests/test_api_table.py`
- `rtk uv run python - <<'PY' ... PY`: checked 29 generated API references against disk.
- `rtk bash scripts/test.bash tests/test_api_table.py tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_index_catalog_documents_lookup_helpers tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown -q`: 35 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py src/paradev/sdk/frontend_api.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py src/paradev/sdk/frontend_api.py tests/test_api_table.py`

Full-suite tests were deferred to keep the active loop light.
