# PIHC3 Recursive Cache Clean Progress

Date: 2026-06-21 06:18

Linear: TAL-000

## Done

- Tightened `projects/PIHC3/compile.bash --clean` so it removes generated PIHC3 runtime directories plus all Python bytecode caches under `system/` and `scripts/`, not only top-level `__pycache__` folders.
- Removed the generated `projects/PIHC3/system/__pycache__` files from the working tree.
- Updated the PIHC3 migration contract to require recursive cache cleanup through the single supported `compile.bash` build wrapper.

## Verification

- Red check first: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'build_wrappers_use_current_paradev_surfaces or project_tree_has_no_generated_cache_files'`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'build_wrappers_use_current_paradev_surfaces or project_tree_has_no_generated_cache_files or generated_runtime_directories_are_local_only'`
- `rtk bash projects/PIHC3/compile.bash --clean --summary --json`
- `rtk bash -lc 'find projects/PIHC3 \( -name __pycache__ -o -name "*.pyc" -o -name .DS_Store \) -print'`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py`
- `rtk git diff --check`

## Risks Or Blockers

- `compile.bash --summary` still computes enough PIHC3 project state to take over a minute; output is compact and reported `error_count: 0`, but the command is not yet a cheap metadata-only health check.
- The PIHC3 summary still reports the known `diagnostic_count: 546` warning surface.

## Next

- Continue reducing PIHC3 migration scripts into documented importer/review groups while preserving the one-command wrapper as the supported build entry point.
