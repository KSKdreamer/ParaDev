# PIHC3 Summary Wrapper Progress

Date: 2026-06-21 04:34

Linear: TAL-000

## Done

- Added `compile.bash --summary` in PIHC3 so the project-local build wrapper can run the compact `paradev summary` surface without dumping the full PIHC3 build plan payload.
- Kept `compile.bash` as the single PIHC3 build front door: normal build, clean build, dry plan, and compact summary all route through the wrapper.
- Documented `--summary --json` in the PIHC3 README and user manual.
- Added contract assertions that the wrapper calls `paradev summary` and that docs advertise the compact health-check command.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'build_wrappers_use_current_paradev_surfaces'`
- `rtk bash projects/PIHC3/compile.bash --help`
- `rtk bash projects/PIHC3/compile.bash --summary --strict-metadata`
- `rtk bash projects/PIHC3/compile.bash --summary --json`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'build_wrappers_use_current_paradev_surfaces or generated_runtime_directories or project_tree_has_no_generated_cache_files'`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py`
- `rtk git diff --check`
- `rtk git diff --check -- README.md compile.bash` inside `projects/PIHC3`
- Generated-file scans for `__pycache__`, `*.pyc`, and `.DS_Store` under PIHC3 returned 0.

## Risks Or Blockers

- `Project.summary()` still computes the full PIHC3 plan before reducing it; output is compact, but runtime is still around the full project plan cost.
- The summary command reports the known copy-root shadow warning count through `diagnostic_count: 546`, with `error_count: 0` and `blocked: false`.

## Next

- Consider a cheaper build-summary implementation that avoids materializing large module/artifact payloads when only counts are needed.
- Continue PIHC3 importer grouping and cleanup after each migrated family has a documented parity path.
