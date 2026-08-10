# API Catalog Reference Groups Progress

Date: 2026-06-20 08:06

Linear: not updated

## Done

- Added `ApiCatalogReferenceGroupRow` and `get_api_catalog_reference_groups()` so SDK callers can read API catalog group titles, kinds, counts, ordered reference ids, and usage text without parsing Markdown.
- Reused the existing private group specs as the single source of truth for both the public helper and the generated Markdown section.
- Regenerated `docs/user-manual/surfaces-api-reference.md` and prepared a clean generated blob for `docs/user-manual/api-catalog-reference.md`.

## Verification

- Red: `rtk uv run --extra dev --extra rest pytest -q tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references` failed on the missing group row/helper and stale 51-row surface table.
- Green: `rtk uv run --extra dev --extra rest pytest -q tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_outputs_table_json tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown` passed in `/tmp/paradev-api-catalog-reference-groups`.
- `rtk git diff --check` passed in `/tmp/paradev-api-catalog-reference-groups-verify`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/__init__.py src/paradev/surfaces/api.py` passed.
- The same focused pytest command passed in `/tmp/paradev-api-catalog-reference-groups-verify`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_architecture.py tests/test_cli.py` still reports the pre-existing top-level `json` and `pathlib` imports in those broad test files.

## Risks Or Blockers

- Full suite intentionally not run to avoid CPU churn while parallel PIHC3 migration work is active.
- Main `docs/user-manual/api-catalog-reference.md` has unrelated dirty row-count drift from current SDK/project/CLI work; this slice stages a clean generated blob from the detached checkout to avoid absorbing that drift.

## Next

- Continue making generated grouping data discoverable through narrow helpers only where it helps SDK, REST, MCP, or GUI consumers avoid hand-filtering rows.
