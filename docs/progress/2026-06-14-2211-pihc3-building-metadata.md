# PIHC3 Building Metadata Progress

Date: 2026-06-14 22:11

Linear: TAL-000

## Done

- Extended the PIHC2 building importer to mirror useful compiled PDX fields into `meta.yaml` settings.
- Regenerated all 38 PIHC3 building modules with `base_cost`, `value`, build flags, `icon_frame`, `level_cap`, `building_tags`, and nested modifier summaries where present.
- Confirmed shared building image/interface assets remain owned by `interface_component`, avoiding per-building duplication.
- Updated PIHC3 building docs, migration design, and the durable legacy inventory.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k building_importer` failed first on missing `base_cost` metadata, then passed: 1 passed, 148 deselected.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_buildings.py --clean` imported 38 building modules.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-building-metadata-build.json` passed with 16,581 modules, 62 collections, 37,210 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- Building GUI parity still needs state placement, slot behavior, scripted effects, and technical map/effect review.

## Next

- Continue with remaining sparse-data non-map families, preferring metadata/source-evidence upgrades before adding new family-specific compiler code.
