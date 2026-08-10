# PIHC3 Clean-Only Wrapper Progress

Date: 2026-06-21 09:50 CST

Linear: TAL-000

## Done

- Added `projects/PIHC3/compile.bash --clean-only` so generated runtime directories and Python bytecode caches can be removed without running a PIHC3 build.
- Kept cleanup scoped to generated `.cache/`, `.paradev/`, `build/`, and bytecode caches under `system/` and `scripts/`.
- Updated the PIHC3 README and user manual to document `--clean-only` beside the one-command build, clean-build, summary, and plan-only forms.
- Added a PIHC3 migration contract test that creates generated probe files, runs `compile.bash --clean-only`, and verifies they are removed without stdout/stderr noise.

## Verification

- `rtk bash projects/PIHC3/compile.bash --help`
- `rtk bash projects/PIHC3/compile.bash --clean-only`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'project_build_wrappers or clean_only or generated_cache_files or generated_runtime_directories or source_root_contains_only_current_project_roots or manual_source_policy'`
- `rtk bash -n projects/PIHC3/compile.bash`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py`
- `rtk git diff --check -- docs/user-manual/pihc3.md tests/test_pihc3_migration_contracts.py`
- `rtk zsh -lc 'git -C projects/PIHC3 diff --check -- compile.bash README.md'`

## Risks Or Blockers

- `projects/PIHC3` is ignored by the root repo and is also a nested git repository. Review `git -C projects/PIHC3 diff -- compile.bash README.md` when preparing this slice.
- The broader goal remains open; this slice only hardens cleanup around the supported PIHC3 build entry point.

## Next

- Continue GUI editor usability and PIHC3 cleanup in similarly small tested slices.
