# PIHC3 UI Asset Component Import

Date: 2026-06-14 13:12 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_ui_asset_components.py` to import compiled PIHC_dev compact UI assets.
- Added the project-local `ui_asset_component` family with a generic path-preserving copy slot.
- Regenerated 11 `src/modules/ui_asset_component` modules from `gfx/interface/alerts/*.dds`, `gfx/interface/autonomy/*.dds`, and `interface/alerts.gui`.
- Excluded those reviewed compact UI paths from the PIHC_dev copy overlay.
- Updated the UI-asset-component migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k ui_asset_component` failed on the missing `ui_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_ui_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k ui_asset_component` passed `2 passed, 86 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_ui_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_ui_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_ui_asset_components.py --clean` imported 11 modules.
- Byte checks confirmed generated `global_alert_icons.dds`, `autonomy_pihc_dominion_icon.dds`, and `interface/alerts.gui` match the PIHC_dev source bytes exactly.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 12,170 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer uses the source slot name `assets`; `asset` is reserved by the default PDX source slot behavior and would parse DDS files incorrectly.
- Broader `gfx/interface` assets and unrelated `interface` GUI/GFX files remain copy-overlay owned or future asset-support work.
