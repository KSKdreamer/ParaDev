# API Catalog Selector Index Progress

Date: 2026-06-20 02:27 +0800

Linear: none

## Done

- Added `selector_helper_index` to the aggregate API catalog table so shared selector helpers are queryable through the same indexed-table path as layer, feature, owner, surface, CLI command, and manual page lookups.
- Documented the new `selector_helper` index in `API_CATALOG_INDEX_CATALOG` and exposed it through `get_api_catalog_selection(index_name="selector_helper", key=...)` / `get_api_catalog_reference_ids("selector_helper", ...)`.
- Skipped empty selector-helper values while preserving the `selector_helper` row field for references that do not have a shared selector helper.
- Regenerated `docs/user-manual/api-catalog-reference.md` and `docs/user-manual/surfaces-api-reference.md`; updated `docs/architecture/interfaces.md` to name the selector-helper grouping as part of the aggregate catalog contract.

## Verification

- Red run: narrow API catalog CLI/architecture tests failed before implementation because `selector_helper_index` was absent from the table, rows, and rendered reference.
- Focused selector checks passed: `5 passed in 1.27s`.
- Affected module run passed after generated-doc refresh: `tests/test_architecture.py tests/test_cli.py tests/test_api_table.py` with `375 passed in 15.83s`.
- Heaven-style scan passed for `src/paradev/surfaces/api_catalog.py`, `tests/test_architecture.py`, and `tests/test_cli.py`.
- `scripts/flake.bash --ci --paths ...` passed for the touched Python paths after Black reformatted one test assertion.

## Risks Or Blockers

- Full suite intentionally not run for this API-catalog-only slice to preserve CPU for parallel PIHC3 migration work.
- Unrelated dirty PIHC3, desktop, documentation, and skill changes remain untouched.

## Next

- Step back to review whether any remaining selector-bearing generated references lack table-level grouped indexes before extending this pattern further.
