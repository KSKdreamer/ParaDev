# PIHC3 Unit Medal Import

## Scope

- Added `projects/PIHC3/scripts/migrate_pihc2_unit_medals.py` to split the compiled PIHC_dev `common/unit_medals/00_default.txt` wrapper into individual PIHC3 `unit_medal` modules.
- Regenerated `projects/PIHC3/src/modules/unit_medal` as 16 native modules, each with `meta.yaml`, `def.txt`, `main.loc`, and `legacy/source.yaml`.
- Preserved the shared `@cost = 30` header in every split `def.txt` that references it, while keeping each module to one `unit_medals = { ... }` entry.
- Pulled unit medal localization from the local HOI4 install, with PIHC_dev localization kept as a later override source if present.
- Updated `projects/PIHC3/docs/migration/32-unit-medals.md` to describe the split import instead of the previous aggregate/starter-only state.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k unit_medal`
  - `2 passed, 18 deselected`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_unit_medals.py --clean`
  - Imported 16 PIHC2 unit medal modules.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q`
  - `20 passed`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_unit_medals.py tests/test_pihc3_migration_contracts.py`
  - `OK: 2 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- PIHC3 build via `Project.load(Path("projects/PIHC3")).build(emit_artifacts=True, emit_manifests=True)`
  - `dry_run: False`
  - `modules: 3192`
  - `collections: 62`
  - `artifacts: 26062`
  - `warnings: 3842`
  - `errors: 0`
  - `blocked: False`

## Notes

- Full root `scripts/test.bash` was not rerun in this slice because the known unrelated frontend API helper failure remains outside the PIHC3 migration path.
- Remaining non-map aggregate families with visible compiled data still include wargoals, operations, operation phases, and resistance activities.
