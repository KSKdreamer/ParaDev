# Summary Reference Sections Progress

Date: 2026-06-16 08:24 CST

Linear: none

## Done

- Added `api_summary_reference_sections(...)` for generated API references that use custom table sections.
- Routed Project inspection and surface contract reference renderers through the shared summary-section helper.
- Added focused unit coverage for summary plus custom reference sections.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py src/paradev/surfaces/__init__.py src/paradev/sdk/project.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py src/paradev/surfaces/__init__.py src/paradev/sdk/project.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_project_inspection_reference_lists_contract_indexes tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries -q`
- Generated API reference parity checked 29 catalog entries.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py src/paradev/surfaces/__init__.py src/paradev/sdk/project.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py src/paradev/surfaces/__init__.py src/paradev/sdk/project.py tests/test_api_table.py`

## Risks Or Blockers

- Full test suite was intentionally deferred to reduce CPU pressure.
- Unrelated dirty files remain in the shared worktree and were not touched.

## Next

- Continue looking for API reference renderer duplication that can be collapsed with generated-reference parity checks.
