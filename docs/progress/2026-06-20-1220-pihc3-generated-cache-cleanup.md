# 2026-06-20 12:20 - PIHC3 Generated Cache Cleanup

## Scope

Cleaned PIHC3 generated filesystem noise and added a contract to keep the nested project free of local bytecode/cache artifacts while migration tests and build wrappers run.

## Changes

- Removed generated `.DS_Store`, `__pycache__`, and `.pyc` files from `projects/PIHC3`.
- Added a PIHC3 migration contract test that fails when generated cache files exist in the nested project tree.
- Updated the PIHC3 compile wrapper to export `PYTHONDONTWRITEBYTECODE=1` before invoking the ParaDev CLI.
- Updated PIHC3 migration contract tests to suppress bytecode writes in the current process and child Python processes.

## Verification

- Red cache contract: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py::test_pihc3_project_tree_has_no_generated_cache_files -q` failed with generated cache files present.
- Red wrapper contract: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py::test_pihc3_project_build_wrappers_use_current_paradev_surfaces -q` failed before `compile.bash` exported `PYTHONDONTWRITEBYTECODE=1`.
- Focused importer probes: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py::test_pihc3_wargoal_importer_extracts_individual_wargoal_contract -q` and `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py::test_pihc3_resistance_activity_importer_extracts_individual_activity_contract -q` passed after the bytecode guard.
- Cleanliness contract: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py::test_pihc3_project_build_wrappers_use_current_paradev_surfaces tests/test_pihc3_migration_contracts.py::test_pihc3_project_tree_has_no_generated_cache_files -q` passed.
- Direct generated-file scan: `rtk zsh -lc 'find projects/PIHC3 -name .DS_Store -type f -o -name __pycache__ -type d -o -name "*.pyc" -type f | sort | sed -n "1,80p"'` produced no output.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py` passed.
- Targeted functional flake: `rtk bash scripts/flake.bash --flake --paths tests/test_pihc3_migration_contracts.py` passed.
- PIHC3 wrapper checks: `rtk bash -n projects/PIHC3/compile.bash` and `rtk bash projects/PIHC3/compile.bash --help` passed.
- Direct PIHC3 wrapper probe: `rtk bash projects/PIHC3/compile.bash --plan-only --json > /tmp/pihc3-plan.json` passed, and the captured JSON parsed with `project_id` set to `PIHC3`.

## Notes

The full `tests/test_pihc3_migration_contracts.py` sweep was attempted but was interrupted with exit code 143 after early progress; no full-file pass is claimed. The targeted migration importer probes that previously implicated PIHC3 bytecode creation each take about 79 seconds and passed cleanly.
