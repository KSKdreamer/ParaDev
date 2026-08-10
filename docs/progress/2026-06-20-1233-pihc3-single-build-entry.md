# 2026-06-20 12:33 - PIHC3 Single Build Entry

## Scope

Removed the redundant PIHC3 SDK build wrapper so the nested project has one supported build entry point: `compile.bash`, which delegates to the current ParaDev CLI.

## Changes

- Deleted `projects/PIHC3/scripts/build.py`; `scripts/` now stays focused on migration and import utilities.
- Updated the PIHC3 migration contract to require that the duplicate SDK build wrapper is absent.
- Added README wording that `compile.bash` is the only supported PIHC3 build entry point.

## Verification

- Red duplicate-wrapper contract: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py::test_pihc3_project_build_wrappers_use_current_paradev_surfaces -q` failed while `projects/PIHC3/scripts/build.py` still existed.
- Red README wording contract: the same test failed until `projects/PIHC3/README.md` named `compile.bash` as the only supported PIHC3 build entry point.
- Focused green: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py::test_pihc3_project_build_wrappers_use_current_paradev_surfaces -q` passed.
- Wrapper plus cleanliness pair: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py::test_pihc3_project_build_wrappers_use_current_paradev_surfaces tests/test_pihc3_migration_contracts.py::test_pihc3_project_tree_has_no_generated_cache_files -q` passed.
- Wrapper checks: `rtk bash -n projects/PIHC3/compile.bash` and `rtk bash projects/PIHC3/compile.bash --help` passed.
- Direct wrapper probe: `rtk bash projects/PIHC3/compile.bash --plan-only --json > /tmp/pihc3-plan-one-entry.json` passed, and the captured JSON parsed with `project_id` set to `PIHC3` and `dry_run` set to `True`.
- Direct generated-file scan: `rtk zsh -lc 'find projects/PIHC3 -name .DS_Store -type f -o -name __pycache__ -type d -o -name "*.pyc" -type f | sort | sed -n "1,80p"'` produced no output.

## Notes

The exact removed-script path now only appears in the contract that forbids it and an older historical progress note that documented the script as stale. Current user-facing PIHC3 build docs point at `compile.bash`.
