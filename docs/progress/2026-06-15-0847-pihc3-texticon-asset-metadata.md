# 2026-06-15 08:47 PIHC3 Texticon Asset Metadata

## Slice

Continued the PIHC2 to PIHC3 migration by enriching `texticon_asset_component` modules. The family still uses one shared path-preserving copy slot for `gfx/texticons/*.dds`, `interface/PIHC_texticons.gfx`, and `interface/PIHC_unit_categories.gfx`, but generated `meta.yaml` settings now expose GUI-browsable sprite and DDS facts.

## Changes

- Added a contract test for compiled `PIHC_TEXTICONS` metadata.
- Updated `projects/PIHC3/scripts/migrate_pihc2_texticon_asset_components.py` to parse GFX sprite declarations and DDS headers.
- Regenerated the 5 ignored PIHC3 texticon asset modules with component ids, source counts, sprite names, texture paths, `legacy_lazy_load` values, image dimensions, mipmaps, byte sizes, pixel formats, FourCC values, RGB bit counts, header sizes, and per-source summaries.
- Updated the PIHC3 migration notes and the shared legacy inventory.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k 'intelligence_agency_asset_component or texticon_asset_component'` passed: 6 passed, 175 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_intelligence_agency_asset_components.py projects/PIHC3/scripts/migrate_pihc2_texticon_asset_components.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 52 `texticon_asset_component`-owned GFX/DDS artifacts.
