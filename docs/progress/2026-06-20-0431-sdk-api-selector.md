# SDK API Selector Progress

Date: 2026-06-20 04:31 +0800

Linear: N/A

## Done

- Added `get_sdk_api_selection(symbol=..., index_name=..., key=...)` to `paradev.sdk.api` so the public SDK facade table supports full-table, row, and module/feature/kind index projections through the shared API table selector.
- Added `tests/test_sdk_api_selection.py` for table, row, index, invalid-selector, and detached-row behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_sdk_api_selection.py` failed on missing `get_sdk_api_selection`.
- Green: `rtk uv run pytest -q tests/test_sdk_api_selection.py tests/test_api_table.py` passed with 163 tests.

## Risks Or Blockers

- Skipped generated `docs/user-manual/sdk-api-reference.md` parity and top-level `paradev.sdk` facade export in this slice because those files already have unrelated `module-batch-edit` changes from another active worker.
- Skipped the full suite to keep CPU available for concurrent PIHC2/PIHC3 migration work.
- Avoided dirty CLI surface, generated SDK/project/CLI references, and broad architecture tests.

## Next

- After the `module-batch-edit` slice lands or clears, expose `get_sdk_api_selection` through `paradev.sdk`, regenerate the SDK API reference, and keep the selector helper listed in the SDK facade table.
