# 2026-06-20 15:14 - PIHC3 Source Root README Cleanup

## Goal

Finish the small project-root cleanup left after removing PIHC3's old top-level source roots.

## Changes

- Extended the PIHC3 migration contract to require:
  - only `src/modules` and `src/collections` under `projects/PIHC3/src`;
  - no tracked root `.keep` placeholder;
  - README wording for both native module and collection roots.
- Removed the obsolete `projects/PIHC3/.keep` placeholder.
- Updated `projects/PIHC3/README.md` to name `src/modules/` and `src/collections/` separately.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_source_root_contains_only_current_project_roots -q` failed on the tracked `.keep` placeholder.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'source_root or project_build_wrappers or system_python_modules or project_tree_has_no_generated_cache_files or idea_importer'`
- `rtk uv run black --check tests/test_pihc3_migration_contracts.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py`
- `rtk bash projects/PIHC3/compile.bash --plan-only --json`
  - `module_count`: 16581
  - `collection_count`: 62
  - `artifact_count`: 37480
  - `diagnostic_count`: 546
  - `error_count`: 0
  - `blocked`: false
- `rtk git diff --check -- tests/test_pihc3_migration_contracts.py`
- `rtk git -C projects/PIHC3 diff --check -- README.md .keep`

## Notes

This does not change build behavior. It keeps the committed PIHC3 project root aligned with the cleaned source layout and removes a placeholder that no longer serves a purpose.
