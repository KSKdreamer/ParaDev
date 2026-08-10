# PIHC3 Difficulty Setting Localization

## Slice

Improved the native difficulty-setting import so GUI-visible PIHC custom strong-AI toggles carry their real display rows instead of fallback ids.

## Changes

- Added a generic `loc` slot to the `difficulty_setting` family in `projects/PIHC3/paradev.yaml`.
- Added `HOI4_GAME_ROOT` and `--game-root` to `projects/PIHC3/scripts/migrate_pihc2_difficulty_settings.py`.
- Loaded localization in this order:
  1. current local HOI4 install;
  2. compiled PIHC_dev mod.
- Kept ownership limited to the `custom_diff_strong_*` setting keys, avoiding duplicate shared `diff_strong_ai_generic` rows.
- Regenerated all 9 difficulty-setting modules.
- Updated difficulty-setting, copy-overlay, architecture, and legacy inventory docs.

## Evidence

- Before the change, `difficulty_setting` had only a PDX source slot and all 9 modules lacked `main.loc`.
- After the change:
  - 9 difficulty-setting modules are present;
  - all 9 have `main.loc`;
  - generated localization contains 18 rows;
  - `custom_diff_strong_C01` now has English `Strengthen §YEquestria Empire§!` and Simplified Chinese `加强 §Y小马利亚帝国§!`.

## Verification

- Red test:
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "difficulty_setting_family or difficulty_setting_importer"`
  - Failed with missing `difficulty_setting` loc slot and missing `compiled_difficulty_setting_locs`.
- Focused tests after implementation:
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "difficulty_setting_family or difficulty_setting_importer"`
  - `2 passed, 147 deselected`.
- Regeneration:
  - `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_difficulty_settings.py --clean`
  - Imported 9 PIHC2 difficulty setting modules.
- Dry build:
  - `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-difficulty-setting-localization-dry-build.json`
  - Summary: 16,581 modules, 62 collections, 37,100 planned artifacts, 713 diagnostics, 0 errors, `blocked: false`.
  - Difficulty-setting ownership: 9 PDX artifacts and 18 localization artifacts.
  - Active copy-root artifacts: 1,403, with 0 copy-root artifacts under `common/difficulty_settings/`.

## Next

Continue closing GUI-visible data gaps in small non-map families while preserving shared generic slots over family-specific code.
