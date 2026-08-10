# PIHC3 Loading Screen Component Import

Date: 2026-06-14 12:54 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_loading_screen_components.py` to import compiled PIHC_dev loading-screen DDS assets.
- Added the project-local `loading_screen_component` family with a generic path-preserving copy slot.
- Regenerated 43 `src/modules/loading_screen_component` modules from `gfx/loadingscreens/*.dds`.
- Excluded `gfx/loadingscreens/*.dds` from the PIHC_dev copy overlay.
- Updated the loading-screen-component migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k loading_screen_component` failed on the missing `loading_screen_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_loading_screen_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k loading_screen_component` passed `2 passed, 84 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_loading_screen_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_loading_screen_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_loading_screen_components.py --clean` imported 43 modules.
- Debugged the first full build failure: using slot name `asset` caused DDS files to be loaded by the default PDX parser. Renaming the source slot to `assets` made the loader treat the files as static copy sources only.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 12,159 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 43 loading-screen-component modules, 43 loading-screen-component-owned copy artifacts, and 0 build errors.

## Notes

- The importer preserves compiled PIHC_dev DDS bytes exactly under their original game-relative paths.
- Broader `gfx/interface` DDS assets and `interface` GUI/GFX files remain copy-overlay owned or future asset-support work.
