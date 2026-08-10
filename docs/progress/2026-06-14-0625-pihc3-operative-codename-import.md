# PIHC3 Operative Codename Import Progress

Date: 2026-06-14 06:25 CST

Linear: N/A

## Done

- Added `projects/PIHC3/scripts/migrate_pihc2_operative_codenames.py` to split compiled PIHC_dev operative codename themes by top-level game record id.
- Replaced the typoed file-stem module `generic_opertive_codenames` with `GENERIC_ENG_OPERATIVE_CODENAME_HISTORICAL`.
- Preserved the compiled PDX root entry and generated fallback localization for both the family-required name-theme key and the compiled PDX `NAME_THEME_HISTORICAL_OPERATIVES` key.
- Removed `operative_codename` from the generic common-source importer so future generic imports do not overwrite the record-id module.
- Updated migration docs for the dedicated operative-codename importer and current generic common-source batch counts.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k operative_codename` -> 3 passed.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` -> 43 passed.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_operative_codenames.py --clean` -> imported 1 operative codename module.
- PIHC3 emitting build -> 3,332 modules, 62 collections, 27,696 artifacts, 0 errors, `blocked: false`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_operative_codenames.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk bash scripts/flake.bash --ci` -> passed.

## Risks Or Blockers

- The source currently has one theme record. Country-specific and multilingual codename packs still need a broader review if PIHC2 or future sources add more themes.
- The fallback `NAME_THEME_HISTORICAL_OPERATIVES` text is generated because neither vanilla nor PIHC_dev provides localization for that key.

## Next

- Continue splitting remaining non-map generic common families where root records are independently editable, with scripted effects/triggers likely needing shared macro handling.
