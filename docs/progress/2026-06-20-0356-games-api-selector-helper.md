# 2026-06-20 03:56 +0800 - Games API selector helper

## Slice
- Added `get_games_api_selection(symbol=..., index_name=..., key=...)` so the `paradev.games` facade API table supports full-table, row, and module/feature/kind index projection lookups through the shared API table selector.
- Exported the helper from `paradev.games` and regenerated `docs/user-manual/games-api-reference.md`, increasing the games API row count to 8.
- Added `tests/test_games_api_selection.py` to cover table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification
- Red: `rtk uv run pytest -q tests/test_games_api_selection.py` failed on missing `get_games_api_selection`.
- Green: `rtk uv run pytest -q tests/test_games_api_selection.py tests/test_api_table.py` -> 165 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/games/api.py src/paradev/games/__init__.py tests/test_games_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/games/api.py src/paradev/games/__init__.py tests/test_games_api_selection.py` -> clean.

## Notes
- Regenerated the games reference from `render_games_api_reference_markdown()` directly to avoid relying on dirty CLI/API catalog files.
- Avoided `src/paradev/games/hoi4/__init__.py`, which is already dirty from concurrent PIHC3 migration work.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the games API table module, games facade export, generated games reference, the focused test, and this note.
