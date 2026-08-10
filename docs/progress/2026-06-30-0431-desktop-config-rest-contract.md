# 2026-06-30 04:31 - Desktop config REST contract

## Summary

- Added the live desktop Config-page routes to the REST/OpenAPI seed: app config read/write, CM-backed config value read/write, and LLM route testing.
- Extended REST API table and CLI assertions so generated route inventories include the GUI-facing config routes.
- Regenerated the REST API reference and aggregate API catalog reference.
- Recorded the config-page audit result for the next slice: stop persisting CM-backed Config-page values in the desktop-only GUI settings blob.

## Verification

```bash
rtk bash scripts/test.bash --serial tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_rest_api_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli_api_rest_mcp_selectors.py::test_cli_api_openapi_and_rest_api_row_advertise_selector tests/test_rest_mcp_api_self_selectors.py::test_generated_references_document_rest_and_mcp_self_selectors -q
rtk bash scripts/test.bash --serial tests/test_rest_api_selection.py tests/test_catalog_api_surface_selectors.py tests/test_pdx_api_surface_selectors.py tests/test_lsp_api_surface_selectors.py tests/test_cli_api_rest_mcp_selectors.py tests/test_rest_mcp_api_self_selectors.py -q
rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py tests/test_architecture.py tests/test_cli.py tests/test_cli_api_rest_mcp_selectors.py tests/test_rest_mcp_api_self_selectors.py
rtk git diff --check
rtk bash scripts/flake.bash --ci
rtk bash scripts/test.bash
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

Notes:

- The new route contract tests failed before implementation because `/desktop/app-config`, `/desktop/config-value`, and `/desktop/llm/test` were runtime routes but absent from `get_openapi_seed()`.
- The standard fast gate passed with `1218 passed, 2 warnings`.
- The Tauri PIHC3 smoke launched `target/debug/paradev-desktop` successfully.
