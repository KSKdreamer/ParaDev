# Custom Reference Table Section Progress

## Scope

- Added `api_table_section()` for generated API reference sections that use custom row renderers.
- Routed Project Inspection and Surface Contract reference renderers through `api_reference_markdown()`, `api_summary_section()`, and `api_table_section()`.
- Kept contract-specific row renderers local so generated rows and docs remain unchanged.
- Added focused helper coverage for the custom table-section formatter.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py src/paradev/sdk/project.py src/paradev/surfaces/__init__.py tests/test_api_table.py`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py src/paradev/sdk/project.py src/paradev/surfaces/__init__.py tests/test_api_table.py`
- `rtk uv run python - <<'PY' ... PY`: checked 29 generated API references against disk.
- `rtk bash scripts/test.bash tests/test_api_table.py tests/test_architecture.py::test_project_inspection_reference_lists_contract_indexes tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_inspections_cli_outputs_reference_markdown tests/test_cli.py::test_architecture_cli_outputs_surface_contract_reference_markdown -q`: 36 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py src/paradev/sdk/project.py src/paradev/surfaces/__init__.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py src/paradev/sdk/project.py src/paradev/surfaces/__init__.py tests/test_api_table.py`

Full-suite tests were deferred to keep the active loop light.
