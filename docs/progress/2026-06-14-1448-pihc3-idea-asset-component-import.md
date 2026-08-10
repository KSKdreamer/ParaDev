# PIHC3 Idea Asset Component Import

Date: 2026-06-14 14:48 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_idea_asset_components.py` to import compiled PIHC_dev idea sprite/icon assets.
- Added the project-local `idea_asset_component` family with a generic path-preserving copy slot.
- Regenerated 440 `src/modules/idea_asset_component` modules from 423 `interface/ideas/*.gfx` files and 440 `gfx/interface/ideas/*.dds` files.
- Excluded reviewed idea sprite/icon paths from the PIHC_dev copy overlay.
- Updated the idea-asset-component migration note, idea migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k idea_asset_component` failed on the missing `idea_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_idea_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k idea_asset_component` passed `2 passed, 100 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_idea_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_idea_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_idea_asset_components.py --clean` imported 440 modules.
- Byte checks confirmed generated `IDEA_C01_ANGRY_BEST_PONY`, `IDEA_ALL_ARTIFACT_ALICORN_AMULET`, and `idea_war_economy` assets match the PIHC_dev source bytes exactly.
- Build ownership checks confirmed representative `interface/ideas/` and `gfx/interface/ideas/` paths are owned by `idea_asset_component`, with 0 copy-root-owned idea asset paths remaining.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 16,353 modules, 62 collections, 36,215 artifacts, 1,882 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer preserves compiled idea GFX and DDS bytes exactly and does not regenerate assets from source `default.png` images.
- Full migration contracts were intentionally not run in this slice to reduce CPU load while other ParaDev workers are refactoring. Focused tests plus a full PIHC3 compile check covered the changed family.
