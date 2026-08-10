# 2026-06-20 03:52 +0800 - Build API selector helper

## Slice
- Added `get_build_api_selection(symbol=..., index_name=..., key=...)` so the `paradev.build` facade API table supports full-table, row, and module/feature/kind index projection lookups through the shared API table selector.
- Exported the helper from `paradev.build` and regenerated `docs/user-manual/build-api-reference.md`, increasing the build API row count to 103.
- Added `tests/test_build_api_selection.py` to cover table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification
- Red: `rtk uv run pytest -q tests/test_build_api_selection.py` failed on missing `get_build_api_selection`.
- Green: `rtk uv run pytest -q tests/test_build_api_selection.py tests/test_api_table.py` -> 165 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/api.py src/paradev/build/__init__.py tests/test_build_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/build/api.py src/paradev/build/__init__.py tests/test_build_api_selection.py` -> clean.

## Notes
- Regenerated the build reference from `render_build_api_reference_markdown()` directly to avoid relying on dirty CLI/API catalog files.
- Preserved the existing `none` registry seam classification for build API-table rows; this slice only adds selection behavior.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the build API table module, build facade export, generated build reference, the focused test, and this note.
