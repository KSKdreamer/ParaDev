# PIHC3 Wargoal Import

## Scope

- Added `projects/PIHC3/scripts/migrate_pihc2_wargoals.py` to split the compiled PIHC_dev `common/wargoals/00_invasion.txt` wrapper into individual PIHC3 `wargoal` modules.
- Regenerated `projects/PIHC3/src/modules/wargoal` as 13 native modules, each with `meta.yaml`, `def.txt`, `main.loc`, and `legacy/source.yaml`.
- Kept the existing generic `wargoal` family shape in `paradev.yaml`; no new family-specific build code was needed.
- Loaded vanilla HOI4 localization for base wargoals and overlaid PIHC_dev replacement localization for `crusade_wargoal`, `law_orthodoxy_wargoal`, and `trade_request_wargoal`.
- Added required-key fallbacks for every emitted language so split modules compile under the existing `required_loc_keys` contract.
- Updated `projects/PIHC3/docs/migration/28-wargoals.md` to describe the split import instead of the previous aggregate/starter-only state.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k wargoal`
  - `2 passed, 20 deselected`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_wargoals.py --clean`
  - Imported 13 PIHC2 wargoal modules.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q`
  - `22 passed`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_unit_medals.py projects/PIHC3/scripts/migrate_pihc2_wargoals.py tests/test_pihc3_migration_contracts.py`
  - `OK: 3 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- PIHC3 build via `Project.load(Path("projects/PIHC3")).build(emit_artifacts=True, emit_manifests=True)`
  - `dry_run: False`
  - `modules: 3204`
  - `collections: 62`
  - `artifacts: 26178`
  - `warnings: 3842`
  - `errors: 0`
  - `blocked: False`

## Notes

- The first PIHC3 build after splitting wargoals was blocked because non-English vanilla loc files did not include object-specific `{object_id}_WAR_NAME` fallback rows. The importer now fills required loc keys for every emitted language, not only English and Simplified Chinese.
- Full root `scripts/test.bash` was not rerun in this slice because the known unrelated frontend API helper failure remains outside the PIHC3 migration path.
- Remaining non-map aggregate families with visible compiled data still include operations, operation phases, and resistance activities.
