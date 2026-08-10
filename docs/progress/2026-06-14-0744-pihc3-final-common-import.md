# PIHC3 final common split import

## Done

- Added `projects/PIHC3/scripts/migrate_pihc2_autonomy_continuous.py`.
- Replaced the final generic common-source ownership with a dedicated importer for `autonomous_state` and `continuous_focus`.
- Regenerated 5 autonomy modules keyed by compiled `id` values such as `autonomy_pihc_dominion`.
- Regenerated 1 continuous-focus palette module keyed by `generic_focus`.
- Retired all family ownership from `projects/PIHC3/scripts/migrate_pihc2_common_sources.py`; it remains as a localization helper for older dedicated importers.
- Limited final-common localization ownership to module ids and nested focus ids, avoiding duplicate ownership of referenced keys such as `puppet_wargoal_focus`.
- Updated final-common migration notes and design counts.

## Verification

- Red contract run: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'autonomy or continuous_focus or final_common'` failed before implementation because the importer was missing and the generic common batch still owned 2 families.
- Localization regression contract failed before the ownership fix because autonomy modules imported the referenced `puppet_wargoal_focus` key.
- Focused contracts passed after fixes.
- Pre-doc PIHC3 emitting build completed with 11,767 modules, 62 collections, 36,147 artifacts, 3,842 diagnostics, 0 errors, and `blocked False`.
- `rtk bash scripts/flake.bash --black --paths projects/PIHC3/scripts/migrate_pihc2_autonomy_continuous.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` passed with no file changes.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_autonomy_continuous.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk bash scripts/flake.bash --ci --paths projects/PIHC3/scripts/migrate_pihc2_autonomy_continuous.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'autonomy or continuous_focus or final_common'` passed with 3 tests.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` passed with 58 tests.
- Final `Project.load(Path("projects/PIHC3")).build(emit_artifacts=True, emit_manifests=True)` completed with 11,767 modules, 62 collections, 36,147 artifacts, 3,842 diagnostics, 0 errors, and `blocked False`.
- `rtk bash scripts/flake.bash --ci` passed.
