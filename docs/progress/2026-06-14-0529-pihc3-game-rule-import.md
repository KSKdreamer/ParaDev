# PIHC3 Game Rule Import Progress

Date: 2026-06-14 05:29 CST

Linear: N/A

## Done

- Added `projects/PIHC3/scripts/migrate_pihc2_game_rules.py` to split compiled PIHC_dev game rules into one PIHC3 module per top-level rule.
- Replaced the previous 3 file-level game-rule modules with 27 rule-level modules under `projects/PIHC3/src/modules/game_rule`.
- Restored rule-owned localization for titles and unique option text/description rows while leaving shared group and option labels to the copied localization overlay.
- Removed `game_rule` from the generic common-source importer so future generic imports do not overwrite the split modules.
- Updated migration docs for the game-rule importer and current PIHC3 build counts.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` -> 33 passed.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_game_rules.py --clean` -> imported 27 game rule modules.
- PIHC3 emitting build -> 3,325 modules, 62 collections, 27,619 artifacts, 0 errors, `blocked: false`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_game_rules.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk bash scripts/flake.bash --ci` -> passed.

## Risks Or Blockers

- The build still reports broader copy-root/native overlap warnings; this slice targets game-rule split granularity and duplicate-free localization ownership.

## Next

- Continue splitting coarse non-map common families such as continuous focuses, faction templates, and operation tokens where one compiled file still hides multiple editable records.
