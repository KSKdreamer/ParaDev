# 2026-06-20 08:47 - API catalog reference group helper

## Scope

- Added `get_api_catalog_reference_group(group)` as a public `paradev.surfaces` SDK helper.
- Kept the returned reference group row detached so callers can mutate it without changing future catalog reads.
- Regenerated the surfaces and aggregate API catalog manuals so the documented API counts match the exported facade.

## Verification

- Started with the focused red check for the new helper contract:
  `rtk uv run pytest tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown`
- Re-ran the same focused checks after implementation and doc regeneration.
- Ran the heaven-style scan on the touched surface modules.
- Ran `rtk git diff --check`.

## Notes

- Full-suite tests were deferred to avoid competing with concurrent PIHC3 migration work. This slice only touches the aggregate API catalog helper, public surface export registration, generated API manuals, and focused tests.
