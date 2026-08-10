# HB API Selector Progress

Date: 2026-06-20 04:17 +0800

Linear: N/A

## Done

- Added `get_hb_api_selection(symbol=..., index_name=..., key=...)` to the public `paradev.hb` facade so the HB facade API table supports full-table, row, and module/feature/kind index projections through the shared API table selector.
- Regenerated `docs/user-manual/hb-api-reference.md`; the HB facade API table now lists 24 rows and includes the selector helper under `hb-api`.
- Added `tests/test_hb_api_selection.py` for table, row, index, invalid-selector, detached-row, public facade export, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_hb_api_selection.py` failed on missing `get_hb_api_selection`.
- Green: `rtk uv run pytest -q tests/test_hb_api_selection.py tests/test_api_table.py` passed with 165 tests.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/hb/api.py src/paradev/hb/__init__.py tests/test_hb_api_selection.py` returned OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/hb/api.py src/paradev/hb/__init__.py tests/test_hb_api_selection.py` reported all three files unchanged.

## Risks Or Blockers

- Skipped the full suite to keep CPU available for concurrent PIHC2/PIHC3 migration work.
- Avoided dirty API catalog, SDK facade, CLI facade, and broad manual files; this slice stays inside the HB facade API module, public HB export list, generated HB reference, focused tests, and this note.

## Next

- Continue closing clean selector gaps in catalog, LSP, SDK API, project API, or CLI after checking current dirty state.
