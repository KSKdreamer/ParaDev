# PIHC3 Event Asset Component Import

Date: 2026-06-14 14:15 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_event_asset_components.py` to import compiled PIHC_dev event sprite/picture assets.
- Added the project-local `event_asset_component` family with a generic path-preserving copy slot.
- Regenerated 867 `src/modules/event_asset_component` modules from 866 non-superevent `interface/events/*.gfx` files and 867 non-superevent `gfx/event_pictures/*.dds` files.
- Excluded reviewed event sprite/picture paths from the PIHC_dev copy overlay while leaving superevent DDS ownership with the existing `superevent` family.
- Updated the event-asset-component migration note, event migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k event_asset_component` failed on the missing `event_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_event_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k event_asset_component` passed `2 passed, 94 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_event_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_event_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_event_asset_components.py --clean` imported 867 modules.
- Byte checks confirmed generated `EVENT_C33_MAIN_1`, `EVENT_ARTIFACTS_1`, and `border_war` assets match the PIHC_dev source bytes exactly.
- Build ownership checks confirmed `interface/events/EVENT_C33_MAIN_1.gfx`, `gfx/event_pictures/EVENT_C33_MAIN_1.dds`, and `gfx/event_pictures/border_war.dds` are owned by `event_asset_component`, while `gfx/event_pictures/EVENT_SUPER_1.dds` remains owned by `superevent`.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 14,545 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer preserves compiled event GFX and DDS bytes exactly and does not regenerate assets from higher-level event source images.
- Full migration contracts were intentionally not run in this slice to reduce CPU load while other ParaDev workers are refactoring. Focused tests plus a full PIHC3 compile check covered the changed family.
