# 2026-06-20 08:53 - API catalog reference group index row

## Scope

- Added the `reference_group` row to `API_CATALOG_INDEX_CATALOG`.
- Documented `get_api_catalog_reference_group(group)` as the lookup helper for full reader-oriented reference group rows.
- Regenerated the aggregate API catalog and surfaces API manuals so the tuple count and index catalog table match the SDK surface.

## Verification

- Started with the focused red check for the missing index row:
  `rtk uv run pytest tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown`
- Re-ran the same focused checks after implementation and doc regeneration.
- Ran the heaven-style scan on the touched catalog module.
- Ran `rtk git diff --check`.

## Notes

- Full-suite tests were deferred for CPU hygiene during concurrent PIHC3 migration work. This slice changes only the aggregate API catalog metadata, generated manuals, and focused API catalog tests.
