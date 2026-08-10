# PIHC3 Special Project Component Metadata

Date: 2026-06-15

## Slice

Expanded the PIHC2 special-project support importer so `SPECIAL_PROJECT_COMPONENT_PIHC_SPECIAL_PROJECT_SUPPORT` is no longer metadata-thin. The importer still preserves the two compiled `common/special_projects` support PDX files and six `interface/special_projects/*.gui` files through shared path-preserving `pdx` and `assets` slots, but `meta.yaml` now records the component id, source slot counts, extension counts, aggregate line/byte totals, 22 project tags, 8 specializations, specialization colors/backgrounds, six `guiTypes` roots, 266 GUI names, 198 unique GUI names, GUI assignment/type counts, and per-file summaries.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k special_project_component`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_special_project_components.py tests/test_pihc3_migration_contracts.py`
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-special-project-component-metadata-build.json`

The build reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`. The manifest owns all 8 reviewed special-project support files with `module:special_project_component/SPECIAL_PROJECT_COMPONENT_PIHC_SPECIAL_PROJECT_SUPPORT`, with 0 copy-root-owned artifacts for those paths.
