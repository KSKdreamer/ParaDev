# PIHC3 Difficulty Setting Import Progress

Date: 2026-06-14 06:38 CST

Linear: N/A

## Done

- Added `projects/PIHC3/scripts/migrate_pihc2_difficulty_settings.py` to split compiled PIHC_dev difficulty settings by each `difficulty_setting` record's `key`.
- Replaced the previous one file-level `00_difficulty` module with 9 setting-level modules under `projects/PIHC3/src/modules/difficulty_setting`.
- Preserved the required `difficulty_settings = { ... }` wrapper in each module's `def.txt` so each module remains a valid standalone HOI4 difficulty-setting file.
- Removed `difficulty_setting` from the generic common-source importer so future generic imports do not overwrite the split modules.
- Updated migration docs for the dedicated difficulty-setting importer and current PIHC3 build counts.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k difficulty_setting` -> 3 passed.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` -> 46 passed.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_difficulty_settings.py --clean` -> imported 9 difficulty setting modules.
- PIHC3 emitting build -> 3,340 modules, 62 collections, 27,704 artifacts, 0 errors, `blocked: false`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_difficulty_settings.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk bash scripts/flake.bash --ci` -> passed.

## Risks Or Blockers

- This slice preserves compiled difficulty settings only. Modifier definition balancing and UI/localization review remain separate work.
- The copy overlay already excludes difficulty-setting `.txt` files, so native files own this output domain.

## Next

- Continue splitting remaining non-map generic common families. Scripted effects/triggers likely need shared macro handling before they move from file-level to record-level modules.
