# 2026-06-20 03:02 +0800 - REST API selector helper

## Slice

- Added `get_rest_api_selection(symbol=..., index_name=..., key=...)` to the REST surface so callers can read the full REST route table, one route row, or one method/feature/frontend-operation index projection through the shared API table selector.
- Regenerated `docs/user-manual/rest-api-reference.md` so the REST API reference advertises the selector helper alongside the route table counts.
- Added `tests/test_rest_api_selection.py` to cover table, row, index, invalid-selector, detached-list, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_rest_api_selection.py` failed on missing `get_rest_api_selection`.
- Green: `rtk uv run pytest -q tests/test_rest_api_selection.py tests/test_api_table.py` -> 164 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py tests/test_rest_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/rest.py tests/test_rest_api_selection.py` -> clean after formatting.

## Notes

- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the REST surface, its generated reference, the new focused test, and this note.
