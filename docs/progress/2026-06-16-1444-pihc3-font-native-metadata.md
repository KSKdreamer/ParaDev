# PIHC3 Font Native Metadata

## Scope

- Continued PIHC2 font asset migration without changing the shared path-preserving copy slot.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_font_components.py` so the aggregate font module exposes generic file metadata in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated the ignored `FONT_COMPONENT_PIHC_FONTS` module with `--clean`.

## Result

- The importer still groups 127 compiled `gfx/fonts` files into one aggregate font module: 63 BMFont `.fnt` metadata files, 44 DDS atlases, and 20 TGA atlases.
- The module now records `module_id`, compiled source paths, file count, extension counts, total byte size, text/image file counts, asset-kind maps, and `file_summaries_by_path`.
- Representative summaries now expose `Arial_14.fnt` as font metadata with 8,354 lines, 8,350 characters, page `Arial_14.dds`, and 960,156 bytes; `Arial_14.dds` as a 2048x2048 DXT3 DDS atlas; and `vic_18.tga` as a 512x1024 32-bit TGA atlas.
- The build output contains 127 `font_component`-owned copy artifacts under `gfx/fonts/` and 0 copy-root-owned font artifacts.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k font_component_importer_extracts_generic_file_metadata_contract` failed before implementation on missing `module_id`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k font_component` passed with 4 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_font_components.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_font_components.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-font-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Remaining Work

- Keep editable font atlas/source regeneration for a later slice only if GUI workflows need font authoring.
- Preserve the current byte-identical compiled font bundle until that higher-level source model exists.
