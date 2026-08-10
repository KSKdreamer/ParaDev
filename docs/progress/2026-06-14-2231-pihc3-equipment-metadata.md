# PIHC3 Equipment Metadata Progress

Date: 2026-06-14 22:31

Linear: TAL-000

## Done

- Extended the PIHC2 regular-equipment importer to mirror compiled equipment PDX fields into `meta.yaml` settings.
- Regenerated all 167 PIHC3 equipment/archetype modules with `equipment_keys`, archetype linkage, stats, resources, module slots, default modules, interface categories, and mission/type lists where present.
- Kept the existing shared `equipment` slots unchanged: PDX, loc, and copied UI assets remain the emitted surfaces.
- Updated PIHC3 equipment docs, migration design, and the durable legacy inventory.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k equipment_importer` failed first on missing `equipment_keys`, then passed: 1 passed, 148 deselected.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_equipments.py --clean` imported 167 equipment modules.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-equipment-metadata-build.json` passed with 16,581 modules, 62 collections, 37,340 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- Editable stat inheritance from raw PIHC2 JSON, designer-window parity, ship designer modules, and balancing validation remain future work.

## Next

- Continue improving sparse GUI-facing non-map families through importer metadata/source evidence before adding new family-specific code.
