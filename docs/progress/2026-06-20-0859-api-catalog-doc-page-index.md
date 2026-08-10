# 2026-06-20 08:59 - API catalog doc page index

## Scope

- Added the rendered `Doc Page Index` section to the aggregate API catalog reference.
- Kept the existing `doc_page_index` table payload and selector behavior unchanged.
- Regenerated `docs/user-manual/api-catalog-reference.md` from the CLI generator.

## Verification

- Started with focused red checks requiring the missing rendered doc-page section:
  `rtk uv run pytest tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown`
- Re-ran the same focused checks after implementation and doc regeneration.
- Ran the heaven-style scan on the touched catalog module.
- Ran `rtk git diff --check`.

## Notes

- Full-suite tests were deferred for CPU hygiene during concurrent PIHC3 migration work. This slice changes only API catalog reference rendering, the generated aggregate manual, and focused reference tests.
