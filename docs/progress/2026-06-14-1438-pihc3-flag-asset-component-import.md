# PIHC3 Flag Asset Component Import

Date: 2026-06-14 14:38 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_flag_asset_components.py` to import compiled PIHC_dev flag TGA assets not already emitted by country modules.
- Added the project-local `flag_asset_component` family with a generic path-preserving copy slot.
- Regenerated 1,110 `src/modules/flag_asset_component` modules from 1,370 compiled flag TGA files.
- Excluded reviewed flag paths and the compiled `.DS_Store` file from the PIHC_dev copy overlay.
- Updated the flag-asset-component migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k flag_asset_component` failed on the missing `flag_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_flag_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k flag_asset_component` passed `2 passed, 98 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_flag_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_flag_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_flag_asset_components.py --clean` imported 1,110 modules.
- Byte checks confirmed generated `30C`, `C01`, and `Z35_transcendence` flag assets match the PIHC_dev source bytes exactly.
- Build ownership checks confirmed top-level `gfx/flags/C01.tga`, unowned `30C` variants, and `gfx/flags/small/Z35_transcendence.tga` are owned by `flag_asset_component`; nested `C01` medium/small flags remain owned by `country`; `.DS_Store` is absent.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 15,913 modules, 62 collections, 36,215 artifacts, 1,882 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer preserves compiled flag TGA bytes exactly and does not regenerate assets from source flag images.
- Full migration contracts were intentionally not run in this slice to reduce CPU load while other ParaDev workers are refactoring. Focused tests plus a full PIHC3 compile check covered the changed family.
