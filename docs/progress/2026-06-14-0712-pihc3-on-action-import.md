# PIHC3 on-action split import

## Done

- Added `projects/PIHC3/scripts/migrate_pihc2_on_actions.py`.
- Replaced the former 93 file-level on-action imports with 115 hook-level `src/modules/on_action` modules.
- Preserved the required `on_actions = { ... }` wrapper in each generated `def.txt`.
- Split multi-hook source files as `<file_stem>__<hook>` while keeping single-hook files on the source file stem.
- Skipped `PIHC_STATE_LORES.txt` because the `state_lore` aggregate family owns `common/on_actions/PIHC_STATE_LORES.txt`.
- Removed `on_action` from the generic compiled common-source importer.
- Updated migration design and on-action notes with the new counts and ownership policy.

## Verification

- `rtk bash scripts/flake.bash --black --paths projects/PIHC3/scripts/migrate_pihc2_on_actions.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` passed with no file changes.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_on_actions.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk bash scripts/flake.bash --ci --paths projects/PIHC3/scripts/migrate_pihc2_on_actions.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k on_action` passed with 3 tests.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` passed with 52 tests.
- `Project.load(Path("projects/PIHC3")).build(emit_artifacts=True, emit_manifests=True)` completed with 3,459 modules, 62 collections, 27,823 artifacts, 3,842 diagnostics, 0 errors, and `blocked False`.
- `rtk bash scripts/flake.bash --ci` passed.
