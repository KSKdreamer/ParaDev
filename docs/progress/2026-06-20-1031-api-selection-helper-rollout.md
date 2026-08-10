# 2026-06-20 10:31 API selection helper rollout

## Summary

- Migrated catalog, localization, LSP, package, and PDX API selection tests to the shared selector-contract helper.
- Preserved each file's local table row-count, surface/index, and generated reference parity assertions.
- Kept SDK, CLI, REST, MCP, and generated API reference behavior unchanged; this is a test-maintainability slice for the API table surface.

## Verification

- `rtk uv run pytest tests/test_catalog_api_selection.py tests/test_localization_api_selection.py tests/test_lsp_api_selection.py tests/test_pdx_api_selection.py tests/test_package_api_selection.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_catalog_api_selection.py tests/test_localization_api_selection.py tests/test_lsp_api_selection.py tests/test_pdx_api_selection.py tests/test_package_api_selection.py`
- `rtk bash scripts/flake.bash --all --paths tests/test_catalog_api_selection.py tests/test_localization_api_selection.py tests/test_lsp_api_selection.py tests/test_pdx_api_selection.py tests/test_package_api_selection.py`
