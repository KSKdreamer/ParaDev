# PIHC3 Flag Asset Native Metadata

## Scope

- Continued PIHC2 flag asset migration without changing the shared path-preserving copy slot.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_flag_asset_components.py` so each flag asset module exposes generic file metadata in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated all 1,110 ignored PIHC3 flag asset modules with `--clean`.

## Result

- The importer still groups 1,370 reviewed compiled `gfx/flags/**/*.tga` files into 1,110 flag asset modules, while native country modules keep ownership of their 1,960 nested medium/small flag files.
- Each module now records `module_id`, compiled source paths, file count, extension counts, total byte size, variant/path maps, image width/height/bit-depth/alpha/byte-size maps by path, TGA image type/origin maps, and `file_summaries_by_path`.
- `FLAG_ASSET_COMPONENT_30C` records root, medium, and small TGA paths with 21,654 total bytes, 82x52, 41x26, and 10x7 dimensions, 32 bits per pixel, 8 alpha bits, image type id 2, and top-left origin.
- The build output contains 1,370 `flag_asset_component`-owned copy artifacts under `gfx/flags/`, 1,960 country-owned nested flag artifacts, 0 copy-root-owned flag artifacts, and 0 `.DS_Store` artifacts.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k flag_asset_component_importer_extracts_generic_file_metadata_contract` failed before implementation on missing `module_id`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k flag_asset_component` passed with 4 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_flag_asset_components.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_flag_asset_components.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-flag-asset-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Remaining Work

- Keep source flag image reconstruction and cosmetic-tag ownership review for a later country/flag parity slice.
- Preserve byte-identical compiled TGA outputs through the shared copy slot until higher-level flag authoring exists.
