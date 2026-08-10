# PIHC3 Resistance Activity Import

## Scope

- Added `projects/PIHC3/scripts/migrate_pihc2_resistance_activities.py` to split the compiled PIHC_dev `common/resistance_activity/resistance_activity.txt` file into individual PIHC3 `resistance_activity` modules.
- Regenerated `projects/PIHC3/src/modules/resistance_activity` as 17 native modules, each with `meta.yaml`, `def.txt`, `main.loc`, and `legacy/source.yaml`.
- Kept the existing generic `resistance_activity` family shape in `paradev.yaml`; no new family-specific build code was needed.
- Loaded vanilla HOI4 localization for activity titles and alert text, with PIHC_dev replacement localization overriding vanilla rows where present.
- Synthesized each module's required `{object_id}_alert` key from the shared `alert_text` localization value without re-declaring shared keys such as `building_is_sabotaged` or `resource_is_sabotaged`, avoiding duplicate localization diagnostics.
- Updated `projects/PIHC3/docs/migration/34-resistance-activities.md` to describe the split import instead of the previous aggregate/starter-only state.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k resistance_activity`
  - `2 passed, 22 deselected`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_resistance_activities.py --clean`
  - Imported 17 PIHC2 resistance activity modules.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q`
  - `24 passed`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_unit_medals.py projects/PIHC3/scripts/migrate_pihc2_wargoals.py projects/PIHC3/scripts/migrate_pihc2_resistance_activities.py tests/test_pihc3_migration_contracts.py`
  - `OK: 4 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- PIHC3 build via `Project.load(Path("projects/PIHC3")).build(emit_artifacts=True, emit_manifests=True)`
  - `dry_run: False`
  - `modules: 3220`
  - `collections: 62`
  - `artifacts: 26362`
  - `warnings: 3842`
  - `errors: 0`
  - `blocked: False`

## Notes

- The first PIHC3 build after splitting resistance activities was blocked by duplicate declarations of shared vanilla alert keys. The importer now treats those shared keys as lookup inputs only and emits only object-owned localization keys.
- Full root `scripts/test.bash` was not rerun in this slice because the known unrelated frontend API helper failure remains outside the PIHC3 migration path.
- Remaining non-map aggregate families with visible compiled data still include operations and operation phases.
