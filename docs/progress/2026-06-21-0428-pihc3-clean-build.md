# PIHC3 Clean Build Progress

Date: 2026-06-21 04:28

Linear: TAL-000

## Done

- Added PIHC3 `compile.bash --clean` so the one-line build wrapper can remove only local generated runtime directories and Python bytecode caches before running the current `paradev build` CLI.
- Documented the clean build command in the PIHC3 README and user manual.
- Removed generated PIHC3 cache residue from the local tree: `system/__pycache__` and `assets/.DS_Store`.
- Extended PIHC3 migration contracts so the clean wrapper, docs, ignored cache dirs, and no-generated-cache invariant stay enforced.

## Verification

- `rtk bash projects/PIHC3/compile.bash --help`
- `rtk bash projects/PIHC3/compile.bash --clean --plan-only --json`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'build_wrappers_use_current_paradev_surfaces or generated_runtime_directories or project_tree_has_no_generated_cache_files'`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py`
- `rtk git diff --check`
- `rtk find projects/PIHC3 -name __pycache__`
- `rtk find projects/PIHC3 -name '*.pyc'`
- `rtk find projects/PIHC3 -name .DS_Store`

## Risks Or Blockers

- The full PIHC3 clean plan still produces the known `copy_root.shadowed_artifact` warnings; it completed with `blocked: false` and `error_count: 0`.
- PIHC3 is a nested Git worktree with extensive pre-existing migration changes; this slice only changes the clean-build wrapper/docs and root migration contract test.

## Next

- Add a compact PIHC3 build-summary check that avoids dumping the full multi-million-token JSON plan during verification.
- Continue pruning or grouping migration importers once each family has a current parity note and review path.
