# PIHC3 Building Localization Fallback

## Slice

Improved the building migration for GUI-visible data. The building importer now reads current local HOI4 localization before overlaying PIHC_dev localization, so vanilla building records imported from PIHC_dev get real localized titles and `main.loc` rows instead of fallback ids.

## Changes

- Added a red contract for `infrastructure` building localization.
- Added `HOI4_GAME_ROOT` and `--game-root` to `projects/PIHC3/scripts/migrate_pihc2_buildings.py`.
- Loaded localization in this order:
  1. current local HOI4 install;
  2. compiled PIHC_dev mod.
- Regenerated all 38 building modules.
- Updated building migration docs and shared legacy inventory notes.

## Evidence

- Before the importer change, `compiled_building_locs(..., building_id="infrastructure")` had no `l_english` rows.
- After the change:
  - 38 building modules are present;
  - 37 building modules have `main.loc`;
  - `infrastructure`, `arms_factory`, and `air_base` now have localized titles;
  - `pihc_bgfx_fog` remains the only unlocalized technical record.

## Verification

- Focused test:
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k building_importer_extracts_individual_building_contract`
  - `1 passed, 148 deselected`.
- Regeneration:
  - `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_buildings.py --clean`
  - Imported 38 PIHC2 building modules.
- Dry build:
  - `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-building-localization-dry-build.json`
  - Summary: 16,581 modules, 62 collections, 36,385 planned artifacts, 713 diagnostics, 0 errors, `blocked: false`.
  - Building ownership: 38 building PDX artifacts and 242 building localization artifacts.
  - Active copy-root artifacts: 1,403, all remaining common/gfx/history/map leftovers are map-adjacent.

## Next

Continue improving GUI-visible data for the other named no-data families, especially modifiers and equipment, while leaving map-related copy-root leftovers for the later map migration slice.
