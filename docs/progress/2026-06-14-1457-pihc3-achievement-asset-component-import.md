# PIHC3 Achievement Asset Component Import

Date: 2026-06-14 14:57 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_achievement_asset_components.py` to import compiled PIHC_dev achievement icon assets.
- Added the project-local `achievement_asset_component` family with a generic path-preserving copy slot.
- Regenerated 49 `src/modules/achievement_asset_component` modules from 147 `gfx/achievements/*.dds` files.
- Excluded reviewed achievement icon paths from the PIHC_dev copy overlay.
- Updated the achievement-asset-component migration note, achievement migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k achievement_asset_component` failed on the missing `achievement_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_achievement_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k achievement_asset_component` passed `2 passed, 102 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_achievement_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_achievement_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_achievement_asset_components.py --clean` imported 49 modules.
- Byte checks confirmed generated normal, grey, and not-eligible `ACHIEVEMENT_PIHC_1CO_ALL_THE_FIRST_GAME` icons match the PIHC_dev source bytes exactly.
- Build ownership checks confirmed representative `gfx/achievements/` paths are owned by `achievement_asset_component`, with 0 copy-root-owned achievement asset paths remaining.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 16,402 modules, 62 collections, 36,215 artifacts, 1,882 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer preserves compiled achievement DDS bytes exactly and does not regenerate assets from source images.
- Full migration contracts were intentionally not run in this slice to reduce CPU load while other ParaDev workers are refactoring. Focused tests plus a full PIHC3 compile check covered the changed family.
