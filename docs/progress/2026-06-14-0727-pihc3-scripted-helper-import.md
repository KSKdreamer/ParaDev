# PIHC3 scripted helper split import

## Done

- Added `projects/PIHC3/scripts/migrate_pihc2_scripted_effects_triggers.py`.
- Replaced 49 file-level scripted-effect modules with 8,277 top-level scripted-effect modules.
- Replaced 7 file-level scripted-trigger modules with 87 top-level scripted-trigger modules.
- Kept per-inventory item helper files owned by native `inventory_item` modules.
- Disambiguated repeated scripted ids as `<file_stem>__<record_id>` while preserving the original top-level PDX key in `def.txt`.
- Removed `scripted_effect` and `scripted_trigger` from the generic compiled common-source importer.
- Updated scripted helper migration notes and design counts.

## Verification

- Red contract run: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'scripted_effect or scripted_trigger'` failed before implementation because the split importer was missing and both families were still in the generic common batch.
- Green contract run: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'scripted_effect or scripted_trigger'` passed with 3 tests.
- Pre-doc PIHC3 emitting build completed with 11,767 modules, 62 collections, 36,131 artifacts, 3,842 diagnostics, 0 errors, and `blocked False`.
- `rtk bash scripts/flake.bash --black --paths projects/PIHC3/scripts/migrate_pihc2_scripted_effects_triggers.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` passed with no file changes after final formatting.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_scripted_effects_triggers.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk bash scripts/flake.bash --ci --paths projects/PIHC3/scripts/migrate_pihc2_scripted_effects_triggers.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` passed with 55 tests.
- Final `Project.load(Path("projects/PIHC3")).build(emit_artifacts=True, emit_manifests=True)` completed with 11,767 modules, 62 collections, 36,131 artifacts, 3,842 diagnostics, 0 errors, and `blocked False`.
- `rtk bash scripts/flake.bash --ci` passed.
