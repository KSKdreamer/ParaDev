# PIHC3 Entity Import Progress

Date: 2026-06-14 02:50

Linear: TAL-299

## Done

- Migrated the PIHC2 HOI4DEV entity/model bundle into `projects/PIHC3/src/modules/entity/HOI4DEV_ENTITIES`.
- Updated the PIHC3 `entity` family to use generic path-preserving `pdx` and `assets` source slots, so `.gfx`/`.asset`, meshes, animations, and textures emit through shared routed-source behavior.
- Imported 6 legacy model source folders, 9 compiled PDX entity files, and 173 static model files from `PIHC_dev/gfx/models`.
- Excluded the now-owned generated entity/model outputs from the PIHC_dev copy root to avoid shadowing the PIHC3 module artifacts.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` passed: 10 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_entities.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `Project.load("projects/PIHC3").build(emit_artifacts=True, emit_manifests=True)` completed with `dry_run False`, 3,033 modules, 62 collections, 25,722 artifacts, 4,183 warnings, 0 errors, and `blocked False`.
- Verified emitted files under `projects/PIHC3/build/mod/gfx/models`, including `00_hoi4dev_meshes.gfx`, `z_hoi4dev_entities.asset`, `zz_hoi4dev_units_entities.asset`, `viento/air/airship/mesh.mesh`, and `viento/weapon/rifle/spec_paint.png`.

## Risks Or Blockers

- Full `rtk bash scripts/test.bash` still fails on unrelated frontend API reference expectations:
  `tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer` and
  `tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`.

## Next

- Continue non-map PIHC2 migration with another missing GUI-visible family, likely buildings, modifiers, or equipment archetypes/types depending on current PIHC3 coverage.
