# PIHC3 Entity Native Metadata

## Scope

- Continued the PIHC2 entity/model migration without splitting the aggregate HOI4DEV model bundle into per-model module families.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_entities.py` so `src/modules/entity/HOI4DEV_ENTITIES` records source inventory, compiled PDX summaries, copied asset summaries, image metadata, and `resources/entities.json` table facts in generic module metadata.
- Regenerated the ignored PIHC3 entity module with `--clean`.

## Result

- The entity module now records 312 source files, 134 source `info.json` records, 6 source model folders, 9 compiled PDX files, and 173 copied mesh/animation/texture/image files.
- Metadata mirrors `entities.json` with 257 tag entries and 244 unit/equipment type entries.
- Compiled PDX summaries expose 134 `pdxmesh` records, 8,871 `entity` records, and 8,674 clone references.
- Copied asset summaries expose extension counts of 25 `.anim`, 141 `.dds`, 6 `.mesh`, and 1 `.png` files, plus byte sizes and DDS/PNG dimensions/header facts where available.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k entity_importer_extracts_source_compiled_and_image_metadata_contract` failed before implementation on missing `module_id`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k 'entity_family or entity_importer'` passed with 3 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_entities.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_entities.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-entity-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build output contains 182 entity-owned artifacts: 9 PDX/model files and 173 copied model assets.

## Remaining Work

- Reconstruct editable per-model/per-variant entity records only if GUI authoring needs record-level model editing.
- Revisit autodiffuse regeneration and texture default synthesis after generic asset/image slots stabilize.
- Validate `entities.json` tag assignment behavior against in-game unit/equipment model selection.
