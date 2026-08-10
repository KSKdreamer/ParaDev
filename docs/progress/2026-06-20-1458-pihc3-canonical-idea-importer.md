# 2026-06-20 14:58 - PIHC3 canonical idea importer

## Slice

Removed the stale old-layout PIHC3 idea importer path and made the current module-layout importer own the canonical migration script name.

## Changes

- Added a PIHC3 migration contract requiring `scripts/migrate_pihc2_ideas.py` to target `src/modules/idea` and requiring the temporary `import_pihc2_ideas_current.py` name to be absent.
- Replaced the old `src/general` and `src/countries` idea migration script with the current importer under `scripts/migrate_pihc2_ideas.py`.
- Updated the idea importer tests and live PIHC3 ideas migration doc to use the canonical script path.

## Verification

- Red check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_idea_importer_uses_canonical_migration_script_name -q` failed because `scripts/import_pihc2_ideas_current.py` still existed.
- Focused contracts: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'idea_importer'` passed with `3 passed`.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_ideas.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_ideas.py tests/test_pihc3_migration_contracts.py` passed with no banned imports.
- PIHC3 one-line dry build: `rtk bash projects/PIHC3/compile.bash --plan-only --json` passed with `module_count: 16581`, `collection_count: 62`, `artifact_count: 37480`, `diagnostic_count: 546`, `error_count: 0`, and `blocked: false`.
- Targeted diff checks passed for the touched parent-repo test file and the touched nested PIHC3 files.

## Notes

- I intentionally interrupted a full `tests/test_pihc3_migration_contracts.py` run after it reached passing progress without failures; it was too slow for this narrow rename/removal slice. The focused importer contracts and PIHC3 plan-only build cover the affected behavior.
