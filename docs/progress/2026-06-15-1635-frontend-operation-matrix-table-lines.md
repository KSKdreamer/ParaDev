# Frontend Operation Matrix Table Lines Progress

Date: 2026-06-15 16:35

Linear: Not updated

## Done

- Replaced frontend operation-matrix header/separator helpers in `src/paradev/sdk/frontend_api.py` with shared `_frontend_api_table_lines` rendering.
- Added stable label tuples for the full frontend reference matrix and compact SDK/CLI matrix.
- Removed the now-unused `_frontend_api_reference_header`, `_frontend_api_reference_separator`, `_frontend_api_sdk_cli_header`, and `_frontend_api_sdk_cli_separator` helpers.
- Confirmed no literal Markdown table-header strings remain in `src/paradev/sdk/frontend_api.py`.

## Verification

- `rtk uv run black src/paradev/sdk/frontend_api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python - <<'PY' ...` checked all 29 generated API references against checked-in docs.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Risks Or Blockers

- Full-suite tests were deferred to keep CPU available for concurrent PIHC migration work.
- Existing unrelated workspace changes were left untouched.

## Next

- Continue scanning generated API reference renderers for local helper pairs that should delegate to `api_table_lines` or `api_table_section`.
