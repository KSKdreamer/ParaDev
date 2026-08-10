# PIHC3 Special Project Asset Component Import

Date: 2026-06-14 15:33 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_special_project_asset_components.py` to import compiled PIHC_dev special-project sprite and shared UI assets.
- Added the project-local `special_project_asset_component` family with a generic path-preserving copy slot.
- Regenerated 26 `src/modules/special_project_asset_component` modules from 25 `interface/special_projects/SP_*.gfx` files, one shared `interface/PIHC_special_projects.gfx` file, and 17 shared root-level `gfx/interface/special_project/*.dds` files.
- Excluded reviewed special-project asset paths from the PIHC_dev copy overlay, while leaving project icon DDS files with native `special_project` modules and GUI/PDX support files for later slices.
- Updated the special-project migration note, new special-project-asset-component note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k special_project_asset_component` failed on the missing `special_project_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_special_project_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k special_project_asset_component` passed `2 passed, 108 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_special_project_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_special_project_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_special_project_asset_components.py --clean` imported 26 modules.
- Byte checks confirmed generated GFX/DDS outputs for `PIHC_special_projects`, `specialization_magic`, `mapicon_facility_specialization_nuclear`, `sp_top_bg`, `SP_ELEC_ARC`, and `SP_WITCHCRAFT_ROCKET` match the PIHC_dev source bytes exactly.
- Build ownership checks confirmed all 43 reviewed special-project asset paths are owned by `special_project_asset_component`, with 0 copy-root-owned reviewed special-project asset paths remaining.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 16,442 modules, 62 collections, 36,212 artifacts, 1,857 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer preserves compiled special-project DDS and GFX bytes exactly and does not regenerate assets from source images.
- Special-project GUI files, project-tag PDX, and specialization PDX remain copy-overlay owned or future structured slices.
- Full migration contracts were intentionally not run in this slice to reduce CPU load while other ParaDev workers are refactoring. Focused tests plus a full PIHC3 compile check covered the changed family.
