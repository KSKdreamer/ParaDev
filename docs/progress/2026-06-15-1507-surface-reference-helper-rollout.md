# Surface Reference Helper Rollout Progress

## Scope

- Added `api_surface_reference_markdown()` for generated API references grouped by surface, with optional feature indexing.
- Routed PDX, LSP, architecture, and catalog API reference renderers through the shared helper.
- Removed redundant local `_..._api_standard_table_rows()` wrappers from those renderers.
- Added focused helper coverage for feature+surface and surface-only reference documents.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/hb/__init__.py tests/test_api_table.py`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/hb/__init__.py tests/test_api_table.py`
- `rtk uv run python - <<'PY' ... PY`: checked 29 generated API references against disk.
- `rtk bash scripts/test.bash tests/test_api_table.py tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces tests/test_architecture.py::test_api_catalog_lists_generated_references -q`: 35 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/hb/__init__.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/hb/__init__.py tests/test_api_table.py`

Full-suite tests were deferred to keep the active loop light.
