# 2026-06-14 21:40 CST - PIHC3 Equipment Resource Source Evidence

## Done

- Extended `equipment` import to preserve PIHC2 `resources/equipments/archetypes/<TAG>` and `resources/equipments/equipments/<TAG>` source files as module-local legacy evidence.
- Copied source files into all 167 imported regular equipment/archetype modules:
  - 34 archetype modules preserve `info.json` and `locs.txt`.
  - 133 regular equipment modules preserve `info.json` and `locs.txt`.
  - 128 regular equipment modules also preserve `default.png` where the PIHC2 source tree provides it.
- Recorded those source paths in module `meta.yaml` settings and `legacy/source.yaml`.
- Left emitted game artifacts unchanged: compiled `common/units/equipment/*.txt`, equipment DDS icons, sprite GFX, and equipment-designer GUI fragments still use the existing native equipment slots.
- Updated equipment migration docs and the legacy inventory to describe the non-emitted resource evidence.

## Verification

- Red check first: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'equipment_importer or equipment_family'` failed because `EquipmentSource` lacked `legacy_source_paths`.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'equipment_importer or equipment_family'`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_equipments.py --clean`
- Byte-checked `EQUIPMENT_CHASSIS_TANK_HEAVY_WOODEN` `default.png`, `info.json`, and `locs.txt` against the PIHC2 source folder.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-equipment-resource-source-build.json`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_equipments.py tests/test_pihc3_migration_contracts.py`
- `rtk git diff --check`

The build reports 16,581 modules across 62 collections, 37,110 artifacts, 713 diagnostics, 0 errors, and `blocked: false`. The manifest still emits representative `EQUIPMENT_CHASSIS_TANK_HEAVY_WOODEN` PDX/DDS artifacts from the `equipment` family, and 0 `legacy/equipments/...` files are emitted as artifacts.

## Risk

- This preserves source folders for audit and future reconstruction; it does not reconstruct editable equipment stat inheritance from raw PIHC2 JSON.
- Ship designer modules, designer-window GUI parity, generated icon workflows, and gameplay balancing remain future equipment slices.
- The module/artifact counts reflect the current dirty workspace build, including parallel work outside this slice.

## Next

- Continue data-family parity work for equipment/building/modifier GUI surfaces, especially module-summary/index visibility if the GUI still reports these families as empty.
