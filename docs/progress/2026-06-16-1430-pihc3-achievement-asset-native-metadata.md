# PIHC3 Achievement Asset Native Metadata

## Scope

- Continued PIHC2 achievement asset migration without changing the shared path-preserving copy slot.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_achievement_asset_components.py` so achievement asset modules expose generic file metadata in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated all 49 ignored PIHC3 achievement asset modules with `--clean`.

## Result

- The importer still groups 147 compiled `gfx/achievements/*.dds` files into 49 achievement asset modules.
- Each module now records `module_id`, compiled source paths, file count, extension counts, total byte size, variant/path maps, image width/height/mipmap/byte-size maps by path, DDS pixel formats, and `file_summaries_by_path`.
- `ACHIEVEMENT_ASSET_COMPONENT_ACHIEVEMENT_PIHC_1CO_ALL_THE_FIRST_GAME` records three `.dds` paths, 12,672 total bytes, normal/grey/not-eligible variants, 64x64 dimensions, one mipmap each, and DXT5 pixel format.
- The build output contains 147 `achievement_asset_component`-owned copy artifacts under `gfx/achievements/` and 0 copy-root-owned achievement DDS artifacts.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k achievement_asset_component_importer_extracts_generic_file_metadata_contract` failed before implementation on missing `module_id`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k achievement_asset_component` passed with 4 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_achievement_asset_components.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_achievement_asset_components.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-achievement-asset-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Remaining Work

- Keep source-image regeneration and aggregate achievement pack emission for later achievement slices.
- Review achievement UI/ribbon behavior only after the compiled achievement and asset surfaces stay stable.
