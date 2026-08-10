# 2026-06-20 15:06 - PIHC3 Remove Legacy Source Roots

## Goal

Make PIHC3's source tree match the current ParaDev build contract: `src/modules` for native modules and `src/collections` for collection descriptors, with old v3 source snapshots removed from top-level `src`.

## Changes

- Added a PIHC3 migration contract asserting `projects/PIHC3/src` contains only `collections` and `modules`.
- Removed obsolete top-level PIHC3 source roots:
  - `src/achievements`
  - `src/characters`
  - `src/countries`
  - `src/country_defs`
  - `src/decisions`
  - `src/events`
  - `src/general`
  - `src/intel_agencies`
  - `src/traits`
- Updated `projects/PIHC3/docs/migration/00-design.md` so Source Policy describes only the current roots.
- Updated the achievement migration note to reference `src/modules/achievement`.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_source_root_contains_only_current_project_roots -q` failed on legacy roots.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_source_root_contains_only_current_project_roots -q`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'source_root or idea_importer or project_build_wrappers or project_tree_has_no_generated_cache_files'`
- `rtk uv run black --check tests/test_pihc3_migration_contracts.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py`
- `rtk bash projects/PIHC3/compile.bash --plan-only --json`
  - `module_count`: 16581
  - `collection_count`: 62
  - `artifact_count`: 37480
  - `diagnostic_count`: 546
  - `error_count`: 0
  - `blocked`: false
- `rtk git diff --check -- tests/test_pihc3_migration_contracts.py docs/progress`
- `rtk git -C projects/PIHC3 diff --check -- docs/migration/00-design.md docs/migration/40-achievements.md`

## Notes

The nested PIHC3 worktree now has a large intentional deletion set under the removed source roots. Existing native module files under `src/modules` and collection descriptors under `src/collections` remain the build inputs.
