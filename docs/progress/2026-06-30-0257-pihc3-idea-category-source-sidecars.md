# PIHC3 Idea Category Source Sidecars

## Summary

- Added `legacy/source.yaml` manifests for all six native PIHC3 idea-category modules.
- Updated the idea-category importer to write the sidecar from the copied PIHC2 category and child evidence paths.
- Normalized regenerated `def.txt` and `main.loc` EOF handling so future importer runs do not create blank-line churn.
- Refreshed `IDEA_CATEGORY_ERA_COLD` from the current PIHC source, moving resource/cold-weather costs into the PDX modifiers and removing duplicated variable-cost localization lines.
- Updated the idea-category migration note to document the sidecar in the module layout.
- Added a migration contract asserting the sidecar schema for generated idea-category modules.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k idea_category`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_idea_categories.py tests/test_pihc3_migration_contracts.py`
- `rtk bash projects/PIHC3/compile.bash --plan-only --summary --json`
- `rtk git diff --check`
- `rtk bash -lc 'cd projects/PIHC3 && git diff --check'`

