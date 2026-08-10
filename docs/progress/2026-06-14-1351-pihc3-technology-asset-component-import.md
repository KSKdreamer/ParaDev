# PIHC3 Technology Asset Component Import

Date: 2026-06-14 13:51 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_technology_asset_components.py` to import compiled PIHC_dev technology sprite/icon assets.
- Added the project-local `technology_asset_component` family with a generic path-preserving copy slot.
- Regenerated 305 `src/modules/technology_asset_component` modules from 300 `interface/technologies/*.gfx` files and 305 `gfx/interface/technologies/*.dds` files.
- Excluded those reviewed technology sprite/icon paths from the PIHC_dev copy overlay.
- Updated the technology-asset-component migration note, technology migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k technology_asset_component` failed on the missing `technology_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_technology_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k technology_asset_component` passed `2 passed, 90 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_technology_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_technology_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_technology_asset_components.py --clean` imported 305 modules.
- Byte checks confirmed generated `TECHNOLOGY_FIREARM_I`, `TECHNOLOGY_SUPPORT`, and `convoy` assets match the PIHC_dev source bytes exactly.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 12,939 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer groups `_small` and `_medium` DDS files with matching technology GFX keys while preserving original game-relative output paths.
- Full migration contracts were intentionally not run in this slice to reduce CPU load while other ParaDev workers are refactoring. Focused tests plus a full PIHC3 compile check covered the changed family.
- Root technology GUI fragments and generated asset-source reconstruction from `default.png` remain future work.
