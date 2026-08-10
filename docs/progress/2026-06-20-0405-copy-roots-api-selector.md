# Copy Roots API Selector Progress

Date: 2026-06-20 04:05 +0800

Linear: N/A

## Done

- Added `get_copy_roots_api_selection(symbol=..., index_name=..., key=...)` to `paradev.sdk.copy_roots` so the copy-roots API table supports full-table, row, and module/feature/kind index projections through the shared API table selector.
- Regenerated `docs/user-manual/copy-roots-api-reference.md`; the copy-roots API table now lists 12 rows and includes the selector helper under `copy-roots-api`.
- Added `tests/test_copy_roots_api_selection.py` for table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_copy_roots_api_selection.py` failed on missing `get_copy_roots_api_selection`.
- Green: `rtk uv run pytest -q tests/test_api_table.py tests/test_copy_roots_api_selection.py` passed with 165 tests.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/copy_roots.py tests/test_copy_roots_api_selection.py` returned OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/copy_roots.py tests/test_copy_roots_api_selection.py` reported both files unchanged.

## Risks Or Blockers

- Skipped the full suite to keep CPU available for concurrent PIHC2/PIHC3 migration work.
- Avoided dirty facade and CLI files; this slice stays inside the copy-roots API-table module, generated reference, focused tests, and this note.

## Next

- Continue closing remaining API-table selector gaps in clean modules before touching dirty SDK, CLI, HB, or migration-owned files.
