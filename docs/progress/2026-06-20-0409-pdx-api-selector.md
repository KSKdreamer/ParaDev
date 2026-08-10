# PDX API Selector Progress

Date: 2026-06-20 04:09 +0800

Linear: N/A

## Done

- Added `get_pdx_api_selection(symbol=..., index_name=..., key=...)` to `paradev.sdk.pdx` so the PDX API table supports full-table, row, and surface/feature index projections through the shared API table selector.
- Regenerated `docs/user-manual/pdx-api-reference.md`; the PDX API table now lists 20 rows and includes the selector helper under `api-table`.
- Added `tests/test_pdx_api_selection.py` for table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_pdx_api_selection.py` failed on missing `get_pdx_api_selection`.
- Green: `rtk uv run pytest -q tests/test_pdx_api_selection.py tests/test_api_table.py` passed with 165 tests.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/pdx.py tests/test_pdx_api_selection.py` returned OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/pdx.py tests/test_pdx_api_selection.py` reported both files unchanged.

## Risks Or Blockers

- Skipped the full suite to keep CPU available for concurrent PIHC2/PIHC3 migration work.
- Avoided dirty SDK facade, CLI facade, and broad manual files; this slice stays inside the PDX API-table module, generated PDX reference, focused tests, and this note.

## Next

- Continue closing clean selector gaps in SDK/HB table modules before touching dirty CLI or facade files.
