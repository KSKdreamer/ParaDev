# 2026-06-20 12:39 - PIHC3 System Plugin Boundary

## Scope

Tightened the PIHC3 project-local `system/` folder so it contains only ParaDev project plugins registered by `paradev.yaml`.

## Changes

- Deleted `projects/PIHC3/system/compile.py`, an obsolete compiler hook that imported the old `paradev.hoi4.mod` API and was not listed in `python_modules`.
- Added a PIHC3 migration contract that requires every `system/*.py` file to be registered in `paradev.yaml` `python_modules`.
- Updated `projects/PIHC3/README.md` to document that `system/` is reserved for registered project-local family plugins.

## Verification

- Red system-boundary contract: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py::test_pihc3_system_python_modules_are_manifest_registered_only -q` failed with extra `system/compile.py`.
- Focused green: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py::test_pihc3_system_python_modules_are_manifest_registered_only tests/test_pihc3_migration_contracts.py::test_pihc3_project_build_wrappers_use_current_paradev_surfaces tests/test_pihc3_migration_contracts.py::test_pihc3_project_tree_has_no_generated_cache_files -q` passed.
- Obsolete API scan: `rtk rg -n "system/compile\\.py|from paradev\\.hoi4\\.mod|paradev\\.hoi4\\.mod|BuildCtx|build_mod" projects/PIHC3 tests/test_pihc3_migration_contracts.py -g '!projects/PIHC3/.git/**' -g '!projects/PIHC3/src/**'` only found the tests that forbid these patterns.
- Direct PIHC3 wrapper probe: `rtk bash projects/PIHC3/compile.bash --plan-only --json > /tmp/pihc3-plan-system-cleanup.json` passed, and the captured JSON parsed with `project_id` set to `PIHC3` and `dry_run` set to `True`.
- Direct generated-file scan: `rtk zsh -lc 'find projects/PIHC3 -name .DS_Store -type f -o -name __pycache__ -type d -o -name "*.pyc" -type f | sort | sed -n "1,80p"'` produced no output.

## Notes

The registered family plugins remain `system/state_lore_family.py` and `system/equipment_module_family.py`. They stay under `system/` because `paradev.yaml` loads them through the current project-local family registration API.
