# 2026-06-30 20:04 - Flag preview metadata cleanup

## Slice

Removed the redundant `settings.preview_source_path` field from PIHC3 generated `flag_asset_component` metadata. `preview_image_source` remains the single preview provenance field, while `legacy_source`, `compiled_source_paths`, `paths_by_variant`, and `file_summaries_by_path` keep detailed compiled source provenance.

## Red

- `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k "flag_asset_component_browser_exposes_preview_metadata or flag_asset_component_importer_extracts_tga_metadata_contract" -q` failed with both current generated metadata and importer output still containing `preview_source_path`.

## Verification

- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_flag_asset_components.py --clean`
- `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k "flag_asset_component_browser_exposes_preview_metadata or flag_asset_component_importer_extracts_tga_metadata_contract" -q`
- `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k flag_asset_component -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_flag_asset_components.py tests/test_pihc3_migration_contracts.py`
- `rtk uv run paradev build projects/PIHC3 --family flag_asset_component --module flag_asset_component/FLAG_ASSET_COMPONENT_30C`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Notes

- Regeneration updated 1,110 PIHC3 flag asset component `meta.yaml` files, each removing one duplicate metadata line.
- Focused flag asset migration contracts passed with 6 selected tests.
- Fast repo gate passed with `1235 passed, 2 warnings`.
- The first focused build smoke failed because the CLI module filter requires `family/object_id` form; the corrected SDK-form module id passed with `diagnostic_count: 0`, `error_count: 0`, and `blocked: false`.
- PIHC3 Tauri smoke reached `Running target/debug/paradev-desktop` and was stopped with Ctrl-C code 130. The known AI profile warning still appears and is unrelated to this metadata cleanup.
- A read-only explorer confirmed no desktop/build consumer depends on `preview_source_path`; thumbnails use `preview_image_path`, and docs already describe `preview_image_source`.
