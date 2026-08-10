# PIHC3 Intelligence Agency Asset Component Import

Date: 2026-06-14 15:11 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_intelligence_agency_asset_components.py` to import compiled PIHC_dev intelligence agency sprite and logo assets.
- Added the project-local `intelligence_agency_asset_component` family with a generic path-preserving copy slot.
- Regenerated 9 `src/modules/intelligence_agency_asset_component` modules from 9 `interface/intelligence_agencies/*.gfx` files and 9 `gfx/interface/intelligence_agencies/*.dds` files.
- Excluded reviewed compiled intelligence agency GFX/DDS paths from the PIHC_dev copy overlay.
- Updated the intelligence-agency migration note, new intelligence-agency-asset-component note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k intelligence_agency_asset_component` failed on the missing `intelligence_agency_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_intelligence_agency_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k intelligence_agency_asset_component` passed `2 passed, 104 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_intelligence_agency_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_intelligence_agency_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_intelligence_agency_asset_components.py --clean` imported 9 modules.
- Byte checks confirmed generated GFX/DDS pairs for `INTEL_AGENCY_BOC`, `INTEL_AGENCY_DEFAULT`, and `INTEL_AGENCY_SEPAL` match the PIHC_dev source bytes exactly.
- Build ownership checks confirmed all 18 compiled intelligence agency GFX/DDS paths are owned by `intelligence_agency_asset_component`, with 0 copy-root-owned compiled intelligence agency asset paths remaining.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 16,411 modules, 62 collections, 36,215 artifacts, 1,882 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer preserves compiled intelligence agency DDS and GFX bytes exactly and does not regenerate assets from source images.
- Full migration contracts were intentionally not run in this slice to reduce CPU load while other ParaDev workers are refactoring. Focused tests plus a full PIHC3 compile check covered the changed family.
