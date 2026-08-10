# 2026-06-20 02:57 +0800 - API table selection helper

## Scope

- Added `api_table_selection(...)` to `paradev._api_table` as the shared selector path for API-table payloads.
- The helper returns a detached full table when no selector is passed, one detached row for `row_key_field`/`row_key`, or one copied index value list for `index_name`/`key`.
- Kept this slice inside the clean shared helper/test files so it does not mix with the parallel `module-batch-edit`, PIHC3, and desktop worktree changes.

## Verification

- Red check before implementation: `rtk uv run pytest -q tests/test_api_table.py::test_api_table_selection_returns_detached_full_table_without_selectors tests/test_api_table.py::test_api_table_selection_returns_row_or_index_projection tests/test_api_table.py::test_api_table_selection_rejects_ambiguous_or_incomplete_selectors` failed on missing `api_table_selection`.
- Green focused check: same three tests passed.
- Module check: `rtk uv run pytest -q tests/test_api_table.py` -> 161 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py` -> OK.
- Focused flake check: `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py tests/test_api_table.py` -> unchanged after formatter pass.
- Full suite skipped to preserve CPU while unrelated migration and API-table work is still active.

## Big picture

- Individual API surfaces can now expose `get_*_selection(...)` wrappers without repeating row-copy, index-copy, and selector-validation logic.
- This keeps the public API-table mental model consistent with the existing API catalog, surface contract, and frontend API selectors.
