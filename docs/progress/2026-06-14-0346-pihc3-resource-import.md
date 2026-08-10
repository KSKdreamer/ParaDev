# PIHC3 Resource Import Progress

Date: 2026-06-14 03:46

Linear: TAL-299

## Done

- Split the compiled PIHC2 resource wrapper from `common/resources/00_resources.txt` into 9 individual PIHC3 `resource` modules.
- Added `projects/PIHC3/scripts/migrate_pihc2_resources.py` with importable contract helpers for compiled source rows, one-resource PDX text, and resource localization.
- Updated the `resource` family localization contract to require real HOI4 resource keys:
  `{object_id}_desc`, `country_resource_{object_id}`, and `country_resource_cost_{object_id}`.
- Regenerated `projects/PIHC3/src/modules/resource` with one module each for oil, aluminium, rubber, tungsten, steel, chromium, crystals, logs, and coal.

## Verification

- Red check: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k resource` failed on old loc keys and missing importer.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'resource or building'` passed: 4 passed.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` passed: 18 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_resources.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `Project.load("projects/PIHC3").build(emit_artifacts=True, emit_manifests=True)` completed with `dry_run False`, 3,177 modules, 62 collections, 25,889 artifacts, 3,842 warnings, 0 errors, and `blocked False`.

## Risks Or Blockers

- `rtk bash scripts/test.bash` failed outside this migration slice because the dirty frontend API renderer references missing `_frontend_api_workspace_action_execution_index_rows`.
- The build still reports the existing warning baseline, but no blocking diagnostics or errors.

## Next

- Continue non-map migration by splitting another aggregate common family, likely `unit_medal`, `wargoal`, `operation_phase`, or `on_action`, depending on compiled wrapper shape and GUI usefulness.
