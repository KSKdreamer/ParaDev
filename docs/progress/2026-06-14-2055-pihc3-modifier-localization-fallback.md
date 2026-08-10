# PIHC3 Modifier Localization Fallback

## Slice

Improved the native PIHC2 modifier import for GUI-visible data. The modifier importer now reads current local HOI4 localization before overlaying PIHC_dev localization, so vanilla static modifier records imported from PIHC_dev get real localized titles and `main.loc` rows instead of fallback ids.

## Changes

- Added a regression contract for `diff_easy_player` modifier localization.
- Added `HOI4_GAME_ROOT` and `--game-root` to `projects/PIHC3/scripts/migrate_pihc2_modifiers.py`.
- Loaded localization in this order:
  1. current local HOI4 install;
  2. compiled PIHC_dev mod.
- Kept BOP modifier localization owned by the native balance-of-power modules.
- Regenerated all 107 modifier modules.
- Updated modifier migration docs and shared legacy inventory notes.

## Evidence

- Before the importer change, `compiled_modifier_locs(..., modifier_id="diff_easy_player")` had no `l_english` rows.
- After the change:
  - 107 modifier modules are present;
  - 55 modifier modules have module-local `main.loc`;
  - `diff_easy_player` has current-game English and Simplified Chinese rows;
  - 33 BOP modifier modules still suppress duplicate `main.loc`;
  - 19 non-BOP modifier source keys still have no matching current-game or PIHC_dev display row.

## Verification

- Focused tests:
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "modifier_importer_extracts_individual_modifier_contract or modifier_family"`
  - `2 passed, 147 deselected`.
- Regeneration:
  - `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_modifiers.py --clean`
  - Imported 107 PIHC2 modifier modules.
- Style:
  - `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_modifiers.py tests/test_pihc3_migration_contracts.py`
  - `OK: 2 file(s) - no banned imports`.
  - `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_modifiers.py`
  - `1 file would be left unchanged`.
- Dry build:
  - `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-modifier-localization-dry-build.json`
  - Summary: 16,581 modules, 62 collections, 36,856 planned artifacts, 713 diagnostics, 0 errors, `blocked: false`.
  - Modifier ownership: 107 PDX artifacts, 485 localization artifacts, and 14 copied asset artifacts.
  - Active copy-root artifacts: 1,403, still limited to common terrain, gfx, history, and map-adjacent leftovers.

## Next

Continue improving GUI-visible data for the other named no-data families, especially equipment and remaining generic support modules, while leaving map-related copy-root leftovers for the later map migration slice.
