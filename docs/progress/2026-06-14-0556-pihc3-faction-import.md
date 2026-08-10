# PIHC3 Faction Template Import Progress

Date: 2026-06-14 05:56 CST

Linear: N/A

## Done

- Added `projects/PIHC3/scripts/migrate_pihc2_factions.py` to split compiled PIHC_dev faction templates into one PIHC3 module per root template.
- Replaced the previous one file-level `generic_factions` module with 4 template-level modules under `projects/PIHC3/src/modules/faction`.
- Preserved only module-local required loc rows plus explicit `name` localization when it exists, avoiding shared manifest/goal/rule localization duplication.
- Removed `faction` from the generic common-source importer so future generic imports do not overwrite the split modules.
- Updated migration docs for the dedicated faction-template importer and current PIHC3 build counts.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k faction` -> 3 passed.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` -> 39 passed.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_factions.py --clean` -> imported 4 faction modules.
- PIHC3 emitting build -> 3,332 modules, 62 collections, 27,696 artifacts, 0 errors, `blocked: false`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_factions.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk bash scripts/flake.bash --ci` -> passed.

## Risks Or Blockers

- Faction goals, manifests, rules, rule groups, upgrades, member upgrades, icon pools, and related scripted/GUI behavior are still copy-overlay or future native slices.
- The build still reports broader copy-root/native overlap warnings; this slice targets faction-template split granularity.

## Next

- Continue splitting coarse non-map common families where the current file-level module hides multiple independently editable records, while leaving aggregate-shaped families such as continuous-focus palettes for a dedicated aggregate design.
