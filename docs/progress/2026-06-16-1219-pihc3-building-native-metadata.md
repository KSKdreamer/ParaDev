# 2026-06-16 12:19 PIHC3 building native metadata

## Scope

Enrich the compiled PIHC_dev building import so PIHC3 native building modules expose source provenance, localization summaries, and shallow field groups through generic settings.

## Changes

- Added a focused red contract for `bitumen_infrastructure` metadata covering building ids, source slot counts, compiled source facts, legacy resource evidence, localization counts, direct field groups, modifier blocks, level-cap fields, tag counts, and `legacy/source.yaml`.
- Extended `projects/PIHC3/scripts/migrate_pihc2_buildings.py` with compact metadata helpers while leaving the building family slots and compiler unchanged.
- Regenerated all 38 building modules with `--clean`.
- Updated the PIHC3 building migration note, design overview, and legacy inventory with the refreshed native coverage.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k building_importer_extracts_source_localization_and_field_metadata_contract` failed first with `KeyError: 'building_id'`.
- Green contract: the same focused command passed with `1 passed, 232 deselected`.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_buildings.py --clean` imported 38 building modules.
- Metadata coverage: 38 modules, 33-45 settings per module, 37 localized modules, 38 legacy manifests, 38 compiled source evidence paths, 1,120 localization rows across 10 HOI4 localization languages, 11 modifier summaries, and 38 level-cap summaries.
- Focused regression: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k 'building_importer or building_family'` passed with `3 passed, 230 deselected`.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_buildings.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_buildings.py tests/test_pihc3_migration_contracts.py` returned `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-building-native-metadata-build.json` completed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- Build ownership: native building modules own 38 building PDX artifacts and 242 localization artifacts; the build has 0 copy-root-owned `common/buildings/` artifacts.

## Follow-Up

State placement, building-slot behavior, map rendering, scripted effects, and technical particle/map-effect review remain future building slices.
