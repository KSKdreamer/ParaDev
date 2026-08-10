# LSP API Selector Progress

Date: 2026-06-20 04:25 +0800

Linear: N/A

## Done

- Added `get_lsp_api_selection(symbol=..., index_name=..., key=...)` to the `paradev.sdk.lsp` API table surface so LSP editor APIs support full-table, row, and surface/feature index projections through the shared API table selector.
- Regenerated `docs/user-manual/lsp-api-reference.md`; the LSP API table now lists 40 rows and includes the selector helper under `api-table`.
- Added `tests/test_lsp_api_selection.py` for row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_lsp_api_selection.py` failed on missing `get_lsp_api_selection`.
- Green: `rtk uv run pytest -q tests/test_lsp_api_selection.py tests/test_api_table.py` passed with 165 tests.

## Risks Or Blockers

- Skipped the full suite to keep CPU available for concurrent PIHC2/PIHC3 migration work.
- Avoided dirty `src/paradev/sdk/__init__.py`, `src/paradev/surfaces/cli.py`, broad architecture tests, SDK/project API docs, and PIHC3 migration files.

## Next

- Continue with clean selector gaps in SDK API or project API after checking the dirty set again.
