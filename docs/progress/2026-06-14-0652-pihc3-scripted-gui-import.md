# PIHC3 Scripted GUI Import Progress

Date: 2026-06-14 06:52 CST

Linear: N/A

## Done

- Added `projects/PIHC3/scripts/migrate_pihc2_scripted_guis.py` to split compiled PIHC_dev scripted GUI records by child GUI id.
- Replaced 13 file-level scripted GUI modules with 109 record-level modules under `projects/PIHC3/src/modules/scripted_gui`.
- Preserved the required `scripted_gui = { ... }` wrapper in each module's `def.txt` so every record remains a valid standalone HOI4 scripted GUI file.
- Removed `scripted_gui` from the generic common-source importer so future generic imports do not overwrite the split modules.
- Updated migration docs for the dedicated scripted GUI importer and current PIHC3 build counts.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k scripted_gui` -> 3 passed.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` -> 49 passed.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_scripted_guis.py --clean` -> imported 109 scripted GUI modules.
- PIHC3 emitting build -> 3,436 modules, 62 collections, 27,800 artifacts, 0 errors, `blocked: false`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_scripted_guis.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk bash scripts/flake.bash --ci` -> passed.

## Risks Or Blockers

- Interface `.gui` layout files, scripted localization, and GUI behavior parity are still separate work; this slice preserves compiled script-side GUI records only.
- Inventory and welcome-screen GUI families now have many editable records, but record-level grouping does not yet provide higher-level UI workflow abstractions.

## Next

- Continue splitting remaining non-map generic common families. Scripted effects and triggers need a dependency-aware split strategy because many files contain large helper sets.
