# PIHC3 Equipment Module Source Evidence Progress

Date: 2026-06-14 21:58

Linear: TAL-000

## Done

- Added explicit `legacy_source_files` and `legacy_source_paths` contracts to the PIHC2 equipment-module/category importer.
- Regenerated 130 `equipment_module` modules and 49 `equipment_module_category` modules with non-emitted PIHC2 source evidence in `legacy/`.
- Regenerated the 7 MIO component modules so reused generic MIO localization keys are single-owned and no longer create project duplicate-key errors.
- Updated PIHC3 migration docs and the durable legacy inventory.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k equipment_module_importer` failed first on missing `legacy_source_paths`.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'equipment_module_importer or equipment_module_family or military_industrial_organization_component'` passed: 4 passed, 145 deselected.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_equipment_modules.py --clean` imported 130 modules and 49 categories.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_military_industrial_organization_components.py --clean` imported 7 MIO component modules.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-equipment-module-mio-build.json` passed with 16,581 modules, 62 collections, 37,170 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- Full PIHC2 parity still needs ship designer modules, designer-window GUI parity, and editable MIO trait-tree authoring if those become GUI-facing workflows.

## Next

- Continue source-evidence and compile-clean migration slices for remaining non-map families with sparse GUI data.
