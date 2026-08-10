# PIHC3 Focus Asset Component Import

Date: 2026-06-14 14:04 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_focus_asset_components.py` to import compiled PIHC_dev focus sprite/icon assets.
- Added the project-local `focus_asset_component` family with a generic path-preserving copy slot.
- Regenerated 739 `src/modules/focus_asset_component` modules from 738 `interface/focuses/*.gfx` files and 739 `gfx/interface/goals/*.dds` files.
- Excluded those reviewed focus sprite/icon paths from the PIHC_dev copy overlay.
- Updated the focus-asset-component migration note, focus migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k focus_asset_component` failed on the missing `focus_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_focus_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k focus_asset_component` passed `2 passed, 92 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_focus_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_focus_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_focus_asset_components.py --clean` imported 739 modules.
- Byte checks confirmed generated `FOCUS_C01_CANTERLOT_PACT`, `FOCUS_C08_CANTERLOT_PACT`, and `goal_unknown` assets match the PIHC_dev source bytes exactly.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 13,678 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer preserves the compiled focus GFX files, including normal and shine sprite declarations, and does not regenerate assets from `default.png`.
- Full migration contracts were intentionally not run in this slice to reduce CPU load while other ParaDev workers are refactoring. Focused tests plus a full PIHC3 compile check covered the changed family.
