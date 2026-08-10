# Architecture API Selector Progress

Date: 2026-06-20 04:12 +0800

Linear: N/A

## Done

- Added `get_architecture_api_selection(symbol=..., index_name=..., key=...)` to `paradev.sdk.architecture` so the architecture API table supports full-table, row, and surface index projections through the shared API table selector.
- Regenerated `docs/user-manual/architecture-api-reference.md`; the architecture API table now lists 16 rows and includes the selector helper under the SDK surface.
- Added `tests/test_architecture_api_selection.py` for table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_architecture_api_selection.py` failed on missing `get_architecture_api_selection`.
- Green: `rtk uv run pytest -q tests/test_architecture_api_selection.py tests/test_api_table.py` passed with 165 tests.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/architecture.py tests/test_architecture_api_selection.py` returned OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/architecture.py tests/test_architecture_api_selection.py` reported both files unchanged.

## Risks Or Blockers

- Skipped the full suite to keep CPU available for concurrent PIHC2/PIHC3 migration work.
- Avoided dirty SDK facade, CLI facade, and broad manual files; this slice stays inside the architecture API-table module, generated architecture reference, focused tests, and this note.

## Next

- Continue closing clean selector gaps in LSP, project API, SDK facade, or HB modules after checking current dirty state.
