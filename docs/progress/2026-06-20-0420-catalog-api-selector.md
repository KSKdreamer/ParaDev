# Catalog API Selector Progress

Date: 2026-06-20 04:20 +0800

Linear: N/A

## Done

- Added `get_catalog_api_selection(symbol=..., index_name=..., key=...)` to the public `paradev.hb` catalog surface so the catalog API table supports full-table, row, and surface/feature index projections through the shared API table selector.
- Regenerated `docs/user-manual/catalog-api-reference.md`; the catalog API table now lists 32 rows and includes the selector helper under `api-table`.
- Added `tests/test_catalog_api_selection.py` for table, row, index, invalid-selector, detached-row, public facade export, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_catalog_api_selection.py` failed on missing `get_catalog_api_selection`.
- Green: `rtk uv run pytest -q tests/test_catalog_api_selection.py tests/test_api_table.py` passed with 165 tests.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/hb/__init__.py tests/test_catalog_api_selection.py` returned OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/hb/__init__.py tests/test_catalog_api_selection.py` reported both files unchanged.

## Risks Or Blockers

- Skipped the full suite to keep CPU available for concurrent PIHC2/PIHC3 migration work.
- Avoided dirty SDK facade, CLI facade, API catalog, and broad manual files; this slice stays inside the catalog API table module, generated catalog reference, focused tests, and this note.

## Next

- Continue closing clean selector gaps in LSP, SDK API, project API, or CLI after checking current dirty state.
