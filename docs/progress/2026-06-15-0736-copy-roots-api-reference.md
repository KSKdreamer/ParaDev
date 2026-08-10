# Copy Roots API Reference

Time: 2026-06-15 07:36 CST

## Scope

- Added the SDK copy-root API table in `paradev.sdk.copy_roots`, covering target roots, validation, `CopyRootSpec`, manifest parsing, copied artifact production, merge/shadow diagnostics, and the table renderer.
- Exposed the table through `paradev copy-roots-api` / `paradev copy-roots-api --markdown`.
- Registered the table in the API catalog and CLI API reference, then regenerated the affected manual pages.
- Updated the handwritten interface, SDK, developer, and manual index docs so copy-root audits use the fixed table helper.

## Checks

- `rtk uv run pytest tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_copy_roots_api_cli_outputs_table_json tests/test_cli.py::test_copy_roots_api_cli_outputs_reference_markdown tests/test_cli.py::test_copy_roots_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown`
- `rtk uv run python -m py_compile src/paradev/sdk/copy_roots.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/copy_roots.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/copy_roots.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- ...`

## Notes

- Behavior is unchanged; this is a documentation/API-table surface for the existing copy-root pipeline.
- Did not touch PIHC3 migration files, desktop work, logo assets, or `node_modules/`.
