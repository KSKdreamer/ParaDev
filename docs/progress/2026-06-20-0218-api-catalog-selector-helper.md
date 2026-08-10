# API Catalog Selector Helper Progress

Date: 2026-06-20 02:18 +0800

Linear: none

## Done

- Added `selector_helper` to every aggregate API catalog source and row so shared selector paths are visible from the overall API table.
- Marked `api-catalog`, `frontend-api`, `sdk-cli-reference`, and `surface-contract-reference` with their shared selector helpers; rows without one use an empty string for stable JSON shape.
- Validated selector-helper metadata as a string during source indexing and as a callable helper during payload loading.
- Regenerated `docs/user-manual/api-catalog-reference.md` and updated `docs/architecture/interfaces.md` to describe the new selector-helper column.

## Verification

- Red run: API catalog CLI/architecture tests failed because `selector_helper` was missing from table and reference rows.
- Focused API catalog tests: `6 passed in 1.08s`.
- Affected module run: `tests/test_architecture.py tests/test_cli.py tests/test_api_table.py` passed with `375 passed in 15.61s`.
- Heaven-style scan passed for `src/paradev/surfaces/api_catalog.py`, `tests/test_architecture.py`, and `tests/test_cli.py`.
- `scripts/flake.bash --ci --paths ...` passed for the touched Python paths.

## Risks Or Blockers

- Full suite intentionally not run for this API-table-only slice to preserve CPU for parallel migration work.
- Unrelated dirty PIHC3, desktop, documentation, and skill changes remain untouched.

## Next

- Continue exposing table-level selector metadata consistently where REST, MCP, and CLI share the same lookup helper.
