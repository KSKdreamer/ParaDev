# PIHC3 Equipment Native Metadata

## Scope

- Continued PIHC2 regular equipment migration without changing the shared `def.txt`, `main.loc`, and path-preserving `assets` slots.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_equipments.py` so each regular equipment/archetype module exposes generic PDX, localization, and compiled UI-asset provenance in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated all ignored native regular equipment modules with `--clean`: 167 modules.

## Result

- Each regular equipment module now records compiled source paths, source file extension counts, source byte/line facts, generated equipment text byte/line facts, generated localization text byte/line facts, compiled PDX/localization output paths, source file stem, `file_summaries_by_path`, compiled asset paths, asset extension counts, total compiled asset bytes, and per-asset byte-size summaries.
- `EQUIPMENT_CHASSIS_TANK_HEAVY_WOODEN` records `common/units/equipment/zz_all_equipments.txt`, 172,311 source bytes, 5,867 source lines, 2,154 generated equipment bytes, 101 generated equipment lines, 473 generated localization bytes, 17 generated localization lines, 4 compiled UI assets, 147,057 compiled asset bytes, and output `common/units/equipment/EQUIPMENT_CHASSIS_TANK_HEAVY_WOODEN.txt`.
- The regenerated tree has 167 `legacy/source.yaml` manifests, 35 unique compiled source files, 167 source path references, 22,957,622 compiled source bytes, 781,719 compiled source lines, 158,227 generated equipment bytes, 7,539 generated equipment lines, 115,926 generated localization bytes, and 2,761 generated localization lines.
- The regenerated tree also has 337 copied compiled UI asset files totaling 6,309,288 bytes: 169 DDS files, 141 GFX files, and 27 equipment-designer GUI files.
- Existing regular-equipment browsing metadata is preserved: 934 owned localization rows, 465 PIHC2 resource evidence paths, 128 modules with source `default.png`, 34 archetype modules, and 133 modules sourced from `zz_all_equipments.txt`.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k equipment_importer_extracts_generic_provenance_contract` failed before implementation on missing `compiled_source_paths`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k 'pihc3_equipment and not unit_component and not common_component and not ai_component and not special_project'` passed with 6 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_equipments.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_equipments.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-equipment-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 167 `module:equipment/<id>` PDX artifacts, 334 module-owned equipment localization artifacts, 337 module-owned equipment asset artifacts, 0 copy-root-owned regular-equipment artifacts, and 0 emitted `legacy/` artifacts.

## Remaining Work

- Keep editable stat inheritance from raw PIHC2 JSON, designer-window GUI parity, ship designer modules, generated icon workflows, and gameplay balancing for later parity slices.
- Current shared slots remain sufficient: `def.txt` owns the wrapped equipment PDX record, `main.loc` owns selected localization rows, and `assets` owns compiled DDS/GFX/designer GUI files.
