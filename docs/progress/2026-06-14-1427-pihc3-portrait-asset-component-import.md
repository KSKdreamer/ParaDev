# PIHC3 Portrait Asset Component Import

Date: 2026-06-14 14:27 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_portrait_asset_components.py` to import compiled PIHC_dev portrait sprite/texture assets.
- Added the project-local `portrait_asset_component` family with a generic path-preserving copy slot.
- Regenerated 258 `src/modules/portrait_asset_component` modules from 254 `interface/portraits/*.gfx` files, 1,661 enumerated `gfx/leaders/*.dds` files, and two additional GFX-referenced department portrait DDS paths.
- Excluded reviewed portrait sprite/texture paths from the PIHC_dev copy overlay.
- Updated the portrait-asset-component migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k portrait_asset_component` failed on the missing `portrait_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_portrait_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k portrait_asset_component` passed `2 passed, 96 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_portrait_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_portrait_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_portrait_asset_components.py --clean` imported 258 modules.
- Byte checks confirmed generated `CHARACTER_ABYSSINIA_KING_MEOWMEOW`, `RANDOM_CHARACTER_pony_military`, and `leader_unknown` portrait assets match the PIHC_dev source bytes exactly.
- Build ownership checks confirmed representative `interface/portraits/`, `gfx/leaders/CHARACTER_*`, `gfx/leaders/RANDOM_CHARACTER_*`, fallback `gfx/leaders/leader_unknown.dds`, and GFX-referenced `CHARACTER_DEPARTMENT_C08_THEORY_ARMY.dds` paths are owned by `portrait_asset_component`.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 14,803 modules, 62 collections, 36,216 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer preserves compiled portrait GFX and DDS bytes exactly and does not regenerate assets from source portrait images or animation videos.
- Full migration contracts were intentionally not run in this slice to reduce CPU load while other ParaDev workers are refactoring. Focused tests plus a full PIHC3 compile check covered the changed family.
