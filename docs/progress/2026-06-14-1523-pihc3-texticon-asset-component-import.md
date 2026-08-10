# PIHC3 Texticon Asset Component Import

Date: 2026-06-14 15:23 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_texticon_asset_components.py` to import compiled PIHC_dev texticon GFX and DDS assets.
- Added the project-local `texticon_asset_component` family with a generic path-preserving copy slot.
- Regenerated 5 `src/modules/texticon_asset_component` modules from 50 `gfx/texticons/*.dds` files and 2 texticon-only GFX declaration files.
- Excluded reviewed texticon paths from the PIHC_dev copy overlay and excluded `gfx/texticons/.DS_Store` plus `gfx/texticons/script.py` as non-game support files.
- Updated the texticon-asset-component migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k texticon_asset_component` failed on the missing `texticon_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_texticon_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k texticon_asset_component` passed `2 passed, 106 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_texticon_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_texticon_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_texticon_asset_components.py --clean` imported 5 modules.
- Byte checks confirmed generated GFX/DDS outputs for `PIHC_texticons`, `PIHC_unit_categories`, `muffins`, `IB_civ_fac_20x20`, `unit_category_air_airship_icon_small`, and the unreferenced witchcraft texticon match the PIHC_dev source bytes exactly.
- Build ownership checks confirmed all 52 reviewed texticon paths are owned by `texticon_asset_component`, with 0 copy-root-owned texticon asset paths remaining.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 16,416 modules, 62 collections, 36,213 artifacts, 1,882 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer preserves compiled texticon DDS and GFX bytes exactly and does not regenerate assets from source images.
- `interface/PIHC_topbar.gfx`, `interface/PIHC_topbar_resources.gui`, `interface/topbar.gui`, and related topbar assets remain copy-overlay owned for a later UI/topbar slice.
- Full migration contracts were intentionally not run in this slice to reduce CPU load while other ParaDev workers are refactoring. Focused tests plus a full PIHC3 compile check covered the changed family.
